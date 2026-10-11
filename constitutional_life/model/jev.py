"""Jev cells: typed decisions over a closed option set. Nothing is generated.

A Jev model receives a state and a set of questions and returns a probability
for every option. A cell asks:

    rule           which of the canonical transformations is hidden (all of them)
    communication  silence | publish                       (channel only)
    signal         0..7                                     (channel only)
    say            which transformation the message names   (channel only)

The engine applies the chosen rule to the query; that is task_answer, and the
chosen rule's canonical description is inferred_rule. The decision is encoded
as an ordinary DecisionV1a record, so scoring, board, memory and replay are the
same code path as for generative cells.

Consequences that are part of the stand, not measurements:
- solved and abstracted coincide on the query: the answer is the rule executed
  by the engine. Rule execution is not tested; rule selection is.
- `say` is a closed vocabulary of canonical descriptions, not free text.
- no grammar and no parse failures from the cell side; a malformed server
  response is an InferenceError, never repaired.

Two backends with one interface:
    TypeSafeJev    POST {base}/v1/systemone   (TypeSafe API, Bearer key)
    OpenJevSGLang  POST {base}/classify       (openjev on SGLang, pairs scored here)
"""

from __future__ import annotations

import math
import os
import random
import threading
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Literal, Protocol

from constitutional_life.cell.observation import CellObservation
from constitutional_life.cell.prompt import render_state
from constitutional_life.cell.schema import ParsedDecision, Publish, Silence, encode_decision
from constitutional_life.model.client import InferenceError, http_json
from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog, build_catalog
from constitutional_life.v1a_constants import (
    JEV_DECODE,
    JEV_MAX_WORKERS,
    JEV_TIMEOUT_S,
    OPENJEV_BASE_URL,
    OPENJEV_CLASSIFY_BATCH,
    OPENJEV_MODEL,
    SIGNAL_VALUES,
    TYPESAFE_API_KEY_ENV,
    TYPESAFE_API_KEY_ENV_FALLBACK,
    TYPESAFE_BASE_URL,
    TYPESAFE_MODEL,
)

Decode = Literal["sample", "argmax"]
OrderMode = Literal["shuffle", "canonical", "reversed"]
CommunicationType = Literal["choice", "noul"]
Distribution = dict[str, float]
Answers = dict[str, Distribution]

RULE_INSTRUCTIONS = "Which is the hidden transformation for this epoch?"
COMMUNICATION_INSTRUCTIONS = "Should this cell publish a message this generation?"
SIGNAL_INSTRUCTIONS = "If this cell publishes, which signal does the message carry?"
# `say` is not a separate Jev question: on publish, say := chosen rule description.
# Declared for TypeSafe v1a belief-spread (V1A_FREEZE): the board carries the
# cell's selected belief, not a second 101-way choice that can diverge from it.
COMMUNICATION_CRITERIA = {
    "silence": "stay silent this generation",
    "publish": "publish one message this generation",
}
# Noul maps yes→publish, no→silence (criteria.true / criteria.false on the wire).
NOUL_COMMUNICATION_CRITERIA = {
    "true": COMMUNICATION_CRITERIA["publish"],
    "false": COMMUNICATION_CRITERIA["silence"],
}
# Draws in this order whether or not the cell publishes, so a permuted inbox
# never shifts another question's draw. No `say` draw — say is bound to rule.
QUESTION_ORDER = ("rule", "communication", "signal")
TOP_K_LOGGED = 5

# openjev v5 training format (config.nli_template, decisions_api.HYPOTHESIS)
NLI_TEMPLATE = "Premise: {premise}\nHypothesis: {hypothesis}"
HYPOTHESIS = 'The answer to "{instr}" is {label}: {crit}'
OPENJEV_MAX_STATE_CHARS = 24_000  # one encoder window; the cell state is far below
ENTAILMENT = 1  # label order: contradiction, entailment, neutral


@dataclass(frozen=True, slots=True)
class JevRequest:
    state: str
    questions: dict[str, dict]
    # Canonical option keys per question (presentation order may differ).
    # For noul communication: ("silence", "publish").
    canonical_keys: dict[str, tuple[str, ...]] = field(default_factory=dict)


class JevBackend(Protocol):
    model: str

    def decide_many(self, requests: Sequence[JevRequest]) -> list[Answers]: ...

    def check(self) -> str: ...


def rule_key(index: int) -> str:
    return f"R{index:03d}"


def rule_options(catalog: FunctionCatalog) -> dict[str, CanonicalFunction]:
    return {rule_key(i): fn for i, fn in enumerate(catalog.functions)}


def _order_criteria(
    criteria: dict[str, str],
    *,
    mode: OrderMode,
    rng: random.Random | None,
) -> dict[str, str]:
    keys = list(criteria)
    if mode == "canonical" or len(keys) < 2:
        return dict(criteria)
    if mode == "reversed":
        return {k: criteria[k] for k in reversed(keys)}
    if rng is None:
        raise ValueError("shuffle order_mode requires an RNG")
    return _shuffle_criteria(criteria, rng)


def build_request(
    obs: CellObservation,
    channel: bool,
    options: dict[str, CanonicalFunction],
    *,
    order_seed: int | None = None,
    order_mode: OrderMode = "shuffle",
    communication_type: CommunicationType = "choice",
) -> JevRequest:
    """Build a Jev request. Choice criteria are ordered by order_mode + order_seed.

    Returned distributions are always re-keyed into canonical_keys order, so
    sampling is independent of presentation order; only the API's beliefs may
    depend on it.
    """
    if order_mode == "shuffle" and order_seed is None:
        raise ValueError("order_mode='shuffle' requires order_seed")
    rng = random.Random(order_seed) if order_mode == "shuffle" else None
    rules = {key: fn.description() for key, fn in options.items()}
    signal_criteria = {str(s): f"signal {s}" for s in SIGNAL_VALUES}
    canonical_keys: dict[str, tuple[str, ...]] = {
        "rule": tuple(rules),
    }
    questions: dict[str, dict] = {
        "rule": {
            "type": "choice",
            "instructions": RULE_INSTRUCTIONS,
            "criteria": _order_criteria(rules, mode=order_mode, rng=rng),
        },
    }
    if channel:
        if communication_type == "noul":
            questions["communication"] = {
                "type": "noul",
                "instructions": COMMUNICATION_INSTRUCTIONS,
                "criteria": dict(NOUL_COMMUNICATION_CRITERIA),
            }
            canonical_keys["communication"] = ("silence", "publish")
        else:
            questions["communication"] = {
                "type": "choice",
                "instructions": COMMUNICATION_INSTRUCTIONS,
                "criteria": _order_criteria(
                    dict(COMMUNICATION_CRITERIA), mode=order_mode, rng=rng
                ),
            }
            canonical_keys["communication"] = tuple(COMMUNICATION_CRITERIA)
        questions["signal"] = {
            "type": "choice",
            "instructions": SIGNAL_INSTRUCTIONS,
            "criteria": _order_criteria(signal_criteria, mode=order_mode, rng=rng),
        }
        canonical_keys["signal"] = tuple(signal_criteria)
        # No `say` question — published name is the chosen rule (see module note).
    return JevRequest(
        state=render_state(obs, channel),
        questions=questions,
        canonical_keys=canonical_keys,
    )



def choose(dist: Distribution, rng: random.Random, decode: Decode) -> str:
    """One draw per call in both modes, so RNG consumption does not depend on decode."""
    keys = list(dist)
    u = rng.random()
    if decode == "argmax":
        return max(keys, key=lambda k: dist[k])
    total = sum(dist.values())
    acc = 0.0
    for key in keys:
        acc += dist[key] / total
        if u < acc:
            return key
    return keys[-1]


def decide_from_answers(
    answers: Answers,
    obs: CellObservation,
    channel: bool,
    options: dict[str, CanonicalFunction],
    rng: random.Random,
    decode: Decode,
) -> tuple[ParsedDecision, dict]:
    picks: dict[str, str] = {}
    for qid in QUESTION_ORDER:
        if qid in answers:
            picks[qid] = choose(answers[qid], rng, decode)
    rule = options[picks["rule"]]
    communication = None
    if channel:
        if picks["communication"] == "publish":
            communication = Publish(
                signal=int(picks["signal"]),
                say=rule.description(),  # bound to chosen rule; not a separate draw
            )
        else:
            communication = Silence()
    decision = ParsedDecision(
        task_answer=rule.apply(obs.query),
        inferred_rule=rule.description(),
        communication=communication,
    )
    record = {
        qid: {
            "chosen": picks[qid],
            "p_chosen": answers[qid][picks[qid]],
            "top": _top(answers[qid]),
        }
        for qid in picks
    }
    if channel and picks.get("communication") == "publish":
        record["say"] = {
            "chosen": picks["rule"],
            "p_chosen": answers["rule"][picks["rule"]],
            "bound_to_rule": True,
            "top": _top(answers["rule"]),
        }
    return decision, record


class JevCompleter:
    """Completer over a Jev backend. Returns DecisionV1a JSON, one per cell."""

    def __init__(
        self,
        backend: JevBackend,
        *,
        catalog: FunctionCatalog | None = None,
        decode: Decode = JEV_DECODE,  # type: ignore[assignment]
    ) -> None:
        self.backend = backend
        self.options = rule_options(catalog or build_catalog())
        self.decode = decode
        self._records: list[dict] = []

    @property
    def model(self) -> str:
        return self.backend.model

    @property
    def communication_type(self) -> CommunicationType:
        return "noul" if isinstance(self.backend, TypeSafeJev) else "choice"

    def check(self) -> str:
        return self.backend.check()

    def complete_batch(
        self,
        observations: Sequence[CellObservation],
        *,
        channel: bool,
        seeds: Sequence[int],
        order_seeds: Sequence[int] | None = None,
        order_mode: OrderMode = "shuffle",
    ) -> list[str]:
        if len(observations) != len(seeds):
            raise ValueError("observations and seeds must align")
        if order_seeds is None:
            order_seeds = seeds
        if len(order_seeds) != len(observations):
            raise ValueError("order_seeds and observations must align")
        answers = self.distributions(
            observations,
            channel=channel,
            order_seeds=order_seeds,
            order_mode=order_mode,
        )
        raws = []
        for obs, seed, order_seed, ans in zip(
            observations, seeds, order_seeds, answers, strict=True
        ):
            decision, record = decide_from_answers(
                ans, obs, channel, self.options, random.Random(seed), self.decode
            )
            self._records.append(
                {
                    "generation": obs.generation,
                    "cell_id": obs.cell_id,
                    "seed": seed,
                    "order_seed": order_seed,
                    "order_mode": order_mode,
                    **record,
                }
            )
            raws.append(encode_decision(decision))
        return raws

    def distributions(
        self,
        observations: Sequence[CellObservation],
        *,
        channel: bool,
        order_seeds: Sequence[int] | None = None,
        order_mode: OrderMode = "shuffle",
    ) -> list[Answers]:
        """Exact per-question distributions in canonical key order. No draw."""
        if order_mode == "shuffle":
            if order_seeds is None:
                raise ValueError("order_mode='shuffle' requires order_seeds")
            if len(order_seeds) != len(observations):
                raise ValueError("order_seeds and observations must align")
        else:
            order_seeds = order_seeds if order_seeds is not None else [0] * len(observations)
        requests = [
            build_request(
                obs,
                channel,
                self.options,
                order_seed=seed,
                order_mode=order_mode,
                communication_type=self.communication_type,
            )
            for obs, seed in zip(observations, order_seeds, strict=True)
        ]
        answers = self.backend.decide_many(requests)
        if len(answers) != len(requests):
            raise InferenceError(f"{len(answers)} answers for {len(requests)} requests")
        out = []
        for req, ans in zip(requests, answers, strict=True):
            _check_answers(ans, req)
            out.append(
                {
                    qid: _normalise({key: ans[qid][key] for key in req.canonical_keys[qid]})
                    for qid in req.questions
                }
            )
        return out

    def measure_order_sensitivity(
        self,
        obs: CellObservation,
        *,
        channel: bool = True,
    ) -> dict:
        """Per-question L1 between canonical and reversed presentation order."""
        (canon,) = self.distributions([obs], channel=channel, order_mode="canonical")
        (rev,) = self.distributions([obs], channel=channel, order_mode="reversed")
        per_q = {}
        for qid in canon:
            if qid == "communication" and self.communication_type == "noul":
                per_q[qid] = {"type": "noul", "l1": None, "note": "no option order"}
            else:
                per_q[qid] = {"type": "choice", "l1": _l1(canon[qid], rev[qid])}
        choice_l1 = [row["l1"] for row in per_q.values() if row["l1"] is not None]
        return {
            "communication_type": self.communication_type,
            "max_l1": max(choice_l1) if choice_l1 else None,
            "questions": per_q,
        }

    def usage(self) -> dict:
        usage = getattr(self.backend, "usage", None)
        return usage() if callable(usage) else {}

    def pop_records(self) -> list[dict]:
        records, self._records = self._records, []
        return records


def _load_dotenv(path: str = ".env") -> None:
    """Disabled in luna_life public tree — use process env only."""
    return



def typesafe_api_key_from_env() -> str:
    _load_dotenv()
    for name in (TYPESAFE_API_KEY_ENV, TYPESAFE_API_KEY_ENV_FALLBACK):
        value = os.environ.get(name, "")
        if value:
            return value
    return ""


def _shuffle_criteria(criteria: dict[str, str], rng: random.Random) -> dict[str, str]:
    keys = list(criteria)
    if len(keys) < 2:
        return dict(criteria)
    for _ in range(32):
        order = list(keys)
        rng.shuffle(order)
        if order != keys:
            return {k: criteria[k] for k in order}
    # Deterministic fallback if shuffle keeps drawing the identity.
    return {k: criteria[k] for k in reversed(keys)}



def _l1(a: Distribution, b: Distribution) -> float:
    keys = set(a) | set(b)
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)


class TypeSafeJev:
    """TypeSafe Jev API. One request per cell; questions are answered together."""

    def __init__(
        self,
        base_url: str = TYPESAFE_BASE_URL,
        model: str = TYPESAFE_MODEL,
        *,
        api_key: str | None = None,
        timeout: float = JEV_TIMEOUT_S,
        max_workers: int = JEV_MAX_WORKERS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key if api_key is not None else typesafe_api_key_from_env()
        self.timeout = timeout
        self.max_workers = max_workers
        self.model_reported: str | None = None
        self._lock = threading.Lock()
        self._usage = {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "prompt_tokens": 0,  # alias of input_tokens for Completer.usage parity
            "cached_tokens": 0,  # TypeSafe does not report cache hits (yet)
        }

    def usage(self) -> dict:
        with self._lock:
            return dict(self._usage)

    def decide_many(self, requests: Sequence[JevRequest]) -> list[Answers]:
        with ThreadPoolExecutor(max_workers=max(1, min(self.max_workers, len(requests)))) as pool:
            return list(pool.map(self.decide, requests))

    def decide(self, request: JevRequest) -> Answers:
        body = self._post(
            {"model": self.model, "state": request.state, "questions": request.questions}
        )
        answers = body.get("answers") if isinstance(body, dict) else None
        if not isinstance(answers, dict):
            raise InferenceError("TypeSafe response has no answers object")
        out: Answers = {}
        for qid, question in request.questions.items():
            raw = answers.get(qid)
            if not isinstance(raw, dict):
                raise InferenceError(f"TypeSafe answer {qid!r} missing")
            if question.get("type") == "noul":
                if "noul" not in raw:
                    raise InferenceError(f"TypeSafe noul answer {qid!r} has no noul field")
                p_yes = float(raw["noul"])
                if not math.isfinite(p_yes) or not 0.0 <= p_yes <= 1.0:
                    raise InferenceError(f"TypeSafe noul answer {qid!r} out of range")
                # yes → publish, no → silence
                out[qid] = {"publish": p_yes, "silence": 1.0 - p_yes}
                continue
            probs = raw.get("probabilities")
            if not isinstance(probs, dict):
                raise InferenceError(f"TypeSafe answer {qid!r} has no probabilities")
            out[qid] = {str(k): float(v) for k, v in probs.items()}
        return out

    def check(self) -> str:
        body = self._post(
            {
                "model": self.model,
                "state": "The sky is blue.",
                "questions": {"q": {"type": "noul", "instructions": "Is the sky blue?"}},
            }
        )
        reported = body.get("model", self.model)
        self.model_reported = str(reported) if reported is not None else self.model
        return f"TypeSafe {self.base_url} model {self.model_reported}"

    def check_option_order(
        self,
        *,
        seed: int = 20260929,
        n_shuffles: int = 3,
    ) -> dict:
        """Compare distributions under permuted criteria order on several questions.

        Proprietary Jev does not guarantee order independence by construction.
        Call before recording any TypeSafe numbers. Returns a report with per-
        question max L1 between the canonical-order answer and each shuffle.
        """
        rng = random.Random(seed)
        catalog = build_catalog()
        # Three cardinalities: binary, 8-way, and a 12-option slice of the rule set.
        rule_slice = {
            rule_key(i): fn.description() for i, fn in enumerate(catalog.functions[:12])
        }
        templates: list[tuple[str, dict[str, str]]] = [
            ("communication", dict(COMMUNICATION_CRITERIA)),
            ("signal", {str(s): f"signal {s}" for s in SIGNAL_VALUES}),
            ("rule_slice", rule_slice),
        ]
        state = (
            "You are one cell. Two examples of a hidden string transform:\n"
            "  ABCD -> DCBA\n  EFGH -> HGFE\nQuery: ABAB\n"
        )
        questions_report = []
        max_l1 = 0.0
        for qid, criteria in templates:
            base_q = {
                "type": "choice",
                "instructions": f"Choose among options for {qid}.",
                "criteria": dict(criteria),
            }
            base = self.decide(JevRequest(state=state, questions={qid: base_q}))[qid]
            shuffle_rows = []
            for i in range(n_shuffles):
                shuffled = _shuffle_criteria(criteria, rng)
                req = JevRequest(
                    state=state,
                    questions={
                        qid: {
                            "type": "choice",
                            "instructions": base_q["instructions"],
                            "criteria": shuffled,
                        }
                    },
                )
                ans = self.decide(req)[qid]
                dist_l1 = _l1(_normalise(base), _normalise(ans))
                max_l1 = max(max_l1, dist_l1)
                shuffle_rows.append(
                    {
                        "shuffle": i,
                        "criteria_order": list(shuffled),
                        "l1": dist_l1,
                    }
                )
            questions_report.append(
                {
                    "question": qid,
                    "n_options": len(criteria),
                    "canonical_order": list(criteria),
                    "shuffles": shuffle_rows,
                    "max_l1": max(row["l1"] for row in shuffle_rows),
                }
            )
        return {
            "model": self.model,
            "model_reported": self.model_reported,
            "n_shuffles": n_shuffles,
            "seed": seed,
            "max_l1": max_l1,
            "questions": questions_report,
        }

    def _record_usage(self, body: dict) -> None:
        usage = body.get("usage") if isinstance(body, dict) else None
        if not isinstance(usage, dict):
            return
        inp = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
        out = int(usage.get("output_tokens") or 0)
        cached = int(usage.get("cached_tokens") or 0)
        with self._lock:
            self._usage["requests"] += 1
            self._usage["input_tokens"] += inp
            self._usage["prompt_tokens"] += inp
            self._usage["output_tokens"] += out
            self._usage["cached_tokens"] += cached

    def _post(self, payload: dict) -> dict:
        if not self.api_key:
            raise InferenceError(
                f"set ${TYPESAFE_API_KEY_ENV} (or ${TYPESAFE_API_KEY_ENV_FALLBACK}) "
                "for the TypeSafe Jev API"
            )
        body = http_json(
            f"{self.base_url}/v1/systemone",
            payload,
            timeout=self.timeout,
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        if not isinstance(body, dict):
            raise InferenceError("TypeSafe response is not a JSON object")
        reported = body.get("model")
        if reported is not None:
            self.model_reported = str(reported)
        self._record_usage(body)
        return body


class OpenJevSGLang:
    """openjev served by SGLang (`serve_sglang.sh`, `--is-embedding`).

    Calls /classify directly rather than the openjev Decisions gateway: the
    gateway caps a question at 64 options and the rule question has 101. The
    probability rule is the gateway's: P(entailment) per option, normalised
    over the options of the question (`normalized_entailment_v1`).
    """

    def __init__(
        self,
        base_url: str = OPENJEV_BASE_URL,
        model: str = OPENJEV_MODEL,
        *,
        timeout: float = JEV_TIMEOUT_S,
        max_workers: int = JEV_MAX_WORKERS,
        batch: int = OPENJEV_CLASSIFY_BATCH,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_workers = max_workers
        self.batch = batch
        self._lock = threading.Lock()
        self._usage = {"pairs": 0, "requests": 0, "prompt_tokens": 0, "cached_tokens": 0}

    def usage(self) -> dict:
        """Cumulative. cached_tokens stays 0 if the server does not report it."""
        with self._lock:
            return dict(self._usage)

    def decide_many(self, requests: Sequence[JevRequest]) -> list[Answers]:
        texts: list[str] = []
        index: list[tuple[int, str, str]] = []
        for i, request in enumerate(requests):
            premise = request.state.strip()
            if len(premise) > OPENJEV_MAX_STATE_CHARS:
                raise InferenceError(f"state is {len(premise)} chars > {OPENJEV_MAX_STATE_CHARS}")
            for qid, question in request.questions.items():
                instr = str(question.get("instructions", "")).strip()
                for key, crit in question["criteria"].items():
                    hypothesis = HYPOTHESIS.format(
                        instr=instr, label=key, crit=key if crit is None else crit
                    )
                    texts.append(NLI_TEMPLATE.format(premise=premise, hypothesis=hypothesis))
                    index.append((i, qid, key))
        entail = self._classify(texts)
        out: list[Answers] = [{qid: {} for qid in r.questions} for r in requests]
        for (i, qid, key), e in zip(index, entail, strict=True):
            out[i][qid][key] = e
        return [{qid: _normalise(dist) for qid, dist in ans.items()} for ans in out]

    def check(self) -> str:
        http_json(f"{self.base_url}/health", timeout=self.timeout)
        pair = NLI_TEMPLATE.format(
            premise="A man is playing a guitar.", hypothesis="Someone is making music."
        )
        e = self._classify_chunk([pair])[0]
        before = self.usage()
        self._classify_chunk([pair])
        after = self.usage()
        prompt = after["prompt_tokens"] - before["prompt_tokens"]
        cached = after["cached_tokens"] - before["cached_tokens"]
        cache = (
            f"repeat pair: {cached}/{prompt} prompt tokens cached"
            if prompt
            else "server reports no token counts"
        )
        return f"openjev {self.base_url} P(entailment) on a sanity pair = {e:.3f}; {cache}"

    def _classify(self, texts: list[str]) -> list[float]:
        chunks = [texts[i : i + self.batch] for i in range(0, len(texts), self.batch)]
        if not chunks:
            return []
        with ThreadPoolExecutor(max_workers=max(1, min(self.max_workers, len(chunks)))) as pool:
            parts = list(pool.map(self._classify_chunk, chunks))
        return [e for part in parts for e in part]

    def _classify_chunk(self, chunk: list[str]) -> list[float]:
        body = http_json(f"{self.base_url}/classify", {"text": chunk}, timeout=self.timeout)
        rows = body if isinstance(body, list) else [body]
        if len(rows) != len(chunk):
            raise InferenceError(f"/classify returned {len(rows)} rows for {len(chunk)} inputs")
        out = []
        prompt_tokens = cached_tokens = 0
        for row in rows:
            logits = row.get("embedding") if isinstance(row, dict) else None
            if not isinstance(logits, list) or len(logits) != 3:
                raise InferenceError("/classify row has no 3-logit embedding")
            out.append(_entailment(logits))
            meta = row.get("meta_info") or {}
            prompt_tokens += int(meta.get("prompt_tokens") or 0)
            cached_tokens += int(meta.get("cached_tokens") or 0)
        with self._lock:
            self._usage["pairs"] += len(chunk)
            self._usage["requests"] += 1
            self._usage["prompt_tokens"] += prompt_tokens
            self._usage["cached_tokens"] += cached_tokens
        return out


def _entailment(logits: list[float]) -> float:
    top = max(logits)
    exps = [math.exp(z - top) for z in logits]
    return exps[ENTAILMENT] / sum(exps)


def _normalise(dist: Distribution) -> Distribution:
    total = sum(dist.values())
    if total <= 0:
        return {k: 1.0 / len(dist) for k in dist}
    return {k: v / total for k, v in dist.items()}


def _check_answers(answers: Answers, request: JevRequest) -> None:
    for qid, question in request.questions.items():
        dist = answers.get(qid)
        if dist is None:
            raise InferenceError(f"no answer for question {qid!r}")
        expected = set(request.canonical_keys.get(qid) or ())
        if not expected:
            if question.get("type") == "noul":
                expected = {"silence", "publish"}
            else:
                expected = set(question["criteria"])
        if set(dist) != expected:
            raise InferenceError(f"answer {qid!r} keys do not match its options")
        if not all(math.isfinite(p) and p >= 0 for p in dist.values()) or sum(dist.values()) <= 0:
            raise InferenceError(f"answer {qid!r} is not a probability distribution")


def _top(dist: Distribution, k: int = TOP_K_LOGGED) -> list[list]:
    ranked = sorted(dist.items(), key=lambda kv: kv[1], reverse=True)[:k]
    return [[key, round(p, 4)] for key, p in ranked]

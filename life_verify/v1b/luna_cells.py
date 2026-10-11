"""Luna cell adapters for TASK_LIFE_REASONING_CELLS (Responses + Decisions).

Completers return ``encode_decision`` strings so SimulationV1b / metrics /
acceptance stay unchanged. No API calls from prompt builders / dry-run helpers.

B↔C parity (locked before smoke):
- Forced rule choice (101 keys; no ``unsolved`` in the model schema).
- ``say`` bound to ``inferred_rule`` (no separate say field; same as Jev
  ``decide_from_answers``).
- Catalog presentation shuffled by ``order_seed`` (Responses lines; Decisions
  averages P=4 criterion shuffles).
- ``task_answer`` always = engine apply of chosen rule (not model-emitted).
- Prompt has no stand jargon.
- C/D decode = ``sample``, matching ``JEV_DECODE`` / M_0 v1b cells.
"""

from __future__ import annotations

import hashlib
import json
import random
import threading
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from constitutional_life.cell.observation import CellObservation
from constitutional_life.cell.schema import (
    ParsedDecision,
    Publish,
    Silence,
    encode_decision,
    parse_decision,
)
from constitutional_life.model.jev import (
    COMMUNICATION_CRITERIA,
    QUESTION_ORDER,
    RULE_INSTRUCTIONS,
    SIGNAL_INSTRUCTIONS,
    Answers,
    JevRequest,
    build_request,
    decide_from_answers,
    rule_key,
    rule_options,
)
from constitutional_life.task.catalog import FunctionCatalog, build_catalog
from constitutional_life.v1a_constants import JEV_DECODE, SIGNAL_VALUES

# ---------------------------------------------------------------------------
# Catalog keys (shared by Responses enum and Decisions criteria)
# ---------------------------------------------------------------------------

# Stand-internal only (invalid/truncated after retry). Never offered in the schema.
UNSOLVED = "unsolved"
CATALOG_VERSION = "life_catalog_v1a_101"  # bump if catalog / key scheme changes
SCHEMA_NAME = "life_cell_decision_v2"


def catalog_keys(catalog: FunctionCatalog | None = None) -> list[str]:
    cat = catalog or build_catalog()
    return [rule_key(i) for i in range(len(cat.functions))]


def catalog_desc_by_key(catalog: FunctionCatalog | None = None) -> dict[str, str]:
    cat = catalog or build_catalog()
    return {rule_key(i): fn.description() for i, fn in enumerate(cat.functions)}


def catalog_version_digest(catalog: FunctionCatalog | None = None) -> str:
    descs = [catalog_desc_by_key(catalog)[k] for k in catalog_keys(catalog)]
    blob = CATALOG_VERSION + "\n" + "\n".join(descs)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def shuffled_catalog_keys(
    desc_by_key: dict[str, str],
    order_seed: int,
) -> list[str]:
    """Presentation order for Responses catalog lines (keys stay bound to descs)."""
    keys = list(desc_by_key)
    rng = random.Random(int(order_seed))
    # Avoid identity when possible (same spirit as Jev _shuffle_criteria).
    for _ in range(32):
        order = list(keys)
        rng.shuffle(order)
        if order != keys:
            return order
    return list(reversed(keys))


# ---------------------------------------------------------------------------
# Responses prompt + JSON schema
# ---------------------------------------------------------------------------

RESPONSES_DECISION_INSTRUCTIONS = """Decide for this cell now.

Return a single JSON object and nothing else with:
- inferred_rule: exactly one catalog key (R000…) for the hidden transformation.
- communication: either {"kind":"silence"} or
  {"kind":"publish","signal":<integer 0-7>}.
  If you publish, the named rule on the board is your inferred_rule.

Choose a catalog key even if unsure. Do not invent keys. Do not return reasoning text."""


def render_catalog_block(
    desc_by_key: dict[str, str],
    *,
    order: Sequence[str] | None = None,
) -> str:
    keys = list(order) if order is not None else sorted(
        desc_by_key, key=lambda k: int(k[1:])
    )
    lines = ["Rule catalog (choose by key):"]
    for key in keys:
        lines.append(f"{key}: {desc_by_key[key]}")
    return "\n".join(lines)


def build_responses_prompt(
    state: str,
    desc_by_key: dict[str, str],
    *,
    order_seed: int,
    instructions: str = RESPONSES_DECISION_INSTRUCTIONS,
) -> str:
    """Life state + shuffled keyed catalog + decision instructions."""
    order = shuffled_catalog_keys(desc_by_key, order_seed)
    return "\n\n".join(
        [
            state.rstrip(),
            render_catalog_block(desc_by_key, order=order),
            instructions.strip(),
        ]
    )


def decision_json_schema(desc_by_key: dict[str, str]) -> dict[str, Any]:
    """Strict JSON schema — forced rule choice; no task_answer; no say."""
    keys = sorted(desc_by_key, key=lambda k: int(k[1:]))
    signal_enum = list(range(8))
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["inferred_rule", "communication"],
        "properties": {
            "inferred_rule": {
                "type": "string",
                "enum": keys,
                "description": "Catalog key of the hidden transformation",
            },
            "communication": {
                "anyOf": [
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["kind"],
                        "properties": {"kind": {"type": "string", "const": "silence"}},
                    },
                    {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["kind", "signal"],
                        "properties": {
                            "kind": {"type": "string", "const": "publish"},
                            "signal": {"type": "integer", "enum": signal_enum},
                        },
                    },
                ]
            },
        },
    }


def responses_text_format(desc_by_key: dict[str, str]) -> dict[str, Any]:
    return {
        "format": {
            "type": "json_schema",
            "name": SCHEMA_NAME,
            "strict": True,
            "schema": decision_json_schema(desc_by_key),
        }
    }


# ---------------------------------------------------------------------------
# Map API JSON → encode_decision
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MappedCellDecision:
    raw_json: str
    decision: ParsedDecision
    inferred_key: str
    say_key: str | None
    ok: bool
    error: str | None


def map_responses_payload(
    payload: dict[str, Any],
    desc_by_key: dict[str, str],
    *,
    query: str,
    catalog: FunctionCatalog | None = None,
    channel: bool = True,
) -> MappedCellDecision:
    """Validate Responses JSON; bind say:=rule; task_answer:=rule.apply(query).

    With ``channel=False`` the engine parses ``no_channel`` (forbids a communication
    field). The model schema still asks for communication; we validate it, then
    encode with ``communication=None`` so parse succeeds. Bs bug 2026-10-10:
    encoding Silence under channel=False zeroed every non-source rule.
    """
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    try:
        # Reject leftover fields from older schema drafts.
        if "task_answer" in payload or (
            isinstance(payload.get("communication"), dict)
            and "say" in payload["communication"]
        ):
            raise ValueError("unexpected task_answer or communication.say")
        ikey = payload.get("inferred_rule")
        if not isinstance(ikey, str) or ikey not in desc_by_key:
            raise ValueError(f"inferred_rule must be a catalog key; got {ikey!r}")
        cat = catalog or build_catalog()
        options = rule_options(cat)
        rule = options[ikey]
        answer = rule.apply(query)
        inferred = rule.description()
        comm_raw = payload.get("communication")
        if not isinstance(comm_raw, dict):
            raise ValueError("communication missing")
        kind = comm_raw.get("kind")
        if kind == "silence":
            if set(comm_raw) != {"kind"}:
                raise ValueError("silence must have only kind")
            communication: Silence | Publish | None = Silence()
            say_key: str | None = None
        elif kind == "publish":
            signal = comm_raw.get("signal")
            if not isinstance(signal, int) or isinstance(signal, bool) or signal not in range(8):
                raise ValueError("signal must be int 0..7")
            # Jev parity: published name = chosen rule description.
            communication = Publish(signal=signal, say=inferred)
            say_key = ikey
        else:
            raise ValueError("communication.kind must be silence|publish")
        if not channel:
            # Engine no_channel schema: keys = task_answer + inferred_rule only.
            communication = None
            say_key = None
        decision = ParsedDecision(
            task_answer=answer,
            inferred_rule=inferred,
            communication=communication,
        )
        enc = encode_decision(decision)
        mode = "channel" if channel else "no_channel"
        pr = parse_decision(enc, mode=mode)
        if not pr.ok or pr.decision is None:
            raise ValueError(pr.error or "encode/parse failed")
        return MappedCellDecision(enc, pr.decision, ikey, say_key, True, None)
    except (TypeError, ValueError, KeyError) as exc:
        return MappedCellDecision(
            raw, _invalid_fallback(channel=channel), "", None, False, str(exc)
        )


def _invalid_fallback(*, channel: bool = True) -> ParsedDecision:
    """After failed retry only — not a legal model choice."""
    return ParsedDecision(
        task_answer="AAAA",
        inferred_rule=UNSOLVED,
        communication=Silence() if channel else None,
    )


def fallback_encode(*, channel: bool = True) -> str:
    return encode_decision(_invalid_fallback(channel=channel))


def assert_encode_logs_rule(enc: str, *, channel: bool, where: str) -> None:
    """Fail hard if a Completer encode would become ``inferred_rule=None`` in the engine.

    Invariant (Bs 2026-10-10): valid Completer output must parse under the active
    channel mode with a non-None rule — no silent drops into rule_history.
    """
    mode = "channel" if channel else "no_channel"
    pr = parse_decision(enc, mode=mode)
    if (
        not pr.ok
        or pr.decision is None
        or not pr.decision.inferred_rule
    ):
        raise RuntimeError(
            f"{where}: encode does not round-trip under mode={mode!r} "
            f"(ok={pr.ok}, error={pr.error!r}, "
            f"inferred={getattr(pr.decision, 'inferred_rule', None)!r}). "
            f"Refusing silent None in rule_history."
        )


# ---------------------------------------------------------------------------
# Responses Completer
# ---------------------------------------------------------------------------


@dataclass
class LunaResponsesCompleter:
    """Generative Luna cell via Responses API (effort=medium for arms A/B)."""

    client: Any  # LunaResponsesClient
    effort: str = "medium"
    catalog: FunctionCatalog = field(default_factory=build_catalog)
    max_workers: int = 16
    retry_invalid: bool = True
    use_structured: bool = True
    _desc: dict[str, str] = field(init=False, repr=False)
    _digest: str = field(init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _stats: dict[str, int] = field(
        default_factory=lambda: {
            "calls": 0,
            "invalid": 0,
            "retries": 0,
            "fallbacks": 0,
        },
        repr=False,
    )
    _records: list[dict] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        self._desc = catalog_desc_by_key(self.catalog)
        self._digest = catalog_version_digest(self.catalog)

    @property
    def model(self) -> str:
        return getattr(self.client, "model", "gpt-6-luna")

    def stats(self) -> dict[str, int]:
        with self._lock:
            return dict(self._stats)

    def usage(self) -> dict:
        u = getattr(self.client, "usage", None)
        return u() if callable(u) else {}

    def pop_records(self) -> list[dict]:
        rec, self._records = self._records, []
        return rec

    def prompt_for_obs(
        self,
        obs: CellObservation,
        *,
        channel: bool,
        order_seed: int,
    ) -> str:
        import constitutional_life.model.jev as jev_mod

        state = jev_mod.render_state(obs, channel)
        return build_responses_prompt(state, self._desc, order_seed=order_seed)

    def complete_batch(
        self,
        observations: Sequence[CellObservation],
        *,
        channel: bool,
        seeds: Sequence[int],
        order_seeds: Sequence[int] | None = None,
        **_kwargs,
    ) -> list[str]:
        if len(observations) != len(seeds):
            raise ValueError("observations and seeds must align")
        order = list(order_seeds) if order_seeds is not None else list(seeds)
        if len(order) != len(observations):
            raise ValueError("order_seeds and observations must align")

        def _one(item: tuple[CellObservation, int, int]) -> tuple[str, dict]:
            obs, seed, oseed = item
            return self._complete_one(obs, channel=channel, seed=seed, order_seed=oseed)

        items = list(zip(observations, seeds, order, strict=True))
        workers = max(1, min(self.max_workers, len(items) or 1))
        if workers == 1 or len(items) <= 1:
            results = [_one(it) for it in items]
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                results = list(pool.map(_one, items))
        raws: list[str] = []
        for raw, rec in results:
            raws.append(raw)
            self._records.append(rec)
        return raws

    def _complete_one(
        self,
        obs: CellObservation,
        *,
        channel: bool,
        seed: int,
        order_seed: int,
    ) -> tuple[str, dict]:
        prompt = self.prompt_for_obs(obs, channel=channel, order_seed=int(order_seed))
        # ``draw`` is a cache-key disambiguator only (not a sampling RNG seed).
        draw = int(seed) % (2**31)
        with self._lock:
            self._stats["calls"] += 1
        row = self._call(prompt, draw=draw)
        mapped = self._map_row(row, query=obs.query, channel=channel)
        retried = False
        if (not mapped.ok) and self.retry_invalid and not row.get("truncated"):
            with self._lock:
                self._stats["retries"] += 1
            retried = True
            prompt2 = prompt + (
                "\n\nYour previous output was invalid. Return only a JSON object "
                "with inferred_rule (a listed catalog key) and communication."
            )
            # Separate cache entry for the retry (draw offset); still not a sample seed.
            row = self._call(prompt2, draw=draw + 1000)
            mapped = self._map_row(row, query=obs.query, channel=channel)
        if not mapped.ok:
            with self._lock:
                self._stats["invalid"] += 1
                self._stats["fallbacks"] += 1
            enc = fallback_encode(channel=channel)
            ok = False
            err = mapped.error
            inferred_key = UNSOLVED
            say_key = None
        else:
            enc = encode_decision(mapped.decision)
            assert_encode_logs_rule(
                enc, channel=channel, where="LunaResponsesCompleter"
            )
            ok = True
            err = None
            inferred_key = mapped.inferred_key
            say_key = mapped.say_key
        rec = {
            "generation": obs.generation,
            "cell_id": obs.cell_id,
            "seed": seed,
            "order_seed": order_seed,
            "channel": channel,
            "effort": self.effort,
            "catalog_digest": self._digest,
            "ok": ok,
            "error": err,
            "retried": retried,
            "inferred_key": inferred_key,
            "say_key": say_key,
            "usage": row.get("usage"),
            "usd_list_rate": row.get("usd_list_rate"),
            "truncated": row.get("truncated"),
            "cache_hit": row.get("cache_hit"),
            "status": row.get("status"),
        }
        return enc, rec

    def _call(self, prompt: str, *, draw: int) -> dict:
        kwargs: dict[str, Any] = {
            "effort": self.effort,
            "draw": draw,
        }
        if self.use_structured and hasattr(self.client, "complete_structured"):
            return self.client.complete_structured(
                prompt,
                text_format=responses_text_format(self._desc),
                catalog_digest=self._digest,
                **kwargs,
            )
        return self.client.complete(prompt, **kwargs)

    def _map_row(
        self, row: dict, *, query: str, channel: bool = True
    ) -> MappedCellDecision:
        if row.get("truncated") or row.get("invalid"):
            return MappedCellDecision(
                row.get("text") or "",
                _invalid_fallback(channel=channel),
                "",
                None,
                False,
                "truncated_or_invalid",
            )
        text = (row.get("text") or "").strip()
        payload = row.get("parsed")
        if payload is None:
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:
                return MappedCellDecision(
                    text,
                    _invalid_fallback(channel=channel),
                    "",
                    None,
                    False,
                    f"json: {exc.msg}",
                )
        if not isinstance(payload, dict):
            return MappedCellDecision(
                text,
                _invalid_fallback(channel=channel),
                "",
                None,
                False,
                "root not object",
            )
        return map_responses_payload(
            payload,
            self._desc,
            query=query,
            catalog=self.catalog,
            channel=channel,
        )


# ---------------------------------------------------------------------------
# Decisions backend + P=4 Completer
# ---------------------------------------------------------------------------


class LunaDecisionsJev:
    """JevBackend: one OpenAI Decisions choice call per question (no multi-q)."""

    def __init__(
        self,
        client: Any,
        *,
        max_workers: int = 8,
        model: str = "gpt-6-luna",
    ) -> None:
        self.client = client
        self.max_workers = max_workers
        self.model = model
        self._lock = threading.Lock()
        self._usage = {"requests": 0, "questions": 0}

    def usage(self) -> dict:
        cu = getattr(self.client, "usage", None)
        base = cu() if callable(cu) else {}
        with self._lock:
            return {**base, **dict(self._usage)}

    def check(self) -> str:
        probs = self.client.choose(
            "The sky is blue.",
            "Is the sky blue?",
            {"yes": "yes, the sky is blue", "no": "no, the sky is not blue"},
            qid="sky",
        )
        return f"OpenAI Decisions {self.model} sky_yes={probs.get('yes')}"

    def decide_many(self, requests: Sequence[JevRequest]) -> list[Answers]:
        workers = max(1, min(self.max_workers, len(requests) or 1))
        if workers == 1 or len(requests) <= 1:
            return [self.decide(r) for r in requests]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(self.decide, requests))

    def decide(self, request: JevRequest) -> Answers:
        out: Answers = {}
        for qid, question in request.questions.items():
            criteria = question["criteria"]
            if not isinstance(criteria, dict) or not criteria:
                raise RuntimeError(f"empty criteria for {qid}")
            probs = self.client.choose(
                request.state,
                question["instructions"],
                {str(k): str(v) for k, v in criteria.items()},
                qid=qid,
            )
            out[qid] = {str(k): float(probs[k]) for k in criteria}
            with self._lock:
                self._usage["requests"] += 1
                self._usage["questions"] += 1
        return out


@dataclass
class LunaDecisionsCompleter:
    """One-pass Luna Decisions cell with P option-order average (arms C/D).

    Default ``decode`` matches ``JEV_DECODE`` (``sample``) used by M_0 / JevCompleter
    in the v1b pilot — one draw from the P-averaged π per question.
    Cost: P × 3 Decisions API calls per cell per generation (rule, communication,
    signal).
    """

    client: Any
    catalog: FunctionCatalog = field(default_factory=build_catalog)
    P: int = 4
    decode: Literal["sample", "argmax"] = JEV_DECODE  # type: ignore[assignment]
    max_workers: int = 8
    _backend: LunaDecisionsJev = field(init=False, repr=False)
    _options: dict = field(init=False, repr=False)
    _records: list[dict] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if self.P < 1:
            raise ValueError("P must be >= 1")
        if self.decode not in ("sample", "argmax"):
            raise ValueError(f"decode must be sample|argmax; got {self.decode!r}")
        self._backend = LunaDecisionsJev(self.client, max_workers=self.max_workers)
        self._options = rule_options(self.catalog)

    @property
    def model(self) -> str:
        return self._backend.model

    @property
    def communication_type(self) -> str:
        return "choice"

    def usage(self) -> dict:
        return self._backend.usage()

    def pop_records(self) -> list[dict]:
        rec, self._records = self._records, []
        return rec

    def check(self) -> str:
        return self._backend.check()

    def complete_batch(
        self,
        observations: Sequence[CellObservation],
        *,
        channel: bool,
        seeds: Sequence[int],
        order_seeds: Sequence[int] | None = None,
        order_mode: str = "shuffle",
        **_kwargs,
    ) -> list[str]:
        if len(observations) != len(seeds):
            raise ValueError("observations and seeds must align")
        if order_seeds is None:
            order_seeds = seeds
        if len(order_seeds) != len(observations):
            raise ValueError("order_seeds and observations must align")

        raws: list[str] = []
        for obs, seed, oseed in zip(observations, seeds, order_seeds, strict=True):
            avg = self._averaged_answers(
                obs, channel=channel, order_seed=int(oseed), order_mode=order_mode
            )
            decision, record = decide_from_answers(
                avg,
                obs,
                channel,
                self._options,
                random.Random(int(seed)),
                self.decode,
            )
            self._records.append(
                {
                    "generation": obs.generation,
                    "cell_id": obs.cell_id,
                    "seed": seed,
                    "order_seed": oseed,
                    "P": self.P,
                    "decode": self.decode,
                    "order_mode": order_mode,
                    "api_calls": self.P * (3 if channel else 1),
                    **record,
                }
            )
            enc = encode_decision(decision)
            assert_encode_logs_rule(
                enc, channel=channel, where="LunaDecisionsCompleter"
            )
            raws.append(enc)
        return raws

    def _averaged_answers(
        self,
        obs: CellObservation,
        *,
        channel: bool,
        order_seed: int,
        order_mode: str,
    ) -> Answers:
        dists: list[Answers] = []
        for p in range(self.P):
            os = order_seed * 1009 + p * 17 + 1
            req = build_request(
                obs,
                channel,
                self._options,
                order_seed=os,
                order_mode=order_mode,  # type: ignore[arg-type]
                communication_type="choice",
            )
            dists.append(self._backend.decide(req))
        keys_by_q = {qid: list(dists[0][qid]) for qid in dists[0]}
        out: Answers = {}
        for qid, keys in keys_by_q.items():
            acc = {k: 0.0 for k in keys}
            for d in dists:
                for k in keys:
                    acc[k] += float(d[qid][k])
            s = sum(acc.values())
            if s <= 0:
                raise RuntimeError(f"zero mass on {qid}")
            out[qid] = {k: acc[k] / s for k in keys}
        return {qid: out[qid] for qid in QUESTION_ORDER if qid in out}


# ---------------------------------------------------------------------------
# Dry-run helpers (no API)
# ---------------------------------------------------------------------------


def sample_prompt_bundle(
    obs: CellObservation,
    *,
    channel: bool = True,
    k: int = 0,
    annotations=None,
    catalog: FunctionCatalog | None = None,
    order_seed: int = 5401,
) -> dict[str, Any]:
    """Build reviewable prompt surfaces without calling any model."""
    from life_verify.v1b.render import render_state_v1b

    cat = catalog or build_catalog()
    desc = catalog_desc_by_key(cat)
    state = render_state_v1b(obs, channel=channel, k=k, annotations=annotations)
    order = shuffled_catalog_keys(desc, order_seed)
    responses_prompt = build_responses_prompt(state, desc, order_seed=order_seed)
    schema = decision_json_schema(desc)
    rules = {rule_key(i): fn.description() for i, fn in enumerate(cat.functions)}
    decisions_preview = {
        "state_chars": len(state),
        "state_head": state[:800],
        "rule_instructions": RULE_INSTRUCTIONS,
        "n_rule_options": len(rules),
        "rule_options_head": [
            {"key": k, "description": rules[k]} for k in list(rules)[:8]
        ],
        "communication_instructions": "Should this cell publish a message this generation?",
        "communication_criteria": dict(COMMUNICATION_CRITERIA),
        "signal_instructions": SIGNAL_INSTRUCTIONS,
        "signal_criteria": {str(s): f"signal {s}" for s in SIGNAL_VALUES},
        "P": 4,
        "decode": JEV_DECODE,
        "api_calls_per_cell_gen": 4 * 3,
        "note": (
            "Decisions: catalog as choice criteria (bare fn.description(), same as "
            "L-VERIFY / Luna pair probes). P=4 order average × 3 questions = 12 API "
            f"calls/cell/gen. decode={JEV_DECODE!r} (= JEV_DECODE / M_0 v1b). "
            "say:=chosen rule (no separate say question)."
        ),
    }
    return {
        "catalog_version": CATALOG_VERSION,
        "catalog_digest": catalog_version_digest(cat),
        "schema_name": SCHEMA_NAME,
        "k": k,
        "channel": channel,
        "cell_id": obs.cell_id,
        "generation": obs.generation,
        "n_examples": len(obs.examples),
        "query": obs.query,
        "order_seed": order_seed,
        "catalog_order_head": order[:8],
        "state_chars": len(state),
        "responses_prompt_chars": len(responses_prompt),
        "responses_prompt": responses_prompt,
        "responses_instructions": RESPONSES_DECISION_INSTRUCTIONS,
        "json_schema": schema,
        "text_format": responses_text_format(desc),
        "decisions_preview": decisions_preview,
        "example_valid_json": {
            "inferred_rule": rule_key(0),
            "communication": {"kind": "publish", "signal": 0},
        },
        "example_silence_json": {
            "inferred_rule": rule_key(0),
            "communication": {"kind": "silence"},
        },
        "parity_notes": [
            "no unsolved in schema (forced 101-way like Decisions)",
            "no say field; publish binds say:=inferred_rule description",
            "no task_answer field; engine applies chosen rule",
            "catalog lines shuffled by order_seed",
            "descriptions = bare CanonicalFunction.description() (same as L-VERIFY)",
            f"C/D decode={JEV_DECODE!r} matches JEV_DECODE",
        ],
    }


def write_sample_review_md(bundle: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    schema_s = json.dumps(bundle["json_schema"], indent=2, ensure_ascii=False)
    ex_pub = json.dumps(bundle["example_valid_json"], indent=2, ensure_ascii=False)
    ex_sil = json.dumps(bundle["example_silence_json"], indent=2, ensure_ascii=False)
    dec = bundle["decisions_preview"]
    parity = "\n".join(f"- {x}" for x in bundle.get("parity_notes", []))
    body = f"""# Life reasoning cells — sample prompt review (no API)

Generated for manual review before any arm launch.
`catalog_digest={bundle["catalog_digest"]}` · schema=`{bundle["schema_name"]}` ·
k={bundle["k"]} · cell={bundle["cell_id"]} · examples={bundle["n_examples"]} ·
query=`{bundle["query"]}` · order_seed={bundle["order_seed"]} ·
catalog_order_head={bundle["catalog_order_head"]}

## B↔C parity

{parity}

## Adapter note

- **Responses (A/B):** state + keyed 101-rule catalog (shuffled by `order_seed`) +
  decision instructions; structured JSON (`inferred_rule` + `communication` only).
- **Decisions (C/D):** same state; catalog as choice criteria; **P={dec["P"]}** × 3
  questions = **{dec["api_calls_per_cell_gen"]}** API calls/cell/gen;
  decode=`{dec["decode"]}` (= `JEV_DECODE` / M_0 v1b).

## Responses — full prompt ({bundle["responses_prompt_chars"]} chars)

```
{bundle["responses_prompt"]}
```

## Responses — JSON schema

```json
{schema_s}
```

## Example model outputs

Publish (`say` filled by stand = description of `inferred_rule`):
```json
{ex_pub}
```

Silence (still must pick a rule key):
```json
{ex_sil}
```

## Decisions — surface preview

- rule instructions: `{dec["rule_instructions"]}`
- n_rule_options: {dec["n_rule_options"]} (no abstain)
- decode: `{dec["decode"]}` · api_calls/cell/gen: {dec["api_calls_per_cell_gen"]}
- first options: {json.dumps(dec["rule_options_head"], ensure_ascii=False)}
- communication criteria: {json.dumps(dec["communication_criteria"], ensure_ascii=False)}
- signal criteria: {json.dumps(dec["signal_criteria"], ensure_ascii=False)}
- note: {dec["note"]}

State head ({dec["state_chars"]} chars total):

```
{dec["state_head"]}
```
"""
    path.write_text(body)

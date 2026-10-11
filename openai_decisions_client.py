"""OpenAI Decisions API client for Stage-1 eval (placement only; no training).

POST /v1/decisions with one `choice` question. Duck-types TypeSafeClient.choose
so `typesafe_policy.TypeSafePolicy` can wrap it (P=4 order averaging).

Public beta (`gpt-6-luna`). Content refusals (e.g. partner word matches no
item) get one forced-choice retry; persistent refusal still aborts.
Disk cache content-keyed.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://api.openai.com"
DEFAULT_MODEL = "gpt-6-luna"
API_KEY_ENV = "OPENAI_API_KEY"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent / "artifacts" / "cache" / "decisions"
MIN_REQUEST_INTERVAL_S = 0.05
# Luna refuses when no option is entailed by the message (common on E1-P probes
# with an off-support word). One retry with this appendix; surface otherwise unchanged.
FORCE_CHOICE_APPENDIX = (
    " You must select exactly one of the listed options even if none matches "
    "the message perfectly."
)


class OpenAIDecisionsError(RuntimeError):
    pass


def _load_dotenv() -> None:
    """Disabled in public luna_life — use OPENAI_API_KEY in the environment."""
    return



def api_key_from_env() -> str:
    _load_dotenv()
    return os.environ.get(API_KEY_ENV, "")


def _math_isfinite(x: float) -> bool:
    return x == x and abs(x) != float("inf")


def _normalise(probs: dict[str, float]) -> dict[str, float]:
    s = sum(float(v) for v in probs.values())
    if s <= 0 or not all(_math_isfinite(float(v)) for v in probs.values()):
        raise OpenAIDecisionsError(f"non-normalisable probabilities: {probs!r}")
    return {k: float(v) / s for k, v in probs.items()}


def _cache_key(payload: dict, draw: int) -> str:
    q = payload["questions"][0]
    choices = q.get("choices") or []
    blob = json.dumps(
        {
            "model": payload["model"],
            "input": payload["input"],
            "name": q.get("name"),
            "instructions": q.get("instructions"),
            "choices": [(c.get("value"), c.get("description")) for c in choices],
            "draw": draw,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode()).hexdigest()


class OpenAIDecisionsClient:
    """One choice question per request. Compatible with TypeSafePolicy via choose()."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        api_key: str | None = None,
        cache_dir: Path | str | None = DEFAULT_CACHE_DIR,
        timeout: float = 120.0,
        use_cache: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key if api_key is not None else api_key_from_env()
        self.timeout = timeout
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_reported: str | None = None
        self.started_at_utc = datetime.now(timezone.utc).isoformat()
        self._lock = threading.Lock()
        self._last_request_t = 0.0
        self._usage = {
            "requests": 0,
            "cache_hits": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "prompt_tokens": 0,
            "cached_tokens": 0,
            "cache_write_tokens": 0,
            "refusals": 0,
            "forced_choice_retries": 0,
            "refusal_uniform": 0,
            # Per choose() call (live or cache hit): how the π was obtained.
            "outcomes_first": 0,
            "outcomes_forced": 0,
            "outcomes_uniform": 0,
        }
        self.last_outcome: str = "first"  # "first" | "forced" | "uniform"

    def usage(self) -> dict:
        with self._lock:
            return dict(self._usage)

    def _record_outcome(self, outcome: str, *, from_cache: bool = False) -> None:
        """Bump outcome counters; on cache hit also restore refusal tallies."""
        if outcome not in ("first", "forced", "uniform"):
            raise OpenAIDecisionsError(f"bad outcome {outcome!r}")
        self.last_outcome = outcome
        with self._lock:
            self._usage[f"outcomes_{outcome}"] += 1
            if not from_cache:
                return
            # Cache hits used to skip these — undercount vs live (e1p_val done row).
            if outcome == "uniform":
                self._usage["refusals"] += 1
                self._usage["forced_choice_retries"] += 1
                self._usage["refusal_uniform"] += 1
            elif outcome == "forced":
                self._usage["refusals"] += 1
                self._usage["forced_choice_retries"] += 1

    def stamp(self) -> dict:
        """Metadata for battery JSON (beta model may change)."""
        return {
            "vendor": "openai",
            "endpoint": f"{self.base_url}/v1/decisions",
            "model_requested": self.model,
            "model_reported": self.model_reported,
            "started_at_utc": self.started_at_utc,
            "usage": self.usage(),
        }

    def choose(
        self,
        state: str,
        instructions: str,
        criteria: dict[str, str],
        *,
        draw: int = 0,
        qid: str = "q",
    ) -> dict[str, float]:
        """Return normalised P(option) keyed by criteria keys. Order of criteria = presentation."""
        if not criteria:
            raise OpenAIDecisionsError("empty criteria")
        # Opaque values: Luna sometimes refuses when value==description==full
        # option text and the message is off-support ("triangular" vs no triangle).
        # Descriptions stay the human-readable option text (same surface as TypeSafe).
        keys = list(criteria.keys())
        choices = [
            {"value": f"opt_{i}", "description": str(criteria[k])}
            for i, k in enumerate(keys)
        ]
        value_to_key = {f"opt_{i}": k for i, k in enumerate(keys)}
        payload = {
            "model": self.model,
            "input": state,
            "questions": [
                {
                    "type": "choice",
                    "name": qid,
                    "instructions": instructions,
                    "choices": choices,
                }
            ],
        }
        key = _cache_key(payload, draw)
        if self.use_cache and self.cache_dir is not None:
            path = self.cache_dir / f"{key}.json"
            if path.is_file():
                try:
                    data = json.loads(path.read_text())
                except json.JSONDecodeError:
                    try:
                        path.unlink()
                    except OSError:
                        pass
                    data = None
                if data is not None:
                    with self._lock:
                        self._usage["cache_hits"] += 1
                    reported = data.get("model_reported")
                    if reported is not None:
                        self._check_model(str(reported))
                    if data.get("refusal"):
                        raise OpenAIDecisionsError(
                            f"cached refusal for {qid!r}: {data.get('refusal')}"
                        )
                    if data.get("refusal_uniform"):
                        outcome = "uniform"
                    elif data.get("forced_choice"):
                        outcome = "forced"
                    else:
                        outcome = str(data.get("outcome") or "first")
                    self._record_outcome(outcome, from_cache=True)
                    return _normalise(
                        {str(k): float(v) for k, v in data["probabilities"].items()}
                    )

        body = self._post(payload)
        answer = self._extract_answer(body, qid)
        forced = False
        uniform_fallback = False
        if answer.get("type") == "refusal":
            with self._lock:
                self._usage["refusals"] += 1
                self._usage["forced_choice_retries"] += 1
            forced = True
            # Retry 1: force appendix, same opaque values.
            payload_force = {
                "model": self.model,
                "input": state,
                "questions": [
                    {
                        "type": "choice",
                        "name": qid,
                        "instructions": instructions + FORCE_CHOICE_APPENDIX,
                        "choices": choices,
                    }
                ],
            }
            body = self._post(payload_force)
            answer = self._extract_answer(body, qid)
            if answer.get("type") == "refusal":
                # Retry 2: letter values (breaks some remaining refusals).
                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                if len(keys) > len(letters):
                    letter_choices = [
                        {"value": f"L{i}", "description": str(criteria[k])}
                        for i, k in enumerate(keys)
                    ]
                    letter_map = {f"L{i}": k for i, k in enumerate(keys)}
                else:
                    letter_choices = [
                        {"value": letters[i], "description": str(criteria[k])}
                        for i, k in enumerate(keys)
                    ]
                    letter_map = {letters[i]: k for i, k in enumerate(keys)}
                payload_letters = {
                    "model": self.model,
                    "input": state,
                    "questions": [
                        {
                            "type": "choice",
                            "name": qid,
                            "instructions": instructions + FORCE_CHOICE_APPENDIX,
                            "choices": letter_choices,
                        }
                    ],
                }
                with self._lock:
                    self._usage["forced_choice_retries"] += 1
                body = self._post(payload_letters)
                answer = self._extract_answer(body, qid)
                if answer.get("type") == "refusal":
                    # Last resort: uniform (do not abort — off-support probes are valid).
                    with self._lock:
                        self._usage["refusal_uniform"] += 1
                    out = _normalise({k: 1.0 for k in keys})
                    self._record_outcome("uniform")
                    if self.use_cache and self.cache_dir is not None:
                        path = self.cache_dir / f"{key}.json"
                        tmp = path.with_suffix(".json.tmp")
                        tmp.write_text(
                            json.dumps(
                                {
                                    "model": self.model,
                                    "model_reported": self.model_reported,
                                    "probabilities": out,
                                    "forced_choice": True,
                                    "refusal_uniform": True,
                                    "outcome": "uniform",
                                },
                                indent=2,
                            )
                        )
                        os.replace(tmp, path)
                    return out
                value_to_key = letter_map
        probs_list = answer.get("probabilities")
        if not isinstance(probs_list, list):
            raise OpenAIDecisionsError(
                f"Decisions answer {qid!r} missing probabilities list: {answer!r}"
            )
        raw = {str(p["value"]): float(p["probability"]) for p in probs_list}
        out = {}
        for vk, ck in value_to_key.items():
            if vk not in raw:
                raise OpenAIDecisionsError(
                    f"Decisions answer missing key {vk!r} in {list(raw)}"
                )
            out[ck] = float(raw[vk])
        out = _normalise(out)
        outcome = "forced" if forced else "first"
        self._record_outcome(outcome)

        if self.use_cache and self.cache_dir is not None:
            path = self.cache_dir / f"{key}.json"
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(
                json.dumps(
                    {
                        "model": self.model,
                        "model_reported": self.model_reported,
                        "probabilities": out,
                        "choice": value_to_key.get(str(answer.get("choice")), answer.get("choice")),
                        "confidence": answer.get("confidence"),
                        "forced_choice": forced,
                        "refusal_uniform": False,
                        "outcome": outcome,
                        "usage": body.get("usage"),
                    },
                    indent=2,
                )
            )
            os.replace(tmp, path)
        return out

    def check(self) -> str:
        """Cheap connectivity + model stamp."""
        probs = self.choose(
            "The sky is blue on a clear day.",
            "What color is the sky in the state?",
            {"blue": "blue", "green": "green"},
            draw=0,
            qid="smoke",
        )
        return (
            f"OpenAI Decisions {self.base_url} model={self.model_reported or self.model} "
            f"P(blue)={probs.get('blue', float('nan')):.3f}"
        )

    def probe_n_choices(self, n: int = 101) -> dict:
        """Live limit check (Life catalog = 101)."""
        criteria = {f"rule_{i:03d}": f"named rule option {i}" for i in range(n)}
        t0 = time.perf_counter()
        probs = self.choose(
            "Pick any catalog option. Prefer rule_000 if indifferent.",
            "Which rule name?",
            criteria,
            draw=0,
            qid="limit",
        )
        return {
            "n": n,
            "ok": len(probs) == n,
            "latency_s": time.perf_counter() - t0,
            "argmax": max(probs, key=probs.get),
            "usage": self.usage(),
            "model_reported": self.model_reported,
        }

    def _extract_answer(self, body: dict, qid: str) -> dict:
        answers = body.get("answers")
        if isinstance(answers, list):
            for a in answers:
                if isinstance(a, dict) and a.get("name") == qid:
                    return a
            if len(answers) == 1 and isinstance(answers[0], dict):
                return answers[0]
            raise OpenAIDecisionsError(f"no answer named {qid!r} in {answers!r}")
        if isinstance(answers, dict) and qid in answers:
            return answers[qid]
        raise OpenAIDecisionsError(f"unexpected answers shape: {type(answers)}")

    def _check_model(self, reported: str) -> None:
        if self.model_reported is None:
            self.model_reported = reported
            return
        if reported != self.model_reported:
            raise OpenAIDecisionsError(
                f"model version changed mid-run: was {self.model_reported!r}, "
                f"now {reported!r}"
            )

    def _record_usage(self, body: dict) -> None:
        usage = body.get("usage") if isinstance(body, dict) else None
        if not isinstance(usage, dict):
            with self._lock:
                self._usage["requests"] += 1
            return
        inp = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
        out = int(usage.get("output_tokens") or 0)
        details = usage.get("input_tokens_details") or {}
        cached = int(details.get("cached_tokens") or usage.get("cached_tokens") or 0)
        cache_w = int(details.get("cache_write_tokens") or 0)
        with self._lock:
            self._usage["requests"] += 1
            self._usage["input_tokens"] += inp
            self._usage["prompt_tokens"] += inp
            self._usage["output_tokens"] += out
            self._usage["cached_tokens"] += cached
            self._usage["cache_write_tokens"] += cache_w

    def _post(self, payload: dict) -> dict:
        if not self.api_key:
            raise OpenAIDecisionsError(f"set ${API_KEY_ENV} for OpenAI Decisions API")
        data = json.dumps(payload).encode()
        last_err: Exception | None = None
        for attempt in range(8):
            with self._lock:
                wait = MIN_REQUEST_INTERVAL_S - (time.monotonic() - self._last_request_t)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(
                f"{self.base_url}/v1/decisions",
                data=data,
                method="POST",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = json.loads(resp.read().decode())
                with self._lock:
                    self._last_request_t = time.monotonic()
                reported = body.get("model", self.model)
                self._check_model(str(reported) if reported is not None else self.model)
                self._record_usage(body)
                return body
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:1200]
                last_err = OpenAIDecisionsError(f"OpenAI Decisions HTTP {e.code}: {detail}")
                # 504 Cloudflare gateway timeout: docs say retry_after ≥ 120s.
                retryable = e.code in (429, 500, 502, 503, 504)
                if not retryable or attempt == 7:
                    raise last_err from e
                backoff = 2.0 ** attempt
                retry_after = None
                try:
                    hint = json.loads(detail)
                    if isinstance(hint, dict) and hint.get("retry_after") is not None:
                        retry_after = float(hint["retry_after"])
                except (json.JSONDecodeError, TypeError, ValueError):
                    pass
                if e.code == 504:
                    sleep_s = max(120.0, retry_after or 120.0)
                elif e.code == 429:
                    sleep_s = max(backoff, retry_after or backoff)
                else:
                    sleep_s = min(60.0, backoff)
                print(
                    json.dumps({
                        "retry": True,
                        "http": e.code,
                        "attempt": attempt + 1,
                        "sleep_s": sleep_s,
                    }),
                    flush=True,
                )
                time.sleep(sleep_s)
            except TimeoutError as e:
                last_err = OpenAIDecisionsError(f"timeout after {self.timeout}s: {e}")
                if attempt == 7:
                    raise last_err from e
                time.sleep(min(60.0, 2.0 ** attempt))
            except urllib.error.URLError as e:
                last_err = OpenAIDecisionsError(f"URL error: {e}")
                if attempt == 7:
                    raise last_err from e
                time.sleep(min(60.0, 2.0 ** attempt))
        raise last_err or OpenAIDecisionsError("request failed")

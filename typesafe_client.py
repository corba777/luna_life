"""TypeSafe Jev HTTP client for Stage 1 eval (evaluation only; no training).

POST /v1/systemone with one choice question. Disk cache keyed by
(model, state, instructions, criteria_order, draw) so reruns and cross-play
cost nothing. Records usage. On API error: raise — except bounded backoff on 429/503/529 overload.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_BASE_URL = "https://api.typesafe.ai"
DEFAULT_MODEL = "jev-1.13.0"
API_KEY_ENV = "TYPESAFE_API_KEY"
API_KEY_ENV_FALLBACK = "JEV_API_KEY"
DEFAULT_CACHE_DIR = Path(__file__).resolve().parent / "runs" / "typesafe" / "cache"
# Pace requests so Cloudflare/origin 520/529s are less likely (TYPESAFE_EVAL_PLAN §7).
# Slightly slower than 0.05 — 529 overload seen under sustained cold-cache runs.
MIN_REQUEST_INTERVAL_S = 0.12


class TypeSafeError(RuntimeError):
    pass


def _load_dotenv() -> None:
    """Disabled in public luna_life — no .env files."""
    return



def api_key_from_env() -> str:
    _load_dotenv()
    for name in (API_KEY_ENV, API_KEY_ENV_FALLBACK):
        value = os.environ.get(name, "")
        if value:
            return value
    return ""


def glide_api_key_from_env() -> str:
    _load_dotenv()
    for name in ("GLIDE_API_KEY", "FASTINO_API_KEY"):
        value = os.environ.get(name, "")
        if value:
            return value
    return ""


GLIDE_BASE_URL = "https://api.fastino.ai"
GLIDE_MODEL = "fastino/glide"


def make_systemone_client(backend: str = "typesafe", **kwargs):
    """TypeSafe Jev or Fastino GLiDE — same System One schema."""
    if backend in ("typesafe", "jev"):
        return TypeSafeClient(**kwargs)
    if backend in ("glide", "glidemodel", "fastino"):
        cache = kwargs.pop("cache_dir", None)
        if cache is None:
            cache = Path(__file__).resolve().parent / "runs" / "glide" / "cache"
        key = kwargs.pop("api_key", None) or glide_api_key_from_env()
        return TypeSafeClient(
            base_url=kwargs.pop("base_url", GLIDE_BASE_URL),
            model=kwargs.pop("model", GLIDE_MODEL),
            api_key=key,
            cache_dir=cache,
            **kwargs,
        )
    raise ValueError(f"unknown systemone backend: {backend}")


def _cache_key(payload: dict, draw: int) -> str:
    # Must NOT sort criteria keys: presentation order is part of the TypeSafe input.
    # Encode questions' criteria as ordered lists of pairs.
    questions = {}
    for qid, q in payload["questions"].items():
        q2 = dict(q)
        if "criteria" in q2 and isinstance(q2["criteria"], dict):
            q2["criteria"] = list(q2["criteria"].items())  # preserves insertion order
        questions[qid] = q2
    blob = json.dumps(
        {
            "model": payload["model"],
            "state": payload["state"],
            "questions": questions,
            "draw": draw,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode()).hexdigest()


def _normalise(probs: dict[str, float]) -> dict[str, float]:
    s = sum(float(v) for v in probs.values())
    if s <= 0 or not all(math_isfinite(float(v)) for v in probs.values()):
        raise TypeSafeError(f"non-normalisable probabilities: {probs!r}")
    return {k: float(v) / s for k, v in probs.items()}


def math_isfinite(x: float) -> bool:
    return x == x and abs(x) != float("inf")


class TypeSafeClient:
    """One choice question per request. Content-keyed on-disk cache."""

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
        self._lock = threading.Lock()
        self._last_request_t = 0.0
        self._usage = {
            "requests": 0,
            "cache_hits": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "prompt_tokens": 0,
            "cached_tokens": 0,
        }

    def usage(self) -> dict:
        with self._lock:
            return dict(self._usage)

    def choose(
        self,
        state: str,
        instructions: str,
        criteria: dict[str, str],
        *,
        draw: int = 0,
        qid: str = "q",
    ) -> dict[str, float]:
        """Return normalised P(option) keyed by criteria keys. Order of criteria matters."""
        if not criteria:
            raise TypeSafeError("empty criteria")
        # Preserve insertion order in the posted payload (TypeSafe reads order).
        questions = {
            qid: {
                "type": "choice",
                "instructions": instructions,
                "criteria": dict(criteria),
            }
        }
        payload = {"model": self.model, "state": state, "questions": questions}
        key = _cache_key(payload, draw)
        if self.use_cache and self.cache_dir is not None:
            path = self.cache_dir / f"{key}.json"
            if path.is_file():
                try:
                    data = json.loads(path.read_text())
                except json.JSONDecodeError:
                    # Concurrent writers can leave a truncated/appended file; drop and refetch.
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
                    return _normalise({str(k): float(v) for k, v in data["probabilities"].items()})

        body = self._post(payload)
        answers = body.get("answers")
        if not isinstance(answers, dict) or qid not in answers:
            raise TypeSafeError(f"TypeSafe response missing answer {qid!r}")
        raw = answers[qid]
        probs = raw.get("probabilities") if isinstance(raw, dict) else None
        if not isinstance(probs, dict):
            raise TypeSafeError(f"TypeSafe answer {qid!r} has no probabilities")
        # Keys must cover criteria; drop extras, require all criteria keys.
        out = {}
        for k in criteria:
            if k not in probs:
                raise TypeSafeError(f"TypeSafe answer missing key {k!r} in {list(probs)}")
            out[k] = float(probs[k])
        out = _normalise(out)

        if self.use_cache and self.cache_dir is not None:
            path = self.cache_dir / f"{key}.json"
            tmp = path.with_suffix(".json.tmp")
            payload_disk = {
                "model": self.model,
                "model_reported": self.model_reported,
                "probabilities": out,
                "usage": body.get("usage"),
            }
            tmp.write_text(json.dumps(payload_disk, indent=2))
            os.replace(tmp, path)
        return out

    def check(self) -> str:
        body = self._post({
            "model": self.model,
            "state": "The sky is blue.",
            "questions": {"q": {"type": "noul", "instructions": "Is the sky blue?"}},
        })
        reported = body.get("model", self.model)
        self.model_reported = str(reported) if reported is not None else self.model
        return f"TypeSafe {self.base_url} model {self.model_reported}"

    def _check_model(self, reported: str) -> None:
        if self.model_reported is None:
            self.model_reported = reported
            return
        if reported != self.model_reported:
            raise TypeSafeError(
                f"model version changed mid-run: was {self.model_reported!r}, now {reported!r}"
            )

    def _record_usage(self, body: dict) -> None:
        usage = body.get("usage") if isinstance(body, dict) else None
        if not isinstance(usage, dict):
            with self._lock:
                self._usage["requests"] += 1
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
            raise TypeSafeError(
                f"set ${API_KEY_ENV} (or ${API_KEY_ENV_FALLBACK}) for the TypeSafe Jev API"
            )
        data = json.dumps(payload).encode()
        # Transient overload (429/503/529): bounded backoff. Other HTTP errors raise
        # immediately (no silent retry on auth/4xx).
        body: Any = None
        last_err: Exception | None = None
        for attempt in range(6):
            with self._lock:
                wait = MIN_REQUEST_INTERVAL_S - (time.monotonic() - self._last_request_t)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(
                f"{self.base_url}/v1/systemone",
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
                last_err = None
                break
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:500]
                last_err = TypeSafeError(f"TypeSafe HTTP {e.code}: {detail}")
                if e.code not in (429, 503, 529) or attempt == 5:
                    raise last_err from e
                time.sleep(min(60.0, 2.0 ** attempt))
            except TimeoutError as e:
                last_err = TypeSafeError(f"API read timeout after {self.timeout}s: {e}")
                if attempt == 5:
                    raise last_err from e
                time.sleep(min(60.0, 2.0 ** attempt))
            except urllib.error.URLError as e:
                reason = getattr(e, "reason", None)
                if isinstance(reason, TimeoutError) and attempt < 5:
                    last_err = TypeSafeError(f"API timeout: {e}")
                    time.sleep(min(60.0, 2.0 ** attempt))
                    continue
                raise TypeSafeError(f"TypeSafe network error: {e}") from e
            finally:
                with self._lock:
                    self._last_request_t = time.monotonic()
        if last_err is not None or body is None:
            raise last_err or TypeSafeError("TypeSafe empty response")
        if not isinstance(body, dict):
            raise TypeSafeError("TypeSafe response is not a JSON object")
        reported = body.get("model")
        if reported is not None:
            self._check_model(str(reported))
        self._record_usage(body)
        return body

"""OpenAI Responses client for gpt-6-luna mode comparison (placement only).

Cache key includes model, effort, max_output_tokens, prompt. Stores status and
incomplete_details. Truncated / incomplete responses are invalid.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai_decisions_client import api_key_from_env

DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_BASE = "https://api.openai.com"
DEFAULT_CACHE = Path(__file__).resolve().parent / "artifacts" / "cache" / "responses"
DEFAULT_MAX_OUTPUT = 8192

LIST_RATE = {
    "input_per_m": 0.10,
    "cached_input_per_m": 0.01,
    "cache_write_per_m": 0.125,
    "output_per_m": 0.50,
}


def usd_from_usage(u: dict | None) -> float:
    u = u or {}
    inp = int(u.get("input_tokens") or 0)
    details = u.get("input_tokens_details") or {}
    cached = int(details.get("cached_tokens") or u.get("cached_tokens") or 0)
    cache_write = int(details.get("cache_write_tokens") or 0)
    uncached = max(0, inp - cached)
    out = int(u.get("output_tokens") or 0)
    return (
        uncached * LIST_RATE["input_per_m"]
        + cached * LIST_RATE["cached_input_per_m"]
        + cache_write * LIST_RATE["cache_write_per_m"]
        + out * LIST_RATE["output_per_m"]
    ) / 1e6


def reasoning_tokens(u: dict | None) -> int:
    u = u or {}
    return int((u.get("output_tokens_details") or {}).get("reasoning_tokens") or 0)


def extract_text(body: dict) -> str:
    parts = []
    for item in body.get("output") or []:
        if item.get("type") != "message":
            continue
        for c in item.get("content") or []:
            if c.get("type") in ("output_text", "text"):
                parts.append(c.get("text") or "")
    return "\n".join(parts).strip()


def parse_opt_key(text: str, valid: set[str]) -> str | None:
    t = (text or "").strip()
    if t in valid:
        return t
    if not t:
        return None
    tok = t.split()[0].strip("`\"',.;:")
    return tok if tok in valid else None


def build_prompt(state: str, question: str, order: list[str]) -> str:
    lines = [state, "", question, "", "Options:"]
    for i, desc in enumerate(order):
        lines.append(f"opt_{i}: {desc}")
    lines.append("")
    lines.append("Answer with the key only (e.g. opt_0).")
    return "\n".join(lines)


class LunaResponsesClient:
    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        cache_dir: Path | str | None = DEFAULT_CACHE,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT,
        timeout: float = 600.0,
        use_cache: bool = True,
    ) -> None:
        self.model = model
        self.api_key = api_key_from_env()
        self.max_output_tokens = max_output_tokens
        self.timeout = timeout
        self.use_cache = use_cache
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        if self.cache_dir is not None:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.model_reported: str | None = None
        self.started_at_utc = datetime.now(timezone.utc).isoformat()
        self._lock = threading.Lock()
        self._usage = {
            "requests": 0,
            "cache_hits": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "reasoning_tokens": 0,
            "incomplete": 0,
            "invalid": 0,
        }

    def usage(self) -> dict:
        with self._lock:
            return dict(self._usage)

    def _cache_key(
        self,
        *,
        effort: str,
        prompt: str,
        draw: int,
        catalog_digest: str | None = None,
        structured: bool = False,
    ) -> str:
        blob = json.dumps(
            {
                "model": self.model,
                "effort": effort,
                "max_output_tokens": self.max_output_tokens,
                "prompt": prompt,
                "draw": draw,
                "catalog_digest": catalog_digest,
                "structured": structured,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode()).hexdigest()

    def _record(self, usage: dict | None, *, cache_hit: bool = False) -> None:
        with self._lock:
            if cache_hit:
                self._usage["cache_hits"] += 1
                return
            self._usage["requests"] += 1
            u = usage or {}
            self._usage["input_tokens"] += int(u.get("input_tokens") or 0)
            self._usage["output_tokens"] += int(u.get("output_tokens") or 0)
            self._usage["reasoning_tokens"] += reasoning_tokens(u)

    def _post(self, payload: dict) -> dict:
        body = json.dumps(payload).encode()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        last_err: Exception | None = None
        for attempt in range(5):
            req = urllib.request.Request(
                f"{DEFAULT_BASE}/v1/responses",
                data=body,
                headers=headers,
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                err = e.read().decode() if e.fp else ""
                if e.code in (429, 500, 502, 503, 529) and attempt < 4:
                    time.sleep(min(60, 2 ** attempt))
                    last_err = e
                    continue
                raise RuntimeError(f"Responses HTTP {e.code}: {err[:800]}") from e
            except (TimeoutError, TimeoutError, urllib.error.URLError, OSError) as e:
                last_err = e
                if attempt < 4:
                    time.sleep(min(60, 2 ** attempt))
                    continue
                raise RuntimeError(f"Responses transport error: {e!r}") from e
        raise RuntimeError(f"Responses failed after retries: {last_err!r}")

    def complete(
        self,
        prompt: str,
        *,
        effort: str,
        draw: int = 0,
        valid_keys: set[str] | None = None,
        text_format: dict | None = None,
        catalog_digest: str | None = None,
    ) -> dict[str, Any]:
        """Return {key, text, status, incomplete_details, usage, truncated, invalid, cache_hit}.

        ``draw`` is only a cache-key disambiguator (retries / duplicate prompts). It is
        not passed to the API as a sampling seed.
        """
        structured = text_format is not None
        ck = self._cache_key(
            effort=effort,
            prompt=prompt,
            draw=draw,
            catalog_digest=catalog_digest,
            structured=structured,
        )
        path = self.cache_dir / f"{ck}.json" if self.cache_dir else None

        if self.use_cache and path is not None and path.is_file():
            row = json.loads(path.read_text())
            # Refuse to reuse incomplete/empty v1-style rows even if key collided.
            if row.get("status") == "incomplete" or not (row.get("text") or "").strip():
                path.unlink(missing_ok=True)
            else:
                self._record(row.get("usage"), cache_hit=True)
                row = dict(row)
                row["cache_hit"] = True
                return self._finalize(row, valid_keys=valid_keys)

        payload: dict[str, Any] = {
            "model": self.model,
            "input": prompt,
            "reasoning": {"effort": effort},
            "max_output_tokens": self.max_output_tokens,
        }
        if text_format is not None:
            payload["text"] = text_format
        t0 = time.time()
        body = self._post(payload)
        elapsed = time.time() - t0
        model = body.get("model")
        if self.model_reported is None:
            self.model_reported = model
        elif model and model != self.model_reported:
            raise RuntimeError(f"model changed: {self.model_reported} → {model}")
        if model and not str(model).startswith("gpt-6-luna"):
            raise RuntimeError(f"unexpected model {model!r}")

        usage = body.get("usage") or {}
        status = body.get("status")
        incomplete = body.get("incomplete_details")
        text = extract_text(body)
        truncated = status == "incomplete" or (
            isinstance(incomplete, dict) and bool(incomplete)
        )
        parsed = None
        if structured and text and not truncated:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = None
        row = {
            "cache_hit": False,
            "model": model,
            "status": status,
            "incomplete_details": incomplete,
            "text": text,
            "parsed": parsed,
            "usage": usage,
            "elapsed_s": elapsed,
            "truncated": truncated,
            "max_output_tokens": self.max_output_tokens,
            "effort": effort,
            "structured": structured,
            "catalog_digest": catalog_digest,
        }
        self._record(usage, cache_hit=False)
        if path is not None:
            # Never persist truncated empties as reusable answers.
            if not truncated:
                path.write_text(json.dumps(row, indent=2) + "\n")
        return self._finalize(row, valid_keys=valid_keys)

    def complete_structured(
        self,
        prompt: str,
        *,
        effort: str,
        text_format: dict,
        draw: int = 0,
        catalog_digest: str | None = None,
    ) -> dict[str, Any]:
        """Responses call with ``text.format`` json_schema; no opt-key validation."""
        return self.complete(
            prompt,
            effort=effort,
            draw=draw,
            valid_keys=None,
            text_format=text_format,
            catalog_digest=catalog_digest,
        )

    def _finalize(self, row: dict, *, valid_keys: set[str] | None) -> dict:
        truncated = bool(row.get("truncated") or row.get("status") == "incomplete")
        text = row.get("text") or ""
        key = None
        if not truncated and valid_keys is not None:
            key = parse_opt_key(text, valid_keys)
        elif not truncated and valid_keys is None:
            key = text.strip().split()[0] if text.strip() else None
        invalid = truncated or (valid_keys is not None and key is None)
        if invalid:
            with self._lock:
                self._usage["invalid"] += 1
                if truncated:
                    self._usage["incomplete"] += 1
        out = dict(row)
        out["key"] = key
        out["truncated"] = truncated
        out["invalid"] = invalid
        out["usd_list_rate"] = usd_from_usage(row.get("usage"))
        out["reasoning_tokens"] = reasoning_tokens(row.get("usage"))
        return out

    def choose_key(
        self,
        state: str,
        question: str,
        order: list[str],
        *,
        effort: str,
        draw: int = 0,
        retry: bool = True,
    ) -> dict:
        valid = {f"opt_{i}" for i in range(len(order))}
        prompt = build_prompt(state, question, order)
        row = self.complete(prompt, effort=effort, draw=draw, valid_keys=valid)
        if row["invalid"] and retry and not row.get("truncated"):
            prompt2 = prompt + (
                "\nYou must select exactly one of the listed option keys."
            )
            row2 = self.complete(
                prompt2, effort=effort, draw=draw + 1000, valid_keys=valid
            )
            row2["retry_of_invalid"] = True
            return row2
        return row

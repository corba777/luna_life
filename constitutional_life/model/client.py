"""SGLang OpenAI-compatible client. Grammar on the decoder; parse is still the outcome.

Default server: http://192.168.78.32:30000
Transport failures raise. Malformed completions are returned as raw text and
scored as parse failures — no retry.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from constitutional_life.cell.grammar import grammar_for
from constitutional_life.cell.observation import CellObservation
from constitutional_life.cell.prompt import render_messages
from constitutional_life.v1a_constants import (
    INFERENCE_MAX_WORKERS,
    INFERENCE_TIMEOUT_S,
    MAX_OUTPUT_TOKENS,
    MODEL_ID,
    SGLANG_BASE_URL,
    TEMPERATURE,
)


class InferenceError(RuntimeError):
    """HTTP/transport failure. Not a parse failure."""


@dataclass(frozen=True, slots=True)
class ChatRequest:
    messages: list[dict[str, str]]
    seed: int
    ebnf: str
    model: str = MODEL_ID
    temperature: float = TEMPERATURE
    max_tokens: int = MAX_OUTPUT_TOKENS


def chat_payload(request: ChatRequest) -> dict:
    """Body for POST /v1/chat/completions. ebnf is top-level for SGLang."""
    return {
        "model": request.model,
        "messages": request.messages,
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "seed": request.seed,
        "ebnf": request.ebnf,
        "skip_special_tokens": True,
        "chat_template_kwargs": {"enable_thinking": False},
    }


def completion_text(payload: dict) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise InferenceError("response has no choices")
    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise InferenceError("choice has no message")
    content = message.get("content")
    if content is None:
        return ""
    if not isinstance(content, str):
        raise InferenceError("message.content is not a string")
    return content


class SglangClient:
    def __init__(
        self,
        base_url: str = SGLANG_BASE_URL,
        model: str = MODEL_ID,
        timeout: float = INFERENCE_TIMEOUT_S,
        max_workers: int = INFERENCE_MAX_WORKERS,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_workers = max_workers

    def complete_batch(
        self,
        observations: Sequence[CellObservation],
        *,
        channel: bool,
        seeds: Sequence[int],
    ) -> list[str]:
        if len(observations) != len(seeds):
            raise ValueError("observations and seeds must align")
        ebnf = grammar_for(channel)
        requests = [
            ChatRequest(
                messages=render_messages(obs, channel),
                seed=seed,
                ebnf=ebnf,
                model=self.model,
            )
            for obs, seed in zip(observations, seeds, strict=True)
        ]
        return self._send_many(requests)

    def list_models(self) -> list[str]:
        payload = self._get("/v1/models")
        data = payload.get("data") if isinstance(payload, dict) else None
        if not isinstance(data, list):
            return []
        names = []
        for row in data:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                names.append(row["id"])
        return names

    def _send_many(self, requests: list[ChatRequest]) -> list[str]:
        if len(requests) == 1:
            return [self._send_one(requests[0])]
        texts = [""] * len(requests)
        workers = min(self.max_workers, len(requests))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(self._send_one, request): i
                for i, request in enumerate(requests)
            }
            for future in as_completed(futures):
                texts[futures[future]] = future.result()
        return texts

    def _send_one(self, request: ChatRequest) -> str:
        payload = self._post("/v1/chat/completions", chat_payload(request))
        return completion_text(payload)

    def _get(self, path: str) -> dict:
        return _object(http_json(self.base_url + path, timeout=self.timeout))

    def _post(self, path: str, payload: dict) -> dict:
        return _object(
            http_json(self.base_url + path, payload, timeout=self.timeout)
        )


def http_json(
    url: str,
    payload: object | None = None,
    *,
    timeout: float,
    headers: dict[str, str] | None = None,
) -> object:
    """GET (payload None) or POST JSON. Every transport failure is InferenceError."""
    all_headers = {"Content-Type": "application/json", **(headers or {})}
    if payload is None:
        req = urllib.request.Request(url, method="GET", headers=all_headers)
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers=all_headers,
        )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise InferenceError(f"HTTP {exc.code} {url}: {detail[:500]}") from exc
    except TimeoutError as exc:
        raise InferenceError(f"timeout {url}: {exc}") from exc
    except ConnectionResetError as exc:
        raise InferenceError(f"reset {url}: {exc}") from exc
    except urllib.error.URLError as exc:
        raise InferenceError(f"connect {url}: {exc.reason}") from exc
    if not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InferenceError(f"non-JSON from {url}: {exc.msg}") from exc


def _object(parsed: object) -> dict:
    if not isinstance(parsed, dict):
        raise InferenceError("JSON root is not an object")
    return parsed

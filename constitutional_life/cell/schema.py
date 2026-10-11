"""DecisionV1a parse and validation. Parse failure is a measured outcome.

No silent retry. The grammar constrains the decoder; this module is the scorer
of whether a completion is a legal record.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

from constitutional_life.v1a_constants import SAY_BYTE_LIMIT

DecisionMode = Literal["channel", "no_channel"]

_ANSWER_LEN = 4
_ANSWER_ALPHABET = frozenset("ABCDEFGH")
_SIGNAL = frozenset(range(8))
_CHANNEL_KEYS = frozenset({"task_answer", "inferred_rule", "communication"})
_NO_CHANNEL_KEYS = frozenset({"task_answer", "inferred_rule"})
_SILENCE_KEYS = frozenset({"kind"})
_PUBLISH_KEYS = frozenset({"kind", "signal", "say"})


@dataclass(frozen=True, slots=True)
class Silence:
    kind: Literal["silence"] = "silence"


@dataclass(frozen=True, slots=True)
class Publish:
    signal: int
    say: str
    kind: Literal["publish"] = "publish"


Communication = Silence | Publish


@dataclass(frozen=True, slots=True)
class ParsedDecision:
    task_answer: str
    inferred_rule: str
    communication: Communication | None


@dataclass(frozen=True, slots=True)
class ParseResult:
    ok: bool
    decision: ParsedDecision | None
    error: str | None
    raw: str
    mode: DecisionMode


def encode_decision(decision: ParsedDecision) -> str:
    payload: dict[str, Any] = {
        "task_answer": decision.task_answer,
        "inferred_rule": decision.inferred_rule,
    }
    if decision.communication is not None:
        if isinstance(decision.communication, Silence):
            payload["communication"] = {"kind": "silence"}
        else:
            payload["communication"] = {
                "kind": "publish",
                "signal": decision.communication.signal,
                "say": decision.communication.say,
            }
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def parse_decision(raw: str, mode: DecisionMode = "channel") -> ParseResult:
    """Parse one completion. Never retries, never repairs."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return ParseResult(False, None, f"json: {exc.msg}", raw, mode)
    if not isinstance(payload, dict):
        return ParseResult(False, None, "json root is not an object", raw, mode)
    try:
        decision = _validate_payload(payload, mode)
    except ValueError as exc:
        return ParseResult(False, None, str(exc), raw, mode)
    return ParseResult(True, decision, None, raw, mode)


def publication_of(decision: ParsedDecision) -> Publish | None:
    if isinstance(decision.communication, Publish):
        return decision.communication
    return None


def _validate_payload(payload: dict[str, Any], mode: DecisionMode) -> ParsedDecision:
    expected = _CHANNEL_KEYS if mode == "channel" else _NO_CHANNEL_KEYS
    keys = set(payload)
    if keys != expected:
        raise ValueError(f"keys {sorted(keys)} != {sorted(expected)}")
    answer = _validate_answer(payload["task_answer"])
    rule = _validate_text(payload["inferred_rule"], field="inferred_rule", min_bytes=1)
    communication: Communication | None
    if mode == "no_channel":
        communication = None
    else:
        communication = _validate_communication(payload["communication"])
    return ParsedDecision(
        task_answer=answer,
        inferred_rule=rule,
        communication=communication,
    )


def _validate_answer(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("task_answer is not a string")
    if len(value) != _ANSWER_LEN or any(ch not in _ANSWER_ALPHABET for ch in value):
        raise ValueError("task_answer is not 4 symbols from A..H")
    return value


def _validate_communication(value: object) -> Communication:
    if not isinstance(value, dict):
        raise ValueError("communication is not an object")
    keys = set(value)
    kind = value.get("kind")
    if kind == "silence":
        if keys != _SILENCE_KEYS:
            raise ValueError("silence must have only kind")
        return Silence()
    if kind == "publish":
        if keys != _PUBLISH_KEYS:
            raise ValueError("publish must have kind, signal, say")
        signal = value["signal"]
        if not isinstance(signal, int) or isinstance(signal, bool) or signal not in _SIGNAL:
            raise ValueError("signal is not an integer 0..7")
        say = _validate_text(value["say"], field="say", min_bytes=1)
        return Publish(signal=signal, say=say)
    raise ValueError("communication.kind is not silence or publish")


def _validate_text(value: object, field: str, min_bytes: int) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field} is not a string")
    n = len(value.encode("utf-8"))
    if n < min_bytes:
        raise ValueError(f"{field} is empty")
    if n > SAY_BYTE_LIMIT:
        raise ValueError(f"{field} is {n} bytes > {SAY_BYTE_LIMIT}")
    if "\x00" in value:
        raise ValueError(f"{field} contains a null byte")
    return value

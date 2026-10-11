"""Engine-managed private memory. Depth 1. Never a chat history.

Excluded on purpose: inferred_rule, why, privateWhy, and messages that
are no longer in the observation inbox.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from constitutional_life.v1a_constants import MEMORY_DEPTH


@dataclass(frozen=True, slots=True)
class PrivateCellMemory:
    previous_task_answer: str | None = None
    previous_correct: bool | None = None
    previous_published: bool = False
    previous_signal: int | None = None
    previous_say: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict) -> PrivateCellMemory:
        return cls(
            previous_task_answer=payload.get("previous_task_answer"),
            previous_correct=payload.get("previous_correct"),
            previous_published=bool(payload.get("previous_published", False)),
            previous_signal=payload.get("previous_signal"),
            previous_say=payload.get("previous_say"),
        )


def empty_memory() -> PrivateCellMemory:
    assert MEMORY_DEPTH == 1
    return PrivateCellMemory()


def remember(
    *,
    task_answer: str | None,
    correct: bool,
    published: bool,
    signal: int | None,
    say: str | None,
) -> PrivateCellMemory:
    if not published:
        signal = None
        say = None
    return PrivateCellMemory(
        previous_task_answer=task_answer,
        previous_correct=correct,
        previous_published=published,
        previous_signal=signal,
        previous_say=say,
    )

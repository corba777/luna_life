"""Declarative constitution + observation. Identical instruction every cell.

The treatment is the inbox, not the wording. Do not name local / regional /
global. No-communication removes the channel from this text and from the
grammar; it does not drop a generated message after the fact.

Two renderings of the same constitution: `json` for generative cells (the
decoder emits a DecisionV1a record) and `typed` for Jev cells (the state is
scored against a closed set of options, nothing is generated). They share
every sentence except the one that says how the decision is returned.
"""

from __future__ import annotations

from typing import Literal

from constitutional_life.board.board import Message
from constitutional_life.board.geometry import N_CELLS
from constitutional_life.cell.memory import PrivateCellMemory
from constitutional_life.cell.observation import CellObservation
from constitutional_life.v1a_constants import GRID, SAY_BYTE_LIMIT

Rendering = Literal["json", "typed"]

_WORLD = f"""You are one cell among {N_CELLS} on a wrapping {GRID}×{GRID} grid.

Each cell has its own private task for this epoch: a hidden transformation of 4-symbol strings over A–H. Every cell in the epoch has the same hidden transformation, but different private examples and a different query each generation. There is no shared score. A correct answer is the hidden transformation applied to your query."""

_SEES_CHANNEL = "You see your private examples, your current query, a one-step memory of your last answer, and eight message slots from other cells. Unused slots are empty."
_SEES_NO_CHANNEL = "You see your private examples, your current query, and a one-step memory of your last answer."

_PUBLISH_JSON = f"You may publish at most one message this generation, or stay silent. A message has an integer signal 0–7 and a short text (at most {SAY_BYTE_LIMIT} UTF-8 bytes). Published messages become visible only from the next generation, and only to cells allowed to see them. Your task_answer and inferred_rule are not shown to other cells."
_PUBLISH_TYPED = "You may publish at most one message this generation, or stay silent. A message has an integer signal 0–7 and names one transformation. Published messages become visible only from the next generation, and only to cells allowed to see them. Your own rule choice and answer are not shown to other cells."

_TAIL_JSON_CHANNEL = """inferred_rule is required. Write the hidden transformation as you currently understand it.

Output a single JSON object and nothing else."""
_TAIL_JSON_NO_CHANNEL = """inferred_rule is required. Write the hidden transformation as you currently understand it. You cannot send or receive messages.

Output a single JSON object and nothing else."""
_TAIL_TYPED_CHANNEL = "Choose the hidden transformation from the listed options. The engine applies your chosen transformation to your query; that is your answer."
_TAIL_TYPED_NO_CHANNEL = "Choose the hidden transformation from the listed options. The engine applies your chosen transformation to your query; that is your answer. You cannot send or receive messages."

CONSTITUTION_CHANNEL = "\n\n".join([_WORLD, _SEES_CHANNEL, _PUBLISH_JSON, _TAIL_JSON_CHANNEL])
CONSTITUTION_NO_CHANNEL = "\n\n".join([_WORLD, _SEES_NO_CHANNEL, _TAIL_JSON_NO_CHANNEL])
CONSTITUTION_TYPED_CHANNEL = "\n\n".join([_WORLD, _SEES_CHANNEL, _PUBLISH_TYPED, _TAIL_TYPED_CHANNEL])
CONSTITUTION_TYPED_NO_CHANNEL = "\n\n".join([_WORLD, _SEES_NO_CHANNEL, _TAIL_TYPED_NO_CHANNEL])

OUTPUT_CHANNEL = (
    '{"task_answer":"<4 symbols A-H>","inferred_rule":"<text>",'
    '"communication":{"kind":"silence"} or '
    '{"kind":"publish","signal":<0-7>,"say":"<text>"}}'
)
OUTPUT_NO_CHANNEL = '{"task_answer":"<4 symbols A-H>","inferred_rule":"<text>"}'


def constitution_for(channel: bool, rendering: Rendering = "json") -> str:
    if rendering == "typed":
        return CONSTITUTION_TYPED_CHANNEL if channel else CONSTITUTION_TYPED_NO_CHANNEL
    return CONSTITUTION_CHANNEL if channel else CONSTITUTION_NO_CHANNEL


def render_user(
    obs: CellObservation,
    channel: bool = True,
    rendering: Rendering = "json",
) -> str:
    parts = [
        f"Cell {obs.cell_id} at row {obs.row} col {obs.col}.",
        f"Epoch {obs.epoch}, generation {obs.epoch_generation} of this epoch.",
        "",
        "Private examples:",
        _render_examples(obs.examples),
        "",
        f"Query: {obs.query}",
        "",
        _render_memory(obs.memory),
    ]
    if channel:
        parts.extend(["", _render_inbox(obs.inbox)])
    if rendering == "json":
        parts.extend(
            [
                "",
                "Output shape:",
                OUTPUT_CHANNEL if channel else OUTPUT_NO_CHANNEL,
            ]
        )
    return "\n".join(parts)


def render_prompt(obs: CellObservation, channel: bool = True) -> str:
    return constitution_for(channel) + "\n\n" + render_user(obs, channel)


def render_state(obs: CellObservation, channel: bool = True) -> str:
    """The Jev `state`: typed constitution + observation, no output shape."""
    return (
        constitution_for(channel, "typed")
        + "\n\n"
        + render_user(obs, channel, "typed")
    )


def render_messages(obs: CellObservation, channel: bool = True) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": constitution_for(channel)},
        {"role": "user", "content": render_user(obs, channel)},
    ]


def _render_examples(examples: list[tuple[str, str]]) -> str:
    if not examples:
        return "(none)"
    return "\n".join(f"  {x} -> {y}" for x, y in examples)


def _render_memory(memory: PrivateCellMemory) -> str:
    if memory.previous_correct is None and memory.previous_task_answer is None:
        return "Previous step: none."
    answer = memory.previous_task_answer or "missing"
    correct = "unknown" if memory.previous_correct is None else str(memory.previous_correct).lower()
    if memory.previous_published:
        pub = f"published signal={memory.previous_signal} say={memory.previous_say!r}"
    else:
        pub = "silence"
    return f"Previous step: answer={answer} correct={correct} {pub}."


def _render_inbox(inbox: list[Message | None]) -> str:
    lines = ["Visible messages (8 slots):"]
    for i, msg in enumerate(inbox, start=1):
        lines.append(f"  {i}. {_render_slot(msg)}")
    return "\n".join(lines)


def _render_slot(message: Message | None) -> str:
    if message is None:
        return "empty"
    return (
        f"sender={message.sender_id} generation={message.generation} "
        f"signal={message.signal} say={message.say!r}"
    )

"""v1b state rendering: v1a text + optional engine-check appendix on inbox slots."""

from __future__ import annotations

import constitutional_life.cell.prompt as prompt_mod
from constitutional_life.board.board import Message
from constitutional_life.cell.observation import CellObservation
from constitutional_life.cell.prompt import constitution_for, render_state, render_user

from life_verify.v1b.checks import SLOT_WITH_CHECK_FMT, SlotAnnotation

# Frozen constitution sentence (PREREG_LIFE_V1B.md). Present iff k > 0.
CHECK_CONSTITUTION_SENTENCE = (
    "When a delivered message names a transformation, the engine attaches check "
    "marks showing whether that transformation matches your private examples (✓) "
    "or not (✗)."
)


def constitution_v1b(
    channel: bool,
    k: int,
    *,
    rendering: str = "typed",
) -> str:
    base = constitution_for(channel, rendering)  # type: ignore[arg-type]
    if k <= 0 or not channel:
        return base
    # Place immediately after the v1a "You see …" sentence. Do not split on
    # blank lines — `_WORLD` itself contains `\n\n`.
    marker = prompt_mod._SEES_CHANNEL if channel else prompt_mod._SEES_NO_CHANNEL
    if marker not in base:
        return base + "\n\n" + CHECK_CONSTITUTION_SENTENCE
    return base.replace(marker, marker + "\n\n" + CHECK_CONSTITUTION_SENTENCE, 1)


def _render_slot_v1b(message: Message | None, ann: SlotAnnotation | None) -> str:
    if message is None:
        return "empty"
    check = ann.render_suffix() if ann is not None else ""
    return SLOT_WITH_CHECK_FMT.format(
        sender=message.sender_id,
        generation=message.generation,
        signal=message.signal,
        say=message.say,
        check=check,
    )


def _render_inbox_v1b(
    inbox: list[Message | None],
    annotations: list[SlotAnnotation | None] | None,
) -> str:
    lines = ["Visible messages (8 slots):"]
    anns = annotations if annotations is not None else [None] * len(inbox)
    if len(anns) != len(inbox):
        raise ValueError("annotations must align with inbox slots")
    for i, (msg, ann) in enumerate(zip(inbox, anns, strict=True), start=1):
        lines.append(f"  {i}. {_render_slot_v1b(msg, ann)}")
    return "\n".join(lines)


def render_user_v1b(
    obs: CellObservation,
    *,
    channel: bool = True,
    k: int = 0,
    annotations: list[SlotAnnotation | None] | None = None,
    rendering: str = "typed",
) -> str:
    if k <= 0:
        return render_user(obs, channel, rendering)  # type: ignore[arg-type]
    parts = [
        f"Cell {obs.cell_id} at row {obs.row} col {obs.col}.",
        f"Epoch {obs.epoch}, generation {obs.epoch_generation} of this epoch.",
        "",
        "Private examples:",
        prompt_mod._render_examples(obs.examples),
        "",
        f"Query: {obs.query}",
        "",
        prompt_mod._render_memory(obs.memory),
    ]
    if channel:
        parts.extend(["", _render_inbox_v1b(obs.inbox, annotations)])
    if rendering == "json":
        parts.extend(
            [
                "",
                "Output shape:",
                prompt_mod.OUTPUT_CHANNEL if channel else prompt_mod.OUTPUT_NO_CHANNEL,
            ]
        )
    return "\n".join(parts)


def render_state_v1b(
    obs: CellObservation,
    *,
    channel: bool = True,
    k: int = 0,
    annotations: list[SlotAnnotation | None] | None = None,
) -> str:
    """Jev state. At k=0 this is byte-identical to ``render_state(obs, channel)``."""
    if k <= 0:
        return render_state(obs, channel)
    return (
        constitution_v1b(channel, k, rendering="typed")
        + "\n\n"
        + render_user_v1b(
            obs, channel=channel, k=k, annotations=annotations, rendering="typed"
        )
    )

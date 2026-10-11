"""Engine-check annotations for delivered inbox slots (Life v1b).

Marks are always computed on the *recipient's* private examples, after delivery
and after any inbox permutation. Never copy marks from a donor.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from constitutional_life.board.board import Message
from constitutional_life.task.catalog import FunctionCatalog
from constitutional_life.task.dsl import parse_program
from constitutional_life.task.identify import Example

# Frozen line format (PREREG_LIFE_V1B.md). Do not change without an amendment.
CHECK_PAIR_FMT = "{x}→{y} {mark}"  # mark is ✓ or ✗
CHECK_SUFFIX_FMT = "  check: {pairs}"  # pairs joined by two spaces
SLOT_WITH_CHECK_FMT = (
    "sender={sender} generation={generation} signal={signal} say={say!r}{check}"
)


@dataclass(frozen=True, slots=True)
class ExampleCheck:
    x: str
    y_expected: str
    y_got: str | None
    ok: bool

    def render(self) -> str:
        mark = "✓" if self.ok else "✗"
        y = self.y_got if self.y_got is not None else "?"
        return CHECK_PAIR_FMT.format(x=self.x, y=y, mark=mark)


@dataclass(frozen=True, slots=True)
class SlotAnnotation:
    """Checks for one delivered (non-empty) slot."""

    checks: tuple[ExampleCheck, ...]

    def render_suffix(self) -> str:
        if not self.checks:
            return ""
        pairs = "  ".join(c.render() for c in self.checks)
        return CHECK_SUFFIX_FMT.format(pairs=pairs)

    def to_log(self) -> list[dict]:
        return [
            {
                "x": c.x,
                "y_expected": c.y_expected,
                "y_got": c.y_got,
                "ok": c.ok,
            }
            for c in self.checks
        ]


def k1_example_index(
    *,
    world_seed: int,
    generation: int,
    cell_id: int,
    n_examples: int = 2,
) -> int:
    """Which example is checked at k=1 — identical across arms of the same world."""
    if n_examples <= 0:
        raise ValueError("n_examples must be positive")
    payload = f"{world_seed}|{generation}|{cell_id}|check_k1".encode()
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") % n_examples


def resolve_named_rule(say: str, catalog: FunctionCatalog):
    try:
        program = parse_program(say)
    except ValueError:
        return None
    return catalog.canonicalize(program)


def select_examples_for_k(
    examples: list[Example],
    k: int,
    *,
    world_seed: int,
    generation: int,
    cell_id: int,
) -> list[Example]:
    if k <= 0:
        return []
    if not examples:
        return []
    if k >= len(examples):
        return list(examples)
    if k == 1:
        idx = k1_example_index(
            world_seed=world_seed,
            generation=generation,
            cell_id=cell_id,
            n_examples=len(examples),
        )
        return [examples[idx]]
    return list(examples[:k])


def check_rule_on_examples(
    say: str,
    examples: list[Example],
    catalog: FunctionCatalog,
) -> tuple[ExampleCheck, ...]:
    fn = resolve_named_rule(say, catalog)
    out: list[ExampleCheck] = []
    for x, y_exp in examples:
        if fn is None:
            out.append(ExampleCheck(x=x, y_expected=y_exp, y_got=None, ok=False))
            continue
        y_got = fn.apply(x)
        out.append(ExampleCheck(x=x, y_expected=y_exp, y_got=y_got, ok=(y_got == y_exp)))
    return tuple(out)


def annotate_inbox(
    *,
    examples: list[Example],
    inbox: list[Message | None],
    k: int,
    world_seed: int,
    generation: int,
    cell_id: int,
    catalog: FunctionCatalog,
) -> list[SlotAnnotation | None]:
    """One annotation per slot (None for empty / k=0)."""
    if k <= 0:
        return [None] * len(inbox)
    selected = select_examples_for_k(
        examples,
        k,
        world_seed=world_seed,
        generation=generation,
        cell_id=cell_id,
    )
    anns: list[SlotAnnotation | None] = []
    for msg in inbox:
        if msg is None:
            anns.append(None)
            continue
        checks = check_rule_on_examples(msg.say, selected, catalog)
        anns.append(SlotAnnotation(checks=checks))
    return anns

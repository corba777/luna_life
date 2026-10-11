"""Seeded source cells for Life v1b — hold and publish P_e without a model call."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from constitutional_life.cell.schema import ParsedDecision, Publish, encode_decision
from constitutional_life.sim.engine import SPARSE_SOLVER_IDS
from constitutional_life.sim.policy import StepDecision
from constitutional_life.task.catalog import CanonicalFunction

# Re-export the frozen four spaced cell ids (pairwise GRID//2 apart).
SOURCE_IDS: tuple[int, ...] = SPARSE_SOLVER_IDS
SOURCE_SIGNAL = 0


@contextmanager
def source_ids_override(ids: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    """Temporarily replace SOURCE_IDS (one-source or zero-source long-chain).

    Empty ``ids`` is allowed (arm B0: channel on, no seeded teacher). Callers that
    did ``from … import SOURCE_IDS`` keep a stale binding — use ``is_source`` /
    ``non_source_ids`` or re-read ``sources.SOURCE_IDS``.
    """
    global SOURCE_IDS
    old = SOURCE_IDS
    SOURCE_IDS = tuple(int(x) for x in ids)
    try:
        yield SOURCE_IDS
    finally:
        SOURCE_IDS = old


def is_source(cell_id: int, *, seeded: bool) -> bool:
    return seeded and cell_id in SOURCE_IDS


def source_step_decision(fn: CanonicalFunction, query: str) -> StepDecision:
    """Deterministic: hold P_e, publish say=P_e every generation, no Completer."""
    desc = fn.description()
    return StepDecision(
        answer=fn.apply(query),
        inferred_rule=desc,
        publish_say=desc,
        signal=SOURCE_SIGNAL,
        source="v1b_source",
        n_hypotheses=1,
        parse_valid=True,
        parse_error=None,
    )


def source_raw_decision(
    fn: CanonicalFunction,
    query: str,
    *,
    channel: bool = True,
) -> str:
    """JSON DecisionV1a for the Completer path (same behaviour as source_step_decision).

    With ``channel=False`` the v1a schema forbids a communication field — the
    source still *holds* ``P_e`` (inferred_rule / answer); it simply cannot publish.
    """
    desc = fn.description()
    if channel:
        comm: Publish | None = Publish(signal=SOURCE_SIGNAL, say=desc)
    else:
        comm = None
    return encode_decision(
        ParsedDecision(
            task_answer=fn.apply(query),
            inferred_rule=desc,
            communication=comm,
        )
    )


def non_source_ids(n_cells: int, *, seeded: bool) -> list[int]:
    if not seeded:
        return list(range(n_cells))
    src = set(SOURCE_IDS)
    return [cid for cid in range(n_cells) if cid not in src]

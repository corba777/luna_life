"""Agreement / cascade metrics. Independent of correctness unless noted.

Pre-registered for TypeSafe v1a (V1A_FREEZE): modal share, say-clusters,
propagation distance, and J − J_mode. Pure functions over one generation's
cell fields plus optional first-sighting map for propagation.

False lock requires majority convergence (modal_share ≥ FALSE_LOCK_MODAL_SHARE)
and a wrong modal rule — not merely modal ≠ P_e.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass

from constitutional_life.board.geometry import N_CELLS, chebyshev, neighbours
from constitutional_life.v1a_constants import FALSE_LOCK_MODAL_SHARE


@dataclass(frozen=True, slots=True)
class CellAgree:
    cell_id: int
    inferred_rule: str | None
    publish_say: str | None
    correct: bool
    expected: str
    query: str


@dataclass(frozen=True, slots=True)
class GenerationAgreement:
    generation: int
    epoch: int
    modal_rule: str | None
    modal_share: float
    n_chosen: int
    n_distinct_chosen: int
    j: float
    j_mode: float | None
    j_minus_j_mode: float | None
    n_published: int
    n_distinct_say: int
    max_say_cluster: int
    max_propagation: int | None
    false_modal: bool | None  # modal_rule != p_e when both known
    false_lock: bool | None  # false_modal and modal_share >= threshold
    true_lock: bool | None  # (not false_modal) and modal_share >= threshold


def is_false_lock(
    *,
    modal_share: float,
    false_modal: bool | None,
    threshold: float = FALSE_LOCK_MODAL_SHARE,
) -> bool | None:
    """Cascade false-lock: majority on a wrong rule. None if false_modal unknown."""
    if false_modal is None:
        return None
    return bool(false_modal) and modal_share >= threshold


def is_true_lock(
    *,
    modal_share: float,
    false_modal: bool | None,
    threshold: float = FALSE_LOCK_MODAL_SHARE,
) -> bool | None:
    """Cascade true-lock: majority on the correct rule. None if false_modal unknown."""
    if false_modal is None:
        return None
    return (not false_modal) and modal_share >= threshold


def moore_cluster_sizes(cell_ids: Sequence[int]) -> list[int]:
    """Connected-component sizes under Moore radius-1, on the torus."""
    if not cell_ids:
        return []
    remaining = set(cell_ids)
    sizes: list[int] = []
    while remaining:
        start = next(iter(remaining))
        stack = [start]
        remaining.remove(start)
        size = 0
        while stack:
            cid = stack.pop()
            size += 1
            for nb in neighbours(cid, 1):
                if nb in remaining:
                    remaining.remove(nb)
                    stack.append(nb)
        sizes.append(size)
    return sizes


def max_say_cluster(publishers: dict[int, str]) -> int:
    """Largest Moore component among cells that published the same say."""
    by_say: dict[str, list[int]] = defaultdict(list)
    for cid, say in publishers.items():
        by_say[say].append(cid)
    best = 0
    for ids in by_say.values():
        sizes = moore_cluster_sizes(ids)
        if sizes:
            best = max(best, max(sizes))
    return best


def max_propagation(
    publishers: dict[int, str],
    first_sighting: dict[str, tuple[int, int]],
    *,
    written_at: int,
) -> int | None:
    """Max Chebyshev distance from a say's first publisher to a later publisher.

    `first_sighting` maps say -> (origin_cell_id, origin_written_generation).
    Only counts publishers of says that originated earlier in the epoch.
    """
    best: int | None = None
    for cid, say in publishers.items():
        origin = first_sighting.get(say)
        if origin is None:
            continue
        origin_cid, origin_gen = origin
        if origin_gen >= written_at:
            continue
        if origin_cid == cid:
            continue
        dist = chebyshev(origin_cid, cid)
        best = dist if best is None else max(best, dist)
    return best


def generation_agreement(
    cells: Sequence[CellAgree],
    *,
    generation: int,
    epoch: int,
    p_e: str | None,
    apply_modal: Callable[[str, str], str | None] | None = None,
    publishers: dict[int, str] | None = None,
    first_sighting: dict[str, tuple[int, int]] | None = None,
    written_at: int | None = None,
) -> GenerationAgreement:
    """Summarise one generation.

    `apply_modal(rule_description, query) -> answer | None` scores J_mode when
    provided; otherwise j_mode is left None.
    """
    chosen = [c.inferred_rule for c in cells if c.inferred_rule]
    counts = Counter(chosen)
    modal_rule, modal_n = counts.most_common(1)[0] if counts else (None, 0)
    n_chosen = len(chosen)
    modal_share = modal_n / n_chosen if n_chosen else 0.0
    j = sum(1 for c in cells if c.correct) / N_CELLS

    j_mode: float | None = None
    j_minus: float | None = None
    if modal_rule is not None and apply_modal is not None:
        mode_correct = 0
        for c in cells:
            ans = apply_modal(modal_rule, c.query)
            if ans is not None and ans == c.expected:
                mode_correct += 1
        j_mode = mode_correct / N_CELLS
        j_minus = j - j_mode

    pubs = publishers if publishers is not None else {
        c.cell_id: c.publish_say for c in cells if c.publish_say
    }
    prop = None
    if first_sighting is not None and written_at is not None:
        prop = max_propagation(pubs, first_sighting, written_at=written_at)

    false_modal = None
    if modal_rule is not None and p_e is not None:
        false_modal = modal_rule != p_e
    false_lock = is_false_lock(modal_share=modal_share, false_modal=false_modal)
    true_lock = is_true_lock(modal_share=modal_share, false_modal=false_modal)

    return GenerationAgreement(
        generation=generation,
        epoch=epoch,
        modal_rule=modal_rule,
        modal_share=modal_share,
        n_chosen=n_chosen,
        n_distinct_chosen=len(counts),
        j=j,
        j_mode=j_mode,
        j_minus_j_mode=j_minus,
        n_published=len(pubs),
        n_distinct_say=len(set(pubs.values())),
        max_say_cluster=max_say_cluster(pubs),
        max_propagation=prop,
        false_modal=false_modal,
        false_lock=false_lock,
        true_lock=true_lock,
    )


def summarise_agreement(rows: Iterable[GenerationAgreement]) -> dict:
    """Run-level unsigned means. Safe for the pilot printout."""
    rows = list(rows)
    if not rows:
        return {"n_generations": 0}

    def mean(attr: str) -> float | None:
        vals = [getattr(r, attr) for r in rows if getattr(r, attr) is not None]
        return sum(vals) / len(vals) if vals else None  # type: ignore[arg-type]

    false_modal_gens = [r for r in rows if r.false_modal is True]
    false_lock_gens = [r for r in rows if r.false_lock is True]
    true_lock_gens = [r for r in rows if r.true_lock is True]
    # Per-epoch lock: last generation of each epoch (run remains the independent unit;
    # the registered primary is the fraction of epochs locked, not a binary run flag).
    by_epoch: dict[int, GenerationAgreement] = {}
    for r in rows:
        by_epoch[r.epoch] = r  # chronologically last write wins
    epoch_lasts = list(by_epoch.values())
    n_epochs = len(epoch_lasts)
    n_false_epochs = sum(1 for r in epoch_lasts if r.false_lock is True)
    n_true_epochs = sum(1 for r in epoch_lasts if r.true_lock is True)
    return {
        "n_generations": len(rows),
        "mean_modal_share": mean("modal_share"),
        "mean_j_mode": mean("j_mode"),
        "mean_j_minus_j_mode": mean("j_minus_j_mode"),
        "mean_max_say_cluster": mean("max_say_cluster"),
        "mean_max_propagation": mean("max_propagation"),
        "mean_n_distinct_chosen": mean("n_distinct_chosen"),
        "frac_false_modal_gens": len(false_modal_gens) / len(rows),
        "frac_false_lock_gens": len(false_lock_gens) / len(rows),
        "frac_true_lock_gens": len(true_lock_gens) / len(rows),
        "false_lock_threshold": FALSE_LOCK_MODAL_SHARE,
        "n_epochs": n_epochs,
        "frac_false_lock_epochs": n_false_epochs / n_epochs if n_epochs else None,
        "frac_true_lock_epochs": n_true_epochs / n_epochs if n_epochs else None,
        "last": {
            "modal_rule": rows[-1].modal_rule,
            "modal_share": rows[-1].modal_share,
            "j": rows[-1].j,
            "j_mode": rows[-1].j_mode,
            "j_minus_j_mode": rows[-1].j_minus_j_mode,
            "false_modal": rows[-1].false_modal,
            "false_lock": rows[-1].false_lock,
            "true_lock": rows[-1].true_lock,
            "max_say_cluster": rows[-1].max_say_cluster,
            "max_propagation": rows[-1].max_propagation,
        },
    }


def agreement_to_dict(row: GenerationAgreement) -> dict:
    return {
        "generation": row.generation,
        "epoch": row.epoch,
        "modal_rule": row.modal_rule,
        "modal_share": row.modal_share,
        "n_chosen": row.n_chosen,
        "n_distinct_chosen": row.n_distinct_chosen,
        "j": row.j,
        "j_mode": row.j_mode,
        "j_minus_j_mode": row.j_minus_j_mode,
        "n_published": row.n_published,
        "n_distinct_say": row.n_distinct_say,
        "max_say_cluster": row.max_say_cluster,
        "max_propagation": row.max_propagation,
        "false_modal": row.false_modal,
        "false_lock": row.false_lock,
        "true_lock": row.true_lock,
    }

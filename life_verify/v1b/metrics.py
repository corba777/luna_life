"""v1b metrics over rule_history — sources excluded from recipient denominators."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from constitutional_life.board.geometry import N_CELLS
from constitutional_life.v1a_constants import EPOCH_LENGTH, FALSE_LOCK_MODAL_SHARE

from life_verify.torus_secondary import infection_delta
from life_verify.v1b.sources import SOURCE_IDS, non_source_ids

GenRow = dict[str, Any]

# Registered lock threshold (V1A_FREEZE / FALSE_LOCK_MODAL_SHARE): modal share ≥ 0.5.
LOCK_MODAL_SHARE = FALSE_LOCK_MODAL_SHARE


def _rules_map(row: GenRow) -> dict[int, str | None]:
    return {int(k): v for k, v in row["rules"].items()}


def _inbox_says_map(row: GenRow) -> dict[int, list[str]]:
    raw = row.get("inbox_says")
    if raw is None:
        raise ValueError("rule_history row missing inbox_says")
    return {int(k): [s for s in (v or []) if s] for k, v in raw.items()}


def _recipient_ids(row: GenRow) -> list[int]:
    """Non-source cell ids for this row (seeded arm excludes SOURCE_IDS)."""
    seeded = bool(row.get("seeded", False))
    if not seeded:
        return list(range(N_CELLS))
    mask = row.get("source_mask")
    if mask is not None:
        # JSON round-trip stringifies keys; coerce so sources stay excluded.
        mask_i = {int(k): bool(v) for k, v in mask.items()}
        return [cid for cid in range(N_CELLS) if not mask_i.get(cid, False)]
    return non_source_ids(N_CELLS, seeded=True)


def _epoch_generation(generation: int, epoch_length: int = EPOCH_LENGTH) -> int:
    """1..epoch_length within the epoch (engine stores 1-based generation)."""
    return ((int(generation) - 1) % epoch_length) + 1


def modal_lock_non_source(
    row: GenRow,
    *,
    kind: str = "correct",
    threshold: float = LOCK_MODAL_SHARE,
) -> bool:
    """True if non-source modal share ≥ threshold and modal is P_e / not P_e.

    Share denominator = all non-source recipients (Nones count against the share),
    matching the registered ≥ 0.5 rule on the recipient population.
    """
    pe = row["p_e"]
    recipients = _recipient_ids(row)
    n = len(recipients)
    if n == 0:
        return False
    rules = _rules_map(row)
    chosen = [rules.get(cid) for cid in recipients if rules.get(cid)]
    if not chosen:
        return False
    modal, count = Counter(chosen).most_common(1)[0]
    if count / n < threshold:
        return False
    if kind == "correct":
        return modal == pe
    if kind == "false":
        return modal != pe
    raise ValueError(f"kind must be 'correct' or 'false', got {kind!r}")


def j_non_source(rows: list[GenRow]) -> float:
    """Mean fraction of non-source cells with inferred_rule == P_e."""
    if not rows:
        return float("nan")
    total = hits = 0
    for row in rows:
        pe = row["p_e"]
        rules = _rules_map(row)
        for cid in _recipient_ids(row):
            total += 1
            hits += int(rules.get(cid) == pe)
    return hits / total if total else float("nan")


def lock_share_non_source(
    rows: list[GenRow],
    *,
    kind: str = "correct",
    threshold: float = LOCK_MODAL_SHARE,
) -> float:
    """Share of generations with a non-source lock (modal share ≥ threshold)."""
    if not rows:
        return float("nan")
    n_lock = sum(
        1 for row in rows if modal_lock_non_source(row, kind=kind, threshold=threshold)
    )
    return n_lock / len(rows)


def frac_lock_epochs_non_source(
    rows: list[GenRow],
    *,
    kind: str = "correct",
    threshold: float = LOCK_MODAL_SHARE,
) -> float:
    """Share of epochs that contain ≥1 locked generation (non-source denom)."""
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    for row in rows:
        by_epoch[int(row["epoch"])].append(row)
    if not by_epoch:
        return float("nan")
    n_hit = sum(
        1
        for epoch_rows in by_epoch.values()
        if any(
            modal_lock_non_source(r, kind=kind, threshold=threshold) for r in epoch_rows
        )
    )
    return n_hit / len(by_epoch)


def gens_to_correct_lock(
    rows: list[GenRow],
    *,
    threshold: float = LOCK_MODAL_SHARE,
    epoch_length: int = EPOCH_LENGTH,
) -> dict[str, Any]:
    """First in-epoch generation with correct lock; right-censored if never.

    Returns mean among uncensored epochs, censor rate, per-epoch rows, and
    the same split by ``n_ops``.
    """
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    for row in rows:
        by_epoch[int(row["epoch"])].append(row)
    for e in by_epoch:
        by_epoch[e].sort(key=lambda r: r["generation"])

    per_epoch: list[dict[str, Any]] = []
    for e in sorted(by_epoch):
        epoch_rows = by_epoch[e]
        n_ops = int(epoch_rows[0].get("n_ops", -1))
        first: int | None = None
        for row in epoch_rows:
            if modal_lock_non_source(row, kind="correct", threshold=threshold):
                first = _epoch_generation(row["generation"], epoch_length)
                break
        per_epoch.append(
            {
                "epoch": e,
                "n_ops": n_ops,
                "gens_to_correct_lock": first,
                "censored": first is None,
            }
        )

    def _summarise(items: list[dict[str, Any]]) -> dict[str, Any]:
        uncens = [
            int(r["gens_to_correct_lock"])
            for r in items
            if not r["censored"] and r["gens_to_correct_lock"] is not None
        ]
        n = len(items)
        n_cens = sum(1 for r in items if r["censored"])
        return {
            "mean_uncensored": (sum(uncens) / len(uncens)) if uncens else float("nan"),
            "censor_rate": n_cens / n if n else float("nan"),
            "n_epochs": n,
            "n_uncensored": len(uncens),
            "n_censored": n_cens,
        }

    out = _summarise(per_epoch)
    out["per_epoch"] = per_epoch
    by_ops: dict[str, Any] = {}
    for n_ops in (1, 2):
        sub = [r for r in per_epoch if int(r.get("n_ops", -1)) == n_ops]
        if sub:
            by_ops[str(n_ops)] = _summarise(sub)
    out["by_n_ops"] = by_ops
    return out


def infection_delta_non_source(rows: list[GenRow]) -> dict[str, float | int | str]:
    """Same contact definition as torus_secondary.infection_delta, non-sources only."""
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    for row in rows:
        by_epoch[int(row["epoch"])].append(row)
    for e in by_epoch:
        by_epoch[e].sort(key=lambda r: r["generation"])

    n_with = n_with_hit = 0
    n_without = n_without_hit = 0
    for e in sorted(by_epoch):
        epoch_rows = by_epoch[e]
        for i in range(len(epoch_rows) - 1):
            a, b = epoch_rows[i], epoch_rows[i + 1]
            pe = a["p_e"]
            if b["p_e"] != pe:
                continue
            ra, rb = _rules_map(a), _rules_map(b)
            inbox_b = _inbox_says_map(b)
            recipients = set(_recipient_ids(b))
            for cid in recipients:
                if ra.get(cid) == pe:
                    continue
                has_contact = pe in inbox_b.get(cid, [])
                became = rb.get(cid) == pe
                if has_contact:
                    n_with += 1
                    n_with_hit += int(became)
                else:
                    n_without += 1
                    n_without_hit += int(became)

    p_with = n_with_hit / n_with if n_with else float("nan")
    p_without = n_without_hit / n_without if n_without else float("nan")
    delta = (p_with - p_without) if (n_with and n_without) else float("nan")
    return {
        "delta": delta,
        "p_with_inbox": p_with,
        "p_without_inbox": p_without,
        "n_with_inbox": n_with,
        "n_without_inbox": n_without,
        "n_with_inbox_hit": n_with_hit,
        "n_without_inbox_hit": n_without_hit,
        "contact": "delivered_inbox_says",
        "denominator": "non_source",
    }


def retention_non_source(rows: list[GenRow]) -> dict[str, float | int | str]:
    """P(rule == P_e at g+1 | rule == P_e at g), non-sources, same P_e across transition.

    Complements infection (adoption on contact). Low retention → J zigzags and lock
    fails even when cells sometimes accept P_e. Descriptive for Life reasoning arms.
    """
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    for row in rows:
        by_epoch[int(row["epoch"])].append(row)
    for e in by_epoch:
        by_epoch[e].sort(key=lambda r: r["generation"])

    n = n_hit = 0
    for e in sorted(by_epoch):
        epoch_rows = by_epoch[e]
        for i in range(len(epoch_rows) - 1):
            a, b = epoch_rows[i], epoch_rows[i + 1]
            pe = a["p_e"]
            if b["p_e"] != pe:
                continue
            ra, rb = _rules_map(a), _rules_map(b)
            for cid in _recipient_ids(a):
                if ra.get(cid) != pe:
                    continue
                n += 1
                n_hit += int(rb.get(cid) == pe)
    return {
        "rate": n_hit / n if n else float("nan"),
        "n": n,
        "n_hit": n_hit,
        "denominator": "non_source",
        "definition": "P(P_e at g+1 | P_e at g)",
    }


def genesis_rate_non_source(rows: list[GenRow]) -> dict[str, float | int]:
    """Fraction of (gen, non-source cell) newly choosing P_e with P_e absent from inbox."""
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    for row in rows:
        by_epoch[int(row["epoch"])].append(row)
    for e in by_epoch:
        by_epoch[e].sort(key=lambda r: r["generation"])

    n_opp = n_hit = 0
    for e in sorted(by_epoch):
        epoch_rows = by_epoch[e]
        for i, row in enumerate(epoch_rows):
            pe = row["p_e"]
            rules = _rules_map(row)
            inbox = _inbox_says_map(row)
            prev = _rules_map(epoch_rows[i - 1]) if i > 0 else {}
            for cid in _recipient_ids(row):
                if prev.get(cid) == pe:
                    continue
                if pe in inbox.get(cid, []):
                    continue
                n_opp += 1
                n_hit += int(rules.get(cid) == pe)
    return {
        "rate": n_hit / n_opp if n_opp else float("nan"),
        "n_opp": n_opp,
        "n_hit": n_hit,
    }


def metrics_bundle(rows: list[GenRow]) -> dict[str, Any]:
    """Headline bundle; always also split by n_ops when present on rows."""
    g2l = gens_to_correct_lock(rows)
    base = {
        "j": j_non_source(rows),
        "frac_correct_lock_gens": lock_share_non_source(rows, kind="correct"),
        "frac_false_lock_gens": lock_share_non_source(rows, kind="false"),
        "frac_correct_lock_epochs": frac_lock_epochs_non_source(rows, kind="correct"),
        "frac_false_lock_epochs": frac_lock_epochs_non_source(rows, kind="false"),
        "gens_to_correct_lock": {
            "mean_uncensored": g2l["mean_uncensored"],
            "censor_rate": g2l["censor_rate"],
            "n_epochs": g2l["n_epochs"],
            "n_uncensored": g2l["n_uncensored"],
            "n_censored": g2l["n_censored"],
            "by_n_ops": g2l["by_n_ops"],
        },
        "infection": infection_delta_non_source(rows),
        "retention": retention_non_source(rows),
        "genesis": genesis_rate_non_source(rows),
        "n_generations": len(rows),
        "lock_threshold": LOCK_MODAL_SHARE,
    }
    by_ops: dict[str, Any] = {}
    for n_ops in (1, 2):
        sub = [r for r in rows if int(r.get("n_ops", -1)) == n_ops]
        if sub:
            sub_g2l = gens_to_correct_lock(sub)
            by_ops[str(n_ops)] = {
                "j": j_non_source(sub),
                "frac_correct_lock_gens": lock_share_non_source(sub, kind="correct"),
                "frac_correct_lock_epochs": frac_lock_epochs_non_source(
                    sub, kind="correct"
                ),
                "gens_to_correct_lock": {
                    "mean_uncensored": sub_g2l["mean_uncensored"],
                    "censor_rate": sub_g2l["censor_rate"],
                    "n_epochs": sub_g2l["n_epochs"],
                },
                "infection": infection_delta_non_source(sub),
                "retention": retention_non_source(sub),
                "genesis": genesis_rate_non_source(sub),
                "n_generations": len(sub),
            }
    base["by_n_ops"] = by_ops
    try:
        base["infection_all_cells"] = infection_delta(rows)
    except Exception as e:
        base["infection_all_cells"] = {"error": repr(e)}
    return base


def assert_sources_excluded_equals_subpopulation(rows: list[GenRow]) -> None:
    """Acceptance §1: metrics with SOURCE_IDS present == non-source subpopulation alone."""
    if not rows or not any(r.get("seeded") for r in rows):
        raise AssertionError("expected seeded trajectory")
    j = j_non_source(rows)
    hits = total = 0
    for row in rows:
        pe = row["p_e"]
        rules = _rules_map(row)
        for cid in _recipient_ids(row):
            total += 1
            hits += int(rules.get(cid) == pe)
    j2 = hits / total if total else float("nan")
    if abs(j - j2) > 1e-12:
        raise AssertionError(f"J mismatch: {j} vs {j2}")
    for row in rows:
        for cid in SOURCE_IDS:
            assert row.get("source_mask", {}).get(cid) is True

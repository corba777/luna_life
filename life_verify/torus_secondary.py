"""Part 3 secondary torus metrics (PREREG_L_VERIFY_PART3.md +
AMENDMENT_L_VERIFY_PART3_SECONDARY.md).

Pure functions over a rule trajectory:
  [{"generation": int, "epoch": int, "p_e": str, "rules": {cell_id: rule|None}}, ...]

S1 spatial / S2 infection (+ diagnostic T(d)) / S3 cross-epoch stale / S4 null contrasts.
Primary lock metrics stay in constitutional_life.sim.agreement.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from typing import Any

from constitutional_life.board.geometry import N_CELLS, chebyshev, neighbours
from constitutional_life.sim.agreement import moore_cluster_sizes
from constitutional_life.v1a_constants import EPOCH_LENGTH

GenRow = dict[str, Any]  # generation, epoch, p_e, rules

# Headline scalars for S4 seed-level Welch (path into secondary_from_trajectory bundle).
HEADLINE_PATHS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("neighbour_agree_excess", ("spatial", "mean_neighbour_agree_excess")),
    ("n_components", ("spatial", "mean_n_components")),
    ("pe_max_component", ("spatial", "mean_pe_max_component")),
    ("infection_delta", ("spread", "infection", "delta")),
    ("infection_p_inbox", ("spread", "infection", "p_with_inbox")),
    ("infection_p_none", ("spread", "infection", "p_without_inbox")),
    ("T_1", ("spread", "mean_T", "1")),  # diagnostic; selection on defined epochs
    ("T_2", ("spread", "mean_T", "2")),
    ("T_3", ("spread", "mean_T", "3")),
    ("stale_g1_3", ("stale", "mean_stale_g1_3")),
)


def _rules_map(row: GenRow) -> dict[int, str | None]:
    raw = row["rules"]
    # JSON may stringify keys
    return {int(k): v for k, v in raw.items()}


def _inbox_says_map(row: GenRow) -> dict[int, list[str]]:
    """Delivered non-null says that informed this generation's decision."""
    raw = row.get("inbox_says")
    if raw is None:
        raise ValueError(
            "rule_history row missing inbox_says — infection_delta needs delivered "
            "messages (engine ≥ Part3 secondary amendment), not neighbour choices"
        )
    return {int(k): [s for s in (v or []) if s] for k, v in raw.items()}


def _epoch_generation(generation: int) -> int:
    """1..EPOCH_LENGTH within the epoch (Life: (generation % EPOCH_LENGTH) + 1
    only when generation is 0-indexed global; stored generation is 1-based after step).

    Engine stores generation = t+1 after a step that ran at board time t.
    epoch_generation = ((generation - 1) % EPOCH_LENGTH) + 1.
    """
    return ((int(generation) - 1) % EPOCH_LENGTH) + 1


def _nanmean(xs) -> float:
    xs = [x for x in xs if x == x]
    return sum(xs) / len(xs) if xs else float("nan")


def _pull(bundle: dict | None, *path):
    if bundle is None:
        return None
    cur: Any = bundle
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


# ------------------------------------------------------------------ S1 spatial

def analytic_label_shuffle_agree(rules: dict[int, str | None]) -> float:
    """E[frac directed pairs agree] under uniform random reassignment of the
    same multiset of non-None labels among those cells. Neighbours never include
    self, so every scored pair is two distinct cells.
    """
    labels = [r for r in rules.values() if r is not None]
    n = len(labels)
    if n < 2:
        return float("nan")
    counts = Counter(labels)
    num = sum(c * (c - 1) for c in counts.values())
    return num / (n * (n - 1))


def neighbour_agreement(
    rules: dict[int, str | None],
    *,
    radius: int = 1,
    rng: random.Random | None = None,
    n_perm: int = 0,
) -> dict[str, float]:
    """Frac of directed Moore-neighbour pairs with the same non-None rule,
    minus the analytic expectation under label shuffle (same marginal).

    n_perm > 0: also average that many Monte-Carlo shuffles (cross-check).
    Moore neighbours(cid, radius) exclude self — asserted in tests.
    """
    rng = rng or random.Random(0)
    pairs = 0
    agree = 0
    for cid in range(N_CELLS):
        r = rules.get(cid)
        if r is None:
            continue
        for nb in neighbours(cid, radius):
            assert nb != cid, "neighbours() must exclude self"
            rn = rules.get(nb)
            if rn is None:
                continue
            pairs += 1
            if rn == r:
                agree += 1
    raw = agree / pairs if pairs else float("nan")
    null = analytic_label_shuffle_agree(rules)

    out = {
        "neighbour_agree": raw,
        "neighbour_agree_shuffle": null,
        "neighbour_agree_excess": (raw - null) if pairs and null == null else float("nan"),
        "n_neighbour_pairs": float(pairs),
        "null_method": "analytic_label_shuffle",
    }

    if n_perm > 0 and pairs:
        chosen = [cid for cid, r in rules.items() if r is not None]
        labels = [rules[cid] for cid in chosen]
        mc = []
        for _ in range(n_perm):
            perm = labels[:]
            rng.shuffle(perm)
            shuffled = dict(zip(chosen, perm))
            agree_s = pairs_s = 0
            for cid in chosen:
                r = shuffled[cid]
                for nb in neighbours(cid, radius):
                    if nb not in shuffled:
                        continue
                    pairs_s += 1
                    if shuffled[nb] == r:
                        agree_s += 1
            if pairs_s:
                mc.append(agree_s / pairs_s)
        if mc:
            out["neighbour_agree_shuffle_mc"] = sum(mc) / len(mc)
            out["neighbour_agree_excess_mc"] = raw - out["neighbour_agree_shuffle_mc"]
    return out


def rule_components(rules: dict[int, str | None]) -> dict[str, float | int | None]:
    """Moore-connected components per chosen rule (PREREG default: 8-connect)."""
    by_rule: dict[str, list[int]] = defaultdict(list)
    for cid, r in rules.items():
        if r is not None:
            by_rule[r].append(cid)
    n_comp = 0
    sizes_all: list[int] = []
    for ids in by_rule.values():
        sizes = moore_cluster_sizes(ids)
        n_comp += len(sizes)
        sizes_all.extend(sizes)
    counts = Counter(r for r in rules.values() if r is not None)
    modal = counts.most_common(1)[0][0] if counts else None
    modal_sizes = moore_cluster_sizes(by_rule[modal]) if modal else []
    return {
        "n_components": n_comp,
        "n_distinct_rules": len(by_rule),
        "mean_component_size": (sum(sizes_all) / len(sizes_all)) if sizes_all else float("nan"),
        "modal_rule": modal,
        "modal_n_components": len(modal_sizes),
        "modal_max_component": max(modal_sizes) if modal_sizes else 0,
        "modal_mean_component": (sum(modal_sizes) / len(modal_sizes)) if modal_sizes else float("nan"),
    }


def spatial_at_generation(row: GenRow, *, seed: int = 0) -> dict:
    rules = _rules_map(row)
    out = {
        "generation": row["generation"],
        "epoch": row["epoch"],
        "p_e": row["p_e"],
        **neighbour_agreement(rules, rng=random.Random(seed ^ int(row["generation"]))),
        **rule_components(rules),
    }
    # size of the true-rule component family
    pe = row["p_e"]
    pe_ids = [cid for cid, r in rules.items() if r == pe]
    pe_sizes = moore_cluster_sizes(pe_ids)
    out["pe_n_components"] = len(pe_sizes)
    out["pe_max_component"] = max(pe_sizes) if pe_sizes else 0
    out["pe_frac"] = len(pe_ids) / N_CELLS
    return out


# ------------------------------------------------------------------ S2 spread / infection

def infection_delta(rows: list[GenRow]) -> dict[str, float | int]:
    """AMENDMENT_L_VERIFY_PART3_SECONDARY: inbox-conditioned conversion.

    Among cells incorrect at generation t (within an epoch):
      P(correct at t+1 | P_e in delivered inbox at t+1)
      − P(correct at t+1 | P_e not in that inbox).

    Contact = what the cell actually received (publish + substrate visibility),
    not “a Moore neighbour chose P_e”. Requires row["inbox_says"].
    """
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
                continue  # should not happen within epoch
            ra, rb = _rules_map(a), _rules_map(b)
            inbox_b = _inbox_says_map(b)
            for cid in range(N_CELLS):
                if ra.get(cid) == pe:
                    continue  # already correct — not a conversion event
                has_contact = pe in inbox_b.get(cid, [])
                became = rb.get(cid) == pe
                if has_contact:
                    n_with += 1
                    n_with_hit += int(became)
                else:
                    n_without += 1
                    n_without_hit += int(became)

    return _infection_from_counts(
        n_with, n_with_hit, n_without, n_without_hit,
    )


def _infection_from_counts(
    n_with: int, n_with_hit: int, n_without: int, n_without_hit: int,
) -> dict[str, float | int | str]:
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
    }


def infection_delta_pooled(infect_rows: list[dict]) -> dict[str, float | int | str]:
    """Beside S4: sum contact counters across seeds, then one Δ (same NaN rule)."""
    n_with = sum(int(r["n_with_inbox"]) for r in infect_rows)
    n_with_hit = sum(int(r["n_with_inbox_hit"]) for r in infect_rows)
    n_without = sum(int(r["n_without_inbox"]) for r in infect_rows)
    n_without_hit = sum(int(r["n_without_inbox_hit"]) for r in infect_rows)
    out = _infection_from_counts(n_with, n_with_hit, n_without, n_without_hit)
    out["n_seeds_pooled"] = len(infect_rows)
    return out


def _finite(x) -> bool:
    return isinstance(x, (int, float)) and x == x


def spread_hit_times(epoch_rows: list[GenRow], *, distances: tuple[int, ...] = (1, 2, 3)) -> dict:
    """Diagnostic: T(d) = first generation when P_e reaches Chebyshev dist ≥ d
    from the initial correct set S0. Noisy under solo discoveries — see infection_delta.
    """
    if not epoch_rows:
        return {"T": {d: None for d in distances}, "censored": True, "S0_size": 0}
    pe = epoch_rows[0]["p_e"]
    # S0: first generation that has any correct cell; else None
    S0: set[int] | None = None
    t0_gen = None
    for row in epoch_rows:
        rules = _rules_map(row)
        hits = {cid for cid, r in rules.items() if r == pe}
        if hits:
            S0 = hits
            t0_gen = row["generation"]
            break
    if S0 is None:
        return {"T": {d: None for d in distances}, "censored": True, "S0_size": 0,
                "false_decay": _false_decay(epoch_rows)}

    T: dict[int, int | None] = {d: None for d in distances}
    for row in epoch_rows:
        if row["generation"] < t0_gen:
            continue
        rules = _rules_map(row)
        for cid, r in rules.items():
            if r != pe:
                continue
            # min distance to S0
            dist = min(chebyshev(cid, s) for s in S0)
            for d in distances:
                if dist >= d and T[d] is None:
                    # generations since epoch start (epoch_generation), not absolute
                    T[d] = _epoch_generation(row["generation"])
    return {
        "T": T,
        "censored": any(T[d] is None for d in distances),
        "S0_size": len(S0),
        "S0_generation": t0_gen,
        "false_decay": _false_decay(epoch_rows),
    }


def _false_decay(epoch_rows: list[GenRow]) -> dict[str, float]:
    """Frac still on the epoch-start modal *false* rule, by epoch_generation."""
    if not epoch_rows:
        return {}
    pe = epoch_rows[0]["p_e"]
    first = _rules_map(epoch_rows[0])
    counts = Counter(r for r in first.values() if r is not None and r != pe)
    if not counts:
        return {str(g): 0.0 for g in range(1, len(epoch_rows) + 1)}
    false_modal = counts.most_common(1)[0][0]
    out = {}
    for row in epoch_rows:
        g = _epoch_generation(row["generation"])
        rules = _rules_map(row)
        out[str(g)] = sum(1 for r in rules.values() if r == false_modal) / N_CELLS
    out["false_modal"] = false_modal
    return out


# ------------------------------------------------------------------ S3 stale

def stale_share_curve(rows: list[GenRow], *, max_g: int = 5) -> dict:
    """For each epoch e≥1: frac choosing P_{e-1} at epoch_generation g=1..max_g."""
    # map epoch -> ordered rows; and epoch -> p_e (from any row)
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    p_e_of: dict[int, str] = {}
    for row in rows:
        e = int(row["epoch"])
        by_epoch[e].append(row)
        p_e_of[e] = row["p_e"]
    for e in by_epoch:
        by_epoch[e].sort(key=lambda r: r["generation"])

    per_epoch = {}
    for e in sorted(by_epoch):
        if e < 1 or (e - 1) not in p_e_of:
            continue
        prev = p_e_of[e - 1]
        curve = {}
        for row in by_epoch[e]:
            g = _epoch_generation(row["generation"])
            if g > max_g:
                continue
            rules = _rules_map(row)
            curve[str(g)] = sum(1 for r in rules.values() if r == prev) / N_CELLS
        if not curve:
            continue
        g1 = curve.get("1", float("nan"))
        half_life = None
        for g in range(1, max_g + 1):
            if str(g) in curve and curve[str(g)] <= 0.5 * g1:
                half_life = g
                break
        mean_1_3 = sum(curve[str(g)] for g in (1, 2, 3) if str(g) in curve) / max(
            1, sum(1 for g in (1, 2, 3) if str(g) in curve)
        )
        per_epoch[str(e)] = {
            "prev_p_e": prev,
            "curve": curve,
            "mean_g1_3": mean_1_3,
            "half_life_g": half_life,
        }
    # aggregate
    means = [v["mean_g1_3"] for v in per_epoch.values()]
    return {
        "by_epoch": per_epoch,
        "mean_stale_g1_3": (sum(means) / len(means)) if means else float("nan"),
        "n_epochs_scored": len(per_epoch),
    }


# ------------------------------------------------------------------ aggregate + S4

def secondary_from_trajectory(rows: list[GenRow], *, shuffle_seed: int = 0) -> dict:
    """Full secondary bundle for one arm / one seed run."""
    rows = sorted(rows, key=lambda r: r["generation"])
    by_epoch: dict[int, list[GenRow]] = defaultdict(list)
    for row in rows:
        by_epoch[int(row["epoch"])].append(row)

    spatial_rows = [spatial_at_generation(r, seed=shuffle_seed) for r in rows]

    spread_by_epoch = {
        str(e): spread_hit_times(by_epoch[e]) for e in sorted(by_epoch)
    }
    # mean T(d) over epochs where defined (selection caveat — diagnostic only)
    T_means: dict[str, float] = {}
    for d in (1, 2, 3):
        vals = [
            spread_by_epoch[str(e)]["T"][d]
            for e in by_epoch
            if spread_by_epoch[str(e)]["T"][d] is not None
        ]
        T_means[str(d)] = _nanmean(vals) if vals else float("nan")

    infect = infection_delta(rows)

    return {
        "n_generations": len(rows),
        "n_epochs": len(by_epoch),
        "spatial": {
            "mean_neighbour_agree_excess": _nanmean(
                [r["neighbour_agree_excess"] for r in spatial_rows]
            ),
            "mean_n_components": _nanmean([r["n_components"] for r in spatial_rows]),
            "mean_pe_max_component": _nanmean([r["pe_max_component"] for r in spatial_rows]),
            "mean_modal_max_component": _nanmean(
                [r["modal_max_component"] for r in spatial_rows]
            ),
            "by_generation": spatial_rows,
        },
        "spread": {
            "infection": infect,
            "mean_T": T_means,
            "by_epoch": spread_by_epoch,
            "note": "headline=infection; mean_T diagnostic (censored-mean selection)",
        },
        "stale": stale_share_curve(rows),
    }


def contrast_vs_nulls(
    channel: dict,
    silent: dict | None,
    g_perm: dict | None,
) -> dict:
    """Per-run S4 deltas (diagnostic). Prefer contrast_vs_nulls_seed_level for text."""

    def _delta(path: tuple) -> dict:
        c = _pull(channel, *path)
        s = _pull(silent, *path)
        p = _pull(g_perm, *path)
        return {
            "channel": c,
            "silent": s,
            "g_perm": p,
            "vs_silent": (c - s) if isinstance(c, (int, float)) and isinstance(s, (int, float))
            and c == c and s == s else None,
            "vs_g_perm": (c - p) if isinstance(c, (int, float)) and isinstance(p, (int, float))
            and c == c and p == p else None,
        }

    return {name: _delta(path) for name, path in HEADLINE_PATHS}


def _welch_defined(a: list, b: list, *, n_seeds: int) -> dict:
    """Welch on indices where both sides are finite; report n_defined."""
    import stats as St

    aa, bb, kept = [], [], []
    for i, (x, y) in enumerate(zip(a, b)):
        if _finite(x) and _finite(y):
            aa.append(float(x))
            bb.append(float(y))
            kept.append(i)
    base = {
        "n_seeds": n_seeds,
        "n_defined": len(kept),
        "seeds_defined": kept,
        "a": aa,
        "b": bb,
    }
    if len(aa) < 2:
        base["note"] = "insufficient_defined_seeds"
        return base
    ci = St.welch_ci(aa, bb)
    base.update({
        "diff": ci["diff"], "lo": ci["lo"], "hi": ci["hi"],
        "df": ci["df"], "se": ci["se"],
        "three_way": ci["three_way"],
        "mean_a": ci["mean_a"], "mean_b": ci["mean_b"],
    })
    return base


def contrast_vs_nulls_seed_level(
    channel_bundles: list[dict],
    silent_bundles: list[dict] | None,
    g_perm_bundles: list[dict] | None,
) -> dict:
    """Reportable S4: unpaired Welch over seeds where both arms are finite.

    Infection (and any other NaN-capable scalar): do not drop the whole metric
    when some seeds lack contact — Welch on the defined subset and report
    n_defined. Beside: pooled infection counters across all seeds.
    """
    import stats as St

    n = len(channel_bundles)
    if n < 1:
        raise ValueError("need ≥1 channel seed bundle")
    if silent_bundles is not None and len(silent_bundles) != n:
        raise ValueError(f"silent seeds {len(silent_bundles)} != channel {n}")
    if g_perm_bundles is not None and len(g_perm_bundles) != n:
        raise ValueError(f"g_perm seeds {len(g_perm_bundles)} != channel {n}")

    out: dict[str, Any] = {
        "n_seeds": n,
        "method": "welch_unpaired_defined_seeds",
        "metrics": {},
    }
    for name, path in HEADLINE_PATHS:
        ch = [_pull(b, *path) for b in channel_bundles]
        ch_f = [float(x) for x in ch if _finite(x)]
        block: dict[str, Any] = {
            "channel": ch,
            "n_channel_defined": len(ch_f),
            "channel_mean_defined": (sum(ch_f) / len(ch_f)) if ch_f else float("nan"),
        }
        if len(ch_f) >= 2:
            # one-sample vs 0 on defined channel seeds (infection null when silent N/A)
            ones = St.one_sample_ci(ch_f, 0.0)
            block["channel_vs_0"] = {
                "diff": ones["diff"], "lo": ones["lo"], "hi": ones["hi"],
                "df": ones["df"], "three_way": ones["three_way"],
                "n_defined": len(ch_f),
            }
        if silent_bundles is not None:
            sil = [_pull(b, *path) for b in silent_bundles]
            block["silent"] = sil
            vs = _welch_defined(ch, sil, n_seeds=n)
            if vs.get("note") == "insufficient_defined_seeds":
                block["vs_silent"] = {
                    **vs,
                    "note": vs["note"] + (
                        " (infection vs silent is usually N/A: silent has no contact)"
                        if name.startswith("infection") else ""
                    ),
                }
            else:
                block["vs_silent"] = {
                    "diff": vs["diff"], "lo": vs["lo"], "hi": vs["hi"],
                    "df": vs["df"], "se": vs["se"],
                    "three_way": vs["three_way"],
                    "silent_mean": vs["mean_b"],
                    "n_defined": vs["n_defined"], "n_seeds": n,
                    "seeds_defined": vs["seeds_defined"],
                }
        if g_perm_bundles is not None:
            gp = [_pull(b, *path) for b in g_perm_bundles]
            block["g_perm"] = gp
            vs = _welch_defined(ch, gp, n_seeds=n)
            if vs.get("note") == "insufficient_defined_seeds":
                block["vs_g_perm"] = vs
            else:
                block["vs_g_perm"] = {
                    "diff": vs["diff"], "lo": vs["lo"], "hi": vs["hi"],
                    "df": vs["df"], "se": vs["se"],
                    "three_way": vs["three_way"],
                    "g_perm_mean": vs["mean_b"],
                    "n_defined": vs["n_defined"], "n_seeds": n,
                    "seeds_defined": vs["seeds_defined"],
                }
        out["metrics"][name] = block

    # Beside: pooled infection counters (all seeds, even if per-seed Δ is NaN)
    ch_inf = [_pull(b, "spread", "infection") for b in channel_bundles]
    if all(isinstance(r, dict) and "n_with_inbox" in r for r in ch_inf):
        pooled: dict[str, Any] = {
            "channel": infection_delta_pooled(ch_inf),  # type: ignore[arg-type]
        }
        if silent_bundles is not None:
            sil_inf = [_pull(b, "spread", "infection") for b in silent_bundles]
            pooled["silent"] = infection_delta_pooled(sil_inf)  # type: ignore[arg-type]
        if g_perm_bundles is not None:
            gp_inf = [_pull(b, "spread", "infection") for b in g_perm_bundles]
            pooled["g_perm"] = infection_delta_pooled(gp_inf)  # type: ignore[arg-type]
        out["infection_pooled"] = pooled
    return out


def load_rule_history(path) -> list[GenRow]:
    import json
    from pathlib import Path
    return json.loads(Path(path).read_text())

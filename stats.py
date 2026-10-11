"""Shared seed-level inference helpers (METRICS.md §6).

All Stage-1 contrast intervals import from here — no local copies of tcrit.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
from scipy import stats


def _as1d(x: Sequence[float]) -> np.ndarray:
    a = np.asarray(x, dtype=float).ravel()
    if a.size == 0:
        raise ValueError("empty sample")
    return a


def welch_df(s1: float, n1: int, s2: float, n2: int) -> float:
    """Welch–Satterthwaite degrees of freedom."""
    v1 = (s1 * s1) / n1
    v2 = (s2 * s2) / n2
    num = (v1 + v2) ** 2
    den = 0.0
    if n1 > 1:
        den += (v1 ** 2) / (n1 - 1)
    if n2 > 1:
        den += (v2 ** 2) / (n2 - 1)
    if den <= 0:
        return float("nan")
    return float(num / den)


def three_way(lo: float, hi: float) -> str:
    """Interval entirely >0 / entirely <0 / contains 0."""
    if lo > 0 and hi > 0:
        return ">"
    if lo < 0 and hi < 0:
        return "<"
    return "indistinguishable"


def welch_ci(
    a: Sequence[float],
    b: Sequence[float],
    *,
    alpha: float = 0.05,
) -> dict:
    """Unpaired Welch CI for mean(a) − mean(b). Never pairs by index."""
    aa, bb = _as1d(a), _as1d(b)
    n1, n2 = int(aa.size), int(bb.size)
    m1, m2 = float(aa.mean()), float(bb.mean())
    # sample sd with ddof=1; for n=1, sd=0 and df collapses
    s1 = float(aa.std(ddof=1)) if n1 > 1 else 0.0
    s2 = float(bb.std(ddof=1)) if n2 > 1 else 0.0
    se = float(np.sqrt((s1 * s1) / n1 + (s2 * s2) / n2))
    d = m1 - m2
    df = welch_df(s1, n1, s2, n2)
    if not np.isfinite(df) or df <= 0 or se == 0.0:
        # degenerate: report point with nan interval ends if se=0 and d!=0 still ok
        if se == 0.0:
            lo = hi = d
            tcrit = float("nan")
        else:
            lo = hi = float("nan")
            tcrit = float("nan")
    else:
        tcrit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
        lo, hi = d - tcrit * se, d + tcrit * se
    return {
        "diff": d,
        "mean_a": m1,
        "mean_b": m2,
        "sd_a": s1,
        "sd_b": s2,
        "n_a": n1,
        "n_b": n2,
        "se": se,
        "df": df,
        "tcrit": tcrit,
        "lo": float(lo),
        "hi": float(hi),
        "alpha": alpha,
        "three_way": three_way(float(lo), float(hi)),
        "method": "welch_unpaired",
    }


def one_sample_ci(
    xs: Sequence[float],
    mu0: float,
    *,
    alpha: float = 0.05,
) -> dict:
    """One-sample t CI for mean(xs) − mu0 (e.g. vs frozen M_0)."""
    a = _as1d(xs)
    n = int(a.size)
    m = float(a.mean())
    d = m - float(mu0)
    if n < 2:
        return {
            "diff": d,
            "mean": m,
            "mu0": float(mu0),
            "sd": 0.0,
            "n": n,
            "se": 0.0,
            "df": 0.0,
            "tcrit": float("nan"),
            "lo": d,
            "hi": d,
            "alpha": alpha,
            "three_way": three_way(d, d),
            "method": "one_sample",
        }
    sd = float(a.std(ddof=1))
    se = sd / np.sqrt(n)
    df = float(n - 1)
    tcrit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
    lo, hi = d - tcrit * se, d + tcrit * se
    return {
        "diff": d,
        "mean": m,
        "mu0": float(mu0),
        "sd": sd,
        "n": n,
        "se": float(se),
        "df": df,
        "tcrit": tcrit,
        "lo": float(lo),
        "hi": float(hi),
        "alpha": alpha,
        "three_way": three_way(float(lo), float(hi)),
        "method": "one_sample",
    }


def ddr_ci(
    multi_e1p: Sequence[float],
    single_e1p: Sequence[float],
    multi_e1: Sequence[float],
    single_e1: Sequence[float],
    *,
    alpha: float = 0.05,
) -> dict:
    """ΔΔR = (mean multi−single on E1-P) − (mean multi−single on E1).

    SE² = Σ_g s_g²/n_g over the four independent groups (METRICS.md §6).
    Never forms per-seed ΔR vectors.
    """
    groups = {
        "multi_e1p": _as1d(multi_e1p),
        "single_e1p": _as1d(single_e1p),
        "multi_e1": _as1d(multi_e1),
        "single_e1": _as1d(single_e1),
    }
    means = {k: float(v.mean()) for k, v in groups.items()}
    ns = {k: int(v.size) for k, v in groups.items()}
    sds = {
        k: float(v.std(ddof=1)) if v.size > 1 else 0.0
        for k, v in groups.items()
    }
    # ΔΔR = (m_me1p - m_se1p) - (m_me1 - m_se1)
    d = (means["multi_e1p"] - means["single_e1p"]) - (
        means["multi_e1"] - means["single_e1"]
    )
    # coefficients on the four means: +1, -1, -1, +1
    coef = {
        "multi_e1p": 1.0,
        "single_e1p": -1.0,
        "multi_e1": -1.0,
        "single_e1": 1.0,
    }
    var_terms = []
    for k in groups:
        n, s = ns[k], sds[k]
        var_terms.append((coef[k] ** 2) * (s * s) / n)
    se2 = float(sum(var_terms))
    se = float(np.sqrt(se2))
    # Welch–Satterthwaite for linear combo of independent means
    num = se2 ** 2
    den = 0.0
    for k in groups:
        n, s = ns[k], sds[k]
        v = (coef[k] ** 2) * (s * s) / n
        if n > 1 and v > 0:
            den += (v ** 2) / (n - 1)
    df = float(num / den) if den > 0 else float("nan")
    if np.isfinite(df) and df > 0 and se > 0:
        tcrit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
        lo, hi = d - tcrit * se, d + tcrit * se
    else:
        tcrit = float("nan")
        lo = hi = d if se == 0 else float("nan")
    return {
        "diff": d,
        "delta_e1p": means["multi_e1p"] - means["single_e1p"],
        "delta_e1": means["multi_e1"] - means["single_e1"],
        "means": means,
        "sds": sds,
        "ns": ns,
        "se": se,
        "df": df,
        "tcrit": tcrit,
        "lo": float(lo),
        "hi": float(hi),
        "alpha": alpha,
        "three_way": three_way(float(lo), float(hi)),
        "method": "ddr_four_groups",
    }


def paired_ci_by_index(
    a: Sequence[float],
    b: Sequence[float],
    *,
    alpha: float = 0.05,
) -> dict:
    """Paired-by-index CI on a_s − b_s. FORBIDDEN for cross-condition contrasts
    (METRICS §6). Kept only to diagnose old artefacts that used this method."""
    aa, bb = _as1d(a), _as1d(b)
    if aa.size != bb.size:
        raise ValueError("paired_ci_by_index requires equal lengths")
    d = aa - bb
    n = int(d.size)
    m = float(d.mean())
    if n < 2:
        return {
            "diff": m,
            "n": n,
            "se": 0.0,
            "df": 0.0,
            "tcrit": float("nan"),
            "lo": m,
            "hi": m,
            "alpha": alpha,
            "three_way": three_way(m, m),
            "method": "paired_by_index_FORBIDDEN",
        }
    sd = float(d.std(ddof=1))
    se = sd / np.sqrt(n)
    df = float(n - 1)
    tcrit = float(stats.t.ppf(1.0 - alpha / 2.0, df))
    lo, hi = m - tcrit * se, m + tcrit * se
    return {
        "diff": m,
        "sd_diff": sd,
        "n": n,
        "se": float(se),
        "df": df,
        "tcrit": tcrit,
        "lo": float(lo),
        "hi": float(hi),
        "alpha": alpha,
        "three_way": three_way(float(lo), float(hi)),
        "method": "paired_by_index_FORBIDDEN",
    }

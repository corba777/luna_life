#!/usr/bin/env python3
"""Central Life figure: J(g) for B/Bs/Ca/Cas/Da + ideal bound.

Two panels by n_ops. Mean over seeds with bootstrap band.
Sample arms C/D omitted (decode noise) — paper figure is the five-arm set.
Writes runs/life_reasoning_cells/fig_j_by_gen.{json,png}.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs/life_reasoning_cells"
BOUND = ROOT / "runs/life_verify/reachability_bound.json"
SEEDS = [1, 2, 3, 4, 5, 6, 7, 18, 22, 29]
# Paper set: reasoning / silent / one-pass / silent one-pass / checked one-pass.
# Cas dashed next to Ca; sample C/D left out of this figure.
PRIMARY = ("B", "Bs", "Ca", "Cas", "Da")
ARMS = PRIMARY
# Legend uses table roles, not internal arm codes (review: readers misread D/C for Da/Ca).
LEGEND = {
    "B": "reasoning",
    "Bs": "reasoning, silent",
    "Ca": "one-pass",
    "Cas": "one-pass, silent",
    "Da": "one-pass + check",
}
BOUND_LABEL = "topological reachability bound"
N_BOOT = 10_000
RNG = np.random.default_rng(20261010)


def j_curve(arm: str, seed: int) -> list[float] | None:
    p = OUT / f"arm_{arm}" / f"seed{seed}" / "rule_history.json"
    if not p.is_file():
        return None
    rh = json.loads(p.read_text())
    out = []
    for row in rh:
        pe = row["p_e"]
        rules = {str(k): v for k, v in row["rules"].items()}
        src = {str(k): bool(v) for k, v in row["source_mask"].items()}
        ids = [cid for cid, is_src in src.items() if not is_src]
        hits = sum(1 for cid in ids if rules.get(cid) == pe)
        out.append(hits / len(ids) if ids else float("nan"))
    return out


def boot_band(curves: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """curves: (n_seed, n_gen) → mean, lo, hi per gen (seed bootstrap)."""
    n, g = curves.shape
    mean = curves.mean(axis=0)
    if n == 1:
        return mean, mean, mean
    idx = RNG.integers(0, n, size=(N_BOOT, n))
    boots = curves[idx].mean(axis=1)  # (n_boot, g)
    lo = np.quantile(boots, 0.025, axis=0)
    hi = np.quantile(boots, 0.975, axis=0)
    return mean, lo, hi


def main() -> None:
    n_ops: dict[int, int] = {}
    for s in SEEDS:
        for arm in ARMS:
            rp = OUT / f"arm_{arm}" / f"seed{s}" / "report.json"
            if rp.is_file():
                n_ops[s] = json.loads(rp.read_text())["n_ops"]
                break

    bound = None
    if BOUND.is_file():
        b = json.loads(BOUND.read_text())
        rows = b.get("ideal_mean_by_generation")
        if isinstance(rows, list) and rows:
            by_g = {int(r["generation"]): float(r["mean_reachable_frac"]) for r in rows}
            bound = [by_g.get(g) for g in range(1, 11)]

    series = {}
    for arm in ARMS:
        for ops in (1, 2):
            curves = []
            for s in SEEDS:
                if n_ops.get(s) != ops:
                    continue
                c = j_curve(arm, s)
                if c is not None and len(c) >= 1:
                    curves.append(c[:10] if len(c) >= 10 else c + [float("nan")] * (10 - len(c)))
            if not curves:
                continue
            arr = np.asarray(curves, dtype=float)
            # pad/truncate to common length
            g = min(len(c) for c in curves)
            arr = arr[:, :g]
            mean, lo, hi = boot_band(arr)
            series[f"{arm}_ops{ops}"] = {
                "mean": mean.tolist(),
                "lo": lo.tolist(),
                "hi": hi.tolist(),
                "n": int(arr.shape[0]),
            }

    colors = {
        "B": "#1f77b4", "Bs": "#aec7e8", "Ca": "#ff7f0e", "Cas": "#ff7f0e",
        "Da": "#2ca02c", "C": "#ffbb78", "D": "#98df8a",
    }
    styles = {
        "B": "-", "Bs": "-", "Ca": "-", "Da": "-", "Cas": "--",
        "C": "--", "D": "--",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.4), sharey=True)
    handles, labels = [], []
    for ax, ops in zip(axes, (1, 2)):
        for arm in PRIMARY:
            key = f"{arm}_ops{ops}"
            if key not in series:
                continue
            y = series[key]["mean"]
            x = list(range(1, len(y) + 1))
            lab = f"{LEGEND[arm]} (n={series[key]['n']})"
            (ln,) = ax.plot(
                x, y, label=lab, color=colors[arm], lw=2,
                ls=styles.get(arm, "-"),
            )
            ax.fill_between(
                x, series[key]["lo"], series[key]["hi"],
                color=colors[arm], alpha=0.18,
            )
            if ops == 2:
                handles.append(ln)
                labels.append(lab)
        if bound:
            (ln,) = ax.plot(
                range(1, len(bound) + 1), bound, "k--",
                label=BOUND_LABEL, linewidth=1.2,
            )
            if ops == 2:
                handles.append(ln)
                labels.append(BOUND_LABEL)
        ax.set_title(f"{ops}-op")
        ax.set_xlabel("generation")
        ax.set_ylim(0, 1.05)
        ax.set_xticks(range(1, 11))
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("J (non-source)")
    fig.suptitle("Life reasoning cells — J by generation")
    fig.tight_layout(rect=(0, 0, 0.76, 1))
    fig.legend(handles, labels, loc="center left", bbox_to_anchor=(0.78, 0.5), fontsize=8)
    png = OUT / "fig_j_by_gen.png"
    js = OUT / "fig_j_by_gen.json"
    fig.savefig(png, dpi=150, bbox_inches="tight")
    js.write_text(json.dumps({
        "series": series,
        "bound": bound,
        "seeds": SEEDS,
        "n_boot": N_BOOT,
        "arms": list(PRIMARY),
        "legend": LEGEND,
        "bound_label": BOUND_LABEL,
        "note": (
            "Legend = table roles (not arm codes). "
            "B/Bs/Ca/Da solid; Cas dashed (next to Ca). "
            "C/D sample omitted (decode noise). Band = seed bootstrap 95%. "
            "Black dashed = topological reachability bound "
            "(ideal adopt-on-first-contact), not a model accuracy ceiling."
        ),
    }, indent=2) + "\n")
    print(json.dumps({
        "wrote_png": str(png),
        "wrote_json": str(js),
        "keys": sorted(series),
        "legend": LEGEND,
        "bound_label": BOUND_LABEL,
    }, indent=2))


if __name__ == "__main__":
    main()

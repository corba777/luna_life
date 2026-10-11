#!/usr/bin/env python3
"""Luna OpenAI Decisions — Life Part-2 probe (API only; no GPU).

Fills the gap left by the main battery: `delta_named` / `delta_argmax_named` and
mixed 1T7F / 1F7T arms (TASK_OPENAI_DECISIONS_BATTERY pred 4 / step 3).
Predictions were locked before any Luna Life number; engine_check + lv_pairs
already ran.

  PYTHONPATH=.:. \\
    python scripts/eval_openai_luna_part2_probe.py \\
      --out runs/openai_decisions/luna_part2_probe.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from constitutional_life.cell.prompt import render_state  # noqa: E402
from constitutional_life.model.jev import RULE_INSTRUCTIONS, rule_key  # noqa: E402
from constitutional_life.probe import ARMS, make_items, observation, summarise  # noqa: E402
from constitutional_life.task.catalog import build_catalog  # noqa: E402

import typesafe_policy as TP  # noqa: E402
from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402

_CAT = build_catalog()
_DESC = [fn.description() for fn in _CAT.functions]
_PID = [fn.program_id for fn in _CAT.functions]
_PID_TO_IDX = {p: i for i, p in enumerate(_PID)}

# Credulity / named-contrast arms (TASK step 3). Skip solo/empty/pub_* here.
DEFAULT_ARMS = ("true", "false", "mixed_1true_7false", "mixed_1false_7true")


def _score_obs(pol: TP.TypeSafePolicy, obs, *, channel: bool, seed: int) -> np.ndarray:
    """π over 101 catalog descriptions; P-average, canonical order."""
    state = render_state(obs, channel=channel)
    # Client remaps keys → opaque opt_i; description = catalog text (battery rule).
    values = list(_DESC)
    acc = None
    for k in range(pol.P):
        p = TP._from_values(
            pol.client, state, RULE_INSTRUCTIONS, values,
            perm_idx=k, stream=77, seed=seed, draw=0,
        )
        pol.n_forwards += 1
        acc = p if acc is None else acc + p
    return acc / pol.P


def _row(item, arm: str, p: np.ndarray) -> dict:
    f_idx = _PID_TO_IDX[item.fn.program_id]
    top = int(np.argmax(p))
    top_set = set(np.flatnonzero(np.isclose(p, p.max())).tolist())
    unique_top = top if len(top_set) == 1 else None
    expected = item.fn.apply(item.query)
    row = {
        "program_id": item.fn.program_id,
        "p_e": item.fn.description(),
        "n_ops": item.fn.n_ops,
        "draw": item.draw,
        "p_rule": float(p[f_idx]),
        "argmax_correct": bool(unique_top == f_idx),
    }
    if arm == "true":
        row["p_named"] = float(p[f_idx])
        row["argmax_named"] = bool(unique_top == f_idx)
    elif arm == "false":
        g_idx = _PID_TO_IDX[item.false_rule.program_id]
        row["false_rule"] = item.false_rule.description()
        row["p_named"] = float(p[g_idx])
        row["argmax_named"] = bool(unique_top == g_idx)
        row["p_follow_false"] = row["p_named"]
    elif arm in ("mixed_1true_7false", "mixed_1false_7true"):
        g_idx = _PID_TO_IDX[item.false_rule.program_id]
        row["false_rule"] = item.false_rule.description()
        row["p_named_true"] = float(p[f_idx])
        row["p_named_false"] = float(p[g_idx])
        row["argmax_true"] = bool(unique_top == f_idx)
        row["argmax_false"] = bool(unique_top == g_idx)
        maj_idx = f_idx if arm == "mixed_1false_7true" else g_idx
        sing_idx = g_idx if arm == "mixed_1false_7true" else f_idx
        row["p_majority"] = float(p[maj_idx])
        row["p_singleton"] = float(p[sing_idx])
        row["argmax_majority"] = bool(unique_top == maj_idx)
        row["argmax_singleton"] = bool(unique_top == sing_idx)
    return row


def _named_contrast(true_rows, false_rows) -> dict:
    p_t = float(np.mean([r["p_named"] for r in true_rows]))
    p_f = float(np.mean([r["p_named"] for r in false_rows]))
    a_t = float(np.mean([r["argmax_named"] for r in true_rows]))
    a_f = float(np.mean([r["argmax_named"] for r in false_rows]))
    return {
        "p_named_true": p_t,
        "p_named_false": p_f,
        "delta_named": p_t - p_f,
        "argmax_named_true": a_t,
        "argmax_named_false": a_f,
        "delta_argmax_named": a_t - a_f,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--per-function", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0, help="0 = all 101 functions")
    ap.add_argument("--P", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--arms", nargs="+", default=list(DEFAULT_ARMS))
    ap.add_argument("--out", default="artifacts/openai_decisions/luna_part2_probe.json")
    a = ap.parse_args()

    client = OpenAIDecisionsClient(timeout=a.timeout)
    if not client.api_key:
        raise SystemExit("OPENAI_API_KEY missing")
    print(client.check(), flush=True)
    pol = TP.TypeSafePolicy(client, P=a.P)

    limit = a.limit or None
    items, pe_rejects = make_items(a.seed, a.per_function, limit)
    report = {
        "label": "gpt-6-luna",
        "task": "TASK_OPENAI_DECISIONS_BATTERY.md § Life Part-2",
        "stamp": client.stamp(),
        "seed": a.seed,
        "n_items": len(items),
        "pe_reject_batches": pe_rejects,
        "P": a.P,
        "arms": {},
        "note": (
            "API-only completion of Luna battery step 3. Predictions locked before "
            "numbers. Primary readout = named_contrast + mixed_1T7F argmax_true "
            "(AMENDMENT_L_VERIFY_PART2_M0). Opaque values=rule_key; descriptions="
            "catalog text."
        ),
    }
    true_rows = false_rows = None
    for arm in a.arms:
        if arm not in ARMS:
            raise SystemExit(f"unknown arm {arm!r}; choose from {ARMS}")
        t1 = time.time()
        rows = []
        channel = arm != "solo"
        for item in items:
            obs = observation(item, arm)
            p = _score_obs(pol, obs, channel=channel, seed=a.seed + item.draw)
            rows.append(_row(item, arm, p))
        summary = summarise(rows)
        summary["elapsed_s"] = time.time() - t1
        summary["usage"] = client.usage()
        report["arms"][arm] = summary
        if arm == "true":
            true_rows = rows
        if arm == "false":
            false_rows = rows
        print(
            f"{arm:22}  P(rule) {summary.get('p_rule', float('nan')):.3f}  "
            f"top-1 {summary.get('argmax_correct', float('nan')):.3f}  "
            f"{summary['elapsed_s']:.0f}s  "
            f"usage={client.usage()}",
            flush=True,
        )

    if true_rows is not None and false_rows is not None:
        report["named_contrast"] = _named_contrast(true_rows, false_rows)
        c = report["named_contrast"]
        print(
            f"Δ_named mass={c['delta_named']:.4f}  "
            f"argmax={c['delta_argmax_named']:.4f}  "
            f"(true {c['argmax_named_true']:.3f} − false {c['argmax_named_false']:.3f})",
            flush=True,
        )
    mixed = report["arms"].get("mixed_1true_7false")
    if mixed is not None:
        print(
            f"mixed_1T7F  argmax_true={mixed.get('argmax_true', float('nan')):.3f}  "
            f"argmax_maj={mixed.get('argmax_majority', float('nan')):.3f}",
            flush=True,
        )
    report["usage_total"] = client.usage()

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, default=float) + "\n")
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

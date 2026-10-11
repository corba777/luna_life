#!/usr/bin/env python3
"""Luna depth curve 3-op eval — TASK_LUNA_DEPTH.md.

Modes: decisions (P=4), resp_none / resp_medium (K=8). Reuses parent 1-op/2-op
from luna_modes.json + luna_modes_cis_fixed.json. No reasoning text stored.

  PYTHONPATH=.:. \\
    python scripts/eval_luna_depth.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

import typesafe_policy as TP  # noqa: E402
from life_verify import luna_depth as D  # noqa: E402
from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402
from openai_responses_luna import LunaResponsesClient  # noqa: E402

OUT = ROOT / "artifacts/openai_decisions/luna_depth.json"
MODES_PARENT = ROOT / "artifacts/openai_decisions/luna_modes.json"
CIS_FIXED = ROOT / "artifacts/openai_decisions/luna_modes_cis_fixed.json"
CHECK = ROOT / "artifacts/openai_decisions/luna_depth_generator_check.json"
K = 8
P = 4
MAX_OUT = 8192
BOOT_N = 5000
BOOT_SEED = 0
EFFORTS = ("none", "medium")


def _perm_order(values: list[str], *, seed: int, perm_idx: int) -> list[str]:
    rng = TP._perm_rng([seed, perm_idx, 77, 7919])
    order = list(values)
    if len(order) >= 2:
        for _ in range(32):
            perm = rng.permutation(len(order))
            new = [order[i] for i in perm]
            if new != order:
                return new
        return list(reversed(order))
    return order


def _pair_pref(counts: dict[str, int], true_desc: str, false_desc: str) -> float:
    ct = counts.get(true_desc, 0)
    cf = counts.get(false_desc, 0)
    if ct > cf:
        return 1.0
    if cf > ct:
        return 0.0
    return 0.5


def _pair_pref_pi(pi: dict[str, float], true_desc: str, false_desc: str) -> float:
    ct = float(pi.get(true_desc, 0.0))
    cf = float(pi.get(false_desc, 0.0))
    if ct > cf:
        return 1.0
    if cf > ct:
        return 0.0
    return 0.5


def _cluster_boot_by_fn(
    deltas: list[tuple[str, float]], *, n_boot=BOOT_N, seed=BOOT_SEED
) -> dict:
    by: dict[str, list[float]] = defaultdict(list)
    for fn, d in deltas:
        by[fn].append(d)
    keys = list(by.keys())
    if not keys:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n_fn": 0}
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.choice(keys, size=len(keys), replace=True)
        vals = [x for k in pick for x in by[k]]
        boots.append(float(np.mean(vals)))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    flat = [d for _, d in deltas]
    return {
        "mean": float(np.mean(flat)),
        "lo": float(lo),
        "hi": float(hi),
        "n_fn": len(keys),
        "n_pairs": len(flat),
        "ci_excludes_0": bool(lo > 0 or hi < 0),
    }


def _sample_keys(client, state, question, values, *, effort, seed) -> dict:
    counts: Counter = Counter()
    n_valid = n_trunc = n_invalid = 0
    reason_tok = []
    statuses = Counter()
    for k in range(K):
        order = _perm_order(values, seed=seed, perm_idx=k % P)
        row = client.choose_key(
            state, question, order, effort=effort, draw=k, retry=True
        )
        statuses[row.get("status")] += 1
        reason_tok.append(row["reasoning_tokens"])
        if row["truncated"]:
            n_trunc += 1
            n_invalid += 1
            continue
        if row["invalid"] or row["key"] is None:
            n_invalid += 1
            continue
        n_valid += 1
        idx = int(row["key"].split("_")[1])
        counts[order[idx]] += 1
    return {
        "counts": dict(counts),
        "n_valid": n_valid,
        "n_truncated": n_trunc,
        "n_invalid": n_invalid,
        "status_counts": dict(statuses),
        "mean_reasoning": float(np.mean(reason_tok)) if reason_tok else 0.0,
        "max_reasoning": int(max(reason_tok)) if reason_tok else 0,
    }


def eval_decisions(pairs: list[D.DepthPair]) -> dict:
    cli = OpenAIDecisionsClient(timeout=120.0)
    pol = TP.TypeSafePolicy(cli, P=P)
    rows = []
    t0 = time.time()
    for i, pair in enumerate(pairs):
        q = D.render_receiver_depth(pair)
        values = list(q["options"])
        # Average P orderings → π over canonical option order
        acc = None
        for k in range(P):
            p = TP._from_values(
                cli, q["state"], q["question"], values,
                perm_idx=k, stream=77, seed=pair.seed, draw=0,
            )
            acc = p if acc is None else acc + p
        p = acc / P
        pi = {values[j]: float(p[j]) for j in range(len(values))}
        pref = _pair_pref_pi(pi, pair.true_desc, pair.false_desc)
        rows.append({
            "id": pair.id,
            "function_id": pair.true_program_id,
            "true_desc": pair.true_desc,
            "false_desc": pair.false_desc,
            "n_ops": 3,
            "pair_pref_choice": pref,
            "pi_true": float(pi[pair.true_desc]),
            "pi_false": float(pi[pair.false_desc]),
        })
        if (i + 1) % 10 == 0 or i == 0:
            print(json.dumps({
                "mode": "decisions",
                "progress": f"{i+1}/{len(pairs)}",
                "mean_pref": float(np.mean([r["pair_pref_choice"] for r in rows])),
                "usage": cli.usage(),
            }), flush=True)
    prefs = [r["pair_pref_choice"] for r in rows]
    return {
        "n": len(rows),
        "pair_pref_choice": float(np.mean(prefs)),
        "elapsed_s": time.time() - t0,
        "usage": cli.usage(),
        "n_forwards": pol.n_forwards,
        "rows": rows,
    }


def eval_responses(client: LunaResponsesClient, pairs: list[D.DepthPair], effort: str) -> dict:
    rows = []
    t0 = time.time()
    for i, pair in enumerate(pairs):
        q = D.render_receiver_depth(pair)
        values = list(q["options"])
        samp = _sample_keys(
            client, q["state"], q["question"], values,
            effort=effort, seed=pair.seed,
        )
        pref = _pair_pref(samp["counts"], pair.true_desc, pair.false_desc)
        if samp["n_valid"] == 0:
            pref = 0.5
        rows.append({
            "id": pair.id,
            "function_id": pair.true_program_id,
            "true_desc": pair.true_desc,
            "false_desc": pair.false_desc,
            "n_ops": 3,
            "pair_pref_choice": pref,
            **{k: samp[k] for k in (
                "n_valid", "n_truncated", "n_invalid",
                "mean_reasoning", "max_reasoning", "status_counts",
            )},
        })
        if (i + 1) % 10 == 0 or i == 0:
            print(json.dumps({
                "mode": f"resp_{effort}",
                "progress": f"{i+1}/{len(pairs)}",
                "mean_pref": float(np.mean([r["pair_pref_choice"] for r in rows])),
                "invalid_rate": float(np.mean([r["n_invalid"] / K for r in rows])),
                "mean_reasoning": float(np.mean([r["mean_reasoning"] for r in rows])),
            }), flush=True)
    prefs = [r["pair_pref_choice"] for r in rows]
    return {
        "n": len(rows),
        "pair_pref_choice": float(np.mean(prefs)),
        "invalid_rate": float(np.mean([r["n_invalid"] / K for r in rows])),
        "truncated_rate": float(np.mean([r["n_truncated"] / K for r in rows])),
        "mean_reasoning": float(np.mean([r["mean_reasoning"] for r in rows])),
        "max_reasoning": int(max((r["max_reasoning"] for r in rows), default=0)),
        "elapsed_s": time.time() - t0,
        "rows": rows,
    }


def _parent_depth_points() -> dict:
    """1-op / 2-op points from parent artifacts."""
    modes = json.loads(MODES_PARENT.read_text())
    out = {
        "decisions": {},
        "resp_none": {},
        "resp_medium": {},
        "resp_high": {},
    }
    if CIS_FIXED.is_file():
        cis = json.loads(CIS_FIXED.read_text())
        r3 = ((cis.get("verdicts") or {}).get("R3_1op") or {})
        if r3.get("decisions_1op") is not None:
            out["decisions"]["1"] = r3["decisions_1op"]
        p2 = (cis.get("pairs_2op") or {}).get("medium_minus_decisions_2op") or {}
        if p2.get("dec_mean_2op") is not None:
            out["decisions"]["2"] = p2["dec_mean_2op"]
    for effort in ("none", "medium", "high"):
        block = (modes.get("responses") or {}).get(effort, {}).get("pairs") or {}
        by = block.get("by_n_ops") or {}
        key = f"resp_{effort}"
        for o in ("1", "2"):
            if o in by:
                out[key][o] = by[o].get("pair_pref_choice")
        if by.get("1"):
            out[key]["mean_reasoning_1"] = by["1"].get("mean_reasoning")
        if by.get("2"):
            out[key]["mean_reasoning_2"] = by["2"].get("mean_reasoning")
    return out


def _verdicts(d3: dict) -> dict:
    """D1–D5 against locked thresholds. Do not edit thresholds after first number."""
    dec = float(d3["decisions"]["pair_pref_choice"])
    none = float(d3["resp_none"]["pair_pref_choice"])
    med = float(d3["resp_medium"]["pair_pref_choice"])
    gap = d3["contrasts"]["medium_minus_decisions"]
    none_gap = d3["contrasts"]["none_minus_decisions"]
    parent = d3["depth_curve"]
    # D5: mean reasoning tokens rise
    r1 = parent["resp_medium"].get("mean_reasoning_1")
    r2 = parent["resp_medium"].get("mean_reasoning_2")
    r3 = d3["resp_medium"]["mean_reasoning"]
    d5_ok = (
        r1 is not None and r2 is not None
        and float(r1) < float(r2) < float(r3)
    )
    return {
        "D1_decisions_le_0.65": {
            "value": dec,
            "pass": bool(dec <= 0.65),
        },
        "D2_medium_ge_0.90": {
            "value": med,
            "pass": bool(med >= 0.90),
        },
        "D3_medium_minus_decisions_ge_0.25": {
            "mean": gap["mean"],
            "lo": gap["lo"],
            "hi": gap["hi"],
            "pass": bool(gap["mean"] >= 0.25 and gap["ci_excludes_0"] and gap["lo"] > 0),
        },
        "D4_none_near_decisions": {
            "abs_delta": abs(none - dec),
            "none_minus_decisions": none_gap,
            "pass": bool(abs(none - dec) < 0.10),
        },
        "D5_reasoning_tokens_rise": {
            "mean_reasoning_1": r1,
            "mean_reasoning_2": r2,
            "mean_reasoning_3": r3,
            "pass": bool(d5_ok),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--skip-decisions", action="store_true")
    ap.add_argument("--skip-responses", action="store_true")
    ap.add_argument("--efforts", default="none,medium")
    ap.add_argument("--n-pairs", type=int, default=D.N_PAIRS)
    ap.add_argument("--smoke", type=int, default=0, help="if >0, only first N pairs")
    a = ap.parse_args()

    if not CHECK.is_file():
        raise SystemExit(
            f"missing {CHECK}; run runs/luna_depth_generator_check.py first"
        )
    check = json.loads(CHECK.read_text())
    if not check.get("ok"):
        raise SystemExit("generator check not ok")

    pairs = D.generate_depth3_pairs(seed=D.DEPTH_SEED, n_pairs=a.n_pairs)
    if a.smoke > 0:
        pairs = pairs[: a.smoke]

    out_path = Path(a.out)
    report: dict = {}
    if out_path.is_file():
        report = json.loads(out_path.read_text())

    report["task"] = "TASK_LUNA_DEPTH"
    report["depth_seed"] = D.DEPTH_SEED
    report["depth_pair_version"] = D.DEPTH_PAIR_VERSION
    report["n_pairs"] = len(pairs)
    report["n_options"] = 103
    report["generator_check"] = {
        "n_unique_3op_pool": check["n_unique_3op_pool"],
        "n_held_out": check["n_held_out"],
        "ok": check["ok"],
    }

    def _save():
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, default=float) + "\n")

    if not a.skip_decisions and "decisions" not in report:
        print(json.dumps({"phase": "decisions", "n": len(pairs)}), flush=True)
        report["decisions"] = eval_decisions(pairs)
        _save()

    efforts = tuple(e.strip() for e in a.efforts.split(",") if e.strip())
    if not a.skip_responses:
        client = LunaResponsesClient(max_output_tokens=MAX_OUT)
        report.setdefault("responses", {})
        for effort in efforts:
            if effort in report["responses"]:
                print(json.dumps({"skip": f"resp_{effort} already present"}), flush=True)
                continue
            print(json.dumps({"phase": f"resp_{effort}", "n": len(pairs)}), flush=True)
            report["responses"][effort] = eval_responses(client, pairs, effort)
            report["responses"][effort]["usage"] = client.usage()
            _save()

    # Contrasts on 3-op (paired by pair, cluster by function)
    dec_rows = {r["id"]: r for r in (report.get("decisions") or {}).get("rows") or []}
    contrasts: dict = {}
    for effort in efforts:
        rows = (report.get("responses") or {}).get(effort, {}).get("rows") or []
        if not dec_rows or not rows:
            continue
        deltas = []
        for r in rows:
            d = dec_rows.get(r["id"])
            if d is None:
                continue
            deltas.append(
                (r["function_id"], float(r["pair_pref_choice"]) - float(d["pair_pref_choice"]))
            )
        contrasts[f"{effort}_minus_decisions"] = _cluster_boot_by_fn(deltas)
    report["contrasts"] = contrasts

    parent = _parent_depth_points()
    curve = {
        "decisions": {
            "1": parent["decisions"].get("1"),
            "2": parent["decisions"].get("2"),
            "3": (report.get("decisions") or {}).get("pair_pref_choice"),
        },
        "resp_none": {
            "1": parent["resp_none"].get("1"),
            "2": parent["resp_none"].get("2"),
            "3": (report.get("responses") or {}).get("none", {}).get("pair_pref_choice"),
            "mean_reasoning_1": parent["resp_none"].get("mean_reasoning_1"),
            "mean_reasoning_2": parent["resp_none"].get("mean_reasoning_2"),
            "mean_reasoning_3": (report.get("responses") or {}).get("none", {}).get("mean_reasoning"),
        },
        "resp_medium": {
            "1": parent["resp_medium"].get("1"),
            "2": parent["resp_medium"].get("2"),
            "3": (report.get("responses") or {}).get("medium", {}).get("pair_pref_choice"),
            "mean_reasoning_1": parent["resp_medium"].get("mean_reasoning_1"),
            "mean_reasoning_2": parent["resp_medium"].get("mean_reasoning_2"),
            "mean_reasoning_3": (report.get("responses") or {}).get("medium", {}).get("mean_reasoning"),
        },
    }
    report["depth_curve"] = curve

    flat = {
        "decisions": report.get("decisions") or {},
        "resp_none": (report.get("responses") or {}).get("none") or {},
        "resp_medium": (report.get("responses") or {}).get("medium") or {},
        "contrasts": contrasts,
        "depth_curve": curve,
    }
    if (
        flat["decisions"].get("rows")
        and flat["resp_none"].get("rows")
        and flat["resp_medium"].get("rows")
        and contrasts.get("medium_minus_decisions")
    ):
        report["verdicts"] = _verdicts(flat)

    _save()
    print(json.dumps({
        "wrote": str(out_path),
        "depth_curve": curve,
        "verdicts": report.get("verdicts"),
        "contrasts": contrasts,
    }, indent=2, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

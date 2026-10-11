#!/usr/bin/env python3
"""Full Luna Decisions vs Responses (none/medium/high) — TASK_LUNA_REASONING_MODES.md.

Reuse Decisions numbers from existing artifacts. Responses modes: K=8, P=4.
Reports choice metrics + invalid/truncated rates per mode × set. No reasoning text stored.

  PYTHONPATH=.:. \\
    python scripts/eval_luna_reasoning_modes.py
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

import e1_env as E  # noqa: E402
import life_verify.env as LV  # noqa: E402
import typesafe_policy as TP  # noqa: E402
from constitutional_life.probe import ARMS, make_items, observation  # noqa: E402
from constitutional_life.cell.prompt import render_state  # noqa: E402
from constitutional_life.model.jev import RULE_INSTRUCTIONS  # noqa: E402
from constitutional_life.task.catalog import build_catalog  # noqa: E402
from openai_responses_luna import LunaResponsesClient, usd_from_usage  # noqa: E402

OUT = ROOT / "artifacts/openai_decisions/luna_modes.json"
DECISIONS_BATTERY = ROOT / "artifacts/openai_decisions/eval_openai_decisions_battery.json"
PART2_JSON = ROOT / "artifacts/openai_decisions/luna_part2_probe.json"
K = 8
P = 4
EFFORTS = ("none", "medium", "high")
MAX_OUT = 8192
BOOT_N = 5000
BOOT_SEED = 0

_CAT = build_catalog()
_DESC = [fn.description() for fn in _CAT.functions]
_PID_TO_IDX = {fn.program_id: i for i, fn in enumerate(_CAT.functions)}


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


def _sample_keys(
    client: LunaResponsesClient,
    state: str,
    question: str,
    values: list[str],
    *,
    effort: str,
    seed: int,
) -> dict:
    """K samples over P orderings → counts by canonical value + validity stats."""
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


def _modal(counts: dict[str, int], values: list[str], *, rng: np.random.Generator) -> str | None:
    if not counts:
        return None
    top = max(counts.values())
    cands = [v for v, c in counts.items() if c == top]
    if len(cands) == 1:
        return cands[0]
    return str(rng.choice(cands))


def _pair_pref(counts: dict[str, int], true_desc: str, false_desc: str) -> float:
    ct = counts.get(true_desc, 0)
    cf = counts.get(false_desc, 0)
    if ct > cf:
        return 1.0
    if cf > ct:
        return 0.0
    return 0.5


def _boot_mean(xs: list[float], *, n_boot=BOOT_N, seed=BOOT_SEED) -> dict:
    a = np.asarray(xs, float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    rng = np.random.default_rng(seed)
    boots = [float(np.mean(rng.choice(a, size=len(a), replace=True))) for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {"mean": float(np.mean(a)), "lo": float(lo), "hi": float(hi), "n": int(len(a))}


def _cluster_boot_by_fn(deltas: list[tuple[str, float]], *, n_boot=BOOT_N, seed=BOOT_SEED) -> dict:
    """Resample held-out functions; mean of pair deltas within."""
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


def eval_pairs(client: LunaResponsesClient, effort: str) -> dict:
    insts = LV.generate_lv_pairs_stratified(
        n_per_ops=LV.PAIR_EVAL_N_PER_OPS,
        split="heldout_fn",
        seed=LV.PAIR_EVAL_SEED,
        harness="canonical",
    )
    rows = []
    t0 = time.time()
    for i, inst in enumerate(insts):
        q = LV.render_receiver_lv(inst)
        values = list(q["options"])
        true_desc = _DESC[inst.function_index]
        # false = the other named say
        false_descs = [s for s in inst.named_says if s != true_desc]
        false_desc = false_descs[0] if false_descs else None
        samp = _sample_keys(
            client, q["state"], q["question"], values,
            effort=effort, seed=inst.seed,
        )
        pref = (
            _pair_pref(samp["counts"], true_desc, false_desc)
            if false_desc is not None
            else 0.5
        )
        if samp["n_valid"] == 0:
            pref = 0.5
        rows.append({
            "id": inst.id,
            "function_id": inst.function_id,
            "n_ops": inst.n_ops,
            "pair_pref_choice": pref,
            **{k: samp[k] for k in (
                "n_valid", "n_truncated", "n_invalid",
                "mean_reasoning", "max_reasoning", "status_counts",
            )},
        })
        if (i + 1) % 20 == 0 or i == 0:
            print(json.dumps({
                "set": "pairs", "effort": effort,
                "progress": f"{i+1}/{len(insts)}",
                "mean_pref": float(np.mean([r['pair_pref_choice'] for r in rows])),
                "invalid_rate": float(np.mean([r['n_invalid']/K for r in rows])),
            }), flush=True)

    def _summ(sub):
        prefs = [r["pair_pref_choice"] for r in sub]
        return {
            "n": len(sub),
            "pair_pref_choice": float(np.mean(prefs)) if prefs else float("nan"),
            "invalid_rate": float(np.mean([r["n_invalid"] / K for r in sub])),
            "truncated_rate": float(np.mean([r["n_truncated"] / K for r in sub])),
            "mean_reasoning": float(np.mean([r["mean_reasoning"] for r in sub])),
            "max_reasoning": int(max((r["max_reasoning"] for r in sub), default=0)),
        }

    out = {
        "overall": _summ(rows),
        "by_n_ops": {
            str(o): _summ([r for r in rows if r["n_ops"] == o]) for o in (1, 2)
        },
        "elapsed_s": time.time() - t0,
        "rows": rows,
    }
    return out


def eval_part2(client: LunaResponsesClient, effort: str) -> dict:
    items, pe_rejects = make_items(0, 1, None)
    arms_out = {}
    t0 = time.time()
    for arm in ("true", "false"):
        rows = []
        for item in items:
            obs = observation(item, arm)
            state = render_state(obs, channel=True)
            values = list(_DESC)
            samp = _sample_keys(
                client, state, RULE_INSTRUCTIONS, values,
                effort=effort, seed=hash(item.fn.program_id) % (2**31),
            )
            rng = np.random.default_rng(hash((item.fn.program_id, effort)) % (2**32))
            modal = _modal(samp["counts"], values, rng=rng)
            f_idx = _PID_TO_IDX[item.fn.program_id]
            true_desc = _DESC[f_idx]
            if arm == "true":
                named = true_desc
            else:
                named = item.false_rule.description()
            argmax_named = bool(modal == named) if modal is not None else False
            argmax_correct = bool(modal == true_desc) if modal is not None else False
            if samp["n_valid"] == 0:
                argmax_named = False
                argmax_correct = False
            rows.append({
                "program_id": item.fn.program_id,
                "n_ops": item.fn.n_ops,
                "argmax_named": argmax_named,
                "argmax_correct": argmax_correct,
                "n_valid": samp["n_valid"],
                "n_truncated": samp["n_truncated"],
                "n_invalid": samp["n_invalid"],
                "mean_reasoning": samp["mean_reasoning"],
                "max_reasoning": samp["max_reasoning"],
            })
        def _summ(sub):
            return {
                "n": len(sub),
                "argmax_named": float(np.mean([r["argmax_named"] for r in sub])),
                "argmax_correct": float(np.mean([r["argmax_correct"] for r in sub])),
                "invalid_rate": float(np.mean([r["n_invalid"] / K for r in sub])),
                "truncated_rate": float(np.mean([r["n_truncated"] / K for r in sub])),
                "mean_reasoning": float(np.mean([r["mean_reasoning"] for r in sub])),
                "max_reasoning": int(max((r["max_reasoning"] for r in sub), default=0)),
            }
        arms_out[arm] = {
            "overall": _summ(rows),
            "by_n_ops": {
                str(o): _summ([r for r in rows if r["n_ops"] == o]) for o in (1, 2)
            },
            "rows": rows,
        }
        print(json.dumps({
            "set": "part2", "arm": arm, "effort": effort,
            "argmax_named": arms_out[arm]["overall"]["argmax_named"],
            "invalid_rate": arms_out[arm]["overall"]["invalid_rate"],
        }), flush=True)

    false2 = arms_out["false"]["by_n_ops"]["2"]
    true2 = arms_out["true"]["by_n_ops"]["2"]
    return {
        "pe_reject_batches": pe_rejects,
        "arms": {a: {k: v for k, v in arms_out[a].items() if k != "rows"} for a in arms_out},
        "named_contrast_2op": {
            "argmax_named_true": true2["argmax_named"],
            "argmax_named_false": false2["argmax_named"],
            "delta_argmax_named": true2["argmax_named"] - false2["argmax_named"],
            "false_recover_true": false2["argmax_correct"],
        },
        "elapsed_s": time.time() - t0,
        "_rows": arms_out,  # kept briefly for optional dump
    }


def eval_e1p_partb(client: LunaResponsesClient, effort: str) -> dict:
    insts, _ = E.generate_p(50, "relabel", (6,), seed=13)
    hits = []
    meta = []
    t0 = time.time()
    n_words = 0
    for inst in insts:
        vocab = E.family_vocab(inst.family)
        l0, l2, T = E.L0_p(inst), E.L2_p(inst), E.truth_p(inst)
        values = [E.describe(it) for it in inst.items]
        for j, w in enumerate(vocab):
            if T[:, j].sum() == 0 or np.allclose(l0[j], l2[j]):
                continue
            top_l0 = set(np.flatnonzero(np.isclose(l0[j], l0[j].max())).tolist())
            top_l2 = set(np.flatnonzero(np.isclose(l2[j], l2[j].max())).tolist())
            if not (len(top_l2) == 1 and top_l2 < top_l0):
                continue
            q = E.render_receiver_p(inst, w)
            samp = _sample_keys(
                client, q["state"], q["question"], values,
                effort=effort, seed=inst.seed + j,
            )
            rng = np.random.default_rng((inst.seed + 17 * j) % (2**32))
            modal = _modal(samp["counts"], values, rng=rng)
            if samp["n_valid"] == 0 or modal is None:
                hit = 0
            else:
                top = values.index(modal)
                hit = 1 if {top} == top_l2 else 0
            hits.append(hit)
            meta.append({
                "inst_id": inst.id,
                "word": w,
                "hit_L2": hit,
                "n_invalid": samp["n_invalid"],
                "n_truncated": samp["n_truncated"],
                "mean_reasoning": samp["mean_reasoning"],
            })
            n_words += 1
        print(json.dumps({
            "set": "e1p_partb", "effort": effort,
            "n_words": n_words,
            "mean_L2": float(np.mean(hits)) if hits else None,
        }), flush=True)

    by_inst: dict[str, list[int]] = defaultdict(list)
    for i, m in enumerate(meta):
        by_inst[m["inst_id"]].append(hits[i])
    inst_ids = [iid for iid, hs in by_inst.items() if hs]
    # instance-cluster CI of mean
    rng = np.random.default_rng(BOOT_SEED)
    groups = [np.asarray(by_inst[iid], float) for iid in inst_ids]
    boots = []
    for _ in range(BOOT_N):
        pick = rng.integers(0, len(groups), size=len(groups))
        vals = np.concatenate([groups[i] for i in pick])
        boots.append(float(np.mean(vals)))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "n_words": n_words,
        "n_inst_with_words": len(inst_ids),
        "pragmatic_argmax_L2": float(np.mean(hits)) if hits else float("nan"),
        "instance_cluster_ci": {
            "mean": float(np.mean(hits)) if hits else float("nan"),
            "lo": float(lo), "hi": float(hi),
        },
        "invalid_rate": float(np.mean([m["n_invalid"] / K for m in meta])) if meta else None,
        "truncated_rate": float(np.mean([m["n_truncated"] / K for m in meta])) if meta else None,
        "mean_reasoning": float(np.mean([m["mean_reasoning"] for m in meta])) if meta else None,
        "elapsed_s": time.time() - t0,
    }


def load_decisions_baselines() -> dict:
    bat = json.loads(DECISIONS_BATTERY.read_text())
    lv = bat.get("rows", {}).get("lv_pairs") or bat.get("headline", {}).get("lv_pairs") or {}
    part_b = bat.get("rows", {}).get("e1p_part_b_choice") or {}
    part2 = json.loads(PART2_JSON.read_text()) if PART2_JSON.is_file() else {}
    # Prefer recount / by_n_ops if present
    return {
        "pairs": {
            "pair_pref_choice": lv.get("pair_pref_choice"),
            "by_n_ops": lv.get("by_n_ops") or lv.get("pair_pref_choice_by_n_ops"),
        },
        "part_b": {
            "pragmatic_argmax_L2": part_b.get("pragmatic_argmax_L2"),
        },
        "part2": {
            "readout_by_n_ops": part2.get("readout_by_n_ops"),
            "named_contrast": part2.get("named_contrast"),
            "arms": {
                a: {k: v for k, v in (part2.get("arms") or {}).get(a, {}).items()
                    if k != "by_n_ops" or True}
                for a in ("true", "false")
            },
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", nargs="+", default=["pairs", "part2", "e1p"],
                    choices=["pairs", "part2", "e1p"])
    ap.add_argument("--efforts", nargs="+", default=list(EFFORTS))
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()

    client = LunaResponsesClient(max_output_tokens=MAX_OUT)
    if not client.api_key:
        raise SystemExit("OPENAI_API_KEY missing")

    decisions = load_decisions_baselines()
    report = {
        "task": "TASK_LUNA_REASONING_MODES.md",
        "model_requested": "gpt-6-luna",
        "K": K,
        "P": P,
        "max_output_tokens": MAX_OUT,
        "decisions_baselines": decisions,
        "responses": {},
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    out_path = Path(a.out)
    # Resume: load prior checkpoint if present.
    if out_path.is_file():
        try:
            prev = json.loads(out_path.read_text())
            if prev.get("responses"):
                report["responses"] = prev["responses"]
                print(json.dumps({
                    "resume": True,
                    "have": {e: list(v.keys()) for e, v in report["responses"].items()},
                }), flush=True)
        except json.JSONDecodeError:
            pass

    def _save():
        report["model_reported"] = client.model_reported
        report["usage_so_far"] = client.usage()
        out_path.write_text(json.dumps(report, indent=2, default=float) + "\n")

    for effort in a.efforts:
        report["responses"].setdefault(effort, {})
        if "pairs" in a.sets and "pairs" not in report["responses"][effort]:
            print(json.dumps({"phase": "pairs", "effort": effort}), flush=True)
            report["responses"][effort]["pairs"] = eval_pairs(client, effort)
            _save()
            print(json.dumps({"checkpoint": f"{effort}/pairs"}), flush=True)
        if "part2" in a.sets and "part2" not in report["responses"][effort]:
            print(json.dumps({"phase": "part2", "effort": effort}), flush=True)
            p2 = eval_part2(client, effort)
            p2.pop("_rows", None)
            report["responses"][effort]["part2"] = p2
            _save()
            print(json.dumps({"checkpoint": f"{effort}/part2"}), flush=True)
        if "e1p" in a.sets and "e1p_partb" not in report["responses"][effort]:
            print(json.dumps({"phase": "e1p", "effort": effort}), flush=True)
            report["responses"][effort]["e1p_partb"] = eval_e1p_partb(client, effort)
            _save()
            print(json.dumps({"checkpoint": f"{effort}/e1p"}), flush=True)
        print(json.dumps({"checkpoint": effort, "usage": client.usage()}), flush=True)

    # Contrasts vs decisions (pairs 2-op primary).
    # Decisions must be resampled per pair — never subtract a constant mean.
    # Prefer cached per-pair prefs via evaluate_lv(return_rows=True); else refuse CI.
    contrasts = {}
    dec_by_id: dict[str, float] = {}
    try:
        from openai_decisions_client import OpenAIDecisionsClient  # noqa: WPS433

        _cli = OpenAIDecisionsClient(timeout=30.0)

        def _no_live(*_a, **_k):
            raise RuntimeError("Decisions cache miss while building contrasts")

        _cli._post = _no_live  # type: ignore[method-assign]
        _pol = TP.TypeSafePolicy(_cli, P=4)
        _insts = LV.generate_lv_pairs_stratified(
            n_per_ops=LV.PAIR_EVAL_N_PER_OPS,
            split="heldout_fn",
            seed=LV.PAIR_EVAL_SEED,
            harness="canonical",
        )
        _res = LV.evaluate_lv(_insts, _pol.receiver_policy_lv, return_rows=True)
        for _r in _res["rows"]:
            if int(_r["n_ops"]) == 2:
                dec_by_id[_r["id"]] = float(_r["pair_pref_choice"])
        decisions["pairs"]["n_decisions_2op_rows"] = len(dec_by_id)
    except Exception as e:
        contrasts["decisions_pair_rows_error"] = repr(e)

    for effort in a.efforts:
        rows = report["responses"][effort].get("pairs", {}).get("rows") or []
        if not dec_by_id or not rows:
            continue
        deltas = []
        missing = 0
        for r in rows:
            if r["n_ops"] != 2:
                continue
            if r["id"] not in dec_by_id:
                missing += 1
                continue
            deltas.append(
                (r["function_id"], float(r["pair_pref_choice"]) - dec_by_id[r["id"]])
            )
        if missing:
            contrasts[f"{effort}_minus_decisions_2op_missing"] = missing
        if deltas:
            contrasts[f"{effort}_minus_decisions_2op"] = _cluster_boot_by_fn(deltas)

    # R0: none ≤ medium ≤ high point estimates on 2-op
    pts = {
        e: report["responses"][e].get("pairs", {}).get("by_n_ops", {}).get("2", {}).get(
            "pair_pref_choice"
        )
        for e in a.efforts
    }
    if all(pts.get(e) is not None for e in ("none", "medium", "high")):
        contrasts["R0_monotone_none_le_medium_le_high"] = bool(
            pts["none"] <= pts["medium"] <= pts["high"]
        )
        contrasts["R0_points"] = pts

    # Validity summary
    validity = {}
    for effort in a.efforts:
        validity[effort] = {}
        for set_name, block in report["responses"][effort].items():
            if set_name == "pairs":
                validity[effort][set_name] = {
                    "invalid_rate": block["overall"]["invalid_rate"],
                    "truncated_rate": block["overall"]["truncated_rate"],
                    "max_reasoning": block["overall"]["max_reasoning"],
                }
            elif set_name == "part2":
                validity[effort][set_name] = {
                    a: {
                        "invalid_rate": block["arms"][a]["overall"]["invalid_rate"],
                        "truncated_rate": block["arms"][a]["overall"]["truncated_rate"],
                        "max_reasoning": block["arms"][a]["overall"]["max_reasoning"],
                    }
                    for a in block["arms"]
                }
            elif set_name == "e1p_partb":
                validity[effort][set_name] = {
                    "invalid_rate": block.get("invalid_rate"),
                    "truncated_rate": block.get("truncated_rate"),
                }

    report["contrasts"] = contrasts
    report["validity"] = validity
    report["usage_total"] = client.usage()
    report["usd_list_rate_total"] = usd_from_usage({
        "input_tokens": client.usage().get("input_tokens", 0),
        "output_tokens": client.usage().get("output_tokens", 0),
        "input_tokens_details": {"cached_tokens": 0, "cache_write_tokens": 0},
    })
    # strip pair rows from final to keep file smaller? Keep — needed for audit.
    Path(a.out).write_text(json.dumps(report, indent=2, default=float) + "\n")
    print(json.dumps({
        "wrote": a.out,
        "contrasts": {k: v for k, v in contrasts.items() if k.startswith("R") or "2op" in k},
        "validity": validity,
        "usage": client.usage(),
    }, indent=2, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

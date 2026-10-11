#!/usr/bin/env python3
"""Fix Luna modes CIs: resample Decisions per pair/instance, not a constant mean.

Cache-only. Joins Responses rows from luna_modes.json with Decisions prefs from
evaluate_lv (return_rows=True) / TypeSafePolicy cache. Writes:
  runs/openai_decisions/luna_modes_cis_fixed.json
and patches contrasts (+ R5) into luna_modes.json.
"""
from __future__ import annotations

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
from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402
from openai_responses_luna import LunaResponsesClient  # noqa: E402

MODES = ROOT / "artifacts/openai_decisions/luna_modes.json"
OUT = ROOT / "artifacts/openai_decisions/luna_modes_cis_fixed.json"
BOOT_N = 5000
BOOT_SEED = 0
K = 8
P = 4
EFFORTS = ("none", "medium", "high")


def _block_post(client, label: str) -> None:
    def _no(*_a, **_k):
        raise RuntimeError(f"{label} cache miss — refused live call")

    client._post = _no  # type: ignore[method-assign]


def _cluster_boot_by_fn(deltas: list[tuple[str, float]], *, n_boot=BOOT_N, seed=BOOT_SEED) -> dict:
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
        "method": "cluster_by_function_paired_deltas",
    }


def _inst_cluster_boot_paired(
    groups: list[tuple[np.ndarray, np.ndarray]],
    *,
    n_boot=BOOT_N,
    seed=BOOT_SEED,
) -> dict:
    """Resample instances; within each, all word-level (a−b) pairs contribute."""
    if not groups:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n_inst": 0}
    rng = np.random.default_rng(seed)
    flat = np.concatenate([a - b for a, b in groups])
    boots = []
    n = len(groups)
    for _ in range(n_boot):
        pick = rng.integers(0, n, size=n)
        vals = np.concatenate([groups[i][0] - groups[i][1] for i in pick])
        boots.append(float(np.mean(vals)))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "mean": float(np.mean(flat)),
        "lo": float(lo),
        "hi": float(hi),
        "n_inst": n,
        "n_words": int(len(flat)),
        "ci_excludes_0": bool(lo > 0 or hi < 0),
        "method": "instance_cluster_paired_word_deltas",
    }


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


def _modal(counts: dict[str, int], values: list[str], *, rng: np.random.Generator) -> str | None:
    if not counts:
        return None
    top = max(counts.values())
    cands = [v for v, c in counts.items() if c == top]
    if len(cands) == 1:
        return cands[0]
    return str(rng.choice(cands))


def decisions_pair_rows() -> list[dict]:
    cli = OpenAIDecisionsClient(timeout=30.0)
    _block_post(cli, "Decisions-lv")
    pol = TP.TypeSafePolicy(cli, P=4)
    insts = LV.generate_lv_pairs_stratified(
        n_per_ops=100, split="heldout_fn", seed=LV.PAIR_EVAL_SEED,
        harness="canonical", n_ops_filter=(1, 2),
    )
    res = LV.evaluate_lv(insts, pol.receiver_policy_lv, return_rows=True)
    assert len(res["rows"]) == 200
    out = []
    for inst, r in zip(insts, res["rows"]):
        assert inst.id == r["id"]
        out.append({
            "id": inst.id,
            "function_id": inst.function_id,
            "n_ops": int(r["n_ops"]),
            "pair_pref_choice": float(r["pair_pref_choice"]),
        })
    print(json.dumps({
        "done": "decisions_pairs",
        "n": len(out),
        "mean_2op": float(np.mean([r["pair_pref_choice"] for r in out if r["n_ops"] == 2])),
        "cache_hits": cli.usage().get("cache_hits"),
    }), flush=True)
    return out


def pairs_contrasts(modes: dict, dec_rows: list[dict]) -> dict:
    dec_by_id = {r["id"]: r for r in dec_rows}
    out = {}
    buggy = modes.get("contrasts") or {}
    for effort in EFFORTS:
        rows = (modes["responses"].get(effort) or {}).get("pairs", {}).get("rows") or []
        deltas = []
        missing = []
        for r in rows:
            if int(r["n_ops"]) != 2:
                continue
            d = dec_by_id.get(r["id"])
            if d is None:
                missing.append(r["id"])
                continue
            assert d["function_id"] == r["function_id"], (r["id"], d["function_id"], r["function_id"])
            deltas.append((r["function_id"], float(r["pair_pref_choice"]) - float(d["pair_pref_choice"])))
        if missing:
            raise RuntimeError(f"{effort}: missing Decisions ids {missing[:3]}")
        key = f"{effort}_minus_decisions_2op"
        fixed = _cluster_boot_by_fn(deltas)
        out[key] = {
            **fixed,
            "buggy_ci": buggy.get(key),
            "resp_mean_2op": float(np.mean([
                r["pair_pref_choice"] for r in rows if r["n_ops"] == 2
            ])),
            "dec_mean_2op": float(np.mean([
                d["pair_pref_choice"] for d in dec_rows if d["n_ops"] == 2
            ])),
        }
        print(json.dumps({"contrast": key, **{k: fixed[k] for k in
              ("mean", "lo", "hi", "ci_excludes_0", "n_fn")}}, default=float), flush=True)
    return out


def e1p_word_hits_decisions() -> tuple[list[dict], dict[str, list[float]]]:
    """Per qualifying word: Decisions hit_L2 + meta; also group by inst."""
    cli = OpenAIDecisionsClient(timeout=30.0)
    _block_post(cli, "Decisions-e1p")
    pol = TP.TypeSafePolicy(cli, P=4)
    insts, _ = E.generate_p(50, "relabel", (6,), seed=13)
    meta = []
    by_inst: dict[str, list[float]] = defaultdict(list)
    for inst in insts:
        vocab = E.family_vocab(inst.family)
        l0, l2, T = E.L0_p(inst), E.L2_p(inst), E.truth_p(inst)
        for j, w in enumerate(vocab):
            if T[:, j].sum() == 0 or np.allclose(l0[j], l2[j]):
                continue
            top_l0 = set(np.flatnonzero(np.isclose(l0[j], l0[j].max())).tolist())
            top_l2 = set(np.flatnonzero(np.isclose(l2[j], l2[j].max())).tolist())
            if not (len(top_l2) == 1 and top_l2 < top_l0):
                continue
            p = np.asarray(pol.receiver_policy_p(inst, w), float)
            top = set(np.flatnonzero(np.isclose(p, p.max())).tolist())
            hit = 1.0 if top == top_l2 else 0.0
            meta.append({"inst_id": inst.id, "word": w, "hit": hit})
            by_inst[inst.id].append(hit)
    print(json.dumps({
        "done": "decisions_e1p",
        "n_words": len(meta),
        "mean": float(np.mean([m["hit"] for m in meta])),
        "cache_hits": cli.usage().get("cache_hits"),
    }), flush=True)
    return meta, by_inst


def _patch_responses_cache_key_v1(client: LunaResponsesClient) -> None:
    """luna_modes.json was filled before catalog_digest/structured entered the key."""
    import hashlib

    def _cache_key_v1(
        *,
        effort: str,
        prompt: str,
        draw: int,
        catalog_digest: str | None = None,
        structured: bool = False,
    ) -> str:
        blob = json.dumps(
            {
                "model": client.model,
                "effort": effort,
                "max_output_tokens": client.max_output_tokens,
                "prompt": prompt,
                "draw": draw,
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        return hashlib.sha256(blob.encode()).hexdigest()

    client._cache_key = _cache_key_v1  # type: ignore[method-assign]


def e1p_word_hits_responses(effort: str) -> tuple[list[dict], dict[str, list[float]]]:
    """Replay Responses e1p from disk cache (same seeds as eval_luna_reasoning_modes)."""
    client = LunaResponsesClient(max_output_tokens=8192)
    _patch_responses_cache_key_v1(client)
    _block_post(client, f"Responses-{effort}-e1p")

    insts, _ = E.generate_p(50, "relabel", (6,), seed=13)
    meta = []
    by_inst: dict[str, list[float]] = defaultdict(list)
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
            counts: Counter = Counter()
            n_valid = 0
            for k in range(K):
                order = _perm_order(values, seed=inst.seed + j, perm_idx=k % P)
                row = client.choose_key(
                    q["state"], q["question"], order, effort=effort, draw=k, retry=True
                )
                if row.get("truncated") or row.get("invalid") or row.get("key") is None:
                    continue
                n_valid += 1
                idx = int(row["key"].split("_")[1])
                counts[order[idx]] += 1
            rng = np.random.default_rng((inst.seed + 17 * j) % (2**32))
            modal = _modal(dict(counts), values, rng=rng)
            if n_valid == 0 or modal is None:
                hit = 0.0
            else:
                top = values.index(modal)
                hit = 1.0 if {top} == top_l2 else 0.0
            meta.append({"inst_id": inst.id, "word": w, "hit": hit})
            by_inst[inst.id].append(hit)
    print(json.dumps({
        "done": f"responses_e1p/{effort}",
        "n_words": len(meta),
        "mean": float(np.mean([m["hit"] for m in meta])),
        "cache_hits": client.usage().get("cache_hits"),
        "requests": client.usage().get("requests"),
    }), flush=True)
    return meta, by_inst


def e1p_contrasts(dec_meta: list[dict], modes: dict) -> dict:
    # Align Decisions words as reference order
    dec_key = {(m["inst_id"], m["word"]): m["hit"] for m in dec_meta}
    out = {}
    for effort in EFFORTS:
        # Prefer replay from cache; fall back only if summary matches and we can skip
        try:
            resp_meta, _ = e1p_word_hits_responses(effort)
        except RuntimeError as e:
            print(json.dumps({"warn": f"e1p replay failed for {effort}", "error": repr(e)}),
                  flush=True)
            continue
        resp_key = {(m["inst_id"], m["word"]): m["hit"] for m in resp_meta}
        if set(resp_key) != set(dec_key):
            raise RuntimeError(f"{effort}: word-key mismatch vs Decisions")
        # group by instance
        by: dict[str, list[tuple[float, float]]] = defaultdict(list)
        for k, dh in dec_key.items():
            by[k[0]].append((resp_key[k], dh))
        groups = [
            (np.asarray([a for a, _ in pairs], float),
             np.asarray([b for _, b in pairs], float))
            for pairs in by.values()
        ]
        fixed = _inst_cluster_boot_paired(groups)
        reported = (modes["responses"].get(effort) or {}).get("e1p_partb", {}).get(
            "pragmatic_argmax_L2"
        )
        out[f"{effort}_minus_decisions_e1p"] = {
            **fixed,
            "resp_mean": float(np.mean(list(resp_key.values()))),
            "dec_mean": float(np.mean(list(dec_key.values()))),
            "reported_resp_mean": reported,
            "mean_match_reported": (
                reported is not None
                and abs(float(reported) - float(np.mean(list(resp_key.values())))) < 1e-9
            ),
        }
        print(json.dumps({
            "contrast": f"{effort}_minus_decisions_e1p",
            **{k: fixed[k] for k in ("mean", "lo", "hi", "ci_excludes_0", "n_inst")},
        }, default=float), flush=True)
    return out


def r_verdicts(pairs: dict, e1p: dict, modes: dict) -> dict:
    pts = {
        e: modes["responses"][e]["pairs"]["by_n_ops"]["2"]["pair_pref_choice"]
        for e in EFFORTS
    }
    r0 = bool(pts["none"] <= pts["medium"] <= pts["high"])
    c_high = pairs["high_minus_decisions_2op"]
    c_none = pairs["none_minus_decisions_2op"]
    r1 = bool(c_high["mean"] >= 0.15 and c_high["ci_excludes_0"] and c_high["lo"] > 0)
    r2 = bool(abs(c_none["mean"]) < 0.10)
    # R3: 1-op ≥ 0.85 all modes + decisions (dec_1 filled by caller if needed)
    dec_1 = (((modes.get("decisions_baselines") or {}).get("pairs") or {})
             .get("by_n_ops") or {}).get("1", {}).get("pair_pref_choice")
    r3_modes = {
        e: modes["responses"][e]["pairs"]["by_n_ops"]["1"]["pair_pref_choice"]
        for e in EFFORTS
    }
    # R4 point thresholds
    p2h = modes["responses"]["high"]["part2"]
    false2 = p2h["arms"]["false"]["by_n_ops"]["2"]
    # overall false also reported by user as 0.012 — check both
    false_all = p2h["arms"]["false"]["overall"]
    r4 = bool(
        false_all["argmax_named"] <= 0.50
        and false_all["argmax_correct"] > 0.10
    )
    e5 = e1p.get("high_minus_decisions_e1p")
    r5 = None
    if e5 is not None:
        r5 = bool(e5["mean"] >= 0.08 and e5["ci_excludes_0"] and e5["lo"] > 0)
    return {
        "R0_monotone": r0,
        "R0_points": pts,
        "R1": {"pass": r1, "contrast": "high_minus_decisions_2op", **{
            k: c_high[k] for k in ("mean", "lo", "hi", "ci_excludes_0")
        }},
        "R2": {"pass": r2, "abs_mean": abs(c_none["mean"]), "threshold": 0.10,
               **{k: c_none[k] for k in ("mean", "lo", "hi")}},
        "R3_1op": {
            "modes": r3_modes,
            "decisions_1op": dec_1,
            "pass": (
                dec_1 is not None
                and dec_1 >= 0.85
                and all(v >= 0.85 for v in r3_modes.values())
            ),
        },
        "R4_part2": {
            "pass": r4,
            "false_argmax_named": false_all["argmax_named"],
            "false_argmax_correct": false_all["argmax_correct"],
            "false_2op_named": false2["argmax_named"],
            "false_2op_correct": false2["argmax_correct"],
            "note": "threshold vs Decisions point refs; no Decisions-resample CI registered",
        },
        "R5_e1p": (
            {"pass": r5, **{k: e5[k] for k in ("mean", "lo", "hi", "ci_excludes_0",
                                               "resp_mean", "dec_mean")}}
            if e5 is not None else {"pass": None, "error": "e1p replay incomplete"}
        ),
    }


def main() -> int:
    t0 = time.time()
    modes = json.loads(MODES.read_text())
    dec_rows = decisions_pair_rows()
    pairs = pairs_contrasts(modes, dec_rows)
    # fill R3 decisions 1op from rows
    dec_1 = float(np.mean([r["pair_pref_choice"] for r in dec_rows if r["n_ops"] == 1]))

    print(json.dumps({"phase": "e1p"}), flush=True)
    dec_meta, _ = e1p_word_hits_decisions()
    e1p = e1p_contrasts(dec_meta, modes)

    verdicts = r_verdicts(pairs, e1p, modes)
    verdicts["R3_1op"]["decisions_1op"] = dec_1
    verdicts["R3_1op"]["pass"] = bool(
        dec_1 >= 0.85
        and all(v >= 0.85 for v in verdicts["R3_1op"]["modes"].values())
    )

    # validity note for high truncation
    val = (modes.get("validity") or {}).get("high", {}).get("pairs", {})
    note_trunc = {
        "high_pairs_truncated_rate": val.get("truncated_rate"),
        "high_pairs_invalid_rate": val.get("invalid_rate"),
        "note": (
            "One truncation on 1600 pair samples (max_output=8192); counted invalid. "
            "Medium never hit the cap (max reasoning ~5.5k)."
        ),
    }

    report = {
        "task": "TASK_LUNA_REASONING_MODES.md",
        "fix": (
            "Prior contrasts subtracted a constant Decisions mean (0.59) from each "
            "Responses pair; cluster CI only reflected Responses variance. "
            "This file joins per-pair Decisions prefs and re-bootstraps."
        ),
        "pairs_2op": pairs,
        "e1p_partb": e1p,
        "verdicts": verdicts,
        "truncation": note_trunc,
        "dose_readout": (
            "Plateau already at medium on 2-op (medium≈high ≫ none); "
            "Life arms A/B use medium."
        ),
        "elapsed_s": time.time() - t0,
    }

    # Patch luna_modes.json contrasts in place. Archive true buggy CIs once;
    # do not overwrite with a later fixed snapshot.
    BUGGY_CONSTANT_DECISIONS = {
        "none_minus_decisions_2op": {
            "mean": 0.01,
            "lo": -0.07020287322849927,
            "hi": 0.09421052631578952,
            "n_fn": 26,
            "n_pairs": 100,
            "ci_excludes_0": False,
            "bug": "subtracted constant Decisions mean 0.59",
        },
        "medium_minus_decisions_2op": {
            "mean": 0.405,
            "lo": 0.39369565217391295,
            "hi": 0.4100000000000001,
            "n_fn": 26,
            "n_pairs": 100,
            "ci_excludes_0": True,
            "bug": "subtracted constant Decisions mean 0.59",
        },
        "high_minus_decisions_2op": {
            "mean": 0.41,
            "lo": 0.4099999999999998,
            "hi": 0.4100000000000001,
            "n_fn": 26,
            "n_pairs": 100,
            "ci_excludes_0": True,
            "bug": "constant Decisions + Responses all 1.0 → zero-width CI",
        },
        "R0_monotone_none_le_medium_le_high": True,
        "R0_points": {"none": 0.6, "medium": 0.995, "high": 1.0},
    }
    prev_bug = modes.get("contrasts_buggy_constant_decisions") or {}
    # Keep original zero-width high CI if already archived; else write known buggy.
    if not (
        isinstance(prev_bug.get("high_minus_decisions_2op"), dict)
        and abs(float(prev_bug["high_minus_decisions_2op"].get("lo", 0))
                - float(prev_bug["high_minus_decisions_2op"].get("hi", 1))) < 1e-9
    ):
        modes["contrasts_buggy_constant_decisions"] = BUGGY_CONSTANT_DECISIONS
    for k, v in pairs.items():
        if k in BUGGY_CONSTANT_DECISIONS:
            v["buggy_ci"] = BUGGY_CONSTANT_DECISIONS[k]
    report["buggy_contrasts_archived"] = modes["contrasts_buggy_constant_decisions"]
    OUT.write_text(json.dumps(report, indent=2, default=float) + "\n")

    new_c = {
        k: {kk: vv for kk, vv in v.items() if kk != "buggy_ci"}
        for k, v in pairs.items()
    }
    new_c["R0_monotone_none_le_medium_le_high"] = verdicts["R0_monotone"]
    new_c["R0_points"] = verdicts["R0_points"]
    for k, v in e1p.items():
        new_c[k] = v
    new_c["verdicts"] = verdicts
    new_c["ci_fix"] = (
        "2026-10-09: Decisions resampled per pair/instance "
        "(see luna_modes_cis_fixed.json)"
    )
    modes["contrasts"] = new_c
    modes["truncation_note"] = note_trunc
    MODES.write_text(json.dumps(modes, indent=2, default=float) + "\n")
    print(json.dumps({
        "wrote": str(OUT),
        "patched": str(MODES),
        "verdicts": {
            "R0": verdicts["R0_monotone"],
            "R1": verdicts["R1"]["pass"],
            "R2": verdicts["R2"]["pass"],
            "R3": verdicts["R3_1op"]["pass"],
            "R4": verdicts["R4_part2"]["pass"],
            "R5": verdicts["R5_e1p"].get("pass"),
        },
        "high_2op_ci": [pairs["high_minus_decisions_2op"]["lo"],
                        pairs["high_minus_decisions_2op"]["hi"]],
    }, indent=2, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

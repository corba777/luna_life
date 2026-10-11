#!/usr/bin/env python3
"""Recursive listener (R2G-style) on E1-P Part-B subset — TASK_RECURSIVE_LISTENER.md Part 1.

Acceptance first (oracle S1 → L2; counterfactual render diff), then Luna Decisions.
M_0 / M_multi are #9b (GPU) — not this script's default.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

import e1_env as E  # noqa: E402
import typesafe_policy as TP  # noqa: E402
from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402

OUT_DIR = ROOT / "runs" / "recursive_listener"
PART_B_N = 50
REL_SEED = 13
BOOT_N = 5000
BOOT_SEED = 0
TIE_SEED = 17
MULTI_MEAN_LDIR = 0.677  # registered Q2 reference


def partb_words(insts):
    """Yield (inst, word_idx, word, top_l2_item) for Part-B filter words."""
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
            yield inst, j, w, next(iter(top_l2))


def inst_t(inst, t: int):
    return replace(inst, target=t, id=f"{inst.id}-t{t}")


def normalise(x: np.ndarray) -> np.ndarray:
    s = float(x.sum())
    if s <= 0:
        return np.full_like(x, 1.0 / len(x))
    return x / s


def choose_argmax(p: np.ndarray, rng: np.random.Generator) -> tuple[int, bool]:
    tops = np.flatnonzero(np.isclose(p, p.max()))
    tied = len(tops) > 1
    return int(rng.choice(tops)), tied


def L_rec_from_speaker_matrix(S: np.ndarray, w_idx: int) -> tuple[np.ndarray, bool]:
    """L_rec(t|w) ∝ S[t, w]. Returns (dist, zero_likelihood)."""
    col = np.asarray(S[:, w_idx], float)
    zero = bool(col.sum() <= 0)
    return normalise(col), zero


def oracle_check(insts) -> dict:
    """Plug env S1 for S_M; must reproduce L2 choices (pragmatic_argmax_L2 = 1.0 up to ties)."""
    hits_set, hits_choice, n_ties, n = [], [], 0, 0
    for inst, j, w, l2_item in partb_words(insts):
        S = E.S1_p(inst)  # [K, V]; independent of target
        Lr, zero = L_rec_from_speaker_matrix(S, j)
        assert not zero
        top_set = set(np.flatnonzero(np.isclose(Lr, Lr.max())).tolist())
        hits_set.append(1 if top_set == {l2_item} else 0)
        rng = np.random.default_rng((inst.seed + TIE_SEED * (j + 1)) % (2**32))
        choice, tied = choose_argmax(Lr, rng)
        n_ties += int(tied)
        hits_choice.append(1 if choice == l2_item else 0)
        n += 1
        # L2 itself is the normalised column of S1
        L2row = E.L2_p(inst)[j]
        assert np.allclose(Lr, L2row), (inst.id, w, Lr, L2row)

    mean_set = float(np.mean(hits_set)) if hits_set else float("nan")
    mean_choice = float(np.mean(hits_choice)) if hits_choice else float("nan")
    # set-match must be exact 1.0; choice can dip only on L2 ties (none on Part-B by filter)
    ok = mean_set == 1.0 and n > 0
    return {
        "n_words": n,
        "pragmatic_argmax_L2_set": mean_set,
        "pragmatic_argmax_L2_choice": mean_choice,
        "tie_rate": n_ties / n if n else float("nan"),
        "pass": ok,
    }


def counterfactual_render_check(insts, n: int = 5) -> dict:
    rows = []
    for inst in insts[:n]:
        base = E.render_sender_p(inst)
        diffs = []
        for t in range(inst.K):
            if t == inst.target:
                continue
            alt = E.render_sender_p(inst_t(inst, t))
            # Only the target line should change (plus id unused in render).
            d_state = [
                (i, a, b)
                for i, (a, b) in enumerate(
                    zip(base["state"].splitlines(), alt["state"].splitlines())
                )
                if a != b
            ]
            d_q = base["question"] != alt["question"]
            d_opts = base["options"] != alt["options"]
            diffs.append({
                "t": t,
                "n_state_line_diffs": len(d_state),
                "state_line_diffs": [
                    {"line": i, "base": a, "alt": b} for i, a, b in d_state
                ],
                "question_differs": d_q,
                "options_differ": d_opts,
            })
        # Exactly one line should mention the target description.
        ok = all(
            d["n_state_line_diffs"] == 1
            and not d["question_differs"]
            and not d["options_differ"]
            and "The target item is:" in d["state_line_diffs"][0]["base"]
            for d in diffs
        )
        rows.append({"inst_id": inst.id, "target": inst.target, "ok": ok, "diffs": diffs})
    return {"n": len(rows), "all_ok": all(r["ok"] for r in rows), "rows": rows}


def instance_cluster_ci(hits_by_inst: dict[str, list[float]], *, seed=BOOT_SEED, n_boot=BOOT_N):
    ids = [i for i, hs in hits_by_inst.items() if hs]
    if not ids:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n_inst": 0}
    groups = [np.asarray(hits_by_inst[i], float) for i in ids]
    flat = np.concatenate(groups)
    mean = float(np.mean(flat))
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(groups), size=len(groups))
        boots.append(float(np.mean(np.concatenate([groups[i] for i in pick]))))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "mean": mean,
        "lo": float(lo),
        "hi": float(hi),
        "n_inst": len(ids),
        "ci_excludes_0": bool(lo > 0 or hi < 0),
    }


def paired_delta_ci(a_by: dict, b_by: dict, *, seed=BOOT_SEED, n_boot=BOOT_N):
    """Instance-cluster bootstrap of mean(a-b) on shared words (paired by inst)."""
    ids = sorted(set(a_by) & set(b_by))
    ids = [i for i in ids if a_by[i] and b_by[i] and len(a_by[i]) == len(b_by[i])]
    if not ids:
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n_inst": 0}
    d_groups = [
        np.asarray(a_by[i], float) - np.asarray(b_by[i], float) for i in ids
    ]
    mean = float(np.mean(np.concatenate(d_groups)))
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(d_groups), size=len(d_groups))
        boots.append(float(np.mean(np.concatenate([d_groups[i] for i in pick]))))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return {
        "mean": mean,
        "lo": float(lo),
        "hi": float(hi),
        "n_inst": len(ids),
        "ci_excludes_0": bool(lo > 0 or hi < 0),
    }


def eval_model(name: str, sp, rp, insts, *, live: bool) -> dict:
    rows = []
    t0 = time.time()
    n_zero = n_ties_rec = n_ties_dir = n_ties_prod = 0
    for inst, j, w, l2_item in partb_words(insts):
        # Speaker matrix S_M[t, ·] via counterfactual targets
        S_rows = []
        for t in range(inst.K):
            S_rows.append(np.asarray(sp(inst_t(inst, t)), float))
        S = np.stack(S_rows, axis=0)  # [K, V]
        L_dir = normalise(np.asarray(rp(inst, w), float))
        L_rec, zero = L_rec_from_speaker_matrix(S, j)
        if zero:
            n_zero += 1
        L_prod = normalise(L_dir * np.asarray(S[:, j], float))

        rng = np.random.default_rng((inst.seed + TIE_SEED * (j + 1)) % (2**32))
        c_dir, tie_dir = choose_argmax(L_dir, rng)
        c_rec, tie_rec = choose_argmax(L_rec, rng)
        c_prod, tie_prod = choose_argmax(L_prod, rng)
        n_ties_dir += int(tie_dir)
        n_ties_rec += int(tie_rec)
        n_ties_prod += int(tie_prod)

        rows.append({
            "inst_id": inst.id,
            "word": w,
            "word_idx": j,
            "l2_item": int(l2_item),
            "L_dir": L_dir.tolist(),
            "L_rec": L_rec.tolist(),
            "L_prod": L_prod.tolist(),
            "S_M_w_given_t": S[:, j].tolist(),
            "choice_dir": c_dir,
            "choice_rec": c_rec,
            "choice_prod": c_prod,
            "hit_dir": int(c_dir == l2_item),
            "hit_rec": int(c_rec == l2_item),
            "hit_prod": int(c_prod == l2_item),
            "tie_dir": tie_dir,
            "tie_rec": tie_rec,
            "tie_prod": tie_prod,
            "zero_likelihood": zero,
        })
        if len(rows) % 25 == 0:
            print(json.dumps({
                "progress": name, "n_words": len(rows),
                "mean_dir": float(np.mean([r["hit_dir"] for r in rows])),
                "mean_rec": float(np.mean([r["hit_rec"] for r in rows])),
                "live": live,
            }), flush=True)

    def by_inst(key):
        out = defaultdict(list)
        for r in rows:
            out[r["inst_id"]].append(float(r[key]))
        return dict(out)

    dir_by, rec_by, prod_by = by_inst("hit_dir"), by_inst("hit_rec"), by_inst("hit_prod")
    n = len(rows)
    summary = {
        "model": name,
        "n_words": n,
        "n_inst_with_words": len(dir_by),
        "pragmatic_argmax_L2_dir": float(np.mean([r["hit_dir"] for r in rows])) if n else float("nan"),
        "pragmatic_argmax_L2_rec": float(np.mean([r["hit_rec"] for r in rows])) if n else float("nan"),
        "pragmatic_argmax_L2_prod": float(np.mean([r["hit_prod"] for r in rows])) if n else float("nan"),
        "delta_rec_minus_dir": None,
        "ci_rec": instance_cluster_ci(rec_by),
        "ci_dir": instance_cluster_ci(dir_by),
        "ci_prod": instance_cluster_ci(prod_by),
        "ci_delta_rec_dir": paired_delta_ci(rec_by, dir_by),
        "tie_rate_dir": n_ties_dir / n if n else float("nan"),
        "tie_rate_rec": n_ties_rec / n if n else float("nan"),
        "tie_rate_prod": n_ties_prod / n if n else float("nan"),
        "zero_likelihood_rate": n_zero / n if n else float("nan"),
        "elapsed_s": time.time() - t0,
        "live": live,
        "rows": rows,
    }
    summary["delta_rec_minus_dir"] = (
        summary["pragmatic_argmax_L2_rec"] - summary["pragmatic_argmax_L2_dir"]
    )
    return summary


def q_readout(luna: dict | None, m0: dict | None, multi_seeds: dict[str, dict]) -> dict:
    out: dict = {}
    if luna is not None:
        d = luna["ci_delta_rec_dir"]
        out["Q1_luna_rec_minus_dir_ge_0.10_ci_excludes_0"] = {
            "pass": bool(d["mean"] >= 0.10 and d["lo"] > 0),
            "mean": d["mean"], "lo": d["lo"], "hi": d["hi"],
        }
        out["Q3_luna_rec_ge_0.75"] = {
            "pass": bool(luna["pragmatic_argmax_L2_rec"] >= 0.75),
            "value": luna["pragmatic_argmax_L2_rec"],
        }
    if m0 is not None:
        d = m0["ci_delta_rec_dir"]
        out["Q1_m0_rec_minus_dir_ge_0.10_ci_excludes_0"] = {
            "pass": bool(d["mean"] >= 0.10 and d["lo"] > 0),
            "mean": d["mean"], "lo": d["lo"], "hi": d["hi"],
        }
        # Q2: M_0 L_rec ≥ multi mean L_dir (0.677), point estimate
        out["Q2_m0_rec_ge_multi_mean_ldir"] = {
            "pass": bool(m0["pragmatic_argmax_L2_rec"] >= MULTI_MEAN_LDIR),
            "m0_rec": m0["pragmatic_argmax_L2_rec"],
            "multi_mean_ldir_ref": MULTI_MEAN_LDIR,
        }
    if multi_seeds:
        recs = [v["pragmatic_argmax_L2_rec"] for v in multi_seeds.values()]
        dirs = [v["pragmatic_argmax_L2_dir"] for v in multi_seeds.values()]
        deltas = [v["delta_rec_minus_dir"] for v in multi_seeds.values()]
        mean_rec = float(np.mean(recs))
        mean_dir = float(np.mean(dirs))
        mean_delta = float(np.mean(deltas))
        # Q4 descriptive: multi recursive gain smaller than M_0's
        multi_gain = mean_delta
        m0_gain = (m0["delta_rec_minus_dir"] if m0 is not None else float("nan"))
        out["Q4_multi_gain_lt_m0_gain"] = {
            "pass": bool(m0 is not None and multi_gain < m0_gain),
            "multi_mean_delta": multi_gain,
            "m0_delta": m0_gain,
            "multi_mean_rec": mean_rec,
            "multi_mean_dir": mean_dir,
            "per_seed_delta": {k: float(v["delta_rec_minus_dir"]) for k, v in multi_seeds.items()},
        }
    return out


def _load_cached_pol(cache_dir: Path):
    import eval_checkpoints as EC  # local import: heavy

    return EC.cached_policies(cache_dir, env="e1p")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--oracle-only", action="store_true")
    ap.add_argument("--cache-only", action="store_true",
                    help="Refuse live API; fail on cache miss")
    ap.add_argument(
        "--models",
        default="luna",
        help="Comma list: luna,m0,multi (multi = shared e1p_multi s0–s4 caches)",
    )
    ap.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    wanted = {m.strip() for m in args.models.split(",") if m.strip()}

    insts, _ = E.generate_p(PART_B_N, "relabel", (6,), seed=REL_SEED)
    assert insts[0].id.startswith("p-relabel-s13-"), insts[0].id
    n_partb = sum(1 for _ in partb_words(insts))
    print(json.dumps({"n_inst": len(insts), "n_partb_words": n_partb, "models": sorted(wanted)}),
          flush=True)

    oracle = oracle_check(insts)
    render = counterfactual_render_check(insts, n=5)
    oracle_path = args.out_dir / "oracle_check.json"
    oracle_path.write_text(json.dumps({
        "oracle": oracle,
        "counterfactual_render": {
            "n": render["n"], "all_ok": render["all_ok"],
            "rows": [
                {"inst_id": r["inst_id"], "target": r["target"], "ok": r["ok"],
                 "n_alts_checked": len(r["diffs"]),
                 "diffs_summary": [
                     {"t": d["t"], "n_state_line_diffs": d["n_state_line_diffs"],
                      "question_differs": d["question_differs"],
                      "options_differ": d["options_differ"],
                      "changed_line": d["state_line_diffs"][0] if d["state_line_diffs"] else None}
                     for d in r["diffs"]
                 ]}
                for r in render["rows"]
            ],
        },
        "n_partb_words": n_partb,
    }, indent=2))
    print(json.dumps({"oracle": oracle, "render_ok": render["all_ok"]}), flush=True)
    if not oracle["pass"] or not render["all_ok"]:
        print("ORACLE/RENDER FAIL — stop", flush=True)
        sys.exit(2)
    if args.oracle_only:
        return

    luna = m0 = None
    multi_seeds: dict[str, dict] = {}
    usage = None

    if "luna" in wanted:
        # Reuse prior artifact if present and complete
        prior = args.out_dir / "e1p_partb_luna.json"
        if prior.is_file() and not args.cache_only:
            luna = json.loads(prior.read_text())
            print(json.dumps({"reuse": "luna", "rec": luna.get("pragmatic_argmax_L2_rec")}),
                  flush=True)
        else:
            client = OpenAIDecisionsClient(timeout=120.0)
            live = True
            if args.cache_only:
                live = False

                def _no(*_a, **_k):
                    raise RuntimeError("cache miss — refused live call (--cache-only)")

                client._post = _no  # type: ignore[method-assign]

            pol = TP.TypeSafePolicy(client, P=4)
            luna = eval_model(
                "gpt-6-luna", pol.sender_policy_p, pol.receiver_policy_p, insts, live=live
            )
            prior.write_text(json.dumps(luna, indent=2))
            usage = pol.usage() if hasattr(pol, "usage") else None

    if "m0" in wanted:
        # Prefer s0 shared cache (same M_0 weights across seeds)
        cdir = ROOT / "runs/eval_cache_e1p_s0/M_0/e1p_relabel"
        sp, rp = _load_cached_pol(cdir)
        m0 = eval_model("M_0", sp, rp, insts, live=False)
        (args.out_dir / "e1p_partb_m0.json").write_text(json.dumps(m0, indent=2))
        print(json.dumps({
            "done": "m0",
            "dir": m0["pragmatic_argmax_L2_dir"],
            "rec": m0["pragmatic_argmax_L2_rec"],
            "delta": m0["delta_rec_minus_dir"],
        }), flush=True)

    if "multi" in wanted:
        for s in range(5):
            cdir = ROOT / f"runs/eval_cache_e1p_s{s}/M_multi/e1p_relabel"
            sp, rp = _load_cached_pol(cdir)
            row = eval_model(f"M_multi_shared_s{s}", sp, rp, insts, live=False)
            multi_seeds[f"s{s}"] = row
            (args.out_dir / f"e1p_partb_multi_s{s}.json").write_text(
                json.dumps(row, indent=2)
            )
            print(json.dumps({
                "done": f"multi_s{s}",
                "dir": row["pragmatic_argmax_L2_dir"],
                "rec": row["pragmatic_argmax_L2_rec"],
                "delta": row["delta_rec_minus_dir"],
            }), flush=True)

    # Prefer existing luna summary if we skipped recompute
    if luna is None and (args.out_dir / "e1p_partb_luna.json").is_file():
        luna = json.loads((args.out_dir / "e1p_partb_luna.json").read_text())

    readout = q_readout(luna, m0, multi_seeds)
    summary = {
        "oracle_pass": True,
        "render_pass": True,
        "n_partb_words": n_partb,
        "luna": ({k: v for k, v in luna.items() if k != "rows"} if luna else None),
        "m0": ({k: v for k, v in m0.items() if k != "rows"} if m0 else None),
        "multi_shared": {
            k: {kk: vv for kk, vv in v.items() if kk != "rows"}
            for k, v in multi_seeds.items()
        },
        "predictions": readout,
        "usage": usage,
    }
    # Merge with prior summary if only partial models this run
    prev_path = args.out_dir / "summary.json"
    if prev_path.is_file():
        prev = json.loads(prev_path.read_text())
        for key in ("luna", "m0", "multi_shared", "usage"):
            if summary.get(key) in (None, {}):
                summary[key] = prev.get(key)
        # rebuild predictions with merged arms
        summary["predictions"] = q_readout(
            summary.get("luna"),
            summary.get("m0"),
            summary.get("multi_shared") or {},
        )
    prev_path.write_text(json.dumps(summary, indent=2))
    print(json.dumps({"summary_predictions": summary["predictions"]}, indent=2, default=float),
          flush=True)


if __name__ == "__main__":
    main()

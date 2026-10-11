#!/usr/bin/env python3
"""OpenAI Decisions (`gpt-6-luna`) zero-shot battery — TASK_OPENAI_DECISIONS_BATTERY.md.

Predictions locked in that task file **before** numbers. Placement only.

  PYTHONPATH=.:. \\
    python scripts/eval_openai_decisions_battery.py --n 100 --pairs --engine-check

API-only; may run parallel to GPU (QUEUE_ORDER §2b note). Does not need Spark.
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

import e1_env as E  # noqa: E402
import typesafe_policy as TP  # noqa: E402
from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402

SEEDS = {
    "e1p": {"val": 12, "relabel": 13},
    "ehp": {"val": 52, "relabel": 53},
}
PART_B_N = 50  # same stream as Part B gate (relabel seed 13, first 50)

PREDICTIONS = {
    "speaker_informative": True,
    "content_listening_good_ehp_v21": True,
    "choice_prg_between_typesafe_and_glide": True,
    "no_ehp_omission_listening": True,
    "engine_check_near_ceiling": True,
    "speak_easy_listen_hard": True,
    # Exact Part-B ladder refs (runs/reasoning/diag_e1p_partb_subset_ladder_5seed.json)
    "typesafe_choice_prg_ref": 0.5490196078431373,
    "glide_choice_prg_ref": 0.8169934640522876,
    "m0_pair_pref_choice_ref": 0.625,
}

OUTCOME_KEYS = (
    "outcomes_first", "outcomes_forced", "outcomes_uniform",
    "refusals", "forced_choice_retries", "refusal_uniform",
    "requests", "cache_hits",
)


def _json_default(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def _usage_delta(u0: dict, u1: dict) -> dict:
    keys = set(u0) | set(u1)
    return {k: u1.get(k, 0) - u0.get(k, 0) for k in sorted(keys)}


def _outcome_frac(delta: dict, *, role: str | None = None) -> dict:
    n = (
        int(delta.get("outcomes_first", 0))
        + int(delta.get("outcomes_forced", 0))
        + int(delta.get("outcomes_uniform", 0))
    )
    if n <= 0:
        out = {"n_calls": 0, "frac_first": float("nan"),
               "frac_forced": float("nan"), "frac_uniform": float("nan")}
    else:
        out = {
            "n_calls": n,
            "frac_first": delta.get("outcomes_first", 0) / n,
            "frac_forced": delta.get("outcomes_forced", 0) / n,
            "frac_uniform": delta.get("outcomes_uniform", 0) / n,
            "outcomes_first": int(delta.get("outcomes_first", 0)),
            "outcomes_forced": int(delta.get("outcomes_forced", 0)),
            "outcomes_uniform": int(delta.get("outcomes_uniform", 0)),
        }
    if role is not None:
        out["role"] = role
    return out


def _word_outcome_frac(word_stats: dict) -> dict:
    n = sum(int(word_stats.get(k, 0)) for k in ("first", "forced", "uniform", "mixed"))
    if n <= 0:
        return {"n_words": 0, "frac_first": float("nan"),
                "frac_forced": float("nan"), "frac_uniform": float("nan"),
                "frac_mixed": float("nan")}
    return {
        "n_words": n,
        "frac_first": word_stats.get("first", 0) / n,
        "frac_forced": word_stats.get("forced", 0) / n,
        "frac_uniform": word_stats.get("uniform", 0) / n,
        "frac_mixed": word_stats.get("mixed", 0) / n,
        **{k: int(word_stats.get(k, 0)) for k in ("first", "forced", "uniform", "mixed")},
    }


def _step(pol, label: str, step: str, fn):
    """Run fn(); return (result, usage_delta, outcome_frac)."""
    u0 = pol.usage()
    t0 = time.time()
    print(json.dumps({"progress": label, "step": step}), flush=True)
    result = fn()
    delta = _usage_delta(u0, pol.usage())
    frac = _outcome_frac(delta)
    print(json.dumps({
        "progress": label, "step": step, "done": True,
        "elapsed_s": round(time.time() - t0, 1),
        **{k: delta.get(k, 0) for k in OUTCOME_KEYS},
        "frac_uniform": frac.get("frac_uniform"),
    }, default=float), flush=True)
    return result, delta, frac


def _mean_receiver_p(pol: TP.TypeSafePolicy, inst, w: str):
    """π averaged over P; track per-perm outcomes on the client."""
    acc = None
    outcomes = []
    for k in range(pol.P):
        p = pol.receiver_policy_p_one(inst, w, k, draw=0)
        outcomes.append(getattr(pol.client, "last_outcome", "first"))
        acc = p if acc is None else acc + p
    return acc / pol.P, outcomes


def _listener_metrics(pol: TP.TypeSafePolicy, insts):
    """Soft prg + argmax_L2 + first-try-only sensitivity (descriptive)."""
    soft_all, soft_first = [], []
    hit_l2 = hit_l0 = n_hard = 0
    hit_l2_f = hit_l0_f = n_hard_f = 0
    word_stats = {"first": 0, "forced": 0, "uniform": 0, "mixed": 0}
    for inst in insts:
        vocab = E.family_vocab(inst.family)
        l0, l2, T = E.L0_p(inst), E.L2_p(inst), E.truth_p(inst)
        for j, w in enumerate(vocab):
            if T[:, j].sum() == 0 or np.allclose(l0[j], l2[j]):
                continue
            p, outcomes = _mean_receiver_p(pol, inst, w)
            if all(o == "first" for o in outcomes):
                tag = "first"
            elif any(o == "uniform" for o in outcomes):
                tag = "uniform"
            elif all(o in ("first", "forced") for o in outcomes) and any(
                o == "forced" for o in outcomes
            ):
                tag = "forced"
            else:
                tag = "mixed"
            word_stats[tag] = word_stats.get(tag, 0) + 1

            d0, d2 = E.js(p, l0[j]), E.js(p, l2[j])
            if d0 + d2 > 0:
                v = (d0 - d2) / (d0 + d2)
                soft_all.append(v)
                if tag == "first":
                    soft_first.append(v)

            top_l0 = set(np.flatnonzero(np.isclose(l0[j], l0[j].max())).tolist())
            top_l2 = set(np.flatnonzero(np.isclose(l2[j], l2[j].max())).tolist())
            if not (len(top_l2) == 1 and top_l2 < top_l0):
                continue
            top = set(np.flatnonzero(np.isclose(p, p.max())).tolist())
            n_hard += 1
            if top == top_l2:
                hit_l2 += 1
            if top == top_l0:
                hit_l0 += 1
            if tag == "first":
                n_hard_f += 1
                if top == top_l2:
                    hit_l2_f += 1
                if top == top_l0:
                    hit_l0_f += 1

    def _hard(h2, h0, n):
        if n == 0:
            nan = float("nan")
            return {"pragmatic_argmax_L2": nan, "pragmatic_argmax_L0": nan,
                    "pragmatic_argmax_gap": nan, "n_words_argmax": 0}
        return {
            "pragmatic_argmax_L2": h2 / n,
            "pragmatic_argmax_L0": h0 / n,
            "pragmatic_argmax_gap": (h2 - h0) / n,
            "n_words_argmax": n,
        }

    return {
        "pragmatic_index": float(np.mean(soft_all)) if soft_all else float("nan"),
        "n_words": len(soft_all),
        "pragmatic_index_first_try_only": (
            float(np.mean(soft_first)) if soft_first else float("nan")
        ),
        "n_words_first_try_only": len(soft_first),
        **_hard(hit_l2, hit_l0, n_hard),
        "pragmatic_argmax_L2_first_try_only": (
            hit_l2_f / n_hard_f if n_hard_f else float("nan")
        ),
        "n_words_argmax_first_try_only": n_hard_f,
        "word_outcome_counts": word_stats,
        "word_outcomes": _word_outcome_frac(word_stats),
        "note_first_try": (
            "first_try_only = all P perms returned outcome=first (no force/uniform). "
            "Descriptive beside primary; not a substitute."
        ),
    }


def _eval_e1p(pol: TP.TypeSafePolicy, insts, label: str) -> dict:
    t0 = time.time()
    u0 = pol.usage()
    outcomes_by_step = {}

    r = []
    u_step = pol.usage()
    for i, inst in enumerate(insts):
        r.append(
            float(E.expected_reward_p(inst, pol.sender_policy_p, pol.receiver_policy_p))
        )
        if (i + 1) % 5 == 0 or i + 1 == len(insts):
            u = pol.usage()
            print(json.dumps({
                "progress": label, "step": "R_team",
                "i": i + 1, "n": len(insts),
                "mean_R": float(np.mean(r)),
                "requests": u.get("requests", 0) - u0.get("requests", 0),
                "cache_hits": u.get("cache_hits", 0) - u0.get("cache_hits", 0),
                "refusals": u.get("refusals", 0) - u0.get("refusals", 0),
                "refusal_uniform": u.get("refusal_uniform", 0) - u0.get("refusal_uniform", 0),
                "elapsed_s": round(time.time() - t0, 1),
            }), flush=True)
    outcomes_by_step["R_team"] = _outcome_frac(
        _usage_delta(u_step, pol.usage()), role="mixed_sender_receiver"
    )

    refs = [E.references_p(i) for i in insts]
    si, d_si, o_si = _step(
        pol, label, "speaker_index",
        lambda: E.speaker_index_p(insts, pol.sender_policy_p),
    )
    o_si = {**o_si, "role": "sender"}
    outcomes_by_step["speaker_index"] = o_si

    # Clear in-memory policy cache so listener path sees client.last_outcome per perm.
    pol.clear_cache()
    listen, d_listen, o_listen = _step(
        pol, label, "listener",
        lambda: _listener_metrics(pol, insts),
    )
    o_listen = {
        **o_listen,
        "role": "receiver",
        "by_word": listen.get("word_outcomes"),
    }
    outcomes_by_step["listener"] = o_listen

    fid, d_fid, o_fid = _step(
        pol, label, "protocol_fidelity",
        lambda: E.protocol_fidelity_p(
            insts, pol.sender_policy_p, pol.receiver_policy_p
        ),
    )
    o_fid = {**o_fid, "role": "mixed_sender_receiver"}
    outcomes_by_step["protocol_fidelity"] = o_fid

    out = {
        "set": label,
        "n": len(insts),
        "R_team": float(np.mean(r)),
        **{f"ref_{k}": float(np.mean([ref[k] for ref in refs])) for k in refs[0]},
        **si,
        **listen,
        **fid,
        "lite": True,
        "seconds": time.time() - t0,
        "usage_delta": _usage_delta(u0, pol.usage()),
        "outcomes_by_step": outcomes_by_step,
    }
    return out


def _eval_part_b_choice(pol: TP.TypeSafePolicy) -> dict:
    """Prediction 3 primary: pragmatic_argmax_L2 on Part-B subset (n=50, seed 13)."""
    insts, _ = E.generate_p(PART_B_N, "relabel", (6,), seed=SEEDS["e1p"]["relabel"])
    # Assert ids match the registered Part-B stream head.
    assert insts[0].id.startswith("p-relabel-s13-"), insts[0].id
    # Same id stream as Part-B ladder artifact.
    ladder = Path("runs/reasoning/diag_e1p_partb_subset_ladder_5seed.json")
    if ladder.is_file():
        meta = json.loads(ladder.read_text())
        expected_n = int(meta.get("n_inst") or meta.get("n") or PART_B_N)
        assert len(insts) == expected_n or expected_n == PART_B_N, (
            len(insts), expected_n
        )
    pol.clear_cache()
    u0 = pol.usage()
    listen = _listener_metrics(pol, insts)
    usage_delta = _usage_delta(u0, pol.usage())
    return {
        "subset": (
            "Part B gate: E1-P relabel seed=13 first n=50, L0≠L2 + L2⊂L0 top "
            "(same as pragmatic_argmax_agree_p / diag_e1p_partb_subset_ladder_5seed)"
        ),
        "n_inst": PART_B_N,
        "instance_ids_head": [insts[i].id for i in range(min(3, len(insts)))],
        "gen_seed": SEEDS["e1p"]["relabel"],
        "typesafe_choice_prg_ref": PREDICTIONS["typesafe_choice_prg_ref"],
        "glide_choice_prg_ref": PREDICTIONS["glide_choice_prg_ref"],
        **listen,
        "usage_delta": usage_delta,
        "outcomes": _outcome_frac(usage_delta, role="receiver"),
    }


def _eval_ehp(pol: TP.TypeSafePolicy, insts, label: str) -> dict:
    t0 = time.time()
    u0 = pol.usage()

    def sender(inst, i):
        return pol.sender_policy_hp(inst, i)

    def receiver(inst, j, fact):
        return pol.receiver_policy_hp(inst, j, fact)

    out = E.evaluate_hp(insts, sender, receiver)
    out["set"] = label
    out["seconds"] = time.time() - t0
    out["usage_delta"] = _usage_delta(u0, pol.usage())
    out["outcomes"] = _outcome_frac(out["usage_delta"])
    if "override_other_dim" in out and "P_anti_none" in out:
        out["other_minus_none"] = float(out["override_other_dim"] - out["P_anti_none"])
    return out


def _eval_pairs(pol: TP.TypeSafePolicy, *, n_per_ops: int = 100) -> dict:
    import life_verify.env as LV

    t0 = time.time()
    u0 = pol.usage()
    insts = LV.generate_lv_pairs_stratified(
        n_per_ops=n_per_ops, split="heldout_fn", seed=LV.PAIR_EVAL_SEED,
        harness="canonical", n_ops_filter=(1, 2),
    )
    res = LV.evaluate_lv(insts, pol.receiver_policy_lv, return_rows=False)
    res["set"] = "lv_pairs_nops_matched"
    res["pair_eval_version"] = getattr(LV, "PAIR_EVAL_VERSION", "nops_matched_v1")
    res["seconds"] = time.time() - t0
    res["usage_delta"] = _usage_delta(u0, pol.usage())
    res["outcomes"] = _outcome_frac(res["usage_delta"])
    res["vs_chance_pref_choice"] = float(res.get("pair_pref_choice", float("nan")) - 0.5)
    res["vs_m0_pref_choice"] = float(
        res.get("pair_pref_choice", float("nan")) - PREDICTIONS["m0_pair_pref_choice_ref"]
    )
    return res


def _eval_engine_check(pol: TP.TypeSafePolicy, *, n_per_ops: int = 100) -> dict:
    """Prediction 5: engine_check_v1 vs default on nops-matched pairs (API)."""
    import life_verify.env as LV

    pass  # engine_check lives in life_verify
    from life_verify.engine_check import render_with_engine_check  # noqa: E402

    insts = LV.generate_lv_pairs_stratified(
        n_per_ops=n_per_ops, split="heldout_fn", seed=LV.PAIR_EVAL_SEED,
        harness="canonical", n_ops_filter=(1, 2),
    )

    def _score(with_check: bool) -> dict:
        orig = LV.render_state_lv

        def _wrapped(inst):
            if not with_check:
                return orig(inst)
            return render_with_engine_check(inst, base=orig(inst))

        LV.render_state_lv = _wrapped  # type: ignore
        pol.clear_cache()
        try:
            by_ops: dict[int, list[float]] = {1: [], 2: []}
            pref_ops: dict[int, list[float]] = {1: [], 2: []}
            for inst in insts:
                # Bypass content-key cache: average P fresh ones.
                acc = None
                for k in range(pol.P):
                    p = pol.receiver_policy_lv_one(inst, k, draw=0)
                    acc = p if acc is None else acc + p
                p = acc / pol.P
                f = inst.function_index
                names = LV.named_indices(inst)
                false = [n for n in names if n != f][0]
                choice = int(np.argmax(p))
                top = np.flatnonzero(np.isclose(p, p.max()))
                choice_f = 1.0 if (len(top) == 1 and choice == f) else 0.0
                pref = 1.0 if p[f] > p[false] else (0.0 if p[f] < p[false] else 0.5)
                by_ops[inst.n_ops].append(choice_f)
                pref_ops[inst.n_ops].append(pref)
            return {
                "n": len(insts),
                "pair_acc_choice": float(np.mean(by_ops[1] + by_ops[2])),
                "pair_pref_choice": float(np.mean(pref_ops[1] + pref_ops[2])),
                "by_n_ops": {
                    str(o): {
                        "n": len(by_ops[o]),
                        "pair_acc_choice": float(np.mean(by_ops[o])),
                        "pair_pref_choice": float(np.mean(pref_ops[o])),
                    }
                    for o in (1, 2)
                },
            }
        finally:
            LV.render_state_lv = orig  # type: ignore

    u0 = pol.usage()
    default = _score(False)
    checked = _score(True)
    delta = checked["pair_acc_choice"] - default["pair_acc_choice"]
    band = (
        "large" if delta >= 0.20 or checked["pair_acc_choice"] >= 0.70
        else "partial" if delta >= 0.05
        else "null"
    )
    usage_delta = _usage_delta(u0, pol.usage())
    return {
        "amendment": "AMENDMENT_L_VERIFY_ENGINE_CHECK",
        "surface": "engine_check_v1",
        "pair_eval_version": LV.PAIR_EVAL_VERSION,
        "default": default,
        "engine_check_v1": checked,
        "delta_choice": delta,
        "delta_pref_choice": (
            checked["pair_pref_choice"] - default["pair_pref_choice"]
        ),
        "band": band,
        "usage_delta": usage_delta,
        "outcomes": _outcome_frac(usage_delta),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--P", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--diag-n", type=int, default=20)
    ap.add_argument("--skip-e1p", action="store_true")
    ap.add_argument("--skip-v21", action="store_true")
    ap.add_argument("--pairs", action="store_true", help="L-VERIFY nops-matched pairs")
    ap.add_argument(
        "--engine-check", action="store_true",
        help="engine_check_v1 vs default on nops-matched pairs (pred 5)",
    )
    ap.add_argument("--n-per-ops", type=int, default=100)
    ap.add_argument("--smoke-only", action="store_true")
    ap.add_argument("--merge-from", default="")
    ap.add_argument("--out", default="artifacts/openai_decisions/eval_openai_decisions_battery.json")
    a = ap.parse_args()

    client = OpenAIDecisionsClient(timeout=a.timeout)
    if not client.api_key:
        raise SystemExit("OPENAI_API_KEY missing")
    print(client.check(), flush=True)
    lim = client.probe_n_choices(101)
    print(json.dumps({"phase": "n_choices_101", **lim}, default=float), flush=True)
    if not lim.get("ok"):
        raise SystemExit("101-choice probe failed — abort before Life/pairs")

    if a.smoke_only:
        path = Path(a.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "smoke_only": True,
            "stamp": client.stamp(),
            "n_choices_101": lim,
            "predictions": PREDICTIONS,
        }, indent=2, default=_json_default))
        print("wrote", path, flush=True)
        return

    pol = TP.TypeSafePolicy(client, P=a.P)
    out = {
        "note": (
            "OpenAI Decisions battery. Predictions locked in "
            "TASK_OPENAI_DECISIONS_BATTERY.md before numbers. Placement only. "
            "Refusal fallback: opaque values → force appendix → letters → uniform; "
            "report outcomes_*; first_try_only listener metrics are descriptive."
        ),
        "task": "TASK_OPENAI_DECISIONS_BATTERY.md",
        "stamp": client.stamp(),
        "n": a.n,
        "P": a.P,
        "predictions": PREDICTIONS,
        "n_choices_101": lim,
        "rows": {},
        "diag": {},
        "queue_note": (
            "Ran API-parallel to v1b GPU pilot (QUEUE_ORDER §2b): preds locked "
            "before numbers; no Spark / no pilot attention steal."
        ),
    }
    if a.merge_from:
        prior = json.loads(Path(a.merge_from).read_text())
        out["rows"].update(prior.get("rows") or {})
        out["diag"].update(prior.get("diag") or {})
        out["resumed_from"] = a.merge_from

    if a.diag_n > 0 and not a.skip_e1p:
        print(json.dumps({"phase": "diag_e1p"}), flush=True)
        diag_insts, _ = E.generate_p(
            a.diag_n, "relabel", (6,), seed=SEEDS["e1p"]["relabel"]
        )
        out["diag"]["e1p_order"] = TP.order_check_e1p(
            pol, diag_insts, n_questions=a.diag_n
        )
        out["diag"]["e1p_noise"] = TP.noise_check_e1p(
            pol, diag_insts, n_questions=a.diag_n
        )
        # Determinism fact for the report (draw=0 vs draw=1).
        out["diag"]["e1p_noise_note"] = (
            "noise_check uses real second API draw=1; L1=0 ⇒ deterministic beta API"
        )
        print(json.dumps({"diag": out["diag"]}, default=float), flush=True)

    if not a.skip_e1p:
        for split in ("val", "relabel"):
            label = f"e1p_{split}"
            print(json.dumps({"phase": label}), flush=True)
            family = "train" if split == "val" else "relabel"
            Ks = (4, 6) if split == "val" else (6,)
            insts, _ = E.generate_p(a.n, family, Ks, seed=SEEDS["e1p"][split])
            block = _eval_e1p(pol, insts, label)
            out["rows"][label] = block
            print(json.dumps({
                "done": label,
                "R_team": block["R_team"],
                "speaker_index": block.get("speaker_index"),
                "pragmatic_index": block.get("pragmatic_index"),
                "pragmatic_argmax_L2": block.get("pragmatic_argmax_L2"),
                "refusal_uniform": block["usage_delta"].get("refusal_uniform"),
                "outcomes_uniform": block["usage_delta"].get("outcomes_uniform"),
                "usage_delta": block["usage_delta"],
            }, default=float), flush=True)

        print(json.dumps({"phase": "e1p_part_b_choice"}), flush=True)
        part_b = _eval_part_b_choice(pol)
        out["rows"]["e1p_part_b_choice"] = part_b
        wo = part_b.get("word_outcomes") or {}
        print(json.dumps({
            "done": "e1p_part_b_choice",
            "pragmatic_argmax_L2": part_b.get("pragmatic_argmax_L2"),
            "pragmatic_argmax_L2_first_try_only": part_b.get(
                "pragmatic_argmax_L2_first_try_only"
            ),
            "pragmatic_index": part_b.get("pragmatic_index"),
            "n_words": part_b.get("n_words"),
            "word_outcomes": wo,
            "frac_uniform_words": wo.get("frac_uniform"),
            "caveat_uniform": (
                (wo.get("frac_uniform") or 0) > 0.03
            ),
        }, default=float), flush=True)

    if not a.skip_v21:
        for split in ("val", "relabel"):
            label = f"ehp_v2_1_{split}"
            print(json.dumps({"phase": label}), flush=True)
            family = "train" if split == "val" else "relabel"
            with E.ehp_variant("b"), E.prompt_variant("goal_explicit"):
                insts, _ = E.generate_hp(
                    a.n, family, seed=SEEDS["ehp"][split], variant="b"
                )
                block = _eval_ehp(pol, insts, label)
            out["rows"][label] = block
            print(json.dumps({
                "done": label,
                "R_team": block["R_team"],
                "requirement_share": block.get("requirement_share"),
                "value_discrimination": block.get("value_discrimination"),
                "P_anti_none": block.get("P_anti_none"),
                "other_minus_none": block.get("other_minus_none"),
                "usage_delta": block["usage_delta"],
            }, default=float), flush=True)

    if a.engine_check:
        print(json.dumps({"phase": "engine_check_v1"}), flush=True)
        block = _eval_engine_check(pol, n_per_ops=a.n_per_ops)
        out["rows"]["engine_check"] = block
        print(json.dumps({
            "done": "engine_check",
            "delta_choice": block.get("delta_choice"),
            "band": block.get("band"),
            "default": block.get("default", {}).get("pair_acc_choice"),
            "checked": block.get("engine_check_v1", {}).get("pair_acc_choice"),
        }, default=float), flush=True)

    if a.pairs:
        print(json.dumps({"phase": "lv_pairs"}), flush=True)
        block = _eval_pairs(pol, n_per_ops=a.n_per_ops)
        out["rows"]["lv_pairs"] = block
        print(json.dumps({
            "done": "lv_pairs",
            "pair_pref_choice": block.get("pair_pref_choice"),
            "pair_pref_mass": block.get("pair_pref_mass"),
            "vs_m0": block.get("vs_m0_pref_choice"),
        }, default=float), flush=True)

    out["stamp"] = client.stamp()
    out["usage_total"] = pol.usage()
    rel_e1p = out["rows"].get("e1p_relabel", {})
    part_b = out["rows"].get("e1p_part_b_choice", {})
    rel_v21 = out["rows"].get("ehp_v2_1_relabel", {})
    eng = out["rows"].get("engine_check", {})
    out["headline"] = {
        "e1p_relabel": {
            "R_team": rel_e1p.get("R_team"),
            "speaker_index": rel_e1p.get("speaker_index"),
            "pragmatic_index": rel_e1p.get("pragmatic_index"),
            "pragmatic_index_first_try_only": rel_e1p.get(
                "pragmatic_index_first_try_only"
            ),
            "outcomes_by_step": rel_e1p.get("outcomes_by_step"),
            "usage_refusal_uniform": (rel_e1p.get("usage_delta") or {}).get(
                "refusal_uniform"
            ),
        },
        "e1p_part_b_choice": {
            "pragmatic_argmax_L2": part_b.get("pragmatic_argmax_L2"),
            "pragmatic_argmax_L2_first_try_only": part_b.get(
                "pragmatic_argmax_L2_first_try_only"
            ),
            "pragmatic_index": part_b.get("pragmatic_index"),
            "pragmatic_index_first_try_only": part_b.get(
                "pragmatic_index_first_try_only"
            ),
            "n_words": part_b.get("n_words"),
            "word_outcomes": part_b.get("word_outcomes"),
            "word_outcome_counts": part_b.get("word_outcome_counts"),
            "outcomes": part_b.get("outcomes"),
            "typesafe_choice_prg_ref": PREDICTIONS["typesafe_choice_prg_ref"],
            "glide_choice_prg_ref": PREDICTIONS["glide_choice_prg_ref"],
            "caveat_uniform_gt_3pct_receiver_words": (
                (part_b.get("word_outcomes") or {}).get("frac_uniform", 0) > 0.03
            ),
        },
        "ehp_v2_1_relabel": {
            "R_team": rel_v21.get("R_team"),
            "requirement_share": rel_v21.get("requirement_share"),
            "value_discrimination": rel_v21.get("value_discrimination"),
            "P_anti_none": rel_v21.get("P_anti_none"),
            "other_minus_none": rel_v21.get("other_minus_none"),
        },
        "engine_check": {
            "delta_choice": eng.get("delta_choice"),
            "band": eng.get("band"),
            "default_choice": (eng.get("default") or {}).get("pair_acc_choice"),
            "checked_choice": (eng.get("engine_check_v1") or {}).get(
                "pair_acc_choice"
            ),
        },
        "lv_pairs": {
            k: out["rows"].get("lv_pairs", {}).get(k)
            for k in (
                "pair_pref_choice", "pair_pref_mass",
                "vs_m0_pref_choice", "vs_chance_pref_choice",
            )
        },
        "followup_paired": (
            "runs/openai_decisions/diag_luna_paired.json — pred3 word/inst "
            "bootstraps vs M_0/TypeSafe/GLiDE; pred5b paired vs M_0 + by n_ops"
        ),
    }
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, default=_json_default))
    print(json.dumps({
        "done": True,
        "out": a.out,
        "headline": out["headline"],
        "usage_total": out["usage_total"],
        "stamp": out["stamp"],
    }, indent=2, default=float), flush=True)


if __name__ == "__main__":
    main()

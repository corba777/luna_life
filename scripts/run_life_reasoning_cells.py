#!/usr/bin/env python3
"""Full Luna arms A–D on the frozen stratified seed schedule.

  PYTHONPATH=.:. \\
    python scripts/run_life_reasoning_cells.py --arms B --max-workers 16

Schedule: runs/life_reasoning_cells/seed_schedule.json (must exist; frozen before metrics).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from constitutional_life.v1a_constants import EPOCH_LENGTH  # noqa: E402

from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402
from openai_responses_luna import LunaResponsesClient  # noqa: E402

from life_verify.v1b import SimulationV1b, metrics_bundle  # noqa: E402
from life_verify.v1b.luna_cells import (  # noqa: E402
    LunaDecisionsCompleter,
    LunaResponsesCompleter,
)
from life_verify.v1b.sources import SOURCE_IDS, is_source  # noqa: E402
from constitutional_life.board.geometry import N_CELLS  # noqa: E402

OUT = ROOT / "runs/life_reasoning_cells"
SCHEDULE = OUT / "seed_schedule.json"

ARM_SPEC = {
    "A": {"mode": "responses", "sparse": False, "k": 0, "effort": "medium", "channel": True},
    "B": {"mode": "responses", "sparse": True, "k": 0, "effort": "medium", "channel": True},
    # B-silent: same cells/sparse/sources as B, channel off (individual-learning floor).
    # Amendment 2026-10-10 — see TASK_LIFE_REASONING_CELLS.md; not in L1–L6.
    "Bs": {"mode": "responses", "sparse": True, "k": 0, "effort": "medium", "channel": False},
    # Registered C/D: decode=sample (= JEV_DECODE / M_0). Ca/Da = argmax amendment
    # (2026-10-10): paper “one-pass vs reasoning” / L5 marks reading use Ca/Da;
    # C/D-sample kept and reported. Ca/Da share Decisions API cache with C/D.
    "C": {
        "mode": "decisions", "sparse": True, "k": 0, "effort": None, "channel": True,
        "decode": "sample",
    },
    "Ca": {
        "mode": "decisions", "sparse": True, "k": 0, "effort": None, "channel": True,
        "decode": "argmax", "cache_arm": "C",
    },
    # Cas = Ca without channel (AMENDMENT_LIFE_CAS.md). Own cache — prompts omit inbox.
    "Cas": {
        "mode": "decisions", "sparse": True, "k": 0, "effort": None, "channel": False,
        "decode": "argmax",
    },
    "D": {
        "mode": "decisions", "sparse": True, "k": 1, "effort": None, "channel": True,
        "decode": "sample",
    },
    "Da": {
        "mode": "decisions", "sparse": True, "k": 1, "effort": None, "channel": True,
        "decode": "argmax", "cache_arm": "D",
    },
}


def _make_completer(arm: str, *, max_workers: int, cache_dir: Path):
    spec = ARM_SPEC[arm]
    if spec["mode"] == "responses":
        client = LunaResponsesClient(
            cache_dir=cache_dir,
            use_cache=True,
            max_output_tokens=8192,
            timeout=600.0,
        )
        return LunaResponsesCompleter(
            client, effort=spec["effort"], max_workers=max_workers
        )
    client = OpenAIDecisionsClient(cache_dir=cache_dir, use_cache=True, timeout=120.0)
    decode = spec.get("decode") or "sample"
    return LunaDecisionsCompleter(
        client, P=4, max_workers=max_workers, decode=decode
    )


def run_one(arm: str, world_seed: int, *, max_workers: int, n_gens: int) -> dict:
    spec = ARM_SPEC[arm]
    save = OUT / f"arm_{arm}" / f"seed{world_seed}"
    save.mkdir(parents=True, exist_ok=True)
    report_path = save / "report.json"
    if report_path.is_file():
        prev = json.loads(report_path.read_text())
        if prev.get("complete"):
            print(json.dumps({"skip": True, "arm": arm, "seed": world_seed}), flush=True)
            return prev

    cache_key = spec.get("cache_arm") or arm
    cache = OUT / f"cache_{cache_key}"
    completer = _make_completer(arm, max_workers=max_workers, cache_dir=cache)
    sim = SimulationV1b(
        world_seed=world_seed,
        substrate="local",
        sparse=spec["sparse"],
        channel=bool(spec.get("channel", True)),
        k=spec["k"],
        seeded=True,
        allow_sparse_seeded=True,
        completer=completer,
        policy_label=f"life-reasoning-{arm}",
    )
    pe0 = sim.fn.description()
    n_ops0 = sim.fn.n_ops
    def _assert_non_source_rules_logged() -> None:
        """Invariant: model cells must leave a non-None inferred_rule in the log.

        ``unsolved`` (Responses invalid→fallback after retry) is legal and passes.
        Only a silent ``None`` (parse drop) aborts.
        """
        if not sim.rule_history:
            return
        row = sim.rule_history[-1]
        rules = {int(k): v for k, v in row["rules"].items()}
        for cid in range(N_CELLS):
            if is_source(cid, seeded=True):
                continue
            if rules.get(cid) is None:
                raise RuntimeError(
                    f"arm={arm} seed={world_seed} gen={row.get('generation')}: "
                    f"non-source cell {cid} has inferred_rule=None in rule_history "
                    f"(silent drop — refuse and abort; unsolved fallback is OK)"
                )

    def _assert_no_channel_invariants() -> None:
        """Cas/Bs: empty inbox + no delivered says (AMENDMENT_LIFE_CAS / Bs fix)."""
        if bool(spec.get("channel", True)):
            return
        if not sim.rule_history:
            return
        row = sim.rule_history[-1]
        inbox = row.get("inbox_says") or {}
        for cid, says in inbox.items():
            if says:
                raise RuntimeError(
                    f"arm={arm} seed={world_seed} gen={row.get('generation')}: "
                    f"channel=False but cell {cid} inbox_says={says!r}"
                )

    t0 = time.time()
    for g in range(n_gens):
        sim.step()
        _assert_non_source_rules_logged()
        _assert_no_channel_invariants()
        print(json.dumps({
            "arm": arm, "seed": world_seed, "gen": g + 1, "n_gens": n_gens,
            "p_e": pe0, "n_ops": n_ops0,
            "elapsed_s": round(time.time() - t0, 1),
        }), flush=True)

    bundle = metrics_bundle(sim.rule_history)
    usage = completer.usage() if hasattr(completer, "usage") else {}
    stats = completer.stats() if hasattr(completer, "stats") else {}
    report = {
        "arm": arm,
        "world_seed": world_seed,
        "p_e": pe0,
        "n_ops": n_ops0,
        "spec": spec,
        "n_gens": n_gens,
        "n_sources": len(SOURCE_IDS),
        "elapsed_s": time.time() - t0,
        "metrics": bundle,
        "usage": usage,
        "completer_stats": stats,
        "complete": True,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (save / "rule_history.json").write_text(json.dumps(sim.rule_history) + "\n")
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    # slim metrics row for rolling summary
    slim = {
        "arm": arm, "world_seed": world_seed, "p_e": pe0, "n_ops": n_ops0,
        "j": bundle.get("j"),
        "frac_correct_lock_epochs": bundle.get("frac_correct_lock_epochs"),
        "infection": bundle.get("infection"),
        "retention": bundle.get("retention"),
        "genesis": bundle.get("genesis"),
        "elapsed_s": report["elapsed_s"],
    }
    print(json.dumps({"done": slim}, default=float), flush=True)
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--arms", default="B",
        help="Comma list A,B,Bs,C,Ca,Cas,D,Da (Cas = Ca channel off; Ca/Da argmax)",
    )
    ap.add_argument("--max-workers", type=int, default=16)
    ap.add_argument("--n-gens", type=int, default=EPOCH_LENGTH)
    ap.add_argument("--seeds", default="",
                    help="Optional override world_seeds comma list; default = schedule")
    args = ap.parse_args()
    if not SCHEDULE.is_file():
        raise SystemExit(f"missing frozen schedule: {SCHEDULE}")
    sched = json.loads(SCHEDULE.read_text())
    if args.seeds.strip():
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    else:
        seeds = list(sched["world_seeds"])
    def _norm_arm(a: str) -> str:
        a = a.strip()
        low = a.lower().replace("-", "_")
        # Mixed-case arms must not become BS / CA under .upper()
        if low in ("bs", "b_silent", "bsilent"):
            return "Bs"
        if low in ("cas", "ca_silent", "casilent"):
            return "Cas"
        if low in ("ca", "c_argmax", "cargmax"):
            return "Ca"
        if low in ("da", "d_argmax", "dargmax"):
            return "Da"
        return a.upper()

    arms = [_norm_arm(a) for a in args.arms.split(",") if a.strip()]
    for a in arms:
        if a not in ARM_SPEC:
            raise SystemExit(f"unknown arm {a}; known={sorted(ARM_SPEC)}")

    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps({
        "start": datetime.now(timezone.utc).isoformat(),
        "arms": arms, "seeds": seeds, "n_gens": args.n_gens,
        "schedule": str(SCHEDULE),
    }), flush=True)

    rows = []
    for arm in arms:
        for seed in seeds:
            rows.append(run_one(arm, seed, max_workers=args.max_workers, n_gens=args.n_gens))

    summary = {
        "task": "TASK_LIFE_REASONING_CELLS.md",
        "schedule": sched,
        "arms": arms,
        "seeds": seeds,
        "n_gens": args.n_gens,
        "rows": [
            {
                "arm": r["arm"], "world_seed": r["world_seed"], "p_e": r["p_e"],
                "n_ops": r["n_ops"], "metrics": r.get("metrics"),
                "elapsed_s": r.get("elapsed_s"),
            }
            for r in rows
        ],
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "summary_partial.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"wrote": str(OUT / "summary_partial.json"), "n_rows": len(rows)}),
          flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Long-chain Life arms: B1/Ca1/Da1 (1 source) + B0 (0 sources).

Predictions: prereg/TASK_LIFE_LONG_CHAIN.md and prereg/AMENDMENT_LONG_CHAIN_B0.md
(locked before the corresponding API calls). Cost cap $40 overall; B0 alone $5.

  PYTHONPATH=. python scripts/run_life_long_chain.py --arms B1,Ca1,Da1 --max-workers 16
  PYTHONPATH=. python scripts/run_life_long_chain.py --arms B0 --cost-cap 5 --max-workers 16
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

from constitutional_life.board.geometry import N_CELLS  # noqa: E402
from constitutional_life.v1a_constants import EPOCH_LENGTH  # noqa: E402

from openai_decisions_client import OpenAIDecisionsClient  # noqa: E402
from openai_responses_luna import LunaResponsesClient, usd_from_usage  # noqa: E402

from life_verify.v1b import SimulationV1b, metrics_bundle  # noqa: E402
from life_verify.v1b.luna_cells import (  # noqa: E402
    LunaDecisionsCompleter,
    LunaResponsesCompleter,
)
from life_verify.v1b.sources import (  # noqa: E402
    is_source,
    source_ids_override,
)
import life_verify.v1b.sources as sources_mod  # noqa: E402

OUT = ROOT / "runs/life_long_chain"
# Prefer live schedule if present; else the published frozen copy.
_SCHED_CANDIDATES = (
    ROOT / "runs/life_reasoning_cells/seed_schedule.json",
    ROOT / "artifacts/life_reasoning_cells/seed_schedule.json",
)
COST_CAP_USD = 40.0
ONE_SOURCE = (0,)
ZERO_SOURCES: tuple[int, ...] = ()

ARM_SPEC = {
    "B0": {
        "mode": "responses", "sparse": True, "k": 0, "effort": "medium",
        "channel": True, "parent_arm": "Bs", "cache_arm": "B0",
        "source_ids": ZERO_SOURCES, "expected_n_sources": 0,
        "amendment": "AMENDMENT_LONG_CHAIN_B0.md",
    },
    "B1": {
        "mode": "responses", "sparse": True, "k": 0, "effort": "medium",
        "channel": True, "parent_arm": "B", "cache_arm": "B1",
        "source_ids": ONE_SOURCE, "expected_n_sources": 1,
    },
    "Ca1": {
        "mode": "decisions", "sparse": True, "k": 0, "effort": None,
        "channel": True, "decode": "argmax", "parent_arm": "Ca", "cache_arm": "Ca1",
        "source_ids": ONE_SOURCE, "expected_n_sources": 1,
    },
    "Da1": {
        "mode": "decisions", "sparse": True, "k": 1, "effort": None,
        "channel": True, "decode": "argmax", "parent_arm": "Da", "cache_arm": "Da1",
        "source_ids": ONE_SOURCE, "expected_n_sources": 1,
    },
}


def _schedule_path() -> Path:
    for p in _SCHED_CANDIDATES:
        if p.is_file():
            return p
    raise FileNotFoundError(
        "seed_schedule.json not found under runs/ or artifacts/life_reasoning_cells/"
    )


def _usd_from_usage_dict(u: dict | None) -> float:
    """List-rate USD from Responses or Decisions completer.usage() shapes."""
    u = u or {}
    if u.get("usd_list_rate") is not None:
        return float(u["usd_list_rate"])
    inp = int(u.get("input_tokens") or u.get("prompt_tokens") or 0)
    out = int(u.get("output_tokens") or 0)
    if inp == 0 and out == 0:
        return 0.0
    return float(
        usd_from_usage(
            {
                "input_tokens": inp,
                "output_tokens": out,
                "input_tokens_details": {
                    "cached_tokens": int(u.get("cached_tokens") or 0),
                    "cache_write_tokens": int(u.get("cache_write_tokens") or 0),
                },
            }
        )
    )


def _usd_from_completer(completer) -> float:
    u = completer.usage() if hasattr(completer, "usage") else {}
    return _usd_from_usage_dict(u)


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
    return LunaDecisionsCompleter(
        client, P=4, max_workers=max_workers, decode=spec.get("decode") or "argmax"
    )


def run_one(arm: str, world_seed: int, *, max_workers: int, n_gens: int) -> dict:
    spec = ARM_SPEC[arm]
    source_ids = tuple(spec.get("source_ids") or ())
    expected_n = int(spec.get("expected_n_sources", len(source_ids)))
    save = OUT / arm / f"seed{world_seed}"
    save.mkdir(parents=True, exist_ok=True)
    report_path = save / "report.json"
    if report_path.is_file():
        prev = json.loads(report_path.read_text())
        if prev.get("complete"):
            print(json.dumps({"skip": True, "arm": arm, "seed": world_seed}), flush=True)
            return prev

    cache = OUT / f"cache_{spec['cache_arm']}"
    completer = _make_completer(arm, max_workers=max_workers, cache_dir=cache)
    with source_ids_override(source_ids):
        assert sources_mod.SOURCE_IDS == source_ids
        sim = SimulationV1b(
            world_seed=world_seed,
            substrate="local",
            sparse=spec["sparse"],
            channel=True,
            k=spec["k"],
            seeded=True,
            allow_sparse_seeded=True,
            completer=completer,
            policy_label=f"life-long-chain-{arm}",
        )
        pe0 = sim.fn.description()
        n_ops0 = int(sim.fn.n_ops)
        if n_ops0 != 2:
            raise RuntimeError(f"expected 2-op seed, got n_ops={n_ops0} pe={pe0}")

        t0 = time.time()
        for g in range(n_gens):
            sim.step()
            row = sim.rule_history[-1]
            rules = {int(k): v for k, v in row["rules"].items()}
            for cid in range(N_CELLS):
                if is_source(cid, seeded=True):
                    continue
                if rules.get(cid) is None:
                    raise RuntimeError(
                        f"arm={arm} seed={world_seed} gen={row.get('generation')}: "
                        f"non-source {cid} inferred_rule=None"
                    )
            mask = row.get("source_mask") or {}
            n_src = sum(
                1 for cid in range(N_CELLS) if mask.get(str(cid), mask.get(cid))
            )
            if n_src != expected_n:
                raise RuntimeError(
                    f"arm={arm}: expected {expected_n} sources, got {n_src}"
                )
            print(json.dumps({
                "arm": arm, "seed": world_seed, "gen": g + 1, "n_gens": n_gens,
                "p_e": pe0, "n_ops": n_ops0, "n_sources": n_src,
                "elapsed_s": round(time.time() - t0, 1),
            }), flush=True)

        bundle = metrics_bundle(sim.rule_history)
        usage = completer.usage() if hasattr(completer, "usage") else {}
        usd = _usd_from_completer(completer)
        report = {
            "arm": arm,
            "task": (
                "AMENDMENT_LONG_CHAIN_B0.md"
                if arm == "B0"
                else "TASK_LIFE_LONG_CHAIN.md"
            ),
            "world_seed": world_seed,
            "p_e": pe0,
            "n_ops": n_ops0,
            "spec": {**spec, "source_ids": list(source_ids)},
            "n_gens": n_gens,
            "n_sources": expected_n,
            "elapsed_s": time.time() - t0,
            "metrics": bundle,
            "usage": usage,
            "usd_list_rate": usd,
            "complete": True,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        (save / "rule_history.json").write_text(json.dumps(sim.rule_history) + "\n")
        report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "done": {
            "arm": arm, "world_seed": world_seed, "j": bundle.get("j"),
            "usd_list_rate": usd, "elapsed_s": report["elapsed_s"],
        }
    }, default=float), flush=True)
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="B1,Ca1,Da1")
    ap.add_argument("--max-workers", type=int, default=16)
    ap.add_argument("--n-gens", type=int, default=EPOCH_LENGTH)
    ap.add_argument("--cost-cap", type=float, default=COST_CAP_USD)
    ap.add_argument(
        "--seeds", default="",
        help="default = 2-op seeds from parent schedule (1–5)",
    )
    args = ap.parse_args()
    sched = json.loads(_schedule_path().read_text())
    if args.seeds.strip():
        seeds = [int(x) for x in args.seeds.split(",") if x.strip()]
    else:
        seeds = [int(s["world_seed"]) for s in sched["seeds"] if int(s["n_ops"]) == 2]

    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    for a in arms:
        if a not in ARM_SPEC:
            raise SystemExit(f"unknown arm {a}; known={sorted(ARM_SPEC)}")

    OUT.mkdir(parents=True, exist_ok=True)
    print(json.dumps({
        "start": datetime.now(timezone.utc).isoformat(),
        "task": "TASK_LIFE_LONG_CHAIN.md",
        "amendment_b0": "AMENDMENT_LONG_CHAIN_B0.md" if "B0" in arms else None,
        "arms": arms, "seeds": seeds, "n_gens": args.n_gens,
        "source_ids_by_arm": {
            a: list(ARM_SPEC[a].get("source_ids") or ()) for a in arms
        },
        "cost_cap_usd": args.cost_cap,
    }), flush=True)

    spent = 0.0
    rows = []
    for arm in arms:
        for seed in seeds:
            if spent >= args.cost_cap:
                print(json.dumps({
                    "stop": "cost_cap", "spent_usd": spent, "cap": args.cost_cap,
                }), flush=True)
                break
            r = run_one(arm, seed, max_workers=args.max_workers, n_gens=args.n_gens)
            rows.append(r)
            spent += float(r.get("usd_list_rate") or 0.0)
            print(json.dumps({"spent_usd": round(spent, 4), "cap": args.cost_cap}), flush=True)
        else:
            continue
        break

    summary = {
        "task": "TASK_LIFE_LONG_CHAIN.md",
        "amendment_b0": "AMENDMENT_LONG_CHAIN_B0.md" if "B0" in arms else None,
        "source_ids_by_arm": {
            a: list(ARM_SPEC[a].get("source_ids") or ()) for a in arms
        },
        "arms": arms,
        "seeds": seeds,
        "n_gens": args.n_gens,
        "spent_usd": spent,
        "cost_cap_usd": args.cost_cap,
        "rows": [
            {
                "arm": r["arm"], "world_seed": r["world_seed"], "p_e": r["p_e"],
                "n_ops": r["n_ops"], "j": (r.get("metrics") or {}).get("j"),
                "usd_list_rate": r.get("usd_list_rate"),
                "elapsed_s": r.get("elapsed_s"),
                "complete": r.get("complete"),
            }
            for r in rows
        ],
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (OUT / "summary_partial.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({
        "wrote": str(OUT / "summary_partial.json"),
        "n_rows": len(rows),
        "spent_usd": spent,
    }), flush=True)


if __name__ == "__main__":
    main()

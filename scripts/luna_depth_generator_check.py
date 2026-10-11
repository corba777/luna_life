#!/usr/bin/env python3
"""No-model generator check for TASK_LUNA_DEPTH — before any API call.

  PYTHONPATH=.:. \\
    python scripts/luna_depth_generator_check.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT)]

from life_verify import luna_depth as D  # noqa: E402

OUT = ROOT / "artifacts/openai_decisions/luna_depth_generator_check.json"
PAIRS_OUT = ROOT / "artifacts/openai_decisions/luna_depth_pairs.json"


def main() -> int:
    report = D.generator_check(seed=D.DEPTH_SEED)
    D.dump_pairs_json(PAIRS_OUT, seed=D.DEPTH_SEED)
    report["pairs_dump"] = str(PAIRS_OUT.relative_to(ROOT))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "ok": report["ok"],
        "n_syntactic_3op": report["n_syntactic_3op"],
        "n_eq_leq2_or_identity": report["n_eq_leq2_or_identity"],
        "n_unique_3op_pool": report["n_unique_3op_pool"],
        "n_held_out": report["n_held_out"],
        "n_pairs": report["n_pairs"],
        "wrote": str(OUT),
        "pairs_dump": report["pairs_dump"],
        "held_out_head": report["held_out_descriptions"][:5],
    }, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

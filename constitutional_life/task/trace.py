"""Walk one cell's observation the way the enumerator does."""

from __future__ import annotations

from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog
from constitutional_life.task.dsl import is_valid_seq
from constitutional_life.task.identify import Example, hypothesis_set, observational_enumerator

DEMO_INPUTS = ("ABCD", "FACE", "HHHH", "ACEG")
H_LIST_CAP = 16


def apply_steps(fn: CanonicalFunction, seq: str) -> list[dict]:
    cur = seq
    steps: list[dict] = []
    for op in fn.canonical.ops:
        nxt = op.apply(cur)
        steps.append({"op": op.description(), "before": cur, "after": nxt})
        cur = nxt
    return steps


def hypothesis_path(
    examples: list[Example],
    catalog: FunctionCatalog,
) -> list[dict]:
    path = [{"n": 0, "x": None, "y": None, "n_h": len(catalog), "H": [], "more": 0}]
    for i in range(len(examples)):
        prefix = examples[: i + 1]
        hyps = hypothesis_set(prefix, catalog)
        names = [h.description() for h in hyps]
        x, y = examples[i]
        path.append(
            {
                "n": i + 1,
                "x": x,
                "y": y,
                "n_h": len(hyps),
                "H": names[:H_LIST_CAP],
                "more": max(0, len(hyps) - H_LIST_CAP),
            }
        )
    return path


def cell_trace(
    fn: CanonicalFunction,
    examples: list[Example],
    query: str,
    catalog: FunctionCatalog,
) -> dict:
    demo = query if is_valid_seq(query) else "ABCD"
    obs = (
        observational_enumerator(examples, query, catalog)
        if is_valid_seq(query)
        else None
    )
    return {
        "ops": [op.description() for op in fn.canonical.ops],
        "apply": apply_steps(fn, demo),
        "path": hypothesis_path(examples, catalog),
        "privileged": fn.apply(demo),
        "observational": obs,
        "query_used": demo,
    }


def world_demos(fn: CanonicalFunction) -> list[dict]:
    return [
        {"input": seq, "steps": apply_steps(fn, seq), "output": fn.apply(seq)}
        for seq in DEMO_INPUTS
    ]

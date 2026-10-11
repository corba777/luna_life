"""Level check for a Jev backend before the sweep. Not τ, not Δ.

For every canonical function, draw an identifying example set (the engine's
sampler, n = N_EXAMPLES) and a query, then ask the cell in these arms:

    solo                 no channel; canonical and reversed option order
    empty                channel, empty inbox
    true                 one neighbour naming P_e
    false                one neighbour naming a rule ruled out by E
    pub_after_ok         empty inbox; memory says previous answer was correct
    pub_after_bad        empty inbox; memory says previous answer was wrong
    mixed_1true_7false   1× P_e + 7× same false name (majority = false)
    mixed_1false_7true   1× false + 7× P_e (majority = true)

Primary recognition contrast (same quantity both sides):

    Δ_named = P(mass on named | true) − P(mass on named | false)

If that gap is near zero, top-1 = 1 under `true` is obedience, not recognition.
`false` against `empty` separates checking from believing. Mixed inboxes ask
whether majority, singleton, or truth wins. Publication arms ask whether the
board gets a truth filter from selective publishing.

    python -m constitutional_life.probe --backend typesafe --arms true false
    python -m constitutional_life.probe --backend typesafe --arms pub_after_ok pub_after_bad mixed_1true_7false mixed_1false_7true
"""

from __future__ import annotations

import argparse
import json
import random
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from constitutional_life.board.board import Message
from constitutional_life.cell.memory import remember
from constitutional_life.cell.observation import CellObservation, make_observation
from constitutional_life.model.client import InferenceError
from constitutional_life.model.factory import describe
from constitutional_life.model.jev import JevCompleter, OrderMode
from constitutional_life.model.seeding import option_order_seed
from constitutional_life.run import add_backend_args, completer_from_args
from constitutional_life.task.catalog import CanonicalFunction, build_catalog
from constitutional_life.task.dsl import N_INPUTS, decode_seq
from constitutional_life.task.identify import (
    hypothesis_set,
    sample_identifying_examples,
)
from constitutional_life.v1a_constants import EPOCH_LENGTH, GRID, N_EXAMPLES, READ_BUDGET

ARMS = (
    "solo",
    "empty",
    "true",
    "false",
    "pub_after_ok",
    "pub_after_bad",
    "mixed_1true_7false",
    "mixed_1false_7true",
)
PAIRS_PER_CELL = {
    "solo": 101,
    # channel: rule 101 + communication 2 + signal 8 = 111 (say bound to rule, no pairs)
    "empty": 111,
    "true": 111,
    "false": 111,
    "pub_after_ok": 111,
    "pub_after_bad": 111,
    "mixed_1true_7false": 111,
    "mixed_1false_7true": 111,
}
CELL_ID = 0
SENDER_ID = 1  # Moore neighbour of cell 0; singleton sender in mixed arms
MAX_IDENTIFYING_BATCHES = 1000
NAMED_ARMS = ("true", "false", "mixed_1true_7false", "mixed_1false_7true")


@dataclass(frozen=True, slots=True)
class Item:
    fn: CanonicalFunction
    draw: int
    examples: list
    query: str
    false_rule: CanonicalFunction


def make_items(seed: int, per_function: int, limit: int | None) -> tuple[list[Item], int]:
    """Build probe items. Returns (items, pe_reject_batches)."""
    catalog = build_catalog()
    fns = list(catalog.functions)[:limit] if limit else list(catalog.functions)
    items = []
    pe_rejects = 0
    for fn in fns:
        for draw in range(per_function):
            examples = None
            for batch in range(MAX_IDENTIFYING_BATCHES):
                rng = random.Random(repr((seed, "probe", fn.program_id, draw, batch)))
                examples, _ = sample_identifying_examples(fn, N_EXAMPLES, catalog, rng)
                if examples is not None:
                    break
                pe_rejects += 1
            if examples is None:
                raise RuntimeError(
                    f"could not identify {fn.description()!r} after "
                    f"{MAX_IDENTIFYING_BATCHES} × 100 E draws"
                )
            rng = random.Random(repr((seed, "probe", fn.program_id, draw, "query")))
            query = decode_seq(rng.randrange(N_INPUTS))
            consistent = {g.program_id for g in hypothesis_set(examples, catalog)}
            ruled_out = [g for g in catalog.functions if g.program_id not in consistent]
            if not ruled_out:
                raise RuntimeError(f"no rules ruled out by E for {fn.description()!r}")
            false_rule = rng.choice(ruled_out)
            items.append(Item(fn, draw, examples, query, false_rule))
    return items, pe_rejects


def _memory(previous_correct: bool | None):
    if previous_correct is None:
        return None
    # Answer text is just scaffolding so the memory line is non-empty.
    return remember(
        task_answer="AAAA",
        correct=previous_correct,
        published=False,
        signal=None,
        say=None,
    )


def _mixed_inbox(item: Item, *, majority_is_true: bool) -> list[Message]:
    """READ_BUDGET messages: one singleton + (READ_BUDGET-1) copies of the other name."""
    assert READ_BUDGET == 8
    true_say = item.fn.description()
    false_say = item.false_rule.description()
    if majority_is_true:
        singleton_say, majority_say = false_say, true_say
    else:
        singleton_say, majority_say = true_say, false_say
    # Singleton first (sender 1); majority fill senders 2..8. Order is part of the arm.
    msgs = [Message(sender_id=SENDER_ID, generation=0, signal=0, say=singleton_say)]
    for i, sid in enumerate(range(2, READ_BUDGET + 1), start=1):
        msgs.append(Message(sender_id=sid, generation=0, signal=i % 8, say=majority_say))
    return msgs


def observation(item: Item, arm: str) -> CellObservation:
    if arm == "solo":
        return make_observation(
            cell_id=CELL_ID, generation=0, epoch=0, epoch_length=EPOCH_LENGTH,
            examples=item.examples, query=item.query,
        )
    delivered: list[Message] = []
    memory = None
    if arm == "true":
        delivered = [Message(sender_id=SENDER_ID, generation=0, signal=0, say=item.fn.description())]
    elif arm == "false":
        delivered = [
            Message(sender_id=SENDER_ID, generation=0, signal=0, say=item.false_rule.description())
        ]
    elif arm == "pub_after_ok":
        memory = _memory(True)
    elif arm == "pub_after_bad":
        memory = _memory(False)
    elif arm == "mixed_1true_7false":
        delivered = _mixed_inbox(item, majority_is_true=False)
    elif arm == "mixed_1false_7true":
        delivered = _mixed_inbox(item, majority_is_true=True)
    # empty / pub_*: delivered stays []
    return make_observation(
        cell_id=CELL_ID, generation=1, epoch=0, epoch_length=EPOCH_LENGTH,
        examples=item.examples, query=item.query, delivered=delivered, memory=memory,
    )


def order_seeds_for(items: list[Item], seed: int, arm: str) -> list[int]:
    generation = 0 if arm == "solo" else 1
    return [
        option_order_seed(seed, generation, CELL_ID, draw=i)
        for i, _ in enumerate(items)
    ]


def _mass_on(rule: dict, fn_of: dict, program_id: str) -> float:
    return sum(p for k, p in rule.items() if fn_of[k].program_id == program_id)


def score(completer: JevCompleter, item: Item, arm: str, answers: dict) -> dict:
    rule = answers["rule"]
    expected = item.fn.apply(item.query)
    fn_of = completer.options
    top = max(rule, key=rule.get)
    top_fn = fn_of[top]
    row = {
        "program_id": item.fn.program_id,
        "p_e": item.fn.description(),
        "n_ops": item.fn.n_ops,
        "draw": item.draw,
        "p_rule": _mass_on(rule, fn_of, item.fn.program_id),
        "p_answer": sum(p for k, p in rule.items() if fn_of[k].apply(item.query) == expected),
        "argmax_correct": top_fn.program_id == item.fn.program_id,
        "chance_answer": sum(1 for f in fn_of.values() if f.apply(item.query) == expected) / len(fn_of),
    }
    # Named-rule mass: same definition for true and false (and mixed).
    if arm == "true":
        named = item.fn
    elif arm == "false":
        named = item.false_rule
        row["false_rule"] = named.description()
    else:
        named = None
    if named is not None:
        row["p_named"] = _mass_on(rule, fn_of, named.program_id)
        row["argmax_named"] = top_fn.program_id == named.program_id
        # Back-compat alias used in earlier reports.
        if arm == "false":
            row["p_follow_false"] = row["p_named"]

    if arm in ("mixed_1true_7false", "mixed_1false_7true"):
        row["false_rule"] = item.false_rule.description()
        row["p_named_true"] = _mass_on(rule, fn_of, item.fn.program_id)
        row["p_named_false"] = _mass_on(rule, fn_of, item.false_rule.program_id)
        row["argmax_true"] = top_fn.program_id == item.fn.program_id
        row["argmax_false"] = top_fn.program_id == item.false_rule.program_id
        majority_id = (
            item.fn.program_id if arm == "mixed_1false_7true" else item.false_rule.program_id
        )
        singleton_id = (
            item.false_rule.program_id if arm == "mixed_1false_7true" else item.fn.program_id
        )
        row["p_majority"] = _mass_on(rule, fn_of, majority_id)
        row["p_singleton"] = _mass_on(rule, fn_of, singleton_id)
        row["argmax_majority"] = top_fn.program_id == majority_id
        row["argmax_singleton"] = top_fn.program_id == singleton_id

    if "communication" in answers:
        row["p_publish"] = answers["communication"]["publish"]
    return row


def summarise(rows: list[dict]) -> dict:
    def mean(key: str, subset: list[dict] = rows) -> float | None:
        vals = [float(r[key]) for r in subset if key in r]
        return sum(vals) / len(vals) if vals else None

    keys = (
        "p_rule",
        "p_answer",
        "argmax_correct",
        "chance_answer",
        "p_named",
        "argmax_named",
        "p_follow_false",
        "p_publish",
        "p_named_true",
        "p_named_false",
        "p_majority",
        "p_singleton",
        "argmax_true",
        "argmax_false",
        "argmax_majority",
        "argmax_singleton",
    )
    out: dict = {"n": len(rows)}
    for key in keys:
        value = mean(key)
        if value is not None:
            out[key] = value
    by_ops = defaultdict(list)
    for r in rows:
        by_ops[r["n_ops"]].append(r)
    out["by_n_ops"] = {
        str(k): {
            "n": len(v),
            "p_rule": mean("p_rule", v),
            "argmax_correct": mean("argmax_correct", v),
            **({
                "p_named": mean("p_named", v),
                "argmax_named": mean("argmax_named", v),
            } if mean("p_named", v) is not None else {}),
        }
        for k, v in sorted(by_ops.items())
    }
    return out


def _run_arm(
    completer: JevCompleter,
    items: list[Item],
    arm: str,
    *,
    seed: int,
    order_mode: OrderMode,
) -> tuple[list[dict], dict]:
    obs = [observation(item, arm) for item in items]
    seeds = order_seeds_for(items, seed, arm)
    usage_before = completer.usage()
    started = time.perf_counter()
    answers = completer.distributions(
        obs,
        channel=arm != "solo",
        order_seeds=seeds,
        order_mode=order_mode,
    )
    elapsed = time.perf_counter() - started
    usage_after = completer.usage()
    rows = [score(completer, item, arm, ans) for item, ans in zip(items, answers, strict=True)]
    summary = summarise(rows)
    summary["elapsed_s"] = elapsed
    summary["order_mode"] = order_mode
    summary["usage"] = {k: v - usage_before.get(k, 0) for k, v in usage_after.items()}
    return rows, summary


def _solo_order_sensitivity(canon_rows: list[dict], rev_rows: list[dict]) -> dict:
    l1s = [abs(a["p_rule"] - b["p_rule"]) for a, b in zip(canon_rows, rev_rows, strict=True)]
    return {
        "n": len(l1s),
        "mean_abs_d_p_rule": sum(l1s) / len(l1s) if l1s else None,
        "max_abs_d_p_rule": max(l1s) if l1s else None,
        "frac_argmax_disagree": (
            sum(
                1
                for a, b in zip(canon_rows, rev_rows, strict=True)
                if a["argmax_correct"] != b["argmax_correct"]
            )
            / len(canon_rows)
            if canon_rows
            else None
        ),
    }


def _named_contrast(true_rows: list[dict], false_rows: list[dict]) -> dict:
    """Δ_named = P(choose named | true msg) − P(choose named | false msg)."""
    p_true = [r["p_named"] for r in true_rows]
    p_false = [r["p_named"] for r in false_rows]
    a_true = [float(r["argmax_named"]) for r in true_rows]
    a_false = [float(r["argmax_named"]) for r in false_rows]
    return {
        "n": len(true_rows),
        "p_named_true": sum(p_true) / len(p_true),
        "p_named_false": sum(p_false) / len(p_false),
        "delta_named": sum(p_true) / len(p_true) - sum(p_false) / len(p_false),
        "argmax_named_true": sum(a_true) / len(a_true),
        "argmax_named_false": sum(a_false) / len(a_false),
        "delta_argmax_named": sum(a_true) / len(a_true) - sum(a_false) / len(a_false),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_backend_args(parser)
    parser.add_argument("--arms", nargs="+", choices=ARMS, default=list(ARMS))
    parser.add_argument("--per-function", type=int, default=1)
    parser.add_argument("--limit", type=int, default=None, help="first N functions only (plumbing)")
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--out", type=Path, default=None, help="default artifacts/g<GRID>/probe-<backend>")
    args = parser.parse_args(argv)
    if args.backend == "llm":
        parser.error("the probe reads exact distributions; it needs a Jev backend")
    out_dir = args.out if args.out is not None else Path("artifacts") / f"g{GRID}" / f"probe-{args.backend}"
    completer, label = completer_from_args(args)
    assert isinstance(completer, JevCompleter)
    items, pe_rejects = make_items(args.seed, args.per_function, args.limit)
    pairs = 0
    for a in args.arms:
        pairs += PAIRS_PER_CELL[a] * len(items) * (2 if a == "solo" else 1)
    print(f"{len(items)} items × arms {' '.join(args.arms)}, ~{pairs} premise–hypothesis pairs, backend {label}")
    if pe_rejects:
        print(f"P_e / identifying-E reject batches: {pe_rejects}")

    report: dict = {
        "policy": label,
        **describe(completer),
        "communication_type": completer.communication_type,
        "seed": args.seed,
        "n_examples": N_EXAMPLES,
        "p_e_rejects": pe_rejects,
        "arms": {},
    }
    rows_out: list[dict] = []
    solo_canon_rows: list[dict] | None = None
    solo_rev_rows: list[dict] | None = None
    true_rows: list[dict] | None = None
    false_rows: list[dict] | None = None

    for arm in args.arms:
        if arm == "solo":
            for mode in ("canonical", "reversed"):
                try:
                    rows, summary = _run_arm(
                        completer, items, arm, seed=args.seed, order_mode=mode  # type: ignore[arg-type]
                    )
                except InferenceError as exc:
                    print(exc)
                    return 1
                key = f"solo_{mode}"
                report["arms"][key] = summary
                rows_out.extend({"arm": key, **r} for r in rows)
                if mode == "canonical":
                    solo_canon_rows = rows
                else:
                    solo_rev_rows = rows
                _print_arm(key, summary)
            continue
        try:
            rows, summary = _run_arm(
                completer, items, arm, seed=args.seed, order_mode="shuffle"
            )
        except InferenceError as exc:
            print(exc)
            return 1
        report["arms"][arm] = summary
        rows_out.extend({"arm": arm, **r} for r in rows)
        if arm == "true":
            true_rows = rows
        if arm == "false":
            false_rows = rows
        _print_arm(arm, summary)

    if true_rows is not None and false_rows is not None:
        report["named_contrast"] = _named_contrast(true_rows, false_rows)
        c = report["named_contrast"]
        print(
            f"Δ_named  P(named|true)−P(named|false) = {c['delta_named']:.4f}  "
            f"({c['p_named_true']:.3f} − {c['p_named_false']:.3f});  "
            f"Δ argmax_named = {c['delta_argmax_named']:.4f}  "
            f"({c['argmax_named_true']:.3f} − {c['argmax_named_false']:.3f})",
            flush=True,
        )

    if solo_canon_rows is not None and solo_rev_rows is not None:
        report["solo_order_sensitivity"] = _solo_order_sensitivity(solo_canon_rows, solo_rev_rows)
        s = report["solo_order_sensitivity"]
        print(
            f"solo order sensitivity  mean|ΔP(rule)| {s['mean_abs_d_p_rule']:.4f}  "
            f"max {s['max_abs_d_p_rule']:.4f}  argmax disagree {s['frac_argmax_disagree']:.3f}"
        )

    try:
        probe_arm = "empty" if any(a != "solo" for a in args.arms) else "solo"
        report["order_sensitivity"] = completer.measure_order_sensitivity(
            observation(items[0], probe_arm),
            channel=any(a != "solo" for a in args.arms),
        )
        osens = report["order_sensitivity"]
        print(
            f"order_sensitivity max_l1={osens.get('max_l1')} "
            f"communication_type={osens.get('communication_type')}"
        )
    except InferenceError as exc:
        print(f"order_sensitivity skipped: {exc}")

    report["chance_rule"] = 1 / len(completer.options)
    reported = getattr(completer.backend, "model_reported", None)
    if reported:
        report["model_reported"] = reported
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "probe.json").write_text(json.dumps(report, indent=2) + "\n")
    with (out_dir / "probe_rows.jsonl").open("w") as fh:
        for row in rows_out:
            fh.write(json.dumps(row) + "\n")
    print(f"chance P(rule) {report['chance_rule']:.3f}. files under {out_dir}")
    return 0


def _print_arm(name: str, summary: dict) -> None:
    if "p_publish" in summary and name.startswith("pub_"):
        line = f"{name:22}  P(publish) {summary['p_publish']:.3f}"
    elif "p_majority" in summary:
        line = (
            f"{name:22}  P(true) {summary.get('p_named_true', float('nan')):.3f}  "
            f"P(false) {summary.get('p_named_false', float('nan')):.3f}  "
            f"P(majority) {summary['p_majority']:.3f}  "
            f"argmax maj {summary.get('argmax_majority', float('nan')):.3f}  "
            f"argmax true {summary.get('argmax_true', float('nan')):.3f}"
        )
    else:
        line = (
            f"{name:22}  P(rule) {summary['p_rule']:.3f}  top-1 {summary['argmax_correct']:.3f}  "
            f"P(answer) {summary['p_answer']:.3f} (chance {summary['chance_answer']:.3f})"
        )
        if "p_named" in summary:
            line += f"  P(named) {summary['p_named']:.3f}  argmax_named {summary.get('argmax_named', float('nan')):.3f}"
        if "p_publish" in summary and not name.startswith("pub_"):
            line += f"  P(publish) {summary['p_publish']:.3f}"
    ops = "  ".join(
        f"{k}-op top-1 {v['argmax_correct']:.3f}" for k, v in summary.get("by_n_ops", {}).items()
    )
    u = summary.get("usage") or {}
    cache = f"  cached {u['cached_tokens']}/{u['prompt_tokens']} tok" if u.get("prompt_tokens") else ""
    extra = f"  [{ops}]" if ops else ""
    print(f"{line}{extra}  {summary['elapsed_s']:.0f}s{cache}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())

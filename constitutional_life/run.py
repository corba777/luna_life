"""One seed against a cell backend (openjev, typesafe, or llm).

    python -m constitutional_life.run --check
    python -m constitutional_life.run --backend openjev --seed 1 --substrate local --generations 1
    python -m constitutional_life.run --backend typesafe --check
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from constitutional_life.cell.observation import inboxes_to_json
from constitutional_life.model.client import InferenceError, SglangClient
from constitutional_life.model.factory import BACKENDS, Backend, describe, make_completer
from constitutional_life.model.types import Completer
from constitutional_life.sim.agreement import agreement_to_dict, summarise_agreement
from constitutional_life.sim.engine import Simulation
from constitutional_life.sim.replay import save_snapshot
from constitutional_life.v1a_constants import BACKEND, EPOCH_LENGTH, GRID


def check_server(client: SglangClient) -> int:
    try:
        models = client.list_models()
    except InferenceError as exc:
        print(f"SGLang not reachable at {client.base_url}")
        print(exc)
        return 1
    print(f"SGLang {client.base_url}")
    if not models:
        print("no models listed")
        return 1
    for name in models:
        mark = "*" if name == client.model else " "
        print(f" {mark} {name}")
    if client.model not in models:
        print(f"configured model {client.model!r} is not in /v1/models; passing it anyway")
    return 0


def check_completer(completer: Completer) -> int:
    if isinstance(completer, SglangClient):
        return check_server(completer)
    try:
        print(completer.check())  # type: ignore[attr-defined]
    except InferenceError as exc:
        print(exc)
        return 1
    backend = getattr(completer, "backend", None)
    order_check = getattr(backend, "check_option_order", None)
    if callable(order_check):
        try:
            report = order_check()
        except InferenceError as exc:
            print(exc)
            return 1
        print(
            f"option-order max L1 = {report['max_l1']:.6g} "
            f"(model_reported={report.get('model_reported')!r})"
        )
        for q in report["questions"]:
            print(f"  {q['question']}: n={q['n_options']} max_l1={q['max_l1']:.6g}")
        out = Path("artifacts") / f"g{GRID}" / "typesafe-option-order.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n")
        print(f"wrote {out}")
    return 0


def execute_run(
    *,
    completer: Completer,
    world_seed: int,
    substrate: str,
    channel: bool,
    generations: int,
    sparse: bool,
    policy_label: str,
    inbox_override: dict | None = None,
    save_dir: Path | None = None,
    skip_order_check: bool = False,
) -> dict:
    pop_records = getattr(completer, "pop_records", None)
    if callable(pop_records):
        pop_records()
    sim = Simulation(
        world_seed=world_seed,
        substrate=substrate,  # type: ignore[arg-type]
        sparse=sparse,
        channel=channel,
        completer=completer,
        policy_label=policy_label,
        inbox_override=inbox_override,
    )
    usage_before = _usage(completer)
    started = time.perf_counter()
    parse_ok = 0
    cells = 0
    last = sim.snapshot()
    order_sensitivity = None
    measure = getattr(completer, "measure_order_sensitivity", None)
    if callable(measure) and generations > 0 and not skip_order_check:
        # One fixed observation from generation 0; costs two inference calls.
        from constitutional_life.cell.observation import make_observation
        from constitutional_life.task.dsl import N_INPUTS, decode_seq

        cid0 = 0
        probe_obs = make_observation(
            cell_id=cid0,
            generation=0,
            epoch=0,
            epoch_length=EPOCH_LENGTH,
            examples=sim.examples[cid0],
            query=decode_seq(0) if N_INPUTS else "AAAA",
            delivered=[],
            memory=sim.memories[cid0],
        )
        try:
            order_sensitivity = measure(probe_obs, channel=channel)
            print(
                f"  order_sensitivity max_l1={order_sensitivity.get('max_l1')} "
                f"communication_type={order_sensitivity.get('communication_type')}",
                flush=True,
            )
        except InferenceError as exc:
            print(f"  order_sensitivity failed: {exc}", flush=True)
    for i in range(generations):
        last = sim.step()
        this_parse = sum(1 for cell in last.cells if cell.parse_valid)
        parse_ok += this_parse
        cells += len(last.cells)
        print(
            f"  gen {i + 1}/{generations}  "
            f"valid {this_parse}/{len(last.cells)}  "
            f"correct {last.correct_this_gen}  "
            f"{time.perf_counter() - started:.0f}s",
            flush=True,
        )
    elapsed = time.perf_counter() - started
    correct = round(last.j_running * cells) if cells else 0
    report = {
        "policy": policy_label,
        **describe(completer),
        "world_seed": world_seed,
        "substrate": substrate,
        "channel": channel,
        "sparse": sparse,
        "generations": generations,
        "n_cells": len(last.cells),
        "elapsed_s": elapsed,
        "calls": cells,
        "correct": correct,
        "score": last.j_running,
        "parse_rate": parse_ok / cells if cells else None,
        "correct_last_gen": last.correct_this_gen,
        "published_last_gen": last.published_this_gen,
        "replay_snapshots": len(sim.replay_snapshots),
        "p_e_rejects": sim.p_e_rejects,
        "j_history": list(sim.j_history),
        "agreement": summarise_agreement(sim.agreement_history),
        "agreement_by_gen": [agreement_to_dict(r) for r in sim.agreement_history],
    }
    if order_sensitivity is not None:
        report["order_sensitivity"] = order_sensitivity
    if hasattr(completer, "communication_type"):
        report["communication_type"] = completer.communication_type  # type: ignore[attr-defined]
    usage_after = _usage(completer)
    if usage_after:
        report["usage"] = {k: v - usage_before.get(k, 0) for k, v in usage_after.items()}
    if save_dir is not None:
        save_dir.mkdir(parents=True, exist_ok=True)
        (save_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        (save_dir / "inboxes.json").write_text(
            json.dumps(inboxes_to_json(sim.recorded_inboxes)) + "\n"
        )
        if callable(pop_records):
            with (save_dir / "decisions.jsonl").open("w") as fh:
                for record in pop_records():
                    fh.write(json.dumps(record) + "\n")
        replay_dir = save_dir / "replay"
        for snap in sim.replay_snapshots:
            save_snapshot(snap, replay_dir / f"g{snap.generation}.json")
    return report


def _usage(completer: Completer) -> dict:
    usage = getattr(completer, "usage", None)
    return usage() if callable(usage) else {}


def add_backend_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--backend", choices=BACKENDS, default=BACKEND)
    parser.add_argument("--base-url", default=None, help="default depends on --backend")
    parser.add_argument("--model", default=None, help="default depends on --backend")


def completer_from_args(args: argparse.Namespace) -> tuple[Completer, str]:
    backend: Backend = args.backend
    return make_completer(backend, base_url=args.base_url, model=args.model)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_backend_args(parser)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--substrate",
        choices=("none", "local", "regional", "global"),
        default="local",
    )
    parser.add_argument("--no-channel", action="store_true")
    parser.add_argument("--sparse", action="store_true")
    parser.add_argument("--generations", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=0, help="if set, overrides --generations")
    parser.add_argument("--out", type=Path, default=None, help="directory for report and replay")
    args = parser.parse_args(argv)
    completer, label = completer_from_args(args)
    if args.check:
        return check_completer(completer)
    generations = args.epochs * EPOCH_LENGTH if args.epochs else args.generations
    try:
        report = execute_run(
            completer=completer,
            world_seed=args.seed,
            substrate=args.substrate,
            channel=not args.no_channel,
            generations=generations,
            sparse=args.sparse,
            policy_label=label,
            save_dir=args.out,
        )
    except InferenceError as exc:
        print(exc)
        return 1
    report["s_per_call"] = report["elapsed_s"] / report["calls"] if report["calls"] else None
    for key, value in report.items():
        if key != "j_history":
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

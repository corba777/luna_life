"""Synchronous v1a step with the oracle policy. For the visualizer, not the LLM run."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from constitutional_life.board.board import (
    Board,
    Message,
    Substrate,
    all_cell_ids,
    circulating_rules,
)
from constitutional_life.board.geometry import N_CELLS, coords
from constitutional_life.cell.memory import PrivateCellMemory, empty_memory, remember
from constitutional_life.cell.observation import CellObservation, make_observation
from constitutional_life.cell.schema import parse_decision
from constitutional_life.cell.score import log_from_parse
from constitutional_life.model.seeding import inference_seed
from constitutional_life.model.types import Completer
from constitutional_life.sim.agreement import (
    CellAgree,
    GenerationAgreement,
    agreement_to_dict,
    generation_agreement,
    summarise_agreement,
)
from constitutional_life.sim.policy import (
    StepDecision,
    decide,
    step_from_log,
    step_from_oracle,
)
from constitutional_life.sim.replay import ReplaySnapshot, is_replay_point, make_replay_snapshot
from constitutional_life.task.catalog import CanonicalFunction, FunctionCatalog, build_catalog
from constitutional_life.task.dsl import N_INPUTS, decode_seq, parse_program
from constitutional_life.task.identify import (
    Example,
    hypothesis_set,
    sample_example_set,
    sample_identifying_examples,
    score_answer,
)
from constitutional_life.task.trace import cell_trace, world_demos
from constitutional_life.v1a_constants import EPOCH_LENGTH, GRID, N_EXAMPLES

# Safety cap on P_e resampling within one epoch. FREEZE reject rate at n=2 is ~0.
MAX_P_E_RESAMPLES = 1000

# Four separate sources, pairwise GRID//2 apart. The four corners would be a
# single 2×2 block on the torus.
_HALF = GRID // 2
SPARSE_SOLVER_IDS = (0, _HALF, _HALF * GRID, _HALF * GRID + _HALF)


@dataclass
class CellView:
    cell_id: int
    row: int
    col: int
    correct: bool
    identified: bool
    source: str
    published: bool
    signal: int | None
    say: str | None
    inferred_rule: str | None
    query: str
    answer: str | None
    expected: str
    n_hypotheses: int
    inbox: int
    inbox_says: list[str]
    inbox_true: int
    inbox_false: int
    say_matches_pe: bool | None
    examples: list[Example]
    parse_valid: bool = True


@dataclass
class Snapshot:
    generation: int
    epoch: int
    epoch_generation: int
    p_e: str
    program_id: str
    substrate: Substrate
    sparse: bool
    correct_this_gen: int
    identified: int
    published_this_gen: int
    published_h_gt_1: int
    learned_from_board: int
    learned_true: int
    learned_false: int
    circulating: list[dict]
    rule_origins: list[dict]
    inertia: float
    j_running: float
    j_history: list[float]
    cells: list[CellView]
    policy: str = "observational-enumerator + board parse"


@dataclass
class Simulation:
    world_seed: int
    substrate: Substrate
    sparse: bool
    catalog: FunctionCatalog = field(default_factory=build_catalog)
    board: Board = field(default_factory=Board)
    generation: int = 0
    epoch: int = 0
    fn: CanonicalFunction | None = None
    examples: dict[int, list[Example]] = field(default_factory=dict)
    correct_total: int = 0
    opportunities: int = 0
    j_history: list[float] = field(default_factory=list)
    rule_origins: dict[str, dict] = field(default_factory=dict)
    channel: bool = True
    memories: dict[int, PrivateCellMemory] = field(default_factory=dict)
    replay_snapshots: list[ReplaySnapshot] = field(default_factory=list)
    completer: Completer | None = None
    policy_label: str = "observational-enumerator + board parse"
    inbox_override: dict[int, dict[int, list]] | None = None
    recorded_inboxes: dict[int, dict[int, list]] = field(default_factory=dict)
    p_e_rejects: int = 0  # FREEZE: reject P_e after 100 failed E draws, then resample
    agreement_history: list[GenerationAgreement] = field(default_factory=list)
    say_first_sighting: dict[str, tuple[int, int]] = field(default_factory=dict)
    _cached: Snapshot | None = None

    def __post_init__(self) -> None:
        if not self.memories:
            self.memories = {cid: empty_memory() for cid in all_cell_ids()}
        self._begin_epoch()
        self._cached = self._idle_snapshot()

    def _rng(self, *parts: object) -> random.Random:
        return random.Random(repr((self.world_seed, *parts)))

    def _begin_epoch(self) -> None:
        """Sample P_e; give every solver cell an identifying E. On failure, reject P_e."""
        fns = self.catalog.functions
        for attempt in range(MAX_P_E_RESAMPLES):
            self.fn = fns[self._rng("epoch", self.epoch, attempt).randrange(len(fns))]
            examples: dict[int, list[Example]] = {}
            rejected = False
            for cid in all_cell_ids():
                rng = self._rng("examples", self.epoch, attempt, cid)
                if self.sparse and cid not in SPARSE_SOLVER_IDS:
                    examples[cid] = self._non_identifying_examples(rng)
                    continue
                drawn, _ = sample_identifying_examples(
                    self.fn, N_EXAMPLES, self.catalog, rng
                )
                if drawn is None:
                    rejected = True
                    break
                examples[cid] = drawn
            if not rejected:
                self.examples = examples
                self.say_first_sighting = {}
                return
            self.p_e_rejects += 1
        raise RuntimeError(
            f"epoch {self.epoch}: rejected P_e {MAX_P_E_RESAMPLES} times "
            f"(identifying E failed for every candidate)"
        )

    def _apply_modal(self, description: str, query: str) -> str | None:
        try:
            program = parse_program(description)
        except ValueError:
            return None
        fn = self.catalog.canonicalize(program)
        if fn is None:
            return None
        return fn.apply(query)

    def _note_origins(
        self,
        writes: list[Message],
        decisions: dict[int, StepDecision],
        epoch: int,
        written_at: int,
    ) -> None:
        for msg in writes:
            if msg.say in self.rule_origins:
                continue
            decision = decisions[msg.sender_id]
            self.rule_origins[msg.say] = {
                "say": msg.say,
                "sender_id": msg.sender_id,
                "generation": written_at,
                "epoch": epoch,
                "source": decision.source,
                "n_hypotheses": decision.n_hypotheses,
                "true_at_birth": decision.publish_say == self.fn.description(),
            }

    def _non_identifying_examples(self, rng: random.Random) -> list[Example]:
        assert self.fn is not None
        for _ in range(100):
            examples = sample_example_set(self.fn, 1, rng)
            if len(hypothesis_set(examples, self.catalog)) > 1:
                return examples
        return []

    def step(self) -> Snapshot:
        assert self.fn is not None
        t = self.generation
        decisions: dict[int, StepDecision] = {}
        queries: dict[int, str] = {}
        inboxes: dict[int, list[Message]] = {}
        observations: list[CellObservation] = []
        writes: list[Message] = []
        cell_ids = all_cell_ids()

        for cid in cell_ids:
            query = decode_seq(self._rng("query", t, cid).randrange(N_INPUTS))
            queries[cid] = query
            if self.inbox_override is not None:
                try:
                    slots = list(self.inbox_override[t][cid])
                except KeyError as exc:
                    raise KeyError(
                        f"no donor inbox for generation {t} cell {cid}"
                    ) from exc
                inbox = [msg for msg in slots if msg is not None]
                obs = make_observation(
                    cell_id=cid,
                    generation=t,
                    epoch=self.epoch,
                    epoch_length=EPOCH_LENGTH,
                    examples=self.examples[cid],
                    query=query,
                    inbox=slots,
                    memory=self.memories[cid],
                )
            else:
                inbox = self.board.deliver(cid, t, self.substrate, self.world_seed)
                obs = make_observation(
                    cell_id=cid,
                    generation=t,
                    epoch=self.epoch,
                    epoch_length=EPOCH_LENGTH,
                    examples=self.examples[cid],
                    query=query,
                    delivered=inbox,
                    memory=self.memories[cid],
                )
            inboxes[cid] = inbox
            observations.append(obs)
            self.recorded_inboxes.setdefault(t, {})[cid] = list(obs.inbox)

        if self.completer is None:
            for obs in observations:
                cid = obs.cell_id
                oracle = decide(obs.examples, obs.query, inboxes[cid], self.catalog)
                decisions[cid] = step_from_oracle(oracle)
        else:
            seeds = [
                inference_seed(
                    self.world_seed,
                    t,
                    obs.cell_id,
                    kind="trajectory",
                    draw=0,
                )
                for obs in observations
            ]
            order_seeds = [
                inference_seed(
                    self.world_seed,
                    t,
                    obs.cell_id,
                    kind="order",
                    draw=0,
                )
                for obs in observations
            ]
            raws = self.completer.complete_batch(
                observations,
                channel=self.channel,
                seeds=seeds,
                order_seeds=order_seeds,
            )
            mode = "channel" if self.channel else "no_channel"
            for obs, raw in zip(observations, raws, strict=True):
                cid = obs.cell_id
                n_hyps = len(hypothesis_set(obs.examples, self.catalog))
                parsed = parse_decision(raw, mode=mode)
                log = log_from_parse(parsed, self.fn.apply(queries[cid]), self.fn, self.catalog)
                decisions[cid] = step_from_log(log, n_hyps)

        for cid, decision in decisions.items():
            if decision.publish_say is not None and decision.signal is not None:
                writes.append(
                    Message(
                        sender_id=cid,
                        generation=t,
                        signal=decision.signal,
                        say=decision.publish_say,
                    )
                )

        correct = 0
        for cid, decision in decisions.items():
            expected = self.fn.apply(queries[cid])
            ok = score_answer(decision.answer, expected)
            if ok:
                correct += 1
            published = decision.publish_say is not None and decision.signal is not None
            self.memories[cid] = remember(
                task_answer=decision.answer,
                correct=ok,
                published=published,
                signal=decision.signal,
                say=decision.publish_say,
            )

        if is_replay_point(t + 1):
            self.replay_snapshots.append(
                make_replay_snapshot(
                    world_seed=self.world_seed,
                    generation=t + 1,
                    epoch=self.epoch,
                    substrate=self.substrate,
                    channel=self.channel,
                    fn=self.fn,
                    observations=observations,
                    queries=queries,
                )
            )

        self._note_origins(writes, decisions, epoch=self.epoch, written_at=t)
        publishers = {
            cid: d.publish_say
            for cid, d in decisions.items()
            if d.publish_say is not None
        }
        for cid, say in publishers.items():
            self.say_first_sighting.setdefault(say, (cid, t))
        agree_cells = [
            CellAgree(
                cell_id=cid,
                inferred_rule=decisions[cid].inferred_rule,
                publish_say=decisions[cid].publish_say,
                correct=bool(
                    decisions[cid].answer is not None
                    and decisions[cid].answer == self.fn.apply(queries[cid])
                ),
                expected=self.fn.apply(queries[cid]),
                query=queries[cid],
            )
            for cid in cell_ids
        ]
        self.agreement_history.append(
            generation_agreement(
                agree_cells,
                generation=t + 1,
                epoch=self.epoch,
                p_e=self.fn.description(),
                apply_modal=self._apply_modal,
                publishers=publishers,
                first_sighting=dict(self.say_first_sighting),
                written_at=t,
            )
        )
        self.board.commit(writes)
        self.generation = t + 1
        self.board.expire(self.generation)
        self.correct_total += correct
        self.opportunities += N_CELLS
        self.j_history.append(correct / N_CELLS)
        snap = self._make_snapshot(decisions, queries, inboxes, epoch_at_step=self.epoch)
        if self.generation % EPOCH_LENGTH == 0:
            self.epoch += 1
            self._begin_epoch()
        self._cached = snap
        return snap

    def snapshot(self) -> Snapshot:
        assert self._cached is not None
        return self._cached

    def _idle_snapshot(self) -> Snapshot:
        assert self.fn is not None
        cells = []
        for cid in all_cell_ids():
            row, col = coords(cid)
            cells.append(
                CellView(
                    cell_id=cid,
                    row=row,
                    col=col,
                    correct=False,
                    identified=False,
                    source="unsolved",
                    published=False,
                    signal=None,
                    say=None,
                    inferred_rule=None,
                    query="----",
                    answer=None,
                    expected="----",
                    n_hypotheses=101,
                    inbox=0,
                    inbox_says=[],
                    inbox_true=0,
                    inbox_false=0,
                    say_matches_pe=None,
                    examples=self.examples[cid],
                    parse_valid=True,
                )
            )
        return Snapshot(
            generation=0,
            epoch=self.epoch,
            epoch_generation=0,
            p_e=self.fn.description(),
            program_id=self.fn.program_id,
            substrate=self.substrate,
            sparse=self.sparse,
            correct_this_gen=0,
            identified=0,
            published_this_gen=0,
            published_h_gt_1=0,
            learned_from_board=0,
            learned_true=0,
            learned_false=0,
            circulating=[],
            rule_origins=[],
            inertia=0.0,
            j_running=0.0,
            j_history=[],
            cells=cells,
            policy=self.policy_label,
        )

    def _make_snapshot(
        self,
        decisions: dict[int, StepDecision],
        queries: dict[int, str],
        inboxes: dict[int, list[Message]],
        epoch_at_step: int,
    ) -> Snapshot:
        assert self.fn is not None
        cells: list[CellView] = []
        identified = 0
        published = 0
        published_h_gt_1 = 0
        from_board = 0
        learned_true = 0
        learned_false = 0
        correct = 0
        p_e = self.fn.description()
        for cid in all_cell_ids():
            row, col = coords(cid)
            decision = decisions[cid]
            query = queries[cid]
            expected = self.fn.apply(query)
            ok = bool(decision.answer is not None and decision.answer == expected)
            if ok:
                correct += 1
            if decision.n_hypotheses == 1:
                identified += 1
            if decision.publish_say:
                published += 1
                if decision.n_hypotheses > 1:
                    published_h_gt_1 += 1
            if decision.source == "message":
                from_board += 1
                if ok:
                    learned_true += 1
                else:
                    learned_false += 1
            inbox = inboxes[cid]
            inbox_true = sum(1 for m in inbox if m.say == p_e)
            cells.append(
                CellView(
                    cell_id=cid,
                    row=row,
                    col=col,
                    correct=ok,
                    identified=decision.n_hypotheses == 1,
                    source=decision.source,
                    published=bool(decision.publish_say),
                    signal=decision.signal,
                    say=decision.publish_say,
                    inferred_rule=decision.inferred_rule,
                    query=query,
                    answer=decision.answer,
                    expected=expected,
                    n_hypotheses=decision.n_hypotheses,
                    inbox=len(inbox),
                    inbox_says=[m.say for m in inbox],
                    inbox_true=inbox_true,
                    inbox_false=len(inbox) - inbox_true,
                    say_matches_pe=(
                        None if decision.publish_say is None else decision.publish_say == p_e
                    ),
                    examples=self.examples[cid],
                    parse_valid=decision.parse_valid,
                )
            )
        circulating = circulating_rules(
            self.board, self.generation, self.substrate, p_e
        )
        origins = []
        mass = 0
        age_mass = 0.0
        for row in circulating:
            origin = self.rule_origins.get(row["say"])
            merged = {**row, **(origin or {})}
            born = int(merged.get("epoch", epoch_at_step))
            merged["epoch_age"] = max(0, epoch_at_step - born)
            origins.append(merged)
            mass += merged["n"]
            age_mass += merged["n"] * merged["epoch_age"]
        inertia = age_mass / mass if mass else 0.0
        return Snapshot(
            generation=self.generation,
            epoch=epoch_at_step,
            epoch_generation=((self.generation - 1) % EPOCH_LENGTH) + 1,
            p_e=p_e,
            program_id=self.fn.program_id,
            substrate=self.substrate,
            sparse=self.sparse,
            correct_this_gen=correct,
            identified=identified,
            published_this_gen=published,
            published_h_gt_1=published_h_gt_1,
            learned_from_board=from_board,
            learned_true=learned_true,
            learned_false=learned_false,
            circulating=origins,
            rule_origins=list(self.rule_origins.values()),
            inertia=inertia,
            j_running=self.correct_total / self.opportunities,
            j_history=list(self.j_history),
            cells=cells,
            policy=self.policy_label,
        )


def snapshot_to_dict(snap: Snapshot, catalog: FunctionCatalog | None = None) -> dict:
    catalog = catalog or build_catalog()
    fn = catalog.by_id(snap.program_id)
    return {
        "generation": snap.generation,
        "epoch": snap.epoch,
        "epoch_generation": snap.epoch_generation,
        "p_e": snap.p_e,
        "program_id": snap.program_id,
        "substrate": snap.substrate,
        "sparse": snap.sparse,
        "correct_this_gen": snap.correct_this_gen,
        "identified": snap.identified,
        "published_this_gen": snap.published_this_gen,
        "published_h_gt_1": snap.published_h_gt_1,
        "learned_from_board": snap.learned_from_board,
        "learned_true": snap.learned_true,
        "learned_false": snap.learned_false,
        "n_distinct_rules": len(snap.circulating),
        "circulating": snap.circulating,
        "inertia": snap.inertia,
        "j_running": snap.j_running,
        "j_history": snap.j_history,
        "policy": snap.policy,
        "n_cells": N_CELLS,
        "epoch_length": EPOCH_LENGTH,
        "enumerator": {
            "p_e": snap.p_e,
            "ops": [op.description() for op in fn.canonical.ops],
            "demos": world_demos(fn),
        },
        "cells": [
            {
                "id": c.cell_id,
                "r": c.row,
                "c": c.col,
                "correct": c.correct,
                "identified": c.identified,
                "source": c.source,
                "published": c.published,
                "signal": c.signal,
                "say": c.say,
                "inferred_rule": c.inferred_rule,
                "query": c.query,
                "answer": c.answer,
                "expected": c.expected,
                "n_hypotheses": c.n_hypotheses,
                "inbox": c.inbox,
                "inbox_says": c.inbox_says,
                "inbox_true": c.inbox_true,
                "inbox_false": c.inbox_false,
                "say_matches_pe": c.say_matches_pe,
                "parse_valid": c.parse_valid,
                "examples": [{"x": x, "y": y} for x, y in c.examples],
                "trace": cell_trace(fn, c.examples, c.query, catalog),
            }
            for c in snap.cells
        ],
    }

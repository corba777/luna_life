"""Luna depth curve — 3-op held-out pairs outside the Life catalog.

TASK_LUNA_DEPTH.md. Does not touch the Life catalog or v1b. Options = 101 catalog
descriptions + the pair's two 3-op names (103).
"""
from __future__ import annotations

import json
import os
import random
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterator

CL_PATH = os.environ.get(
    "CONSTITUTIONAL_LIFE_PATH",
    str(Path(__file__).resolve().parents[1]),
)
if CL_PATH not in sys.path:
    sys.path.insert(0, CL_PATH)

from constitutional_life.board.board import Message  # noqa: E402
from constitutional_life.board.geometry import N_CELLS, neighbours  # noqa: E402
from constitutional_life.cell.memory import empty_memory, remember  # noqa: E402
from constitutional_life.cell.observation import make_observation, pad_inbox  # noqa: E402
from constitutional_life.cell.prompt import render_state  # noqa: E402
from constitutional_life.model.jev import RULE_INSTRUCTIONS, rule_key  # noqa: E402
from constitutional_life.task.catalog import (  # noqa: E402
    CanonicalFunction,
    build_catalog,
    function_id,
)
from constitutional_life.task.dsl import (  # noqa: E402
    N_INPUTS,
    Op,
    decode_seq,
    encode_seq,
    parse_op,
    validate_seq,
)
from constitutional_life.v1a_constants import (  # noqa: E402
    EPOCH_LENGTH,
    MESSAGE_TTL_BY_SUBSTRATE,
    N_EXAMPLES,
    READ_BUDGET,
    REGION_RADIUS,
)

DEPTH_SEED = 5410
DEPTH_PAIR_VERSION = "depth3_v1"
N_HELD_OUT = 25
N_PAIRS = 100
N_OPS = 3
MAX_EXAMPLE_ATTEMPTS = 200

_CAT = build_catalog()
_DESC = [fn.description() for fn in _CAT.functions]
_CATALOG_TABLES = {fn.output_table for fn in _CAT.functions}
N_CATALOG = len(_DESC)

# Life substrate mix (same as life_verify.env) — local copy to avoid circular import.
_SUBSTRATE_MIX = {"local": 0.50, "regional": 0.25, "global": 0.25}
_SUBSTRATE_RADIUS = {"local": 1, "regional": REGION_RADIUS, "global": None}


@dataclass(frozen=True, slots=True)
class DepthFunction:
    """3-op composition; bypasses Program's 1–2 op limit."""

    ops: tuple[Op, ...]
    output_table: tuple[int, ...]
    program_id: str

    def __post_init__(self) -> None:
        if len(self.ops) != N_OPS:
            raise ValueError(f"expected {N_OPS} ops, got {len(self.ops)}")

    def description(self) -> str:
        return ";".join(op.description() for op in self.ops)

    def apply(self, seq: str) -> str:
        out = validate_seq(seq)
        for op in self.ops:
            out = op.apply(out)
        return out

    @property
    def n_ops(self) -> int:
        return len(self.ops)


@dataclass(frozen=True, slots=True)
class DepthPair:
    id: str
    true_program_id: str
    true_desc: str
    false_program_id: str
    false_desc: str
    examples: tuple[tuple[str, str], ...]
    query: str
    named_says: tuple[str, str]
    seed: int
    harness: str = "canonical"


def _one_op_atoms() -> tuple[CanonicalFunction, ...]:
    atoms = tuple(fn for fn in _CAT.functions if fn.n_ops == 1)
    if len(atoms) != 17:
        raise RuntimeError(f"expected 17 one-op catalog atoms, got {len(atoms)}")
    return atoms


def _compose_table(tables: list[tuple[int, ...]]) -> tuple[int, ...]:
    """Compose output tables left-to-right: t0 then t1 then t2."""
    out = list(range(N_INPUTS))
    for table in tables:
        out = [table[i] for i in out]
    return tuple(out)


def _ops_from_atom(fn: CanonicalFunction) -> Op:
    ops = fn.canonical.ops
    if len(ops) != 1:
        raise RuntimeError(fn.description())
    return ops[0]


def iter_depth3_candidates() -> Iterator[tuple[tuple[Op, ...], tuple[int, ...], str]]:
    """All 17³ syntactic 3-op compositions with their output tables and descriptions."""
    atoms = _one_op_atoms()
    atom_ops = [_ops_from_atom(a) for a in atoms]
    atom_tables = [a.output_table for a in atoms]
    for i, oi in enumerate(atom_ops):
        ti = atom_tables[i]
        for j, oj in enumerate(atom_ops):
            tj = atom_tables[j]
            for k, ok in enumerate(atom_ops):
                tk = atom_tables[k]
                ops = (oi, oj, ok)
                table = _compose_table([ti, tj, tk])
                desc = ";".join(o.description() for o in ops)
                yield ops, table, desc


def build_depth3_pool() -> dict:
    """Behavioural dedupe against identity / ≤2-op catalog / other 3-ops.

    Among equal tables keep the lexicographically smallest description.
    """
    n_syntactic = 0
    best: dict[str, tuple[str, tuple[Op, ...], tuple[int, ...]]] = {}
    n_eq_leq2 = 0
    for ops, table, desc in iter_depth3_candidates():
        n_syntactic += 1
        if table in _CATALOG_TABLES:
            n_eq_leq2 += 1
            continue
        pid = function_id(table)
        cur = best.get(pid)
        if cur is None or desc < cur[0]:
            best[pid] = (desc, ops, table)
    pool = [
        DepthFunction(ops=ops, output_table=table, program_id=pid)
        for pid, (_desc, ops, table) in sorted(best.items(), key=lambda kv: kv[1][0])
    ]
    return {
        "n_syntactic": n_syntactic,
        "n_eq_leq2_or_identity": n_eq_leq2,
        "n_unique_3op": len(pool),
        "pool": pool,
    }


@lru_cache(maxsize=1)
def held_out_depth3(seed: int = DEPTH_SEED, n: int = N_HELD_OUT) -> tuple[DepthFunction, ...]:
    info = build_depth3_pool()
    pool: list[DepthFunction] = info["pool"]
    if len(pool) < n:
        raise RuntimeError(f"depth3 pool too small: {len(pool)} < {n}")
    rng = random.Random(f"luna_depth|heldout|{DEPTH_PAIR_VERSION}|{seed}")
    chosen = rng.sample(pool, n)
    chosen.sort(key=lambda f: f.description())
    return tuple(chosen)


def parse_depth_description(text: str) -> DepthFunction:
    parts = text.split(";")
    if len(parts) != N_OPS:
        raise ValueError(f"expected {N_OPS} ops, got {len(parts)} in {text!r}")
    ops = tuple(parse_op(p) for p in parts)
    # Rebuild table from ops (apply chain)
    table = []
    for i in range(N_INPUTS):
        s = decode_seq(i)
        for op in ops:
            s = op.apply(s)
        table.append(encode_seq(s))
    table_t = tuple(table)
    return DepthFunction(ops=ops, output_table=table_t, program_id=function_id(table_t))


def _table_agrees(table: tuple[int, ...], examples: list[tuple[str, str]]) -> bool:
    for inp, out in examples:
        if table[encode_seq(inp)] != encode_seq(out):
            return False
    return True


def _sample_examples_pair(
    true_fn: DepthFunction,
    false_fn: DepthFunction,
    rng: random.Random,
    n_examples: int = N_EXAMPLES,
    max_attempts: int = MAX_EXAMPLE_ATTEMPTS,
) -> list[tuple[str, str]] | None:
    """Examples fit true, not false, and no ≤2-op catalog function."""
    for _ in range(max_attempts):
        idxs = rng.sample(range(N_INPUTS), n_examples)
        examples = [
            (decode_seq(i), decode_seq(true_fn.output_table[i])) for i in idxs
        ]
        if _table_agrees(false_fn.output_table, examples):
            continue
        if any(_table_agrees(fn.output_table, examples) for fn in _CAT.functions):
            continue
        return examples
    return None


def generate_depth3_pairs(
    *,
    seed: int = DEPTH_SEED,
    n_pairs: int = N_PAIRS,
    n_held: int = N_HELD_OUT,
) -> list[DepthPair]:
    held = list(held_out_depth3(seed=seed, n=n_held))
    by_id = {f.program_id: f for f in held}
    rng = random.Random(f"luna_depth|pairs|{DEPTH_PAIR_VERSION}|{seed}|{n_pairs}")
    # ~4 pairs per function: cycle through held-out as true
    out: list[DepthPair] = []
    for k in range(n_pairs):
        true_fn = held[k % len(held)]
        for _ in range(80):
            inst_seed = rng.randrange(2**31)
            irng = random.Random(inst_seed)
            false_fn = irng.choice([f for f in held if f.program_id != true_fn.program_id])
            examples = _sample_examples_pair(true_fn, false_fn, irng)
            if examples is None:
                continue
            names = [true_fn.description(), false_fn.description()]
            irng.shuffle(names)
            query = decode_seq(irng.randrange(N_INPUTS))
            out.append(DepthPair(
                id=f"lv-pair-{DEPTH_PAIR_VERSION}-heldout_fn-s{seed}-op3-{k:04d}",
                true_program_id=true_fn.program_id,
                true_desc=true_fn.description(),
                false_program_id=false_fn.program_id,
                false_desc=false_fn.description(),
                examples=tuple((a, b) for a, b in examples),
                query=query,
                named_says=(names[0], names[1]),
                seed=inst_seed,
            ))
            break
        else:
            raise RuntimeError(f"failed to build depth pair k={k} true={true_fn.description()}")
    assert len(out) == n_pairs
    assert all(p.true_program_id in by_id for p in out)
    return out


def _sample_substrate(rng: random.Random) -> str:
    names, weights = zip(*_SUBSTRATE_MIX.items())
    return rng.choices(list(names), weights=list(weights), k=1)[0]


def _legal_senders(cell: int, substrate: str) -> list[int]:
    radius = _SUBSTRATE_RADIUS[substrate]
    if radius is None:
        return [c for c in range(N_CELLS) if c != cell]
    return neighbours(cell, radius)


def _pick_senders(rng: random.Random, pool: list[int], n: int) -> list[int]:
    if n == 0:
        return []
    if n <= len(pool):
        return rng.sample(pool, n)
    return [rng.choice(pool) for _ in range(n)]


def observe_depth(pair: DepthPair):
    """Life-shaped observation; inbox names the two 3-op rules."""
    rng = random.Random(f"obs|depth|{pair.seed}")
    substrate = _sample_substrate(rng)
    ttl = MESSAGE_TTL_BY_SUBSTRATE[substrate]
    cell = rng.randrange(N_CELLS)
    epoch = rng.randrange(0, 4)
    true_desc = pair.true_desc
    epoch_generation = rng.randrange(2, EPOCH_LENGTH + 1)
    generation = epoch * EPOCH_LENGTH + (epoch_generation - 1)
    if generation < 1:
        generation = 2
        epoch = generation // EPOCH_LENGTH
        epoch_generation = (generation % EPOCH_LENGTH) + 1
    epoch_start = epoch * EPOCH_LENGTH
    prev_desc = _DESC[rng.randrange(N_CATALOG)]
    pool = _legal_senders(cell, substrate)
    senders = _pick_senders(rng, pool, len(pair.named_says))
    msgs = []
    for s, say in zip(senders, pair.named_says):
        if say == true_desc:
            max_age = min(ttl, generation - epoch_start)
            age = rng.randint(1, max(1, max_age))
            msg_gen = generation - age
            if msg_gen < epoch_start:
                msg_gen = epoch_start
            say_eff = say
        else:
            age = rng.randint(1, min(ttl, generation))
            msg_gen = generation - age
            say_eff = prev_desc if msg_gen // EPOCH_LENGTH < epoch else say
        msgs.append(Message(
            sender_id=s,
            generation=msg_gen,
            signal=rng.randrange(8),
            say=say_eff,
        ))
    # Memory: empty or catalog-only (3-op never in prior epoch).
    if generation == 0 or rng.random() < 0.4:
        memory = empty_memory()
    else:
        prior_q = decode_seq(rng.randrange(N_INPUTS))
        ref_fn = _CAT.functions[rng.randrange(N_CATALOG)]
        answer = ref_fn.apply(prior_q)
        memory = remember(
            task_answer=answer,
            correct=True,
            published=False,
            signal=None,
            say=None,
        )
    obs = make_observation(
        cell_id=cell,
        generation=generation,
        epoch=epoch,
        epoch_length=EPOCH_LENGTH,
        examples=[tuple(e) for e in pair.examples],
        query=pair.query,
        inbox=pad_inbox(msgs, READ_BUDGET),
        memory=memory,
    )
    return obs


def render_receiver_depth(pair: DepthPair) -> dict:
    """103 options: catalog 101 + true + false 3-op descriptions."""
    obs = observe_depth(pair)
    options = list(_DESC) + [pair.true_desc, pair.false_desc]
    if len(options) != N_CATALOG + 2:
        raise RuntimeError(len(options))
    if len(set(options)) != len(options):
        raise RuntimeError("option collision with catalog — 3-op desc equals a catalog name")
    return {
        "state": render_state(obs, channel=True),
        "question": RULE_INSTRUCTIONS,
        "options": options,
        "labels": [rule_key(i) for i in range(len(options))],
        "true_desc": pair.true_desc,
        "false_desc": pair.false_desc,
    }


def generator_check(*, seed: int = DEPTH_SEED) -> dict:
    """No-model checks for TASK_LUNA_DEPTH. Deterministic under DEPTH_SEED."""
    info = build_depth3_pool()
    pool: list[DepthFunction] = info["pool"]
    held = held_out_depth3(seed=seed)
    pairs = generate_depth3_pairs(seed=seed)

    # Dedupe vs ≤2-op
    leq2_overlap = sum(1 for f in held if f.output_table in _CATALOG_TABLES)
    # Unique tables among held
    n_unique_held = len({f.program_id for f in held})

    # Parse-back
    parse_ok = 0
    for f in held:
        back = parse_depth_description(f.description())
        if back.program_id != f.program_id or back.output_table != f.output_table:
            raise AssertionError(f"parse-back fail: {f.description()}")
        parse_ok += 1

    # Pair invariants
    for p in pairs:
        true_fn = next(f for f in held if f.program_id == p.true_program_id)
        false_fn = next(f for f in held if f.program_id == p.false_program_id)
        ex = list(p.examples)
        assert _table_agrees(true_fn.output_table, ex)
        assert not _table_agrees(false_fn.output_table, ex)
        assert not any(_table_agrees(fn.output_table, ex) for fn in _CAT.functions)
        assert set(p.named_says) == {p.true_desc, p.false_desc}
        q = render_receiver_depth(p)
        assert len(q["options"]) == 103
        assert p.true_desc in q["options"] and p.false_desc in q["options"]

    # Determinism
    held2 = held_out_depth3(seed=seed)
    pairs2 = generate_depth3_pairs(seed=seed)
    assert [f.description() for f in held] == [f.description() for f in held2]
    assert [p.id for p in pairs] == [p.id for p in pairs2]
    assert [p.true_desc for p in pairs] == [p.true_desc for p in pairs2]
    assert [p.examples for p in pairs] == [p.examples for p in pairs2]

    return {
        "depth_seed": seed,
        "depth_pair_version": DEPTH_PAIR_VERSION,
        "n_atomic_1op": 17,
        "n_syntactic_3op": info["n_syntactic"],
        "n_eq_leq2_or_identity": info["n_eq_leq2_or_identity"],
        "n_unique_3op_pool": info["n_unique_3op"],
        "n_held_out": len(held),
        "n_unique_held": n_unique_held,
        "leq2_overlap_held": leq2_overlap,
        "parse_back_ok": parse_ok,
        "n_pairs": len(pairs),
        "held_out_descriptions": [f.description() for f in held],
        "held_out_program_ids": [f.program_id for f in held],
        "pair_ids_head": [p.id for p in pairs[:5]],
        "pair_ids_tail": [p.id for p in pairs[-5:]],
        "n_options": 103,
        "deterministic": True,
        "ok": True,
    }


def dump_pairs_json(path: Path, *, seed: int = DEPTH_SEED) -> None:
    held = held_out_depth3(seed=seed)
    pairs = generate_depth3_pairs(seed=seed)
    payload = {
        "depth_seed": seed,
        "depth_pair_version": DEPTH_PAIR_VERSION,
        "held_out": [
            {
                "program_id": f.program_id,
                "description": f.description(),
                "n_ops": f.n_ops,
            }
            for f in held
        ],
        "pairs": [
            {
                "id": p.id,
                "true_program_id": p.true_program_id,
                "true_desc": p.true_desc,
                "false_program_id": p.false_program_id,
                "false_desc": p.false_desc,
                "examples": list(p.examples),
                "query": p.query,
                "named_says": list(p.named_says),
                "seed": p.seed,
            }
            for p in pairs
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")

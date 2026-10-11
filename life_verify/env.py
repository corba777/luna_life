"""
L-VERIFY Part 1 — a single Constitutional Life cell with a scripted inbox.

One decision: the `rule` question over the 101 canonical functions. The trained
skill is local: accept a named rule that is consistent with the cell's own two
identifying examples E, reject a named rule that contradicts E. No lattice, no
other learning cells. Spec: TASK_LIFE_VERIFIER.md; bands: PREREG_L_VERIFY.md.

Everything that defines the Life surface (typed constitution, user block, option
descriptions, `RULE_INSTRUCTIONS`, hypothesis template) is imported from
`constitutional_life`; this module only adds
  - a frozen function split (train / held-out),
  - the scripted inbox generator (fixed mixture),
  - a harness pool (canonical + paraphrased constitutions),
  - metrics and numpy reference policies (no model).
"""
from __future__ import annotations

import json
import os
import random
import sys
from collections import Counter
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable

import numpy as np

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
from constitutional_life.cell.prompt import render_state, render_user  # noqa: E402
from constitutional_life.model.jev import RULE_INSTRUCTIONS, rule_key  # noqa: E402
from constitutional_life.task.catalog import build_catalog  # noqa: E402
from constitutional_life.task.dsl import N_INPUTS, decode_seq  # noqa: E402
from constitutional_life.task.identify import hypothesis_set, sample_identifying_examples  # noqa: E402
from constitutional_life.v1a_constants import (  # noqa: E402
    EPOCH_LENGTH,
    GRID,
    MESSAGE_TTL_BY_SUBSTRATE,
    N_EXAMPLES,
    READ_BUDGET,
    REGION_RADIUS,
)

HERE = Path(__file__).resolve().parent
SPLIT_PATH = HERE / "function_split.json"
SPLIT_SEED = 20261004

INBOX_TYPES = (
    "empty", "true_only", "true_false_maj", "false_only",
    "true_maj_false", "mixed_distinct", "pair",
)
# Frequency-balanced + pair (AMENDMENT_L_VERIFY_FREQ_BALANCE + AMENDMENT_L_VERIFY_PAIR).
# Mirror pairs equal → frequency uninformative; `pair` = pure discrimination primary.
# Old leaky mix: runs/life_verify/archive_freq_leak_mixture_20261005/.
MIXTURE_VERSION = "freq_balanced_v3_pair"
MIXTURE = {
    "empty": 0.15,
    "true_only": 0.10,       # singleton true  ↔ false_only
    "false_only": 0.10,      # singleton false (always n=1); weak reject incentive
    "true_false_maj": 0.125,  # true minority   ↔ true_maj_false
    "true_maj_false": 0.125,
    "mixed_distinct": 0.15,  # all distinct — every name is frequency-1
    "pair": 0.25,            # one true + one false once — primary verify signal
}
assert abs(sum(MIXTURE.values()) - 1.0) < 1e-12
assert abs(MIXTURE["true_only"] - MIXTURE["false_only"]) < 1e-12
assert abs(MIXTURE["true_false_maj"] - MIXTURE["true_maj_false"]) < 1e-12
assert set(MIXTURE) == set(INBOX_TYPES)
TRAIN_HARNESSES = ("canonical", "p1", "p2", "p3")
ALL_HARNESSES = TRAIN_HARNESSES + ("heldout",)
N_OPTIONS = 101

# Observation-surface sampling (AMENDMENT_L_VERIFY_SURFACE.md). Generator only.
SUBSTRATE_MIX = {"local": 0.50, "regional": 0.25, "global": 0.25}
SUBSTRATE_RADIUS = {"local": 1, "regional": REGION_RADIUS, "global": None}
MEMORY_MIXTURE = {
    "none": 0.10,
    "correct_silent": 0.25,
    "correct_published": 0.15,
    "wrong_silent": 0.30,
    "wrong_published": 0.20,
}

_CAT = build_catalog()
_DESC = [fn.description() for fn in _CAT.functions]
_DESC_TO_IDX = {d: i for i, d in enumerate(_DESC)}
_PID_TO_IDX = {fn.program_id: i for i, fn in enumerate(_CAT.functions)}
assert len(_DESC_TO_IDX) == len(_DESC) == N_OPTIONS, "descriptions must be unique over 101 options"


# ------------------------------------------------------------------ instance

@dataclass(frozen=True)
class InstanceLV:
    id: str
    function_id: str                         # program_id
    function_index: int                      # 0..100 catalog index
    n_ops: int
    examples: tuple[tuple[str, str], ...]    # 2 identifying examples
    query: str
    inbox_type: str                          # see INBOX_TYPES / MIXTURE
    named_says: tuple[str, ...]              # descriptions of the non-null slots (padded with nulls in render)
    harness: str                             # canonical|p1|p2|p3|heldout
    seed: int
    split: str                               # train_fn|heldout_fn


def named_indices(inst: InstanceLV) -> tuple[int, ...]:
    """Catalog indices of the *mixture intent* names on the instance (pre-surface)."""
    return tuple(_DESC_TO_IDX[s] for s in inst.named_says)


def effective_named_says(inst: InstanceLV) -> tuple[str, ...]:
    """Says as rendered in `_obs` (cross-epoch slots → previous-epoch rule)."""
    return tuple(m.say for m in _obs(inst).inbox if m is not None)


def effective_named_indices(inst: InstanceLV) -> tuple[int, ...]:
    """Catalog indices of the rendered inbox — what metrics and oracles must use."""
    return tuple(_DESC_TO_IDX[s] for s in effective_named_says(inst))


def with_harness(inst: InstanceLV, harness: str) -> InstanceLV:
    if harness not in ALL_HARNESSES:
        raise ValueError(f"unknown harness {harness!r}")
    return replace(inst, harness=harness)


def empty_variant(inst: InstanceLV) -> InstanceLV:
    """Same cell, same E and query, nothing in the inbox (the `solo` counterfactual)."""
    return replace(inst, inbox_type="empty", named_says=(), id=inst.id + "|solo")


def instance_content_key(inst: InstanceLV) -> tuple:
    return (inst.function_id, inst.examples, inst.query, inst.named_says, inst.harness)


# ------------------------------------------------------------------ function split

def function_split(seed: int = SPLIT_SEED) -> tuple[list[int], list[int]]:
    """Frozen (train_indices, heldout_indices), stratified by n_ops (~70 / ~31).

    Persisted to `function_split.json` on first call and reloaded afterwards;
    the reload is verified against the catalog so a changed catalog fails loudly.
    """
    if SPLIT_PATH.is_file():
        blob = json.loads(SPLIT_PATH.read_text())
        pids = [fn.program_id for fn in _CAT.functions]
        if blob["program_ids"] != pids:
            raise RuntimeError("function_split.json does not match the current catalog")
        return list(blob["train"]), list(blob["heldout"])
    rng = random.Random(seed)
    train: list[int] = []
    held: list[int] = []
    by_ops: dict[int, list[int]] = {}
    for i, fn in enumerate(_CAT.functions):
        by_ops.setdefault(fn.n_ops, []).append(i)
    frac = 31 / 101
    for n_ops in sorted(by_ops):
        idx = list(by_ops[n_ops])
        rng.shuffle(idx)
        k = int(round(len(idx) * frac))
        held.extend(idx[:k])
        train.extend(idx[k:])
    train.sort()
    held.sort()
    SPLIT_PATH.write_text(json.dumps({
        "seed": seed,
        "note": "frozen L-VERIFY function split; stratified by n_ops; do not regenerate",
        "program_ids": [fn.program_id for fn in _CAT.functions],
        "train": train,
        "heldout": held,
        "n_ops": {str(k): len(v) for k, v in sorted(by_ops.items())},
    }, indent=2))
    return train, held


# ------------------------------------------------------------------ inbox generator

def _allocate(n: int, rng: random.Random) -> list[str]:
    """Quota-allocated inbox types (largest remainder), shuffled. Small n keeps the mixture."""
    raw = {t: MIXTURE[t] * n for t in INBOX_TYPES}
    counts = {t: int(v) for t, v in raw.items()}
    rest = n - sum(counts.values())
    order = sorted(INBOX_TYPES, key=lambda t: (raw[t] - counts[t], rng.random()), reverse=True)
    for t in order[:rest]:
        counts[t] += 1
    types = [t for t in INBOX_TYPES for _ in range(counts[t])]
    rng.shuffle(types)
    return types


def _fill_inbox(inbox_type: str, f: int, false_pool: list[int], rng: random.Random) -> list[int]:
    """Catalog indices named in the non-null slots (before slot shuffling)."""
    if inbox_type == "empty":
        return []
    if inbox_type == "true_only":
        return [f]
    if inbox_type == "true_false_maj":
        g = rng.choice(false_pool)
        return [f] + [g] * rng.randint(3, 5)
    if inbox_type == "false_only":
        # Always a singleton false name — mirrors true_only (freq_balanced_v2+).
        return [rng.choice(false_pool)]
    if inbox_type == "pair":
        # One true + one false, each once — pure discrimination (AMENDMENT_L_VERIFY_PAIR).
        return [f, rng.choice(false_pool)]
    if inbox_type == "true_maj_false":
        k = rng.randint(3, 5)
        m = rng.randint(1, 2)
        return [f] * k + [rng.choice(false_pool) for _ in range(m)]
    if inbox_type == "mixed_distinct":
        d = rng.randint(2, 5)
        with_true = rng.random() < 0.5
        n_false = d - 1 if with_true else d
        names = rng.sample(false_pool, n_false)
        return ([f] if with_true else []) + names
    raise ValueError(inbox_type)


def generate_lv(n: int, split: str = "train_fn", seed: int = 0,
                harness_pool: tuple[str, ...] = TRAIN_HARNESSES) -> list[InstanceLV]:
    """n instances: functions from `split`, inbox types by the fixed mixture, harness uniform
    from `harness_pool`. Ids embed split and seed (never key caches on id alone)."""
    if split not in ("train_fn", "heldout_fn"):
        raise ValueError(split)
    for h in harness_pool:
        if h not in ALL_HARNESSES:
            raise ValueError(f"unknown harness {h!r}")
    train_idx, held_idx = function_split()
    pool = train_idx if split == "train_fn" else held_idx
    rng = random.Random(f"lv|{split}|{seed}")
    types = _allocate(n, rng)
    out: list[InstanceLV] = []
    for k in range(n):
        inst_seed = rng.randrange(2**31)
        irng = random.Random(inst_seed)
        # resample the function if no identifying pair of examples is found
        for _ in range(50):
            fi = irng.choice(pool)
            fn = _CAT.functions[fi]
            examples, _ = sample_identifying_examples(fn, N_EXAMPLES, _CAT, irng)
            if examples is not None:
                break
        else:
            raise RuntimeError("no identifying examples found")
        hyp = {_PID_TO_IDX[h.program_id] for h in hypothesis_set(examples, _CAT)}
        assert hyp == {fi}
        false_pool = [i for i in range(N_OPTIONS) if i not in hyp]
        names = _fill_inbox(types[k], fi, false_pool, irng)
        irng.shuffle(names)
        query = decode_seq(irng.randrange(N_INPUTS))
        harness = harness_pool[irng.randrange(len(harness_pool))]
        out.append(InstanceLV(
            id=f"lv-{split}-s{seed}-{k:04d}",
            function_id=fn.program_id,
            function_index=fi,
            n_ops=fn.n_ops,
            examples=tuple((x, y) for x, y in examples),
            query=query,
            inbox_type=types[k],
            named_says=tuple(_DESC[i] for i in names),
            harness=harness,
            seed=inst_seed,
            split=split,
        ))
    return out


# Stratified pair eval (AMENDMENT_L_VERIFY_PAIR_EVAL + PAIR_NOPS).
PAIR_EVAL_SEED = 5401
PAIR_EVAL_N_PER_OPS = 100
PAIR_TRAIN1OP_SEED = 5402  # confirmatory row on train-split 1-op functions
PAIR_EVAL_VERSION = "nops_matched_v1"  # false name has same n_ops as true (AMENDMENT_L_VERIFY_PAIR_NOPS)


def generate_lv_pairs_stratified(
    n_per_ops: int = PAIR_EVAL_N_PER_OPS,
    split: str = "heldout_fn",
    seed: int = PAIR_EVAL_SEED,
    harness: str = "canonical",
    n_ops_filter: tuple[int, ...] | None = None,
    *,
    match_false_n_ops: bool = True,
) -> list[InstanceLV]:
    """All-`pair` instances, equal count per n_ops (default 100×1-op + 100×2-op).

    Primary pair readout set. Ids: `lv-pair-{split}-s{seed}-op{n}-{k:04d}`.
    `n_ops_filter=(1,)` with split=train_fn → confirmatory train-1-op row.

    If `match_false_n_ops` (default True, v1): false name drawn only from functions
    with the same n_ops as the true rule — kills length/complexity confound.
    """
    if split not in ("train_fn", "heldout_fn"):
        raise ValueError(split)
    if harness not in ALL_HARNESSES:
        raise ValueError(harness)
    if n_per_ops < 1:
        raise ValueError(n_per_ops)
    train_idx, held_idx = function_split()
    pool = train_idx if split == "train_fn" else held_idx
    ops = tuple(n_ops_filter) if n_ops_filter is not None else (1, 2)
    by_ops: dict[int, list[int]] = {o: [] for o in ops}
    for i in pool:
        o = _CAT.functions[i].n_ops
        if o in by_ops:
            by_ops[o].append(i)
    for o, idxs in by_ops.items():
        if not idxs:
            raise RuntimeError(f"no {o}-op functions in {split}")
    # Same-n_ops false pools over the full catalog (not only the split).
    catalog_by_ops: dict[int, list[int]] = {}
    for i, fn in enumerate(_CAT.functions):
        catalog_by_ops.setdefault(fn.n_ops, []).append(i)
    rng = random.Random(f"lv|pair|{PAIR_EVAL_VERSION}|{split}|{seed}|{ops}|{match_false_n_ops}")
    out: list[InstanceLV] = []
    for n_ops in ops:
        idxs = by_ops[n_ops]
        for k in range(n_per_ops):
            inst_seed = rng.randrange(2**31)
            irng = random.Random(inst_seed)
            for _ in range(50):
                fi = irng.choice(idxs)
                fn = _CAT.functions[fi]
                examples, _ = sample_identifying_examples(fn, N_EXAMPLES, _CAT, irng)
                if examples is not None:
                    break
            else:
                raise RuntimeError(f"no identifying examples for {n_ops}-op pool")
            hyp = {_PID_TO_IDX[h.program_id] for h in hypothesis_set(examples, _CAT)}
            assert hyp == {fi} and fn.n_ops == n_ops
            if match_false_n_ops:
                false_pool = [i for i in catalog_by_ops[n_ops] if i not in hyp]
            else:
                false_pool = [i for i in range(N_OPTIONS) if i not in hyp]
            if not false_pool:
                raise RuntimeError(f"empty false pool for n_ops={n_ops} match={match_false_n_ops}")
            names = _fill_inbox("pair", fi, false_pool, irng)
            # _fill_inbox("pair") picks one false from false_pool; enforce same-ops if matched.
            assert not match_false_n_ops or all(
                _CAT.functions[j].n_ops == n_ops for j in names
            )
            irng.shuffle(names)
            query = decode_seq(irng.randrange(N_INPUTS))
            out.append(InstanceLV(
                id=f"lv-pair-{PAIR_EVAL_VERSION}-{split}-s{seed}-op{n_ops}-{k:04d}",
                function_id=fn.program_id,
                function_index=fi,
                n_ops=fn.n_ops,
                examples=tuple((x, y) for x, y in examples),
                query=query,
                inbox_type="pair",
                named_says=tuple(_DESC[i] for i in names),
                harness=harness,
                seed=inst_seed,
                split=split,
            ))
    return out


# ------------------------------------------------------------------ rendering / harness pool

def _sample_substrate(rng: random.Random) -> str:
    names, weights = zip(*SUBSTRATE_MIX.items())
    return rng.choices(list(names), weights=list(weights), k=1)[0]


def _legal_senders(cell: int, substrate: str) -> list[int]:
    radius = SUBSTRATE_RADIUS[substrate]
    if radius is None:
        return [c for c in range(N_CELLS) if c != cell]
    return neighbours(cell, radius)


def _pick_senders(rng: random.Random, pool: list[int], n: int) -> list[int]:
    if n == 0:
        return []
    if not pool:
        raise RuntimeError("empty neighbour pool")
    if n <= len(pool):
        return rng.sample(pool, n)
    return [rng.choice(pool) for _ in range(n)]


def _sample_memory(
    rng: random.Random,
    inst: InstanceLV,
    generation: int,
    *,
    epoch: int,
    epoch_generation: int,
    prev_desc: str,
):
    """Life-like one-step memory. Forced empty at generation 0 (AMENDMENT).

    Life does not clear memory in `_begin_epoch`. At epoch_generation==1 with
    epoch>0 the stored step is from the *previous* epoch's rule — so "correct"
    memories use `prev_desc`, not the current f (otherwise the cell never sees
    the misleading "I was right" signal after a rule change).
    """
    if generation == 0:
        return empty_memory()
    kind = rng.choices(
        list(MEMORY_MIXTURE.keys()), weights=list(MEMORY_MIXTURE.values()), k=1
    )[0]
    if kind == "none":
        return empty_memory()
    # Rule the previous answer was scored against.
    cross_epoch_mem = epoch > 0 and epoch_generation == 1
    ref_desc = prev_desc if cross_epoch_mem else _DESC[inst.function_index]
    ref_idx = _DESC_TO_IDX[ref_desc]
    ref_fn = _CAT.functions[ref_idx]
    prior_q = decode_seq(rng.randrange(N_INPUTS))
    published = kind.endswith("published")
    if kind.startswith("correct"):
        answer = ref_fn.apply(prior_q)
        correct = True
        # AMENDMENT_L_VERIFY_PAIR_BINARY: say bound to the rule that produced the answer
        # (Life: publish names the chosen rule). No inbox swap.
        say = ref_desc
    else:
        wrong_pool = [i for i in range(N_OPTIONS) if i != ref_idx]
        wi = rng.choice(wrong_pool)
        answer = _CAT.functions[wi].apply(prior_q)
        correct = False
        say = _CAT.functions[wi].description()
    # Runtime invariant (train + eval): published say must be the rule of `answer` on prior_q.
    # The existential "∃q: say(q)=answer" test is useless — it passes under the old inbox swap.
    if published:
        say_fn = _CAT.functions[_DESC_TO_IDX[say]]
        if say_fn.apply(prior_q) != answer:
            raise AssertionError(
                f"memory say/answer unbound: say={say!r} prior_q={prior_q!r} "
                f"answer={answer!r} say(prior_q)={say_fn.apply(prior_q)!r} correct={correct}"
            )
    return remember(
        task_answer=answer,
        correct=correct,
        published=published,
        signal=rng.randrange(8) if published else None,
        say=say if published else None,
    )


def observe_lv(inst: InstanceLV) -> tuple:
    """Deterministic Life-legal observation + sampling meta (AMENDMENT).

    Returns `(obs, meta)` where meta has substrate / ttl / prev_desc / epoch_generation
    for distribution checks against a real Life engine run.
    """
    rng = random.Random(f"obs|{inst.seed}")
    substrate = _sample_substrate(rng)
    ttl = MESSAGE_TTL_BY_SUBSTRATE[substrate]
    cell = rng.randrange(N_CELLS)
    epoch = rng.randrange(0, 4)
    true_desc = _DESC[inst.function_index]
    # Current-rule names cannot appear in the inbox at epoch_generation==1 (every
    # visible message is from the previous epoch). If the mixture intends a true
    # name, start at epoch_generation ≥ 2 so it can be stamped in-epoch.
    if any(s == true_desc for s in inst.named_says):
        epoch_generation = rng.randrange(2, EPOCH_LENGTH + 1)
    else:
        epoch_generation = rng.randrange(1, EPOCH_LENGTH + 1)
    generation = epoch * EPOCH_LENGTH + (epoch_generation - 1)
    n_msg = len(inst.named_says)
    if n_msg and generation < 1:
        # Non-empty inbox is impossible at global generation 0 on the board.
        generation = 1
        epoch = generation // EPOCH_LENGTH
        epoch_generation = (generation % EPOCH_LENGTH) + 1
        if any(s == true_desc for s in inst.named_says) and epoch_generation < 2:
            generation = 2
            epoch = generation // EPOCH_LENGTH
            epoch_generation = (generation % EPOCH_LENGTH) + 1
    epoch_start = epoch * EPOCH_LENGTH
    # One previous-epoch rule for this observation (≠ current f). Used for every
    # cross-epoch stamp — matches Life: those messages name the prior P_e.
    prev_pool = [i for i in range(N_OPTIONS) if i != inst.function_index]
    prev_desc = _DESC[rng.choice(prev_pool)]
    pool = _legal_senders(cell, substrate)
    senders = _pick_senders(rng, pool, n_msg)
    msgs = []
    n_cross = 0
    for s, say in zip(senders, inst.named_says):
        if say == true_desc and epoch_generation > 1:
            # Keep current-rule names inside this epoch (impossible at epoch_gen=1).
            max_age = min(ttl, generation - epoch_start)
            age = rng.randint(1, max(1, max_age))
            msg_gen = generation - age
            if msg_gen < epoch_start:
                msg_gen = epoch_start
            say_eff = say
        else:
            age = rng.randint(1, min(ttl, generation))
            msg_gen = generation - age
            # Cross-epoch ⇒ previous epoch's rule (false for current E).
            say_eff = prev_desc if msg_gen // EPOCH_LENGTH < epoch else say
        if msg_gen // EPOCH_LENGTH < epoch:
            n_cross += 1
        msgs.append(Message(
            sender_id=s,
            generation=msg_gen,
            signal=rng.randrange(8),
            say=say_eff,
        ))
    memory = _sample_memory(
        rng, inst, generation,
        epoch=epoch, epoch_generation=epoch_generation, prev_desc=prev_desc,
    )
    obs = make_observation(
        cell_id=cell,
        generation=generation,
        epoch=epoch,
        epoch_length=EPOCH_LENGTH,
        examples=[tuple(e) for e in inst.examples],
        query=inst.query,
        inbox=pad_inbox(msgs, READ_BUDGET),
        memory=memory,
    )
    meta = {
        "substrate": substrate,
        "ttl": ttl,
        "prev_desc": prev_desc,
        "epoch_generation": epoch_generation,
        "n_cross_epoch": n_cross,
    }
    return obs, meta


def _obs(inst: InstanceLV):
    """Deterministic Life-legal observation (AMENDMENT_L_VERIFY_SURFACE.md)."""
    return observe_lv(inst)[0]


# Paraphrase constitutions. They state the same facts as the canonical typed
# constitution (grid, shared hidden transformation, private examples and query,
# memory, eight slots, publishing, choose from options) and say nothing about
# whether to trust the messages. Only the constitution wording differs; the user
# block (examples / query / memory / inbox) is the canonical Life text, verbatim.
_P1 = f"""You are a single cell in a wrapping {GRID}x{GRID} grid of {N_CELLS} cells.

During this epoch every cell works on the same hidden transformation of 4-symbol strings over the letters A-H. Each cell gets its own private examples and its own query in every generation. Nothing is scored jointly. An answer is right when it equals the hidden transformation applied to your query.

What you can see: your private examples, your query, a one-step memory of your previous answer, and eight message slots that other cells may have filled. Slots nobody filled are marked empty.

You may publish at most one message per generation, or keep silent. A message carries a signal from 0 to 7 and names one transformation. It becomes visible only in later generations and only to cells that are allowed to see it. Your own rule choice and your answer stay private.

Pick the hidden transformation from the listed options. The engine applies it to your query to produce your answer."""

_P2 = f"""Setting: one cell on a {GRID}x{GRID} torus ({N_CELLS} cells in total).

Task: the cells of an epoch share one hidden mapping from 4-symbol strings over A-H to 4-symbol strings. A cell is shown a few private input-output examples of the mapping and one query input. A cell is correct when the answer it gives for its query is what the hidden mapping returns for that input. Cells are not scored together.

Inputs to a cell: private examples; the query; the previous step (one step of memory); eight inbox slots, each either empty or holding a message from another cell.

Output of a cell: a choice of one transformation from the options. You may also publish one message (a signal 0-7 naming a transformation) or stay silent; published messages appear in later generations, and only to cells that can see them. The chosen rule and the answer are not shown to anybody else."""

_P3 = f"""You are a cell ({N_CELLS} cells, wrapping {GRID}x{GRID} grid).
- Hidden: one transformation of 4-symbol strings over A-H, the same for all cells this epoch.
- Yours: private examples and a query that change every generation.
- No shared score. Correct = the hidden transformation applied to your query.
- You see: examples, query, memory of your last step, eight message slots (unused ones are empty).
- You may publish at most one message (signal 0-7 plus one named transformation) or stay silent. Messages show up in later generations, only for cells allowed to see them. Your rule choice and answer stay private.
- Decide: pick the hidden transformation from the options. The engine applies it to your query."""

_HELDOUT = f"""## World
A wrapping {GRID}x{GRID} grid. {N_CELLS} cells. You are one of them.

## What is hidden
For the length of an epoch, all cells face one secret rule that rewrites a 4-letter string (letters A to H). The rule is the same everywhere in the grid. What differs from cell to cell and from generation to generation is the evidence you hold (a couple of private before/after examples) and the string you are asked about. There is no common score; you are right if you give what the secret rule gives for your string.

## What you read
Your examples, your string, a note about your previous step, and eight inbox slots. A slot is empty unless another cell put a message there.

## What you may write
One message at most per generation (a signal from 0 to 7 plus the name of one transformation), or nothing. Messages arrive in later generations and only for cells that are allowed to see them. Your own rule choice and answer are never shown to others.

## Your decision
Select the secret rule from the listed options; the engine applies it to your string, and that is your answer."""

PARAPHRASES = {"p1": _P1, "p2": _P2, "p3": _P3, "heldout": _HELDOUT}


def render_state_lv(inst: InstanceLV) -> str:
    """Canonical = exact Life `render_state(obs, channel=True)`; others swap the constitution."""
    obs = _obs(inst)
    if inst.harness == "canonical":
        return render_state(obs, channel=True)
    try:
        constitution = PARAPHRASES[inst.harness]
    except KeyError:
        raise ValueError(f"unknown harness {inst.harness!r}") from None
    return constitution + "\n\n" + render_user(obs, True, "typed")


def render_receiver_lv(inst: InstanceLV) -> dict:
    """{state, question, options, labels}: options in catalog order, labels R000..R100.
    Hypothesis (jev_policy): The answer to "{question}" is {label}: {option}."""
    return {
        "state": render_state_lv(inst),
        "question": RULE_INSTRUCTIONS,
        "options": list(_DESC),
        "labels": [rule_key(i) for i in range(N_OPTIONS)],
    }


# ------------------------------------------------------------------ reference policies (numpy, no model)

def _onehot(i: int) -> np.ndarray:
    p = np.zeros(N_OPTIONS)
    p[i] = 1.0
    return p


def solo_oracle_lv(inst: InstanceLV) -> np.ndarray:
    """A solo cell that knows E: puts all mass on the correct f (the solo ceiling)."""
    return _onehot(inst.function_index)


def consistent_named(inst: InstanceLV) -> list[int]:
    """Rendered named rules (distinct, slot order) consistent with E."""
    H = {_PID_TO_IDX[h.program_id] for h in hypothesis_set([tuple(e) for e in inst.examples], _CAT)}
    seen: list[int] = []
    for i in effective_named_indices(inst):
        if i in H and i not in seen:
            seen.append(i)
    return seen


def oracle_verifier_lv(inst: InstanceLV, solo_fn: Callable[[InstanceLV], np.ndarray] | None = None) -> np.ndarray:
    """A named rule consistent with E if any (unique by construction), else solo."""
    ok = consistent_named(inst)
    if ok:
        return _onehot(ok[0])
    return (solo_fn or solo_oracle_lv)(empty_variant(inst) if solo_fn else inst)


def credulous_mode_lv(inst: InstanceLV, solo_fn: Callable[[InstanceLV], np.ndarray] | None = None) -> np.ndarray:
    """The most frequent *rendered* named rule (ties split uniformly, C2); empty -> solo."""
    names = effective_named_indices(inst)
    if not names:
        return (solo_fn or solo_oracle_lv)(empty_variant(inst) if solo_fn else inst)
    cnt = Counter(names)
    top = max(cnt.values())
    p = np.zeros(N_OPTIONS)
    modes = [i for i, c in cnt.items() if c == top]
    for i in modes:
        p[i] = 1.0 / len(modes)
    return p


# ------------------------------------------------------------------ metrics

def _unique_argmax(p: np.ndarray) -> int | None:
    """Index of the unique maximum, or None if there is a tie at the top."""
    top = np.flatnonzero(np.isclose(p, p.max()))
    return int(top[0]) if len(top) == 1 else None


def _rec(inst: InstanceLV, p: np.ndarray) -> dict:
    p = np.asarray(p, dtype=float)
    f = inst.function_index
    # Metrics follow the rendered inbox (cross-epoch → previous-epoch rule = false).
    names = list(effective_named_indices(inst))
    name_set = set(names)
    false_names = name_set - {f}
    choice = _unique_argmax(p)
    # Choice probes: unique top equals the named target (f or a false name).
    choice_f = 1.0 if choice == f else 0.0
    choice_false = 1.0 if (choice is not None and choice in false_names) else 0.0
    # Binary named preference (AMENDMENT_L_VERIFY_PAIR_BINARY) — only meaningful for pair.
    g = next(iter(false_names)) if len(false_names) == 1 else None
    pi_f = float(p[f])
    pi_g = float(p[g]) if g is not None else float("nan")
    if g is not None:
        if pi_f > pi_g:
            pref_choice = 1.0
        elif pi_f < pi_g:
            pref_choice = 0.0
        else:
            pref_choice = 0.5
        denom = pi_f + pi_g
        pref_mass = (pi_f / denom) if denom > 0 else 0.5
        off_named = 1.0 if (choice is not None and choice not in {f, g}) else 0.0
    else:
        pref_choice = float("nan")
        pref_mass = float("nan")
        off_named = float("nan")
    return {
        "type": inst.inbox_type,
        "n_ops": inst.n_ops,
        "harness": inst.harness,
        "pi_f": pi_f,
        "pi_g": pi_g,
        # mass on the (distinct) false names; for a single false name this is pi(g)
        "pi_false": float(sum(p[j] for j in false_names)),
        "n_false_names": len(false_names),
        "choice_f": choice_f,
        "choice_false": choice_false,
        # for one-false false_only: unique top equals that g
        "choice_g": (
            1.0 if (len(false_names) == 1 and choice is not None
                    and choice == next(iter(false_names)))
            else 0.0
        ),
        "pair_pref_choice": pref_choice,
        "pair_pref_mass": pref_mass,
        "pair_off_named_choice": off_named,
    }


def _mean(xs) -> float:
    xs = list(xs)
    return float(np.mean(xs)) if xs else float("nan")


def _aggregate(recs: list[dict]) -> dict:
    by_t = {t: [r for r in recs if r["type"] == t] for t in INBOX_TYPES}
    acc_type = {t: _mean(r["pi_f"] for r in rs) for t, rs in by_t.items()}
    acc_type_choice = {t: _mean(r["choice_f"] for r in rs) for t, rs in by_t.items()}
    one_false = [r for r in by_t["false_only"] if r["n_false_names"] == 1]
    true_only = _mean(r["pi_f"] for r in by_t["true_only"])
    one_false_mass = _mean(r["pi_false"] for r in one_false)
    true_only_ch = _mean(r["choice_f"] for r in by_t["true_only"])
    one_false_ch = _mean(r["choice_g"] for r in one_false)
    return {
        "n": len(recs),
        # Mass (π) and choice (unique argmax) side by side — transfer lesson 2026-10-04.
        "acc": _mean(r["pi_f"] for r in recs),
        "acc_choice": _mean(r["choice_f"] for r in recs),
        "acc_type": acc_type,
        "acc_type_choice": acc_type_choice,
        "n_type": {t: len(rs) for t, rs in by_t.items()},
        # Catalog accuracy on true+false once (101-way; chance ≠ 0.5).
        "pair_acc": acc_type["pair"],
        "pair_acc_choice": acc_type_choice["pair"],
        # Primary discrimination (AMENDMENT_L_VERIFY_PAIR_BINARY): among the two names.
        "pair_pref_mass": _mean(r["pair_pref_mass"] for r in by_t["pair"]),
        "pair_pref_choice": _mean(r["pair_pref_choice"] for r in by_t["pair"]),
        "pair_off_named_choice": _mean(r["pair_off_named_choice"] for r in by_t["pair"]),
        # Secondary: lone true vs lone false — weak reject incentive on false_only.
        "delta_named": true_only - one_false_mass,
        "delta_named_choice": true_only_ch - one_false_ch,
        "follow_false": _mean(r["pi_false"] for r in by_t["false_only"]),
        "follow_false_choice": _mean(r["choice_false"] for r in by_t["false_only"]),
        "minority_true": acc_type["true_false_maj"],
        "minority_true_choice": acc_type_choice["true_false_maj"],
        "solo_retained": acc_type["empty"],
        "solo_retained_choice": acc_type_choice["empty"],
    }


HARNESS_GAP_METRICS = (
    "pair_pref_mass", "pair_pref_choice",
    "pair_acc", "pair_acc_choice",
    "delta_named", "delta_named_choice",
    "minority_true", "follow_false",
    "minority_true_choice", "follow_false_choice",
)


def evaluate_lv(
    insts: list[InstanceLV],
    policy_fn: Callable[[InstanceLV], np.ndarray],
    *,
    return_rows: bool = False,
) -> dict:
    """policy_fn(inst) -> pi [101]. Overall metrics plus splits by n_ops and by harness.

    Primary pair discrimination: `pair_pref_choice` / `pair_pref_mass`
    (AMENDMENT_L_VERIFY_PAIR_BINARY). `pair_acc[_choice]` = 101-way catalog accuracy.
    `harness_gap` when both canonical and heldout are present.
    """
    recs = [_rec(inst, policy_fn(inst)) for inst in insts]
    out = _aggregate(recs)
    out["by_n_ops"] = {str(k): _aggregate([r for r in recs if r["n_ops"] == k])
                       for k in sorted({r["n_ops"] for r in recs})}
    out["by_harness"] = {h: _aggregate([r for r in recs if r["harness"] == h])
                         for h in ALL_HARNESSES if any(r["harness"] == h for r in recs)}
    bh = out["by_harness"]
    if "canonical" in bh and "heldout" in bh:
        out["harness_gap"] = {m: abs(bh["canonical"][m] - bh["heldout"][m]) for m in HARNESS_GAP_METRICS}
    if return_rows:
        # Compact rows for CPU recompute of preference metrics (no full π vector).
        out["rows"] = [
            {
                "id": inst.id,
                "n_ops": r["n_ops"],
                "type": r["type"],
                "pi_f": r["pi_f"],
                "pi_g": r["pi_g"],
                "pair_pref_choice": r["pair_pref_choice"],
                "pair_pref_mass": r["pair_pref_mass"],
                "pair_off_named_choice": r["pair_off_named_choice"],
                "choice_f": r["choice_f"],
            }
            for inst, r in zip(insts, recs)
        ]
    return out


def ladder_lv(insts: list[InstanceLV], solo_fn: Callable[[InstanceLV], np.ndarray] | None = None) -> dict:
    """solo / credulous_mode / oracle_verifier on the same instances.

    solo_fn=None: oracle solo (one-hot on f) — the model-free ladder used in acceptance tests.
    solo_fn=model policy: solo is the model's own distribution under an empty inbox.
    """
    def solo(inst):
        e = empty_variant(inst)
        return (solo_fn or solo_oracle_lv)(e if solo_fn else inst)

    rows = {
        "solo": solo,
        "credulous_mode": lambda i: credulous_mode_lv(i, solo_fn),
        "oracle_verifier": lambda i: oracle_verifier_lv(i, solo_fn),
    }
    return {name: evaluate_lv(insts, fn) for name, fn in rows.items()}

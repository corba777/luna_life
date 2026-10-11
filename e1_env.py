"""
E1 — Reference game (Stage 1 spec v4.1, Section 2).

Generator, validation battery (information value, leakage, counterfactual pairs,
symbol disjointness) and exact metric utilities (CFI, selectivity, sender MI).

Policy interfaces (a real model wrapper maps option letters back through `perm`):
    sender_policy(inst, perm_idx)        -> (p_slot1, p_slot2), arrays over family vocab (canonical order)
    receiver_policy(inst, msg, perm_idx) -> array over inst.items (canonical order)

All logs are natural; JS divergence is bounded by log 2 ≈ 0.693.

P (number of paired option orderings) has no default and must be passed explicitly:
P = 1 for order-invariant Jev scoring, P = 4 for letter-readout LLM arms (spec v4.2).
"""
from __future__ import annotations

import contextlib
import hashlib
import itertools
import json
import math
import string
from dataclasses import dataclass, replace, asdict
from typing import Callable, Sequence

import numpy as np

# ---------------------------------------------------------------- vocabularies

FAMILIES = {
    "train": {
        "shape": ["round", "square", "triangular", "oval"],
        "color": ["red", "blue", "green", "yellow"],
        "material": ["wooden", "metal", "glass"],
    },
    "relabel": {  # E1-relabel: disjoint vocabulary, used only for held-out eval
        "shape": ["hexagonal", "crescent", "diamond", "star-shaped"],
        "color": ["purple", "orange", "black", "white"],
        "material": ["stone", "paper", "plastic"],
    },
}
ATTRS = ("shape", "color", "material")

NUISANCE = [  # z_nuis: equally salient, never bears on the optimal action
    "The room is cold.",
    "It is raining outside.",
    "A clock is ticking loudly.",
    "The lights are dim.",
    "Someone is whistling nearby.",
    "The window is open.",
    "There is a smell of coffee.",
    "The floor creaks.",
]

LABELS = string.ascii_uppercase + string.ascii_lowercase  # 52, as in OpenJev


def family_vocab(family: str) -> list[str]:
    """Message vocabulary V_m: all attribute values of the family, canonical order."""
    f = FAMILIES[family]
    return [v for a in ATTRS for v in f[a]]


# ---------------------------------------------------------------- instances

@dataclass(frozen=True)
class Instance:
    id: str
    family: str
    K: int
    items: tuple[tuple[str, str, str], ...]  # canonical order; (shape, color, material)
    target: int                              # z_rel: index into items
    nuisance: int                            # z_nuis: index into NUISANCE
    seed: int                                # drives option permutations (shared by counterfactuals)


def describe(item: Sequence[str]) -> str:
    shape, color, material = item
    return f"{color} {shape} {material} object"


def identifying_pairs(items, i) -> list[tuple[str, str]]:
    """Pairs of item i's attribute values that no other item shares."""
    out = []
    for a, b in itertools.combinations(range(3), 2):
        key = (items[i][a], items[i][b])
        if not any((items[j][a], items[j][b]) == key for j in range(len(items)) if j != i):
            out.append(key)
    return out


def all_pair_identifiable(items) -> bool:
    # Required for EVERY item, not just the target: otherwise "the target is one of the
    # identifiable items" would leak z_rel into the receiver's observation.
    return all(identifying_pairs(items, i) for i in range(len(items)))


def sample_instance(rng: np.random.Generator, family: str, K: int, idx: int,
                    *, gen_seed: int) -> Instance:
    f = FAMILIES[family]
    universe = list(itertools.product(f["shape"], f["color"], f["material"]))
    for _ in range(10_000):
        pick = rng.choice(len(universe), size=K, replace=False)
        items = tuple(universe[p] for p in pick)
        if all_pair_identifiable(items):
            break
    else:
        raise RuntimeError(f"no pair-identifiable item set for {family}, K={K}")
    target = int(rng.integers(K))              # independent of the item set
    nuisance = int(rng.integers(len(NUISANCE)))
    seed = int(rng.integers(2**31))
    # Include gen_seed so train (seed=1000+s) and val (seed=2000+s) never share ids.
    return Instance(
        f"{family}-s{gen_seed}-K{K}-{idx:05d}", family, K, items, target, nuisance, seed,
    )


def generate(n: int, family: str, Ks: Sequence[int], seed: int) -> list[Instance]:
    rng = np.random.default_rng(seed)
    return [sample_instance(rng, family, int(rng.choice(Ks)), i, gen_seed=seed)
            for i in range(n)]


def instance_content_key(inst: Instance) -> str:
    """Stable cache key: family + items + target + nuisance (not inst.id)."""
    return f"{inst.family}|{repr(inst.items)}|t{inst.target}|n{inst.nuisance}"


def instance_hp_content_key(inst: "InstanceHP") -> str:
    """Stable cache key for E-HP (not inst.id)."""
    def fact_k(f):
        if isinstance(f, AdditiveHP):
            return ("A", f.option, f.word, f.weight)
        return ("M", f.option, f.dim, f.value)
    return repr((
        inst.family, inst.kind, inst.consensus, inst.correct, inst.holder,
        (inst.requirement.dim, inst.requirement.bound),
        tuple(fact_k(f) for f in inst.shared),
        tuple(tuple(fact_k(f) for f in bag) for bag in inst.private),
    ))


def reward(inst: Instance, action: int) -> float:
    return float(action == inst.target)


def optimal_action(inst: Instance) -> int:
    return inst.target


# ---------------------------------------------------------------- counterfactual pairs

def rel_counterfactual(inst: Instance, rng) -> Instance:
    t = int(rng.choice([k for k in range(inst.K) if k != inst.target]))
    return replace(inst, target=t, id=inst.id + f"-rel{t}")


def nuis_counterfactual(inst: Instance, rng) -> Instance:
    n = int(rng.choice([k for k in range(len(NUISANCE)) if k != inst.nuisance]))
    return replace(inst, nuisance=n, id=inst.id + f"-nuis{n}")


# ---------------------------------------------------------------- rendering (paired permutations)

def _perm(inst: Instance, perm_idx: int, stream: int, n: int) -> np.ndarray:
    """Deterministic in (inst.seed, perm_idx, stream): identical for z and z'."""
    return np.random.default_rng([inst.seed, perm_idx, stream]).permutation(n)


def render_sender(inst: Instance, perm_idx: int) -> list[dict]:
    vocab = family_vocab(inst.family)
    item_lines = "\n".join(f"- {describe(it)}" for it in inst.items)
    state = (
        "You are the SENDER in a two-player game.\n"
        f"Items on the table:\n{item_lines}\n"
        f"The target item is: {describe(inst.items[inst.target])}.\n"
        f"{NUISANCE[inst.nuisance]}\n"
        "Your partner sees the same items but not which one is the target. "
        "You may send exactly two words from this list: " + ", ".join(vocab) + "."
    )
    qs = []
    for slot in (1, 2):
        p = _perm(inst, perm_idx, stream=slot, n=len(vocab))
        qs.append({
            "state": state,
            "question": f"Choose word {slot} of your message.",
            "options": [{"label": LABELS[k], "value": vocab[p[k]], "canonical": int(p[k])}
                        for k in range(len(vocab))],
        })
    return qs


def render_receiver(inst: Instance, msg: tuple[str, str], perm_idx: int) -> dict:
    p = _perm(inst, perm_idx, stream=0, n=inst.K)
    item_lines = "\n".join(f"- {describe(inst.items[p[k]])}" for k in range(inst.K))
    state = (
        "You are the RECEIVER in a two-player game.\n"
        f"Items on the table:\n{item_lines}\n"
        "Your partner knows which item is the target. They could send any two words from: "
        + ", ".join(family_vocab(inst.family)) + ".\n"
        "Their message: "
        f"\"{msg[0]} {msg[1]}\"."
    )
    return {
        "state": state,
        "question": "Which item is the target?",
        "options": [{"label": LABELS[k], "value": describe(inst.items[p[k]]), "canonical": int(p[k])}
                    for k in range(inst.K)],
    }


def scripted_message(inst: Instance, rng: np.random.Generator) -> tuple[str, str]:
    """M_single partner (spec v4.1, Section 4): fixed, non-learning sender.
    Sends a uniformly random identifying pair of the target, in random word order,
    so the trained receiver cannot learn a single fixed code. Ignores z_nuis."""
    pairs = identifying_pairs(inst.items, inst.target)
    a, b = pairs[int(rng.integers(len(pairs)))]
    return (a, b) if rng.random() < 0.5 else (b, a)


# ---------------------------------------------------------------- exact metrics

def js(p: np.ndarray, q: np.ndarray) -> float:
    m = 0.5 * (p + q)
    def kl(a, b):
        mask = a > 0
        return float(np.sum(a[mask] * np.log(a[mask] / b[mask])))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def receiver_marginal(inst, sender_policy, receiver_policy, perm_idx, eps=1e-9) -> np.ndarray:
    """π_R(a | do(z)) = Σ_m π_S(m|z) π_R(a|m), exact over the V_m^2 message pairs."""
    vocab = family_vocab(inst.family)
    p1, p2 = sender_policy(inst, perm_idx)
    out = np.zeros(inst.K)
    for i, j in itertools.product(range(len(vocab)), repeat=2):
        w = p1[i] * p2[j]
        if w > eps:
            out += w * receiver_policy(inst, (vocab[i], vocab[j]), perm_idx)
    return out / out.sum()


def expected_reward(inst, sender_policy, receiver_policy, perm_idx=0) -> float:
    return float(receiver_marginal(inst, sender_policy, receiver_policy, perm_idx)[inst.target])


def cfi(insts, sender_policy, receiver_policy, *, P: int, seed=0) -> dict:
    """End-to-end CFI_rel, CFI_nuis, selectivity. Exact per ordering, mean over P paired orderings."""
    rng = np.random.default_rng(seed)
    rel, nuis = [], []
    for inst in insts:
        ir, inn = rel_counterfactual(inst, rng), nuis_counterfactual(inst, rng)
        for k in range(P):
            base = receiver_marginal(inst, sender_policy, receiver_policy, k)
            rel.append(js(base, receiver_marginal(ir, sender_policy, receiver_policy, k)))
            nuis.append(js(base, receiver_marginal(inn, sender_policy, receiver_policy, k)))
    r, n = float(np.mean(rel)), float(np.mean(nuis))
    return {"CFI_rel": r, "CFI_nuis": n, "Selectivity": r - n}


def sender_mi(insts, sender_policy, *, P: int) -> dict:
    """Exact I(z_rel; m) and I(z_nuis; m) under uniform priors, per instance, averaged."""
    def mi(variants, k):
        dists = []
        for v in variants:
            p1, p2 = sender_policy(v, k)
            dists.append(np.outer(p1, p2).ravel())
        dists = np.array(dists)
        return entropy(dists.mean(0)) - float(np.mean([entropy(d) for d in dists]))
    rel, nuis = [], []
    for inst in insts:
        vr = [replace(inst, target=t) for t in range(inst.K)]
        vn = [replace(inst, nuisance=n) for n in range(len(NUISANCE))]
        for k in range(P):
            rel.append(mi(vr, k))
            nuis.append(mi(vn, k))
    r, n = float(np.mean(rel)), float(np.mean(nuis))
    return {"I_rel": r, "I_nuis": n, "SenderSel": r - n}


def receiver_sel(insts, receiver_policy, *, P: int, seed=0) -> dict:
    """do(m) at fixed receiver history.
    Relevant: identifying message for target vs for another item.
    Irrelevant: two different identifying messages for the SAME target (semantically equivalent).
    Items with a single identifying pair contribute only to the relevant term.

    Non-saturating (v4.4): R_logp_correct, R_logp_equiv_gap — usable when JS saturates.
    """
    rng = np.random.default_rng(seed)
    rel, irr = [], []
    logp_correct, logp_equiv_gap = [], []
    for inst in insts:
        other = int(rng.choice([k for k in range(inst.K) if k != inst.target]))
        m_t = identifying_pairs(inst.items, inst.target)
        m_o = identifying_pairs(inst.items, other)
        for k in range(P):
            a = receiver_policy(inst, m_t[0], k)
            rel.append(js(a, receiver_policy(inst, m_o[0], k)))
            p0 = float(np.clip(a[inst.target], 1e-12, 1.0))
            logp_correct.append(math.log(p0))
            if len(m_t) > 1:
                b = receiver_policy(inst, m_t[1], k)
                irr.append(js(a, b))
                p1 = float(np.clip(b[inst.target], 1e-12, 1.0))
                logp_equiv_gap.append(abs(math.log(p0) - math.log(p1)))
    r = float(np.mean(rel)); i = float(np.mean(irr)) if irr else float("nan")
    return {
        "R_rel": r, "R_equiv": i, "ReceiverSel": r - i, "n_equiv_pairs": len(irr),
        "R_logp_correct": float(np.mean(logp_correct)),
        "R_logp_equiv_gap": float(np.mean(logp_equiv_gap)) if logp_equiv_gap else float("nan"),
    }

# ---------------------------------------------------------------- scripted reference policies

def _onehot(n, i):
    v = np.zeros(n); v[i] = 1.0; return v


def perfect_sender(inst, k):
    vocab = family_vocab(inst.family)
    a, b = identifying_pairs(inst.items, inst.target)[0]
    return _onehot(len(vocab), vocab.index(a)), _onehot(len(vocab), vocab.index(b))


def leaky_sender(inst, k):
    """Correct, but picks WHICH identifying pair from the nuisance: I(z_nuis; m) > 0."""
    vocab = family_vocab(inst.family)
    pairs = identifying_pairs(inst.items, inst.target)
    a, b = pairs[inst.nuisance % len(pairs)]
    return _onehot(len(vocab), vocab.index(a)), _onehot(len(vocab), vocab.index(b))


def uniform_sender(inst, k):
    n = len(family_vocab(inst.family)); return np.full(n, 1 / n), np.full(n, 1 / n)


def literal_receiver(inst, msg, k):
    """Uniform over items carrying every word of the message; uniform over all if none."""
    c = np.array([all(w in it for w in msg) for it in inst.items], dtype=float)
    return c / c.sum() if c.sum() else np.full(inst.K, 1 / inst.K)


def first_word_receiver(inst, msg, k):
    """Reads only word 1: sensitive to which (equivalent) pair was sent."""
    return literal_receiver(inst, (msg[0], msg[0]), k)


def uniform_receiver(inst, msg, k):
    return np.full(inst.K, 1 / inst.K)


# ---------------------------------------------------------------- validation battery

def check_disjointness(family: str) -> list[str]:
    bad = [v for v in family_vocab(family)
           if v in set(string.ascii_letters) or v in set(string.digits)
           or (len(v) <= 2 and v.upper() in LABELS)]
    return bad


def leakage_battery(insts) -> dict:
    """Receiver-side cheaters without z. All must sit at chance (mean 1/K)."""
    def rarest(inst):
        counts = {}
        for it in inst.items:
            for v in it: counts[v] = counts.get(v, 0) + 1
        return int(np.argmin([sum(counts[v] for v in it) for it in inst.items]))
    def most_pairs(inst):
        return int(np.argmax([len(identifying_pairs(inst.items, i)) for i in range(inst.K)]))
    cheaters = {
        "first_canonical": lambda inst: 0,
        "first_option_perm0": lambda inst: int(_perm(inst, 0, 0, inst.K)[0]),
        "rarest_values": rarest,
        "most_identifying_pairs": most_pairs,
    }
    chance = float(np.mean([1 / i.K for i in insts]))
    n = len(insts)
    se = float(np.sqrt(chance * (1 - chance) / n))
    res = {"chance": chance, "se": se}
    for name, f in cheaters.items():
        acc = float(np.mean([reward(i, f(i)) for i in insts]))
        res[name] = {"acc": acc, "z": (acc - chance) / se}
    return res


def validate(insts, label: str) -> dict:
    rng = np.random.default_rng(123)
    # information value: oracle with z vs best receiver without z
    v_priv = float(np.mean([1 - 1 / i.K for i in insts]))
    oracle = float(np.mean([reward(i, optimal_action(i)) for i in insts]))
    # counterfactual pairs are verified here, not assumed
    rel_ok = all(optimal_action(rel_counterfactual(i, rng)) != optimal_action(i) for i in insts)
    nuis_ok = all(optimal_action(nuis_counterfactual(i, rng)) == optimal_action(i) for i in insts)
    ident_ok = all(all_pair_identifiable(i.items) for i in insts)
    return {
        "set": label, "n": len(insts),
        "K_counts": {int(k): int(sum(i.K == k for i in insts)) for k in sorted({i.K for i in insts})},
        "V_priv": v_priv, "oracle_reward": oracle,
        "rel_counterfactuals_change_optimum": rel_ok,
        "nuis_counterfactuals_keep_optimum": nuis_ok,
        "all_items_pair_identifiable": ident_ok,
        "symbol_violations": check_disjointness(insts[0].family),
        "leakage": leakage_battery(insts),
    }



# ================================================================= E1-P (one-word, v4.4)
# Public names suffixed _p. Merge of the standalone reference; do not import e1p_env.

def truth_p(inst: Instance) -> np.ndarray:
    """T[i, w] = 1 if word w is true of item i."""
    vocab = family_vocab(inst.family)
    return np.array([[float(w in it) for w in vocab] for it in inst.items])


def S0_p(inst):  # [K, V]
    T = truth_p(inst)
    return T / T.sum(1, keepdims=True)


def L0_p(inst):  # [V, K]; words true of nothing -> uniform
    T = truth_p(inst).T
    s = T.sum(1, keepdims=True)
    return np.where(s > 0, T / np.maximum(s, 1), 1.0 / inst.K)


def S1_p(inst):  # [K, V]: informative speaker, argmax_w L0(t|w) over true words
    T, L = truth_p(inst), L0_p(inst).T  # L[i, w] = L0(i|w)
    out = np.zeros_like(T)
    for t in range(inst.K):
        sc = np.where(T[t] > 0, L[t], -1.0)
        best = np.isclose(sc, sc.max())
        out[t] = best / best.sum()
    return out


def L2_p(inst):  # [V, K]: posterior under S1
    P = S1_p(inst).T
    s = P.sum(1, keepdims=True)
    return np.where(s > 0, P / np.maximum(s, 1e-12), L0_p(inst))


def reward_pair_p(inst, S, L) -> float:
    """Team reward of speaker S [K,V] with receiver argmax of L [V,K] (uniform over ties)."""
    r = 0.0
    for t in range(inst.K):
        for w in np.nonzero(S[t])[0]:
            best = np.flatnonzero(np.isclose(L[w], L[w].max()))
            r += S[t, w] * (1.0 / len(best) if t in best else 0.0)
    return r / inst.K


def max_matching_p(T: np.ndarray) -> tuple[int, dict]:
    """Bipartite matching items->words over edges T[i,w]=1 (augmenting paths)."""
    K, V = T.shape
    word_of, item_of = {}, {}

    def augment(i, seen):
        for w in np.nonzero(T[i])[0]:
            if w in seen:
                continue
            seen.add(w)
            if w not in item_of or augment(item_of[w], seen):
                item_of[w], word_of[i] = i, w
                return True
        return False

    size = sum(augment(i, set()) for i in range(K))
    return size, word_of


def references_p(inst) -> dict:
    """Exact ladder per instance. gap = R_truth - R_S0L0 (set-level filter uses this)."""
    size, _ = max_matching_p(truth_p(inst))
    L0m = L0_p(inst)
    r_s0l0 = float(np.mean([S0_p(inst)[t] @ L0m[:, t] for t in range(inst.K)]))
    r_truth = size / inst.K
    return {
        "R_S0L0": r_s0l0,
        "R_S1L0": reward_pair_p(inst, S1_p(inst), L0_p(inst)),
        "R_S1L2": reward_pair_p(inst, S1_p(inst), L2_p(inst)),
        "R_truth": r_truth,
        "R_code": 1.0 if inst.K <= len(family_vocab(inst.family)) else float("nan"),
        "gap": r_truth - r_s0l0,
    }


def generate_p(n, family, Ks, seed, min_gap=0.15, max_tries=200_000):
    """Keep item sets with R_truth - R_S0L0 >= min_gap. Target/nuisance drawn after accept."""
    rng = np.random.default_rng(seed)
    f = FAMILIES[family]
    universe = [(s, c, m) for s in f["shape"] for c in f["color"] for m in f["material"]]
    out, tries = [], 0
    while len(out) < n:
        tries += 1
        if tries > max_tries:
            raise RuntimeError(f"only {len(out)} sets with gap >= {min_gap}")
        K = int(rng.choice(Ks))
        pick = rng.choice(len(universe), size=K, replace=False)
        items = tuple(universe[p] for p in pick)
        probe = Instance("probe", family, K, items, 0, 0, 0)
        if references_p(probe)["gap"] < min_gap:
            continue
        inst = Instance(
            f"p-{family}-s{seed}-K{K}-{len(out):05d}", family, K, items,
            int(rng.integers(K)), int(rng.integers(len(NUISANCE))), int(rng.integers(2**31)),
        )
        out.append(inst)
    return out, tries


def subset_beyond_gricean_p(insts, min_gap=0.15):
    return [i for i in insts if references_p(i)["R_truth"] - references_p(i)["R_S1L2"] >= min_gap]


# Prompt surface. Default = Stage-1 training/eval templates (frozen for all
# trained checkpoints). Named variants are *new conditions* for diagnostics
# only — never silently swap under trained models (see CLAUDE §11).
#   goal_explicit — cooperative goal stated (prompt-goal check)
#   ehp_v2a       — E-HP only: unknown req-status = meets; requirement partner-known
PROMPT_VARIANT = "default"  # "default" | "goal_explicit" | "ehp_v2a"

_PROMPT_VARIANTS = ("default", "goal_explicit", "ehp_v2a")

# E-HP *environment* variant (generator). Separate from prompt surface.
#   default — v2 as trained for P6 (non-holder has satisfying req measurement of 1−c)
#   b       — Variant B: non-holder has no req measurement; two other-dim measurements
EHP_VARIANT = "default"  # "default" | "b"
_EHP_VARIANTS = ("default", "b")


@contextlib.contextmanager
def prompt_variant(name: str):
    global PROMPT_VARIANT
    if name not in _PROMPT_VARIANTS:
        raise ValueError(f"unknown prompt variant: {name}")
    old = PROMPT_VARIANT
    PROMPT_VARIANT = name
    try:
        yield
    finally:
        PROMPT_VARIANT = old


@contextlib.contextmanager
def ehp_variant(name: str):
    """Switch E-HP generator structure (default vs B). Does not change prompts."""
    global EHP_VARIANT
    if name not in _EHP_VARIANTS:
        raise ValueError(f"unknown ehp variant: {name}")
    old = EHP_VARIANT
    EHP_VARIANT = name
    try:
        yield
    finally:
        EHP_VARIANT = old


def render_sender_p(inst: Instance) -> dict:
    vocab = family_vocab(inst.family)
    item_lines = "\n".join(f"- {describe(it)}" for it in inst.items)
    if PROMPT_VARIANT == "goal_explicit":
        state = (
            "You are the SENDER in a cooperative two-player game. "
            "You and your partner share one team reward: you succeed only if "
            "your partner picks the target item.\n"
            f"Items on the table:\n{item_lines}\n"
            f"The target item is: {describe(inst.items[inst.target])}.\n"
            f"{NUISANCE[inst.nuisance]}\n"
            "Your partner sees the same items but not which one is the target. "
            "Send exactly ONE word from this list to help them identify the "
            "target (prefer a word that rules out alternatives when possible): "
            + ", ".join(vocab) + "."
        )
        question = "Choose the word that best helps your partner identify the target."
    else:
        state = (
            "You are the SENDER in a two-player game.\n"
            f"Items on the table:\n{item_lines}\n"
            f"The target item is: {describe(inst.items[inst.target])}.\n"
            f"{NUISANCE[inst.nuisance]}\n"
            "Your partner sees the same items but not which one is the target. "
            "You may send exactly ONE word from this list: " + ", ".join(vocab) + "."
        )
        question = "Choose the word to send."
    return {"state": state, "question": question, "options": vocab}


def render_receiver_p(inst: Instance, w: str) -> dict:
    vocab = family_vocab(inst.family)
    item_lines = "\n".join(f"- {describe(it)}" for it in inst.items)
    if PROMPT_VARIANT == "goal_explicit":
        state = (
            "You are the RECEIVER in a cooperative two-player game. "
            "You and your partner share one team reward: you succeed only if "
            "you pick the target item.\n"
            f"Items on the table:\n{item_lines}\n"
            "Your partner knows which item is the target and chose ONE word "
            "from the list below intending to help you find it: "
            + ", ".join(vocab) + ".\n"
            f"Their message: \"{w}\"."
        )
    else:
        state = (
            "You are the RECEIVER in a two-player game.\n"
            f"Items on the table:\n{item_lines}\n"
            "Your partner knows which item is the target. They could send any ONE word from: "
            + ", ".join(vocab) + ".\n"
            f"Their message: \"{w}\"."
        )
    return {
        "state": state,
        "question": "Which item is the target?",
        "options": [describe(it) for it in inst.items],
    }


def receiver_marginal_p(inst, sp, rp):
    vocab = family_vocab(inst.family)
    p = sp(inst)
    out = np.zeros(inst.K)
    for j, w in enumerate(vocab):
        if p[j] > 1e-9:
            out += p[j] * rp(inst, w)
    return out / out.sum()


def expected_reward_p(inst, sp, rp):
    return float(receiver_marginal_p(inst, sp, rp)[inst.target])


def cfi_p(insts, sp, rp, seed=0):
    rng = np.random.default_rng(seed)
    rel, nuis = [], []
    for inst in insts:
        base = receiver_marginal_p(inst, sp, rp)
        rel.append(js(base, receiver_marginal_p(rel_counterfactual(inst, rng), sp, rp)))
        nuis.append(js(base, receiver_marginal_p(nuis_counterfactual(inst, rng), sp, rp)))
    r, n = float(np.mean(rel)), float(np.mean(nuis))
    return {"CFI_rel": r, "CFI_nuis": n, "Selectivity": r - n}


def sender_mi_p(insts, sp):
    def mi(variants):
        d = np.array([sp(v) for v in variants])
        return entropy(d.mean(0)) - float(np.mean([entropy(x) for x in d]))
    rel = [mi([replace(i, target=t) for t in range(i.K)]) for i in insts]
    nuis = [mi([replace(i, nuisance=n) for n in range(len(NUISANCE))]) for i in insts]
    return {"I_rel": float(np.mean(rel)), "I_nuis": float(np.mean(nuis)),
            "SenderSel": float(np.mean(rel) - np.mean(nuis))}


def tie_split_argmax(p) -> np.ndarray:
    """C2: uniform mass over tied argmax entries (np.isclose defaults)."""
    p = np.asarray(p, float)
    b = np.isclose(p, p.max()).astype(float)
    return b / b.sum()


def pragmatic_index_p(insts, rp):
    """L0 = -1, L2 = +1 over words where they differ (JS-based)."""
    vals = []
    for inst in insts:
        vocab, l0, l2 = family_vocab(inst.family), L0_p(inst), L2_p(inst)
        T = truth_p(inst)
        for j, w in enumerate(vocab):
            if T[:, j].sum() == 0 or np.allclose(l0[j], l2[j]):
                continue
            p = rp(inst, w)
            d0, d2 = js(p, l0[j]), js(p, l2[j])
            if d0 + d2 > 0:
                vals.append((d0 - d2) / (d0 + d2))
    return {"pragmatic_index": float(np.mean(vals)) if vals else float("nan"), "n_words": len(vals)}


def pragmatic_argmax_agree_p(insts, rp):
    """Calibration-free companion to pragmatic_index (METRICS §3).

    On E1-P, L0 is flat on the word's support and L2 concentrates on a unique
    item inside that support — so tops always *intersect*. Restrict to words
    where L0 ≠ L2 and L2's top is a **proper subset** of L0's top (always true
    on our sets when L0≠L2). Score set-equality of the model's C2 top with
    L2's singleton (`pragmatic_argmax_L2`) or with L0's full support
    (`pragmatic_argmax_L0` = fully literal-flat). Soft JS can rise from sharper
    π alone; exact top-set match cannot.
    """
    hit_l2 = hit_l0 = n = 0
    for inst in insts:
        vocab, l0, l2 = family_vocab(inst.family), L0_p(inst), L2_p(inst)
        T = truth_p(inst)
        for j, w in enumerate(vocab):
            if T[:, j].sum() == 0 or np.allclose(l0[j], l2[j]):
                continue
            top_l0 = set(np.flatnonzero(np.isclose(l0[j], l0[j].max())).tolist())
            top_l2 = set(np.flatnonzero(np.isclose(l2[j], l2[j].max())).tolist())
            if not (len(top_l2) == 1 and top_l2 < top_l0):
                continue
            p = np.asarray(rp(inst, w), float)
            top = set(np.flatnonzero(np.isclose(p, p.max())).tolist())
            n += 1
            if top == top_l2:
                hit_l2 += 1
            if top == top_l0:
                hit_l0 += 1
    if n == 0:
        nan = float("nan")
        return {"pragmatic_argmax_L2": nan, "pragmatic_argmax_L0": nan,
                "pragmatic_argmax_gap": nan, "n_words": 0}
    return {
        "pragmatic_argmax_L2": hit_l2 / n,
        "pragmatic_argmax_L0": hit_l0 / n,
        "pragmatic_argmax_gap": (hit_l2 - hit_l0) / n,
        "n_words": n,
    }


def _speaker_index_vals(insts, sp):
    vals = []
    for inst in insts:
        for t in range(inst.K):
            x = replace(inst, target=t)
            l0t = L0_p(x)[:, t]
            e = np.asarray(sp(x), float) @ l0t
            e0, e1 = S0_p(x)[t] @ l0t, S1_p(x)[t] @ l0t
            if e1 - e0 > 1e-9:
                vals.append((e - e0) / (e1 - e0))
    return vals


def speaker_index_p(insts, sp):
    """Sender informativeness rescaled so S0 = 0 and S1 = 1 (mass-based primary)."""
    vals = _speaker_index_vals(insts, sp)
    return {"speaker_index": float(np.mean(vals)) if vals else float("nan")}


def speaker_index_argmax_p(insts, sp):
    """Same as speaker_index_p but with C2 tie-split argmax of π_S."""
    vals = _speaker_index_vals(insts, lambda x: tie_split_argmax(sp(x)))
    return {"speaker_index_argmax": float(np.mean(vals)) if vals else float("nan")}


def expected_reward_all_p(inst, sp, rp) -> float:
    """R^all: mean over all targets of the same item set (uniform prior)."""
    return float(np.mean([
        expected_reward_p(replace(inst, target=t), sp, rp) for t in range(inst.K)
    ]))


def speaker_ceiling_p(inst, sp) -> float:
    """C(π_S): oracle posterior-argmax listener under uniform prior (METRICS §3)."""
    V = len(family_vocab(inst.family))
    P = np.array([np.asarray(sp(replace(inst, target=t)), float) for t in range(inst.K)])
    r = 0.0
    for t in range(inst.K):
        for w in range(V):
            pw = float(P[t, w])
            if pw < 1e-15:
                continue
            col = P[:, w]
            A = np.flatnonzero(np.isclose(col, col.max()))
            r += pw * (1.0 / len(A) if t in A else 0.0)
    return r / inst.K


def listener_efficiency_p(inst, sp, rp) -> float:
    """η = R^all(π_S, π_R) / C(π_S)."""
    c = speaker_ceiling_p(inst, sp)
    if c <= 1e-12:
        return float("nan")
    return expected_reward_all_p(inst, sp, rp) / c


def oracle_sender_ceiling_p(inst, rp) -> float:
    """B(π_R): max over true words of π_R(t|w), averaged over targets."""
    vocab = family_vocab(inst.family)
    T = truth_p(inst)
    r = 0.0
    for t in range(inst.K):
        x = replace(inst, target=t)
        true_ws = np.nonzero(T[t])[0]
        if len(true_ws) == 0:
            continue
        r += max(float(rp(x, vocab[int(w)])[t]) for w in true_ws)
    return r / inst.K


def sender_minus_s1_p(inst, sp, rp) -> float:
    """R^all(π_S, π_R) − R^all(S1, π_R) with frozen receiver."""
    s1 = lambda x: S1_p(x)[x.target]
    return expected_reward_all_p(inst, sp, rp) - expected_reward_all_p(inst, s1, rp)


def ceilings_p(insts, sp, rp) -> dict:
    """Aggregate ceiling / efficiency metrics over instances (METRICS §3)."""
    C = [speaker_ceiling_p(i, sp) for i in insts]
    R_all = [expected_reward_all_p(i, sp, rp) for i in insts]
    eta = [
        (r / c if c > 1e-12 else float("nan"))
        for r, c in zip(R_all, C)
    ]
    B = [oracle_sender_ceiling_p(i, rp) for i in insts]
    dS1 = [sender_minus_s1_p(i, sp, rp) for i in insts]
    return {
        "speaker_ceiling": float(np.mean(C)),
        "R_all": float(np.mean(R_all)),
        "listener_efficiency": float(np.nanmean(eta)),
        "oracle_sender_ceiling": float(np.mean(B)),
        "sender_minus_s1": float(np.mean(dS1)),
    }


def receiver_logp_p(insts, rp):
    """Mean log π_R(target | w) over words true of the target (clip 1e-12).

    Primary key: ``R_logp_true_words`` (METRICS B3). ``R_logp_correct`` kept as a
    read alias for old JSON schemas — same value, different semantics from E1's
    ``R_logp_correct`` (first identifying pair).
    """
    vals = []
    for inst in insts:
        vocab = family_vocab(inst.family)
        for j in np.nonzero(truth_p(inst)[inst.target])[0]:
            p = float(np.clip(rp(inst, vocab[j])[inst.target], 1e-12, 1.0))
            vals.append(math.log(p))
    m = float(np.mean(vals)) if vals else float("nan")
    return {"R_logp_true_words": m, "R_logp_correct": m}  # alias

def protocol_fidelity_p(insts, sp, rp):
    """Split the S0+L0-level R_team puzzle into sender vs receiver leakage.

    sender_truth_mass: E[ Σ_w π_S(w) 1[w true of target] ]. S0 = 1; mass on false words
        is why an informative-looking speaker can still hurt a literal listener.
    receiver_literal_mass: E_{w~π_S}[ Σ_i π_R(i|w) 1[w true of i] ]. L0 = 1 on supported
        words; mass on items the word does not describe is the other leak.
    Both in [0, 1]. Reported next to speaker/pragmatic indices.
    """
    st, rl = [], []
    for inst in insts:
        vocab = family_vocab(inst.family)
        T = truth_p(inst)
        p = sp(inst)
        st.append(float(p @ T[inst.target]))
        mass = 0.0
        for j, w in enumerate(vocab):
            if p[j] < 1e-12:
                continue
            ri = rp(inst, w)
            mass += p[j] * float(ri @ T[:, j])
        rl.append(mass)
    return {
        "sender_truth_mass": float(np.mean(st)),
        "receiver_literal_mass": float(np.mean(rl)),
        "sender_false_mass": float(1.0 - np.mean(st)),
        "receiver_off_support_mass": float(1.0 - np.mean(rl)),
    }


def evaluate_p(insts, sp, rp):
    refs = [references_p(i) for i in insts]
    return {
        "n": len(insts),
        "R_team": float(np.mean([expected_reward_p(i, sp, rp) for i in insts])),
        **{f"ref_{k}": float(np.mean([r[k] for r in refs])) for k in refs[0]},
        **cfi_p(insts, sp, rp), **sender_mi_p(insts, sp),
        **pragmatic_index_p(insts, rp),
        **speaker_index_p(insts, sp),
        **speaker_index_argmax_p(insts, sp),
        **receiver_logp_p(insts, rp),
        **protocol_fidelity_p(insts, sp, rp),
        **ceilings_p(insts, sp, rp),
    }

def s0_sender_p(inst):
    return S0_p(inst)[inst.target]


def s0_message_p(inst, rng) -> str:
    """M_single scripted partner: S0 sample."""
    vocab = family_vocab(inst.family)
    return vocab[int(rng.choice(len(vocab), p=S0_p(inst)[inst.target]))]


def s1_sender_p(inst):
    return S1_p(inst)[inst.target]


def l0_receiver_p(inst, w):
    return L0_p(inst)[family_vocab(inst.family).index(w)]


def l2_argmax_receiver_p(inst, w):
    row = L2_p(inst)[family_vocab(inst.family).index(w)]
    b = np.isclose(row, row.max()).astype(float)
    return b / b.sum()


def truthful_protocol_p():
    """Best truthful joint protocol; matching recomputed per instance (no stale closure)."""
    def maps(x):
        _, word_of = max_matching_p(truth_p(x))
        return word_of, {w: i for i, w in word_of.items()}

    def sp(x):
        word_of, _ = maps(x)
        if x.target in word_of:
            return _onehot(len(family_vocab(x.family)), word_of[x.target])
        return S0_p(x)[x.target]

    def rp(x, w):
        _, item_of = maps(x)
        j = family_vocab(x.family).index(w)
        return _onehot(x.K, item_of[j]) if j in item_of else L0_p(x)[j]
    return sp, rp


def main_p(out_dir="."):
    sets = {}
    for name, fam, Ks, seed in [
        ("e1p_train", "train", (4, 6), 11),
        ("e1p_val", "train", (4, 6), 12),
        ("e1p_relabel_heldout", "relabel", (6,), 13),
    ]:
        n = 2000 if name == "e1p_train" else 300
        insts, tries = generate_p(n, fam, Ks, seed)
        path = f"{out_dir}/{name}.jsonl"
        with open(path, "w") as fh:
            for i in insts:
                fh.write(json.dumps(asdict(i)) + "\n")
        sets[name] = {
            "path": path,
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
            "acceptance_rate": len(insts) / tries,
            "validation": validate(insts, name) | {"all_items_pair_identifiable": "n/a (E1-P)"},
            "_insts": insts,
        }

    val = sets["e1p_val"]["_insts"][:150]
    tp_s, tp_r = truthful_protocol_p()
    sanity = {
        "S0+L0": evaluate_p(val, s0_sender_p, l0_receiver_p),
        "S1+L0": evaluate_p(val, s1_sender_p, l0_receiver_p),
        "S1+L2(argmax)": evaluate_p(val, s1_sender_p, l2_argmax_receiver_p),
        "truthful_protocol": evaluate_p(val, tp_s, tp_r),
    }
    for v in sets.values():
        v.pop("_insts")
    sub = subset_beyond_gricean_p(val)
    sanity["subset_beyond_gricean"] = {
        "n": len(sub), "share": len(sub) / len(val),
        "S1+L2(argmax)": evaluate_p(sub, s1_sender_p, l2_argmax_receiver_p)["R_team"] if sub else None,
    }
    manifest = {"spec": "stage1 v4.4", "env": "E1-P", "min_gap": 0.15, "sets": sets, "sanity": sanity}
    with open(f"{out_dir}/e1p_manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


# ---------------------------------------------------------------- main (E1)

def main(out_dir="."):
    sets = {
        "e1_train": generate(2000, "train", Ks=(4, 6), seed=1),
        "e1_val": generate(500, "train", Ks=(4, 6), seed=2),
        "e1_relabel_heldout": generate(500, "relabel", Ks=(8,), seed=3),
    }
    manifest = {"spec": "stage1 v4.4", "env": "E1", "sets": {}}
    for name, insts in sets.items():
        path = f"{out_dir}/{name}.jsonl"
        with open(path, "w") as fh:
            for i in insts:
                fh.write(json.dumps(asdict(i)) + "\n")
        manifest["sets"][name] = {
            "path": path, "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
            "validation": validate(insts, name),
        }

    val = sets["e1_val"][:200]
    pairs = {
        "perfect+literal": (perfect_sender, literal_receiver),
        "leaky+literal": (leaky_sender, literal_receiver),
        "leaky+first_word": (leaky_sender, first_word_receiver),
        "uniform+literal": (uniform_sender, literal_receiver),
        "perfect+uniform": (perfect_sender, uniform_receiver),
    }
    sanity = {}
    for name, (s, r) in pairs.items():
        sanity[name] = {
            "E[R]": float(np.mean([expected_reward(i, s, r) for i in val])),
            **cfi(val, s, r, P=1),
            **sender_mi(val[:50], s, P=1),
        }
    sanity["receivers_do_m"] = {
        "literal": receiver_sel(val, literal_receiver, P=1),
        "first_word": receiver_sel(val, first_word_receiver, P=1),
    }
    manifest["metric_sanity"] = sanity
    with open(f"{out_dir}/e1_manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    return manifest


# ================================================================= E-HP (v2)
# Hidden profile via a shared requirement. Public names end in `_hp`.
# Pivotal fact = holder's requirement-dimension measurement when it violates (HP).
# Non-holder view is identically distributed in HP and CC → deaf baseline = 1 − P(HP).

FAMILIES_HP = {
    "train": {"options": ("Plan A", "Plan B"),
              "pos": ["reliable", "popular", "scalable", "well-documented", "secure", "modular"],
              "neg": ["fragile", "unpopular", "rigid", "poorly documented", "insecure", "monolithic"],
              "dims": {"cost": ("cost", "$", "k", "at most"),
                       "time": ("delivery time", "", " days", "at most"),
                       "capacity": ("capacity", "", " users", "at least")}},
    "relabel": {"options": ("Route North", "Route South"),
                "pos": ["scenic", "paved", "quiet", "lit", "shaded", "sign-posted"],
                "neg": ["muddy", "busy", "dark", "exposed", "unmarked", "noisy"],
                "dims": {"length": ("length", "", " km", "at most"),
                         "climb": ("total climb", "", " m", "at most"),
                         "water": ("water stops", "", "", "at least")}},
}
N_ADD_SHARED_HP, N_ADD_PRIVATE_HP = 3, 2
THRESH_HP = {"cost": 10, "time": 14, "capacity": 500, "length": 20, "climb": 600, "water": 3}
STEP_HP = {"cost": 2, "time": 3, "capacity": 100, "length": 4, "climb": 150, "water": 1}


@dataclass(frozen=True)
class AdditiveHP:
    option: int
    word: str
    weight: int


@dataclass(frozen=True)
class MeasureHP:
    option: int
    dim: str
    value: int


@dataclass(frozen=True)
class RequirementHP:
    dim: str
    bound: int


@dataclass(frozen=True)
class InstanceHP:
    id: str
    family: str
    kind: str          # "HP" | "CC"
    consensus: int     # c
    correct: int
    holder: int
    requirement: RequirementHP
    shared: tuple      # tuple[AdditiveHP]
    private: tuple     # (tuple[fact x4], tuple[fact x4]); fact = AdditiveHP | MeasureHP
    seed: int


def satisfies_hp(req: RequirementHP, fam: str, m: MeasureHP) -> bool:
    kind = FAMILIES_HP[fam]["dims"][req.dim][3]
    return m.value <= req.bound if kind == "at most" else m.value >= req.bound


def additive_value_hp(facts) -> np.ndarray:
    v = np.zeros(2)
    for f in facts:
        if isinstance(f, AdditiveHP):
            v[f.option] += f.weight
    return v


def rational_choice_hp(inst: InstanceHP, facts) -> int:
    """Eliminate options known to violate the requirement; then highest additive value."""
    bad = {f.option for f in facts
           if isinstance(f, MeasureHP) and f.dim == inst.requirement.dim
           and not satisfies_hp(inst.requirement, inst.family, f)}
    ok = [o for o in (0, 1) if o not in bad]
    if len(ok) == 1:
        return ok[0]
    v = additive_value_hp(facts)
    return int(np.argmax(v))


def own_view_hp(inst: InstanceHP, i: int):
    return list(inst.shared) + list(inst.private[i])


def _additive_hp(rng, fam, used, support, mag):
    opt, w = (support, mag) if rng.random() < 0.5 else (1 - support, -mag)
    for _ in range(2):
        pool = FAMILIES_HP[fam]["pos" if w > 0 else "neg"]
        choices = [x for x in pool if (opt, x) not in used]
        if choices:
            break
        opt, w = 1 - opt, -w
    word = choices[int(rng.integers(len(choices)))]
    used.add((opt, word))
    return AdditiveHP(opt, word, w)


def _measure_hp(rng, fam, dim, option, satisfy: bool | None):
    t, s = THRESH_HP[dim], STEP_HP[dim]
    kind = FAMILIES_HP[fam]["dims"][dim][3]
    k = int(rng.integers(1, 3))
    if satisfy is None:
        satisfy = bool(rng.random() < 0.5)
    up = (kind == "at least") == satisfy
    return MeasureHP(option, dim, t + k * s if up else max(t - k * s, s))


def generate_hp(n, family, seed, variant: str | None = None):
    """Generate E-HP instances.

    ``variant`` overrides the process-global ``EHP_VARIANT`` for this call.
    ``\"b\"``: non-holder drops the requirement measurement and gets two
    other-dimension measurements instead (CLAUDE §11 Variant B). Default
    generator (and frozen P6) is unchanged.
    """
    variant = EHP_VARIANT if variant is None else variant
    if variant not in _EHP_VARIANTS:
        raise ValueError(f"unknown ehp variant: {variant}")
    rng = np.random.default_rng(seed)
    dims = list(FAMILIES_HP[family]["dims"])
    out, tries = [], 0
    while len(out) < n:
        tries += 1
        used = set()
        c = int(rng.integers(2))
        kind = "HP" if rng.random() < 0.5 else "CC"
        holder = int(rng.integers(2))
        rdim = dims[int(rng.integers(len(dims)))]
        req = RequirementHP(rdim, THRESH_HP[rdim])
        shared = tuple(_additive_hp(rng, family, used, c, int(rng.choice([2, 3])))
                       for _ in range(N_ADD_SHARED_HP))
        privs = []
        other_dims = [d for d in dims if d != rdim]
        for i in (0, 1):
            add = [_additive_hp(rng, family, used, int(rng.integers(2)), 1)
                   for _ in range(N_ADD_PRIVATE_HP)]
            if i == holder:
                m_req = _measure_hp(rng, family, rdim, c, satisfy=(kind == "CC"))
                odim = other_dims[int(rng.integers(len(other_dims)))]
                m_other = _measure_hp(rng, family, odim, int(rng.integers(2)), satisfy=None)
                facts = add + [m_req, m_other]
            elif variant == "b":
                # No req measurement; two other-dim measurements (distinct dims).
                m_o1 = _measure_hp(
                    rng, family, other_dims[0], int(rng.integers(2)), satisfy=None,
                )
                m_o2 = _measure_hp(
                    rng, family, other_dims[1 % len(other_dims)],
                    int(rng.integers(2)), satisfy=None,
                )
                facts = add + [m_o1, m_o2]
            else:
                m_req = _measure_hp(rng, family, rdim, 1 - c, satisfy=True)
                odim = other_dims[int(rng.integers(len(other_dims)))]
                m_other = _measure_hp(rng, family, odim, int(rng.integers(2)), satisfy=None)
                facts = add + [m_req, m_other]
            rng.shuffle(facts)
            privs.append(tuple(facts))
        tag = "" if variant == "default" else f"-{variant}"
        inst = InstanceHP(
            f"ehp{tag}-{family}-s{seed}-{len(out):05d}", family, kind, c,
            (1 - c) if kind == "HP" else c, holder, req, shared,
            (privs[0], privs[1]), int(rng.integers(2**31)),
        )
        ok = True
        for j in (0, 1):
            base = own_view_hp(inst, j)
            if additive_value_hp(base)[c] - additive_value_hp(base)[1 - c] < 2:
                ok = False
            for f in inst.private[1 - j]:
                v = additive_value_hp(base + [f])
                if v[c] - v[1 - c] < 2:
                    ok = False
        if rational_choice_hp(inst, own_view_hp(inst, 0) + list(inst.private[1])) != inst.correct:
            ok = False
        if ok:
            out.append(inst)
    return out, tries


def render_fact_hp(inst: InstanceHP, f) -> str:
    fam = FAMILIES_HP[inst.family]
    opt = fam["options"][f.option]
    if isinstance(f, AdditiveHP):
        return f"{opt}: {f.word} ({f.weight:+d})"
    name, pre, post, _ = fam["dims"][f.dim]
    return f"{opt}: {name} {pre}{f.value}{post}"


def render_requirement_hp(inst: InstanceHP) -> str:
    name, pre, post, kind = FAMILIES_HP[inst.family]["dims"][inst.requirement.dim]
    body = (f"the chosen option must have {name} {kind} "
            f"{pre}{inst.requirement.bound}{post}.")
    if PROMPT_VARIANT in ("ehp_v2a", "goal_explicit"):
        # Partner-known mark: required for E-HP v2 (PREREG_EHP_V2); also used by ehp_v2a.
        return f"Requirement (your partner knows it too): {body}"
    return f"Requirement: {body}"


def _hp_opener(inst: InstanceHP) -> str:
    """Lead-in before the requirement line. Variant-specific rules live here."""
    fam = FAMILIES_HP[inst.family]
    a, b = fam["options"]
    if PROMPT_VARIANT == "ehp_v2a":
        return (
            f"You and a partner must choose between {a} and {b}. "
            f"Points (+/-) are evidence.\n"
            f"{render_requirement_hp(inst)}\n"
            f"An option is out only if a known measurement shows it fails the "
            f"requirement. If you have no measurement of an option on the "
            f"requirement's dimension, treat it as meeting the requirement and "
            f"decide by points."
        )
    if PROMPT_VARIANT == "goal_explicit":
        return (
            f"You and a partner must jointly choose between {a} and {b}. "
            f"You share one team reward: both of you must vote for the correct "
            f"option. Points (+/-) are evidence; an option that fails the "
            f"requirement is out.\n{render_requirement_hp(inst)}"
        )
    return (
        f"You and a partner must choose between {a} and {b}. "
        f"Points (+/-) are evidence; an option that fails the requirement is "
        f"out.\n{render_requirement_hp(inst)}"
    )


def _hp_closer_line() -> str:
    if PROMPT_VARIANT == "goal_explicit":
        # v2.1: goal + help only. Do NOT name the requirement-fact strategy
        # (see PREREG_EHP_V2 § Amendment v2.1). Old closer had:
        # "... especially a fact about the requirement when it decides the answer."
        return "Share exactly ONE private fact to help your partner vote correctly."
    return "You may share exactly ONE of your private facts with your partner."


def render_sender_hp(inst: InstanceHP, i: int) -> dict:
    fam = FAMILIES_HP[inst.family]
    lines = "\n".join(f"- {render_fact_hp(inst, f)}" for f in inst.shared)
    mine = "\n".join(f"- {render_fact_hp(inst, f)}" for f in inst.private[i])
    closer = _hp_closer_line()
    state = (
        f"{_hp_opener(inst)}\n"
        f"Shared facts (your partner knows these):\n{lines}\n"
        f"Your private facts (your partner does not know these):\n{mine}\n"
        f"{closer}"
    )
    if PROMPT_VARIANT == "goal_explicit":
        question = "Which private fact should you share to help your partner vote correctly?"
    else:
        question = "Which private fact do you share?"
    return {
        "state": state,
        "question": question,
        "options": [render_fact_hp(inst, f) for f in inst.private[i]],
    }


def render_receiver_hp(inst: InstanceHP, j: int, fact) -> dict:
    fam = FAMILIES_HP[inst.family]
    d = render_sender_hp(inst, j)
    if fact is None:
        # Diagnostic no-message probe (baseline anti-consensus); not used in training.
        partner_line = "Your partner has not shared a fact."
    elif PROMPT_VARIANT == "goal_explicit":
        partner_line = (
            f"Your partner chose the following fact intending to help you vote "
            f"correctly (you share one team reward): {render_fact_hp(inst, fact)}"
        )
    else:
        partner_line = f"Your partner shared: {render_fact_hp(inst, fact)}"
    return {
        "state": d["state"].replace(_hp_closer_line(), partner_line),
        "question": "Which option do you vote for?",
        "options": list(fam["options"]),
    }


def team_reward_hp(inst: InstanceHP, sender, receiver) -> float:
    p = [sender(inst, 0), sender(inst, 1)]
    r = 0.0
    for a, b in itertools.product(range(4), repeat=2):
        w = p[0][a] * p[1][b]
        if w < 1e-12:
            continue
        r += w * receiver(inst, 0, inst.private[1][b])[inst.correct] \
               * receiver(inst, 1, inst.private[0][a])[inst.correct]
    return r


def _onehot_hp(n, k):
    v = np.zeros(n)
    v[k] = 1.0
    return v


def uniform_sender_hp(inst, i):
    return np.full(4, 0.25)


def salient_sender_hp(inst, i):
    """Share the additive fact with the largest |weight| (ties uniform)."""
    s = np.array([abs(f.weight) if isinstance(f, AdditiveHP) else 0
                  for f in inst.private[i]], float)
    b = np.isclose(s, s.max()).astype(float)
    return b / b.sum()


def measurement_sender_hp(inst, i):
    """Share a measurement, uniformly — right kind, no link to the requirement."""
    m = np.array([float(isinstance(f, MeasureHP)) for f in inst.private[i]])
    return m / m.sum()


def requirement_sender_hp(inst, i):
    """Share the measurement on the requirement's dimension (uniform over ties).

    Under Variant B the non-holder has no such measurement → uniform over the
    four private facts (cannot signal the requirement).
    """
    idxs = _req_indices_hp(inst, i)
    if not idxs:
        return np.full(len(inst.private[i]), 1.0 / len(inst.private[i]))
    out = np.zeros(len(inst.private[i]))
    for k in idxs:
        out[k] = 1.0
    return out / out.sum()


def rational_receiver_hp(inst, j, fact):
    facts = own_view_hp(inst, j) if fact is None else own_view_hp(inst, j) + [fact]
    return _onehot_hp(2, rational_choice_hp(inst, facts))


def deaf_receiver_hp(inst, j, fact):
    return _onehot_hp(2, rational_choice_hp(inst, own_view_hp(inst, j)))


def additive_receiver_hp(inst, j, fact):
    """Sums points, ignores requirements entirely."""
    facts = own_view_hp(inst, j) if fact is None else own_view_hp(inst, j) + [fact]
    return _onehot_hp(2, int(np.argmax(additive_value_hp(facts))))


def nonholder_features_hp(inst: InstanceHP):
    j = 1 - inst.holder
    view = own_view_hp(inst, j)
    v = additive_value_hp(view)
    others = [f for f in inst.private[j]
              if isinstance(f, MeasureHP) and f.dim != inst.requirement.dim]
    # Default: one other-dim; Variant B: two — use the first for the AUC feature.
    m = others[0]
    return [
        v[inst.consensus] - v[1 - inst.consensus],
        sum(abs(f.weight) for f in inst.private[j] if isinstance(f, AdditiveHP)),
        float(m.option == inst.consensus),
        float(satisfies_hp(RequirementHP(m.dim, THRESH_HP[m.dim]), inst.family, m)),
    ]


def auc_hp(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    return float((pos[:, None] > neg[None, :]).mean()
                 + 0.5 * (pos[:, None] == neg[None, :]).mean())


def _req_indices_hp(inst: InstanceHP, i: int) -> list[int]:
    return [k for k, f in enumerate(inst.private[i])
            if isinstance(f, MeasureHP) and f.dim == inst.requirement.dim]


def _req_idx_hp(inst: InstanceHP, i: int) -> int:
    idxs = _req_indices_hp(inst, i)
    if not idxs:
        raise ValueError(f"no requirement measurement for agent {i}")
    return idxs[0]


def _req_mass_hp(pi, inst: InstanceHP, i: int) -> float | None:
    """π mass on req-dim measurements, or None if this agent has none (Variant B nh)."""
    idxs = _req_indices_hp(inst, i)
    if not idxs:
        return None
    pi = np.asarray(pi, float)
    return float(sum(pi[k] for k in idxs))


def _req_argmax_mass_hp(pi, inst: InstanceHP, i: int) -> float | None:
    """C2 tie-split argmax mass on req-dim measurements (None if agent has none)."""
    idxs = _req_indices_hp(inst, i)
    if not idxs:
        return None
    a = tie_split_argmax(pi)
    return float(sum(a[k] for k in idxs))


def _other_meas_idx_hp(inst: InstanceHP, i: int) -> int:
    for k, f in enumerate(inst.private[i]):
        if isinstance(f, MeasureHP) and f.dim != inst.requirement.dim:
            return k
    raise ValueError("no other-dimension measurement")


def _entropy_hp(p) -> float:
    p = np.asarray(p, float)
    p = p[p > 0]
    return float(-(p * np.log(p)).sum()) if len(p) else 0.0


def holder_message_type_mass_hp(insts, sender) -> dict:
    """Holder π_S mass by message type, split HP/CC — Grice check for other-dim.

    Returns mean π(req) / π(other-dim) / π(additive) for the holder, plus Bayes
    ``P(HP | holder sent other-dim)`` under the empirical kind prior on ``insts``.
    Scripted uniform → P(HP|other) = P(HP) by construction. A co-trained sender
    that reserves other-dim for CC yields P(HP|other) ≪ P(HP).
    """
    def _masses(inst):
        h = inst.holder
        pi = np.asarray(sender(inst, h), float)
        req = float(pi[_req_idx_hp(inst, h)])
        other = float(pi[_other_meas_idx_hp(inst, h)])
        add = float(1.0 - req - other)
        return req, other, add

    by = {"HP": [], "CC": []}
    for inst in insts:
        by[inst.kind].append(_masses(inst))
    out = {"n": len(insts), "n_HP": len(by["HP"]), "n_CC": len(by["CC"])}
    for kind, rows in by.items():
        if not rows:
            out[kind] = {"req": float("nan"), "other": float("nan"), "additive": float("nan")}
            continue
        arr = np.asarray(rows, float)
        out[kind] = {
            "req": float(arr[:, 0].mean()),
            "other": float(arr[:, 1].mean()),
            "additive": float(arr[:, 2].mean()),
        }
    p_hp = out["n_HP"] / max(out["n"], 1)
    p_o_hp = out["HP"]["other"]
    p_o_cc = out["CC"]["other"]
    p_o = p_hp * p_o_hp + (1.0 - p_hp) * p_o_cc
    out["P_HP"] = float(p_hp)
    out["P_other"] = float(p_o)
    out["P_HP_given_other"] = (
        float((p_o_hp * p_hp) / p_o) if p_o > 1e-12 else float("nan")
    )
    return out


def ladder_refs_hp(insts) -> dict:
    """Exact reference ladder means over `insts`."""
    ev = lambda s, r: float(np.mean([team_reward_hp(x, s, r) for x in insts]))
    return {
        "deaf": ev(uniform_sender_hp, deaf_receiver_hp),
        "uniform_rational": ev(uniform_sender_hp, rational_receiver_hp),
        "salient_rational": ev(salient_sender_hp, rational_receiver_hp),
        "measurement_rational": ev(measurement_sender_hp, rational_receiver_hp),
        "requirement_additive": ev(requirement_sender_hp, additive_receiver_hp),
        "requirement_rational": ev(requirement_sender_hp, rational_receiver_hp),
    }


def evaluate_hp(insts, sender, receiver) -> dict:
    """Primary E-HP metrics for a (sender, receiver) policy pair.

    Consensus override is a receiver-side ``do(m)`` contrast at the **non-holder**'s
    fixed view (the agent who cannot already see a violation of ``c``). Messages are
    the **holder's** private facts (what the non-holder actually hears in play):
    - violating: holder's requirement measurement when it violates (HP);
    - satisfying: holder's requirement measurement when it satisfies (CC);
    - other-dim: holder's other-dimension measurement.

    (Earlier builds probed ``m_nonholder`` for the satisfying / other-dim arms — that
    fact is what the *holder* hears, and names option ``1−c``, so FA rates did not
    match in-game CC errors. Fixed 2026-10-01.)

    Under a rational receiver: violating → vote ``1−c``, satisfying / other-dim →
    vote ``c``, so ``consensus_override = 1``. A deaf receiver is invariant in ``m``,
    so the contrast is 0.

    Also returns baseline anti-consensus probes (METRICS A2): ``P_anti_none``
    (``receiver(..., None)``), ``P_anti_additive`` (holder additive facts), and
    ``value_discrimination = override_violating − override_satisfying``.
    """
    r_all, r_hp, r_cc = [], [], []
    req_share, req_share_hp, req_share_cc, viol_share = [], [], [], []
    req_share_argmax, viol_share_argmax = [], []
    ov_viol, ov_sat, ov_other = [], [], []
    anti_none, anti_add = [], []
    # In-game reconciliation probes (non-holder only; not part of P6 estimand).
    nh_err_cc_req, nh_err_cc_all = [], []
    H_s, H_r = [], []
    for inst in insts:
        r = team_reward_hp(inst, sender, receiver)
        r_all.append(r)
        (r_hp if inst.kind == "HP" else r_cc).append(r)
        c = inst.consensus
        h, nh = inst.holder, 1 - inst.holder
        m_holder = inst.private[h][_req_idx_hp(inst, h)]
        m_holder_other = inst.private[h][_other_meas_idx_hp(inst, h)]
        holder_violates = not satisfies_hp(inst.requirement, inst.family, m_holder)
        for i in (0, 1):
            pi = np.asarray(sender(inst, i), float)
            H_s.append(_entropy_hp(pi))
            m_req = _req_mass_hp(pi, inst, i)
            if m_req is not None:
                req_share.append(m_req)
                (req_share_hp if inst.kind == "HP" else req_share_cc).append(m_req)
                req_share_argmax.append(_req_argmax_mass_hp(pi, inst, i))
            if inst.kind == "HP" and i == h:
                # Holder always has the req measurement in default and B.
                viol_share.append(float(pi[_req_idx_hp(inst, i)]))
                viol_share_argmax.append(
                    float(tie_split_argmax(pi)[_req_idx_hp(inst, i)])
                )
        for j in (0, 1):
            partner = 1 - j
            for f in inst.private[partner]:
                H_r.append(_entropy_hp(np.asarray(receiver(inst, j, f), float)))
        # Non-holder × holder facts under do(m).
        if holder_violates:
            ov_viol.append(float(np.asarray(receiver(inst, nh, m_holder))[1 - c]))
        else:
            ov_sat.append(float(np.asarray(receiver(inst, nh, m_holder))[1 - c]))
        ov_other.append(float(np.asarray(receiver(inst, nh, m_holder_other))[1 - c]))
        # Baseline anti-consensus (diagnostic; METRICS A2).
        anti_none.append(float(np.asarray(receiver(inst, nh, None))[1 - c]))
        for f in inst.private[h]:
            if isinstance(f, AdditiveHP):
                anti_add.append(float(np.asarray(receiver(inst, nh, f))[1 - c]))
        # In-game: non-holder error on CC under actual sender mix / under req message.
        if inst.kind == "CC":
            p_h = np.asarray(sender(inst, h), float)
            err = 0.0
            for k, f in enumerate(inst.private[h]):
                err += float(p_h[k]) * float(np.asarray(receiver(inst, nh, f))[1 - c])
            nh_err_cc_all.append(err)
            nh_err_cc_req.append(float(np.asarray(receiver(inst, nh, m_holder))[1 - c]))
    override_violating = float(np.mean(ov_viol)) if ov_viol else float("nan")
    override_satisfying = float(np.mean(ov_sat)) if ov_sat else float("nan")
    override_other_dim = float(np.mean(ov_other)) if ov_other else float("nan")
    consensus_override = (
        override_violating - max(override_satisfying, override_other_dim)
        if ov_viol and ov_sat and ov_other else float("nan")
    )
    p_anti_none = float(np.mean(anti_none)) if anti_none else float("nan")
    p_anti_additive = float(np.mean(anti_add)) if anti_add else float("nan")
    value_discrimination = (
        override_violating - override_satisfying
        if ov_viol and ov_sat else float("nan")
    )
    return {
        "n": len(insts),
        "n_HP": sum(1 for x in insts if x.kind == "HP"),
        "R_team": float(np.mean(r_all)) if r_all else float("nan"),
        "R_team_HP": float(np.mean(r_hp)) if r_hp else float("nan"),
        "R_team_CC": float(np.mean(r_cc)) if r_cc else float("nan"),
        "requirement_share": float(np.mean(req_share)) if req_share else float("nan"),
        "requirement_share_HP": float(np.mean(req_share_hp)) if req_share_hp else float("nan"),
        "requirement_share_CC": float(np.mean(req_share_cc)) if req_share_cc else float("nan"),
        "requirement_share_argmax": (
            float(np.mean(req_share_argmax)) if req_share_argmax else float("nan")
        ),
        "violating_share_HP": float(np.mean(viol_share)) if viol_share else float("nan"),
        "violating_share_HP_argmax": (
            float(np.mean(viol_share_argmax)) if viol_share_argmax else float("nan")
        ),
        "override_violating": override_violating,
        "override_satisfying": override_satisfying,
        "override_other_dim": override_other_dim,
        "consensus_override": consensus_override,
        "value_discrimination": value_discrimination,
        "P_anti_none": p_anti_none,
        "P_anti_additive": p_anti_additive,
        "shift_viol": (
            override_violating - p_anti_none
            if ov_viol and anti_none else float("nan")
        ),
        "shift_sat": (
            override_satisfying - p_anti_none
            if ov_sat and anti_none else float("nan")
        ),
        "nh_error_CC_do_req": float(np.mean(nh_err_cc_req)) if nh_err_cc_req else float("nan"),
        "nh_error_CC_in_game": float(np.mean(nh_err_cc_all)) if nh_err_cc_all else float("nan"),
        "sender_entropy": float(np.mean(H_s)) if H_s else float("nan"),
        "receiver_entropy": float(np.mean(H_r)) if H_r else float("nan"),
        "ladder_references": ladder_refs_hp(insts),
    }

def _acceptance_hp(insts) -> dict:
    ev = lambda s, r: float(np.mean([team_reward_hp(x, s, r) for x in insts]))
    return {
        "n_HP": sum(1 for x in insts if x.kind == "HP"),
        "deaf": ev(uniform_sender_hp, deaf_receiver_hp),
        "uniform+rational": ev(uniform_sender_hp, rational_receiver_hp),
        "salient+rational": ev(salient_sender_hp, rational_receiver_hp),
        "measurement+rational": ev(measurement_sender_hp, rational_receiver_hp),
        "requirement+additive": ev(requirement_sender_hp, additive_receiver_hp),
        "requirement+rational": ev(requirement_sender_hp, rational_receiver_hp),
        "first3": [
            f"{x.kind}/h{x.holder}/{x.requirement.dim}" for x in insts[:3]
        ],
        "nonholder_leak_auc": (
            lambda X, y: [auc_hp(X[y, k], X[~y, k]) for k in range(X.shape[1])]
        )(np.array([nonholder_features_hp(x) for x in insts]),
          np.array([x.kind == "HP" for x in insts])),
    }


# Exact acceptance targets (deterministic; freeze).
ACCEPTANCE_HP = {
    "ehp_val": {
        "n_HP": 153, "deaf": 0.4900, "uniform+rational": 0.6175,
        "salient+rational": 0.4900, "measurement+rational": 0.7450,
        "requirement+additive": 0.4900, "requirement+rational": 1.0000,
        "first3": ["CC/h1/time", "HP/h1/cost", "HP/h0/time"],
        "auc_tol": 0.06, "auc_train": None,
    },
    "ehp_relabel": {
        "n_HP": 161, "deaf": 0.4633, "uniform+rational": 0.5975,
        "salient+rational": 0.4633, "measurement+rational": 0.7317,
        "requirement+additive": 0.4633, "requirement+rational": 1.0000,
        "first3": ["CC/h0/water", "CC/h0/water", "CC/h1/climb"],
        "auc_tol": 0.06, "auc_train": None,
    },
    "ehp_train": {
        "n_HP": 990, "deaf": 0.5050, "uniform+rational": 0.6288,
        "salient+rational": 0.5050, "measurement+rational": 0.7525,
        "requirement+additive": 0.5050, "requirement+rational": 1.0000,
        "first3": ["HP/h1/time", "HP/h0/cost", "HP/h1/cost"],
        "auc_tol": 0.02, "auc_train": [0.495, 0.5, 0.489, 0.511],
    },
}

# Variant B ladders — frozen in PREREG_EHP_V2 before Pilot 0 (n=200, seeds 52/53).
ACCEPTANCE_HP_B = {
    "ehp_b_val": {
        "family": "train", "seed": 52, "n": 200,
        "n_HP": 92, "deaf": 0.5400, "uniform+rational": 0.6550,
        "salient+rational": 0.5400, "measurement+rational": 0.7700,
        "requirement+additive": 0.5400, "requirement+rational": 1.0000,
        "auc_tol": 0.08,
    },
    "ehp_b_relabel": {
        "family": "relabel", "seed": 53, "n": 200,
        "n_HP": 101, "deaf": 0.4950, "uniform+rational": 0.6212,
        "salient+rational": 0.4950, "measurement+rational": 0.7475,
        "requirement+additive": 0.4950, "requirement+rational": 1.0000,
        "auc_tol": 0.08,
    },
}


def main_hp(out_dir="."):
    sets_spec = [
        ("ehp_train", "train", 51, 2000),
        ("ehp_val", "train", 52, 300),
        ("ehp_relabel", "relabel", 53, 300),
    ]
    sets, failures = {}, []
    for name, fam, seed, n in sets_spec:
        insts, tries = generate_hp(n, fam, seed)
        path = f"{out_dir}/{name}.jsonl"
        with open(path, "w") as fh:
            for i in insts:
                fh.write(json.dumps(asdict(i)) + "\n")
        got = _acceptance_hp(insts)
        exp = ACCEPTANCE_HP[name]
        for key in ("n_HP", "deaf", "uniform+rational", "salient+rational",
                    "measurement+rational", "requirement+additive",
                    "requirement+rational", "first3"):
            g, e = got[key], exp[key]
            if isinstance(e, float):
                if abs(g - e) > 1e-4:
                    failures.append(f"{name}.{key}: got {g}, expected {e}")
            elif g != e:
                failures.append(f"{name}.{key}: got {g}, expected {e}")
        aucs = got["nonholder_leak_auc"]
        if exp["auc_train"] is not None:
            for k, (a, e) in enumerate(zip(aucs, exp["auc_train"])):
                if abs(a - e) > 1e-3:
                    failures.append(f"{name}.auc[{k}]: got {a}, expected {e}")
        else:
            for k, a in enumerate(aucs):
                if abs(a - 0.5) > exp["auc_tol"]:
                    failures.append(f"{name}.auc[{k}]: {a} outside 0.5±{exp['auc_tol']}")
        # Scripted metric spot-checks on this set
        m_opt = evaluate_hp(insts, requirement_sender_hp, rational_receiver_hp)
        m_deaf = evaluate_hp(insts, uniform_sender_hp, deaf_receiver_hp)
        if abs(m_opt["consensus_override"] - 1.0) > 1e-6:
            failures.append(f"{name}: requirement+rational consensus_override="
                            f"{m_opt['consensus_override']} ≠ 1")
        if abs(m_opt["requirement_share"] - 1.0) > 1e-6:
            failures.append(f"{name}: requirement_share={m_opt['requirement_share']} ≠ 1")
        if abs(m_opt.get("value_discrimination", float("nan")) - 1.0) > 1e-6:
            failures.append(f"{name}: requirement+rational value_discrimination="
                            f"{m_opt.get('value_discrimination')} ≠ 1")
        if abs(m_opt["override_violating"] - 1.0) > 1e-6 or abs(m_opt["override_satisfying"]) > 1e-6:
            failures.append(f"{name}: req+rational hit/FA_sat="
                            f"{m_opt['override_violating']}/{m_opt['override_satisfying']}")
        if abs(m_deaf["consensus_override"] - 0.0) > 1e-6:
            failures.append(f"{name}: uniform+deaf consensus_override="
                            f"{m_deaf['consensus_override']} ≠ 0")
        # Deaf: hit = FA_sat = FA_other = P_anti_none
        for k in ("override_violating", "override_satisfying", "override_other_dim",
                  "P_anti_none", "P_anti_additive"):
            if abs(m_deaf[k] - m_deaf["P_anti_none"]) > 1e-6:
                failures.append(f"{name}: deaf {k}={m_deaf[k]} ≠ P_anti_none="
                                f"{m_deaf['P_anti_none']}")
                break
        sets[name] = {
            "path": path,
            "sha256": hashlib.sha256(open(path, "rb").read()).hexdigest(),
            "n": n,
            "acceptance_rate": len(insts) / tries,
            "acceptance": got,
            "evaluate_requirement_rational": {
                k: m_opt[k] for k in (
                    "R_team", "requirement_share", "consensus_override",
                    "override_violating", "override_satisfying", "override_other_dim",
                )
            },
        }
    manifest = {
        "spec": "stage1 E-HP v2",
        "env": "E-HP",
        "sets": sets,
        "acceptance_ok": not failures,
        "acceptance_failures": failures,
    }
    with open(f"{out_dir}/ehp_manifest.json", "w") as fh:
        json.dump(manifest, fh, indent=2)
    if failures:
        raise AssertionError("E-HP acceptance failed:\n  " + "\n  ".join(failures))
    return manifest


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    which = sys.argv[2] if len(sys.argv) > 2 else "e1"
    if which == "e1p":
        m = main_p(out)
    elif which in ("ehp", "e1hp", "hp"):
        m = main_hp(out)
    else:
        m = main(out)
    print(json.dumps(m, indent=2))

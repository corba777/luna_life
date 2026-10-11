"""TypeSafe policy wrappers for Stage 1 environments.

Same numpy interfaces as JevPolicy (sender_policy / receiver_policy and _p / _hp
variants). Every question is asked under P option orderings; the returned
distribution is the mean over orderings, mapped back to canonical option order.

Option orderings are deterministic in (instance seed, question id, perm_idx) and
identical across counterfactual variants that share the same render seed fields
used by e1_env._perm — for E1 we reuse render_* (perm_idx). For E1-P / E-HP,
which have no built-in perm, we shuffle criteria presentation only.
"""
from __future__ import annotations

import itertools
from typing import Sequence

import numpy as np

import e1_env as E
from typesafe_client import TypeSafeClient

DEFAULT_P = 4  # paired option permutations (TYPESAFE_EVAL_PLAN §4)


def _shuffle_criteria(values: Sequence[str], rng: np.random.Generator) -> dict[str, str]:
    """Criteria keyed by the option string itself; insertion order = presentation."""
    order = list(values)
    if len(order) >= 2:
        for _ in range(32):
            perm = rng.permutation(len(order))
            new = [order[i] for i in perm]
            if new != order:
                order = new
                break
        else:
            order = list(reversed(order))
    return {v: v for v in order}


def _perm_rng(seed_parts: Sequence[int]) -> np.random.Generator:
    return np.random.default_rng(list(seed_parts))


def _from_values(client: TypeSafeClient, state: str, question: str,
                 values: Sequence[str], *, perm_idx: int, stream: int,
                 seed: int, draw: int) -> np.ndarray:
    """Shuffle presentation of `values`; return probs in canonical value order."""
    rng = _perm_rng([seed, perm_idx, stream, 7919])
    criteria = _shuffle_criteria(values, rng)
    probs = client.choose(state, question, criteria, draw=draw)
    out = np.array([probs[v] for v in values], dtype=float)
    return out / out.sum()


class TypeSafePolicy:
    """Frozen TypeSafe Jev as both roles. In-memory + on-disk (via client) cache."""

    def __init__(self, client: TypeSafeClient | None = None, *, P: int = DEFAULT_P):
        self.client = client or TypeSafeClient()
        self.P = int(P)
        if self.P < 1:
            raise ValueError("P must be >= 1")
        self._cache: dict = {}
        self.n_forwards = 0  # API calls that missed the in-memory cache (disk may still hit)

    def clear_cache(self):
        self._cache.clear()

    def usage(self) -> dict:
        return self.client.usage()

    # ---- single ordering (for order / noise diagnostics) ----

    def sender_policy_one(self, inst, perm_idx: int, *, draw: int = 0):
        # Fixed state (perm_idx=0 render); only criteria order varies with perm_idx.
        # Matches TypeSafe order sensitivity and keeps counterfactual pairs aligned.
        key = ("S1ord", inst.family, inst.items, inst.target, inst.nuisance, perm_idx, draw)
        if key not in self._cache:
            qs = E.render_sender(inst, 0)
            vocab = E.family_vocab(inst.family)
            slots = []
            for slot, q in enumerate(qs):
                self.n_forwards += 1
                slots.append(_from_values(
                    self.client, q["state"], q["question"], list(vocab),
                    perm_idx=perm_idx, stream=1 + slot, seed=inst.seed, draw=draw,
                ))
            self._cache[key] = (slots[0], slots[1])
        return self._cache[key]

    def receiver_policy_one(self, inst, msg, perm_idx: int, *, draw: int = 0):
        key = ("R1ord", inst.family, inst.items, tuple(msg), perm_idx, draw)
        if key not in self._cache:
            q = E.render_receiver(inst, msg, 0)
            values = [E.describe(it) for it in inst.items]
            self.n_forwards += 1
            self._cache[key] = _from_values(
                self.client, q["state"], q["question"], values,
                perm_idx=perm_idx, stream=0, seed=inst.seed, draw=draw,
            )
        return self._cache[key]

    def sender_policy_p_one(self, inst, perm_idx: int, *, draw: int = 0):
        key = ("SPord", inst.family, inst.items, inst.target, inst.nuisance, perm_idx, draw)
        if key not in self._cache:
            q = E.render_sender_p(inst)
            self.n_forwards += 1
            self._cache[key] = _from_values(
                self.client, q["state"], q["question"], list(q["options"]),
                perm_idx=perm_idx, stream=1, seed=inst.seed, draw=draw,
            )
        return self._cache[key]

    def receiver_policy_p_one(self, inst, w, perm_idx: int, *, draw: int = 0):
        key = ("RPord", inst.family, inst.items, w, perm_idx, draw)
        if key not in self._cache:
            q = E.render_receiver_p(inst, w)
            values = list(q["options"])
            self.n_forwards += 1
            self._cache[key] = _from_values(
                self.client, q["state"], q["question"], values,
                perm_idx=perm_idx, stream=0, seed=inst.seed, draw=draw,
            )
        return self._cache[key]

    def sender_policy_hp_one(self, inst, i: int, perm_idx: int, *, draw: int = 0):
        key = ("SHPord", inst.id, i, perm_idx, draw,
               tuple(TypeSafePolicy._fact_key(f) for f in inst.private[i]),
               inst.kind, inst.holder, inst.requirement.dim)
        if key not in self._cache:
            q = E.render_sender_hp(inst, i)
            self.n_forwards += 1
            self._cache[key] = _from_values(
                self.client, q["state"], q["question"], list(q["options"]),
                perm_idx=perm_idx, stream=10 + i, seed=inst.seed, draw=draw,
            )
        return self._cache[key]

    def receiver_policy_hp_one(self, inst, j: int, fact, perm_idx: int, *, draw: int = 0):
        fk = TypeSafePolicy._fact_key(fact)
        key = ("RHPord", inst.id, j, fk, perm_idx, draw,
               tuple(TypeSafePolicy._fact_key(ff) for ff in inst.private[j]),
               inst.kind, inst.holder, inst.requirement.dim)
        if key not in self._cache:
            q = E.render_receiver_hp(inst, j, fact)
            self.n_forwards += 1
            self._cache[key] = _from_values(
                self.client, q["state"], q["question"], list(q["options"]),
                perm_idx=perm_idx, stream=20 + j, seed=inst.seed, draw=draw,
            )
        return self._cache[key]

    # ---- averaged over P (main eval interface) ----

    def sender_policy(self, inst, perm_idx=0):
        # External perm_idx ignored: we average all internal orderings.
        key = ("S", inst.family, inst.items, inst.target, inst.nuisance)
        if key not in self._cache:
            acc1 = acc2 = None
            for k in range(self.P):
                p1, p2 = self.sender_policy_one(inst, k, draw=0)
                acc1 = p1 if acc1 is None else acc1 + p1
                acc2 = p2 if acc2 is None else acc2 + p2
            self._cache[key] = (acc1 / self.P, acc2 / self.P)
        return self._cache[key]

    def receiver_policy(self, inst, msg, perm_idx=0):
        key = ("R", inst.family, inst.items, tuple(msg))
        if key not in self._cache:
            # Lazy: only the requested message. Pre-warming all V² pairs is right for
            # OpenJev prefix cache; for TypeSafe each message is a separate paid call.
            acc = None
            for k in range(self.P):
                p = self.receiver_policy_one(inst, msg, k, draw=0)
                acc = p if acc is None else acc + p
            self._cache[key] = acc / self.P
        return self._cache[key]

    def sender_policy_p(self, inst, perm_idx=0):
        key = ("SP", inst.family, inst.items, inst.target, inst.nuisance)
        if key not in self._cache:
            acc = None
            for k in range(self.P):
                p = self.sender_policy_p_one(inst, k, draw=0)
                acc = p if acc is None else acc + p
            self._cache[key] = acc / self.P
        return self._cache[key]

    def receiver_policy_p(self, inst, w, perm_idx=0):
        key = ("RP", inst.family, inst.items, w)
        if key not in self._cache:
            acc = None
            for k in range(self.P):
                p = self.receiver_policy_p_one(inst, w, k, draw=0)
                acc = p if acc is None else acc + p
            self._cache[key] = acc / self.P
        return self._cache[key]

    @staticmethod
    def _fact_key(f):
        if f is None:
            return ("None",)
        if isinstance(f, E.AdditiveHP):
            return ("A", f.option, f.word, f.weight)
        return ("M", f.option, f.dim, f.value)

    def sender_policy_hp(self, inst, i, perm_idx=0):
        key = ("SHP", inst.id, i,
               tuple(self._fact_key(f) for f in inst.private[i]),
               inst.kind, inst.holder, inst.requirement.dim)
        if key not in self._cache:
            acc = None
            for k in range(self.P):
                p = self.sender_policy_hp_one(inst, i, k, draw=0)
                acc = p if acc is None else acc + p
            self._cache[key] = acc / self.P
        return self._cache[key]

    def receiver_policy_hp(self, inst, j, fact, perm_idx=0):
        key = ("RHP", inst.id, j, self._fact_key(fact),
               tuple(self._fact_key(ff) for ff in inst.private[j]),
               inst.kind, inst.holder, inst.requirement.dim)
        if key not in self._cache:
            acc = None
            for k in range(self.P):
                p = self.receiver_policy_hp_one(inst, j, fact, k, draw=0)
                acc = p if acc is None else acc + p
            self._cache[key] = acc / self.P
        return self._cache[key]

    def receiver_policy_lv_one(self, inst, perm_idx: int, *, draw: int = 0):
        """L-VERIFY / Life rule head: π over 101 catalog descriptions (canonical order)."""
        import life_verify.env as LV
        q = LV.render_receiver_lv(inst)
        values = list(q["options"])
        self.n_forwards += 1
        return _from_values(
            self.client, q["state"], q["question"], values,
            perm_idx=perm_idx, stream=77, seed=inst.seed, draw=draw,
        )

    def receiver_policy_lv(self, inst, perm_idx=0):
        import life_verify.env as LV
        key = ("RLV", LV.instance_content_key(inst))
        if key not in self._cache:
            acc = None
            for k in range(self.P):
                p = self.receiver_policy_lv_one(inst, k, draw=0)
                acc = p if acc is None else acc + p
            self._cache[key] = acc / self.P
        return self._cache[key]


def l1(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.abs(a - b).sum())


def order_check_e1(policy: TypeSafePolicy, insts, *, n_questions: int = 20) -> dict:
    """L1 across P orderings on sender-word and receiver-item questions."""
    rows = {"sender_word": [], "receiver_item": []}
    count = 0
    for inst in insts:
        if count >= n_questions:
            break
        # sender slot 1
        dists = [policy.sender_policy_one(inst, k)[0] for k in range(policy.P)]
        rows["sender_word"].append(_pairwise_mean_l1(dists))
        count += 1
        if count >= n_questions:
            break
        vocab = E.family_vocab(inst.family)
        msg = (vocab[0], vocab[1])
        dists = [policy.receiver_policy_one(inst, msg, k) for k in range(policy.P)]
        rows["receiver_item"].append(_pairwise_mean_l1(dists))
        count += 1
    return {k: _summarise(v) for k, v in rows.items()}


def order_check_e1p(policy: TypeSafePolicy, insts, *, n_questions: int = 20) -> dict:
    rows = {"sender_word": [], "receiver_item": []}
    count = 0
    for inst in insts:
        if count >= n_questions:
            break
        dists = [policy.sender_policy_p_one(inst, k) for k in range(policy.P)]
        rows["sender_word"].append(_pairwise_mean_l1(dists))
        count += 1
        if count >= n_questions:
            break
        w = E.family_vocab(inst.family)[0]
        dists = [policy.receiver_policy_p_one(inst, w, k) for k in range(policy.P)]
        rows["receiver_item"].append(_pairwise_mean_l1(dists))
        count += 1
    return {k: _summarise(v) for k, v in rows.items()}


def order_check_ehp(policy: TypeSafePolicy, insts, *, n_questions: int = 20) -> dict:
    rows = {"sender_fact": [], "receiver_vote": []}
    count = 0
    for inst in insts:
        if count >= n_questions:
            break
        dists = [policy.sender_policy_hp_one(inst, 0, k) for k in range(policy.P)]
        rows["sender_fact"].append(_pairwise_mean_l1(dists))
        count += 1
        if count >= n_questions:
            break
        fact = inst.private[1][0]
        dists = [policy.receiver_policy_hp_one(inst, 0, fact, k) for k in range(policy.P)]
        rows["receiver_vote"].append(_pairwise_mean_l1(dists))
        count += 1
    return {k: _summarise(v) for k, v in rows.items()}


def noise_check_e1(policy: TypeSafePolicy, insts, *, n_questions: int = 20) -> dict:
    """L1 between two identical calls (draw=0 vs draw=1), fixed ordering perm_idx=0."""
    rows = {"sender_word": [], "receiver_item": []}
    count = 0
    for inst in insts:
        if count >= n_questions:
            break
        a = policy.sender_policy_one(inst, 0, draw=0)[0]
        b = policy.sender_policy_one(inst, 0, draw=1)[0]
        rows["sender_word"].append(l1(a, b))
        count += 1
        if count >= n_questions:
            break
        vocab = E.family_vocab(inst.family)
        msg = (vocab[0], vocab[1])
        a = policy.receiver_policy_one(inst, msg, 0, draw=0)
        b = policy.receiver_policy_one(inst, msg, 0, draw=1)
        rows["receiver_item"].append(l1(a, b))
        count += 1
    return {k: _summarise(v) for k, v in rows.items()}


def noise_check_e1p(policy: TypeSafePolicy, insts, *, n_questions: int = 20) -> dict:
    rows = {"sender_word": [], "receiver_item": []}
    count = 0
    for inst in insts:
        if count >= n_questions:
            break
        a = policy.sender_policy_p_one(inst, 0, draw=0)
        b = policy.sender_policy_p_one(inst, 0, draw=1)
        rows["sender_word"].append(l1(a, b))
        count += 1
        if count >= n_questions:
            break
        w = E.family_vocab(inst.family)[0]
        a = policy.receiver_policy_p_one(inst, w, 0, draw=0)
        b = policy.receiver_policy_p_one(inst, w, 0, draw=1)
        rows["receiver_item"].append(l1(a, b))
        count += 1
    return {k: _summarise(v) for k, v in rows.items()}


def noise_check_ehp(policy: TypeSafePolicy, insts, *, n_questions: int = 20) -> dict:
    rows = {"sender_fact": [], "receiver_vote": []}
    count = 0
    for inst in insts:
        if count >= n_questions:
            break
        a = policy.sender_policy_hp_one(inst, 0, 0, draw=0)
        b = policy.sender_policy_hp_one(inst, 0, 0, draw=1)
        rows["sender_fact"].append(l1(a, b))
        count += 1
        if count >= n_questions:
            break
        fact = inst.private[1][0]
        a = policy.receiver_policy_hp_one(inst, 0, fact, 0, draw=0)
        b = policy.receiver_policy_hp_one(inst, 0, fact, 0, draw=1)
        rows["receiver_vote"].append(l1(a, b))
        count += 1
    return {k: _summarise(v) for k, v in rows.items()}


def _pairwise_mean_l1(dists: list[np.ndarray]) -> float:
    if len(dists) < 2:
        return 0.0
    vals = []
    for i, j in itertools.combinations(range(len(dists)), 2):
        vals.append(l1(dists[i], dists[j]))
    return float(np.mean(vals))


def _summarise(vals: list[float]) -> dict:
    if not vals:
        return {"n": 0, "mean_l1": None, "max_l1": None}
    return {
        "n": len(vals),
        "mean_l1": float(np.mean(vals)),
        "max_l1": float(np.max(vals)),
        "p50_l1": float(np.median(vals)),
    }

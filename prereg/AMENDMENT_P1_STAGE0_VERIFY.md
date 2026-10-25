# Amendment — P1 stage 0: can one-pass agents verify a single rule against their own example?

**Status:** locked 2026-10-25, after the dry build in `runs/p1_stage0/gate.json`. No call was
made before this lock. Local arms are pre-approved and wait for the wave-2a servers. The Luna
arms run inside the $20 envelope. Parent: `RESEARCH_ROADMAP.md`, protocol track P1.

## Why this comes first

P1 replaces votes ("my rule is X") with evidence ("rule X does not fit my example") and lets the
population intersect the exclusions. The roadmap says one-op checks are within one-pass reach. That
is not enough. Every candidate that competes with P_e has to be excluded, and P_e itself is two-op,
so its yes answers must be reliable too. What a one-pass agent does on a two-op check of a *given*
rule has not been measured. The first article measured pair choice: one-pass two-op accuracy was
0.59, for Luna Decisions and for Responses at effort none. A yes/no check of one given rule is a
different task, and it could be easier or harder.

The protocol P1 can use is decided by this measurement. The decision rule is fixed below, before
any data.

## Items

- **Examples:** worlds 1, 3 and 5. These are the three worlds where P_e is the prefix plus one
  swap. Each world has 100 cell examples.
- **Candidate rules for each example:** 8, chosen by the hash
  `sha256("p1s0|{world}|{cell}|{slot}")` within each slot, with the truth computed by code:
  - P_e;
  - the prefix (it fits 75 of 100 by construction);
  - 2 other rules from the cell's S_c (fitting);
  - 2 non-fitting one-op catalog rules;
  - 2 non-fitting two-op catalog rules.
- **Size:** 2,272 items (dry build, `runs/p1_stage0/items.json`, sha256 `cad6dfa8…`). The written
  3 × 100 × 8 = 2,400 cannot be built. Sixteen world-1 class-A cells have only one fitting rule left
  after P_e and the prefix: cells 8, 21, 22, 26, 28, 34, 35, 57, 59, 68, 70, 72, 78, 88, 92 and 95.
  Their second "other fitting" slot is left empty rather than filled with a repeat or a substitute.
  All rates are computed per n_ops and fit status, so the missing slots change counts, not
  definitions. Fitting and non-fitting are reported by n_ops (one-op, two-op)
  and by class (A, B).
- **Prompt:** one state text for every model. It is built from the Life cell prompt's own blocks,
  quoted. It contains the Life constitution's first block, the cell's private example line in the
  Life format, and then: "Candidate rule: <rule description>. Does this rule map the example's
  input to its output?" The Life prompt has no glossary of operations. Rules appear only as catalog
  descriptions, such as `shift_symbols(1);swap(2,3)`, and the model infers their meaning as it does
  in Life. No definitions are added. The dry build quotes world 1, cell 0, slot 0:

```
You are one cell among 100 on a wrapping 10×10 grid.

Each cell has its own private task for this epoch: a hidden transformation of 4-symbol strings over A–H. Every cell in the epoch has the same hidden transformation, but different private examples and a different query each generation. There is no shared score.

Private examples:
  DHFB -> EACG

Candidate rule: shift_symbols(1);swap(2,3). Does this rule map the example's input to its output?
```

  There is no inbox, no memory and no catalog list. This is an isolated check, so nothing social enters.
- **Answer:** Yes or No. Decision arms read the two labels. Generation arms return JSON
  `{"fits": true|false}` under a strict schema. The schema applies only after the reasoning
  channel, as the wave-2b reasoning gate checks.

## Arms

| arm | agent | kind |
|---|---|---|
| S0-lmdec | Luna Decisions, yes/no, P = 2 orderings (Yes/No swapped), argmax of the average | one pass |
| S0-lmnone | Luna Responses, effort none | one pass |
| S0-q3L0 | AnyJev 0.3.0 L0 on Qwen3-4B, `yes_no`, both orderings, prior `none` | one pass |
| S0-tacit | Tacit-4B, `yes_no`, one pass | one pass |
| S0-lmmed | Luna Responses, effort medium | reasoning reference |
| S0-q3think | Qwen3-4B, thinking on, card decoding | reasoning reference, same base as Tacit |

The revisions, decoding and gates are as locked in the wave-2a amendment. That includes the answer
mass m ≥ 0.99 per question for decision arms, and the sampler gate for local engines. Cost:
- S0-lmdec: 2,272 × 2 Decisions calls, the built items;
- S0-lmnone and S0-lmmed: 2,272 Responses calls each.

The cost is from stored token counts, with a cap at twice the estimate. The price below uses
2,400 items, the written size, so the cap sits above the built set. Uncached input is $0.10/M
and output is $0.50/M. Decisions input is 0.497 tokens per character on 480 stored rows, and
those rows have no output tokens. Responses input is 0.417 tokens per character on 480 stored
rows. Effort-none output averages 28.43 tokens. Effort-medium output averages 316.05 tokens on
the 80 stored QI-1b calls.

| arm | priced calls | input mean | output mean | estimate | cap |
|---|---:|---:|---:|---:|---:|
| S0-lmdec | 4,800 | 249.03 | 0 | $0.1195 | $0.2391 |
| S0-lmnone | 2,400 | 184.62 | 28.43 | $0.0784 | $0.1569 |
| S0-lmmed | 2,400 | 184.62 | 316.05 | $0.4236 | $0.8471 |

The three estimates sum to $0.6215 and the caps to $1.2431. Spent $10.0983. Projection $10.7198
of $20, so the run does not stop to ask. Exact figures are in `runs/p1_stage0/gate.json`.

## Measures (per arm, by n_ops and class)

- TPR = P(yes | fits) and FPR = P(yes | not fits), with Wilson 95% intervals and the cluster
  bootstrap over examples (the panel hull).
- Youden J = TPR − FPR.
- Calibration of decision-arm probabilities (reliability by decile), descriptive.

## The aggregation criterion (derived now)

Under P1, n cells each check a candidate R against their own examples, and the count of "no" answers
excludes R. A rule that fits a share f_R of examples gets yes answers at the rate
q_R = f_R·TPR_k + (1 − f_R)·FPR_k, where k is R's number of operations. The protocol has to rank P_e
above every competitor. The binding competitor is the prefix (one-op, f = 0.75):

- Δ = q(P_e) − q(prefix) = TPR_2 − (0.75·TPR_1 + 0.25·FPR_1).
- The separation is detectable at n voters if Δ > 1.645 · sqrt(q_e(1 − q_e)/n + q_p(1 − q_p)/n), a
  one-sided 95% normal bound.

It is evaluated at:
- n = 100, global pooling, `all`;
- n = 9, a lattice neighbourhood including the cell itself.

The rates are the measured point estimates. The same rule is also evaluated at the lower hull bound
of Δ.

## Decision rule (locked)

Per one-pass arm:

- **D-global:** the separation holds at n = 100 with Δ at its lower hull bound. That arm is a P1
  candidate on `all`.
- **D-local:** the separation holds at n = 9, with Δ at its point estimate. That arm is a P1
  candidate on the lattice as well. This is a one-shot criterion and therefore conservative. Even
  perfect checkers only just pass it (Δ = 0.25 against a bound of 0.237), and on the lattice,
  evidence also propagates over rounds beyond one neighbourhood. A D-local failure is read as "no
  one-shot local separation", not as "infeasible on the lattice".
- **D-none:** the separation fails at n = 100. P1 as exclusion messages is not feasible for that
  agent on this task. The readout says so, and the protocol track moves to a design that supplies
  verification from the environment (the QX-2 direction), rather than from the agent.

Every arm, whatever its outcome, is reported against the reasoning references.

## Predictions (locked)

The unit is the example, clustered by cell, with sign-flip over examples on paired items. α = 0.05,
one-sided.

- **V1 (two-op checking is weaker than one-op checking without reasoning):** for S0-lmdec and
  S0-q3L0, J(two-op) < J(one-op).
- **V2 (reasoning closes the gap):** J(two-op) of S0-lmmed > J(two-op) of S0-lmdec, and J(two-op) of
  S0-q3think > J(two-op) of S0-q3L0.
- **Not predicted:**
  - whether any one-pass arm meets D-global or D-local; the decision rule above is what is read;
  - Tacit against L0 on this task. It is descriptive here; the class-B 0/8 test T1 is in wave 2a.

## Pre-stated readings

- **A one-pass arm meets D-global but not D-local:** evidence aggregation favours `all` (global
  pooling), while voting favoured the lattice (the local veto). P1 then predicts that the ranking of
  the two topologies reverses under the evidence protocol. That would be a strong, testable claim
  for P1 proper.
- **D-local holds:** P1 runs on both topologies.
- **D-none for every one-pass arm:** a one-pass agent cannot supply even the evidence a collective
  would need. The route to collective intelligence among decision agents then runs through
  environment-supplied verification, not message formats. That is a substantive negative result
  and is written up as such.
- **If the design is the cause:**
  - The state text is not the Life prompt, and a model may check better or worse outside its
    context. The P1 runs use the Life prompt, and stage 1 re-measures TPR and FPR inside it.
  - Yes/no wording bias is handled by both orderings for decision arms. For generation arms it is
    read from FPR.

## Design audit

1. **Fidelity.** The blocks are quoted from the Life prompt builder, and the truth comes from the
   catalog functions. The dry build recomputed every label with an independent implementation of
   the operations: it agrees with the catalog on all 101 rules for all 300 examples. The prefix
   fits 75 of 100 examples in each of worlds 1, 3 and 5. The item file's sha256 is
   `cad6dfa8bfe8d83ef6402901300c97a946e90486d02d449e6231e31a55cf859b`.
2. **Coverage.** Worlds 1, 3 and 5, with one-op and two-op balanced inside each item group. Worlds 2
   and 4 are excluded, as in QX-1.
3. **Controls.** The reasoning references sit on the same items. Both orderings are used for the
   decision arms.
4. **Observability.** One isolated item per call. Nothing from other cells.
5. **Gate consistency.** The label recomputation, prompt identity across models, the answer mass m,
   the sampler gate and the cost cap run together before any battery call.
6. **Statistical unit.** The example, clustered by cell: 300 examples, 8 items each.
7. **Pre-stated readings.** Above.

## Queue

Luna arms run as soon as this file is locked: API, no GPU. Local arms run after wave 2a, on the same
servers.
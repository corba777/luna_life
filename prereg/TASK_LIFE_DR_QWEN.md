# Task — Qwen3-4B-Thinking in the clean distributed world

**Status:** locked. The Q2' threshold 0.92 is confirmed. This file is the lock, before Stage 1.
Local model via SGLang, no API cost. Parents: `TASK_LIFE_DR_TOPOLOGY.md` and
its amendments, `runs/life_dr_topology/readout_final.md`,
`runs/life_dr_topology/review_checks.md`,
`runs/life_distributed/decisions_discovery_note.md`, `ARM_REGISTRY.md`.

## Amendment (locked)

Three changes, from the external review and from `review_checks.md`.

1. **Q2'.** On the same `all` replicates as Q2, also score the prefix-rejection agreement:
   the share of cells for which "does not hold the modal wrong rule at g20" and "own example
   rules that rule out" give the same answer. The threshold is ≥ 0.92, confirmed, the lowest
   value on the five Luna `all` runs whose modal wrong rule is the prefix (0.96, 0.92, 1.00,
   1.00, 1.00). On those five runs this agreement equals the Q2 agreement, except w3 r2, where
   Q2 is 0.99 and this agreement is 1.00, because one cell holds a third rule.
2. **Q1 and Q2 are conditional on the modal wrong rule.** They are scored only when that rule
   at g20 is the prefix (the first operation of P_e). A replicate whose modal wrong rule is
   something else is "not the prefix", not a pass and not a fail. World 2 on Luna is the case
   this excludes: the prefix fits 75, and the runs settled on `swap(1,2)`.
3. **Stage 0, the 25 cells.** In the chosen world, 25 examples rule the prefix out (worlds 1,
   3 and 5; the same count holds in world 2; world 4's first operation fits 0, and world 4 is
   not eligible to be chosen). Report how many of those 25 do not hold the prefix at g1, and
   how many hold P_e at g1. The same two counts are reported for every world. They do not
   enter the go rule.

## Why

Luna with reasoning finds the rule in the clean distributed world, and topology then decides how the
rule spreads. Luna Decisions almost never finds it (2 finds in 4320 cell-rounds without a channel, 0
with one). The open question is whether a small local reasoning model finds and spreads it.

The topology run also produced a prediction that comes from the world design and not from a fit.
In `all`, if the true rule does not win the plurality at the first mass publication, the population
settles on the simpler prefix rule (the first operation of P_e, which fits 75 of 100 examples). Only
the 25 cells whose own example rules the prefix out keep P_e. This was found post hoc on Luna. Here
it is tested on a second model, locked in advance.

## Agent

Registry name prefix `dist/qwen4bT.local`. Qwen3-4B-Thinking-2507, the same weights, SGLang
settings, thinking mode, sampling and max-token limit as the earlier Qwen runs. The agent copies them
from the earlier manifest and records them. The prompt, catalog, schema and parser are byte-identical
to DRc, apart from the inbox block in `all` and its slot-count sentence, as in the topology task.
Each cell sees its own single example.

## Stage 0 — round-1 probe (go/no-go)

- All 5 worlds, 100 cells, round 1 only, 1 replicate, `moore` (round 1 has an empty inbox in every
  topology, so this probe serves all of them).
- Report per world: g1 P_e holders, the modal rule and its share, the parse-failure and truncation
  counts, median and 99th-percentile thinking tokens, and GPU time per decision.
- Also, per world, among the cells whose example rules out the prefix: how many do not hold the
  prefix at g1, and how many hold P_e at g1. In worlds 1, 2, 3 and 5 that set has 25 cells. In
  world 4 the first operation of P_e fits no example, so the set is all 100 cells and the two
  counts are still reported. The go rule does not use these counts. The chosen world's two
  counts are the ones named in the amendment.
- **Go rule (from Luna data):** go to Stage 1 if at least one of worlds 1, 3, 5 has ≥ 3 g1 holders.
  Reason: 3 g1 holders is the smallest seed from which a Luna lattice run took off (DRc world 2, r1).
  Below it, no Luna run nucleated, and the lattice outcome for Qwen would be the floor.
- If no world meets the rule, stop. Record the g1 counts as the result.

## Stage 1 — lattice and all, one world

- World: the one of 1, 3, 5 with the most g1 holders in Stage 0 (ties: lowest world number).
- Arms: `dist/qwen4bT.local/moore/none` and `dist/qwen4bT.local/all/none`. 2 independent replicates
  each, 20 rounds. EPOCH_LENGTH set to at least 21. P_e and the example hash are checked every round.
  Replicates use separate caches and make their own calls on identical round-1 prompts.
- GPU time is estimated from the Stage 0 timing, plus a one-round probe of `all` at round 5 (a full
  inbox), before launch. That estimate is reported to Artem before the full launch.

## Predictions (locked)

Let x(g) be the share of the 100 cells holding P_e at round g.

- **Q1 (all, the plateau).** For each `all` replicate where P_e is **not** the plurality among the
  messages published at round 2 (read from the round-3 inbox), **and** the modal wrong rule at g20
  is the prefix: x(20) ∈ [0.21, 0.29]. The centre, 0.25, is the design count of examples that the
  prefix rule does not fit. The half-width, 0.04, is the largest deviation from 0.25 in the five
  Luna plateau runs (0.23 to 0.29). It is a measured tolerance, not a guess. If the modal wrong
  rule is not the prefix, the replicate is "not the prefix".
- **Q2 (all, who holds the truth).** In the same runs, the agreement between "holds P_e at g20" and
  "own example inconsistent with the modal non-P_e rule" is ≥ 0.92. That is the lowest Luna value.
  The modal-is-the-prefix condition is part of "the same runs".
- **Q2' (all, prefix rejection).** In the same runs, the agreement between "does not hold the modal
  wrong rule at g20" and "own example rules that rule out" is ≥ 0.92. Confirmed. That is the lowest
  value on the five Luna prefix-modal runs in `review_checks.md`.
- **Q3 (all, tipping).** For each `all` replicate where P_e **is** the plurality among the round-2
  messages: x(20) ≥ 0.90. In Luna this happened once (w5 r1), and that run reached 1.00 by round 3.
- **Descriptive:** the lattice x(g) against DRc in the same world; the P(adopt | k_published) curve
  against Luna's; independent finds per round; replicate agreement.

Q1, Q2 and Q2' are read only for the replicates whose conditions hold, including the requirement
that the modal wrong rule at g20 is the prefix. If no replicate meets a condition, that prediction
is reported as "not reached", not as a pass or a fail. A replicate that meets the round-2 condition
and whose modal wrong rule is not the prefix is reported as "not the prefix".

## Readout

Stage 0 table, including the two prefix-cell counts; then x(g) per run; Q1, Q2, Q2' and Q3 verdicts; the descriptive tables; and a J(g) figure,
one panel per topology, with the DRc and Luna-`all` runs of the same world shown faintly.

## Constraints

Same prompt for all models. Thinking text from Qwen is local and may be stored for debugging, but it is
not used as training data in this task. New runner, committed before launch; edit no running script.
nohup, a liveness watchdog with no auto-relaunch, and the manifest under a lock. Amendments come
before numbers.
# Addendum — informativeness as the primary QX measure (QX-1r and the unrun QX-1p arms)

**Status:** locked 2026-10-28. Pre-run addendum: it applies only to arms with no call yet (QX-1r; QX-1p
arms QXp-oss120, QXp-qi, QXp-gemma-off/on, QXp-nemo-off/on, QXp-flint). Arms already run (QX-1 Qwen,
QXp-lmmed, QXp-lmnone, QXp-oss20) keep their locked verdicts; the new measure is reported for them as
descriptive, labelled post hoc. Dry build: `runs/life_dr_qwen/qx_informativeness/dry_build.json`
(`ok: true`; informative ≡ separates on all four run arms; 4,096-input gates pass; baseline mean
0.98665…). Basis: `AMENDMENT_DR_QWEN_QX1.md`, `AMENDMENT_QX1P_PANEL.md`, `AMENDMENT_QX1R.md`,
`QX_TRACK_PLAN.md`. Mirror: Life surface → `luna_life` `prereg/` when committed.

## Why

The question (Valko): under a shared wrong hypothesis, does an agent choose an experiment that could
reveal the error, and does the consensus make that less likely?

The locked measure so far is "confirming": the test input has equal letters at the world's swap
pair, so the true rule and the prefix give the same output. That measure uses the truth, which the
agent does not have, and in practice it mostly tracks a model's preference for constant strings such
as `AAAA`. X1a (aimed confirming) was added to correct that, at the cost of clarity.

A measure that asks the question directly and uses only what the agent knows: does the chosen test
distinguish the rule the agent holds from at least one other rule that also fits the agent's own
example? A careful experimenter picks such a test. It is already computed in every QX readout as
"separates".

## Measures (per call)

- **Informative (agent-centred, primary):** with held rule R (the prefix, by the constructed memory)
  and own consistent set S_c, the test x is informative iff there is r ∈ S_c, r ≠ R, with
  r(x) ≠ R(x).
- **Refuting (truth-centred, secondary):** P_e(x) ≠ prefix(x). This is the complement of
  "confirming".
- **Baseline:** for each cell, the share of all 4,096 inputs that are informative (mean ≈ 0.987).
  Reported beside, not a threshold.

## Predictions (locked for each arm with no call yet)

Unit: the cell (60), draws pooled. Paired sign-flip over cells, exact enumeration when ≤ 20
non-zero cells, otherwise 10^6 flips with the tolerance rule; α = 0.05. The gate (> 5 % failures in
a condition) applies to every test that uses that condition.

- **S1 (consensus lowers informativeness):** P(informative | C1) < P(informative | C0), one-sided.
- **S2 (individual quality against chance, two-sided, descriptive):** P(informative | C0) against
  the cell's random baseline, as the mean of per-cell differences, with its hull.

X1 and X1a stay as locked for QX-1r and keep their pre-stated readings. In the QX-1r readout S1 is
listed first.

## Pre-stated readings

- **S1 holds:** consensus makes the agent's chosen experiment less able to reveal the error. This is
  the direct answer to the question at the level of one agent's choice.
- **S1 fails, S2 near 0 (informative ≈ baseline):** the agent picks experiments as informative as
  random inputs, with or without consensus. An experimenting population would find the error, and
  QX-2 needs a tight budget to stay collective.
- **S1 fails, S2 well below 0:** the agent picks uninformative experiments regardless of the inbox.
  The obstacle is individual test choice, not social pressure.

## Already-run arms (descriptive, post hoc)

Report informative C0 / C1 and S1's statistic for QX-1 Qwen (164/240, 147/240), QXp-lmmed (240,
238), QXp-lmnone (gated; descriptive), QXp-oss20 (154, 165), labelled post hoc. QX-1r is the
confirmatory test for Qwen.

## QX-2 (planning note, not locked here)

QX-2 returns the experiment's result. Its primary outcome is population-level: share of runs in
which the false consensus is abandoned, and time to first refutation, against the no-experiment
runs. Informativeness of chosen tests is its mechanism measure.

## Gates

The informative and refuting functions are checked on all 4,096 inputs for every selected cell:
the prefix's own outputs are never "informative against itself"; P_e is in every S_c; the counts on
already-run arms reproduce the "separates" column of their readouts exactly.
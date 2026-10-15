# Task — Remove the cell's own evidence (DR-noex): is the check what makes the population work?

**Status:** **locked** 2026-10-15. Predictions locked with this file, before any run. API only (Luna
Responses, `effort=medium`). Follows `DESIGN_CHECKLIST.md` and the standing rules in `PLAN_NEXT.md`.
Parents: `TASK_LIFE_DISTRIBUTED.md` (DR, DRs), `TASK_LIFE_DRO_ITER.md`,
`runs/life_distributed/adopt_consistency.md` (post-hoc). Gate: `prompts/dr_noex_gate.md` (PASS).

## Why

Post-hoc counts over every received rule (DR, pooled): a rule that is the inbox majority and fits the
cell's example is adopted 64.5% of the time (443/687); a majority rule that contradicts the example,
1.8% (7/396). One-pass cells (DC): 16.6% vs 8.0%. The reading is that reasoning cells filter incoming
rules against their own example, and that this filter is what lets the true rule spread. This task
tests it causally: remove the example after the first round and see whether the population effect
survives.

Note: removing the example removes the cell's evidence, not only a "checking step". The claim tested
is that own evidence at decision time is necessary for the collective effect.

## Arm

| arm | cells | g1 prompt | g ≥ 2 prompt | channel |
|---|---|---|---|---|
| **DR-noex** | Luna Responses, `effort=medium` | identical to DR | DR prompt with the private-examples block removed | rules only, as DR |

- Same five worlds, seeds, catalog, channel filter, memory line (`rule='…' published=…`), query,
  schema and parser as DR. 10 generations, 100 cells, no sources, no feedback.
- From g2 the examples block is replaced by the fixed line `Your private example is not shown this
  generation.` and the constitution's "You see your private examples, …" sentence is replaced by
  "You saw your private example in the first generation; from now on you see your current query, …"
  (exact text fixed in the gate file before the run). Nothing else changes.

## Gate

- g1: payload byte-identical to DR g1 for the same seed and cell (runner's request builder, raw bytes).
- g2 dry render (3 cells): diff vs DR g2 with the same forced history; allowed differences only the
  examples block and the one constitution sentence, listed verbatim in `prompts/dr_noex_gate.md`.
- Runtime masked check at g2 of seed 1 before any g3 request; fresh empty `cache_DR_noex`; per-generation
  live/cached/fallback log; fail if g ≥ 2 has 0 live requests.

## Metrics

J(g) for all 100 cells, J@g10 per seed and seed mean; P(adopt | consistent) and P(adopt | inconsistent)
with the majority split, same definitions as `adopt_consistency.md` (consistency is computed against the
cell's hidden example); cost.

## Predictions (lock)

- **N1 (primary):** DR-noex J@g10 ≤ DR J@g10 − 0.40 in at least 4 of 5 worlds (DR: 1.00, 0.80, 0.75,
  0.71, 1.00).
- **N2:** DR-noex seed-mean J@g10 ≤ 0.40.
- **N3 (descriptive):** P(adopt | majority ∧ inconsistent) for DR-noex vs DR (0.018) and DC (0.080).

## Readout

- **N1 PASS:** without its own evidence at decision time, the population loses most of the effect; the
  check against private evidence is necessary for it.
- **N1 FAIL:** the population still converges without per-round evidence; the effect is carried by
  something else (first-round choices plus memory and spreading). Report N3 and the g1 composition.

## Cost

DR cost ≈ $0.36 per world (Phase 1); five worlds ≈ $2 (shorter prompts from g2). Alarm $5.

## Artifacts

`prompts/dr_noex_gate.md`, `runs/life_distributed/DR_noex/seed{n}/`,
`runs/life_distributed/dr_noex_summary.json` (N1–N3 with DR, DRs, DC alongside),
`fig_dr_noex.png` (J(g): DR, DR-noex, DRs).
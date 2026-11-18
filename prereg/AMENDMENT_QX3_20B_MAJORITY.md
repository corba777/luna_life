# Amendment — QX-3: does gpt-oss-20b follow a majority of rule names?

**Status:** locked v2 (2026-11-18), written by the reviewer for Artem. v2 states the rejection rule
(dry build of v1). It must be locked before anyone
computes the majority-step measure on the gpt-oss-20b main-phase runs (r2–r5); if that measure is
computed first, for this model, by anyone, this amendment is void as a test and its result is reported
as post hoc. It adds no model call.

## Why

For Luna, a cell without evidence leaves H_F almost only when five or more of its eight neighbours name
another rule: Family S held in five runs of world 0 (`AMENDMENT_QX3_MAIN.md`) and W-S in five worlds
(`AMENDMENT_QX3_WORLDS.md`); over the five worlds, 2 of 356 cells left at one to four naming neighbours
and 187 of 208 at five or more.

In the one gpt-oss-20b rule-only run looked at so far (pilot r1, δ = 1/8, B = 1, entry 6), counted after
the data, no cell without evidence left H_F: 0 of 90 at one to four and 0 of 11 at five or more. This
amendment fixes, before the main-phase gpt-oss-20b runs are read for it, a test of whether gpt-oss-20b
follows a majority less than Luna does.

## Data

**gpt-oss-20b · δ 1/8 · B 1 · rule only · world 0**, runs r2–r5 of the QX-3 main phase
(`qx3_20b_d8_B1_R_r2` … `_r5`), when all four have finished. The pilot run r1, where the observation was
made, is not used in the test.

**Luna · δ 1/8 · B 1 · rule only · world 0**, runs r2–r6 of the main phase (the Family S runs), already
read.

## Measure

Exactly the Family S measure of `AMENDMENT_QX3_MAIN.md`: in each run, the cells that held H_F at g − 1
and have no counterexample of their own in memory at g; k = the number of their neighbours that named a
rule other than H_F in generation g − 1; per cell, its first generation with k ≥ 5 (and, reported beside
it, its first with 1 ≤ k ≤ 4). **p_high** = the share of those cells that hold another rule at that
generation. Keys are read from the trace, or computed from `build_world(0)` and checked.

A run with fewer than 5 cells in the k ≥ 5 group has no p_high and is left out of the test, and the
number left out is reported.

Luna's p_high values, already computed: r2 32/32, r3 32/36, r4 37/42, r5 36/38, r6 29/35.

## Test

**T-M: gpt-oss-20b's p_high is below Luna's.** One-sided exact permutation test on the run values of
p_high, the gpt-oss-20b runs against the five Luna runs, ties counted against rejection (`THEORY.md`
§8.2), α = 0.05. With four gpt-oss-20b runs there are 126 splits (smallest p 1/126); with three, 56.
T-M holds when p ≤ 0.05; complete separation (every gpt-oss-20b run below every Luna run, p = 1/126
with four runs) is not required. With the Luna values above and four gpt-oss-20b runs, up to six
splits at least as extreme as the observed one still give p ≤ 0.05. If fewer than three gpt-oss-20b
runs have a p_high, T-M is not decided.

## Prediction stated in advance

T-M holds. Basis: 0 of 11 in the pilot against 187 of 208 for Luna across worlds; gpt-oss-20b also
shares results in about 2 % of its messages and sends nothing in about 14 % of its turns, so it may weigh
its neighbours little in general.

## Readings stated in advance

| pattern | reading |
|---|---|
| T-M holds, gpt-oss-20b p_high near 0 | gpt-oss-20b does not follow a majority of names; the majority step is a property of Luna, not of the setup. |
| T-M holds, gpt-oss-20b p_high clearly above 0 | gpt-oss-20b follows a majority, but less often than Luna. |
| T-M does not hold | The pilot observation does not repeat; the per-run shares are the summary. |
| T-M not decided | Too few gpt-oss-20b cells ever had five naming neighbours; reported as such. |

The one-to-four group is reported for both models with no test.

## Also reported, no test

The same measure on the gpt-oss-20b rule-only runs of `AMENDMENT_QX3_WORLDS.md` (worlds 1–3) when they
exist, and on the gpt-oss-20b runs with results (descriptive, as in the reviewer's count of 2026-11-18,
where cells without evidence rarely reach five naming neighbours).

## Dry build (CPU, no model call)

1. The measure code (the Family S code with p_high) on the Luna r2–r6 traces, reproducing the values
   above, and on the gpt-oss-20b pilot r1 trace, reproducing 0 of 90 and 0 of 11.
2. The test on constructed values: four runs all below five gives 1/126; ties; a run with fewer than 5
   cells left out; fewer than three runs not decided.
3. A statement from the agent that the majority-step measure has not been computed on
   `qx3_20b_d8_B1_R_r2`–`_r5`, and that the Family B readout code does not compute it before the lock;
   if the main-phase readout's "dose table of arm R" includes these runs, it is held back until the
   lock.

## Outputs

The readout with T-M, the per-run tables for both models, and a recheck package with SHA256SUMS.
Nothing enters the QX page before the reviewer's recheck.

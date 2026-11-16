# Amendment — QX-3 pilot addition: rule only at a high dose of names (Luna, δ = 1/8)

**Status:** locked v2 (2026-11-16), after the dry build and the reviewer's review. No call is made
before Artem's go, logged in the switch log with his words.

## Why

In the QX-3 Luna pilot (`AMENDMENT_QX3_PILOT.md`, δ = 1/64), the rule-only arm had three finders
(readout v2: cells with an own result that contradicts H_F). A cell on H_F heard another rule
named by one neighbour in 299 cell-generations, by two in 32 and by three in 1. It left H_F once.
The arm therefore tested one dose: one neighbour of eight.

In the paper's Life world, a rule name alone does spread, and there a quarter of the cells name
the true rule from round 1. Luna is a threshold responder there. The pilot cannot say whether Luna
ignores rule names in this world, or only ignores one name of eight.

This addition runs the rule-only arm where many cells find the error, so that cells without
evidence of their own hear another rule from several neighbours.

## Run

- **Model and arm:** Luna, arm R (rule only), as locked in `AMENDMENT_QX3_PILOT.md`: same engine,
  prompt, schema, decoding and G = 24.
- **Cell:** δ = 1/8, B = 1. In the two QX-2 Luna runs of this cell, 44 and 46 cells found a
  counterexample by generation 12.
- **Runs and calls:** 1 run, 2,400 calls. Run name `qx3_luna_d8_B1_R_r1`; the cache key includes
  the arm and the run.
- **Cost:** at the measured arm-R rate ($0.000422 per call), about $1.01. Hard stop $2.00.
  Envelope left before this run: $11.06 (2026-11-16).
- **Runner:** `runs/run_qx3_luna_r_dose.py`, a new file. The files pinned by the QX-3 20b manifest
  are not edited. The spend ledger starts from the non-cached rows already in this run's
  `calls.jsonl`, so a restart cannot reset the stop.

No R+E or forced arm is run in this cell. With results in messages, Luna had 94 and 96 cells on
H_T at generation 6 and 100 by generation 10 in the QX-2 runs, so those arms would add nothing.

## Measures (descriptive)

A cell is **without evidence** at generation g if its memory at g holds no result that
contradicts H_F (own or received; in arm R nothing is received).

For a cell at generation g, **k** is the number of its neighbours that named a rule other than
H_F in generation g − 1. This is the primary definition. The same tables are reported beside it
for neighbours that named H_T.

1. **Dose table.** For cells that held H_F at generation g − 1 and are without evidence at g, by
   k = 0, 1, 2, 3, 4+ and for k ≥ 3 together: cell-generations, and how many hold another rule at
   generation g.
2. **First exposure at k ≥ 3.** Take each cell's first generation g with k ≥ 3 at which it held
   H_F at g − 1 and is without evidence. Count the cells that hold another rule at generation g or
   g + 1. This is the window behind the pilot's 74 of 91 and 90 of 96. A cell whose own
   counterexample arrives at g or g + 1 is excluded and counted separately.
3. The pilot's readout fields for arm R, with finders as in readout v2: every cell with an own
   result that contradicts H_F, and the rule it ends on.

## Intervals and their level

Each proportion is reported with an exact (Clopper–Pearson) interval. The readings below rest on
two comparisons, so by the Bonferroni correction each interval is taken at level
1 − 0.05/2 = 97.5 %, which keeps the joint coverage at 95 % or more (`THEORY.md`, §8).

The intervals treat observations as independent. In measure 1 the same cell appears in several
generations, so those intervals are nominal; the number of distinct cells is reported beside
each row. Measure 2 has one observation per cell.

## References, from the pilot's measured rates (proportions, 97.5 % intervals)

- **No-name-effect level.** Pilot arm R, one naming neighbour: 1 of 299 cell-generations left H_F,
  interval [0.0000, 0.021]. The reference is its upper bound, 0.021.
- **Evidence level.** Pilot arm R+E: 74 of 91 cells left H_F in the window of measure 2,
  interval [0.70, 0.90]. Arm R+E forced, beside it: 90 of 96, [0.86, 0.98].

**Smallest informative sample.** With no cell leaving, the upper bound of measure 1 falls to
0.021 only when n ≥ ln(0.0125) / ln(1 − 0.021) = 207 cell-generations. Below that, "no dose
effect" cannot be read from this run.

## Readings stated in advance

| observation | reading |
|---|---|
| Measure 1 at k ≥ 3: lower bound above 0.021 | Rule names move Luna at a high dose. The pilot's rule-only result holds for one name of eight, not for names in general. |
| … and measure 2: interval overlaps [0.70, 0.90] | At that dose a name is about as strong as a counterexample. |
| … and measure 2: upper bound below 0.70 | Names move Luna at a high dose, but less than a counterexample does. |
| Measure 1 at k ≥ 3: upper bound at or below 0.021 | No dose effect found. Rule names do not move Luna here even when several neighbours give them. |
| Neither bound condition met (this includes n < 207 with no cell leaving) | Not decided by this run. Reported as such. |

There is no test and no p-value. A main-phase amendment may add a locked test, sized from this run.

## Gates and dry build (CPU, no model call)

- Format gate as in the pilot.
- **Prompt identity.** The generation-1 schema equals the pilot's pinned arm-R schema. The
  empty-inbox render equals the pinned file `20b_gen1_prompt_R.txt`, which is the same text as the
  Luna pin. The prompt the engine sends at generation 1 is that text with the eight slots filled by
  the generation-0 seed messages, each naming H_F, as in the pilot. The stub's cell-0 prompt equals
  the engine's.
- The stub runs the arm through the engine with every invariant asserted.
- The readout reproduces, on the pilot's δ = 1/64 arm-R trace, the split 299 / 32 / 1 with one
  leave at k = 1, and on the R+E and forced traces 74 of 91 and 90 of 96.
- Scripted reference for this cell under arm R (random agent, G = 24), copied from the pilot's dry
  build: abandonment 0.124 and recovery 0.045 at generations 12 and 24.
- Calls, cost at the measured rate, and the envelope left.

## Outputs

Calls (final text and usage, no reasoning), the trace, the readout and a recheck package with
SHA256SUMS. Nothing enters the QX page before the reviewer's recheck from raw data.

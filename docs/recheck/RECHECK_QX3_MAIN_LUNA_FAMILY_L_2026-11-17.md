# Recheck — QX-3 main phase, Luna, Family L (2026-11-17)

Package `qx3_luna_family_l_artem_recheck_2026-11-17.zip`, sha256 `e59f30ac…15d1`; SHA256SUMS passes (15 files).
Amendment `AMENDMENT_QX3_MAIN.md` locked v3, sha256 `d1c61ebc…37a1`. Recomputed from the 12 traces with
`qx3_check.py` and a separate permutation script (own code). Every number in the agent's readout reproduces.

## Primary measure and locked tests

x̄ = mean share of cells on H_T over generations 13–24 (δ = 1/64, B = 1, runs r2–r5):

| arm | r2 | r3 | r4 | r5 | mean |
|---|---:|---:|---:|---:|---:|
| R | 0.0058 | 0 | 0.0100 | 0.0117 | 0.0069 |
| R+E | 0.9992 | 1 | 0.9992 | 0.9983 | 0.9992 |
| forced | 0.8242 | 1 | 0.9842 | 0 | 0.7021 |

| test | prediction | p (one-sided exact, 70 splits) | at 0.0167 |
|---|---|---:|---|
| L1 R+E > R | holds | 1/70 = 0.0143 | holds |
| L2 forced > R | holds | 5/70 = 0.0714 | does not hold |
| L3 forced > R+E | does not hold | 67/70 = 0.957 | does not hold, as predicted |

Locked reading for L2: the four runs of the two arms are not completely ordered; the summary is the difference of
means, +0.695, with forced ranging 0–1 and R 0–0.012. No claim of "no difference" is made.

Secondary contrast x̄_nf (cells without an own counterexample), no α: R 0 in every run; R+E 0.82–0.93;
forced 0.80, 0.96, 0.95, 0. Permutation p: 1/70 (R+E vs R), 5/70 (forced vs R).

## Why forced r5 is 0 (post hoc)

- Forced r5 had no finder: 96 tests, none on a δ-input (inputs starting "DG"). With no counterexample in any
  memory, the attach rule has nothing to attach, and every cell stays on H_F.
- The R and forced arms send the same prompt. Their pooled δ-test rate is 27 of 790 (3.4 %). At that rate the
  chance that a run of about 97 tests has no δ-test is about 3.4 %. One forced run in five (pilot included) had none.
- In the three forced runs with finders (3–4 each), the population reached H_T (x̄ 0.82–1.00), and every
  non-finder on H_T had first seen a shared counterexample (96, 96, 97 of 96, 96, 97).
- In R, every run had finders (2–6), and no non-finder ever reached H_T.

## Discovery and replication (post hoc; corrected 2026-11-18)

The first version of this report said that the R+E prompt raises discovery and that L1 therefore mixes sharing with
more finding. That was wrong. It pooled every test, including tests made after a cell had received a counterexample.
Split by what the cell held when it chose the test (`fl_split.py`, `fl_find.py`, own code):

| arm | δ-tests with no counterexample in memory | δ-tests after a received one | … same input as received |
|---|---:|---:|---:|
| R | 16 / 394 (4.1 %) | — | — |
| R+E | 8 / 348 (2.3 %) | 33 / 51 | 4 |
| forced | 5 / 351 (1.4 %) | 6 / 45 | 2 |

- Independent finders (first own counterexample from a test chosen before any received one), per run r2–r5:
  R 3, 2, 6, 5; R+E 2, 4, 1, 1; forced 2, 1, 2, 0. Discovery is not higher under the R+E prompt.
- The R+E excess is cells that, after receiving a counterexample, test other inputs where the rules differ
  (33 of 51 tests, only 4 on the received input itself). They then count as finders. In forced, receivers do this
  in 6 of 45 tests.
- The pooled 41 / 399 against 27 / 790 of the first version are these rows added up.

So L1's gap is the spreading of evidence, not more discovery. In two R+E runs a single independent finder was
enough for x̄ ≥ 0.998. The "finder" counts in the readout should be split into independent and following finders.

## Integrity

- 28,800 calls, no fallback, one attempt per decision, no truncation, no reasoning field.
- No result in arm R; every shared result is in the sender's memory with the stored, true output; forced attachments
  equal the reconstructed attach rule; no test in generation 24; memory in the traces equals memory rebuilt from
  decisions. Cost of the 12 runs $15.28.

## Consequence for the reading

For Luna at δ = 1/64, a counterexample spreads through the population whenever at least one cell finds one, and a
rule name never does. Whether anyone finds one is a separate step, at about 2–4 % of tests under every prompt. L2
fails on that step (forced r5, no finder), not on spreading. The page and the message to Valko should state both.

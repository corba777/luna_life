# Task — A minimal transition model, fitted on interventions, tested on live logs

**Status:** draft for lock. Local analysis, no API calls (pre-approved). Locked before any fitting.
Parents: `runs/life_dr_tipping/final_readout.md`, `runs/life_dr_tipping/redo/redo_readout.md`,
Part E and Part G readouts, `runs/life_dr_controls/part1_readout.md`, `adopt_by_share.md`.

## Why

The micro-rule is so far descriptive: each piece was found or tested separately. The question is
whether a small model of one decision, fitted only on controlled interventions, predicts what cells do
in the live runs. If it does, the micro-rule is predictive. If it does not, the misfit says what is
missing.

## Data

**Fit set (interventions only, interleaved order only):** the redo of Parts 0b, 0c and D; Part E
(shuffled arm only); Part G. The top-block constructions are excluded.

**Test set (live logs, never used for fitting):** Luna `all`, `all8exact`, `allshuf`, r8, r8q and the
lattice, all worlds and replicates already run, rounds 2–20 (rounds 2–10 for the H = 10 runs). Only
decisions inside the support of the fit set are scored:
- the cell's own example fits the prefix (class A), or rules it out (class B) for the class-B terms;
- the visible lines are P_e lines, prefix lines and empty slots only (no third rule);
- the cell is either a non-holder of P_e holding the prefix (an adoption decision) or a P_e holder at
  d = 1 (a leave decision).
The excluded share of live decisions is reported.

## Model (fixed now)

Two logistic regressions, one for adoption (non-holders) and one for leaving (holders at d = 1):

logit P = b0 + b1·s + b2·1[s > 1/2] + b3·log(1 + n_opp) + b4·signal_Pe/7 + b5·signal_opp/7 + b6·class_B

- s: P_e share of the visible (non-empty) lines; n_opp: number of visible non-P_e lines;
  signal_Pe, signal_opp: mean signals on P_e lines and on opposing lines (0 when there is none);
  class_B: 1 if the cell's example rules the prefix out (adoption model only; the leave data are class A).
- No other term. Fitted by maximum likelihood with a ridge penalty λ = 1 on b1–b6, unscaled
  features as defined. Standard errors by cluster bootstrap over source cells, 2000 draws, seed 0.

## Baselines (fixed now)

- **B0:** the base rate of the test set (one constant per decision type).
- **B1 (share only):** the same logistic with b0, b1 and b2 only, fitted on the same fit set.

## Predictions (locked)

The metric is the mean log loss on the test set. Differences get a 95% cluster-bootstrap interval over
runs (world × replicate × arm), 2000 draws, seed 0.

- **M1 (the model predicts):** for each decision type, the full model's test log loss is below B0's,
  and the interval of the difference excludes 0.
- **M2 (more than share):** for the leave model, the full model's test log loss is below B1's, and the
  interval excludes 0. Basis: the redo length effect (0.39 at 8 lines against 0.70 at 88 at logged
  signals) is not a share effect.
- **M3 (arm gap reproduced):** on the subset that produced the observed figures (worlds 1, 3 and 5,
  replicates r1 and r2 of `all` and `all8exact`), the model's predicted mean leave rate for class-A
  holders at d = 1 in the (0.25, 0.5) share bin, pre-tipping rounds, is higher for `all` than for
  `all8exact`, and the predicted gap is within ±0.15 of the observed gap (0.729 − 0.339 = 0.390). The
  tolerance 0.15 is about the half-width of the wider observed interval in that bin.
- **Descriptive:** calibration plots by decile; coefficients with intervals; per-arm and per-topology
  log loss; the residual by holding time d and by round, which shows what the model is missing.

## Qwen

When the Qwen interventions (QI-1m and QI-G) and Qwen Stage 1 are done, the same model is fitted on the
Qwen interventions and tested on the Qwen live logs, with M1–M3 re-locked for Qwen in an amendment
written before that fit. M3 for Qwen uses the Qwen observed gap if both arms exist; otherwise M3 is not
reached.

## Order

Luna part after Part G finishes. Qwen part after its interventions and Stage 1. Commit this file before
any fitting; commit the fitting script before running it.
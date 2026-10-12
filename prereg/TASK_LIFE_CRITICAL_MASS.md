# Task — Critical mass: how small a minority can still turn the population?

**Status:** draft for lock. Predictions are locked with this file, before any run. API only (Luna),
no GPU. Parents: `TASK_LIFE_LONG_CHAIN.md`, `AMENDMENT_LONG_CHAIN_B0.md`.

## Why

With no seeded source (B0), every population converged on the true two-op rule. In the first
generation 23–44% of cells found it on their own, and messages plus checking selected it from among
the hypotheses some agents already held. This is selection, not discovery. How large must that
minority be? Without messages, the solo share stays flat for ten generations (Bs ≈ 0.25), so below
some share the population should stall or settle on a false rule.

## Knob: ambiguity of the private example

The share of solo finds depends on how many catalog rules fit a cell's single example: with more
rules that fit, the reasoning cell is less likely to pick P_e. Manipulate it directly:

- **k = number of catalog rules (out of the 101) consistent with the cell's private example, P_e
  included.** Levels k ∈ {2, 4, 8}. Every non-source cell in a run gets an example with exactly k.
- The default sparse examples have k ≈ 2.5 on average (`|H|`); the existing B0 runs serve as the
  reference row, not as the k = 2 level.
- Every cell can still check: P_e always fits its example, and so do k − 1 others. Higher k means a
  weaker filter, so more of the decision falls to votes and feedback. This is part of the
  manipulation, and the readout says so.

## Part 0 — Generator check (no model; before lock of numbers)

For each world seed 1–5 (the same 2-op P_e as all Life runs) and each k:
1. Enumerate inputs over the 8-symbol alphabet; keep those whose example (input, P_e(input)) is fit
   by exactly k catalog rules.
2. Draw one example per cell with the generator seed (`CRITMASS_SEED`, committed). If an exact-k
   input does not exist for some (seed, k), report it and **drop that cell of the design**. Do not
   relax k.
3. Report per (seed, k): pool size, achieved k per cell (must equal k), the set of co-fitting rules
   and how many of them are 1-op. The share of 1-op rules among the co-fitting ones matters, given
   the simplicity pull.

## Arms

| arm | cells | sources | channel | examples |
|---|---|---|---|---|
| **K2** | Luna Responses, medium | 0 | on | exactly 2 rules fit |
| **K4** | same | 0 | on | exactly 4 fit |
| **K8** | same | 0 | on | exactly 8 fit |
| **K8s** | same | 0 | **off** | exactly 8 fit (silent control at the hardest level) |

- World seeds 2-op 1–5. Everything else as B0: decoding, memory, feedback, 10 generations,
  invariant checks, served model and backend recorded.
- J over all 100 cells. Lock = modal share ≥ 0.5 (registered).

## Metrics

- **g1 solo share** (P_e holders at g1, before any message) per (arm, seed). This is the measured
  size of the minority; the analysis uses it, not k.
- J by generation, J at g10, correct and false lock, the modal rule at g10.
- The g1 share of the largest false rule (the size of the wrong majority).
- Per seed: the generation at which P_e first becomes modal (or "never").

## Predictions (lock)

- **K1:** the seed-mean g1 solo share decreases with k: K2 > K4 > K8.
- **K2 (primary, threshold):** pooling every (arm, seed) with the channel on (15 runs), the true rule
  is modal at g10 in **all** runs with g1 solo share ≥ 0.15, and in **at most half** of the runs
  with g1 solo share ≤ 0.05.
- **K3:** K8 J at g10 > K8s J at g10 in ≥ 4/5 seeds. Even at the hardest level the channel adds
  something.
- **K4 (descriptive):** false locks at g10 grow with k. Report the modal false rule and whether it is
  1-op.

## Readout

- K2 PASS → a critical mass exists between 5% and 15% initial holders. Report the transition by
  plotting P(true rule modal at g10) against the g1 solo share over all 15 runs.
- K2 FAIL because even ≤ 5% minorities win → selection is very robust here; the next limit is
  discovery (no holder at all), which needs a new message protocol.
- K2 FAIL because ≥ 15% minorities lose → ambiguity hurts more than the minority size alone
  explains: with many co-fitting rules, votes, not checks, decide. Compare with Part 0's share of
  1-op co-fitting rules.
- If some k levels yield no runs in a bin (for example, nothing ≤ 0.05), say so; the threshold claim
  then covers only the observed range.

## Cost and schedule

4 arms × 5 seeds, as B0 (~$0.45 per seed): about $9. Cap $15; report the actual cost. Runs in
parallel with Ca1/Da1 and the GPU grid.

## Artifacts

- `runs/life_critical_mass/generator_check.json` (Part 0)
- `runs/life_critical_mass/{K2,K4,K8,K8s}/seed{n}/`
- `runs/life_critical_mass/summary.json` (K1–K4; per-run g1 solo share, g1 false-majority share,
  modal rule at g10, J(g))
- `runs/life_critical_mass/fig_critical_mass.png`: P(true rule modal at g10) and J at g10 against the
  g1 solo share, one point per run, coloured by k; B0 reference runs in grey

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. Commit this file
before the first call. Generator check before any model call. Amendments before numbers.
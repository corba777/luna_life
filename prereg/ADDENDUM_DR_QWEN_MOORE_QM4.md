# Addendum to `AMENDMENT_DR_QWEN_MOORE.md` — QM4, does the cell's leave propensity carry over to the lattice

**Status:** locked before any moore call. It adds QM4 and changes nothing in the locked QM1–QM3.
Dry-build values below are from existing caches; live calls were refused.
Parents: `AMENDMENT_DR_QWEN_MOORE.md` (locked), `runs/life_dr_qwen/qit/qit_readout.md` (including its
post-hoc section), `runs/life_dr_qwen/stage1_readout.md`.

## Why

In Qwen `all`, world 1, the class-B leave decision splits into two parts:

- A stable per-cell propensity. The 25 cells differ beyond binomial noise (χ² = 53.1 on 24 df,
  p = 0.0006), and their rates agree across temperatures (r = 0.61).
- A nearly independent draw at each decision. The within-cell kappa between two draws of the same
  prompt is 0.02.

In `all` the inbox is nearly the same for every cell, and the memory line on these prompts is always
P_e. What stays fixed per cell is its own example and its query. If the propensity is a property of
the cell, it should hold on the lattice. The lattice has the same 25 class-B cells with the same
examples, but different inboxes. These figures were found post hoc. QM4 tests them on new data.

## Data

- **`all` propensity, per cell:** class-B leaves over opportunities, pooled over the logged Stage 1
  decisions and the QI-T draws at T6 and T3 on the same 637 prompts. That makes three decisions per
  opportunity. QI-T showed no temperature effect, so pooling the two temperatures is justified.
- **Lattice propensity, per cell:** class-B leaves over opportunities (records where the cell held P_e
  at the previous round), moore rounds 2–20, r1 and r2 pooled.
- **Inclusion:** a cell enters QM4 only if it has at least 5 lattice opportunities. The excluded cells
  are listed. If fewer than 15 cells qualify, QM4 is reported as "not reached". This rule is fixed
  before any lattice data exist.

## Statistic and references (fixed now)

- **Statistic:** the Spearman rank correlation ρ between the two per-cell propensities.
- **Reliability of the `all` estimate:** ρ_1, the Spearman correlation of the 25 per-cell rates
  between T6 and T3, is 0.447. That is one draw per opportunity against one draw per opportunity. With
  three decisions per opportunity, the reliability is R_all = 3ρ_1 / (1 + 2ρ_1) = 0.708, by the
  Spearman–Brown formula.
- **Pooled `all` propensity, per cell.** Leaves are logged + T6 + T3, over 3n opportunities. The
  unweighted mean of the 25 cell rates is 0.165.

| cell | n | logged | T6 | T3 | pooled | p |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 31 | 4 | 2 | 1 | 7 | 0.075 |
| 3 | 33 | 3 | 5 | 2 | 10 | 0.101 |
| 6 | 25 | 3 | 2 | 5 | 10 | 0.133 |
| 9 | 21 | 3 | 2 | 1 | 6 | 0.095 |
| 11 | 30 | 5 | 6 | 4 | 15 | 0.167 |
| 14 | 29 | 4 | 4 | 3 | 11 | 0.126 |
| 17 | 18 | 6 | 2 | 5 | 13 | 0.241 |
| 30 | 21 | 4 | 1 | 2 | 7 | 0.111 |
| 33 | 28 | 3 | 4 | 4 | 11 | 0.131 |
| 36 | 28 | 5 | 5 | 5 | 15 | 0.179 |
| 39 | 22 | 7 | 4 | 6 | 17 | 0.258 |
| 41 | 15 | 3 | 7 | 6 | 16 | 0.356 |
| 44 | 29 | 7 | 4 | 2 | 13 | 0.149 |
| 47 | 34 | 4 | 5 | 6 | 15 | 0.147 |
| 60 | 25 | 4 | 1 | 2 | 7 | 0.093 |
| 63 | 24 | 3 | 8 | 5 | 16 | 0.222 |
| 66 | 21 | 6 | 4 | 5 | 15 | 0.238 |
| 69 | 26 | 6 | 8 | 7 | 21 | 0.269 |
| 71 | 25 | 5 | 2 | 7 | 14 | 0.187 |
| 74 | 34 | 1 | 4 | 3 | 8 | 0.078 |
| 77 | 20 | 5 | 2 | 4 | 11 | 0.183 |
| 90 | 31 | 2 | 3 | 5 | 10 | 0.108 |
| 93 | 28 | 4 | 5 | 3 | 12 | 0.143 |
| 96 | 18 | 4 | 3 | 4 | 11 | 0.204 |
| 99 | 21 | 3 | 3 | 2 | 8 | 0.127 |
- **Reliability of the lattice estimate:** one decision per opportunity. Its reliability is taken as
  ρ_1, scaled by Spearman–Brown for the ratio of mean lattice opportunities per cell to mean `all`
  opportunities per cell (25.5). This is computed after the run, by this fixed formula.
- **Ceiling:** ρ_max = √(R_all · R_lattice). This is the correlation expected if each cell's
  propensity is exactly the same in both arms, given the measurement noise.

## Prediction (locked)

- **QM4 (the propensity carries over):** ρ > 0, one-sided permutation test (10 000 permutations of
  the lattice propensities across cells, `numpy` Generator seed 0), α = 0.05.

## Pre-stated readings

- **QM4 passes and the bootstrap 95% interval of ρ contains ρ_max:** the propensity is a stable
  property of the cell. It carries over unchanged across topologies. Since the inbox changes and the
  example does not, the example is the leading candidate for its source. The interval is a bootstrap
  over cells, 2000 draws, seed 0.
- **QM4 passes and the interval lies below ρ_max:** the propensity is partly stable. The lattice
  reorders some cells, so it depends partly on the arm, for example on local inbox content.
- **QM4 fails:** the `all` propensity does not carry over. The cell differences in `all` were specific
  to that arm, or too noisy to transfer. "Cell trait" is then not claimed.
- **QM2 interaction:** QM2 tests the mean level, and QM4 tests the ordering. Either can pass without
  the other. If QM2 fails, the lattice level differs, but the cells can still keep their order. The
  readout reports the two together.
- **If the design is the cause:** on the lattice some class-B cells may rarely hold P_e, which gives
  few opportunities and noisy rates. The inclusion rule and the reliability scaling are there for
  this. The readout also reports the result with the threshold at 3 and at 8 opportunities,
  descriptively.

## Design audit

1. **Fidelity.** No new prompts. Both estimates come from logged or cached decisions, and the lattice
   run is unchanged.
2. **Coverage.** The same 25 cells and the same examples. The `all` estimate pools three decision sets
   on identical prompts.
3. **Controls.** The permutation null breaks the cell pairing between the two arms.
4. **Observability.** The propensity is read from decisions only. QM4 relies on nothing the cell does
   not see.
5. **Gate consistency.** There are no new runtime gates. The dry build computes ρ_1, R_all and the
   per-cell `all` propensities, and records them. The lattice part is computed after the run, by the
   formulas above.
6. **Statistical unit.** The cell (n ≤ 25).
7. **Pre-stated readings.** Above.

## Power

25 cells. The true propensity is the pooled `all` cell rate shrunk toward the unweighted mean:
π_i = μ + R_all (p_i − μ), μ = 0.165. No rate left [0, 1]. Each cell keeps its Stage 1 opportunity
count, multiplied by 0.5, 1, or 2 and rounded to the nearest integer, at least 1. Lattice leaves are
binomial at π_i. The tested correlation is Spearman between the fixed pooled rates and the simulated
lattice rates. The permutation p-value is (1 + the number of 10 000 permuted correlations at least
as large) / 10 001, one-sided, α = 0.05. One `numpy` Generator seed 0 covers the study, scales in
the order 0.5, 1, 2. ρ_max uses mean lattice opportunities divided by 25.5. 2000 simulations each.

| scale | power | mean ρ_max |
|---|---:|---:|
| 0.5 | 0.6215 | 0.450 |
| 1 | 0.8485 | 0.563 |
| 2 | 0.9780 | 0.661 |

The power at the 0.5 scaling is below 0.8. The design is not changed.
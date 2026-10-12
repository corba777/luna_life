# Amendment — Critical mass: ambiguity levels that exist

**Status:** locked (`bf5f9001a7`, before K2 readout). K2 runs already under way are unaffected
(same k = 2 definition); their numbers stay sealed until this commit lands. Parent:
`TASK_LIFE_CRITICAL_MASS.md`.

## What Part 0 showed

`generator_check.json` (`CRITMASS_SEED` = 20261011):

- **k = 8 does not exist** for any world seed: no input has exactly 8 co-fitting catalog rules.
  The |H| histograms are concentrated on 1–4, with a thin tail (k = 5, 6, 7, 11, 24 on 8–232
  inputs each). K8 and K8s as written cannot run.
- **k = 4 for seed 4** has a pool of 64 inputs. It was dropped by the generator's
  sampling-without-replacement rule. That rule is not in the task; the task drops a cell of the
  design only when no exact-k input exists.

Without a hard level, the lower bin of K2 (runs with g1 solo share ≤ 0.05) may stay empty and the
primary prediction untestable. This amendment restores a hard level using inputs that exist.

## Changes

1. **Sampling with replacement** at every level. Cells may share the same example input. A design
   cell is dropped only when the exact-k pool is empty. This restores K4 seed 4. Report the number of
   distinct inputs used per (seed, level).
2. **K8 → KH ("high ambiguity").** For each world seed, k_H = the largest k with a non-empty pool,
   with every cell drawn from that pool (with replacement). Record k_H per seed. Expected from
   Part 0: 11 for seeds 1, 3 and 4; 24 for seed 2; seed 5 to be read from its histogram.
   - If k_H's pool has fewer than 8 distinct inputs, still run it, and report how many distinct
     inputs it has.
3. **K8s → KHs:** the silent control at the KH level, same examples.
4. **Analysis unchanged:** every K prediction is read against the measured g1 solo share, not k.
   Heterogeneous k_H across seeds is therefore acceptable and is reported per run.

## Predictions (unchanged text; arm names updated)

- K1: the seed-mean g1 solo share decreases K2 > K4 > KH.
- K2 (primary): over all channel-on runs (K2, K4, KH; up to 15), the true rule is modal at g10 in
  all runs with g1 solo share ≥ 0.15, and in at most half of the runs with g1 solo share ≤ 0.05.
- K3: KH J at g10 > KHs J at g10 in ≥ 4/5 seeds.
- K4 (descriptive): false locks at g10 grow from K2 to KH. Report the modal false rule and its
  number of ops, and the share of 1-op co-fitting rules per level (from Part 0).

If no run falls at or below 0.05 even at KH, K2's lower clause is reported as **untestable in the
observed range**, not as pass or fail.

## Cost

Adds KH + KHs (10 runs, ~$5). New cap for the task: $20.

## Artifacts

- `generator_check.json` regenerated with replacement sampling and the KH level (keep the old file
  as `generator_check_v0.json`)
- arm folders `KH/`, `KHs/` replace `K8/`, `K8s/`
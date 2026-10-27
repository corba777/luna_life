# Amendment — does Luna medium on `all` sometimes tip? (20 new replicates)

**Status:** locked 2026-10-26. This is a Luna API job. Artem raised the envelope to **$50** on 2026-10-26.
Calls inside it run without a new go; at $50, stop and ask. No call is made before this file is
committed as locked, after a dry build that fills every **[dry build]** value. The basis is
`AMENDMENT_CONTAGION.md` (locked), `runs/contagion/part_ab_readout.md`,
`runs/contagion/part_b_descriptives.md` and `THEORY.md` §3. Dry build:
`runs/luna_all_tip/dry_build.json` (live calls refused).

## Why

The Part B simulation, built from Luna's Part A curves and measured inputs and not fitted to this
outcome, reproduces the frozen Luna `all` state (median 0.296; observed 0.232 and 0.307). It also
predicts something not seen yet: the frozen state is metastable. In 30 of 200 simulated replicates
(0.150, Wilson 95% [0.107, 0.207]), the visible P_e share crosses Luna's threshold near 1/2 by chance,
and the population tips to P_e. Those runs end at a median x of 0.999 and tip at a median round of 3.
Both observed replicates are frozen, which is likely (0.85² ≈ 0.72) if the prediction is right.

This is a falsifiable, out-of-sample consequence of the micro → macro model. A threshold agent on a
global board does not lose for certain; it loses with a probability set by its curve and by early
noise.

## Runs

- **LM-medium-all-tip:** Luna Responses at `effort=medium`, world 1, `all`, 100 cells, 20 rounds,
  **20 new replicates**.
- **Same as the reference:** the panel full-run builder, byte-identical to the Luna `all` reference
  (already shown at rounds 1 and 11), the same model, decoding and schema as the reference runs.
- **Caches:** each replicate has its own new, empty cache directory,
  `runs/luna_all_tip/cache_r<k>/`. No existing cache is read, so the replicates are independent
  samples. The runtime invariant refuses a cache path without the arm id and replicate number.
- **Cost:** from the stored Luna `all` medium token counts
  (`runs/life_dr_topology/cache_all_r{1,2}`, effort=medium): mean input 3772.32 tokens, mean output
  388.92 tokens. At list rate ($0.10/M input, $0.50/M output), **$1.1434 per replicate** (2,000
  calls), **$22.87 in all**. The cap is twice the estimate: **$45.74**. The envelope stop at $50
  applies first. Spent so far: $11.81. Projection after this arm: $34.68 of $50.

## Measures (per replicate)

- x(t) for rounds 1–20, and mean x(10–20).
- **Tipping:** mean x(10–20) > 0.9, the threshold already used in the simulation descriptive.
- **Tip round:** the first round with x ≥ 0.5.
- Class B at round 20, the visible P_e share s(t) per round, and publication by round and class.

## Predictions (locked)

The unit is the replicate, 20 new ones. The 2 earlier replicates are reported beside them and not
scored.

- **T1 (tipping occurs):** at least 1 of the 20 replicates tips. Under the simulated rate 0.150, the
  chance of 0 tips in 20 is 0.85²⁰ = 0.039. A result of 0/20 therefore rejects the simulated tipping
  rate at α = 0.05, one-sided.
- **T2 (tipping is not common):** at most **8** of the 20 replicates tip (the 97.5th percentile of
  Binomial(20, 0.207), the Wilson upper bound). A larger count means the model underestimates
  tipping.
- **T3 (the frozen level):** the median mean x(10–20) of the non-tipping replicates lies within the
  simulated non-tipper 5th–95th band **[0.269, 0.753]** (170 of 200 simulated replicates with
  mean x(10–20) ≤ 0.9; Generator seed 0; Part A fits and measured publication).

## Pre-stated readings

- **T1–T3 hold:** Luna's `all` loss is probabilistic, as the curve-level model predicts. The paper
  states the loss rate, not "Luna loses on `all`".
- **T1 fails (0/20):** the simulator overstates early noise or the threshold's softness at s ≈ 1/2.
  Part A's a(0.5) = 0.375 is the candidate, and the readout compares the observed s(t) at rounds 2–4
  with the simulated s(t).
- **T2 fails:** Luna on `all` tips more often than its isolated curves imply. In-situ adoption is then
  stronger than in the battery, as already seen for gpt-oss-20b.
- **T3 fails:** the frozen level differs from the model, and the witness or publication inputs are
  examined.

## Design audit

1. **Fidelity.** The builder, model and settings are the reference's, already byte-checked.
2. **Coverage.** World 1, `all` only. That is where the prediction is.
3. **Controls.** The 2 existing replicates, and the 200 simulated replicates as the predicted
   distribution.
4. **Observability.** Cells see their prompts only.
5. **Gate consistency.** Run together with live calls refused:
   - prompt identity at round 1 against the reference;
   - empty, distinct cache directories;
   - the cost estimate and cap;
   - the envelope projection.
6. **Statistical unit.** The replicate, n = 20. The test is a count. Power to see at least one tip if
   the true rate is 0.15 is 1 − 0.039 = 0.961.
7. **Pre-stated readings.** Above.

## Queue

API only, no GPU. It runs after the lock, in parallel with the local queue. Replicates run one
after another under one waiter, with a log line per replicate.

# Amendment — TASK_LIFE_DR_MICROMODEL: M1v2, adoption inside the fit range

**Status:** post hoc: computed before this file was written. Not a lock. Local, no API cost. No
refit. Parent: `TASK_LIFE_DR_MICROMODEL.md`. The unrestricted M1 adopt failure stands.

## What was already seen

Per-arm log losses of the full adoption model were already in the readout. The comparison of that
model to B0 and to B1 on live adoption rows with `n_opp` ≤ 8 was computed before this file was
written, on lattice, r8, r8q and `all8exact`. The every-arm score uses the same cut. Neither one
is a pre-stated test.

## Design

- Coefficients: the adoption `beta` and `b1` arrays in `runs/life_dr_micromodel/luna_fit.json`.
  sha256 of `{"beta":…,"b1":…}` with `separators=(",", ":")` is
  `d525913b65decc614e46dd0735f1b5312613eee2e8b7a7d936349330fcb9662a`.
  The scoring script checks that hash and does not call the fitter.
- Scored rows: live adoption decisions whose `n_opp` is inside the fit range. The fit takes
  `n_opp` in {0, 1, 2, 3, 4, 5, 6, 7, 8}, so the cut is `n_opp` ≤ 8. Every arm is eligible.
  Rows with `n_opp` > 8 are counted and excluded.
- B0 is the base rate of these scored rows, held fixed inside the bootstrap. B1 is the stored
  share-only coefficient vector, not a refit.
- The difference is full-model log loss minus the baseline. The interval is a cluster bootstrap
  over runs (arm × replicate × world), 2000 draws, seed 0, the same function as M1.

## Prediction (not a lock)

**M1v2.** On this set, the full model is below B0 and below B1, and each interval lies entirely
below 0.

- **Both pass.** Inside the inbox lengths the adoption model was fitted on, it predicts the live
  rows better than the base rate and better than share alone. The unrestricted M1 failure is the
  long-inbox extrapolation. A pass is also what dropping the arms with the worst per-arm log losses
  can produce, and those losses were already seen.
- **Fails against B0.** The failure is not only inbox length. Inside the fit range the model still
  does not beat the base rate.
- **Beats B0 and fails against B1.** Share is enough. The other terms do not improve log loss
  inside the range.
- **The other way around.** The extra terms help and the share-only model does not beat the base rate.

A cell-level bootstrap, clustered on (arm, replicate, world, cell), is reported beside M1v2 and is
not scored.

## Design audit

1. **Fidelity to live data.** Yes. No new prompt is built. The rows are the live adoption rows
   already replayed for the micromodel test. Nothing in the prompt is rewritten.
2. **Coverage.** The cut is the one already computed. Fit `n_opp` is 0 through 8 (960 adoption rows). Scoring
   keeps `n_opp` ≤ 8 and drops the rest. The other features, as closed intervals on those 960 rows:
   share s in [0, 1], the half indicator in {0, 1}, both signal means in [0, 1], class B in {0, 1}.
   Live rows with `n_opp` ≤ 8 stay inside those intervals, because a signal is an integer 0 through 7
   and a share is a ratio of counts. The fit only uses the eight shares of an 8-line inbox
   (0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 1). Other shares with `n_opp` ≤ 8 stay in the score.
   That discrete gap is inside the interval, and the pass reading above already says the cut can
   be doing the work.
3. **Controls.** Yes. B0 is the scored set's own base rate. B1 is the share-only model fitted on
   the same interventions. There is no new manipulation.
4. **Observability.** Yes. M1v2 uses the share, the half indicator, log(1 + n_opp), the two mean
   signals, and class B. Each is in the inbox or in the cell's example. Holding time is not a
   feature. Memory in the prompt is one step.
5. **Gate consistency.** Yes. `runs/score_life_dr_micromodel_v2.py --gate` checks the coefficient
   hash and that the fit's `n_opp` maximum is 8. It does not replay and it does not fit. The gate
   does not make this file a lock.
6. **Statistical unit.** Yes. The scored unit is the run. Decisions on the same cell are not
   treated as independent: the cell-level bootstrap is reported beside the run-level interval and
   is not scored.
7. **Pre-stated readings.** No. The comparison was computed before this file was written. The
   branches under Prediction describe a result already in hand. That is why this file is not a lock.

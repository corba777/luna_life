# Amendment — refit the adoption model on the long inboxes

**Status:** locked before the refit. No API. Parent: `TASK_LIFE_DR_MICROMODEL.md` and
`AMENDMENT_DR_MICROMODEL_ADOPT88.md`. The unrestricted M1 adopt failure stands. M1v2 stays
post hoc.

## Fit

Same coefficients and the same ridge. No new term. The adoption rows are:

- the Part 0b redo, which is the whole of the previous adoption fit together with
- the Part E class-A rows (the shuffled 3/5 and 5/3 inboxes; the Part E order rows are leave
  decisions and are not in this fit), and
- the filled conditions of the adoption intervention (L8-125, L88-125, S25, S375, S625).

Empty8 and empty88 have no share. The fitter drops an empty inbox, and so does this fit. They
remain the controls in the intervention. An unparsed call is dropped and the count is reported.

## Test

Live adoption rows of `all` and `allshuf` with `n_opp` > 8. B0 is that set's base rate, held
fixed inside the bootstrap. B1 is b0, b1 and b2 only, fitted on this fit set. The metric is mean
log loss. The interval clusters on the run (arm × replicate × world), 2000 draws, seed 0.

## Prediction (locked)

**M1.** On this test, the full model is below B0 and below B1, and each run-level interval lies
entirely below 0.

- **Both pass.** The long-inbox failure was missing fit data at those lengths. With this set in
  the fit, the model predicts the live long inboxes better than the base rate and better than
  share alone.
- **Fails against B0.** Length was not the whole failure. On `n_opp` > 8 the model still does
  not beat the base rate.
- **Beats B0 and fails against B1.** Share is enough on the long live inboxes. The other terms
  do not improve log loss there.
- **The other way around.** The extra terms help and the share-only model does not beat the base
  rate.
- **If the design is the cause.** The added rows are only P_e and the prefix, at 8 or 88 lines,
  in redo order, with logged signals. A live `all` inbox has a variable length and other rules,
  and third-rule inboxes stay out of this test. A pass does not say the model learned those.
  World 2 is in the test frame and not among the 20 intervention cells.

## Design audit

1. **Fidelity to live data.** The Part 0b and Part E rows are the prompts already scored for the
   first fit. The added rows are the intervention prompts, whose differences from the live inbox
   are listed in `AMENDMENT_DR_MICROMODEL_ADOPT88.md`. This refit builds no new prompt.
2. **Coverage.** The previous adoption fit has `n_opp` 0 through 8. This fit adds `n_opp` 7
   (already inside that range), 33, 55, 66 and 77. The test is every live `all` and `allshuf`
   adoption row with `n_opp` > 8, so lengths other than those four stay in the score. Worlds in
   the Part 0b redo and Part E are 1 and 3. Worlds in the 20 intervention cells are 1, 3 and 5.
   World 2 has 88 eligible cells and the hash draws none of them. The test frame is `all`
   replicates 1–2 in worlds 1–5, `all` replicates 3–10 in world 1, and `allshuf` replicates
   3–10 in world 1. World 4 has no prefix holder, so it has no adoption row. World 2 is in the
   test and not in the intervention sample. World is not a feature of the model.
3. **Controls.** Yes. B0 is the test set's own base rate. B1 is the share-only model fitted on
   this same fit set.
4. **Observability.** Yes. The features are the share, the half indicator, log(1 + n_opp), the
   two mean signals, and class B. Each is in the inbox or in the example. Holding time is not a
   feature. Memory is one step.
5. **Gate consistency.** Yes, for what can be checked before the calls return.
   `runs/fit_life_dr_micromodel_refit.py --gate` checks that the Part 0b redo and Part E still
   contribute 960 adoption rows with `n_opp` at most 8, and that the dry build is 140 prompts.
   It does not fit and it does not score. The intervention gate has already passed.
6. **Statistical unit.** Yes. The scored unit is the run. The interval is the same cluster
   bootstrap as M1.
7. **Pre-stated readings.** Yes. The branches are under Prediction, including the reading in
   which the cleaned inbox produces the result.

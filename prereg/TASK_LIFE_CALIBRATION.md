# Task — A calibrated choice model: where do the thresholds come from?

**Status:** draft for lock. No API calls; existing logs only. Predictions are locked with this file,
before any dose–response curve, fit or simulation is computed. Follows `DESIGN_CHECKLIST.md` and the
standing rules in `PLAN_NEXT.md`. Parents: `TASK_LIFE_TECH_LEAD.md` (Ca-r, Da-r),
`TASK_LIFE_PHONE.md` (R8, R8c, All, Allc), `runs/life_phone/readout.md`.

## Why

The Phone predictions (P1–P3) used thresholds that were not derived from anything ("≤ 0.24",
"by g3", "≥ 3 of 5"). A FAIL against such a threshold says only that the intuition was wrong, not
which assumption was. This task builds a cell-choice model from the grid (Moore) runs, checks
whether it reproduces the Phone runs it was not fitted on, and so gives future predictions a source.

The working hypothesis, from the literature on contagion on networks (Centola & Macy 2007;
Iacopini et al. 2019 on simplicial contagion; Barkoczi & Galesic 2016 on conformity and network
efficiency):

- Without a filter, adopting a rule from the inbox is a **complex contagion**: the inbox shows
  sender counts, cells conform, and one sender of P_e among several senders of other rules rarely
  moves a cell. Four sources (4% of cells) are below critical mass on the lattice (Ca-r 0.24). On the
  complete graph (All) the dynamics are mean-field and bistable: each world falls into one basin,
  which gives the bimodal outcome (three worlds near 0.9, two false locks).
- With the engine filter, competitors that contradict the cell's own example are removed, so P_e is
  often the only or the dominant surviving rule. **The filter turns a complex contagion into a
  simple one**: one sender is enough, there is no threshold (Da-r 0.92, Allc 1.00).

Phone results are already known. Part 3 is therefore a **retrodiction**, not a prediction, and is
reported as such. It is still a real test because no Phone data enters the fit.

## Part 0 — rule synonyms in the catalog (group structure, no API)

The operations (shift_symbols, swap, rotate_left, reverse, …) generate a group acting on strings.
Two different catalog words can be the same group element (the same function on all inputs).

- For every catalog rule, compute its output on **all** inputs of the world's length over A–H.
  Group rules into classes of identical functions. Report the classes with more than one member.
- For each world, list the catalog rules that agree with P_e on **every** cell example used in
  that world (observationally equivalent there, even if not the same function).
- For every false-lock modal rule at g10 in Phone All, and for the modal non-P_e rules in Ca-r:
  is it a synonym of P_e, or observationally equivalent to it in that world?
- Commutation: for every 2-op rule, whether its two ops commute.

If a "false lock" rule is a synonym of P_e, the metric J is wrong for that world and every J in
the affected arms is recomputed with the synonym class counted as P_e, reported next to the
original. Part 0 is read before Parts 1–3 are computed.

## Part 1 — dose–response (existing logs)

**Arms:** Ca-r, Da-r (Moore); R8, R8c, All, Allc (Phone). One-pass Decisions only. Seeds 1–5,
generations 2–10, non-source cells.

**Events.** One event per (arm, seed, generation g, cell) where the cell does **not** hold P_e at
g−1. Record:
- **k:** number of senders of P_e in the inbox the cell saw at g (after the filter in check arms;
  also record the pre-filter count);
- **n:** total senders in that inbox; **s = k / n**, P_e's share;
- **m:** the sender count of the strongest competitor (the most-sent non-P_e rule, after the filter);
- **plurality:** whether P_e has the largest count in the inbox (ties recorded separately);
- **own feedback** at g−1 (right / wrong) and whether the cell's own rule appears in the inbox;
- **outcome:** whether the cell holds P_e at g.

**Inbox reconstruction.** The phone arms' `rule_history.inbox_says` field is wrong before v3 (it
logged the Moore inbox). Reconstruct every inbox from all cells' published rules at g−1, the
committed `PHONE_SEED` draws (R8, R8c) and the filter (check arms), using the runner's own code
paths. **Gate:** where the logs hold a correct inbox (Ca-r, Da-r, phone v3 generations), the
reconstruction matches it in 100% of events; any mismatch stops the task. State in the output
which generation's publications a choice at g sees, taken from the runner code.

**Curves.** P(adopt P_e) as a function of k, of s, and of plurality, per arm, pooled over seeds
with 95% intervals from a bootstrap that resamples (seed, cell) clusters. Bins with < 20 events are
shown but not interpreted.

**Two models, fitted per arm by maximum likelihood:**
- **Simple contagion (S):** P = 1 − (1 − q)^k, where each P_e sender independently converts with
  probability q (one parameter). If k = 0, the outcome P is a free parameter r (spontaneous
  adoption).
- **Threshold (T):** P = σ(a + b·s + c·plurality + d·[own feedback wrong]), with the same r for
  k = 0.

**Predictions (locked):**
- **D1:** in each no-filter arm (Ca-r, R8, All), T beats S by ΔAIC ≥ 10.
- **D2:** in each filter arm (Da-r, R8c, Allc), S is not beaten by T by more than ΔAIC = 10.
- **D3:** P(adopt | k = 1) is higher in each filter arm than in its no-filter pair (Da-r vs Ca-r,
  R8c vs R8, Allc vs All); the bootstrap 95% interval of the difference excludes 0 for every pair.

ΔAIC = 10 is the conventional "very strong" level; it is a convention, not a fitted number, and
is used only for this reason.

## Part 2 — the choice model (fitted on Moore arms only)

A conditional logit over the candidate rules a cell can choose at g. The candidates are its own
rule, every rule in its inbox (after the filter where there is one), and one "other" option that
covers every remaining catalog rule. The utility of a candidate rule ρ is:

  U(ρ) = β₁·log(1 + count(ρ)) + β₂·share(ρ) + β₃·[ρ is own] + β₄·[ρ is own]·[own feedback wrong]
         + β₅·log prior(ρ)

- **prior(ρ):** the one-pass prior mass of ρ from probe A (the same estimates used in the Phone
  descriptive files). If probe A does not cover every rule, report its coverage and give
  uncovered rules the mean uncovered mass.
- **"other":** a single utility β₀. When it is chosen, the specific rule is drawn in proportion to
  the prior.
- If the logs keep the Decisions option probabilities, also fit to them as soft targets and report
  both fits. The cell's real choice is the argmax over four orders, so the logit describes how
  choices vary across cells and examples, not a coin each cell flips.

**Fit:** Ca-r and Da-r jointly, with the same β, and the filter applied as a deterministic step
before the choice. This tests whether the filter alone explains the difference between Ca-r and
Da-r. Also fit Ca-r alone and Da-r alone, and report whether β differs (likelihood-ratio test).
**No Phone data enters any fit.**

## Part 3 — retrodiction of Phone by simulation

With the joint Moore β fixed, simulate R8, R8c, All and Allc on worlds 1–5. Use the real sources,
examples, catalog, filter, `PHONE_SEED` draws and real g1 states, with 500 runs per (arm, world).
Generations 2–10 use only the choice model.

**Pass criteria (locked).** These are derived from coverage, not chosen:

- **R1 (level):** in each phone arm, the real J@g10 falls inside the simulated central 90% interval
  in ≥ 4 of 5 worlds. If the model is calibrated, each world is covered with probability 0.9, and
  P(≥ 4 of 5) = 0.9⁵ + 5·0.9⁴·0.1 = 0.92. So R1 fails by chance only about once in twelve.
- **R2 (bimodality, All):** the simulated J@g10 distribution in All is bimodal, with more than 50%
  of its mass below 0.2 or above 0.8, in at least the worlds where the real run ended near 0 or near 1.
- **R3 (which worlds lie, All):** the two worlds where real All ended in a false lock are the two
  with the highest simulated P(false lock). Chance level is 1 / C(5,2) = 0.10.
- **R4 (speed, Allc):** the real generation at which Allc first reaches J ≥ 0.80 falls inside the
  simulated central 90% interval in ≥ 4 of 5 worlds (the same coverage argument as R1).

**Readout.**
- **R1–R4 pass:** a Moore-only choice model plus topology plus filter explains Phone. Future
  thresholds (for the noisy-verifier and saboteur tasks, and for graph choice) are taken from this
  model's simulations.
- **R1 or R4 fail in the no-filter arms only:** the choice rule changes with inbox size, since a
  99-sender inbox is not a scaled 8-sender one. Report the residual against s and n.
- **R3 fails:** the prior and counts do not decide the race. Report the simulated vs real switch
  order next to `prior_vs_switch_descriptive`.
- **D1–D3 fail:** the complex vs simple contagion account is wrong. This is stated in the readout
  and in any text that used it.

## Out of scope (next task, after this readout)

- Searching over graphs in simulation (edge pruning, clustering vs expanders, after Montanari &
  Saberi 2010), then 1–2 targeted API runs with thresholds taken from the model.
- The noisy verifier (error rate ε) and saboteur arms, with predictions taken from the model.
- The critical mass of sources as a function of topology, from the model.

## Artifacts

- `runs/life_calibration/part0_synonyms.{md,json}`
- `runs/life_calibration/part1_dose_response.{md,json}`, `fig_dose_response.png` (P(adopt) vs k
  and vs s, filter and no-filter pairs side by side)
- `runs/life_calibration/part2_choice_model.json` (β, standard errors, LR tests, fit diagnostics)
- `runs/life_calibration/part3_retrodiction.{md,json}`, `fig_retrodiction.png` (real J(g) over
  simulated 5–95% bands, per arm and world)
- `runs/life_calibration/readout.md` (D1–D3, R1–R4 verdicts; Part 0 effect on J if any)

## Constraints

No API calls. Closed-model outputs are not used as training data. A statistical model fitted to
logged choices is not training data, and no model weights are trained. No reasoning text is used.
Use new scripts only, and commit this file before any Part 1–3 number is computed. Amendments
come before numbers. Fixed seeds for the bootstrap and the simulation are committed with the
scripts.
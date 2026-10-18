# Amendment — TASK_LIFE_DR_TOPOLOGY: Part A2, a cell-heterogeneity automaton

**Status:** written after the Part A gate failed (7 of 10 at round 10) and before any API call.
No API calls. Parents: `TASK_LIFE_DR_TOPOLOGY.md`, `AMENDMENT_DR_TOPOLOGY_CHANNEL.md`,
`runs/life_dr_topology/partA_predictions.{md,json}`.

## Why

The Part A automaton treats every cell of a world as the same. All three runs outside the interval
(w2r1, w3r1, w4r1) grew faster than the automaton allowed, and all three grew from one or a few
nuclei. One mechanism the automaton leaves out is that cells differ. Each cell has one fixed private
example. A cell whose example rules out most of the catalog has less reason to hold a false rule than
a cell whose example fits many rules. If growth runs through the first kind of cell, a model that
averages the two kinds understates growth from a single nucleus.

## Standing of this model, stated in advance

This model is chosen **after** seeing the Part A failure. Passing the in-sample gate is therefore
weaker evidence than it would have been for Part A, and the extra bins make the in-sample fit easier.
Its real test is r8, which the model has not seen. For that reason:
- **One shot.** This is the only revision. If A2 fails the gate, no further model variants are tried
  for this task, and r8 and all stay descriptive.
- The class definition below is fixed by the world design, not by the DRc logs.

## Cell class (fixed now, from the world audit only)

For each cell c, let |S_c| be the number of catalog rules consistent with its private example
(from the world audit used by `_load_audit`; the design guarantees |S_c| ≥ 3).
- **sharp:** |S_c| ≤ the median of |S_c| over the 100 cells of that world;
- **vague:** |S_c| > that median.

No other split, threshold or covariate is tried. Report the class sizes per world. If the median
split leaves either class with fewer than 30 cells in a world, report it and use the split anyway.

## Steps

1. **Is there heterogeneity at all? (descriptive)** From the pinned DRc logs, rounds 2–30, both
   replicates: P(adopt | k, class) and P(keep | k, class), pooled over worlds and per world, with the
   same cluster bootstrap as `nucleation_descriptive` (2000 draws, seed 0). Report the difference
   sharp − vague at k = 0, 1, 2, 3 with its 95% interval.
2. **Automaton A2.** As in Part A, but the tables are indexed by (k, class), and each cell uses its own
   class. A bin with fewer than 20 events takes that class's value pooled over worlds. If that is
   still below 20, it takes the Part A value for k, which pools the two classes.
3. **Gate, unchanged from Part A.** 1000 runs per world × replicate from the real round-1 state,
   new fixed seed `20261019`. Real x(10) and x(20) inside the central 90% interval in ≥ 8 of 10 runs at
   each round. P(≥ 8 of 10 | calibrated) = 0.93.
4. **If the gate passes:** simulate r8 with the same process as Part A (senders redrawn every round,
   `r8_peers`, `PHONE_SEED` 20261016, empty inbox at round 1). Fix the T1 world list by the P > 0.5
   rule and lock T1 and T2 in a new amendment **before any API call**. `all` stays weak: report
   the share-interpolated simulation, and do not use it as a test.
5. **If the gate fails:** stop modelling. r8 and all are descriptive, as already recorded.

Also report, descriptively: among cells that adopted P_e while having at least one P_e neighbour, the
share that are sharp, against the base share of sharp cells. This shows directly whether fronts move
through sharp cells.

## Output

`runs/life_dr_topology/partA2_heterogeneity.{md,json}`: class sizes, step 1 tables and differences,
gate coverage per run and round with the runs outside the interval, and, if the gate passes, the
r8 and all simulations with P(direction) per world.

## Constraints

No API calls. Commit this amendment before computing any A2 number. Do not edit running scripts.
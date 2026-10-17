# Task — Is ten rounds enough? Extending the clean distributed world

**Status:** draft for lock. Predictions are locked with this file, before any round past 10 is run.
API: Luna Responses, the same settings as DRc. Parents: `TASK_LIFE_DR_CLEAN.md`,
`runs/life_dr_clean/readout.md`.

## Why

In DRc, 8 of 10 world × replicate runs were still rising at round 10, by up to +0.15 per round.
The single nine-example agent (DRo-iter) had plateaued near 0.75 by round 4. The article's
comparison "a single agent did as well or better in four of five worlds" therefore holds at ten
rounds and may not hold later. Two runs had almost no P_e left at round 10 (world 2 r2: 0.04;
world 4 r2: 0.00). With no holders, the true rule can only come back through an independent find.

## What runs

- **DRc only**: both replicates, worlds 1–5, **continued from round 10 to round 30**. DRc-noex is
  not continued; 6 of its 10 runs are already at 0.
- **Continuation by cache replay, not by a new start.** Rounds 1–10 replay from each replicate's
  own cache. Rounds 11–30 call the model.

## Gate

- **New runner file**, committed before launch. Its only change from the DRc runner is the
  number of generations (10 → 30) and an explicit replay allowance for rounds 1–10. The DRc
  runner itself is not edited.
- **Replay check:** for every world and replicate, rounds 1–10 make **0 HTTP requests** and hit
  the cache on all 1000 decisions. Any cache miss in rounds 1–10 aborts that world before
  round 11. A miss means the payload differs and the history would diverge.
- **State check at round 10:** after replay, each cell's held rule at g10 equals the logged DRc
  value for that cell, in every world and replicate. A mismatch aborts.
- **Replicate isolation:** replicate 1 continues only from replicate 1's cache, and replicate 2
  from its own. A hit on the other replicate's cache aborts.
- **Runtime assertions from DRc kept every round:** empty `source_mask`, and exactly 100
  decisions per round.
- nohup, a liveness watchdog with no auto-relaunch, and the manifest under a lock, all as in
  CHAIN_HYGIENE.

## Predictions (locked)

Notation: x(g) is the share of all 100 cells holding P_e at round g in one world × replicate run.
σ̂ = 0.189 is the DRc run-to-run noise at round 10 (5 df).

- **E1 (the climbers keep climbing).** The six runs with x(10) ≥ 0.30 (worlds 1, 3 and 5, both
  replicates) all have x(20) > x(10). Derived threshold: under no drift, each run rises or falls
  with probability 1/2, and P(6 of 6) = 1/64 ≈ 0.016.
- **E2 (lost runs stay lost).** The two runs with x(10) ≤ 0.05 (world 2 r2, world 4 r2) have
  x(30) < 0.25, the uniform-pick baseline of the world design.
- **E3 (descriptive, no threshold).** At rounds 20 and 30: the population mean per world against
  DRo-iter, with the per-world noise band σ̂·√1.5 = 0.23; the ten-run mean against 0.75.
- **E4 (descriptive).** Per run, the first round at which x ≥ 0.90, or "never by 30". Also the
  number of independent finds (switches to P_e with no P_e in the inbox) in rounds 11–30.

## Readout

- At round 20 and at round 30, report: x(g) per run, E1 and E2 verdicts, E3 and E4 tables, and
  the J(g) figure over rounds 1–30 with ten thin lines coloured by world and the mean in bold.
- **E1 holds:** ten rounds understated the clean world. The article's 10-round comparison with
  the single agent gets a sentence giving the 20- and 30-round result.
- **E1 fails:** the populations had largely settled. The 10-round figures stand as the result.
- The article is not edited until this readout is reviewed.

## Cost

DRc rounds 1–10 cost about $3.8 for both replicates. Rounds 11–30 are about twice that, ≈ $8.
**Alarm at $15. Stop at $20**, which is Artem's explicit cap for this task. Report the actual cost.

## Constraints

Closed-model outputs are not used as training data. No reasoning text is requested or stored.
Use a new runner and edit no running script. Commit this file before the gate. Amendments come
before numbers.
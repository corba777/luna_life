# Amendment — gpt-oss-120b Stage 2 runs extended to 40 rounds; convergence and clusters

**Status:** locked 2026-10-30 after the dry build below (Artem: EPOCH_LENGTH 41, extended horizon
gate). Local, pre-approved. Locked before any Stage 2 call. Basis:
`AMENDMENT_OSS120_PREDICTION.md` (O1–O3, Stage 2), `AMENDMENT_REPLICATES.md` (4 + 4 runs), the
prediction record (sha `6a0561cb…`), its `sim_inputs.json`, and the simulator as recorded.

## Why

In the recorded simulation the lattice has not settled by round 20: its mean x rises from 0.39 at
round 10 to 0.61 at round 20, while `all` is flat near 0.35. Extended with the same inputs, the
simulator says the lattice population converges on P_e, and does so by cluster growth:

| simulated (4,000 runs, record inputs) | lattice | `all` |
|---|---|---|
| mean x at rounds 10 / 20 / 30 / 40 | 0.39 / 0.61 / 0.83 / 0.94 | 0.35 / 0.37 / 0.40 / 0.43 |
| median x(30–40) [5 %, 95 %] | 0.948 [0.635, 0.979] | 0.353 [0.313, 0.964] |
| P(run x(30–40) ≥ 0.8) | 0.84 | 0.08 |
| P_e Moore components, rounds 5 / 20 / 40 (median) | 6 / 1 / 1 | — |
| largest P_e cluster, rounds 5 / 20 / 40 (median) | 14 / 60 / 97 | — |

On `all` the population mostly stays stuck, and occasionally tips (about 10 % of runs by round
40). If the real runs do the same, the lattice result is a qualitative one: a local population
reaches the true rule that a fully connected one does not reach. No agent learns anything; each call
is one pass. Convergence, if it happens, is collective.

## Change

Stage 2 runs (4 per topology) run for **40 rounds** instead of 20. Everything else is as locked.

Stage 2 runs use EPOCH_LENGTH = 41 so that world 1 holds for all 40 rounds; with the Stage 1 value
of 21 a new epoch would start at round 22.

- **O1–O3 are unchanged and are scored on rounds 1–20 only**, with the locked window x(10–20). The
  dynamics are causal, so rounds 21–40 cannot change rounds 1–20, provided the prompts of rounds
  1–20 are the same as in a 20-round run (gate below).
- Cost: 8 runs × 40 rounds × 100 cells = 32,000 calls instead of 16,000; about **104 GPU h**
  (32,000 × 11.667 s, the 1a rate), plus the sampler gate and server start.

## Gate (new)

The prompts of rounds 1–20 must not depend on the total number of rounds. Dry build: render the
round-1 and round-11 prompts with `rounds = 20` and `rounds = 40` for the same seed and state; they
must be byte-identical. If any prompt names the horizon, this amendment is withdrawn and Stage 2
runs 20 rounds as locked.

Extended (Artem, before lock), kept in the Stage 2 dry-check:
1. rounds 1–20 byte-identical for (EPOCH_LENGTH 21, rounds 20) and (41, 40);
2. no prompt in rounds 1–40 states the epoch length, the round count or the rounds left;
3. rounds 20, 21, 22 and 40 rendered with 41 and diffed against round 20: only round-dependent
   state may differ (inbox, memory, round number if shown), with no epoch-boundary text.

## Predictions (locked, from the record inputs; thresholds derived from 4,000 simulated runs)

Unit: the run. Only the 8 Stage 2 runs.

- **E1 (convergence ranking):** the mean of x(30–40) over the 4 lattice runs exceeds the mean over
  the 4 `all` runs. Scored by sign, as B1 and O1. Simulated probability 0.9997 (MC SE 0.0002). The
  exact permutation p (4 against 4, 70 splits) is reported beside it.
- **E2 (coarsening):** in at least 3 of the 4 lattice runs, the number of P_e Moore components
  (8-neighbourhood, class B included) at round 20 is smaller than at round 5. Simulated per-run
  probability 0.944 (MC SE 0.005), so P(≥ 3 of 4) = 0.982 (MC SE 0.003).
- **E3 (descriptive):** the number of lattice runs with x(30–40) ≥ 0.8 (simulated per-run 0.837,
  MC SE 0.008), of `all` runs with x(30–40) ≥ 0.8 (0.082, MC SE 0.006), the largest-cluster size and
  component count at rounds 5, 10, 20, 30, 40 per run, and the round at which a lattice run first
  reaches x ≥ 0.9.

The simulated reference values are recomputed in the dry build at 2,000 replicates (seed 0) with MC
SE and written into the locked file; the numbers above come from my independent simulator and are
replaced by those. (Done: the values above and in the dry-build section are the 2,000-rep values.)

## Dry build (2026-10-30)

**Reference values** (`runs/sim_oss120_extend40.py` on the record's `sim_inputs.json`, sha
`a6771107…`; the record's simulator and RNG order, run to 40 rounds, rounds 21–40 at the rounds 2–20
publication rates; at 20 rounds it reproduces `replay_oss120_sim_inputs.py` bit for bit. 2,000 reps,
seed 0. Output `runs/oss120/extend40_sim.json`, sha `e3626524…`.)

| simulated (2,000 runs) | lattice | `all` |
|---|---|---|
| mean x at rounds 10 / 20 / 30 / 40 | 0.39 / 0.61 / 0.83 / 0.94 | 0.35 / 0.37 / 0.40 / 0.43 |
| median x(10–20) [5 %, 95 %] | 0.477 [0.334, 0.695] | 0.348 [0.312, 0.446] |
| median x(30–40) [5 %, 95 %] | 0.947 [0.619, 0.979] | 0.355 [0.314, 0.968] |
| mean x(30–40) (MC SE) | 0.893 (0.003) | 0.419 (0.004) |
| P(run x(30–40) ≥ 0.8) (MC SE) | 0.837 (0.008) | 0.082 (0.006) |
| P_e Moore components, rounds 5 / 10 / 20 / 30 / 40 (median) | 6 / 4 / 1 / 1 / 1 | — |
| largest P_e cluster, rounds 5 / 10 / 20 / 30 / 40 (median) | 15 / 30 / 59 / 88 / 97 | — |
| lattice runs reaching x ≥ 0.9 by round 40 (MC SE) | 0.867 (0.008) | — |
| first round with x ≥ 0.9, among those runs: median [5 %, 95 %] | 30 [21, 38] | — |

E1: 500 disjoint quartets per topology, p over all 500 × 500 quartet pairs, MC SE from 1,000
bootstrap resamples of the quartets. E2: binomial in the per-run probability, SE by the delta method.

**Epoch finding.** The engine ends an epoch after `EPOCH_LENGTH` rounds and then draws a new P_e and
new examples. Stage 1 pins `EPOCH_LENGTH = 21`, so 20-round runs stay in epoch 0. At 40 rounds with
that pin, round 22 starts epoch 1 with a different P_e and new examples ("Epoch 1, generation 1"),
which is not the world the simulator extends. Decided (Artem): Stage 2 uses 41 (line under Change).

Two implementation traps, both closed by `build_stage2` in `runs/oss120_stage2_horizon_gate.py`,
which the Stage 2 runner imports:
- `_make_inner` imports modules that set the epoch length at import time (31, then 21), so a pin set
  before the build is lost on the first build in a process. Shown: lattice, pin 41 before the build
  → engine at 21 after the build, world 1 lost after round 21, round 22 reads "Epoch 1, generation 1".
  `build_stage2` pins after the build.
- The `all` inbox (`run_life_dr_qwen_stage1.slots_for`) computes the generation within the epoch
  from its own constant (21), not from the engine. With only the engine at 41, round 22 of `all`
  gets an empty inbox ("Visible messages (0 slots)" instead of 83). `build_stage2` sets that
  constant to 41 as well. The runner asserts all three values (engine, v1a, `slots_for`) = 41 before
  every round, and P_e, examples and epoch 0 after every round.

**Horizon gate** (`runs/oss120_stage2_horizon_gate.py`, output `runs/oss120/stage2_horizon_gate.json`,
sha `4c2a383f…`). The Stage 2 builder and round loop run on CPU with a stub whose decision is a
function of the prompt hash, so identical prompts give identical states. Both topologies:

1. Rounds 1–20 of (41, 40) are byte-identical to (21, 20), all 2,000 prompts per topology (rounds 1
   and 11 included). Round-1 sets equal the 1b set (lattice `e478728f`, `all` `c70a50b8`).
2. Rounds 1–40: with the per-cell and per-round paragraphs masked (cell line, header, examples,
   query, previous step, inbox, catalog, and in `all` the inbox slot count in the intro sentence),
   all 4,000 prompts per topology share one template. That template contains none of: 20, 21, 40,
   41, "epoch length", "round(s)", "remaining", "left", "final", "horizon", "total", "out of",
   "end(s)", "until". Every header is "Epoch 0, generation t of this epoch." with t the round
   (the round number is shown; the length and the rounds left are not). The examples, and the set of
   catalog entries, are the same in every round.
3. Rounds 21, 22, 40 against round 20, per cell: what differs is the header round number (100
   cells), the query (99–100), the previous step (99–100), the inbox (100; in `all` also its slot
   count) and the catalog order (100: the option order is drawn per round, as in rounds 1–20; the
   entries do not change). Nothing else differs; no epoch-boundary text. P_e, the world-1 examples
   and epoch 0 hold through round 40.

**Pass.**

## Pre-stated readings

- **E1 and E2 hold:** on the lattice, the true rule spreads from the witnesses through growing
  clusters until it covers the population; on `all` it does not. The micro-to-macro prediction
  extends from a ranking to a qualitative outcome.
- **E1 holds, E2 fails:** the lattice wins, but not by cluster growth; the spatial mechanism of the
  model is wrong.
- **E1 fails (lattice stalls):** the simulator's long-run behaviour is wrong. The most likely
  cause is the witness convention (class B held at P_e from round 2): in the population witnesses
  may abandon P_e. The per-round witness share is reported to decide this.

## Design audit

1. **Fidelity.** Same runner, prompts and server; only the horizon is longer (gate above).
2. **Coverage.** gpt-oss-120b only. Continuing the existing gpt-oss-20b and Qwen runs past round 20
   is a separate decision; Luna is not extended (budget).
3. **Controls.** `all` runs extended equally.
4. **Observability.** Cells see their prompts only.
5. **Gate consistency.** All Stage 2 gates plus the horizon gate run before the first call.
6. **Statistical unit.** The run.
7. **Pre-stated readings.** Above.
8. **Recheck.** Per-round cell states and final text per call are exported; clusters are recomputed
   from the cell states with independent code.
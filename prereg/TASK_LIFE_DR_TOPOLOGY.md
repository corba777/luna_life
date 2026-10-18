# Task — Topology in the clean distributed world (reasoning agent)

**Status:** ready for lock. The structure and tests are locked with this file. The T1 world list is
fixed by Part A (no API) and recorded in an amendment before any API call. API: Luna Responses, `reasoning.effort = medium`, the same settings
as DRc. Parents: `TASK_LIFE_DR_CLEAN.md`, `TASK_LIFE_DR_CLEAN_EXT.md`,
`AMENDMENT_DR_CLEAN_EXT_PINNED.md`, `runs/life_dr_clean_ext_pinned/readout_g30.md`, `ARM_REGISTRY.md`.

## Why

The clean distributed world has been run only on the lattice (DRc). There it splits: worlds 1, 3
and 5 reach the full grid by rounds 11–15, and worlds 2 and 4 are bimodal across replicates. This
task asks how much of that comes from the topology of the rule channel:

| channel | reach | local cliques | question |
|---|---|---|---|
| moore (DRc, existing) | 8 | many | baseline: nucleation with critical mass |
| r8 | 8 | almost none | same reach, no local reinforcement (Montanari & Saberi 2010) |
| all | 99 | one global clique | global plurality decides; Zollman effect risk |

This is the reference row of the agent × topology matrix. Later rows (Luna Decisions, Qwen,
SPADE) are compared with it.

## Arms

| registry name | runs |
|---|---|
| `dist/luna.resp-medium/r8/none` | 2 independent replicates × worlds 1–5 × 20 rounds |
| `dist/luna.resp-medium/all/none` | 2 independent replicates × worlds 1–5 × 20 rounds |
| `dist/luna.resp-medium/moore/none` (DRc) | existing pinned data, rounds 1–20, not rerun |

**Channel content (decided by Artem): only the rule channel changes.** Each cell still sees 9
examples: its own and those of its 8 Moore neighbours, as in DRc. The other design, where examples
follow the channel, was rejected. In `all` it would hand every cell all 100 examples and turn the
world into a single-agent problem. The agent first confirms from code which channel carries examples
in DRc and records it in the manifest. If DRc does not carry neighbour examples as described, the
agent stops and reports before any run.

Everything else is byte-identical to DRc: worlds, examples, catalog, prompt template, schema,
parser, no check, empty `source_mask`. The `r8` senders are drawn once per world from the committed
`PHONE_SEED` and stay fixed for all rounds; both replicates use the same draw.

## Gate

- **New runner, committed before launch.** `EPOCH_LENGTH` is set explicitly to at least 21 and recorded
  in the manifest.
- **Pinned world, checked live every round:** P_e and the hash of all 100 examples are identical
  to round 1. Any change aborts the run (CHAIN_HYGIENE §26).
- **First live prompt diff:** before round 1 of each world, the rendered prompt for 3 cells is diffed
  against the DRc round-1 prompt for the same cells. The only allowed difference is the inbox block.
  The diff is saved to the manifest. In the `all` arm, the inbox shows all 99 senders.
- **Runtime assertions from DRc, every round:** empty `source_mask`; exactly 100 decisions; no check
  applied.
- **Independent replicates:** each replicate has its own empty cache directory. A cache hit across
  replicates or arms aborts the run.
- nohup, a liveness watchdog with no auto-relaunch, the manifest under a lock, commit hash per arm ×
  replicate × world.

## Noise and the test (derived, locked)

Let x(g) be the share of the 100 cells holding P_e at round g in one run.

- **σ̂ at round 20**, pooled over all replicate pairs at g20: 5 moore pairs (pinned DRc), 5 r8 and 5 all.
  σ̂² = mean over the 15 pairs of (x¹ − x²)²/2, with 15 df.
- For each topology T ∈ {r8, all}: D_T = (1/5)·Σ_w (m_T,w − m_moore,w), where m is the replicate
  mean. Var(m_T − m_moore) = σ², so SE(D_T) = σ̂/√5.
- **Two-sided test, descriptive:** t = D_T / SE(D_T) against t₁₅ = 2.131 (α = 0.05). Part A predicts
  opposite signs in different worlds, so the pooled D_T can cancel. The primary tests are T1–T2 below.
- **Limitation, stated in advance:** x is bounded, and runs at 0 or 1 add almost no variance. A pooled
  σ̂ assumes the same noise in all topologies; the per-topology σ̂ are reported next to it.

## Part A — predictions from the measured lattice rule (no API, before any run)

Source: `runs/life_dr_clean_ext_pinned/nucleation_descriptive.json`. The measured per-world tables
P(adopt | k) and P(keep | k), k = P_e senders among 8, define a stochastic cellular automaton. It is
a lookup table with no fitted parameters. Bins with fewer than 20 events take the pooled value.

The adoption curve is a complex contagion: 0.007, 0.024, 0.039, 0.13, 0.40, 0.73, 0.90 for k = 0…6.
A simple contagion fitted at k = 1 gives 0.09 at k = 4 against 0.40 measured. The midpoint is near
k ≈ 4.3 of 8, a local majority.

Steps:
1. **In-sample gate (Moore).** Simulate the lattice from each run's real round-1 state, 1000 runs per
   world × replicate, and get the central 90% interval of x(10) and x(20). Gate: the real x falls
   inside the interval in ≥ 8 of the 10 runs at each round. If the automaton is calibrated, each run is
   covered with probability 0.9, and P(≥ 8 of 10) = 0.93. **If the gate fails, the automaton gives no
   prediction.** The r8 and all runs are then reported as descriptive only.
2. **r8.** Simulate on the committed r8 sender graph. The inbox has 8 slots as on the lattice, so the
   table transfers without a change of inbox size. That inbox-size change was what failed in the
   calibration task.
3. **all.** The table is indexed by k of 8. Using it for 99 senders needs an assumption: the share
   s = k/8, interpolated. This is the transfer that failed in calibration Part 3. The `all` prediction
   is therefore labelled **weak**, and a failure there is read as "inbox size changes the choice rule",
   not as a topology result.

Preliminary deterministic mean-field values (binomial sender draws for r8, exact share for all),
computed before this file. They are not the locked numbers; the stochastic simulation replaces them:

| world | moore g10 / g20 (real, r1, r2) | r8 mean-field g10 / g20 | all mean-field g10 / g20 |
|---|---|---|---|
| 1 | 0.61, 0.80 / 1.00, 1.00 | 1.00 / 1.00 | 0.22 / 0.22 |
| 2 | 0.23, 0.04 / 0.53, 0.03 | 0.04 / 0.06 | 0.04 / 0.04 |
| 3 | 0.39, 0.83 / 1.00, 1.00 | 0.99 / 1.00 | 0.25 / 0.98 |
| 4 | 0.26, 0.00 / 0.40, 0.01 | 0.02 / 0.02 | 0.02 / 0.01 |
| 5 | 0.84, 0.68 / 1.00, 1.00 | 1.00 / 1.00 | 0.34 / 1.00 |

The hypothesis this implies: **locality helps the rare-find worlds and slows the common-find worlds.**
Random mixing spreads P_e faster where it starts common (worlds 1, 3 and 5). Where P_e starts rare and
fragile (worlds 2 and 4), only the lattice lets a local cluster form a local majority, which is
nucleation. This is the trade-off of Montanari & Saberi (2010), and it was not what the reviewer
expected before computing it. The expectation had been "Zollman: r8 and all slower everywhere".

## Predictions (locked after Part A, before any API run)

Because the predicted sign differs by world, the pooled D_T can cancel. D_T stays as a descriptive
statistic. The primary tests are per world:

- **T1 (r8, direction).** In worlds 1, 3 and 5, the replicate mean of r8 at g10 exceeds the moore mean
  at g10. In worlds 2 and 4, the r8 mean at g20 is below the moore mean at g20. The world list is
  final only if the stochastic simulation gives the same direction with P > 0.5 in each world; worlds
  where it does not are dropped from T1 before lock. Chance level: (1/2)^n for n listed worlds
  (1/32 for all five).
- **T2 (r8, level).** Real x(10) and x(20) inside the simulated central 90% interval in ≥ 8 of 10 runs
  (coverage argument as in the gate, 0.93).
- **T3 (all, weak).** The same two tests on the all simulation. Reported with the transfer caveat.
- **Descriptive:** first round with x ≥ 0.90; independent finds per round; replicate agreement per
  world; D_T with t against t₁₅.

## Readout

x(g) per run; D_T, t and verdicts; T1–T3; the figure of J(g) over rounds 1–20, with one panel per
topology, thin lines per run coloured by world, and the mean in bold. Article text is not edited
until the readout is reviewed.

## Cost

Agent estimate from logged tokens, scaled by prompt length, 2 replicates × 5 worlds × 20 rounds:
all ≈ $7.4, r8 ≈ $4.8, total ≈ $12.2. Output tokens are assumed equal to the lattice, which may
understate the cost if reasoning gets longer on a 99-sender inbox. Before the full launch, the first
round of world 1 in `all` is run alone and its measured cost per call replaces the estimate.
**Alarm at $15. Stop at $20** (confirmed by Artem).

## Order of work

1. Commit this file.
2. Confirm the example channel from code (see Arms).
3. Part A: the automaton, the in-sample gate, the r8 and all simulations. Write
   `runs/life_dr_topology/partA_predictions.{md,json}`. Fix the T1 world list from the simulation and
   record it in an amendment **before** any API call.
4. Write and commit the runner, then run the gate checks and the single-round cost probe for `all`.
5. Launch both arms. Report at g10 and at g20.

## Constraints

Closed-model outputs are not used as training data. No reasoning text is requested or stored.
Use a new runner and edit no running script. Commit this file before the gate. Amendments come
before numbers.
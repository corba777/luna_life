# Amendment — random-8: separating mixing from message volume (gpt-oss-20b, world 1)

**Status:** locked v3 (2026-11-15; v2 names the two accounts in Why; v3 fixes the three defects from
the agent's dry build and adds the locked theory prediction T8), before any call. Written by the
reviewer for Artem; dry build accepted; locked on Artem's instruction. No call is made before
Artem's go. It runs locally on the GPU after the anchor/inference battery.

## Why

The paper's locked replicate test (`AMENDMENT_REPLICATES.md`, R1) found gpt-oss-20b ahead on the
complete graph: mean x(10–20) was 0.71 on `all` against 0.35 on the Moore lattice, in six runs per
topology (p = 1/924). The two topologies differ in two ways at once:

- **Mixing.** On the lattice, a cell hears the same eight neighbours every round. On `all`, it
  hears the whole population.
- **Volume.** On the lattice, a cell sees at most 8 lines. On `all`, it sees every line published
  in the previous round, up to 99.

The `all` advantage could come from either. An external review raised this, and the paper does not
yet separate the two. A third topology does, keeping the lattice's volume and the complete graph's
mixing.

**Two named accounts.**
- **Volume.** In the spin-model account of LLM debate (Okawa 2026, ICML; PMLR 306), topology enters
  only through the effective number of observed neighbours z̄, and collective alignment grows with
  λ z̄ / T. On that account, random-8 (z̄ = 8) should behave like the lattice.
- **Mixing.** An effect of spatial structure beyond z̄: the same eight neighbours every round on
  the lattice, against fresh ones on random-8. On that account, random-8 should behave like `all`.

The tests and readings below are unchanged by this framing. The "volume" reading is the z̄-only
mean-field account; the "mixing" reading is an effect of structure beyond z̄.

## The new topology: random-8

- **Inbox.** Each round, each cell gets 8 slots. Their senders are 8 distinct cells drawn uniformly
  from the other 99, afresh each round.
  - The draw is `random.Random(int.from_bytes(sha256("random8|run|round|cell")[:16], "big")).sample(others, 8)`,
    where `others` is the list of the other 99 cells in increasing order. The slots keep the order
    of the sample.
  - `run` is 1–6 for the six model runs, and `round` is the 1-based decision round.
  - The simulator's replicates use their own run numbers (1–2,000). The simulator is not a model
    run, so sharing numbers 1–6 with the real runs does not matter.
- **Slots.** As on the lattice, a slot shows the sender's line if the sender published in the
  previous round, and is empty if it did not. The engine's local TTL is 1. In 15,200 stored lattice
  slots of an R1 run, every non-empty slot had lag 1.
- **Prompt.** It is the lattice prompt with only the sender identities changed. The constitution
  already describes the inbox as "eight message slots from other cells" and visibility as "only to
  cells allowed to see them", so no wording changes. The dry build verifies this. For one cell and
  round, the random-8 prompt and the lattice prompt differ only in the `sender=` values and the line
  contents of the slots.
- **The graph is directed and changes every round.** A sender does not see its listeners. This
  differs from both reference topologies, and it is stated as a limit.

## Runs, model, engine

- **Runs.** Six runs on world 1, 20 rounds each, with the same configuration as the six R1
  replicates.
  - Model: gpt-oss-20b, same revision.
  - Engine: SGLang, same image and launch spec.
  - Sampling: same as R1. No request seed; the cell order follows the stored rule.
- **Date.** The rendered date is pinned to 2026-11-03 with a pinned chat template. The replicates
  rendered 2026-11-03 or 2026-11-04. A paired check found no date effect (Limitations).
- **Calls and time.** 6 × 100 × 20 = 12,000 calls. The agent states the time from the R1 runs'
  measured wall time.

## Comparison set

The six R1 replicate runs per topology (lattice and `all`), as stored. The two original runs per
topology are not used, since R1 itself used only the six new ones. Using the same comparison set
avoids choosing runs after seeing them.

## Prediction from theory (computed before the lock, no model call)

The battery-driven simulator that produced the R1–R3 bands is run in a random-8 mode.
- **Inputs.** The same 20b battery fits as R3.
- **Mechanism.** Each cell samples 8 senders per round, and k and m (P_e and prefix lines among the
  8) enter the same a(k, m) and b(k, m).
  - Publication follows the lattice's measured schedule, by round and class, because random-8 uses
    the lattice prompt surface.
  - The start is round 1 as on the lattice. The inbox window is the previous round only.
- **Runs.** 2,000 simulated runs.

**Locked outputs:**
- the predicted mean x(10–20) for random-8 and its 5–95 % band;
- the predicted position π = (x̄_r8 − x̄_lat) / (x̄_all − x̄_lat), using the simulator's own lattice
  and `all` means;
- the power of M1 and M2 below at six runs. For this, run-to-run spread is taken from the simulator
  and, beside it, from the R1 runs' observed standard deviations.

For the power check, random-8 has no runs of its own, so its run-to-run SD is taken from the R1
lattice runs (0.062). The two topologies have the same volume. The simulator's own random-8 SD
(0.085) is reported beside it. If both powers are below 0.5, the agent reports this before the lock,
and Artem decides whether to add runs or proceed.

**Computed before the lock** (`runs/topology_random8/prediction_random8.json`, sha256
`f957d4bab5d4fc469356ce0476f6aeddaebf338cfdcc4c36938b1c84eddfbc28`):

| | simulator mean x(10–20) | 5–95 % band |
|---|---:|---|
| lattice | 0.406 | [0.314, 0.535] |
| random-8 | 0.411 | [0.325, 0.587] |
| `all` | 0.673 | [0.418, 0.876] |

- Predicted π = 0.018.
- Power at six runs: M1 0.02–0.03 and M2 0.89–0.96, from the simulator and from the R1 SDs.
- R1 lattice SD (proxy for random-8 in the R1-SD power arm): 0.062. Simulator random-8 SD: 0.085.

The response-function theory therefore predicts the **volume** reading. Random-8 should stay at the
lattice's level, because with eight slots the model's a(k, m) gains nothing from fresh senders.
This turns the control into a test of the theory's own account of the topology gap.

**Theory test T8 (locked).** The prediction holds if three conditions are met together:
- M1 fails;
- M2 holds;
- at least 4 of the 6 random-8 runs lie inside the simulator band [0.325, 0.587].

The 4-of-6 threshold comes from the simulator. A run falls in its own 5–95 % band with probability
0.90, so under the theory P(≥ 4 of 6) = 0.984, and the false-rejection rate is 1.6 %. T8 is reported
beside the M1/M2 readings. It does not change them.

## Locked tests

Both are exact one-sided permutation tests on the run means of x(10–20), six against six, each at
α = 0.025 (Bonferroni over two). The smallest possible p is 1/924.

| name | statistic | holds if |
|---|---|---|
| M1 | x̄(random-8) − x̄(lattice) | p < 0.025 (random-8 higher) |
| M2 | x̄(`all`) − x̄(random-8) | p < 0.025 (random-8 lower) |

**Pre-stated readings:**

| M1 | M2 | reading |
|---|---|---|
| holds | fails | Mixing carries the topology effect. Random-8 reaches `all`'s level with the lattice's volume, so the claim stands as written. |
| fails | holds | Volume carries it. Random-8 stays at the lattice's level, so the effect is about how many lines an agent reads, not about who they come from. The claim is rephrased around inbox size and composition. |
| holds | holds | Both contribute. Random-8 lies between the two; π is reported with its bootstrap interval over runs. |
| fails | fails | Not separated at six runs. Reported as such, with the observed π. |

## Descriptive, beside the tests

- **π.** Observed π, with a 95 % interval from bootstrapping the runs within each topology.
- **Bands.** How many of the six random-8 runs lie inside the simulator's 5–95 % band, as R3 does
  for the other topologies.
- **Witnesses.** The share of witnesses on P_e at round 20, by topology.
- **Inbox composition.** The mean share of P_e among non-empty slots seen by class-A cells, by
  round and topology. This shows whether random-8 reproduces `all`'s inbox composition at lattice
  volume.
- **Signal conventions on random-8.** Whether a population-wide convention forms under the page's
  rule. On `all`, 20b forms one in most runs; on the lattice, none forms. This is descriptive only.
  It speaks to the signals story but is not part of this paper's claim.

## Gates

- **Format.** As in R1: invalid or truncated answers, retry rule and stop threshold unchanged.
- **Prompt identity.** The dry build replays round 2 of one stored lattice run with random-8
  senders. It must show that the prompts differ only inside the slots.
- **Sampler.** The dry build shows the sender draw for three cells and two rounds. It also shows
  that the draw never includes the cell itself, and never repeats a sender within one inbox.

## Limits

- One model and one world.
- Six runs.
- The random-8 graph is directed and changes every round. It matches the lattice in volume and
  `all` in mixing, but it is not the only way to do either.
- A result for 20b does not carry over to the threshold model (Luna) or to 120b. Those would need
  their own runs, which are not planned here because of the Luna budget and 120b's GPU cost.

## Outputs

- The run directories, in the R1 format.
- `runs/topology_random8/prediction_random8.json`, written before the lock and pinned by sha256
  `f957d4bab5d4fc469356ce0476f6aeddaebf338cfdcc4c36938b1c84eddfbc28`.
- `readout.json` / `.md`.
- A recheck package in the usual format: rule histories, inboxes, prompts, simulator code and
  seeds, and SHA256SUMS.

Nothing enters the paper before the reviewer's recheck from raw data.

## Queue

1. `wait_qwen_anchor_inference_done`.
2. `wait_go_topology_random8`, which needs a go file and a switch-log line with Artem's words.
3. Precheck: manifest sha, free GPU, no foreign SGLang.
4. Runs.
5. Readout.
6. Package.

Every `gpu_step` call site uses `|| fail`. Watcher v3 and the GPU monitor run beside it.

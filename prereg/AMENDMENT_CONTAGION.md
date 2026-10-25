# Amendment — response rule × topology: a dose-response battery, a micro → macro simulation, and a gpt-oss-20b confirmation in worlds 3 and 5

**Status:** locked 2026-10-25. The second dry build (`runs/contagion/gate.json`, 2026-10-25) filled the
values below. Local arms are pre-approved. The Luna arm runs inside the $20 envelope
(spent $10.3993). Basis:

- `runs/model_panel/oss20_all_readout.md`;
- `runs/model_panel/oss20_lattice_readout.md`;
- the `all` hazard tables for gpt-oss-20b, Luna medium and Qwen;
- the panel fingerprints;
- `DESIGN_AUDIT_CHECKLIST.md`.

## Why

In world 1, with byte-identical `all` prompts, the topology ranking reverses between models:

| model | lattice mean x(10–20) | `all` mean x(10–20) |
|---|---|---|
| Luna medium | 0.86, 0.97 | 0.23, 0.31 |
| gpt-oss-20b | 0.37, 0.45 | 0.85, 0.87 |
| Qwen-Thinking | moore is running | 0.16, 0.20 |

The witnesses of both models end on P_e (class B 24–25/25). What differs is how class A responds to
the messages it sees.

This resembles the diffusion distinction between complex contagion, which needs a threshold share of
contacts and spreads in clustered networks (Centola and Macy, 2007), and simple contagion, which
spreads fastest under global mixing. The first dry build shows the plain version of that story is
not enough:

- **No class-A cell has four or more class-B Moore neighbours.** On a filled lattice inbox, a majority
  step can therefore never fire from the witnesses alone. A pure step curve stays at x = 0.25 on both
  topologies.
- **Luna's lattice win must use what a filled-inbox step leaves out: empty slots.** Luna's battery
  L fingerprint is 0.85. That is the difference between adopting P_e from one P_e line with seven
  empty slots and from one P_e line with seven prefix lines. Luna class A publishes in 1% of cells at
  round 1, so early lattice inboxes are mostly empty, and a witness's line can be the whole visible
  majority.
- **gpt-oss-20b's L is 0.275.** Its class A publishes from round 1 (89%), and the prefix fills
  inboxes at once.

So the candidate mechanism has two parts: the response to visible lines, with empty slots not
counting against, and the publication policy, which sets how many slots are empty. Part A measures
the response, empty slots included. Part B puts the measured publication policy back in and asks
whether the two together predict the ranking. Part C checks the gpt-oss-20b reversal in two new
worlds.

## Part A — dose-response battery

- **Cells:** 20 world-1 class-A cells, by the ascending hash `sha256("cdr|{cell}")`: 91, 62, 59, 5,
  57, 52, 35, 46, 15, 32, 12, 1, 95, 37, 64, 2, 83, 26, 97 and 19. The source is the panel full-run
  builder at round 4.
- **Two directions, with memory as a constructed state:**
  - **Adopt:** memory `Previous step: rule='<prefix>' published=yes`. The outcome is "answers P_e".
  - **Abandon:** memory `Previous step: rule='<P_e>' published=yes`. The outcome is "answers the
    prefix".
- **n = 8 (lattice):** (k P_e lines, m prefix lines, 8 − k − m empty slots), using the builder's own
  empty-slot rendering.
  - **Filled:** k + m = 8, with k = 0, 1, 2, 3, 4, 5, 6, 8.
  - **With empty slots:**
    - k = 1 with m = 0, 1, 2, 3;
    - k = 2 with m = 0, 1, 2, 3;
    - k = 3 with m = 0, 1, 2.
  - That is 19 conditions.
- **n = 88 (`all`):** P_e share 0, 0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.75, 1.00, giving P_e
  counts 0, 4, 9, 18, 26, 35, 44, 53, 66 and 88, with prefix lines filling the rest. An `all` inbox
  holds only published lines, so it has no empty slots. That is 10 conditions.
- **Positions, signals and models:**
  - Positions follow the redo hash.
  - Signals come from the Part D hash over the world-1 published-signal pools of the corresponding
    rule (7,592 P_e signals, 10,145 prefix signals).
  - The models are Luna medium (API), gpt-oss-20b and Qwen3-4B-Thinking-2507 (local, the panel
    settings). Every model gets the same message content, byte for byte.
- **Draws:** 2 per cell and condition. The exception is the n = 88 minority shares (0.05–0.30), which
  get 6 draws in both directions, because A2 had power 0.216 at 2 draws. Power at 6 draws is 0.637, moderate.
- **Calls per model:** 2,960. That is 19 × 2 × 20 × 2 = 1,520 at n = 8, plus 480 for the six
  non-minority shares at 2 draws, plus 960 for the four minority shares at 6 draws.
  - Luna cost $1.4356, cap $2.8712. Stored medium means, first 2,000 files: short input 2,212.83,
    long input 3,805.06, output 372.53. Envelope after this arm: $11.8349 of $20.
  - Local wall time: gpt-oss-20b 3.90 h at 4.74 s/call; Qwen 31.23 h at 37.98 s/call. Qwen is the
    long arm.

**Measures, descriptive, per model and direction:**

- P(outcome | condition), with the panel hull;
- at n = 8, a logistic fit in (k, m), log-odds = a + b·k + c·m;
- at n = 88, a logistic fit in share.

**Predictions (locked).** The unit is the cell, draws pooled. One-sided cell-level sign-flip
comparing two models on the same 20 cells, α = 0.05.

- **A1 (step at n = 88):** S88 = P(adopt | 0.60) − P(adopt | 0.40) is larger for Luna medium than for
  gpt-oss-20b. Basis: battery S, 0.675 against 0.20.
- **A2 (minority uptake at n = 88):** M88 = mean P(adopt | 0.10, 0.20, 0.30) is larger for gpt-oss-20b.
  Basis: the `all` hazards, 0.054 against 0.023 at 11–25 lines.
- **A3 (resistance to a majority at n = 88):** R88 = P(abandon | 0.30) is larger for Luna medium.
  Basis: the hazards onto the prefix at a prefix majority, 0.72 against 0.12–0.25.
- **A4 (empty slots do not count against):** E8 = P(adopt | k = 1, m = 0) − P(adopt | k = 1, m = 7) is
  larger for Luna medium than for gpt-oss-20b. Basis: battery L, 0.85 against 0.275.
- **Qwen:** not predicted. It is reported against both models.

## Part B — micro → macro simulation (no model calls)

The code is `runs/contagion_sim.py`. Its final version is committed before any Part A call.

- **Population:** the world-1 grid and class layout, on the lattice (8 Moore neighbours) and on
  `all`.
- **Inputs measured from each model's own world-1 full runs:**
  - class-B round-1 holding, after which class B keeps P_e;
  - the publication probability by round and class, with round 1 kept apart.
- **Class-A updates:** class A follows that model's Part A fits.
  - On the lattice, the n = 8 (k, m) fit is applied to the counts of P_e and prefix lines in the
    cell's 8 slots. Unpublished neighbours are empty slots.
  - On `all`, the n = 88 share fit is applied to the P_e share among published lines.
  - The adopt fit acts on prefix holders, and the abandon fit on P_e holders.
- **Runs:** 200 replicates per model × topology, numpy Generator seed 0, rounds 1–20, and mean x(10–20).

**Mechanics checks, gates, live calls refused.** The synthetic expectations of the first draft are
withdrawn: the dry build showed they were wrong for this class geometry. They are replaced by checks
with derived answers.

- **(i) Deterministic cases:**
  - an adopt probability of 0 everywhere keeps x at its round-1 value;
  - an adopt probability of 1 on any P_e line, with everyone publishing, reaches x = 1 on `all` by
    round 2, and on the lattice by round 1 + the largest Moore distance from any class-A cell to a
    class-B cell, which is 1. Every class-A cell already has a class-B Moore neighbour (the minimum is
    2), so this case reaches x = 1 at round 2 on the lattice as well as on `all`. Adopt probability 0
    keeps x at its round-1 value, 0.25, on both topologies.
- **(ii) In-sample replay:** driven by the empirical full-run hazards of each model, binned by (k, m)
  on the lattice and by share on `all`, the simulator's median mean x(10–20) falls within the two
  observed replicates' range ± that range's width. This checks the mechanics only. It is not the
  prediction. Dry build, both models, both topologies: the median is inside that band. Luna lattice
  median 0.972 against replicates 0.865 and 0.967; Luna `all` 0.291 against 0.232 and 0.307;
  gpt-oss-20b lattice 0.448 against 0.374 and 0.445; gpt-oss-20b `all` 0.885 against 0.850 and 0.871.
  An unseen bin adopts and abandons at probability 0. The Luna lattice figures are the pinned DRc
  histories.

**Prediction (locked):**

- **B1:** using the Part A fits, not the full-run hazards, the median simulated sign of
  x_lattice − x_all equals the observed sign for Luna medium (positive) and for gpt-oss-20b
  (negative).
- **Qwen:** scored once moore gives its lattice x.

**Pre-stated readings:**

- **B1 holds for both models:** the controlled response, empty slots included, plus the publication
  policy, reproduces which topology wins. That is a micro → macro link with no topology-specific
  fitting.
- **B1 fails while A4 holds:** the empty-slot effect exists, but it does not carry the ranking.
- **B1 fails in general:** something the fits omit matters, for example memory over more than one
  step, signal values or line order. The failure is reported, and the simulation is not tuned after
  the fact.

## Part C — gpt-oss-20b confirmation in worlds 3 and 5

- **Runs:** gpt-oss-20b, the panel full-run builder and settings, worlds 3 and 5, `all` and lattice
  (Moore), 2 replicates each, 20 rounds. That is 8 arms and 16,000 calls, about 21 h.
- **Reference:** Luna medium's existing `all` histories in worlds 3 and 5. They match the panel
  builder byte for byte at rounds 1 and 11 (dry build). Luna's lattice histories in those worlds are
  r8 (random 8 peers), not Moore, so they are **not comparable** and are reported only as labelled
  descriptives.

**Predictions (locked).** Each must hold in both replicates of a world.

- **C1:** gpt-oss-20b on `all` has mean x(10–20) > 0.5. The threshold is definitional: a population
  majority.
- **C2:** gpt-oss-20b's mean x(10–20) on `all` exceeds its own Moore-lattice mean.

**Pre-stated readings:**

- **C1 and C2 hold in both worlds:** the reversal is not a world-1 property.
- **A failure in one world:** reported with that world's Luna `all` level beside it. No Moore Luna
  reference exists there.

## Gates (live calls refused unless stated)

- **World-1 Luna lattice reference.** The pinned DRc histories are compared with the panel Moore
  builder byte for byte, at round 1 and round 11, the check already done for `all`.
  - Result: 100/100 cells, both replicates, both rounds, and the replayed rules match the pinned
    histories. The world-1 lattice comparison is like-for-like. A4 and B1 are not flagged.
  - If they had differed, the comparison would have been restated as not like-for-like, and A4 and
    B1 flagged accordingly.
  - This gate was run first.
- **Part A inboxes:** exact k P_e lines, m prefix lines, and empty slots rendered by the builder.
  Positions and signals are by hash. Prompts are byte-identical across conditions outside the memory
  line and the inbox block, and across models.
- **Part B:** checks (i) and (ii) above.
- **Part C:** prompt identity against the Luna world-3 and world-5 `all` references. Passed in the dry
  build.
- **Standard:** the sampler gate, live, for gpt-oss-20b and Qwen before their Part A arms; the Luna
  cost cap and envelope projection.

## Design audit

1. **Fidelity.** Part A is built by the panel builder, including its empty-slot rendering. The
   constructed memory and inbox are stated. Part C uses the full-run builder unchanged.
2. **Coverage.** Part A uses world-1 class-A cells. Part C uses worlds 3 and 5. Class B is not tested
   in Part A, because witnesses hold in every model.
3. **Controls.** Part A gives the same cells and content to every model, with counts manipulated
   within a model. Part B's mechanics checks and in-sample replay come before the out-of-sample
   prediction. Part C's references are matched for `all` only.
4. **Observability.** A cell sees its prompt only.
5. **Gate consistency.** All gates above run together. The world-1 Luna lattice gate runs first.
6. **Statistical unit.**
   - Part A: 20 cells, paired across models. Power, 2,000 simulations, 20,000 sign-flips, Generator
     seed 0, one-sided: A1 0.996 (2 draws); A2 0.637 (6 draws, moderate); A3 1.000 at the 0.12 end and 0.993
     at the 0.25 end (2 draws); A4 0.9995 (2 draws). A1 and A4 put the named contrast on the high
     condition and 0 on the low condition.
   - Part C: the replicate, 2 per arm, with each prediction required in both. This is weak, and
     stated.
7. **Pre-stated readings.** Above.

## Queue

1. The world-1 Luna lattice gate, now; it needs no GPU.
2. Part A: Luna on the API after the lock. The local arms after moore and before wave 2a: gpt-oss-20b
   (3.90 h), then Qwen (31.23 h at 37.98 s per call).
3. Part B, as soon as Part A closes; CPU only.
4. Part C, after wave 2b.
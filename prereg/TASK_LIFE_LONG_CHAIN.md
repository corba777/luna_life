# Task — Long chain: does the true rule travel five hops from a single source?

**Status:** locked (predictions before first call; Part 0 closed; W2 received-only amendment
locked before multi-seed close). Zero-source arm **B0** / W6–W8: see
`AMENDMENT_LONG_CHAIN_B0.md` (commit before first B0 call). API only (Luna), no GPU. Parent:
`TASK_LIFE_REASONING_CELLS.md`. Diagnostics carried over from `TASK_LIFE_SPREAD_DIAG.md`.

## Why

In the main runs, four sources are spaced so that every cell is at most two Chebyshev steps from one
(8 Moore neighbours, TTL = 1, no forwarding; a cell publishes only the rule it holds). The rule
only has to travel two hops, so the grid says little about chains. Cells adopt and republish, so
the rule moves as a wave, and on the wavefront a cell usually sees **one** neighbour with P_e.

Spread diagnostics: reasoning cells switch on one P_e neighbour 51% of the time per generation and
track the reachability bound (median lag 0). One-pass cells mostly follow the crowd: 3% on one
neighbour, 25% on 3+. A long chain separates the two. A wave of reasoning cells should survive one
neighbour at a time; a wave of crowd-followers should stall at its front.

## Part 0 — Fix the dose–response first (logs only, before any new run)

`TASK_LIFE_SPREAD_DIAG.md` reported `prev_correct` as missing. It is recoverable from
`memory.previous_correct`, as already done for Ca. Recompute P(switch to P_e | exposed) for B, Ca
and Da on the existing runs, stratified by:
- `prev_correct` (true / false);
- `n_competing` consistent rules (0 / 1 / 2+), where this can be computed;
- generation bucket (1–3 / 4–10).

Report whether B's rise from 1 to 3+ P_e neighbours survives stratification. This number feeds the
reading of W1 below; it does not change any prediction.

### Part 0 — closed (logs only; before long-chain close)

Artifact: `runs/life_reasoning_cells/spread_diag_stratified.json`.

Votes are not a simple “need a crowd” story for reasoning / checked cells. Stratified on
`prev_correct=false` (cell just told “wrong”):

| arm | competitor rules in inbox consistent with the example | P(switch\|1 P_e nb) | P(switch\|3+)|
|---|---|---:|---:|
| **B** | 0 | ~0.77 | ~0.87 |
| **B** | 1 | ~0.25 | ~0.75 |
| **Da** | 0 | ~0.75 | ~0.97 |
| **Da** | 1 | ~0.04 | ~0.41 |
| **Ca** | 0 | ~0.04 | ~0.27 |

**B / Da:** check filters first; among survivors, vote count breaks ties. One P_e neighbour is
enough when the check leaves a unique candidate; when two rules pass the check, majority decides.
**Ca:** no check — always crowd-following, even with zero competitors.

Chain implication: the wavefront usually shows one P_e neighbour. With no compatible competitor,
reasoning cells accept ~77%/gen; with a competitor, that cell can stall. W1 can still fail on
hard sets with many check-compatible candidates. Raw B 1→3+ rise is mostly this confound, not a
hard multi-vote requirement.

## Design

| arm | cells | sources | channel | check |
|---|---|---|---|---|
| **B1** | Luna Responses, medium | **1** | on | own reasoning |
| **Ca1** | Luna Decisions, argmax | **1** | on | none |
| **Da1** | Luna Decisions, argmax | **1** | on | engine ✓/✗, k=1 |

- **One source** at cell 0. On the 10×10 torus with Moore neighbourhoods, the maximum distance to it
  is 5.
- **Same world seeds as the main 2-op runs (1–5):** same P_e, same private examples, same order
  seeds. Every contrast against the four-source arms (B, Ca, Da) is paired by seed. Only the source
  set changes.
- **Depth:** 2-op only. 1-op is out of scope: reasoning cells solve it alone.
- **Epoch:** 10 generations, as in the parent. The ideal bound for one source reaches all cells at
  g6 (recompute and report it with the existing reachability code). There is no extension: whatever
  has not arrived by g10 counts as not arrived.
- Everything else as in the parent: sparse examples, memory, feedback, decoding, P=4 for
  Decisions, invariant checks (`assert_encode_logs_rule`, served model and backend recorded).
- J is computed over the 99 non-source cells. Lock = modal share ≥ 0.5 (registered).

## Metrics

- J by generation and epoch mean; J at g10; correct and false lock.
- **Distance profile:** share holding P_e at g10 by distance ring d = 1…5; first holding generation
  by d.
- **First-hold class** (locked before multi-seed close; B1 seed 1 lag −1 prompted the split, not a
  W2 redesign after all seeds): at the generation a non-source first holds P_e, classify
  - **received** — P_e appears in that cell's `inbox_says` in the same generation (wave delivery);
  - **found alone** — P_e is absent from `inbox_says` (local 2-op discovery; cf. Bs J ≈ 0.25 with
    channel off). Report counts and lag for both; never pool them for the wave speed claim.
  - Caveat (one line in the close report): **received is conservative** — a cell that finds P_e
    alone *after* it already sits in the inbox is still labelled received, so wave speed can look
    slightly optimistic; it does not change the W2 claim.
- **Lag vs bound:** first holding generation minus the bound's earliest generation for that cell.
  **Primary lag for W2 = median over received first-holds only.** All-cell lag is descriptive
  (solo finds pull the median negative and mask wave speed).
- **Front exposure:** for each switch to P_e, the number of P_e neighbours at that moment.
  Expected mostly 1 on a long chain.
- Paired contrasts against the four-source arms on the same seeds, with a cluster bootstrap by seed.

## Predictions (lock)

- **W1 (primary):** B1 J at g10 ≥ 0.80, and correct lock in ≥ 4/5 seeds. The wave of reasoning
  cells carries the rule five hops with one source.
- **W2:** B1 median lag vs the one-source bound ≤ 1 generation, **among received first-holds only**
  (amendment locked before full close; see Metrics).
- **W3:** Ca1 J at g10 ≤ 0.10, below Ca with four sources at g10 (0.25). Its share holding P_e
  falls with distance (d = 1 > d = 5).
- **W4:** Da1 J at g10 ≥ 0.60. The external check carries the wave, but more slowly than B1.
- **W5 (descriptive):** front exposure is 1 P_e neighbour in ≥ 60% of B1 switches.

## Readout

- W1 + W3 PASS → the chain needs agents that can verify. Reasoning cells pass the rule on one by
  one, while crowd-following cells stall at the front, where they never see a crowd.
- W1 FAIL with B1 lag growing with distance → reasoning cells also need several confirmations. Read
  this with Part 0: if stratified B also rises with votes, this is "votes matter", not a ceiling of
  the epoch. **Also read lineage:** negative lag among *received* cells means a neighbour found
  P_e alone and re-seeded the grid — effective chain length ≪ 5; high J can be multi-source, not a
  five-hop wave from cell 0. W1’s formal verdict (J + lock) is unchanged; interpretation uses the
  descriptive lineage block below.
- W3 FAIL (Ca1 spreads) → one-pass cells copy more than the dose–response suggested; check what
  they adopt (P_e or a false rule).

### Descriptive — P_e origin / lineage (no new runs; all arms)

Locked before full close (B1 seed 2 received lag −1). Does not change W1–W5 thresholds.

For each cell that ever holds P_e, at first hold:
- **origin:** `source` (seeded cell), `solo` (P_e ∉ inbox), or `received` (P_e ∈ inbox).
- **lineage** for `received`: inherit from Moore neighbours that held P_e in the previous
  generation — `source-lineage` / `solo-lineage` / `mixed` if both lines are present among those
  neighbours. Solo finds are `solo-lineage`; the seeded cell is `source-lineage`.

Report (primary interest **B1**; same block for Ca1/Da1 — nearly all should be source-lineage
because Cas 2-op ≈ 0):
- share of `received` cells that are `source-lineage` only; distance profile of that share;
- **J_source_lineage at g10** = (non-source cells holding P_e at g10 with `source-lineage`) / 99.
  This is the descriptive answer to “did the wave from one source travel five hops.”

## Cost and schedule

Three arms × 5 seeds × 10 generations, the same call pattern as the parent arms. Cap at $40;
report the actual cost. Runs in parallel with the GPU grid.

## Artifacts

- `runs/life_long_chain/{B1,Ca1,Da1}/seed{n}/`
- `runs/life_long_chain/summary.json` (W1–W5, distance profiles, paired contrasts with the
  four-source arms)
- `runs/life_long_chain/reachability_bound_1src.json`
- `runs/life_long_chain/fig_wave.png`: J(g) per arm with the one-source bound, plus share holding
  P_e by distance at g10
- Part 0: `runs/life_reasoning_cells/spread_diag_stratified.json`

## Constraints

Placement only: no training on outputs, no reasoning text requested or stored. Commit this file
before the first call. Amendments before numbers.
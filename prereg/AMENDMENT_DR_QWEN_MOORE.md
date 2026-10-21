# Amendment — Qwen Stage 1: predictions for the moore (lattice) arm

**Status:** locked before any moore call. Local. Not launched with this lock. The pre-lock dry
build passed with live calls refused. Values that were marked **[dry build]** are measured from
existing logs; they were not chosen.
Parents: Qwen Stage 1 task (moore arm specification: world 1, 2 replicates, 20 rounds),
`runs/life_dr_qwen/stage1_readout.md`, `runs/life_dr_tipping/redo/redo_readout.md`,
`AMENDMENT_DR_QWEN_QIT.md`, `DESIGN_AUDIT_CHECKLIST.md`.

## Why

Qwen `all` (world 1) showed two things. The own-example filter is almost perfect (Q2' = 1.00 and 0.97).
Class-B cells flicker off P_e at h_out = 104/637 = 0.163, and their leaves go mostly to rules that fit
their own example and are barely present in the inbox (0–4 of about 70 lines). Luna's class-B leaves
go to the prefix (65 of 66), and Luna's leaving rises with inbox length at equal share (redo: 8 against
88 lines). So two readings of Qwen's leaving compete:

- **Non-social:** leaving does not depend on the inbox; on the lattice (8 lines) h_out stays at its
  `all` level.
- **Social, Luna-like:** leaving scales with inbox length as Luna's does; on the lattice h_out falls by
  Luna's length ratio.

`all` cannot separate them, because every receiver sees nearly the same inbox. The lattice changes the
inbox length from about 70 to 8 and makes it differ across cells.

## Run

As specified in the Stage 1 task and the queue line: world 1, moore topology, 2 replicates, 20 rounds,
the Stage 1 prompt and sampling (temperature 0.6, top_p 0.95, top_k 20, no seed). Runner
`runs/run_life_dr_qwen_moore.py`, histories in `runs/life_dr_qwen/stage1_moore/`.

## Reference values

- h_all = 104/637 = 0.163: Qwen `all` class-B h_out, both replicates pooled.
- r_len = p8 / p88 = (62/160) / (112/160) = 62/112 = 0.5536. Redo D2r, logged signals, shares 0.25
  and 0.375 pooled: 62 of 160 leaves at 8 lines, 112 of 160 at 88 lines.
- h_social = r_len · h_all = (62/112)·(104/637) = 403/4459 = 0.0904: the lattice h_out expected if Qwen's leaving
  scales with length as Luna's does. This carries Luna's ratio, measured on class-A holders at shares
  0.25 and 0.375, over to Qwen class B. It is a reference point, not a fitted value. On the lattice
  the local P_e share of a class-B holder can also be higher than in `all`. Under the social reading
  that lowers h_out further, so h_social is an upper value for that reading.
- ε = Qwen `all` error count on Q2' over both replicates: 3 of 200 cell-states. ε_up = 0.04317, its
  Wilson 95% upper bound (z = 1.959963984540054).

## Predictions (locked)

Unit: the class-B transition, with a cluster bootstrap over the 25 class-B cells (both replicates
pooled inside each cell, 2000 draws, `numpy` Generator seed 0), the same procedure as the Stage 1
cell-level section.

- **QM1 (the filter holds on the lattice):** in each replicate, the agreement between "does not hold
  the modal wrong rule at g20" and "own example rules that rule out" is ≥ 1 − q95/100. Here q95 is the
  95th percentile of Binomial(100, ε_up), q95 = 8. Read only if the modal wrong rule at g20 is
  the prefix; otherwise "not the prefix", as in Stage 1.
- **QM2 (leaving is not inbox-driven):** the bootstrap 95% interval of the lattice class-B h_out
  contains h_all = 0.163 and excludes h_social.
- **QM3 (where leaves go):** the share of lattice class-B leaves that move to a rule consistent with the
  cell's own example is greater than the same share on Luna's lattice run in world 1. That share is
  0 of 35: pinned DRc, world 1, both replicates, rounds 2–20 (r1 23, r2 12). Every destination is the
  prefix `shift_symbols(1)`. Test: one-sided Fisher, α = 0.05, with the cell bootstrap beside
  it. If Luna's lattice world-1 run has fewer than 10 class-B leave events, QM3 is reported as "not
  reached".

## Descriptive (not scored)

As already listed in the Stage 1 task: x(g) against Luna DRc world 1; the P(adopt | k_published) curve
against Luna's; independent finds per round; agreement between replicates. In addition:
- class-B h_in and h_out per replicate;
- the two-state identity, implied x against the observed mean x over rounds 10–20;
- h_out by the local P_e share of the holder's inbox (0–8 lines);
- the destination table of class-B leaves.

## Pre-stated readings

- **QM2 passes:** Qwen's leaving does not depend on inbox length. The flicker is a property of the
  cell, not a response to messages, and the lattice keeps the `all` hazard.
- **QM2 fails, interval contains h_social and excludes h_all:** Qwen's leaving scales with the inbox as
  Luna's does. The `all` flicker was then inbox-driven, despite going to rules that are absent from the
  inbox.
- **Contains both, or neither:** undecided at this sample size. The interval is reported, and the
  local-share breakdown is the only reading.
- **QM1 fails:** the filter weakens with short inboxes. The package says Q2' is an `all` result for
  Qwen.
- **QM3 passes:** the two models leave in different directions on the lattice too, not only in `all`.
- **QI-T interaction:** if QI-T finds that temperature explains the flicker, QM2 is read as a statement
  about Qwen at T = 0.6, not about the model.
- **If the design is the cause:** any run-level failure (parse failures, truncations, a replayed round)
  is counted per round. If more than 2% of live calls in any replicate fail to parse, QM1–QM3 are
  reported with that caveat.

## Design audit

1. **Fidelity to live data.** The run uses the Stage 1 builder and the moore topology unchanged. The
   dry gate matched all 100 round-1 prompts to the Stage 0 world-1 cache. Re-run with this lock:
   100 of 100 keys present, 0 live calls. Round 1 is not replayed from the Stage 0 cache.
   `GuardedClient` reads only `runs/life_dr_qwen/cache_stage1_moore_r1` or `r2`. A Stage 0 file, or
   the other replicate's file, increments `sibling_collisions` and is not returned: with that key
   planted as a sibling and live calls refused, the call raised and wrote nothing. The replicate
   index does not enter the cache key. `_disk_key` hashes model, revision, prompt, draw, catalog
   digest, schema, sampling, max_tokens and thinking mode. The draw is
   `inference_seed(world, generation, cell, kind="trajectory", draw=0)`, payload
   `world|generation|cell|kind|draw`. Two builds of round 1 produced the same 100 keys. r1 and r2
   do not share a round-1 state: the keys sit in different directories, both empty at this lock
   (0 of 100), and each replicate makes its own unseeded call. The request body matches the Stage 1
   body field by field (temperature 0.6, top_p 0.95, top_k 20, min_p 0, presence_penalty 0,
   max_tokens 32768, no seed). The POST was not sent.
2. **Coverage.** h_all was measured on class-B holders with about 70-line inboxes. The lattice gives 8
   lines, and that is the manipulation. r_len comes from Luna class A at shares 0.25 and 0.375. Its
   use for Qwen class B is stated as an extrapolation in the reference values, and QM2 compares
   against it only as a reference.
3. **Controls.** The `all` arm of the same model, world, prompt and sampling is the baseline for QM2.
   Luna's lattice run is the baseline for QM3.
4. **Observability.** The cell sees its 8 inbox lines, its one-step memory line and its own example.
   QM2 relies on nothing else. The local-share breakdown uses only what the cell sees.
5. **Gate consistency.** Pre-lock gates, run together with live calls refused: the round-1 prompt match;
   the request body equal to the Stage 1 body field by field; the cache-key and replicate check in
   item 1; every measured value written in. All four passed at this lock. Launch gates, checked by
   the runner at start and not at lock: the lock is free and the server is idle.
6. **Statistical unit.** The transition, with the cluster bootstrap over the 25 class-B cells. The same
   25 cells appear in `all` and in moore, because the examples are fixed by world. The QM2 interval is
   on the lattice h_out alone, against fixed reference values, so the `all` sample's own uncertainty is
   not counted twice. It is quoted beside it.
7. **Pre-stated readings.** Above, including the undecided case, the QI-T interaction and failures in
   the run itself.

## Power

Simulate the QM2 decision under h_out = 0.163 and under h_out = h_social. Assume the lattice gives the
same number of class-B holder opportunities as `all` (637) and the same per-cell spread (resample the
Stage 1 per-cell counts), 2000 simulations each. Record the probability of the correct verdict under
each. If either is below 0.8, the readout says so. The design is not changed after seeing that
number unless this amendment is re-locked.

Each simulation resamples the 25 Stage 1 per-cell opportunity counts with replacement (they sum to
637), draws binomial leaves at the stated rate, then applies the QM2 cluster bootstrap (2000 cell
resamples, 2.5 and 97.5 percentiles). `numpy` Generator seed 0, one generator per rate. Correct under
0.163 means the interval contains 0.163 and excludes h_social = 0.0904. Correct under h_social means
it contains 0.0904 and excludes 0.163. The probabilities are 0.929 and 0.932. Both are above 0.8.
# Amendment — more population runs for the local models (gpt-oss-20b, gpt-oss-120b)

**Status:** locked 2026-10-28. Local, pre-approved. Dry build:
`runs/oss_replicates/dry_build.json` (summary `dry_build.md`). No call before this lock.
Basis:
- `AMENDMENT_CONTAGION.md` (B1, Part C) and its readouts;
- `AMENDMENT_OSS120_PREDICTION.md` (O1–O3), not yet at Stage 2;
- the recheck reports `QX_RECHECK_REPORT.md` and `RECHECK_REPORT_2.md`;
- `DESIGN_AUDIT_CHECKLIST.md`, including items 9–12.

## Why

The micro-to-macro result (B1) rests on two population runs per topology and model. For gpt-oss-20b
that is two lattice runs (0.37, 0.45) and two complete-graph runs (0.85, 0.87). Compute on the local
machine is not a constraint, so the replicate count is the cheapest weakness of the paper to fix.
Qwen is not included: about 42 h per run, and it is not a basis of B1's two-model claim. Its 2 + 2
runs are stated as such.

## Runs

**R-oss20.** gpt-oss-20b, world 1, Moore lattice and `all`, **6 new replicates per topology**
(12 runs, 24,000 calls, about **31.6 h** at 4.740 s/call from the four existing W1-oss20
full-run cache spans / `runs/contagion/gate.json` `wall.oss_seconds_per_call`).
- Configuration identical to the existing W1-oss20 full runs: the panel full-run builder, image,
  model revision, decoding, context 40,960, and the default chat template with its live date. The
  rendered date of every run is recorded. The configuration is fixed now, before the date-pair
  readout exists, and is not changed after it. If the date pair shows a difference, it is reported
  beside these runs as a limitation.
- Fresh, empty cache per run, with arm and replicate id in the path. Replicates alternate
  (lattice r3, `all` r3, lattice r4, …) under one waiter, so drift over time is shared.
- The sampler gate on this server uses a non-degenerate prompt (checklist item 12), and its result is
  in the readout. **Named before any R-oss20 call:** W1-oss20 full-run `all` round-1 cell **0**
  (prompt sha256 `0fcd2042…`); prior across the two existing replicates: top share **0.5**
  (`reverse;shift_symbols(3)` : 1, `shift_symbols(1);swap(2,3)` [= P_e] : 1). Cap **64+64**.
  (Part A named fallback `n88-k66-m22-adopt` cell 2, top share 0.625, remains available if the
  full-run prompt cannot be rebuilt.)

**R-oss120.** In `AMENDMENT_OSS120_PREDICTION.md`, Stage 2 becomes **4 replicates per topology**
instead of 2 (16,000 calls, wall **~51.9 h** at the locked 11.667 s/call). This changes no Stage-1
input and is locked before the prediction record exists. O1 is then the sign of the mean over 4
runs per topology; O2 requires each of the 4 runs per topology within the simulated 5–95 % band.
Everything else in that amendment is unchanged. Dated pre-record line in that file, same commit.

## Predictions (locked)

Unit: the run. Only the new runs are scored. The existing two runs per topology are reported beside
them and not pooled into any test.

- **R1 (gpt-oss-20b ranking replicates):** the 6 new `all` runs have a higher mean x(10–20) than the 6
  new lattice runs. One-sided exact permutation test on 6 against 6 (924 splits), α = 0.05.
- **R2 (sign in every pair, descriptive):** the share of the 36 (lattice, `all`) pairs of new runs in
  which `all` is higher. Not scored.
- **R3 (simulator band):** the share of new runs inside the simulated 5–95 % band of their topology,
  using the committed simulator at **2,000 replicates, seed 0**, with Monte Carlo SE. Not scored; it
  shows whether the band describes run-to-run spread.

Power for R1 (dry build, `runs/oss_replicates/dry_build.json`):
- **Simulator** (2,000 draws per topology from committed Part B / `contagion_sim.run_lagged`,
  seed 0; then 2,000 Monte Carlo 6-vs-6 tests): power **0.974** (MC SE **0.0036**). Bands
  mean x(10–20): lattice 5–95% [0.314, 0.535]; all [0.418, 0.876].
- **Normal model** with observed means and within-topology SD of the existing runs
  (lattice 0.374, 0.445 → SD 0.050; all 0.850, 0.871 → SD 0.015): power **1.000**.

## Pre-stated readings

- **R1 holds:** the gpt-oss-20b topology ranking replicates in new runs; the paper reports 8 runs per
  topology with the new 6 as the test.
- **R1 fails:** the ranking seen in the first two runs per topology does not replicate. B1 for
  gpt-oss-20b is restated as not supported, and the paper says so.
- **R3 low (most runs outside the band):** the simulator's run-to-run spread is too narrow; level
  claims stay withdrawn, and the ranking claim rests on R1 alone.
- **If the design is the cause:** the live-date template differs in rendered date across runs; the
  date is recorded and checked against the date-pair readout.

## Gates (live calls refused unless stated)

- Prompt identity at rounds 1 and 11 against the existing W1-oss20 runs, byte for byte except the
  rendered date line. **Dry build:** match on both topologies (100/100 cells); user prompts have no
  date; only Harmony `Current date:` via `strftime_now` can differ by calendar day
  (`dry_build.json` → `prompt_identity`).
- Context: I_max + `max_tokens` ≤ 40,960 for the gpt-oss tokenizer on the full-run prompt set.
  **Dry build:** I_max **4189** + 32768 = **36957** ≤ 40960 (fits).
- Fresh, distinct cache paths; a runner that refuses an existing cache.
- The sampler gate (live), non-degenerate prompt named with its prior distribution (above).

## Design audit

1. **Fidelity.** Same builder and configuration as the existing W1-oss20 runs; only the chat-template
   date line can differ. Dry-build prompt identity at rounds 1 and 11: match.
2. **Coverage.** World 1, both topologies. Part C covers worlds 3 and 5.
3. **Controls.** The two topologies alternate under one waiter.
4. **Observability.** Cells see their prompts only.
5. **Gate consistency.** Prompt identity, I_max, sampler-gate prior, and R1 power all filled on the
   dry build before lock (`runs/oss_replicates/dry_build.json`). Checklist items 8–12: live date
   recorded (item 8); recheck package after readout (item 9); simulator bands at 2,000 reps
   (item 10); I_max fits (item 11); gate prior top share 0.5 ≤ 0.8, cap 64+64 (item 12).
6. **Statistical unit.** The run; 6 against 6 for R1, power stated.
7. **Pre-stated readings.** Above.
8. **Recheck.** A recheck package per checklist item 9 follows the readout.

## Queue

After 120b Stage 1 and its prediction record: 120b Stage 2 (**4 + 4**), then R-oss20 (12 runs), then
Part C. About **4.4 days** of GPU in total (Stage 2 ~51.9 h + R-oss20 ~31.6 h + Part C ~21.1 h).
Order changes are logged in `RESEARCH_ROADMAP.md`.

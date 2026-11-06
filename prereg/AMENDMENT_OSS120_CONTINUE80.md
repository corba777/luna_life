# Amendment — gpt-oss-120b Stage 2 runs continued from round 40 to round 80

**Status:** locked 2026-11-05 (Artem: "Dry build checked; lock"). Dry build
`runs/oss120/continue80/dry_check.json`, all gates passed. Local, pre-approved (Artem, 2026-11-03).
No call before the waiter's go. Basis: `AMENDMENT_OSS120_EXTEND40.md`
(E1–E3, scored), the Stage 2 runs and their recheck (`PAPER_LIFE_CHANGELOG.md`, 2026-11-02), the
prediction record (`6a0561cb…`) and its `sim_inputs.json`.

## Why

By round 40 every gpt-oss-120b lattice run was still rising (x(40) = 0.67, 0.53, 0.81, 0.96) and P_e
clusters were merging. The record's simulator was too fast because it held every witness on P_e
from round 2; in the runs, witnesses took P_e up gradually. The question is now direct: do these
populations, left to run, converge on the true rule on the lattice and not on the complete graph?

The same eight populations are continued, so the test is about their own future, from their own
round-40 state.

## Runs

- The eight Stage 2 runs (lattice r1–r4, `all` r1–r4), rounds 41–80, 32,000 calls, about
  **90–100 h (≈ 4 days)**. Stage 2 took 85.3 h for its 32,000 calls (9.6 s per call), but round
  walls grew within every run (mean ≈ 890 s in rounds 2–10, ≈ 1,010 s in rounds 31–40; slope
  1.6–7.3 s per round, steepest in `all`). Projection for rounds 41–80, summed over the eight runs:
  85 h at each run's Stage 2 mean, 89 h at its rounds 31–40 rate, 97 h on its linear trend. Plus
  about 45 s per run for the restore (below) and one server start with the sampler gate.
  Source: `runs/run_oss120_continue80.py hours` (end of round t = latest cache-file time of round
  t's records).
- Same server, image, revision, context, pinned date template, request body
  (`reasoning_effort: "medium"`) and builder as in Stage 2; EPOCH_LENGTH pinned to **81** in all three
  places it is read (engine, v1a constants, `slots_for`), set after the build as in Stage 2, asserted
  before every round, with a test (`runs/test_oss120_continue80_pins.py`, 7/7).
- Order alternates as in Stage 2. Fresh cache per continued run; no resume; final text, finish
  reason and launch fields stored per call; per-round cell states.
- Health during the continuation: counts only, as in Stage 2 (calls, empty texts, retries,
  truncations, tokenize mismatches per run); no x or other outcome is looked at before the end.

**How a run is restored.** The engine is deterministic given the answers: board, delivery, query,
catalog order and inference seeds all come from seeded RNGs keyed by world, generation and cell.
A run's round-40 state is rebuilt by replaying rounds 1–40 through the Stage 2 builder (EPOCH_LENGTH
81), every answer served from that run's own Stage 2 cache under the Stage 2 cache key; a cache miss
aborts, and no call is made in rounds 1–40. The replayed cell states, records and rule history must
equal the stored ones before round 41 is played (gate 2, repeated at the start of every live run;
written to `restore.json`). From round 41 the same client sends each prompt to the server and
writes a fresh cache. Runner: `runs/run_oss120_continue80.py`.

## Gates (live calls refused unless stated)

Dry build: `runs/oss120/continue80/dry_check.json` (CPU, no server, no live call).

1. **Continuation identity (CPU, stub) — passed.** Stub answers are a function of the prompt's
   sha256 (≈ 1 % unparseable, so the retry path runs). For each topology, three arms in separate
   interpreters: (a) the Stage 2 runner itself, 40 rounds at EPOCH_LENGTH 41, writing a cache;
   (b) 45 rounds without a break at 81; (c) a fresh process that restores (a) by replay and plays
   rounds 41–45 through the live path. Prompts of rounds 41–45 are byte-identical between (b) and
   (c) (every cell and draw, retries included); the full engine and completer state (rules, memory
   lines, board and published messages, rule history, inbox log, held rules and publication bits,
   call counts; 6.6 / 23 MB as canonical JSON for lattice / `all`) is byte-identical at round 40
   and at round 45; cell states of rounds 1–40 at 81 equal those of (a) at 41; the replay used every
   cache entry of (a) (4,051 / 4,053). Limitation: stub populations stay near x = 0, so P_e-holding
   states are exercised by gate 2, not here.
2. **Restored round 40 equals the stored round 40 — passed, all 8 runs.** Replay of rounds 1–40
   reproduces `cell_states.jsonl` for every round 1–40 (not only round 40), `records.jsonl` (apart
   from the cache-hit flag) and the rule history, and uses each run's 4,000 cache entries, all of
   them (≈ 45 s per run). Round 41 then renders 100 prompts per run, one per cell, header "Epoch 0,
   generation 41 of this epoch.", one template per topology (the gate-3 template); largest real
   round-41 prompt 1,921 tokens (lattice) and 3,934 (`all`), pinned template, 120b tokenizer.
   Repeated at the start of every live run before its first call.
3. **Horizon — passed.** A stub run of rounds 1–80 at EPOCH_LENGTH 81, per topology: rounds 1–40
   byte-identical to the Stage 2 build; one template across rounds 1–80; every header "Epoch 0,
   generation t"; examples and catalog entries constant; world 1, epoch 0 through round 80; no
   horizon word in the template (20, 21, 40, 41, 80, 81, epoch length, round(s), remaining, left,
   final, horizon, total, out of, end(s), until); rounds 41, 42 and 80 differ from round 40 only in
   round state (header, query, previous step, visible messages, catalog order).
4. Item 14–18 checks and the sampler gate at server start, as in Stage 2. **I_max = 4,189 tokens**
   (`panel_full_context.worst_prompts`: every other cell publishing the longest catalog rule, `all`
   render, at each round 41–80; range 4,188–4,189, the same as Stage 2's round-20 value) + 32,768
   max_tokens = 36,957 ≤ 40,960 (headroom 4,003).
5. **GPU exclusivity.** Strict precheck before the first call: manifest of this dry build matches
   the logged one, no GPU compute process, jev-sglang down until the runner starts its own, and
   open-webui not running. A continuous exclusivity monitor (`runs/monitor_gpu_exclusive.py`,
   every 5 s) starts before the waiter and runs from the waiter's start to its done or dead file:
   any GPU compute process that is neither the waiter's descendant nor jev-sglang is logged
   FOREIGN, and open-webui running at any sample is logged VIOLATION. open-webui stays off for the
   whole run. The monitor logs only and never stops a run (no resume exists); any FOREIGN or
   VIOLATION sample is reported in the readout with the rounds it overlaps.
   **Request count, per run.** The runner counts every POST attempt it sends (retries included)
   and stores it with the run's live window (UTC start and end of rounds 41–80) in `run.ok`. The
   readout counts the chat-completions POSTs in the server's access log inside each window (± 2 s;
   uvicorn logs a request at completion) and compares the two; any excess is reported as foreign
   requests for that run. Checked on Stage 2 (cache-file times as windows): 4,000 server POSTs =
   4,000 client calls in every run, 0 foreign; the other 128 POSTs fall before the first run.

## Model used for the predictions

The record's simulator, with one change: witnesses are no longer held on P_e. Each witness moves
onto P_e with hazard h_in and off it with hazard h_out per round (Proposition 4b), measured in the
Stage 2 runs over rounds 2–40, by topology: lattice h_in = 128/552 = 0.232, h_out = 77/3,348 =
0.023; `all` h_in = 148/395 = 0.375, h_out = 109/3,505 = 0.031. Class A uses the record's fits and
publication. Each continued run is simulated from its own stored round-40 state (holdings and
publication bits), 2,000 replicates, seed 0, with MC SE.

Note: the hazards are measured on rounds 2–40 of the same runs; the predictions concern rounds 41–80,
which no input has seen.

Code: `runs/sim_oss120_continue80.py` (imports the update and the fits of the committed
`runs/sim_oss120_extend40.py`; recomputes the witness counts from the stored cell states and aborts
unless they equal the ones above; numpy `default_rng(0)` per run; per round the class A uniforms,
then the witness uniforms, then the publication uniforms). Output `runs/oss120/continue80_sim.json`
(sha256 `0c02948b…`). Window x(70–80): mean over rounds 70–80 inclusive of the share of 100 cells
holding P_e. MC SE of a median by 1,000 bootstrap resamples of the replicates.

| run | x(40) | witnesses on P_e at 40 (of 25) | median x(70–80) [p05, p95] | P(x(70–80) ≥ 0.8) | P(x(70–80) < 0.5) |
|---|---:|---:|---|---:|---:|
| lattice r1 | 0.67 | 25 | 0.93 [0.85, 0.96] | 0.984 ± 0.003 | 0.0005 ± 0.0005 |
| lattice r2 | 0.53 | 24 | 0.93 [0.75, 0.96] | 0.9275 ± 0.006 | 0.010 ± 0.002 |
| lattice r3 | 0.81 | 24 | 0.93 [0.86, 0.96] | 0.991 ± 0.002 | 0 |
| lattice r4 | 0.96 | 25 | 0.93 [0.87, 0.96] | 0.991 ± 0.002 | 0 |
| `all` r1 | 0.24 | 23 | 0.31 [0.27, 0.36] | 0.0055 ± 0.002 | 0.992 ± 0.002 |
| `all` r2 | 0.36 | 24 | 0.31 [0.27, 0.37] | 0.012 ± 0.002 | 0.986 ± 0.003 |
| `all` r3 | 0.92 | 24 | 0.95 [0.93, 0.97] | 1.000 | 0 |
| `all` r4 | 0.52 | 25 | 0.93 [0.28, 0.97], bimodal (mean 0.64; median MC SE 0.12) | 0.517 ± 0.011 | 0.481 ± 0.011 |

MC SE of every lattice and `all` r1–r3 median ≤ 0.001. Artem's independent simulation (4,000
replicates) agreed run by run within 0.02 (medians and P(≥ 0.8)) and gave K1 ≈ 0.998, K2 ≈ 0.988; the scored values
below are the committed simulator's.

## Predictions (locked)

Unit: the run.

- **K1 (lattice converges):** at least 3 of the 4 lattice runs have x(70–80) ≥ 0.8. Predicted
  probability **0.997 ± 0.0004** (Poisson-binomial over the four per-run P(≥ 0.8); MC SE by the
  delta method).
- **K2 (stuck `all` runs stay stuck):** `all` r1 and r2 both have x(70–80) < 0.5. Predicted
  probability **0.978 ± 0.003** (product of the two per-run P(< 0.5); delta method).
- **K3 (ranking, late):** mean x(70–80) of the 4 lattice runs exceeds that of the 4 `all` runs.
  Scored by sign; exact permutation p beside it (smallest possible one-sided p with 4 + 4 runs:
  1/70 = 0.014). Simulated probability 0.998 (replicate i of each run forms a quartet; descriptive).
- **K4 (descriptive):** per run, x(80), the round at which x first reaches 0.9, P_e Moore components
  and largest cluster at rounds 40, 50, 60, 70, 80, the witness share per round, and `all` r4 (the
  model gives it even odds) and `all` r3 (predicted to stay converged).

## Pre-stated readings

- **K1 and K2 hold:** the lattice populations converge on the true rule that 75 % of their cells
  cannot tell from a false one, while the complete-graph populations that had frozen stay frozen.
  The response functions plus measured witness uptake predict the long-run outcome run by run.
- **K1 fails (lattice stalls below 0.8):** something slows the lattice beyond the model, for
  example class-A cells next to P_e clusters adopting less than the battery says; reported with the
  per-round adoption hazard by inbox.
- **K2 fails (a frozen `all` run tips):** the complete graph can escape the witness plateau late;
  the bistability is not settled by round 40.

## Design audit

1. **Fidelity.** Same populations and configuration; only the horizon is longer (gates 1–3).
2. **Coverage.** gpt-oss-120b only.
3. **Controls.** `all` runs continued equally.
4. **Observability.** Cells see their prompts only.
5. **Gate consistency.** All gates before the first call.
6. **Statistical unit.** The run; per-run predictions from the run's own state.
7. **Pre-stated readings.** Above.
8. **Recheck.** Package as for Stage 2; I recompute x, clusters and the scores from the cell states
   and the stored text.

## Queue

After Part C (verdicts final 2026-11-05) and the Thinking probe (v20u, done 2026-11-05); the
continuation is the next GPU job. While it runs, only CPU work beside it: the dry build of
`AMENDMENT_WITNESS_DIRECTION.md`; its GPU steps (Stage 1a, timed HF probe) run after the
continuation. Thinking response training is deferred to the end of the queue. The waiter is a new file armed only after
this amendment is committed as locked: steps `wait_gpu_free` → `wait_go_continue80` (Artem's go,
logged with his words) → strict precheck (gate 5) → server start and sampler gate → the eight runs
in Stage 2 order → automatic CPU readout export. Exclusivity monitor and watcher v3
(`--manual-steps wait_go_continue80`) start before the waiter.
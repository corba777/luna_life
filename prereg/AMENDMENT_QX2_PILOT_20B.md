# AMENDMENT — QX-2 phase 2: pilot on gpt-oss-20b

**Status:** locked 2026-11-14 (Artem's review of the full text and the B = 1 / B = 4 prompts; §1 cap and
§6 test descriptives added at his request before the lock). No call before Artem's go is logged. Phase 1, which this pilot uses unchanged:
`AMENDMENT_QX2_PHASE1.md` (locked). Plan: `QX2_PLAN.md`.

**Purpose.** Check the mechanics and the outcome definitions on a cheap local model, and measure prompt
and answer lengths and time per call. **No hypothesis is tested.** Pilot numbers are descriptive.

- The main-phase predictions take their thresholds from the locked scripted references, not from the
  pilot.
- After the pilot, only mechanics may change (format, prompt defects, engine bugs), each by a new
  amendment before the grid.

## 1. Arms

The world, catalog, prompt, schema, mapper, protocol and lattice are exactly as locked in phase 1
(world seed 0, G = 12). A replicate is an independent sampling run on the same world.

| arm (runner name) | δ | B | replicates | calls |
|---|---|---:|---:|---:|
| population, lattice (`pop_d8_B1_r1`, `pop_d8_B1_r2`) | 1/8 | 1 | 2 | 2,400 |
| population, lattice (`pop_d8_B4_r1`, `pop_d8_B4_r2`) | 1/8 | 4 | 2 | 2,400 |
| population, lattice (`pop_d64_B4_r1`) | 1/64 | 4 | 1 | 1,200 |
| no-test control (`control_B0_r1`) | — | 0 | 1 | 1,200 |
| single agent, pooled (100·B tests, ≤ 9 / 34 per call) | 1/8 | 1, 4 | 2 | 48 |
| single agent, cell (B tests, ≤ 1 per call) | 1/8 | 1, 4 | 2 | 48 |
| **total** | | | | **7,296** (+ retries) |

**Pooled single-agent cap (locked phase-1 rule).** The pooled agent has 100·B tests, at most
⌈100·B/12⌉ = 9 (B = 1) or 34 (B = 4) per call, and none in generation 12 (`AMENDMENT_QX2_PHASE1.md`,
§2, "Single-agent baselines"). Tests can therefore be used only in generations 1–11: at most 11 × 9 =
99 of 100 (B = 1) and 11 × 34 = 374 of 400 (B = 4). The locked simulator applies the same cap
(`qx2_sim.simulate_single`, per = ⌈N·B/G⌉ through `qx2_world.single_max_tests`, no test when g = G),
and so do the pilot runner and the prompt ("at most {per} per generation"; the `tests` array has
`maxItems` = min(per, tests left), and no `tests` field in generation 12). The prompt still states the
nominal total ("You have 100 tests for the whole run"). The cell baseline (B tests, at most one per
call, generations 1–11) is not capped below B.

**Decisions (Artem, 2026-11-13):**

- **δ.** δ = 1/8 for the arms as drafted: a refutation arrives in every run, so sharing, relay and
  overturn are exercised.
- **One population run at δ = 1/64 with B = 4.** It checks the mechanics in the main cell and measures
  lengths in the Luna setting. With 400 tests a refutation is near certain (scripted random:
  P = 0.999 by generation 12). The Luna re-estimate (§5) uses this run's lengths.
- **One control replicate.**

**Run order.** `pop_d8_B1_r1`, `pop_d8_B4_r1`, `pop_d64_B4_r1`, `pop_d8_B1_r2`, `pop_d8_B4_r2`,
`control_B0_r1`, then the eight single-agent runs. The format gate (§4) falls in the first run.

## 2. Model, engine, sampling

- **Model.** gpt-oss-20b, revision `6cee5e81ee83917806bbde320786a8fb61efebee`.
- **Engine.** SGLang image `sha256:223b675fee9e…` (v0.5.18, the QX-1 / QX-1p image), launched with the
  wave-1 `W1-oss20` spec:
  - `mem` 0.70;
  - parser `gpt-oss`;
  - context 36,864.
- **Server lifecycle.** One fresh server for the whole pilot, stopped at `.ok` or `.aborted`. The
  launch time and full `server_args` are recorded in the run log.
- **Sampling.** As `W1-oss20`:
  - temperature 1.0, top_p 1.0;
  - `reasoning_effort` medium;
  - `max_tokens` 32,768;
  - strict `json_schema` per call (phase-1 schema);
  - no seed in the request.
- **Concurrency.** 16.
- **Generation-synchronous.** All 100 cell calls of generation g finish (with their retries) before
  results, messages and memory for g + 1 are built.
- **Cache key.** sha256 over (arm, replicate, generation, cell, draw, prompt).
  - On resume, cached answers are reused. Nothing is re-asked.
  - The cache is never keyed by cell id alone.
- **Retry and fallback.** As locked:
  1. one re-sample (draw + 1) of the same prompt;
  2. then keep the previous rule, no test, no publish.
- **Engine invariants (asserted on every call; a violation stops the run):**
  - every published result's input is in the sender's memory, and its output equals $H_T$ of that
    input;
  - no test is requested in generation 12 or beyond the budget;
  - every message slot shows only neighbours;
  - test results reach only the requester.

## 3. Dry check of the runner (CPU, before lock; no model call)

`python runs/run_qx2_pilot20b.py dry --reps 200 --write runs/qx2_pilot20b/dry_check.json`

1. **Scripted model through the real engine.**
   - A stub "model" answers from the random and adopt_shared policies. Every call goes through the
     runner's prompt renderer, per-cell schema, mapper, retry and engine. Every stub answer must
     validate against that call's schema.
   - Population runs: δ ∈ {1/8, 1/64} × B ∈ {1, 4} × {random, adopt_shared}, 200 replicates each.
   - Single agent: pooled and cell, the same δ and B, random, 400 replicates each.
   - Abandonment and recovery must match the locked `sim_reference.json` rows within ±3 SE of the
     difference.
   - SE: the replicate is the unit on both sides (one population run, or one single-agent run). The
     locked simulator rows are re-run with their reference seeds to get per-replicate values; their
     means must equal `sim_reference.json` (check). Variance = the pooled per-replicate variance of the
     engine and simulator samples, × (1/n_engine + 1/n_sim). Only if both samples are constant is it
     the Bhatia–Davis bound m(1 − m) at the **simulator's** mean m; this is 0 when m ∈ {0, 1}, and then
     any difference fails.
   - This tests the engine against the simulator.
2. **Retries.**
   - An injected invalid first answer is resolved on the re-sample (2 calls).
   - An injected invalid pair falls back: previous rule, no test, no publish.
   - A valid first answer makes 1 call.
   - The single-agent fallback requests no tests.
3. **Invariants fire** on a corrupted state:
   - a shared input not in memory;
   - a shared output that is not $H_T$;
   - a test in generation 12.
4. **Schema validation.** The validator rejects a test field in generation 12 and a result input
   outside memory.
5. **Prompt identity.** For each B ∈ {1, 4}, the generation-1 prompt the runner renders for cell 37 is
   byte-identical to the locked phase-1 sample for that B (`runs/qx2/prompts/gen1_B1.txt`,
   `gen1_B4.txt`). The B = 1 and B = 4 prompts differ from each other in exactly three lines: the
   budget sentence ("You have 1 test" / "You have 4 tests for the whole run, …"), the results header
   ("0 of 1 test used" / "0 of 4 tests used") and "Tests left: 1." / "Tests left: 4.".
6. **Luna arithmetic.** The estimate on synthetic usage equals the hand formula.
7. **Lock inputs.** The phase-1 dry-build sha256 and the world digest match the phase-1 lock.

Before the GPU step, the waiter logs the manifest sha256 (the runner, phase-1 code and `runs/qx2/`
outputs).

## 4. Gates (during the run)

- **Format.** A stop is triggered if, in the first 400 cell decisions (each with its retry):
  - more than 4 end in fallback (invalid after the retry), or
  - more than 4 are truncated.
  
  The stored basis is 0 invalid and 0 truncated in 480 QX-1p 20b calls on a 101-rule catalog prompt.
- **Invariants.** Any engine-invariant violation (§2) stops the run.
- **Length.** If any prompt exceeds 30,000 tokens, the run stops. The expected maximum is about
  3,500.
- On a stop: `.aborted` with the reason. Nothing is re-run without a new amendment line and Artem's go.

## 5. Luna re-estimate and budget rule (Artem, 2026-11-13)

**CPU step, automatic after the pilot readout.**

- **Scope priced.** δ = 1/64 with B = 1 and B = 4, one replicate each: 2,400 cell calls, + the pilot's
  measured retry rate. This is the only Luna scope allowed in QX-2.
- **Inputs.** All from the **δ = 1/64, B = 4 run** (`pop_d64_B4_r1`), Artem 2026-11-13:
  - its measured prompt tokens, with a ×1.10 tokenizer margin, since they are 20b token counts;
  - its completion tokens: the mean, and the 95th percentile as the upper case;
  - its retry rate.
  - QX-1p Luna medium unit costs: the cached fixed prefix (14,764 tokens at $0.01/M) and the output
    rate ($0.50/M), with the per-cell prompt billed at the cache-write rate ($0.125/M), because the
    catalog order is shuffled.
- **Rule.**
  - A Luna call in QX-2 is allowed **only if the upper-case estimate is at most $5 in total**, and
    never above the $13.20 left in the $100 envelope.
  - **And only with Artem's explicit go** (Artem, 2026-11-14), logged in the switch log with his
    words. Meeting the cost rule alone never starts or arms a Luna call.
  - Otherwise there is no Luna arm in QX-2.
- **Output.** The estimate is written to `runs/qx2_pilot20b/luna_estimate.json` and logged as
  `MILESTONE: QX-2 Luna estimate $… (rule: ≤ $5) → eligible / not eligible`.
- **A pass does not start Luna.** A Luna arm needs its own amendment and Artem's go.
- **The full grid runs on local models only** (20b, then Qwen3-4B-Thinking).

## 6. Readout (descriptive)

**Per arm and replicate:**

- abandonment and recovery, beside the locked scripted references for the same δ and B;
- first refutation;
- final-rule accuracy on all inputs and on δ-inputs;
- test quality;
- tests (Artem, 2026-11-14), per arm and replicate, pooled over cells and generations (readout table
  and `readout.json`):
  - pattern: the literal strings AAAA and ABCD vs any other input; beside it, the shape (all four letters
    equal / all distinct / neither);
  - share of tests on δ-inputs (= test quality; single-agent arms included);
  - Hamming distance (0–4) from each test to the nearest input among the testing cell's own two
    examples (cell 0's examples for the single agent), as counts and mean;
- how the test field is constrained: in the population schema, `test` is
  `anyOf [string, pattern ^[A-H]{4}$; null]`, required and present only while the cell can test (tests
  left and g < 12); in the single-agent schema, `tests` is an array of strings with pattern
  `^[A-H]{4}$` and `maxItems` = min(per, tests left), absent in generation 12. No enum and no order:
  any of the 4,096 inputs is allowed. (The only input enum in the schema is for a shared result: the
  cell's memory, sorted.);
- overturn within k = 2 and explained away;
- message mix: silence, rule, own result, relayed result;
- the share of shared results that refute $H_F$;
- fallback and truncation rates.

**Cost and time:**

- prompt, completion and reasoning tokens per generation;
- seconds per call and GPU hours.

**For the main phase:**

- whether the mechanics worked (tests requested, results shared and relayed);
- any defect found.

No contrast, no p-value. The recheck package is in the usual format: prompts, raw answers, state per
generation, world, code and hashes. Reasoning text is stored in the package but not printed in any
summary.

## 7. Time and queue

- **Time.** 7,296 calls + about 5 % retries, at 3.6 s per call (range 3.2–4.8 s, from QX-1p 20b
  scaled to QX-2 prompt length). That is about **7.7 h** (6.8–10.2 h).
- **Queue.** A new waiter after the 120b signal intervention:
  1. `wait_signal_intervention_120b_done`
  2. `wait_go_qx2_pilot20b` (go file plus a switch-log line with Artem's words)
  3. `wait_precheck` (manifest sha)
  4. the population and control arms, then the single-agent arms
  5. readout
  6. `luna_estimate` (CPU, automatic)
  7. package
  8. done
- Watcher v3, with the go step listed as manual. GPU monitor beside it.
- **ETA.** The 120b intervention is expected to finish around Saturday 23:00–00:30. The pilot would
  then end around Sunday 07:00–11:00.

## 8. Runner and dry check (hashes)

| File | sha256 |
|---|---|
| `runs/run_qx2_pilot20b.py` | `52d44f20661e778d99483a62fa167fd84faca25430e4e08fe03a6b4063090878` |
| `runs/qx2_pilot20b/dry_check.json` | `ff47f7f7c6436812e9ee0f6517ee778bdd61527b09c810bece896598aad36e02` |
| `runs/qx2_world.py` (phase 1, locked) | `ebe9982f82b11c7a90d8229d05f2e49f7855d41c81c27743b943039f508075b9` |
| `runs/qx2_sim.py` (phase 1, locked) | `89645df1f25ba7ed6255e483ae75e56d2447fab136e4cd4cf18901af8f29449a` |
| `runs/qx2_dry_build.py` (phase 1, locked) | `ff71204c3d6d1ab0ee3c368715a2874d4b3df5053636b2e44d778d8564fa8133` |
| `runs/qx2/dry_build.json` (phase 1, locked) | `981d340555267e64a580823b50cb6ef6250c2c27a607abd76a35f3e9a18ed50d` |
| `runs/qx2/sim_reference.json` (phase 1, locked) | `8289693c7a8929acd18e94a2b9753f804cc3073d6fab18da5a2a48278ee67e9a` |
| `AMENDMENT_QX2_PHASE1.md` (locked) | `b95f47ab697d1618449baa9ee207d06824d4bff1abf1f32101cc61aa71032364` |

**Dry check result (2026-11-14, CPU only, 0 model calls, 127 s):** pass. 200 population replicates per
(δ, B, agent), 400 single-agent replicates per (baseline, δ, B); simulator 1,000 / 2,000 replicates per
row, as locked. All 15 checks pass, including "simulator per-replicate values reproduce
`sim_reference.json`". Engine vs simulator, 16 rows × 2 outcomes, replicate-unit SE: max |z| = 0.90.
Pooled replicate variance in 26 of 32 comparisons; Bhatia–Davis in 6 where both samples are constant
and equal (z = 0). Main-cell rows (δ = 1/64, B = 4): adopt_shared abandonment 1.000 vs 0.998 (SE
0.0032, z 0.63), recovery 0.611 vs 0.610; random abandonment 0.062 vs 0.061. Luna estimate arithmetic on
synthetic usage: $2.45 central / $3.58 upper (synthetic numbers, not a forecast).

The 15th check is new: the test descriptives of §6 on a hand case (AAAA, ABCD, one of cell 0's
example inputs, and that input shifted by four letters) and on a stub single-agent run.

**Third full run kept as history** (`runs/qx2_pilot20b/dry_check_r3_pre_testdesc.json`, sha256
`2f8ae07e…63f4`, runner `968589a6…a7df`; pass, 14 checks, max |z| 0.90). Replaced only because the
runner gained the §6 test descriptives (Artem, 2026-11-14). Engine vs simulator rows are identical to
the current run (same seeds).

**Second full run kept as history** (`runs/qx2_pilot20b/dry_check_r2_cellfloor.json`, sha256
`1b6fc977…679d`, runner `cf86b601…de8e`; pass, max |z| 0.86). Its SE used the engine's per-replicate
variance, but with a floor at the per-cell binomial variance at the pooled mean (m = mean of engine and
simulator), and the Bhatia–Davis floor at that pooled m in constant rows. Replaced (Artem, 2026-11-14)
because the floor mixed cell and replicate units, and m must be the simulator's mean. The engine
replicates and the means are unchanged (same seeds). Only the SE and z values changed.

**First full run failed and is kept** (`runs/qx2_pilot20b/dry_check_fail1.json`, sha256
`c3c9b4e6…0196`, runner `ddedd951…1470`). Only failure: δ = 1/64, B = 4, adopt_shared abandonment,
engine 1.000 vs simulator 0.998, z = 8.17. Cause: the SE floor used per-cell binomial variance, but this
outcome is replicate-level (a replicate with no refutation has abandonment 0). The simulator had 2 of 1,000
such replicates; 0 of 200 in the engine has probability 0.998^200 ≈ 0.67. Fix: when every engine replicate
is identical, the variance floor is the Bhatia–Davis bound m(1 − m). Only `_se` changed; all other rows
are identical between the two runs (same seeds). That fix produced the second run above, since replaced.

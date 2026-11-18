# Amendment — QX-3 with four tests per cell: does a rule name carry the true rule when finders can check it?

**Status:** locked v2 (2026-11-18), written by the reviewer for Artem. v2 takes in the dry build of v1:
the Luna cost from the measured prompt length, the trace fields added by the runner, the queue, and the
start rule written out. It is locked after the reviewer's review. No call is made before the lock and Artem's go,
logged in the switch log with his words.

## Why

In QX-3 every cell had one test for the whole run (B = 1). The Luna runs at δ = 1/64 (entries 7 and 8)
showed, after the data:

- A cell that finds the first counterexample usually takes U, the simpler sibling of H_T (the same
  substitution without its condition): 34 of 49 such cells. One counterexample and the cell's two
  examples fit both rules, and with B = 1 its only test was the counterexample, so it cannot rule U out.
- A cell with its own counterexample takes H_T when a neighbour names it: 36 of 39.
- With rule names only, the first finders took U, H_T was never named, and x̄ stayed at 0–0.012 in
  every world.

With four tests a finder can rule U out itself, since about 35–41 % of Luna's tests fall where U and
H_F differ but H_T and H_F do not. This amendment asks whether rule names then carry H_T: first to the
finders' own rule, then to neighbours.

## Setup

Every run is labelled **model · δ · B · message · world**.

| part | model | δ | B | message | worlds | new runs |
|---|---|---|---:|---|---|---:|
| L4 | Luna | 1/64 | 4 | rule only | 0, 1, 2, 3 | 4 |
| O4 | gpt-oss-20b | 1/64 | 4 | rule only; rule + chosen result | 0, 1, 2, 3 | 8 |

- G = 24, world seeds as in `AMENDMENT_QX3_WORLDS.md`. Prompts, schemas and decoding are those of the
  QX-3 runs; only B changes. The prompt states the budget, as it does at B = 1.
- **B = 4 means four tests per cell for the whole run,** at most one per generation, each result
  arriving in the next generation, no test in generation 24.
- **gpt-oss-20b at δ = 1/64.** In entry 1 this model found no counterexample at δ = 1/64 with B = 4
  (0 of 44 tests). That was QX-2, one run, in world 0. If it again finds none, O4 answers only that,
  and is reported so.
- **Comparison runs, already made or queued:** Luna, δ = 1/64, B = 1, rule only, worlds 0 (r2), 1, 2,
  3 (entry 8). For gpt-oss-20b there are no B = 1 runs at δ = 1/64; O4 is read on its own.
- **Run names:** `qx3b4_{model}_d64_B4_{arm}_w{seed}`, for example `qx3b4_luna_d64_B4_R_w1`. The new
  runner writes the world seed, the H_F, H_T and U keys and the generation-0 messages onto each trace
  after the run; the engine (`run_population`) is not changed. Analyses read the keys from the trace.

### Luna

- Cost per run is projected from the B = 1 rule-only rate ($1.02) scaled by the generation-1 prompt
  length (5,996 characters at B = 4 against 5,994 at B = 1): $4.08 for four runs.
- **Hard stop: $6.00.** **Start rule:** a run starts only if this amendment's Luna spend so far plus
  1.5 × the run's projected cost is at most $6.00, and all Luna spend stays within the $45.00
  authorization (Artem, 2026-11-18: «ну давай $20 сверху, но не больше») with $2.00 still unspent for
  the why-probe.

### gpt-oss-20b

- The QX-3 revision, image, request body and server context 40,960.
- About 2.8 GPU-hours per rule-only run and 3.4 per run with results, at QX-3 rates; B = 4 adds tests,
  not calls. About 25 hours for eight runs.
- **Queue:** the live queue is not changed (QX-3 main 20b, Nemotron with budget, QX-2 continuation).
  These runs wait until a waiter for the gpt-oss-20b runs of `AMENDMENT_QX3_WORLDS.md` exists and that
  set finishes, unless Artem orders otherwise.

## Measures

Per run: x̄ (mean share on H_T over generations 13–24) and x̄_nf (only cells that never had a
counterexample of their own). Per finder (first own counterexample before any received one): the rule
it holds two generations after its counterexample, and whether it then holds its own result ruling out
U (an input where U changes the output and the stored output equals H_F's). The number of cells that
named H_T in each generation. The share of tests on the H_T region and on the U-only region.

## Tests

**T-L4 (Luna): B = 4 above B = 1, rule only.** One-sided exact permutation test on x̄, the four L4
runs against the four Luna B = 1 rule-only runs of entry 8 (worlds 0–3). One claim, α = 0.05, so
p ≤ 3/70. A missing or partial run leaves it not decided.

**T-O4 (gpt-oss-20b): rule + chosen result above rule only, at B = 4.** The same test on the eight O4
runs. One claim, α = 0.05.

Each model is its own claim. No test joins them.

## Predictions stated in advance

| test | prediction | basis |
|---|---|---|
| T-L4 | holds | with four tests Luna finds the counterexample about four times as often, and finders can rule U out themselves; even if only finders hold H_T, x̄ rises above the B = 1 values (0–0.006) |
| T-O4 | uncertain | at δ = 1/64 gpt-oss-20b may find no counterexample at all |

## Readings stated in advance

| pattern | reading |
|---|---|
| T-L4 holds, x̄_nf ≈ 0 | Four tests let finders reach H_T, but the name still does not move cells without evidence. The rule-only failure at B = 1 was partly the wrong name and partly that names do not move. |
| T-L4 holds, x̄_nf clearly above 0 | Once H_T is named, cells without evidence follow it in places; read with the majority step of entries 5 and 7 (number of naming neighbours at each move). |
| T-L4 does not hold | Even with four tests, finders do not reach H_T, or there are too few of them; the per-finder table says which. |
| L4 finders mostly hold U two generations after their counterexample, with no own U-refuting result | The budget is not the limit; Luna does not use its tests to separate U from H_T. |
| T-O4 any outcome with zero finders in a run | gpt-oss-20b does not find the region at δ = 1/64; the comparison says nothing about spreading. |

## Gates

As in `AMENDMENT_QX3_WORLDS.md`: world checks, the format gate, the engine invariants (no result in the
rule-only arm; at most four tests per cell, at most one per generation, none in generation 24), the
Luna stop and start rule.

## Dry build (CPU, no model call)

1. The B = 4 generation-1 prompt for each model and arm against the B = 1 prompt: only the budget text
   differs. Its token count and the Luna cost projection.
2. The engine with a fake client at B = 4: test counts per cell, arrival timing, the rule-only
   invariant.
3. Run names and cache keys distinct from all earlier runs.
4. The U key per world from `build_world(seed)`, and the U-only region.
5. The tests on constructed values, including a missing run.
6. GPU hours and the queue position.

## Outputs

Calls (reasoning stored for gpt-oss-20b only), traces, the readout with both tests and the per-finder
table, and one recheck package per model with SHA256SUMS. Nothing enters the QX page before the
reviewer's recheck from raw data.

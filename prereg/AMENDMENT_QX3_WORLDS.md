# Amendment — QX-3 across worlds: rule alone against rule plus counterexample, and the majority step

**Status:** locked v2 (2026-11-18), written by the reviewer for Artem. v2 takes in the dry build of v1:
explicit run names, the world-0 trace fields computed rather than read, the GPU time and Luna sums
corrected, and a counting rule for tests on the region. It is locked after the reviewer's review. No call is made before the lock and Artem's go,
logged in the switch log with his words.

## Why

The QX-3 main phase (`AMENDMENT_QX3_MAIN.md`) repeated each condition four or five times in one world,
world seed 0. Its runs differ only through the models' own sampling. That shows the results are not
an accident of one run. It does not show that they are not a property of world 0.

A world seed draws much of what a cell sees (agent's report on `qx2_world.build_world`, 2026-11-18):
the 16 substitution rules of the catalog and which of them is H_T, so also the region of inputs where
H_F and H_T differ; the rule keys; each cell's two examples; the catalog line order in each prompt; and
the generation-0 signals. H_F (`shift_symbols(1)`), the 100 base rules and δ are fixed by design.

This amendment runs the two central comparisons in other worlds, with **one run per world**. A run
in a new world varies the world and the model's sampling at once, so the world is the unit of repeat.

## Worlds

- **New worlds:** seeds 1, 2, 3 for the message comparison, and seeds 1, 2, 3, 4 for the majority
  step. Their hidden regions, from the dry build of 2026-11-18:

  | seed | δ = 1/8: H_T differs where | δ = 1/64: H_T differs where |
  |---|---|---|
  | 1 | position 3 is C | positions 0 and 3 are C |
  | 2 | position 0 is E | positions 0 and 3 are E and C |
  | 3 | position 3 is D | positions 1 and 3 are E and D |
  | 4 | position 0 is C | positions 0 and 2 are C and D |

  In none of them does a cell's example lie in either region.
- **World 0** enters every comparison with **one** run fixed here, before any data of this amendment:
  run r2 of the main phase for each arm and model. No new run is made in world 0.
- Seeds were not chosen by looking at any model output. They are the next integers.

## Runs

| model | cell | arms | worlds | new runs | new calls |
|---|---|---|---|---:|---:|
| Luna | δ = 1/64, B = 1 | R, R+E | 1, 2, 3 (+ 0: r2) | 6 | 14,400 |
| Luna | δ = 1/8, B = 1 | R | 1, 2, 3, 4 (+ 0: r2) | 4 | 9,600 |
| gpt-oss-20b | δ = 1/8, B = 1 | R, R+E | 1, 2, 3 (+ 0: r2) | 6 | 14,400 |

- The prompts, schemas, attach rule, decoding and G = 24 are those of the main phase. The only change
  is the world seed. The forced arm is not repeated across worlds.
- **Run names** carry the model, δ, budget, arm and world, for example `qx3w_luna_d64_B1_R_w1`,
  `qx3w_luna_d8_B1_R_w1` and `qx3w_20b_d8_B1_RE_w1`. The cache key hashes the run name, so it includes
  the world. No answer is shared between worlds or with the main phase.
- **Traces store** the world seed, the H_F key, the H_T key for the run's δ, and the generation-0
  messages. Every analysis reads the keys from the trace, never from a constant: in world 4 the
  δ = 1/64 substitution has key K026, which is H_F's key in world 0. The stored world-0 runs (r2) have
  none of these fields; for them the readout computes the same fields from `build_world(0)`, checks
  them against the trace, and does not rewrite the trace.
- **Runners** are new files. Nothing pinned by an earlier manifest is edited.

### Luna

- **Cost at the measured QX-3 rates:** R $1.02, R+E $1.44, dose R $1.06 per run, so $7.38 for the
  message comparison and $4.24 for the majority step, $11.62 in all. Generation-1 prompts in worlds 1–4
  are 6,192–6,195 characters, as in world 0, so the rates should carry over.
- **Hard stop: $16.00** for this amendment's Luna calls, summed from their non-cached rows.
- **Start rule:** a run starts only if this amendment's Luna spend so far plus 1.5 × the run's projected
  cost is at most $16.00, and the total Luna spend stays within the authorization ($45.00; Artem,
  2026-11-18: «ну давай $20 сверху, но не больше»).
- **Order:** the message comparison first (w1 R, w1 R+E, w2 R, …), then the dose runs (w1 … w4).

### gpt-oss-20b

- The main phase's revision, image, request body and server context 40,960.
- At the main phase's measured times, about 2.8 GPU-hours per R run and 3.4 per R+E run, 19 hours in
  all.
- **Queue:** after the QX-3 main phase on gpt-oss-20b and Nemotron with the thinking budget, before
  the QX-2 continuation and the Qwen temperature battery, unless Artem orders otherwise.

## Measures

As in the main phase: **x̄**, the mean share of the 100 cells on H_T (this world's H_T) over
generations 13–24, one value per run. x̄_nf (cells without a counterexample of their own) is reported,
with no α. Per run, descriptive: the number of independent finders (first own counterexample from a
test chosen before any received one) and following finders, and the share of tests on the region: a
test is on the region when its input is one where that world's H_T and H_F differ, and the share is
taken over every test the cells spent.

## Tests

**W-L (Luna) and W-B (gpt-oss-20b): R+E above R.** One-sided exact permutation test on the x̄ values,
four worlds against four (70 splits, ties against rejection, `THEORY.md` §8.2). Each model is its own
claim, one test each, at α = 0.05, so p ≤ 3/70 = 0.043 is needed. Complete separation gives 1/70.
With one run out of order the p is 2/70 or more, depending on the values, so the test can still
hold; the dry build shows the cases.

The worlds are treated as independent units, and the R and R+E runs of one world are not paired. A
paired test over four worlds could not reach 0.05 (its smallest p is 1/16).

**W-S (Luna): the majority step.** The Family S test of `AMENDMENT_QX3_MAIN.md`, unchanged, over the
five worlds 0 (r2), 1, 2, 3, 4: d = p_high − p_low per run, with a run of fewer than 5 cells in either
group counting as d ≤ 0. W-S holds if d > 0 in all five, P ≤ 1/32.

**Missing runs:** a comparison with a missing or partial run is reported as not decided.

## Predictions stated in advance

| test | prediction | basis |
|---|---|---|
| W-L | holds | world 0: R 0–0.012 against R+E 0.998–1.000 in four runs |
| W-B | uncertain | the gpt-oss-20b main phase is not yet read; pilot 0.274 against 0.614 |
| W-S | holds | world 0: d 0.83–1.00 in five runs |

## Readings stated in advance

| pattern | reading |
|---|---|
| W-L holds | For Luna, rule names fail and shared evidence carries a rare error in other worlds too, with a different hidden region and different examples. |
| W-L fails, and an R+E run had no independent finder | The comparison failed on discovery in that world, as in run 5 of the forced arm in world 0. Reported with the finder counts; it is not read as evidence failing to spread. |
| W-L fails with finders in every R+E run | The world-0 result does not carry over; the per-world values are the summary. |
| W-B holds or fails | Read in the same way, for gpt-oss-20b at δ = 1/8. |
| W-S holds | The majority step is not a property of world 0. |
| W-S fails | The per-world shares are the summary; no claim that the step is absent. |

A new world can also change how easy the region is to find, because the catalog descriptions move
with it. The share of tests on the region is reported per world for that reason.

## Gates

- **World checks:** `world_checks` passes for each seed; no example lies in either region; the H_F and
  H_T keys in each trace equal those of `build_world(seed)`.
- **Format:** as in the main phase (more than 4 fallbacks or truncations in the first 400 decisions
  stops that run).
- **Engine:** the main phase's invariants in every run.
- **Luna:** the $16.00 stop and the start rule.

## Dry build (CPU, no model call)

1. World checks for seeds 1–4, with the regions above, the keys of H_F and H_T, and the absence of
   examples in the regions.
2. Generation-1 prompts for each world, arm and model, and their differences from world 0: only the
   world-drawn parts (examples, the 16 substitution lines, keys, catalog order, generation-0 signals).
3. Run names and cache keys distinct from each other and from the main phase.
4. The trace fields: world seed, H_F key, H_T key, generation-0 messages.
5. A grep of the analysis and recheck scripts for literal rule keys.
6. The tests on constructed values (W-L/W-B: complete separation gives p = 1/70; cases with one run
   out of order that give p ≤ 3/70 and cases that give more; W-S as in the main phase).
7. Luna cost, the start rule and the stop; gpt-oss-20b GPU hours.

## Outputs

Calls (final text and usage; reasoning stored for gpt-oss-20b only), traces, the readout with all
tests, and one recheck package per model with SHA256SUMS. Nothing enters the QX page or the paper
before the reviewer's recheck from raw data.

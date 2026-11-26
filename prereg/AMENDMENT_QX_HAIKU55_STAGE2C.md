# Amendment — Claude Haiku 5.5, Stage 2C: the QX-3 main set at δ 1/64 (repeated runs, world 0)

**Status:** draft v2 (2026-11-24), written by the reviewer for Artem. v2 takes in the dry build
(`runs/dry_build_qx_haiku55_stage2c.md`, of v1 `ad1e9034…`): run names, 0 prompt and 0 schema mismatches against
Luna's main-phase generation-1 prompts (400 cells per arm), token counts, the projection and the start rule. Stage 2, item 4 of `AMENDMENT_QX_HAIKU55.md`
(v2, locked `c5d7488d…`): "The QX-3 main set at δ 1/64 (as entries 7, 8) — only if money remains." Artem,
2026-11-24 18:44: «Давай». Money ceiling for Haiku: $72 in all (Artem, 2026-11-24 10:52). Locked after the
agent's dry build and the reviewer's review; no call before the lock and Artem's go, logged verbatim.

## Why

Entry 7 repeated Luna's δ 1/64 pilot four times per arm in world 0: rule only against rule plus a chosen
result against rule plus an engine-attached result (Family L). Haiku has so far been run once per world
(entries 19, 20). This stage gives Haiku the same repeated-run design, so its run-to-run spread is measured,
and asks the same three questions for the rare error. Entry 20 showed the bottleneck that this stage will
meet: with one test per cell Haiku's tests land on the δ 1/64 region at about the random rate, so many runs
may have no finder at all. The forced arm separates "no finder" from "a finder who does not share".

## Design (only the model changes)

Prompts, schemas, engine, world, attach rule, G = 24 and measures as in `AMENDMENT_QX3_MAIN.md` (locked) for
Luna's δ 1/64 family, with the pilot world of entry 7 (world 0, `ql/world_pilot.json`); decoding as in Haiku
Stage 0 (adaptive thinking, effort medium, max_tokens 8192, Luna's schema, prompt bytes as rendered for Luna).

**Claude Haiku 5.5 · δ 1/64 · B 1 · message: R (rule only), R+E (rule plus a chosen result), R+E forced
(the engine attaches the cell's most recent result that refutes H_F, if it has one) · G 24 · world 0 ·
4 runs per arm (r1–r4).** 12 runs, 28,800 calls.

- Run order: by run, then by arm: r1 R, r1 R+E, r1 forced, r2 R, … Run names: `qx3_haiku55_d64_B1_R_r{1..4}`,
  `qx3_haiku55_d64_B1_RE_r{1..4}`, `qx3_haiku55_d64_B1_REf_r{1..4}` (dry build: 28,800 distinct cache keys, none
  cached). Generation-1 prompts: cell 0 sha256 `2c7222bb…` (R, forced; byte-equal) and `00cdb8a2…` (R+E); schema
  `0e7055f0…` for all three arms; input 4,461 / 4,489 / 4,461 tokens (cell 0).
- Cache key includes model, arm and run; no answer is shared between runs.
- The Stage 2B run `qx3w_haiku55_d64_B1_R_w0` (x̄ 0, no finder) is reported beside arm R, not in any test,
  because it was run on the worlds engine, not the main-phase runner.
- Missing runs: if any arm has fewer than four finished runs, the family is not decided (as in the original).

## Measures

As in `AMENDMENT_QX3_MAIN.md`: x̄ per run (share on H_T, generations 13–24) is primary; x̄_nf descriptive.
Also reported, no test: finders per run and the rule each holds two generations after its first
counterexample (H_T, the unconditional substitution K047, H_F, other); messages with a result, refuting or
not, own or relayed; first received counterexample → rule in that generation and two later; tests on the
region.

## Tests (Family HL; one-sided exact permutation on x̄, four runs against four, 70 splits, ties against
rejection; Bonferroni over three tests, each at p ≤ 0.0167, so each holds only with complete separation)

- **H1:** R+E above R.
- **H2:** R+E forced above R.
- **H3:** R+E forced above R+E.

## Predictions stated in advance, derived from measured data

Inputs, all measured on Haiku: tests on the region in world 0 at δ 1/64: 8 of 500 (Stage 2B, B 1 and B 4) →
finders per run ≈ Poisson(1.6), P(no finder) ≈ 0.20; a finder holds H_T two generations later in 8 of 15
(Stage 2B); a finder attaches its counterexample at some point in 32 of 89 cases (Stage 2A, δ 1/8); a received
counterexample is taken in 237 of 242 (entry 19). A simulation with these inputs (seed 0, 200,000 families;
the level of a spreading run drawn uniformly in [0.3, 0.9], since it is not measured at δ 1/64) gives the
chance of complete separation:

| test | P(separation), derived | prediction |
|---|---:|---|
| H1 | 0.05 | does not hold: an R+E run spreads with P ≈ 0.44, and all four must |
| H2 | 0.40 | uncertain: a forced run spreads whenever it has a finder (P ≈ 0.80) |
| H3 | 0.08 | does not hold (depends on the unmeasured spread level) |

Stated risk: the inputs are measured at δ 1/8 (sharing) or across four worlds (finding); world 0 alone may
differ, and at δ 1/64 a received counterexample also fits K047, so receivers may split as finders did.

## Readings stated in advance

| pattern | reading |
|---|---|
| H2 holds, H1 does not | With guaranteed sharing the rare error reaches the grid in every run; without it, too few finders share. The limit is the sender, given a finder. |
| H1 and H2 hold | Haiku's own sharing suffices at δ 1/64 in every run, against the prediction. |
| neither holds; runs without a finder in every arm | Finding is the limit: with one test per cell the rare error is often not found at all. |
| neither holds; finders present but receivers on K047 | Shared evidence moves cells, but to a rule that fits it as well as H_T. |
| H3 holds | Attached evidence beats Haiku's own sharing in every run. |
| family not decided | Reported as such, with the finished runs described. |

## Money

Projection from Haiku's measured cost per call (δ 1/64 B 1 R, Stage 2B: $0.00064; δ 1/8 R+E, Stage 2A: $0.00075;
forced taken as $0.00072): R 9,600 × 0.00064 + R+E 9,600 × 0.00075 + forced 9,600 × 0.00072 ≈ **$20.3** (dry build: $20.256).
**Stop $30.40** (1.5 × projection), summed from non-cached rows of this stage's calls. Haiku money left before this
stage: $72 − $14.19 − $18.90 = $38.91; the stop fits. Start rule as in the original: a run starts only if the
spend so far plus 1.5 × that run's projection is at most the stop. The page and paper carry no dollar figures.

## Gates

Format gate per run as in the original (more than 4 fallbacks or truncations in the first 400 decisions stops
that run); API errors retried once, then counted; a run with more than 2 % failed calls is stopped and reported.
Engine invariants of the original asserted in every run (no result in R; results stored with true outputs;
the attach rule; no test in generation 24).

## Dry build (CPU, no model call)

1. Twelve run names with distinct cache keys; run order.
2. Generation-1 prompts and schemas for each arm, byte-equal to Luna's main-phase prompts of the same arm
   (mismatch count reported).
3. Token counts per arm and the projection at the measured rates; the start rule checked on the projection.
4. The test code on constructed run values (complete separation p = 1/70; one overlap ≥ 2/70; ties; a missing
   run → not decided).

## Outputs

Calls (final text and usage; no reasoning text stored), traces, readout with H1–H3, one recheck package per
finished set of three arms (r1, r2, …) with SHA256SUMS. Nothing enters the page before the reviewer's recheck
from raw data; the page entry comes with all twelve runs in the run viewer.

# Amendment — Claude Haiku 5.5, Stage 2A: rule names against shared evidence across worlds (W-H)

**Status:** draft v2 (2026-11-24), written by the reviewer for Artem. v2 takes in the dry build
(`runs/dry_build_qx_haiku55_stage2a.md`): run names and cache keys checked distinct, prompts rebuilt, token
counts, the cost projection and stop, W-H on stubs. Stage 2, part 1 of
`AMENDMENT_QX_HAIKU55.md` (v2, locked `c5d7488d…`). Artem, 2026-11-24 07:35, agreeing to the reviewer's
proposal: "Согласен" — worlds R and R+E first, because Haiku's bottleneck in isolation is passing evidence on.
Locked after the agent's dry build and the reviewer's review; no call before the lock and Artem's go.

## Design (only the model changes)

The prompts, schemas, attach rule, engine, world construction, trace contents and measures are those of
`AMENDMENT_QX3_WORLDS.md` (locked v2) at the setting of its gpt-oss-20b part (W-B):

**Claude Haiku 5.5 · δ 1/8 · B 1 · rule only (R) and rule + chosen result (R+E), QX-3 · G 24 · worlds 0–3, one
run per world and arm** (8 runs, 19,200 calls). World 0 is run fresh (Haiku has no main-phase runs). Run
names `qx3w_haiku55_d8_B1_{R,RE}_w{0..3}`. Decoding as in Stage 0 (adaptive thinking, effort medium,
max_tokens 8192, Luna's schema, prompt bytes identical to the engine's rendering for Luna).

## Test

**W-H: R+E above R on x̄** (mean share on H_T over generations 13–24), one-sided exact permutation test, four
worlds against four (70 splits, ties against rejection), α = 0.05, p ≤ 3/70. A missing or partial run leaves it
not decided.

**Prediction: holds.** Basis (derived, not intuition): (i) in every model that attached counterexamples,
attached results moved neighbours (W-B gpt-oss-20b 1/70 at δ 1/8 with results on 2–3 % of messages; W-L Luna);
(ii) in isolation Haiku attaches the counterexample in about a third of its updating answers with its own
evidence (80/238), far more than gpt-oss-20b (3/30); (iii) Haiku did not leave H_F without evidence in any
isolation condition (U0, 0/240), so rule names alone are not expected to carry H_T in R.

## Readings stated in advance

As in `AMENDMENT_QX3_WORLDS.md`: W-H holds → for Haiku, shared evidence carries the rare error where names do
not; W-H fails and an R+E run had no independent finder → failed on discovery, reported with finder counts;
W-H fails with finders in every R+E run → evidence does not carry for Haiku; x̄_nf in R clearly above 0 → Haiku
follows names (read with the majority-step counts).

Also reported, no test: x̄_nf per run, finders (independent, following), tests on the region, results per
message and the share of results that are counterexamples, silence share, the first-contact table of entry 16
(by the rule the sender named), and the TEST_CHOICE measures (descriptive, as for Luna).

## Money (internal; no dollar figures on the page)

Projection from the dry build: input 4,717 tokens per call (mean of a generation-1 prompt, 4,461, and the
longest late prompt, 4,973, by Anthropic's count endpoint), output 657 tokens per call (Stage 0–1 mean),
19,200 calls ≈ $15.4. **Hard stop $23.10** (projection × 1.5); stop + $0.77 already spent ≈ $23.9, under the $50
ceiling. Runs go in the order R_w0, RE_w0, R_w1, RE_w1, …, so a stop
leaves complete pairs.

## Gates

As in `AMENDMENT_QX3_WORLDS.md` and `AMENDMENT_QX_HAIKU55.md` (format gate per run: more than 4 fallbacks or
truncations in the first 400 decisions stops that run; API failures retried once; > 2 % failed calls stops the
run).

## Outputs

One recheck package per two worlds (traces with world seed and keys, calls with usage, output tokens and USD,
no reasoning text), the readout with W-H. A page entry with the runs in the run viewer (model group
"Claude Haiku 5.5") after the reviewer's recheck.

# Amendment — gpt-oss-120b on two core QX-3 experiments, worlds 0–3

**Status:** draft v1 (2026-11-25), written by the reviewer for Artem. Artem, 2026-11-25 22:38: «120b бросать не хочется, он
ближе к Luna и иметь что-то os кроме GPT моделей»; 22:42, on the reviewer's proposal to close 120b before adding models:
«Как тебе кажется лучше, переключиться и закрыть по максимуму 120b и потом добавлять модели?». Locked after the agent's dry
build and the reviewer's review; no model call before the lock and Artem's go, logged verbatim. GPU only; no API money.

## Why

gpt-oss-120b has run QX-2 on the four cells (entry 14, extended to 24 generations) and the isolation battery (entry 16), but
no QX-3 population run. Two QX-3 experiments carry the main comparisons between models: rule names against shared results at
δ 1/8 (entry 13 for gpt-oss-20b, entry 19 for Claude Haiku 5.5, both held), and the same at δ 1/64 with four tests per cell
(entry 17 for gpt-oss-20b, not held; entry 24 for Haiku, held). This amendment runs both for gpt-oss-120b, so its bottleneck
can be placed beside the others'.

## Design (only the model changes)

Engine, prompts, schemas, world files and messages exactly as the runs they mirror: Part A as gpt-oss-20b's entry 13 /
Haiku's entry 19 (worlds engine, δ 1/8, B 1); Part B as gpt-oss-20b's entry 17 / Haiku's entries 20 and 24 (δ 1/64, B 4).
Model, revision, SGLang image, launch spec, chat template and decoding as pinned for gpt-oss-120b in the ladder and isolation
runs (reasoning effort medium, max_tokens 32,768); reasoning stored for every call (open model).

- **Part A — gpt-oss-120b · δ 1/8 · B 1 · rule only vs rule + chosen result · 24 generations · worlds 0–3, one run each.**
  8 runs, run names `qx3w_oss120_d8_B1_{R,RE}_w{0..3}`.
- **Part B — gpt-oss-120b · δ 1/64 · B 4 · rule only vs rule + chosen result · 24 generations · worlds 0–3, one run each.**
  8 runs, run names `qx3b4_oss120_d64_B4_{R,RE}_w{0..3}`.

All 16 runs are new (120b has no QX-3 run to reuse). Order: Part A world by world (R then RE), then Part B the same way.
16 × 2,400 = 38,400 calls. Time, from 120b's measured pace in the QX-2 extensions (≈ 400 calls per hour): ≈ 6 h per run,
≈ 48 h per part, ≈ 4 days in all; stated as an assumption, the first run measures it.

## Measures

x̄ per run (share on H_T, generations 13–24) primary. Descriptive, as in entries 19 and 24: x̄_nf; finders (own counterexample);
tests on the region; rules held at 24 (H_T, H_F, the unconditional substitution U in Part B, other); messages with a result, with
a counterexample, and (Part B) with a U-refuting result, own or relayed; for each cell that first holds H_T, whether its memory
then held a counterexample and a U-refuting result, own or received; the majority step (Family S definition, entry 7) in the
rule-only runs.

## Tests (one-sided exact permutation on x̄, four worlds against four, 70 splits, ties against rejection; each holds at p ≤ 3/70)

- **W-H120 (Part A):** x̄ with a chosen result above x̄ with rule only, δ 1/8.
- **W-H4E120 (Part B):** the same at δ 1/64 with four tests.

## Predictions stated in advance, derived from measured data

Inputs: the two other models with both parts measured, and 120b's isolation rates (entry 16). Spread of a counterexample needs a
receiver that updates on a received one and a holder that sends it: received-counterexample update rate × own attach rate is
0.93 × 0.34 ≈ 0.32 for Haiku, 0.57 × 0.47 ≈ 0.27 for 120b, 0.33 × 0.15 ≈ 0.05 for gpt-oss-20b (isolation, U2 consistent share
× U1 attach share).

- **W-H120: holds.** At δ 1/8 both models measured held with complete separation (20b 1/70 with factor 0.05; Haiku 2/70 with
  0.32); 120b's factor (0.27) lies between them, and its QX-2 runs show counterexamples carrying the spread beyond the finders.
- **W-H4E120: uncertain.** At δ 1/64 with four tests Haiku held (1/70) and gpt-oss-20b did not (41/70). Haiku's H_T holders
  combined a received counterexample with their own U-refuting result (129 of 189); whether 120b does depends on its tests and
  on taking the counterexample (57 % of received ones in isolation, against Haiku's 93 %). No derivation gives a side.

Stated risk: 120b's QX-3 test placement and majority step are unmeasured.

## Readings stated in advance

| pattern | reading |
|---|---|
| both hold | 120b's bottleneck matches Haiku's at the population level: shared results move it, finding sets the ceiling. |
| A holds, B does not | Like gpt-oss-20b at δ 1/64: with a rare error, shared results do not reach H_T; the memory measure says whether the missing piece is the second result or taking the first. |
| A does not hold | Against the prediction; read with the attach and update counts which link failed. |
| rule-only x̄_nf well above 0 | 120b follows names like Luna (majority step), unlike Haiku and gpt-oss-20b. |

## Gates, dry build, outputs

Format gate as in the QX-3 worlds runs; waiters keep stdout and stderr in a log file; the readout is run end to end on stub traces
in the dry build. Dry build (CPU, plus a server start without completion calls only if the GPU is free): the 16 run names and cache
keys; generation-1 prompts byte-equal to the mirrored runs of gpt-oss-20b (Part A: entry 13 / Haiku entry 19; Part B: entry 17) after
the model change (mismatch counts per world); the 120b pins and their sources; the U-refuting input sets for Part B; the time
projection. Outputs: one recheck package per finished world pair (R and RE) with SHA256SUMS, in the same message as the finish;
readouts with W-H120 and W-H4E120 at the end of each part. Nothing enters the page before the reviewer's recheck; entries come
with all runs in the run viewer (Core experiments: δ 1/8 · R vs R+E and Four tests, gpt-oss-120b).

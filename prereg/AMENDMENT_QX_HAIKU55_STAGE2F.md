# Amendment — Claude Haiku 5.5, Stage 2F: δ 1/64, four tests, rule plus a chosen result, worlds 0–3

**Status:** draft v1 (2026-11-25), written by the reviewer for Artem. Artem, 2026-11-25 15:18: «Что ты думаешь про Four
Tests with choosen result for Haiku?»; 15:19, on the money: «Готов докинуть». Locked after the agent's dry build, the
reviewer's review and Artem's stated new Haiku ceiling; no call before the lock and Artem's go, logged verbatim.

## Why

At δ 1/64 Haiku's population runs have failed for two reasons (entries 20, 22, 23): few cells find the counterexample
with one test, and a single counterexample fits the unconditional substitution as well as H_T, so finders and their
neighbours take the substitution. Reaching H_T needs a second result that the substitution gets wrong. Luna put H_T
together from such results found by different cells (entry 8). With four tests per cell (Stage 2B, entry 20) every world
had finders (6, 4, 3, 2) and 18 % of tests fell where the substitution is refuted, but with rule names alone no cell
without its own counterexample moved (x̄ 0.015–0.043). This stage gives the same setting the chosen result, which is the
only change: can Haiku cells assemble H_T from the results their neighbours send? It also completes the Core experiments
row "Four tests" for Haiku in both messages, as for gpt-oss-20b (entry 17).

## Design (only the message changes against Stage 2B part L)

**Claude Haiku 5.5 · δ 1/64 · B 4 · rule plus a chosen result · 24 generations · worlds 0–3 · one run per world.**
4 runs, 9,600 calls, run names `qx3b4_haiku55_d64_B4_RE_w{0..3}`. Engine, prompts, schemas and world files exactly as the
Stage 2B four-test runs `qx3b4_haiku55_d64_B4_R_w{0..3}` with the message switched to rule plus a chosen result (the
paragraph used in entries 19 and 23). The rule-only arm is those four Stage 2B runs, compared by file hash, not rerun.
Decoding as in Haiku Stage 0. No reasoning text stored.

## Measures and test

x̄ per run (share on H_T, generations 13–24) primary. Descriptive: x̄_nf; finders; rules held at 24 (H_T, the
unconditional substitution U, H_F, other); messages with a result, with a counterexample (output ≠ H_F(input)), and with a
U-refuting result (input x with U(x) ≠ H_T(x), output = H_T(x)), each split own / relayed; for every cell that first holds
H_T, whether its memory then held (a) a counterexample and (b) a U-refuting result, own or received.

**Test W-H4E:** x̄ with a chosen result above x̄ with rule only, four worlds against four, one-sided exact permutation,
70 splits, ties against rejection; holds at p ≤ 3/70.

## Prediction stated in advance, derived from measured data

Rule-only x̄ (fixed): 0.0425, 0.0233, 0.0267, 0.0150; the test needs (nearly) every world with results above 0.0425.
Measured on Haiku at δ 1/64 with a chosen result and at least one finder (Stage 2C runs 1, 3, 4; Stage 2E worlds 0–2):
x̄ = 0.294, 0.158, 0.472, 0.0008, 0.0792, 0.0158 — above 0.0425 in 4 of 6. Taking 4/6 per world: chance that all four
worlds exceed it ≈ (2/3)⁴ ≈ 0.20. **Prediction: does not hold** (derived chance ≈ 0.20). Stated risk: those runs had one
test per cell and 1–3 finders; with four tests and more finders per run the chance per world may be higher.

## Readings stated in advance

| pattern | reading |
|---|---|
| holds; H_T holders' memories held both a counterexample and a U-refuting result | Shared results let Haiku cells assemble the rule from evidence found by different cells, as Luna did. |
| holds; H_T holders mostly had their own counterexample | Four tests made more finders, and sharing added some spread; assembly from others' evidence not shown. |
| does not hold; finders on U, receivers on U | Shared evidence moves cells, but to the rule that fits a single counterexample; U-refuting results do not reach or do not move them. |
| does not hold; U-refuting results were received but cells stayed on U | The evidence that separates H_T from U arrives but does not change the chosen rule. |

## Money

Projection: 9,600 × $0.00072 (Stage 2E measured $0.000706 per call, rounded up for longer memories with four tests) ≈
**$6.91**; **stop $10.37** (1.5 ×). Haiku spent so far: $14.19 + $18.90 (2B) + $6.26 (2D) + $20.58 (2C) + $6.78 (2E) =
$66.70. The $72 ceiling does not cover the stop: **Artem states the new Haiku ceiling before the lock** (at least
$66.70 + $10.37 = $77.07). Start rule as before. The page carries no dollar figures.

## Gates, dry build, outputs

Format gate as in Stage 2B. Waiters keep stdout and stderr in a log file (lesson of Stage 2E). The readout is computed by
code tested on the dry-build stubs before the first call. Dry build (CPU): run names and cache keys; generation-1 prompts
byte-equal to the Stage 2B four-test prompts with the message paragraph of entry 23 (mismatch counts per world); the
sha256 of the four reused rule-only traces; the U-refuting input set per world (count, and a check that U and H_T differ
on each); token counts and the start rule; the test code and the full readout run end to end on stub traces. Outputs:
calls (usage, no reasoning), traces, readout with W-H4E and the descriptive measures, a package with SHA256SUMS in the same
message as the finish. Nothing enters the page before the reviewer's recheck; the entry comes with the four runs in the
run viewer (Core experiments, Four tests, Claude Haiku 5.5).

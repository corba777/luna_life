# Amendment — Claude Haiku 5.5, Stage 2D: QX-2 on the four cells

**Status:** draft v2 (2026-11-24), written by the reviewer for Artem. v2 (before any dry build) adds the extension to 24 generations by the locked group-B rule and a fixed 2D stop of $8.51 (Artem 19:44: 12 or 24 generations should not be split). Artem, 2026-11-24 19:31, on the reviewer's
question "Писать ли Stage 2D (QX-2 для Haiku)?": «Да, писать». Money ceiling for Haiku: $72 in all (Artem,
2026-11-24 10:52). Locked after the agent's dry build and the reviewer's review; no call before the lock and
Artem's go, logged verbatim.

## Why

Every model on the page has run QX-2 on the four cells ("rule, result or nothing", world 0): gpt-oss-20b
(entry 1), Luna (entries 2–3), Nemotron with a thinking budget (entry 12), gpt-oss-120b (entry 14). Claude Haiku
5.5 has not, so the one experiment shared by all models has a gap. This stage fills it with the same world,
prompts and schema; only the model changes.

## Design (only the model changes)

As locked in `AMENDMENT_QX2_PHASE1.md` and run for Luna (`AMENDMENT_QX2_LUNA.md`) and the ladder
(`AMENDMENT_QX2_LADDER.md`): world seed 0, G = 12, catalog, prompt bytes (`gen1_B1.txt`, `gen1_B4.txt`), the
strict schema `qx2_cell_decision_v1`, the mapper, retry and fallback rules, protocol, engine invariants and format
gate.

**Claude Haiku 5.5 · four cells: δ 1/64 · B 4, δ 1/8 · B 4, δ 1/8 · B 1, δ 1/64 · B 1 (the Luna order) ·
message: rule, result or nothing · G 12, extended to 24 by the locked rule below · world 0 · one run per cell.**
4 × 1,200 = 4,800 calls for generations 1–12; up to 4,800 more if all four cells are extended.

**Extension to 24 generations (as group B of `AMENDMENT_QX2_CONTINUE24.md`, locked).** After generation 12, a cell's
run is extended to generation 24 if (i) 1 to 99 cells hold H_T at generation 12 and (ii) more cells hold H_T at
generation 12 than at generation 9. The readout script applies the rule to the stored trace and logs its decision
before any generation-13 call. Generations 1–12 are prompted with G = 12; generations 13–24 are rendered with
G = 24, as in that amendment. A run that is not extended ends at 12 and is shown to its last generation, like the
other models' QX-2 runs.

- Decoding as in Haiku Stage 0 (adaptive thinking, effort medium, max_tokens 8192); prompt bytes as rendered for
  Luna's QX-2 run; response format the QX-2 schema, passed as in Luna's QX-2 run.
- Run names `qx2_haiku55_{d64_B4, d8_B4, d8_B1, d64_B1}_r1`; the cache key includes model and arm; no answer is
  shared between arms or with any other stage.
- Reasoning text is not stored (closed model).

## Readout (descriptive, no test)

The items of the ladder readout, per cell: abandonment and recovery beside the scripted references; first
refutation; test descriptives and the δ-share; the message mix, with own and relayed results; refuting results
shared, with senders; the finder breakdown; signal use by message content; calls. One table puts Haiku beside the
other four models per cell. No contrast and no p-value; each cell is one replicate.

## Expectations (stated before the data; descriptive, not tested)

From Haiku's measured profile: at δ 1/8 it finds counterexamples about as often as its tests land on the region
(entries 19, 20), moves on a received counterexample almost always, and attaches its own in about a third of
updating answers (entry 16). So δ 1/8 cells are expected to recover where finders share; at δ 1/64 with B 1,
tests on the region are rare (1.6 % in Stage 2B), so that cell may find nothing in 12 generations.

## Money

Projection = 4,800 (and up to 4,800 more for extensions) × the measured Haiku cost per call at the QX-2 prompt length, from the dry build's token
counts (rough guide: QX-3 prompts gave $0.00064–0.00075 per call, ≈ $3–4 here). Ceiling: Haiku money left before Stages 2C and 2D is $38.91 and Stage 2C's stop is $30.40, so
Stage 2D may spend at most **$8.51** (its stop). Start rule: generations 1–12 of a cell, and each extension, start
only if the spend so far plus 1.5 × that part's projection is at most $8.51; a part not started is reported. **Order: Stage 2D runs before Stage 2C** (smaller, fills the
shared experiment); each has its own go. The page and paper carry no dollar figures.

## Gates

Format gate as locked for QX-2 (more than 4 fallbacks or truncations in the first 400 decisions stops that cell's
arm); API errors retried once, then counted; a run with more than 2 % failed calls is stopped and reported.

## Dry build (CPU, no model call)

0. The extension rule run on the stored traces of the four other models (decisions equal to those logged for
   group B where it was applied).

1. Generation-1 prompts for B 1 and B 4 byte-equal to `gen1_B1.txt` and `gen1_B4.txt`; schema equal to the
   pinned `qx2_cell_decision_v1` as passed in Luna's QX-2 run (mismatch counts).
2. Request bodies for Haiku (decoding above); how the QX-2 schema is passed, compared with Luna's QX-2 request.
3. Four run names with distinct cache keys; a fake-client pass through the engine with every invariant asserted.
4. Token counts (count endpoint) for generation 1, B 1 and B 4, cell 0 and the longest cell; projection for
   1–12 and for the extensions (G = 24 prompts); the start rule against $8.51.

## Outputs

Calls (final text and usage; no reasoning text), traces, the readout, a recheck package with SHA256SUMS. Nothing
enters the page before the reviewer's recheck from raw data; the page entry comes with the four runs in the run
viewer (model group haiku).

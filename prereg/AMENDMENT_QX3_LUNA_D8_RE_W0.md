# Amendment — Luna, δ 1/8, rule plus a chosen result, world 0 (descriptive)

**Status:** draft v1 (2026-11-26), written by the reviewer for Artem. Artem, 2026-11-26 14:33–14:35, on adding rule plus
chosen result for Luna at δ 1/8: «Давай один мир сделаем». Locked after the agent's dry build and the reviewer's review; no
call before the lock and Artem's go, logged verbatim. API only; it touches neither the GPU nor any waiter.

## Why

At δ 1/8 Luna reaches H_T with rule names alone (x̄ 0.99–1.00, entries 7, 8, 10), through its majority step. The core
table therefore has only Luna's rule-only arm in this row. A test "results above rule only" is at its ceiling and is not
run. What one run with results can show is how the population gets there: how fast, and by which route (a received
counterexample, or a majority of neighbours naming H_T).

## Design (only the model changes against Claude Haiku 5.5's entry-19 run in world 0)

**Luna · δ 1/8 · B 1 · rule plus a chosen result · 24 generations · world 0 · one run.** 2,400 calls, run name
`qx3w_luna_d8_B1_RE_w0`. Engine, prompts, schema, world file and message exactly as the rule-plus-result run of entry 19 in
world 0 (Claude Haiku 5.5, `qx3w_haiku55_RE_w0`), and as the worlds engine of entries 8, 13 and 19; decoding as Luna in
entries 7 and 8 (`gpt-6-luna`, reasoning effort medium; no reasoning stored). The rule-only comparison is Luna's world-0 run
of entry 7 (`qx3m_luna_d8_r2`), compared by file hash, not rerun.

## Measures (descriptive; no test)

- x(t), generations 1–24; x̄ (13–24); x̄_nf; finders.
- First generation with x ≥ 0.5 and with x ≥ 0.9, against the rule-only run.
- Route to H_T: for each cell that first names H_T, whether its memory then held a counterexample (own or received), and
  how many of its eight neighbours named a rule other than H_F in the generation before (0, 1–4, 5 or more).
- Messages with a result, with a counterexample, own or relayed.

## Readings stated in advance

| pattern | reading |
|---|---|
| x ≥ 0.9 earlier than rule only; most first H_T holders without own evidence held a received counterexample | Shared results carry the correction ahead of the majority step. |
| same generation as rule only; most first H_T holders had five or more non-H_F neighbours and no counterexample | Luna's route stays the majority step; results ride along. |
| later than rule only | Results slow it down at δ 1/8 (stated as observed). |

One run in one world: these are descriptions, not tests.

## Money (chat and logs only)

2,400 calls at Luna's measured cost per call in its δ 1/8 runs; stop 1.5 ×. Start rule against the Luna authorization: spent
so far + 1.5 × projection ≤ $45 (spent before this run ≈ $42.77). Pages carry no dollar figures.

## Gates, dry build, outputs

Format gate as in entries 8 and 19. Waiter with stdout and stderr in a log file. Dry build (CPU, no call): run name and
cache keys; generation-1 prompts byte-equal to `qx3w_haiku55_RE_w0` (mismatch count; only the model field may differ in the
request); the sha256 of the reused rule-only trace; token counts, projection and start rule; the readout run end to end on a
stub trace. Output: calls (usage, answer text), trace, readout, a package with SHA256SUMS in the same message as the finish.
Nothing enters the page before the reviewer's recheck; the run goes into the run viewer (δ 1/8 · R vs R+E, Luna).
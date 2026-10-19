# Task — Tipping probability and the signal × length interaction (Luna, world 1)

**Status:** locked. Predictions are locked with this file, before any API call. Luna Responses,
`reasoning.effort = medium`, the same settings, prompt, catalog, schema and parser as the controls arms.
Parents: `TASK_LIFE_DR_CONTROLS.md` and its amendments, `runs/life_dr_controls/part0c_report.md`,
`runs/life_dr_controls/part1_readout.md`, the second Google Deep Review, `ARM_REGISTRY.md`.

**Budget:** new and separate from the controls total ($41.55). Alarm at $15, stop at $20 (approved by
Artem). Cost is checked after every round of every run and after every 40 intervention calls.

## Why

1. Part 0c excluded inbox length only with signal 0 written on most rebuilt lines. Publishers put P_e
   on signal 7 almost always, and low-signal opposition is far more permeable than high-signal
   opposition. The reviewer asks whether length interacts with opposition confidence.
2. The claim that `all8exact` tips more often than `all` rests on 3 of 6 against 0 of 6 runs, across
   three worlds. Two replicates per condition cannot bound a tipping probability.

## Part D — signal × length, fixed cell state (≈ $0.45)

Source cells: the same 40 Part 0c cell-rounds (`part0c_selection.json`), class A, fresh P_e holders at
d = 1, pre-tipping. Their own example, query and memory are fixed. Only the inbox is set.

Inbox: P_e lines and prefix lines only, no empty slot, no third rule. Shares 0.25 (2/6 and 22/66) and
0.375 (3/5 and 33/55). Senders, order and formats exactly as in Part 0c.

Two signal conditions:
- **logged:** every P_e line carries signal 7. Each prefix line carries a signal drawn by a fixed hash
  from the empirical distribution of prefix-line signals in the source cell's arm and round (the
  messages published at round t − 1 of that run).
- **zero:** every line carries signal 0.

2 lengths × 2 signal conditions × 2 shares × 40 cells × 2 draws = 640 calls, own cache namespace.
Leave means the parsed rule is a catalog rule other than P_e. Parse failures are counted and excluded.

**Predictions (locked):**
- **D1 (replication of Part 0c's direction):** under zero signals, pooled over shares,
  P(leave | 8 lines) > P(leave | 88 lines). One-sided Fisher, α = 0.05.
- **D2 (the reviewer's interaction):** under logged signals, pooled over shares,
  P(leave | 88 lines) > P(leave | 8 lines). One-sided Fisher, α = 0.05.
- **D3 (P_e loses its confidence):** at 8 lines, pooled over shares,
  P(leave | zero) > P(leave | logged). One-sided Fisher, α = 0.05.
- **Reading.** D2 passes: Part 0c's exclusion of length does not hold at live confidence, and the
  long inbox can pull holders back. D2 fails while D1 passes: the reverse length effect holds at both
  confidence levels, and length stays excluded. D3 tests the candidate explanation for the gap
  between Part 0c and the logs.
- **Descriptive:** all 8 cells of the 2 × 2 × 2 design with Wilson intervals, split by source arm.

## Parts B and C — tipping probability in world 1

World 1 (`P_e = shift_symbols(1);swap(2,3)`, prefix `shift_symbols(1)` fits 75). Arms
`dist/luna.resp-medium/all8exact/none` (B) and `dist/luna.resp-medium/all/none` (C). 8 new replicates
each, r3 to r10. Each replicate starts from round 1 with fresh calls, its own hash salt, its own empty
cache and its own history directory. No cache is shared with any earlier run.

**Tipping** is x(g) ≥ 0.90 at some round g ≤ H.

**Horizon.** B uses H = 20; the earlier `all8exact` tips crossed at rounds 6, 11 and 17. For C, before
any call, the agent computes from all existing `all`-format Luna runs (topology `all`, both replicates,
five worlds; `dist-m60`; `dist-m85`) the latest first round with x ≥ 0.90 among the runs that tipped,
and the largest x reached after that round by any run that did not tip. H_C is that latest round plus
2, at most 20. If any non-tipping run reached x ≥ 0.50 after round H_C − 2, H_C is 20. H_C is committed
with the runner, before any call.

**Order.** C r3, B r3, C r4, B r4, …, so a stop leaves the arms balanced. A stop ends after the current
run; a run cut mid-way is excluded and reported.

**Prediction (locked):**
- **T1:** among the 8 new runs per arm, the tipping count under `all8exact` exceeds that under `all`.
  One-sided Fisher exact on the 2 × 2 table, α = 0.05. Only the new runs are tested, because the old
  world-1 runs helped form the hypothesis. The 10-run counts (old plus new) are reported as
  descriptive, with Wilson intervals.
- **Descriptive:** per run, x(g), the round-2 and round-3 P_e shares, whether P_e was the round-2
  plurality, the first round with x ≥ 0.90, and the prefix-rejection agreement at the last round.
  Whether any early quantity (round-2 plurality, x(3), x(5)) separates tipped from plateau runs is
  reported as post hoc.

## Gates

- New runner with a lock file per run directory; committed before launch; one launch only.
- First-prompt diff: round-1 prompts of each new replicate are byte-identical to the round-1 prompt of
  the same cell in the existing world-1 run of the same arm.
- P_e and the example hash checked every round. EPOCH_LENGTH ≥ 21.
- Part D: the 40 source prompts rebuilt and checked byte-identical to the logged prompts before any
  call, as in the Part 0c audit.
- Cost after every round and every 40 intervention calls. Alarm $15, stop $20. nohup, liveness
  watchdog, no auto-relaunch.

## Order and cost

Part D first (≈ $0.45), report. Then C and B interleaved: about $1.29 per `all8exact` run (8 runs, about
$10.3) and about $0.9 per `all` run at H_C ≈ 10 (8 runs, about $7.2; less or more with H_C). Total about
$18. If the projection after D and H_C exceeds $20, the number of replicates is reduced equally in both
arms before launch, and the new n is written into this file as an amendment before any B or C call.

## Constraints

No reasoning text is requested or stored. Closed-model outputs are not training data. Same prompt as the
existing arms. Edit no running script. Amendments come before numbers. Qwen Stage 1 and its queue are
not touched.
# Amendment — TASK_LIFE_DR_TIPPING: Part F, `all` with per-receiver line order

**Status:** locked before any Part F call. Approved by Artem. Parents: `TASK_LIFE_DR_TIPPING.md`,
`AMENDMENT_DR_TIPPING_REDO.md`, `AMENDMENT_DR_TIPPING_PART_E.md`,
`runs/life_dr_tipping/inbox_order_posthoc.md`.

## Why

`all` is the only topology whose inbox order is shared by every receiver: lines are sorted by sender
id, so about 99 of 100 cells see the same first lines. The lattice, r8, r8q and `all8exact` (above 8
publishers) give each receiver its own hash order. `all` is also the only topology whose false
consensus holds in most runs. Part E showed that line position has a large causal effect: at 88 lines
and share 0.375, holders leave P_e in 3/80 with P_e as a top block and in 55/80 with the lines shuffled.
A shared order makes every cell attend to the same senders, which correlates decisions. Part F removes
that one difference.

## Design

- Arm `dist/luna.resp-medium/allshuf/none`: identical to `dist/luna.resp-medium/all/none` in senders,
  line content, signals, header, slot sentence and prompt. The only change is the order of the inbox
  lines. Each receiver sees the published lines (its own excluded) ordered by
  `sha256("allshuf|{world}|{replicate}|{round}|{receiver}|{sender}")`, ascending.
- World 1, replicates r3–r10 (8 runs), horizon H = 10 as in Part C. Tipping is x(g) ≥ 0.90 at some
  g ≤ 10.
- Each replicate has its own hash salt for the order, its own empty cache, its own history directory,
  and a lock file. One launch. No cache is shared with any other run.
- Control: the 8 Part C runs (`all`, world 1, r3–r10, H = 10), already running under the locked task.

## Gates (before any call)

- Round 1 (empty inbox): every Part F prompt byte-identical to the Part C round-1 prompt of the same
  cell.
- From round 2: for a given receiver and round, the Part F inbox is a permutation of the inbox the `all`
  builder produces from the same published messages; checked on a dry run built from a logged `all`
  round (multiset of lines equal, order different for at least 90 of 100 receivers).
- P_e and the example hash checked every round; EPOCH_LENGTH ≥ 21.

## Prediction (locked)

- **F1:** the tipping count in the 8 Part F runs exceeds the tipping count in the 8 Part C runs.
  One-sided Fisher exact on the 2 × 2 table, α = 0.05.
- **Stated power.** With 8 against 8, F1 can pass only with a large difference (for example 4 of 8
  against 0 of 8, p = 0.038). A smaller difference will be reported as not significant, with the
  counts and Wilson intervals.
- **Descriptive:** per run, x(g), the round-2 and round-3 P_e shares, whether P_e was the round-2
  plurality, the first round with x ≥ 0.90; and the across-cell agreement of decisions within a round
  (share of class-A cells that change rule in the same direction), Part F against Part C.

## Reading

F1 passes: the shared order is a cause of the `all` plateau, and the false consensus rests partly on
correlated attention. F1 fails: the shared order is not shown to matter at this sample size, and the
mechanism of the `all` / `all8exact` difference stays open.

## Order and cost

Part F starts after the intervention redo and the C3 completion have been launched, alongside B/C,
under its own lock and cap of **$10**. About $1.0 per run, $8 in all. Projected task total about $32,
inside the $40 stop. If the combined projection passes $38, Part F's replicate count is reduced
before launch and the new n is written here first.
# Amendment — adoption interventions at 8 and 88 lines (draft, not locked)

**Status:** locked. The dry-build gate passed. Parent: `TASK_LIFE_DR_MICROMODEL.md`. No refit
in this amendment. The calls sit inside the shared Part G + H + I envelope: cumulative spend
stays below $10, and at $10 the run stops and asks.

## Why

The adoption fit has `n_opp` ≤ 8. Live `all` and `allshuf` inboxes are longer, and M1 on that
unrestricted set failed. The test set is densest in (0, 0.25], 16330/35750 rows, where the model
predicts 0.307 against an observed 0.034. The next bin, (0.25, 0.5), is 12373/35750, predicted
0.543 against observed 0.058. This draft puts share 0.125 on both an 8-line inbox and an 88-line
inbox, and keeps the longer shares at 88 lines.

## Population

Class A: the cell's example fits the prefix. The cell is holding the prefix, so it is not holding
P_e. That is the class-A population the adoption model was fitted on.

The population is confirmed: class A, holding the prefix, not holding P_e.

Source arm: `all`. Worlds 1, 2, 3 and 5. World 4's prefix fits no example, and no cell in the
`all` logs holds it. Worlds 1 and 3 use the prefix-signal pools already in the tipping gate.
World 5 is added, and world 2 is added because class-A cells hold its prefix. Each added world
has its own `all` prefix-signal pool, collected by the same replay as the tipping gate: the
signals on prefix lines published at that round. Eligible cells hold the prefix and have a
class-A example, on a round whose pool is non-empty. Take 20, ordered by the same cell hash
Part 0b uses, across that pooled set. Two draws.

## Conditions

Same source prompt. Only the inbox block and the slot-count sentence change. P_e positions are
set by the redo hash. Logged signals: a P_e line has signal 7,
and a prefix line draws from that cell's logged prefix-signal pool. Opposition lines are the prefix
only, so no third rule enters. The 8-line header says `eight message slots`. The 88-line header
says `88 message slots`.

| condition | lines | P_e | prefix | empty | share | n_opp |
|---|---:|---:|---:|---:|---:|---:|
| L8-125 | 8 | 1 | 7 | 0 | 0.125 | 7 |
| empty8 | 8 | 0 | 0 | 8 | — | — |
| L88-125 | 88 | 11 | 77 | 0 | 0.125 | 77 |
| S25 | 88 | 22 | 66 | 0 | 0.25 | 66 |
| S375 | 88 | 33 | 55 | 0 | 0.375 | 55 |
| S625 | 88 | 55 | 33 | 0 | 0.625 | 33 |
| empty88 | 88 | 0 | 0 | 88 | — | — |

11/88 = 0.125. 20 × 7 × 2 = 280 calls. Part I was $0.267 for 480 calls, so this is about $0.16.
Own cache, own lock, one launch. The cap is the cumulative envelope, not a new $10. Cumulative
spend before this draft is $1.32.

## Intended use

Once these calls exist, the adoption model is refitted on the Part 0b redo, the Part E shuffled
adoption rows, and this set. The test is the live adoption rows of `all` and `allshuf` with
`n_opp` > 8. M1 for that refit, full model below B0 and below B1 with the run-level interval
excluding 0, is locked in a separate amendment before the refit. Empty inboxes have no share, so
the same support rule as the current fitter drops empty8 and empty88 from the fit. They stay in
this design as the controls.

## Predictions (locked)

One-sided Fisher, α = 0.05. The scored unit is the cell: 20 cells, two draws summarized as a cell
rate. A call-level Fisher is reported beside it and is not the scored test.

- **A1.** At 88 lines, P(adopt P_e | S625) > P(adopt P_e | S25).
- **A2.** At 88 lines, P(adopt P_e | S25) > P(adopt P_e | empty88). The same comparison at S375
  and at S625 is descriptive.
- **Descriptive, the widened cells.** At each length, P(adopt P_e | share 0.125) against the empty
  inbox of that length. These are the low-share cells. They are not the scored tests.
- **Pass.** Adoption at 88 lines responds to the P_e share, and the low share is above an empty
  inbox. The long-inbox gap is then a place the model had no fit data.
- **A1 fails and A2 passes.** A long inbox of prefix lines already lifts adoption, and raising the
  P_e share from 0.25 to 0.625 adds nothing detectable at 20 cells.
- **A2 fails.** The filled 88-line inbox does not beat silence. Share on a long inbox is not, by
  itself, an adoption treatment relative to no message.
- **If the design is the cause.** The inbox contains only P_e and the prefix, at a fixed length, in
  redo order. A live `all` inbox has a variable length and other rules. A pass here does not say
  the live long inbox works the same way.

## Design audit

1. **Fidelity to live data.** The source prompt is a logged `all` prompt for that cell and round.
   Replaced: the inbox block and the slot-count sentence. Kept: the example, the query, the
   one-step memory line, and the rest of the constitution. Differences from the live inbox, all
   deliberate: length fixed at 8 or at 88; every filled line is P_e or the prefix; P_e signals are
   7 rather than the sender's logged signal; prefix signals are redrawn from the logged pool; P_e
   positions follow the redo hash rather than the live order. Senders are the first 8 or the first
   88 other cells in the redo's sender order. An `all` prompt says `N message slots`; the 8-line
   conditions replace that with `eight message slots`, and the 88-line conditions with
   `88 message slots`. Empty8 and empty88 replace every slot with `empty`.
2. **Coverage.** The population is confirmed. On the grid as written:
   L8-125 has `n_opp` = 7, inside the fit maximum of 8, and share 0.125, one of the eight shares
   the fit actually used. It is the in-range anchor for (0, 0.25], the bin with 16330/35750 test
   rows, observed 0.034 against predicted 0.307. L88-125 has `n_opp` = 77 and the same share, so
   that bin is also measured at a length the fit never saw. S25, S375 and S625 have `n_opp` 66, 55
   and 33. S375 is share 0.375, inside (0.25, 0.5), the other dense bin (12373/35750, observed
   0.058 against predicted 0.543). S625 is above one half. Empty8 and empty88 have no filled line.
   Eligible rounds after the pool filter: 2304. By world, 1 has 463, 2 has 88, 3 has 215, 5 has
   1538. World 2 has class-A holders (249 before dropping empty pools) and its own pools, and the
   hash draws none of them. The 20 cells are worlds 1 (5), 3 (2) and 5 (13).
   The live adoption rows the refit reads are `all` replicates 1–2 in worlds 1–5, `all`
   replicates 3–10 in world 1, and `allshuf` replicates 3–10 in world 1. World 4 has no cell
   holding its prefix, so it contributes no adoption row. World 2 is in that test frame and not
   in these 20 cells. Part 0b and Part E, the other adoption fit sources, are worlds 1 and 3.
   This set adds world 5. World is not a feature of the model.
3. **Controls.** Yes. Empty8 is the 8-line header with no
   message. Empty88 is the 88-line header with no message. Within a length, the filled conditions
   share order, signals, and rule types, and differ in the P_e count.
4. **Observability.** Yes. Share, signals, line count, and the example are in the prompt. The
   predictions do not use holding time. Memory stays the logged one-step line.
5. **Gate consistency.** Yes. The dry build is `runs/life_dr_micromodel/adopt88/gate.json`. Outside
   the inbox, the slot sentence, the line counts, the empty inboxes, the rule names, the P_e
   signal 7, and the call count 280 all hold. P_e positions are set by the redo hash. Per
   condition, the number of inboxes whose P_e lines form a block starting at slot 1, against the
   expectation under uniform placement (one subset in C(n_lines, n_pe), 20 inboxes): L8-125 is
   2 against 2.5, upper bound 5; L88-125, S25, S375 and S625 are 0 against an expectation near 0,
   upper bound 0. The 95% bound is the 0.95 quantile of that binomial. None exceeds it.
6. **Statistical unit.** Yes. The scored unit is the cell, 20 cells. The call-level Fisher is
   beside it and is not scored.
7. **Pre-stated readings.** Yes. The branches are under Predictions, including the reading in
   which the cleaned inbox, rather than the live channel, produces the result.

# Amendment — TASK_LIFE_DR_CONTROLS: Part 0c

**Status:** locked. Written before any Part 0c call. Parent: `TASK_LIFE_DR_CONTROLS.md`.

Part 0c holds the inbox share fixed and changes the inbox length. It does not change Part 1, Part 2, or Part 3.

## Pool

Worlds 1, 3 and 5, replicates 1 and 2, from the closed `all8exact` runs and the closed `all` runs. Decision rounds 2–20.

An eligible cell is one cell at one round. The same cell at another round is a different eligible cell.

The cell's own example fits the prefix: the prefix, the first operation of P_e, is in its cofiting list. Entering the round it holds P_e at holding time d = 1. d is the Part 0.2 count: consecutive rounds on P_e ending at the previous round. d = 1 means it holds P_e entering this round and did not hold P_e entering the previous round. At round 2 every holder has d = 1.

The previous round's published P_e share is below 0.5. That share is P_e messages divided by all messages published in the previous round. For `all8exact` it is `published_counts` on the previous round. For `all` it is the longest inbox at this round, because a non-publisher sees every published line. A round with no published messages is not eligible.

## Hash

`sha256("part0c-cell|{arm}|{replicate}|{world}|{round}|{cell}")`, hexadecimal, ascending. Within each arm, the first 20. If an arm has fewer than 20, all of its eligible cells are taken and n is reported. No other ranking.

## Inbox

Four conditions. The two numbers are P_e lines and prefix lines. Every other line is the prefix. No third rule and no empty slot.

| condition | P_e lines | prefix lines | lines | format |
|---|---:|---:|---:|---|
| L8-25 | 2 | 6 | 8 | `all8exact` |
| L88-25 | 22 | 66 | 88 | `all` |
| L8-375 | 3 | 5 | 8 | `all8exact` |
| L88-375 | 33 | 55 | 88 | `all` |

L8-25 and L88-25 are share 0.25. L8-375 and L88-375 are share 0.375.

Senders are the other 99 cells. Their order is the ascending `sha256("part0c-order|{arm}|{replicate}|{world}|{round}|{cell}|{sender}")`. The condition is not in the hash, so the 8 senders are the first 8 of the 88. In that order, the first P_e-count slots say P_e and the rest say the prefix.

The generation on every line is the generation on the original lines of that source prompt. Selection stops with no call if those original lines do not all carry one generation. The signal is the signal on the original line from that sender. A sender with no original line has signal 0.

The 8-line format uses the header `Visible messages (8 slots):` and the slot sentence `eight message slots`. The 88-line format uses the header `Visible messages (88 slots):` and the slot sentence `88 message slots`. The source cell keeps the rest of its own prompt. The sentence replacement is exactly one occurrence.

## Calls

Two draws per cell per condition. The draw is only a cache-key disambiguator, as in Part 0b. With 20 cells from each arm the total is 4 × 40 × 2 = 320. The selection file records the actual total before any call.

The cache directory is `cache_part0c`. It is not a cache of any other arm.

The request is the Part 0b structured call. The schema tells the model not to return reasoning text. The report stores the catalog key, the rule it names, and the usage. It does not store reasoning text.

Cost is checked after every 40 completed calls. The Part 0c stop is $1.50. At or above that amount the next batch does not start. A stopped run is reported as stopped, and P1 and P2 are not scored.

## Scoring

Leave means the parsed rule is a catalog rule and it is not P_e. A call with no catalog rule is a parse failure. Parse failures are counted and are excluded from n, from the rates, and from the Fisher tables.

Intervals are Wilson score intervals with z = 1.96.

- **P1.** P(leave | L88-25) > P(leave | L8-25), one-sided Fisher exact, α = 0.05, both source arms and both draws pooled.
- **P2.** P(leave | L88-375) > P(leave | L8-375), the same test.
- **Reading.** Both pass: the long list pulls fresh holders back at equal share, and the `all8exact` / `all` difference has a causal length component. Neither passes: the observed outflow difference is attributed to selection by adoption path and share-within-bin, and the mechanism is recorded as open. One of two is mixed.
- **Descriptive.** Leave rates split by source arm, at each of the four inboxes.

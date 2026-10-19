# Amendment — TASK_LIFE_DR_CONTROLS: Part 0b selection

**Status:** written before any Part 0b call. Parent: `TASK_LIFE_DR_CONTROLS.md`.

## Pool

Worlds 1 and 3, replicates 1 and 2, decision rounds 3–8, pinned DRc logs. A cell is eligible
when the rule it holds entering the round is not P_e. That rule is the logged rule of the
previous round. Class A also requires that the prefix is in S_c and that the held rule is the
prefix. Class B also requires that the prefix is not in S_c and that the held rule is not the
prefix. S_c is the cofiting list in the world audit.

## Hash

`sha256("part0b-cell|{replicate}|{world}|{round}|{cell}")`, hexadecimal, ascending. The first
20 of each class. No other ranking.

## Inbox

The eight senders are the cell's Moore neighbours. Their order is the ascending
`sha256("part0b-order|{replicate}|{world}|{round}|{cell}|{condition}|{sender}")`.

The generation on every filled line is the generation on the original lines of that prompt.
If the original inbox has no line, it is the previous round's generation index.

The signal on a filled line is the signal on the original line from that same sender. If that
sender has no original line, the signal is 0.

In that shuffled order, the first `n_pe` slots say P_e, the next `n_prefix` slots say the
prefix, and the remaining slots are empty.

## The eleventh condition

The task names ten conditions. I2 compares "1 P_e line, 7 empty" with "1 P_e line, 7 prefix
lines". The second is not among the ten: the filled list goes from 0/8 to 2/6. It is added as
condition `1/7`, so I2 is the comparison the task wrote. The ten named conditions are
unchanged. The calls are 11 × 40 × 2 = 880.

## Cache

A new directory named `cache_part0b` under the controls run. It is not a cache of any other arm.

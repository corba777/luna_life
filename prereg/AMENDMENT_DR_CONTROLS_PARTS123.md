# Amendment — TASK_LIFE_DR_CONTROLS: Parts 1, 3 and 2

**Status:** written before any Part 1, Part 3 or Part 2 call, and before the Part 3 world audit.
Parent: `TASK_LIFE_DR_CONTROLS.md`.

The predictions, the worlds, the budgets and the order are the ones in the task. This file only
fixes the sampling and the placement the task leaves unnamed.

## Part 1 — eight lines

The inbox is always eight slots. The constitution sentence stays "eight message slots". The
header is `Visible messages (8 slots):`.

Round 1 has no publishers. All eight slots are empty.

When the previous round has 8 or fewer publishers, those publishers are shown in ascending
sender id, as in `all`, and the remaining slots are empty.

When it has more than 8 publishers, eight lines are built as follows. Let n(r) be the number
of publishers of rule r, and N their total.

- Each rule is assigned floor(8 · n(r) / N) lines.
- The leftover lines, one at a time, go to the rules with the largest fractional parts
  8 · n(r) / N − floor(8 · n(r) / N).
- An equal fractional part is broken by the ascending sha256 of
  `all8exact-r{replicate}|{world}|{round}|{cell}|tie|{rule}`.
- The lines of a rule are that many of its publishers, the ones with the smallest sha256 of
  `all8exact-r{replicate}|{world}|{round}|{cell}|pub|{sender}`.
- Those eight lines are then ordered by the ascending sha256 of
  `all8exact-r{replicate}|{world}|{round}|{cell}|order|{sender}`.

`round` is the 1-indexed decision round. The two replicates use different salts, so the
samples differ. Each replicate has its own cache and makes its own calls. A sibling cache
file is never opened.

Plurality for C1 and C2 is the unique most common rule among the messages published at
round 2, counted once per publisher from the decisions of that round. A tie means P_e is
not the plurality. The eight-line sample is not the count.

The task spend is the Part 0b cache plus the caches of these parts. Alarm at $45. Stop at $55,
checked after every round.

## Part 3 — where the prefix is ruled out

World 1 places the examples that rule its prefix out on 25 cells: the stride lattice in
`life_verify/distributed.py` (`draw_world`). Those cell ids, sorted, are the lattice.

- `dist-m60` rules the prefix out on all 25 lattice cells and on the 15 lowest non-lattice
  cell ids. The prefix then fits 60 cells.
- `dist-m85` rules the prefix out on the 15 lowest lattice cell ids. The prefix then fits
  85 cells.

Every other cell gets an example the prefix fits. The pools are world 1's: an example that
rules the prefix out, or an example the prefix fits. `random.Random` is seeded by
`(20261013, "dr-controls-part3", name)`. The hidden rule is world 1's rule.

A draw is kept when every example fits P_e, every cell has |S_c| ≥ 3, the intersection of
all S_c is exactly {P_e}, and no catalog rule other than P_e fits more cells than the
prefix. Those are the constraints in the task. The world-1 neighbour check is not an extra
filter: with 15 exclusions it does not cover every neighbourhood, so it would reject every
`dist-m85` draw. The audit records the fit count of every catalog rule, |S_c| for every
cell, and the intersection. It is committed before any Part 3 call. If no draw passes,
Part 3 is not launched.

## Part 2 — the two graphs

`r8` replicate 3 redraws eight senders every round. The rank is the sha256 of
`{PHONE_SEED}|r3|{world}|{generation}|{cell}|{sender}`, with `PHONE_SEED` 20261016 and
`generation` the decision round. Replicates 1 and 2 stay on the hash that has no replicate
field.

`r8q` draws eight senders once per cell, uniformly without replacement from the other 99,
and keeps them for all 20 rounds. The rank is the sha256 of
`{PHONE_SEED}|r8q|r{replicate}|{world}|{cell}|{sender}`. The two replicates are independent.
Round 1 is an empty inbox on both arms.

C3 is the mean over the five worlds of (x_r1 − x_r3)² / 2 at round 20.

C4 compares, in worlds 1, 3 and 5, each r8q replicate's first round with x ≥ 0.90 to the
first round where the mean of the two lattice replicates has x ≥ 0.90. A run that never
reaches 0.90 inside its logged window is slower than a lattice mean that does. The six
comparisons are reported as counts. They are not a scored test.

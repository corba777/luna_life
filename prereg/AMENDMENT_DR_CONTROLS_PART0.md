# Amendment — TASK_LIFE_DR_CONTROLS: Part 0 mechanics

**Status:** written before any Part 0 number. No API calls. Parent: `TASK_LIFE_DR_CONTROLS.md`.

The update rule, the bins, the domain cut and the two nulls are the ones in the task. This file
only fixes the cases the task leaves unnamed, so the program is determined before it runs.

## 0.1 Rule agent

- S_c is the cofiting list in the world audit.
- Round 1 is the logged rule of the matching run. The inbox is empty, so the update rule keeps it.
  The agent then runs rounds 2–20. x(g) is the share holding P_e after round g.
- A visible line is one stored say. Empty slots are not lines.
- A rule has a strict majority when twice its line count exceeds the number of visible lines.
  At most one rule can. It is adopted only if it is in S_c.
- Otherwise the cell keeps its rule when that rule is in S_c.
- Otherwise it takes the most frequent visible rule that is in S_c. A tie keeps the current rule
  when the current rule is one of the tied rules, and otherwise takes the lexicographically
  smallest rule string. If no visible rule is in S_c, the cell keeps its rule.
- Moore senders are the eight torus neighbours. r8 senders are `r8_peers(world, round, cell)`
  with `PHONE_SEED` 20261016, the same schedule as the logged run. `all` senders are the other 99.
  A sender contributes one line when it published, and the line is the rule it held.
- Variant (a) publishes every cell every round.
- Variant (b), 100 runs per logged run. The probability depends on the topology, the round and
  whether the cell holds P_e. It is pooled over both replicates and all five worlds of that
  topology. On moore and r8 it is (P_e lines in the inboxes) / (P_e-holding senders in those
  peer sets), and the same ratio for lines that are not P_e. On `all` the publisher multiset is
  the one reconstructed from the next inbox, and the ratio is publishers of that class over cells
  of that class. A class with no cells has probability 0. Draws use one numpy Generator(0) per
  topology, in the order replicate, world, run index, round, cell.
- Comparisons with the LLM use rounds 1–20 of the logged run, including the count of false
  domains. The 30-round domain count is a different window and is not the comparator.
- The modal wrong rule is the most common rule among cells not holding P_e. A tie takes the
  lexicographically smallest. Prefix-rejection agreement is the share of cells for which
  "does not hold that rule" and "the rule is not in S_c" are the same answer. If every cell
  holds P_e the modal rule is undefined.
- Replicate-style variance of (b) pairs run index i of replicate 1 with run index i of
  replicate 2, takes the mean over i of (x¹ − x²)² / 2 in each world, then the mean over worlds.

## 0.2 Holding time

d at round g is the number of consecutive rounds ending at g−1 on the rule the cell holds
entering g. A switch is a different rule at g. Bins are d = 1…10 and d > 10, split by whether
the held rule is P_e. Moore uses rounds 2–30. r8 and all use rounds 2–20. Intervals are a
cluster bootstrap over world × replicate × cell, 2000 draws, seed 0, restarted per topology.

## 0.3 Avalanches

Synchrony counts every cell that switches to the same new rule in the same round. A spatial
avalanche is an 8-connected component of those cells. Both are computed on all three topologies.
The windowed null is the one already used: windows of three rounds, the per-window switch count
fixed, new-rule labels kept in time order, 1000 permutations, seed 0. The position null keeps
the number of switches to each rule in each round and places them on random cells that did not
already hold that rule. Rules are placed in lexicographic order, without reusing a cell. A round
that runs out of eligible cells is redrawn. Seed 0 is restarted per topology and per null.
The reported p-value is (b + 1) / (B + 1), with b the number of permutations whose statistic is
at least the observed one. The statistics are the mean, the 99th percentile and the maximum
avalanche size.

## 0.4 Boundary exposures

A qualifying domain is a false domain on moore with maximum size at least 5 and lifetime at
least 10, on the rounds 1–30 logs. At each round g of its life, each of its boundary cells is
an exposure when the inbox at g+1 contains at least one P_e line. The cell switches when its
rule at g+1 differs. The share bins are the bins in `adopt_by_share.md`. The population curve
next to it is P(adopt P_e | bin) on moore, rounds 2–20, for cells not holding P_e.

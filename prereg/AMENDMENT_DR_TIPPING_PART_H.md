# Amendment — TASK_LIFE_DR_TIPPING: Part H, does compositional completion generalize across worlds

**Status:** locked before any Part H call. Approved by Artem: Part G and Part H together, and any
further Luna call in this task, run without a new go while their cumulative spend stays below **$10**;
above that, stop and ask. Parents: `AMENDMENT_DR_TIPPING_REDO.md`, `AMENDMENT_DR_TIPPING_PART_G.md`,
the third Google Deep Review.

## Why

The package says the LLM adds compositional discovery over a rule agent: a cell whose own example
rules the prefix out, shown only prefix lines, answers P_e (Part 0b redo: 20/40 under 0/8). All class-B
cells came from world 3, because the Part 0b selector covered worlds 1 and 3 only and world 1 had no
eligible cell-round. Part H tests worlds 1, 2 and 5, with world 3 rebuilt the same way as a calibration.

## Cells

- Worlds 1, 2, 3 and 5. World 4 is excluded: its prefix `reverse` fits 0 of 100 examples, so "rules
  the prefix out" does not define a class there.
- Class B: the cell's own example rules out the first operation of that world's P_e. Each such world
  has 25. Twenty per world by the ascending hash `sha256("partH|{world}|{cell}")`.
- Source prompt: that cell's logged round-4 prompt from the pinned DRc replicate 1 history (lattice,
  8 slots). Its own example and query are kept.
- Memory line: replaced with `Previous step: rule='<R>' published=no`, where R is the rule of the
  cell's S_c that is neither P_e nor the prefix with the smallest hash
  `sha256("partH-mem|{world}|{cell}|{rule}")`. (|S_c| ≥ 3 and the prefix is outside S_c, so R exists.)
  This is a constructed state; the readout says so.

## Inbox conditions (8 slots, real Moore neighbour ids, redo order)

- **empty8:** all 8 slots empty.
- **pre8:** 8 prefix lines.
- **pe1pre7:** 1 P_e line and 7 prefix lines; the P_e position is chosen by the redo hash.

Prefix-line signals are drawn by the Part D hash from the source round's prefix-signal pool of that
world's DRc run (signal 7 if that pool is empty); the P_e line has signal 7. Generation = 3.

4 worlds × 20 cells × 3 conditions × 2 draws = 480 calls. Own cache `runs/life_dr_tipping/part_h/cache`,
own lock, one launch. Projected about $0.3.

## Gates (before any call)

- Outside the memory line and the inbox block, every prompt is byte-identical to its source prompt.
- In every pre8 and pe1pre7 inbox the prefix string is that world's first operation of P_e.
- The memory rule R fits the cell's own example and is neither P_e nor the prefix.

## Predictions (locked)

Answer = the parsed catalog rule. One-sided Fisher, α = 0.05; beside it, the cell-level paired
sign-flip test and a cluster bootstrap over cells (2000 draws, seed 0), reported, not scored.

- **H1 (prefix lines help completion, new worlds):** pooled over worlds 1, 2 and 5,
  P(answer P_e | pre8) > P(answer P_e | empty8).
- **H2 (the filter holds):** pooled over all four worlds, the share answering the prefix under pre8 is
  ≤ 0.08 (the same bound as I3).
- **Descriptive:** every world × condition cell with Wilson intervals; world 3 rebuilt against the real
  Part 0b redo class-B rate (20/40 under 0/8); world 2 read against the catalog-spelling question
  (whether its P_e is reachable by composing the prefix with a swap the cell can name).

## Reading

H1 passes: completion from a false partial rule is not a world-3 property. H1 fails: the claim stays
limited to world 3, and the package says so. A world-3 rebuild far from 20/40 means the constructed
memory changes behaviour, and the new-world results are read with that caveat.
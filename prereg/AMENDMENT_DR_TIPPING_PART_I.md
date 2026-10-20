# Amendment — TASK_LIFE_DR_TIPPING: Part I, where the own-example filter fails

**Status:** locked before any Part I call. Approved by Artem; inside the shared Luna envelope of this
task (run without a new go while cumulative Part G + H + I spend stays below $10; at $10, stop and ask).
Parents: `AMENDMENT_DR_TIPPING_PART_H.md` and its readout.

## Why

Class-B cells (own example rules the prefix out) still answer the prefix in world 1, in live runs
(1–10% of cell-rounds, by topology) and in Part H, where an empty inbox already gives 9/40. In worlds
2, 3 and 5 the same rate is near 0 (Part H empty inbox: 0/40 in each). With no message in the inbox,
this is an error of checking the rule against the example, not conformity. World 1's P_e is
`shift_symbols(1);swap(2,3)`: the prefix differs from it by swapping two adjacent positions. World 3
(`shift_symbols(6);swap(1,3)`) and world 5 (`shift_symbols(1);swap(0,3)`) differ by a non-adjacent swap.
Part I varies only that difference.

## Design

- Rule pairs: true rule `shift_symbols(k);swap(i,j)` against the prefix `shift_symbols(k)`, for
  k ∈ {1, 6} and every pair (i, j) ∈ {(0,1), (1,2), (2,3), (0,2), (1,3), (0,3)}: 12 pairs.
  Adjacent: (0,1), (1,2), (2,3). Non-adjacent: (0,2), (1,3), (0,3).
- Examples: for each pair, 20 inputs over A–H drawn by the hash `sha256("partI|{k}|{i}|{j}|{n}")`,
  kept only if the two swapped positions differ after the shift (so the prefix does not fit). The
  output is the true rule applied to the input. The same 20 base inputs are reused across pairs where
  the constraint allows, to keep the example pool comparable.
- Prompt: the logged round-1 prompt of one fixed source cell (pinned DRc replicate 1, world 1, cell 0):
  empty inbox (8 empty slots), memory `Previous step: none.`, its own query. Only the example line is
  replaced. Round 1 has no social information, so any prefix answer is a checking error.
- 12 pairs × 20 examples × 2 draws = 480 calls. Own cache `runs/life_dr_tipping/part_i/cache`, own lock,
  one launch. Projected about $0.3.

## Scoring

The parsed rule is mapped to its function on (A–H)^4. **Prefix answer:** the function equals
`shift_symbols(k)`. **Consistent answer:** the function maps the example input to its output.
**True answer:** the function equals the true rule. Parse failures are counted and excluded.

## Gates (before any call)

- Every prompt is byte-identical to the source prompt outside the example line.
- For every example, the prefix does not fit and the true rule does.

## Predictions (locked)

One-sided Fisher, α = 0.05; beside it, a by-example paired comparison where the same base input serves
both groups (reported, not scored).
- **I1 (adjacency):** pooled over k, P(prefix answer | adjacent pairs) > P(prefix answer | non-adjacent
  pairs).
- **I2 (world 1 against world 5):** at k = 1, P(prefix answer | (2,3)) > P(prefix answer | (0,3)).
  Basis: live class-B prefix holding, world 1 against world 5, on every topology.
- **Descriptive:** the 2 × 6 table of prefix, consistent and true answers with Wilson intervals; the
  effect of k at fixed (i, j); the true-answer rate by pair (a no-social-context discovery baseline).

## Reading

I1 passes: the model's check of a rule against its example misses adjacent swaps, and the world-1
filter failure is a checking limit rather than conformity. I1 fails while I2 passes: the failure is
specific to some pairs; the 2 × 6 table says which. Both fail: the world-1 failure is not explained by
the swap type at round 1, and conformity or state (memory, later rounds) stays a candidate.

## Qwen

QI-I: the same 480 prompts on Qwen after QI-H, with I1 and I2 re-locked in a short amendment committed
before any QI-I call. Local, pre-approved.
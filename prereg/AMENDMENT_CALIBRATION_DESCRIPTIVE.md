# Amendment — descriptive metrics on the calibration task

**Parent:** `TASK_LIFE_CALIBRATION.md`  
**Status:** locked before the inbox-reconstruction gate and before any of the numbers below.  
**Unchanged:** the choice-model features in Part 2, and the pass rules D1–D3 and R1–R4. No Phone data enters any fit. Part 3 stays a retrodiction.

## Why

Part 0 found no synonym of P_e, so J stands. These metrics describe the cells' information and the false-lock modals. They are not estimators and they do not change a locked contrast.

## Information deficit

For each non-source cell, `|R(x)|` is the number of catalog rules consistent with that cell's own example, and the report includes `log2 |R(x)|`. Sources are excluded: their examples are identifying, so `|R(x)| = 1` by construction. The distribution is per world (the examples do not depend on the arm).

**After the filter (check arms only).** Mean, over non-source cells and generations 2–10, of the number of distinct inbox rules that survive that arm's filter. Generation 1 has no prior publications. Survival is the arm's own rule:

- R8c and Allc: a message survives when `PhoneCompleter._build_inbox` keeps it (`engine_ok` on the cell's examples). Failures are dropped before the choice.
- Da-r: the Moore inbox is not dropped. A rule survives when the engine check on the cell's k=1 example is consistent. Non-sources have one example, so that mark is `engine_ok` on the cell's only example.

## Partial agreement of non-P_e modals

For each false-lock or non-P_e modal rule listed in Part 0, apply the modal and P_e to every unique example input in that world. Agreement is the fraction of (input, position) pairs whose symbols match, plus the four position-wise fractions. A rule is a single op of P_e when its description equals one operation in P_e's program.

## Feedback against conformity

`rule_history` does not store own feedback. Recompute it as the engine does: the query is `decode_seq` of the world-seeded draw at that cell and generation, and feedback is wrong when the held rule and P_e disagree on that query.

Cells: non-sources holding the false-lock modal at generations 8, 9, and 10, in Phone All worlds 1–2 and Ca-r world 2. Report the fraction whose feedback at that generation was wrong. Retention into the next generation uses generations 8 and 9 only; generation 10 has no next row. The retained fraction is among the cells whose feedback was wrong.

## Commutation column

Every per-world table gains a column: whether that world's P_e has two operations that commute. World 2 is the only non-commuting P_e among the five. Any reading of that column is post hoc, n = 1.

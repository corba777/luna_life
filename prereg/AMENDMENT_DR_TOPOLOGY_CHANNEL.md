# Amendment — TASK_LIFE_DR_TOPOLOGY: what a cell sees

**Status:** written before Part A and before any API call. Parent: `TASK_LIFE_DR_TOPOLOGY.md`
(committed `2be4c22`, public mirror `6e74008`).

## What was wrong

The task said that each DRc cell sees 9 examples: its own and its 8 Moore neighbours'. That is
false. The agent checked the code (`run_life_dr_clean_ext_pinned.py` builds the observation with
`examples=sim.examples[cid]`; `_apply_world_examples` stores one `(input, output)` pair per cell)
and a saved prompt (world 1, cell 1, round 2: one line under `Private examples:`, then
`Visible messages (8 slots):`). Nine examples belong to DRo and DRo-iter, which have no inbox.

The error was the reviewer's, in the task text. The gate caught it before any spend.

## What changes

- Each cell sees **its own single private example**, its query, its one-step memory and its inbox,
  exactly as in DRc. Only the inbox changes:
  - `r8`: 8 slots, filled by the cell's 8 senders from the committed `PHONE_SEED` graph;
  - `all`: the rules of the other 99 cells.
- The "Channel content" paragraph under Arms is replaced by the line above. The reason given there
  for rejecting the other design (`all` would hand every cell 100 examples) no longer applies,
  because no examples travel on any channel.
- The prompt diff check stays as written: against DRc round 1, the only allowed difference is the
  inbox block. The private-example block must be byte-identical.

## What does not change

Part A, the gate, the predictions T1–T3, the noise test, the cost caps ($15 alarm, $20 stop) and
the order of work. The adoption and keep tables were measured on DRc as it actually ran, with one
private example per cell, so they apply to the r8 and all arms without change.
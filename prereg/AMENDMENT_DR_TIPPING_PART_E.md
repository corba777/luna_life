# Amendment — Part E, order of the P_e lines (Luna)

**Status:** locked. Predictions are locked with this file, before any Part E call. Parents:
`TASK_LIFE_DR_TIPPING.md`, `AMENDMENT_DR_CONTROLS_PART0B.md`, `AMENDMENT_DR_CONTROLS_PART0C.md`,
`runs/life_dr_tipping/part_d_inbox_audit.md`.

**What was wrong.** Parts 0b, 0c and D place the rebuilt P_e lines in a contiguous block at the top of
the inbox. The logged inboxes do not. Class-B discovery under 0/8 and I3 have no P_e line, so they are
unaffected. I1, I2, the class-A curve, the length contrasts and D3 were measured with a top block.

## Design

Luna Responses, `reasoning.effort = medium`, the same prompt, catalog, schema and parser. Own cache
`runs/life_dr_tipping/part_e/cache`. Own lock `runs/life_dr_tipping/part_e/writer.lock`. The running
C/B process is not touched, and this cache is outside the directory that process scans.

**Order arm.** The 40 Part 0c/D source cells. Logged signals as in Part D: every P_e line has signal 7,
and each prefix line's signal is drawn by the Part D hash from that source round's prefix-signal pool.
Share 0.375 only (3/5 on 8 lines, 33/55 on 88 lines). Two orders:

- **top:** the Part D block, P_e lines first;
- **shuffled:** the same lines, permuted by a fixed hash of arm, replicate, world, round, cell and
  condition.

4 conditions × 40 cells × 2 draws = 320 calls. Leave means a parsed catalog rule other than P_e.
Parse failures are counted and excluded.

**Class-A arm.** The 20 Part 0b class-A cells. Conditions 3/5 and 5/3 only, with the Part 0b signals
and senders, in shuffled order. 2 × 20 × 2 draws = 80 calls. Adopt means the parsed rule is P_e.

## Predictions

- **E1.** At 88 lines, pooled over source arms, P(leave | shuffled) > P(leave | top block). One-sided
  Fisher, α = 0.05. Basis: the `all`-origin identity replay leaves in 29/40 = 0.725 on the real
  interleaved inboxes, against 1/40 = 0.025 in the Part D top-block cell at 88 lines, logged signals,
  share 0.375.
- **E2.** Class A, shuffled order, P(adopt | 5/3) > P(adopt | 3/5). One-sided Fisher, α = 0.05. This
  is I1 under the corrected order.
- **Descriptive, not a prediction.** The length contrast under shuffled order, P(leave | 8 lines)
  against P(leave | 88 lines), with a two-sided Fisher p, pooled and by source arm. The two-sided p is
  twice the smaller one-sided tail, capped at 1.

## Cost

Part E stops at $0.30, checked after every 40 calls. A batch that finishes over the cap is kept and
no further batch starts. This cap is separate from the C/B stop.

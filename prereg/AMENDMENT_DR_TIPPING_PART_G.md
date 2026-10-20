# Amendment — TASK_LIFE_DR_TIPPING: Part G, whose confidence holds the holder

**Status:** locked before any Part G call. Approved by Artem, with a Part G cap of **$10**. This lifts the
API freeze for Part G only. Parents: `TASK_LIFE_DR_TIPPING.md`, `AMENDMENT_DR_TIPPING_REDO.md`,
`runs/life_dr_tipping/final_readout.md`.

## Why

D3 (and D3r) set every line to signal 0 against logged signals, so it moves two things at once: the
confidence on the P_e lines (logged: 7) and the confidence on the opposing lines (logged: mostly 1, 6 or
7). The live logs point both ways: low-signal opposition is more permeable to P_e adoption (0.066
against 0.008 in the (0, 0.25] bin), which predicts that zeroing the opposition should help P_e; yet
zeroing everything made holders leave more. Part G separates the two.

## Design

- Source cells: the 40 Part 0c/D cells (`part0c_selection.json`), class A, fresh P_e holders at d = 1.
- Construction: exactly the redo construction (`AMENDMENT_DR_TIPPING_REDO.md`): which sender positions
  carry P_e is set by the redo hash, not a top block. Lengths 8 and 88; shares 0.25 and 0.375; P_e and
  prefix lines only.
- Signals, 2 × 2:
  - P_e lines: **7** or **0**;
  - opposing (prefix) lines: **logged** (drawn by the Part D hash from the source round's prefix-signal
    pool) or **0**.
- 4 signal conditions × 2 lengths × 2 shares × 40 cells × 2 draws = 1280 calls. Own cache
  `runs/life_dr_tipping/part_g/cache`, own lock, one launch, cap $10 (projected about $0.8).
- Leave means a parsed catalog rule other than P_e. Parse failures are counted and excluded.

## Gates (before any call)

- The (P_e 7, opposition logged) cells reproduce the redo D-logged prompts byte for byte; the
  (P_e 0, opposition 0) cells reproduce the redo D-zero prompts byte for byte.
- In every prompt, only the signal values differ across the four signal conditions of one cell,
  length and share.

## Predictions (locked)

Pooled over lengths and shares; one-sided Fisher, α = 0.05.

- **G1 (own confidence):** with opposition logged, P(leave | P_e at 0) > P(leave | P_e at 7).
- **G2 (opposition confidence):** with P_e at 7, P(leave | opposition logged) > P(leave | opposition at 0).
  Basis: the live logs, where low-signal opposition is more permeable.
- **Descriptive:** all 16 cells with Wilson intervals, by source arm; the interaction (G1 effect at
  opposition 0 against at opposition logged); the length contrast inside each signal condition; and
  the replication check that (0, 0) against (7, logged) reproduces the redo D3r direction.

## Reading

G1 passes, G2 fails: P_e's own confidence holds its holders; the opposition's confidence does not
matter at fixed share. G2 passes, G1 fails: the opposition's confidence is what pulls holders off. Both
pass: both matter; the descriptive interaction says whether they add. Neither passes: D3r reflects
something else about all-zero inboxes, and that is reported as open.

After Part G the API freeze is back in force.
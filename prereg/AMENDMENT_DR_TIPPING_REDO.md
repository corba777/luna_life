# Amendment — TASK_LIFE_DR_TIPPING: budget, and the intervention redo with interleaved order

**Status:** locked before any call it governs. Parent: `TASK_LIFE_DR_TIPPING.md`. It does not change
Parts B and C or the locked T1, which are running.

## Budget

The task budget rises to **alarm $30, stop $40** (approved by Artem). It covers Part D, Parts B and C,
the redo below and the C3 completion. The running B/C process keeps its own $20 stop; the redo runs
as a separate process with its own cap of $2 and the C3 completion with its own cap of $5, so all
together stay under $40 (projected about $25).

## Why

The Part D inbox audit (`runs/life_dr_tipping/part_d_inbox_audit.md`) found that every rebuilt inbox in
Parts 0b, 0c and D placed the P_e lines as a contiguous block at the top, followed by the other lines.
Real inboxes interleave them (0 of 20 real `all` inboxes and 1 of 20 real `all8exact` inboxes have a
top block). The same 40 Part 0c/D cells leave P_e at 0.73 on their real inboxes and at 0.025–0.125 on
rebuilt 88-line inboxes with logged signals. Order is the leading candidate.

## The redo

Parts 0b, 0c and D are repeated exactly as locked — the same source cells, conditions, draws, signal
rules, headers, slot sentences and sender sets — with one change: **which sender positions carry P_e
is chosen by a fixed hash** of (part, arm, replicate, world, round, cell, condition) instead of the
first n_pe positions. Lines stay in the sender order already used, and each line keeps the signal its
sender would carry under the original rule of that part (Part 0b: the original line's signal; Part
0c: the original sender's signal or 0; Part D: logged or zero as locked). Empty slots in Part 0b keep
their positions.

Calls: Part 0b 880, Part 0c 320, Part D 640; 1840 in all, about $1.05. Own cache namespaces
(`cache_part0b_mix`, `cache_part0c_mix`, `cache_part_d_mix`), own lock file.

## Gates (before any call)

- Outside the inbox block, every redo prompt is byte-identical to the original prompt of the same cell
  and condition.
- Inside the block, the multiset of (sender, rule, signal) lines equals the original's, apart from the
  reassignment of which senders carry P_e; report how many redo inboxes still have P_e as a top block
  by chance.
- The selection files and the audit are committed with the runner.

## Predictions (locked)

The original predictions are re-locked unchanged, on the redo data only:
- **I1r, I2r, I3r** as I1, I2, I3 of Part 0b.
- **P1r, P2r** as P1, P2 of Part 0c (P(leave | 88 lines) > P(leave | 8 lines) at each share, signal as
  in Part 0c).
- **D1r, D2r, D3r** as D1, D2, D3 of Part D.

New. These names are O1 and O2, not E1 and E2. Part E
(`AMENDMENT_DR_TIPPING_PART_E.md`) is a separate, earlier, narrower test with its own E1 and E2.
Its shuffle is a permutation of the lines. This redo reassigns which senders carry P_e. Both are
reported.
- **O1 (order holds holders).** Over all 640 Part D conditions-by-cells, pooled over length, signal and
  share: P(leave | redo) > P(leave | original top block). One-sided Fisher, α = 0.05. Basis: identity
  replay 0.73 on real interleaved inboxes against 0.025–0.125 under a top block.
- **O2 (order helps adoption).** Part 0b class A, pooled over the five mixed conditions 2/6, 3/5, 4/4,
  5/3, 6/2: P(adopt P_e | original top block) > P(adopt P_e | redo). One-sided Fisher, α = 0.05.
- **Descriptive:** every cell of every part, original against redo, with Wilson intervals; by source arm.

**Reading.** Results that hold in the redo stand. Results that change are reported as artifacts of the
top-block construction, and the package text is corrected. The class-B result under 0/8 contains no
P_e line and is a check: it should not change beyond sampling noise.

## C3 completion — r8 r3, worlds 1, 4 and 5 (approved by Artem)

`TASK_LIFE_DR_CONTROLS.md` Part 2 locked C3 on all five worlds. Worlds 1, 4 and 5 of r8/r3 were
contaminated by the duplicate launch and excluded. They are now rerun from scratch, under this task's
budget, so C3 can be reported on five worlds as locked.

- Arm `dist/luna.resp-medium/r8/none`, replicate r3, worlds 1, 4 and 5, 20 rounds.
- The same r3 sender schedule (replicate salt) as the clean r3 worlds 2 and 3, so the five worlds share
  one schedule definition.
- Fresh, empty caches (`cache_r8_r3_w{1,4,5}_clean`), new history directories (`r8/r3_clean/seed{1,4,5}`),
  the locked runner with a lock file per run directory, one launch. The contaminated files are kept
  and not read.
- Gates: round-1 prompts byte-identical to r1's for the same cells; P_e and example hash every round;
  the r3 sender schedule of round 2 matches the schedule the clean worlds 2 and 3 used for the same
  round and world seed definition.
- About $1.4 per world, $4.2 in all, inside the $40 stop; own cap $5.
- **C3 stays descriptive** as locked: the r1–r3 variance at g20 over five worlds, next to r1–r2
  (0.00006) and the lattice (0.040). The two-world figure (0.00005) is kept beside it.
- Order: after the intervention redo; it may run alongside B/C, each under its own lock.

## Qwen

`TASK_LIFE_DR_QWEN_INTERVENTIONS.md` gets its own amendment: after QI-1 (the original 880 Part 0b
prompts, kept for the model comparison on identical inputs), run QI-1m on the 880 redo Part 0b prompts,
with I1q–I3q re-locked on them. Local, no API cost.
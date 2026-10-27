# Amendment — the first-speaker lottery: Luna medium on `all` with a constructed round-2 board (F0 / F1)

**Status:** locked 2026-10-27. Luna API job inside the $100 envelope (spent $54.55). Dry build filled
every dry-build value (below). Gates passed (`runs/luna_first_speaker/gate.json`). Basis:
- `AMENDMENT_LUNA_ALL_TIPPING.md` and `runs/luna_all_tip/readout.md`;
- the post-hoc pooled-round-1 simulation `runs/luna_all_tip/posthoc_r1_pool22.md`;
- `THEORY.md` §3;
- `DESIGN_AUDIT_CHECKLIST.md`.

## Why

Luna medium on `all` tipped in 8 of 20 replicates. In these runs:
- round-1 publication is near zero (class A about 1 %, class B about 3 %), so the round-2 board holds
  0 to a few lines;
- whether those lines name P_e predicts the outcome: P(tip | s(2) ≥ 0.5) = 6/8, against
  P(tip | s(2) < 0.5 or empty) = 2/12;
- the simulator with round-1 inputs pooled over 22 replicates gives a tip rate of 0.315 [0.255,
  0.382], against an observed 0.40 [0.22, 0.61].

All of this is post hoc. The hypothesis it suggests is a **first-speaker lottery**: Luna's threshold
rule (`THEORY.md` §2–3) turns the composition of the first few published lines into the population
outcome. If that is right, fixing the round-2 board should fix the outcome, and that can be tested
by manipulation.

## Runs

World 1, `all`, 100 cells, 20 rounds, Luna Responses `effort=medium`. The panel full-run builder is
used unchanged, byte-identical to the reference. Each replicate has its own fresh cache. A new runner
file (`runs/run_luna_first_speaker.py`) handles the construction; no running script is edited.

- **Round 1** is live and unchanged for every replicate. Each cell's round-1 rule is its own decision.
- **Round-2 board, constructed** from that replicate's own round-1 rules. This is a constructed state,
  as in Part H, and the readout says so.
  - **F0 ("everyone speaks"):** every cell is shown as having published its round-1 rule. A cell's
    round-2 inbox holds the other 99 cells' lines, and its memory line is
    `Previous step: rule='<own round-1 rule>' published=yes`.
  - **F1 ("only witnesses speak"):** only the class-B cells holding P_e at round 1 are shown as
    published. Every other cell is shown silent. Memory lines carry `published=yes` for those
    witnesses and `published=no` for every other cell, with their own round-1 rule.
  - **Signals:** a cell that really published at round 1 keeps its own signal. Every other shown line
    takes a signal from the Part D hash over the world-1 published-signal pool of that rule.
- **Rounds 3–20** run live and unchanged from the constructed round-2 state: published decisions,
  inboxes and memory come from the cells' own outputs again.
- **Replicates:** 8 per arm, 16 in total. Cost **$1.969 per replicate** (the tipping arm's audited spend, $39.379 over 20), so **$31.50** for 16;
  cap twice the estimate, **$63.01**; envelope stop at $100 (envelope before $54.55, **$86.05** after the
  estimate). The cap does not fit under the envelope ($54.55 + $63.01 > $100): the $100 stop binds first.

## Measures (per replicate)

- s(2), the constructed P_e share on the round-2 board.
- x(t) for rounds 1–20 and the mean x(10–20). Tip means mean x(10–20) > 0.9, the definition the
  tipping amendment used.
- The tip round, class B at round 20, and publication by round and class from round 3 on.

## Reference values (fixed by the dry build, before any call)

The committed simulator is run on each arm's construction: Luna's Part A fits, rounds 3–20
publication from the pooled inputs, and the round-2 board built from simulated round-1 starts
(pooled over 22). 1,000 replicates per arm, seed 0. It gives:

- p̂0, the simulated F0 tip rate, with its Wilson 95% interval **12/1000 = 0.012 [0.007, 0.021]**;
- p̂1, the simulated F1 tip rate, with its Wilson 95% interval **1000/1000 = 1.000 [0.996, 1.000]**;
- the expected s(2) per arm: F0 is about the round-1 P_e share (about 0.16); F1 is 1.0 whenever at
  least one witness holds P_e at round 1. Dry build: F0 **0.168** (the mean round-1 P_e share); F1 **1.000**,
  with at least one witness in 1000/1000 simulated starts (mean 16.8 witnesses).

## Predictions (locked)

The unit is the replicate, 8 per arm.

- **F-T1 (the board decides):** F1 tips in more replicates than F0. One-sided Fisher exact,
  α = 0.05.
- **F-T2 (F1 tips):** the F1 tip count is at least the 2.5th percentile of Binomial(8, lower Wilson
  bound of p̂1) = Binomial(8, 0.996): **at least 7 of 8**.
- **F-T3 (F0 freezes):** the F0 tip count is at most the 97.5th percentile of Binomial(8, upper Wilson
  bound of p̂0) = Binomial(8, 0.021): **at most 1 of 8**.

## Pre-stated readings

- **F-T1–F-T3 hold:** on a global board, Luna's outcome is set by who speaks first. Two consequences
  follow:
  - the earlier "Luna loses on `all`" was a statement about an unmanipulated first-speaker draw;
  - who speaks first is a protocol variable that can be designed. This connects to P1 and to
    publication policy as a lever.
- **F-T1 holds, F-T2 fails:** constructed witness-only boards push toward P_e but do not settle the
  outcome. Later prefix publication by class A dilutes the board. The readout reports s(t) for
  rounds 3–5 against the simulator's.
- **F-T3 fails (F0 tips):** the threshold is softer at s ≈ 0.16 than Part A says, or memory of an
  "everyone spoke" round changes the response. The readout compares round-3 adoption with Part A's
  α(s).
- **F-T1 fails:** the round-2 board does not decide the outcome. The lottery reading of the post-hoc
  data is withdrawn.
- **If the design is the cause:** the constructed memory line (`published=yes/no`) differs from what
  some cells actually did at round 1. That is the manipulation, and it is stated. Signals for lines
  that were not really published come from the pool by hash, not from the cell.

## Gates (live calls refused, except round-1 calls in the dry build's 1-replicate smoke)

- **Construction check, on stored round-1 decisions from one tipping replicate:**
  - F0 inboxes have 99 lines, one per other cell, with that cell's round-1 rule;
  - F1 inboxes hold exactly the round-1 class-B P_e holders;
  - the memory lines follow the arm rule.
- Rounds 3–20 prompts are produced by the unchanged builder from the constructed state. A replay
  of one tipping replicate from round 3, with that replicate's real round-2 state, reproduces its
  stored round-3 prompts byte for byte.
- Fresh, empty cache directories for each arm and replicate, with an arm id in each path.
- Cost estimate and cap, and the envelope projection.

## Design audit

1. **Fidelity.** The builder is unchanged. Only the round-2 board and memory are constructed, as
   stated.
2. **Coverage.** World 1, `all`, where the lottery was seen.
3. **Controls.** F0 and F1 differ only in the round-2 construction, and both start from live round-1
   decisions. The 20 unmanipulated replicates are the natural reference.
4. **Observability.** Cells see their prompts only. The manipulation is what they see.
5. **Gate consistency.** All gates above run together.
6. **Statistical unit.** The replicate, 8 per arm. Power for F-T1 at p̂0 and p̂1 is **1.00** (50,000 draws, seed 0; one-sided Fisher exact, α = 0.05).
   If it is below 0.8, that is stated, and the design is not changed after the number is seen.
7. **Pre-stated readings.** Above.

## Queue

API only, no GPU. F1 and F0 replicates alternate (F1 r1, F0 r1, F1 r2, …) under one waiter, so that
any drift over time is shared between the arms. It starts after the lock, in parallel with the local
queue.
# Task — How the true rule spreads: votes needed, relay, distance (analysis only)

**Status:** analysis of existing logs. No new runs, no API calls, no GPU.
Parent: `TASK_LIFE_REASONING_CELLS.md`, `AMENDMENT_LIFE_CAS.md`. Arms used: B, Ca, Da (with channel).
Descriptive only; any follow-up experiment (source count, TTL) gets its own task with predictions
before it runs.

## Questions

1. **Votes:** how many distinct neighbours must carry P_e before a cell switches to it? Does a
   reasoning cell switch on one message, while a one-pass cell needs more?
2. **Relay:** do cells that do not hold P_e forward it? Does anyone beyond the immediate
   neighbours help?
3. **Distance and lag:** how does the switch time depend on distance from the nearest source, and
   how far behind the topological reachability bound is each arm?

## Part 0 — Delivery mechanics (from code, no data)

Write `runs/life_reasoning_cells/delivery_mechanics.md`, citing file and line:
- neighbourhood (4 or 8 cells, torus wrap);
- what a cell publishes each step (its current rule only? its whole inbox?);
- TTL: its value, what decrements it, and **who forwards**: only holders of the rule, every cell a
  message passes through, or nobody (TTL = lifetime in the inbox only);
- inbox contents at decision time: deduplicated or with counts? With sender ids? With hop count?
- how the reachability bound in `reachability_bound.json` models this: which assumption gives
  1.0 at g3.

## Part 1 — Votes at the moment of switch (B, Ca, Da; 1-op and 2-op separately)

For every transition of a non-source cell from a rule ≠ P_e to P_e:

| field | meaning |
|---|---|
| `n_senders_pe` | distinct cells whose messages carrying P_e were in the inbox at the decision |
| `n_msgs_pe` | messages carrying P_e (with duplicates, if the inbox keeps them) |
| `n_competing` | distinct other rules in the inbox, and how many of those fit the cell's example |
| `share_pe` | P_e share among the rules in the inbox |
| `prev_correct` | feedback on the cell's previous answer |
| `lag_first_seen` | generations from the first appearance of P_e in this cell's inbox to the switch |

Report the distributions per arm and depth: `n_senders_pe` = 1 / 2 / 3+, and the median lag.

Also report the **exposure-conditioned switch rate**: P(switch to P_e at g | P_e in inbox at g,
cell not holding P_e), split by `n_senders_pe` (1, 2, 3+) and by `prev_correct`. This is the
dose–response curve: if one message suffices, the rate is flat in `n_senders_pe`; if cells follow
majorities, it rises.

## Part 2 — Relay

- Using sender ids and hop counts (if logged): the share of P_e messages a cell received from
  **non-holders** of P_e (relayed), against those received directly from holders.
- For each switch: was the immediate sender a holder or a relay?
- If the logs carry no sender or hop data, say so, and give the answer from Part 0 instead.
  Do not reconstruct it by guessing.

## Part 3 — Distance and lag

- For every non-source cell, its torus distance to the nearest source (in the neighbourhood
  metric from Part 0).
- First generation holding P_e, against distance: per arm, the median and IQR by distance.
- Lag behind the bound: first holding generation minus the earliest generation the bound says P_e
  can reach that cell. Per arm and depth.
- Cells that never hold P_e: their distance distribution against that of the cells that do.

## Readout (descriptive)

- One sender is enough and lag ≈ 0 (B) → verification replaces social proof; spread is limited by
  topology, not persuasion.
- Ca switch rate rises with `n_senders_pe` → one-pass cells follow the crowd. That fits their
  lack of a consistency filter.
- Relay share > 0 → cells that do not believe the rule still help spread it. That changes the
  answer to "is it only neighbours?"

## Artifacts

- `runs/life_reasoning_cells/delivery_mechanics.md`
- `runs/life_reasoning_cells/spread_diag.json` (per-switch rows, per-arm summaries,
  dose–response tables, distance tables)
- `runs/life_reasoning_cells/fig_spread.png`: switch rate against `n_senders_pe` (B, Ca, Da) and
  first-hold generation against distance, with the bound

## Constraints

Logs only; CPU; no changes to any run artifact. Anything not in the logs is reported as missing,
not inferred.
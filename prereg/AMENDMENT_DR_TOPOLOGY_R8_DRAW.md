# Amendment — TASK_LIFE_DR_TOPOLOGY: r8 draw, all slot count, inbox log, cost

**Status:** written before Part A and before any API call. Parents:
`TASK_LIFE_DR_TOPOLOGY.md`, `AMENDMENT_DR_TOPOLOGY_CHANNEL.md`.

## r8 senders are redrawn every round

The task says the r8 senders are drawn once per world and stay fixed for all rounds.
Phone does not do that. `r8_peers` in `runs/run_life_phone.py` ranks the other 99 cells by
`sha256(f"{PHONE_SEED}|{world}|{generation}|{cell}|{c}")` and keeps 8. `PhoneCompleter._build_inbox`
passes `epoch_generation` as that generation. `PHONE_SEED` is `20261016`. The hash has no
replicate field, so both replicates share the draw. It does have the round, so the eight
senders change every round.

With `EPOCH_LENGTH` at least 21, rounds 1–20 have `epoch_generation` 1 through 20, each once.
Round 1 (`epoch_generation` 1) has an empty inbox, as in Phone. Part A and the runner use
`r8_peers(world, round, cell)` with `round` the 1-indexed decision round. The gate reproduction
for world 1, cell 1, round 2 is the eight senders `60, 91, 19, 47, 34, 56, 28, 8`.

## all names the true slot count

The DR constitution sentence says "eight message slots", and `prompt._render_inbox` always
prints `Visible messages (8 slots):`. `make_observation` rejects an inbox whose length is not 8.
Phone All avoids the rejection by replacing `make_observation`, and its header is
`Visible messages ({n} slots):` with `n = len(inbox)`. That inbox is one line per publisher
among the other 99, sender id and rule text, not a count per rule. Publishers who stayed
silent are omitted, so `n` is the number of lines, not 99.

The `all` arm uses that render. The constitution sentence that says "eight message slots"
is changed to the same `n`. A header of 8 above a longer inbox is not allowed. Against a DRc
round-1 prompt, `r8` may differ only in the inbox block. `all` may differ in the inbox block
and in that one sentence, and nowhere else. The private-example block stays byte-identical.

## inbox_says is the inbox the cell was shown

The engine writes `rule_history.inbox_says` from Moore `deliver` before a completer replaces
the inbox. That was the Phone bug before v3. For `r8` and `all`, after every round,
`inbox_says` for every cell is the list of says in the inbox that cell was shown, and the row
carries `inbox_says_kind` naming the arm. Independent finds are counted from that field.

## Cost is checked after every round

The pinned DRc runner adds the world's `usd_list_rate` only after `run_world` returns.
The topology runner reads the cumulative list-rate cost after every round, alarms at $15 and
stops at $20. The caps are unchanged.

## What k means in Part A

`nucleation_descriptive.json` defines k as the number of Moore neighbours holding P_e at the
previous round, not as the number of P_e lines in the inbox. Part A uses those tables.
Bins with fewer than 20 events take the pooled probability for that event and k.

- moore: the eight cells are the Moore neighbours.
- r8: the eight cells are that round's peers. A peer counts when it holds P_e.
- all, labelled weak: `s` is the share of the other 99 cells holding P_e, and the table is
  read by linear interpolation at `k = 8s`.

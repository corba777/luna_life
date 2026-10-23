# Amendment — LM-none on the lattice with witnesses seeded on P_e (discovery against yielding)

**Status:** locked. This is a Luna API job inside the $20 envelope, approved by Artem on
2026-10-23. No call is made before this file is committed as locked after a dry build. The dry
build is `runs/gate_lm_none_seedb.py` (0 live calls). Parents: `AMENDMENT_PANEL_FULL_RUNS.md`
(locked), `runs/model_panel/lm_none_full_readout.md`, `DESIGN_AUDIT_CHECKLIST.md`.

## Why

LM-none (Luna, `effort=none`) lost the lattice completely: mean x over rounds 10–20 was 0.0009 and 0.
F1–F3 passed. The readout shows two failures at once, and the locked design did not separate them:

- **Discovery.** At round 1, 0/25 class-B cells named P_e in every replicate. Luna medium had 15–18.
- **Yielding.** Class-B cells on the prefix, which their own example rules out, rose from 6–9/25 at
  round 1 to 16–20/25 on the lattice by round 20.

Because no witness ever held P_e, the data cannot say whether a reasoning-off witness that has the
truth would keep it and pass it on. This run gives the witnesses P_e and asks only that.

## Run

**LM-none-seedB.** It is the LM-none-lattice arm unchanged — the same runner, world 1, 2 replicates,
20 rounds, 100 cells, Responses `effort=none`, the same prompt builder — with one difference:

- **The seed.** At round 1, each of the 25 class-B cells gets the memory line of a cell that held P_e
  in the previous round and did not publish. The builder renders it as
  `Previous step: rule='shift_symbols(1);swap(2,3)' published=no.`
- **Everything else stays as in LM-none-lattice:** class-A cells keep the round-1 memory line, all
  round-1 inboxes are empty, and from round 2 on the memory comes from each cell's own decisions.
  This is a constructed state, as in Part H, and the readout says so.
- **Control:** the existing LM-none-lattice replicates, which are the unseeded run. Luna medium on the
  lattice is the reference.
- **Cost:** $0.9167, the measured token spend of LM-none-lattice. Cap $1.80, which is twice the
  $0.90 estimate and above that measured spend. Shared envelope $20. The runner stops from
  `usd_from_usage` on the live token counts.

## Measures (per replicate)

- **Round-1 retention:** class-B cells naming P_e at round 1, out of 25. This is the manipulation
  check.
- **Class B at g20:** cells on P_e, on the prefix, and on other rules.
- **x(g)** for rounds 1–20, and mean x over rounds 10–20.
- **Spread:** class-A cells on P_e at any round, and the first round each one adopts it.

## Reference values and thresholds (fixed now)

- **y_bat** = 145/240 = 0.604: LM-none's class-B prefix adoption under 0/8 on the enlarged battery set.
- **k_hold** = 14, the 95th percentile of Binomial(25, 1 − y_bat = 95/240). It is the smallest k
  with cdf ≥ 0.95 (cdf(14) = 0.969, cdf(13) = 0.928): the most witnesses that would still hold
  P_e at round 20 if each yielded with the battery rate.
- **t_lat** = 0.75, from `AMENDMENT_PANEL_FULL_RUNS.md`.

## Predictions (locked)

Each must hold in both replicates. These are read only if the manipulation check holds.

- **Manipulation check:** round-1 retention ≥ 13/25, a majority of the seeded witnesses, in each
  replicate. If it fails, the seed did not take, SB1 and SB2 are reported but not read, and the
  readout says the memory line alone did not install P_e.
- **SB1 (witnesses yield even with the truth):** class-B cells on P_e at g20 ≤ k_hold.
- **SB2 (no Luna-like spread):** mean x over rounds 10–20 < t_lat.

## Pre-stated readings

- **SB1 and SB2 pass:** a reasoning-off witness that holds P_e gives it up, and the population does
  not reach P_e. Luna medium's lattice win needs reasoning for both discovery and resistance.
- **SB1 fails and SB2 passes:** the witnesses keep P_e, but it does not spread. Discovery was the
  missing piece for the witnesses themselves, and spread needs something more: class-A adoption.
  The spread measures say which.
- **SB1 and SB2 both fail:** with the truth installed, reasoning-off Luna holds it and spreads it like
  Luna medium. The bottleneck of LM-none was discovery alone.
- **The manipulation check fails:** without reasoning, the cell does not keep a rule handed to it in
  memory, so memory carries little for this agent. That is itself reported.
- **If the design is the cause:** the seed is a single memory line, and one round later the memory is
  the cell's own. A cell that drops P_e at round 1 is not yielding to neighbours, because the
  round-1 inbox is empty. Round-1 drops and later drops are reported apart.

## Design audit

1. **Fidelity.** Passed, live calls refused. Every round-1 prompt equals the LM-none-lattice
   round-1 prompt for the same cell, byte for byte, except the memory line of the 25 class-B cells.
   The 75 class-A prompts are identical. Round-1 prompts do not take a replicate index
   (`inference_seed` is world, generation, cell), so both replicates send this prompt. The seeded
   line, taken from the rendered prompt, is
   `Previous step: rule='shift_symbols(1);swap(2,3)' published=no.`
   After one dummy decision, round 2 is byte-identical for all 100 cells, so the seed does not
   persist. Rounds 2–20 are built by the unchanged runner.
2. **Coverage.** World 1 on the lattice, as in the control. Nothing is extrapolated.
3. **Controls.** LM-none-lattice is the unseeded control in the same arm and world. Luna medium on the
   lattice is the reference.
4. **Observability.** The seed is in the prompt the cell sees. Nothing else is assumed.
5. **Gate consistency.** These ran together with live calls refused:
   - the round-1 diff against the control: 25 memory lines differ, nothing else; round 2 matches
     on all 100 cells;
   - k_hold = 14;
   - the token-based spend cap is $1.80, and the measured LM-none-lattice spend $0.9167 is under it;
   - the envelope after this run plus LM-dec. LM-dec had not closed at the dry build (replicate 1,
     round 20, $2.3039 from token counts). Using the locked LM-dec estimate $4.62 and this run at
     the measured $0.9167, the envelope is $9.85 of $20. If both arms stop at their caps ($9.24 and
     $1.80), it is $15.36 of $20.
6. **Statistical unit.** The replicate (2), and each prediction must hold in both. This is weak, and
   stated.
7. **Pre-stated readings.** Above.

## Descriptive beside it (from existing data, no calls)

From the finished LM-none runs. A class-B rule fits the cell's own example when its description is
in that cell's cofitting set in `runs/life_distributed/world_audit.json` for world 1. P_e is in
every cofitting set. The prefix is in none of the class-B sets. No class-B cell named P_e at round
1, so the number that fit is also the number of witnesses whose round-1 rule checks their example.

| run | other rules | of which fit the cell's example |
|---|---:|---:|
| lattice, replicate 1 | 19 | 0 |
| lattice, replicate 2 | 19 | 1 (cell 33, `rotate_left(2);shift_symbols(7)`) |
| all, replicate 1 | 17 | 0 |
| all, replicate 2 | 16 | 0 |

Witnesses checking anything at round 1: 0, 1, 0, 0 of 25.
# Amendment — Qwen: QI-T, does decoding temperature drive class-B flicker

**Status:** locked before any QI-T call. Local. Not launched with this lock. The pre-lock dry
build passed with live calls refused.
Parents: `runs/life_dr_qwen/stage1_readout.md` (sections "Class-B hazards" and "Cell-level hazards"),
`DESIGN_AUDIT_CHECKLIST.md`.

## Why

In Qwen Stage 1 `all` (world 1), class-B cells leave P_e at h_out = 104/637 = 0.163, against Luna's
66/833 = 0.079 (cell-level difference +0.084 [0.045, 0.125]), and mostly to other rules consistent with
their own example. Luna's leaves go to the prefix (65/66). The two runs differ in model and in decoding:
Qwen samples at temperature 0.6, top_p 0.95, top_k 20; Luna runs with reasoning effort `medium` and no
temperature in the request, so its effective sampling is unknown and cannot be set. QI-T asks whether
Qwen's leave rate falls when only its temperature is lowered. It does not compare Qwen with Luna at equal
temperature; that comparison is not available.

## Prompts

- Population: every Qwen Stage 1 `all` record (r1 and r2, rounds 2–20) of a class-B cell that held P_e
  at the previous round. These are exactly the h_out opportunities: 279 in r1 and 358 in r2, 637 in all.
  No subsampling.
- Each prompt is the logged prompt of that record, byte for byte (memory line `rule='<P_e>'`, the live
  inbox, the cell's own example and query, the logged catalog order).

## Conditions

- **T6:** temperature 0.6, top_p 0.95, top_k 20, min_p 0, presence_penalty 0, max_tokens 32768, thinking
  on, `thinking_mode` `template_default`. Identical to Stage 1. A fresh draw, not the logged answer.
- **T3:** the same, with temperature 0.3. Nothing else changes.
- One draw per prompt per condition: 1274 calls. No per-request seed: the Stage 1 body has no `seed`
  field, and adding one would make T6 differ from Stage 1 and T3 differ from T6 in a second field.
  Draws are unseeded, as in Stage 1, and the readout says so. (Revision before lock: the first draft
  seeded each draw by condition, which contradicted the request-body gate; the dry build found it.)
- Own cache `runs/life_dr_qwen/qit/cache`, own lock file, one launch with nohup and the watchdog, no
  auto-relaunch. Queue position: after QI-1, before QI-2.

## Scoring

- **Leave:** the parsed held rule is not P_e. Parse failures and truncations are counted per condition
  and scored as their own category; they are not silently dropped. The primary test uses the pairs in
  which both draws parsed; the readout reports how many pairs that removes.
- **Logged leave:** the live Stage 1 outcome of the same record (from the logs, already known: 104 of
  637).

## Reference values (measured, fixed now)

- p_log = 104/637 = 0.163: the logged Qwen leave rate on these prompts, at T = 0.6.
- p_Luna = 66/833 = 0.079: Luna's pooled class-B h_out in the same arm and world.

## Predictions (locked)

Unit: the prompt pair (T6, T3) on the same record. Primary test: one-sided exact McNemar on the
discordant pairs, α = 0.05. Beside it, reported and not scored: a cluster bootstrap over the 25 class-B
cells (2000 draws, `numpy` Generator seed 0) of p(T3) − p(T6).

- **T0 (replication, gate on reading, not a hypothesis):** p(T6) is consistent with p_log: the Wilson 95%
  interval of p(T6) contains 0.163. If it does not, the fresh draws do not reproduce the live rate (for
  example a server or template change), and T1 is reported but not read.
- **T1 (temperature lowers leaving):** p(T3) < p(T6) by the McNemar test.

## Pre-stated readings

Read only if T0 holds.

- **T1 fails** (no significant drop): Qwen's flicker is not a decoding-temperature effect in the range
  0.3–0.6. The Qwen–Luna difference in h_out stays attributed to the model-plus-decoding system, and
  temperature is not its explanation.
- **T1 passes and p(T3) ≤ p_Luna (0.079):** lowering Qwen's temperature alone brings its leave rate to
  Luna's level or below. The Qwen–Luna h_out difference cannot be attributed to the model; the package
  says the difference is consistent with decoding alone.
- **T1 passes and p(T3) > p_Luna:** temperature explains part of the flicker, not all of it. The package
  reports the fraction (p(T6) − p(T3)) / (p(T6) − p_Luna) with its bootstrap interval, as descriptive.
- **Independent of T1:** the destination of T3 leaves (consistent with own example or not; prefix or
  not), against T6. If T3 leaves shift toward the prefix, lowering temperature changes the kind of error,
  not only its rate, and that is stated.
- **If the design is the cause:** a T3 truncation or parse-failure rate far above T6 (thinking loops at
  low temperature) would make "fewer leaves" an artefact of lost answers; the per-condition failure
  counts are read before T1, and if T3 loses more than 5% of pairs that T6 keeps, T1 is reported with
  that caveat.

## Power (dry build)

One-sided exact McNemar, n = 637 pairs, p(T6) = 0.163, p(T3) = 0.079, 10 000 simulations each,
`numpy` Generator seed 0; within-prompt correlation is the correlation of the two binary leave
indicators. Power: 0.9987 at correlation 0, 1.0000 at correlation 0.5 (dry build, before lock). Power
against smaller drops is not claimed.

## Design audit

1. **Fidelity to live data.** Prompts are the logged prompts byte for byte. Dry build: assert byte
   identity for all 637 against the Stage 1 logs, and that the T6 request body equals the Stage 1 body
   field by field. Only `temperature` differs in T3; dry build asserts that too.
   First dry build: 637 of 637 prompts hash to existing Stage 1 cache keys, all distinct, each with the
   logged memory line `Previous step: rule='shift_symbols(1);swap(2,3)'`. The body gate failed only
   because of the seed rule, now removed.
   Re-run, live calls refused: 637 of 637 again (279 in r1, 358 in r2), all distinct, the same memory
   line, and 104 logged leaves. The T6 body equals the Stage 1 body field by field. The T3 body differs
   only in `temperature`, 0.3 against 0.6. Neither body contains `seed`.
2. **Coverage.** The prompts are the whole population on which h_out = 0.163 was measured: no
   extrapolation in share, inbox length, round or cell. Temperature 0.3 is outside the measured range by
   design, and that is the manipulation.
3. **Controls.** T6 is the untouched condition inside the same design, and T0 checks it against the live
   rate.
4. **Observability.** The cell cannot see the temperature; the prediction relies on no visible
   mechanism. Memory is one step (`rule='<P_e>'`), which the prompts contain as logged.
5. **Gate consistency.** Pre-lock gates, run together on the dry build with live calls refused: byte
   identity of prompts; T6 body equal to the Stage 1 body field by field; T3 body differing from T6 in
   `temperature` only; no `seed` field in either. Launch gates, checked by the runner at start and not
   at the dry build: lock file free; server idle (no other job). The first dry build ran while QI-1 was
   running, so "server idle" could not hold there; it is a launch gate by definition.
   Re-run of the pre-lock gates, together, live calls refused: pass. Byte identity 637/637. T6 equals
   the Stage 1 body field by field. T3 differs from T6 in `temperature` only. No `seed` in either body.
6. **Statistical unit.** The prompt pair for the primary test; repeated records of one cell are not
   independent, so the cell-cluster bootstrap is reported beside it.
7. **Pre-stated readings.** Above, including the design-as-cause reading (failures at low temperature)
   and the case where T0 fails.
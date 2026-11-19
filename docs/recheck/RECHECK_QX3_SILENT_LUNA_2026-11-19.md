# Recheck — QX-3 without messages, Luna, T-SL (2026-11-19)

Package `qx3_luna_silent_artem_recheck_2026-11-19.zip`, sha256 `4beea40d…1b84a`; SHA256SUMS passes (9,614 files).
Amendment `AMENDMENT_QX3_SILENT.md` locked v2 with addendum 1 (`4ca1367a…5815545`, stop $5.00 → $6.00, written
before any result was read). Recomputed with `sl_check.py` (own code; keys from the traces, world 0 computed; H_T
at δ = 1/8 rebuilt independently per world; every stored test output equals it). Every number in the agent's
readout reproduces.

Luna · δ 1/8 · B 1 · worlds 0–3.

| world | silent x̄ | rule only x̄ | difference | silent x̄_nf | rule only x̄_nf | finders silent / rule only |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0.5167 | 1.0000 | +0.483 | 0 | 0.360 | 61 / 64 |
| 1 | 0.5192 | 0.9992 | +0.480 | 0 | 0.459 | 55 / 54 |
| 2 | 0.3858 | 0.9875 | +0.602 | 0 | 0.468 | 43 / 52 |
| 3 | 0.5592 | 1.0000 | +0.441 | 0 | 0.250 | 58 / 75 |

**T-SL holds:** p = 1/70 (unpaired over the same four worlds, an approximation; positive in every world), as
predicted. All runs 24 × 100, not partial, no received results, no fallbacks counted.

- Silent x̄_nf = 0 in every world: no cell reached H_T without its own counterexample. The floor for guessing is 0.
- Two generations after their counterexample, silent finders held H_T in 205 of 217 cases, rule-only finders in
  239 of 245.
- Silent cells still wrote messages (2,031–2,076 per run, never delivered) against 2,384–2,391 in rule only.
- Mean tokens per call, 9,600 calls each, no cache hits: silent reasoning 314.7, output 351.0; rule only 197.4 and
  234.9. The silent runs cost more per call than projected for this reason.

Reading: at δ = 1/8 rule names add about half the population for Luna (+0.44 to +0.60), all of it through cells
without evidence of their own; the finders are about the same with and without names.

# gpt-oss-120b, continuation of the Stage 2 runs to round 80 — closed readout

Locked amendment: `prereg/AMENDMENT_OSS120_CONTINUE80.md` (sha256 `7cb8c3af…`). Eight runs (lattice and
`all`, replicates 1–4), world 1; rounds 1–40 replayed from the Stage 2 runs (no call), rounds 41–80 live.
x(70–80) = mean over rounds 70–80 inclusive of the share of the 100 cells holding P_e (class B included).

**Verdicts (final, 2026-11-09): K1 fails, K2 fails, K3 fails.** Independent recheck from the raw
files with separate code (x per round, K1–K3, request counts, re-parse, inbox lengths): every number
matches.

| prediction | rule | predicted p | observed | verdict |
|---|---|---:|---|---|
| K1 | ≥ 3 of 4 lattice runs with x(70–80) ≥ 0.8 | 0.9972 | 2 of 4 | fails |
| K2 | `all` r1 and r2 both x(70–80) < 0.5 | 0.9781 | 0.852, 0.861 | fails |
| K3 | mean lattice x(70–80) > mean `all` | 0.9975 (descriptive) | 0.797 vs 0.871; exact permutation p = 0.986 | fails |

| run | x(40) | x(70–80) | x(80) | first round x ≥ 0.9 | predicted median x(70–80) [p05, p95] | predicted P(≥ 0.8) | predicted P(< 0.5) |
|---|---:|---:|---:|---:|---|---:|---:|
| lattice/r1 | 0.67 | 0.725 | 0.71 | 67 | 0.93 [0.85, 0.96] | 0.9840 | 0.0005 |
| lattice/r2 | 0.53 | 0.765 | 0.78 | never | 0.93 [0.75, 0.96] | 0.9275 | 0.0100 |
| lattice/r3 | 0.81 | 0.854 | 0.88 | 52 | 0.93 [0.86, 0.96] | 0.9905 | 0.0000 |
| lattice/r4 | 0.96 | 0.845 | 0.77 | 38 | 0.93 [0.87, 0.96] | 0.9910 | 0.0000 |
| all/r1 | 0.24 | 0.852 | 0.87 | 74 | 0.31 [0.27, 0.36] | 0.0055 | 0.9920 |
| all/r2 | 0.36 | 0.861 | 0.88 | 47 | 0.31 [0.27, 0.37] | 0.0120 | 0.9860 |
| all/r3 | 0.92 | 0.897 | 0.93 | 23 | 0.95 [0.93, 0.97] | 1.0000 | 0.0000 |
| all/r4 | 0.52 | 0.875 | 0.87 | 46 | 0.93 [0.28, 0.97] | 0.5170 | 0.4810 |

Predicted values are given to four places from continue80_sim.json; the amendment quotes the same values rounded to three.

Lattice P_e Moore components (largest cluster) at rounds 40 / 50 / 60 / 70 / 80:

- lattice/r1: 2 (65) / 1 (69) / 1 (87) / 1 (85) / 1 (71)
- lattice/r2: 2 (52) / 1 (62) / 2 (56) / 1 (65) / 1 (78)
- lattice/r3: 1 (81) / 1 (85) / 1 (93) / 1 (97) / 1 (88)
- lattice/r4: 1 (96) / 1 (96) / 1 (81) / 1 (93) / 1 (77)

Health per run (all eight): 4,000 calls, every stored text re-parsed to the stored decision, 0 tokenizer
mismatches, 0 calls ending at max_tokens. Server POSTs equal client attempts in every live window (0 foreign);
the exclusivity monitor logged no foreign GPU process and no open-webui sample.

Files: `readout.json` (the run's readout, byte copy), `continue80_sim.json` (the locked predictions'
simulator output, byte copy), `run_summary.json` (calls, POST attempts, wall time and live window per run,
byte copy).

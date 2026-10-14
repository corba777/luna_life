# TASK_LIFE_DISTRIBUTED — Phase 1 readout

Generated: 2026-10-14T08:40:10.963216+00:00
**Complete:** True
**USD (list):** $3.9662 (alarm $25)

## Verdicts

- **D1** (DRs ≤ chance+0.15): **PASS** (DRs mean J=0.146, thresh=0.401)
- **D2** (DRo acc ≥ 0.80): **FAIL** (mean=0.5599999999999999) — as registered; do not amend
- **D3** (DR ≥ DRs+0.30 in ≥4/5): **PASS** (5/5)
- **D4** (DC−DCs < 0.15 mean): **PASS** (mean Δ=0.014000000000000002)
- **D5** (intersection): descriptive — see `intersection_diag.md`

### D2 post-hoc (labelled; not an amendment)

DRo is one call per neighbourhood, so it tests one-shot pooling of nine examples, not information sufficiency (world audit proves ∩ S = {P_e}). DR J@g10 mean 0.852 > DRo mean 0.5599999999999999: the population with ten generations beats one-shot pooling. A DRo fail means one call poorly assembles nine examples, not that the neighbourhood lacks information.

### D5 (DR switches to P_e)

DR: (a∧b) share 76%–92% (mean 83%); majority-alone (c) mean 0%. Full table in `intersection_diag.md`.

## DRo detail (calls, wrong class, tokens)

| seed | n | acc | USD | reason tok/call | wrong: 1op⊂S_c | wrong: partial | wrong: none |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 0.2 | 0.0066 | 243 | 16 | 0 | 0 |
| 2 | 20 | 0.5 | 0.0213 | 1712 | 9 | 1 | 0 |
| 3 | 20 | 0.75 | 0.0111 | 687 | 5 | 0 | 0 |
| 4 | 20 | 0.5 | 0.0245 | 2028 | 3 | 7 | 0 |
| 5 | 20 | 0.85 | 0.0103 | 614 | 3 | 0 | 0 |

## Per-seed table (chance beside DRs; D3 Δ)

| seed | chance E[1/|S_c|] | share 1-op | DRs J | DR J | Δ(DR−DRs) | D3 | DRo acc | DC J | DCs J |
|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| 1 | 0.2507 | 0.75 | 0.21 | 1.0 | 0.79 | PASS | 0.2 | 0.04 | 0.04 |
| 2 | 0.1968 | 0.97 | 0.07 | 0.8 | 0.73 | PASS | 0.5 | 0.04 | 0.04 |
| 3 | 0.2504 | 0.76 | 0.12 | 0.75 | 0.63 | PASS | 0.75 | 0.04 | 0.04 |
| 4 | 0.2950 | 0.42 | 0.11 | 0.71 | 0.6 | PASS | 0.5 | 0.1 | 0.04 |
| 5 | 0.2641 | 0.75 | 0.22 | 1.0 | 0.78 | PASS | 0.85 | 0.05 | 0.04 |

## Drop share (channel arms)

| arm | seed | n_publishes | n_dropped | drop_share |
|---|---:|---:|---:|---:|
| DR | 1 | 693 | 0 | 0.0000 |
| DR | 2 | 651 | 0 | 0.0000 |
| DR | 3 | 746 | 0 | 0.0000 |
| DR | 4 | 685 | 0 | 0.0000 |
| DR | 5 | 663 | 0 | 0.0000 |
| DC | 1 | 948 | 0 | 0.0000 |
| DC | 2 | 930 | 0 | 0.0000 |
| DC | 3 | 948 | 0 | 0.0000 |
| DC | 4 | 934 | 0 | 0.0000 |
| DC | 5 | 941 | 0 | 0.0000 |
| DRs | 1 | 0 | 0 | 0.0000 |
| DRs | 2 | 0 | 0 | 0.0000 |
| DRs | 3 | 0 | 0 | 0.0000 |
| DRs | 4 | 0 | 0 | 0.0000 |
| DRs | 5 | 0 | 0 | 0.0000 |
| DCs | 1 | 0 | 0 | 0.0000 |
| DCs | 2 | 0 | 0 | 0.0000 |
| DCs | 3 | 0 | 0 | 0.0000 |
| DCs | 4 | 0 | 0 | 0.0000 |
| DCs | 5 | 0 | 0 | 0.0000 |

## USD by arm × seed

| arm | s1 | s2 | s3 | s4 | s5 | sum |
|---|---:|---:|---:|---:|---:|---:|
| DR | 0.3604 | 0.4443 | 0.4007 | 0.4230 | 0.3713 | 1.9997 |
| DRs | 0.3185 | 0.4378 | 0.3889 | 0.4032 | 0.3443 | 1.8926 |
| DRo | 0.0066 | 0.0213 | 0.0111 | 0.0245 | 0.0103 | 0.0739 |
| DC | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| DCs | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

## Artifacts

- `summary.json` — D1–D5 machine-readable
- `intersection_diag.md` — D5 detail
- `world_audit.md` — chance / |S_c|
- Commit provenance: re-run `summarize_life_distributed_phase1_readout.py` for the git_commit map (optional).


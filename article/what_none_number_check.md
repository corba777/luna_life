# Number check — What None of Them Knew (v10)

Generated before publish. Columns: text value · source file · source value · match.
Tolerance: displayed rounding (±0.015 absolute, or ±1.5 percentage points).
**Do not edit the article text from this table.**

| text | source file | source value | match |
|---|---|---|---|
| 0.99 (messages, round 10) | `runs/life_own_memory/summary.json` → M2.B_seed_mean_j_g10 | 0.9896 | yes |
| 0.89 (memory, no channel) | same → M2.Bs-mem_seed_mean_j_g10 | 0.8896 | yes |
| 0.25 (neither / memoryless) | same → M1 Bs-r seed mean | 0.2458 | yes |
| gap 0.10 (messages − memory) | same → M2.delta | 0.1000 | yes |
| 31% vs 11% (find after wrong) | `runs/life_own_memory/m1_retention_hazard.json` pooled_hazard Bs-mem / Bs-r | 0.3126 / 0.1115 | yes |
| 94% (re-derived same rule) | `runs/life_own_memory/m5_persistence_seed1.json` Bs-r.persistence | 0.9379 | yes |
| 99.7% / 69% (keep true rule) | m1_retention_hazard pooled_retention Bs-mem / Bs-r | 0.9969 / 0.6867 | yes |
| steady 0.26 vs observed 0.25 | find 0.11, loss 1−0.687≈0.31 → 0.11/(0.11+0.31); Bs-r J@g10 | 0.262; 0.246 | yes |
| 85–90% alone found | Bs-mem ever held P_e / 100 cells, seeds 1–5 | 0.85–0.98 (1–3 in 0.85–0.90) | yes |
| one-pass alone 0.00 | `runs/life_onepass_no_source/curves_onepass.json` Cas g10 seed_mean | 0.000 | yes |
| alone + previous rule 0.02 | same Cas-mem g10 | 0.019 | yes |
| channel, no sources 0.04 | same Ca0 g10 | 0.044 | yes |
| channel, four sources 0.25 | same Ca g10 | 0.254 | yes |
| channel + check, no sources **0.79** | same Da0 g10 | 0.794 | yes |
| channel + check, four sources 0.92 | same Da g10 | 0.923 | yes |
| convert 40% / 3% | `runs/life_reasoning_cells/spread_diag.json` Da_nops2 / Ca_nops2 dose_response_rate.1 | 0.4040 / 0.0314 | yes |
| reasoning-off 0.47 | `runs/life_luna_none/summary.json` An seed_mean_j_g10 | 0.4688 | yes |
| An0 without sources 0.01 | `runs/life_an_no_source/summary.json` An0 mean j_g10_all_100 | 0.012 | yes |
| temperature 0 → 0.62 | `runs/life_an_t0_run/summary.json` An_T0 seed_mean_j_g10 | 0.6167 | yes |
| uniform baseline 0.25 | `runs/life_distributed/summary.json` chance_mean | 0.2514 | yes |
| table round1 / round10 reasoning no channel 0.14 / 0.15 | DR/DRs rule_history means | DRs g1 0.140, g10 0.146 | yes |
| table reasoning + channel 0.14 / **0.85** | DR rule_history / summary J_g10 | g1 0.136, g10 0.852 | yes |
| table one-pass no/yes channel 0.04 / 0.04–0.05 | DC/DCs | g1 0.04; g10 0.054 / 0.04 | yes |
| per-world DR 1.00, 0.80, 0.75, 0.71, 1.00 | summary.json J_g10.DR | same | yes |
| gap ≥ 0.60 every world | DR−DRs per seed | min 0.60 (seed 4) | yes |
| D5 76–92% | summary.json D5.DR share_a_and_b | 0.765–0.919 | yes |
| 65% / 2% adopt maj∧cons / maj∧incons | `adopt_consistency.json` DR pool | 0.645 / 0.018 | yes |
| 17% / 8% one-pass | same DC pool | 0.166 / 0.080 | yes |
| seed-1: 25 cells, 15 at g1, 21 at g2 | `dr_seed1_shift1_inconsistent.json` | 25; g1 Pe=15; g2 Pe=21 | yes |
| 14 of 20; seven of nine | `dro_iter_seed1_wrong_diag.json` | g10_n_wrong=14; 13× n_fit_of_9=7 | yes |
| DRo 0.56 | summary.json DRo_accuracy mean | 0.560 | yes |
| DRo-iter 0.75; table 0.30/0.80/0.80/0.90/0.95 | `dro_iter_summary.json` | g10 mean 0.75; per_seed match | yes |
| margin 0.002 | dro_iter_readout I2 | 0.852−0.750=0.102 vs thresh 0.10 | yes |
| DR-noex mean 0.46; 47%; seed1 0.96 | `dr_noex_summary.json` | 0.460; N3 0.472; seed1 0.96 | yes |
| DRs round 10 by world 0.21, 0.07, 0.12, 0.11, 0.22 | `dr_noex_summary.json` j_g10.DRs (same as summary.json J_g10.DRs) | 0.21, 0.07, 0.12, 0.11, 0.22 | yes |
| example only in round 1, round 10 by world 0.96, 0.17, 0.45, 0.46, 0.26 | `dr_noex_summary.json` j_g10.DR_noex | 0.96, 0.17, 0.45, 0.46, 0.26 | yes |
| first-world shares over 96 non-source cells; silent arms keep 4 sources | `life_verify/v1b/metrics.py` j_non_source; TASK_LIFE_OWN_MEMORY Bs-mem/Bs-r seeded | denominator 96; sources kept | yes |
| same-rule false one-step, fit / not, reasoning 54% / 2% | `runs/article_review_followups.json` same_rule_control.DR.pooled | 0.541 (60/111) / 0.017 (5/293) | yes |
| same-rule, one-pass 16% / 11% | same, DC.pooled | 0.162 (51/314) / 0.108 (67/621) | yes |
| true rule found without hearing it, after round 1: five | same, dr_independent_discovery.total | 5 | yes |
| keep a rule marked wrong: reasoning-off 18%, one-pass 65% | same, first_world_keep An / Ca, previous answer wrong | 0.175 (487/2787) / 0.649 (2323/3582) | yes |
| keep a rule marked right: reasoning-off 69% | same, An, previous answer right | 0.690 (1058/1533) | yes |
| sampled one-pass kept a rule marked right 13% | same, C, previous answer right | 0.126 (11/87) | yes |
| no seeded cells, channel on, round 10: 0.99 | `runs/life_long_chain/summary.json` predictions.W6 mean of per_seed_j_g10 | 0.98, 0.99, 1.00, 1.00, 1.00; mean 0.994 | yes |
| nine times as many calls per neighbourhood | `TASK_LIFE_DRO_ITER.md`: one agent per neighbourhood vs nine cells | 9 / 1 | yes |
| distill 86%; completed 92% | `life_distill/phase0_readout.md` | 0.863; 0.919 | yes |
| SPADE 0.94 | `spade_grid/g2g3_spade_4b_cot_close.json` cot 2-op pair_pref | 0.942 | yes |

## Verdict

**All listed numbers match their readout sources within display rounding.** No stop-for-mismatch.

Opening “14%” = DR/DRs round-1 seed mean ≈ 0.14. Closing DR-noex “half” = 0.85→0.46.

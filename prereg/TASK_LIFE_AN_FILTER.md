# Task — Why does reasoning-off Luna (An) beat one-pass Decisions (Ca) in Life?

**Status:** locked. Analysis of existing logs only: **0 API calls, 0 GPU**. Predictions are
locked with this file, before any number is computed. Follows `DESIGN_CHECKLIST.md`.
Parents: `TASK_LIFE_LUNA_NONE.md` (A1 FAIL, A2 PASS), `TASK_LUNA_RULE_PREFERENCE.md` (C decomposition).

**Design checklist:** analysis-only (no new arm / prompt). Items 1–3 N/A until a follow-up
experiment is locked. Items 4–6 apply (registered before numbers; claim scope; always name J@g10
vs mean J). Item 7: cost = 0.

## Why

2-op, J@g10: An 0.47, Ca 0.25, B 0.99. Raw A3: An adopts neighbour rules that contradict its own
example in 10.4% of adoptions, Ca 62.1%, B 0.47%. Seed 2: An 0.56, Ca 0.00. Seed 1 goes the other
way: An 0.21, Ca 0.56.

Raw A3 is confounded: An and Ca populations have different inboxes (An holds P_e more often, so
it sees fewer wrong majorities). This task compares the arms **in matched inbox situations** and
decomposes An's advantage into adoption and retention, as was done for memory.

## Definitions (all from logged fields; list the exact field names in the gate file)

- **Consistent(rule, cell):** engine applies `rule` to the cell's private example input and the
  result equals the example output. Computed offline with the task engine.
- **Situation:** one non-source cell-generation g ≥ 2, 2-op seeds 1–5, arms An, Ca, B.
- **Inbox stratum** of a situation, from the logged inbox (exact, not reconstructed):
  - `m` = most frequent non-P_e rule in the inbox, `n_m` = its count (1, 2, 3+);
  - `cons_m` = Consistent(m, cell);
  - `k` = number of P_e messages (0, 1, 2+);
  - `prev_is_m`, `prev_is_pe` from the cell's own previous rule.
- **Adopt m:** chosen rule == m and prev ≠ m.
- **h(k):** P(choose P_e | k, prev ≠ P_e). **r:** P(keep P_e | prev = P_e, correct=true).

Matched comparisons use strata present in **both** arms with n ≥ 20 each, weighted by the pooled
stratum counts (same weights for both arms). Report unweighted per-stratum values too.

## Analyses

1. **Conformity filter.** P(adopt m) by stratum (n_m, cons_m, prev_is_m=false), per arm.
2. **Adoption of the true rule.** h(1) and h(2+) per arm, raw and matched on (n_m, cons_m).
3. **Retention.** r per arm, per seed.
4. **Decomposition.** Steady-share check h/(h + 1 − r) per arm vs observed mean J g6–g10 (as in
   own-memory M1).
5. **Answer source.** For each arm, state how `answer` is produced (model text or engine from the
   chosen rule). For An only: share of decisions where the emitted answer equals the chosen rule
   applied to the query. Descriptive; it tells whether An's text answer and its rule agree.
6. **Seed 1 (descriptive).** Modal rules at g10, h(1), r and the stratum table for An vs Ca;
   one paragraph on why Ca is higher there. No prediction.

## Predictions (lock)

- **F1 (filter):** in matched strata with cons_m = false and n_m ≥ 2, P(adopt m) for An is at
  least 0.30 below Ca (weighted).
- **F2 (filter is specific):** in matched strata with cons_m = true, |P(adopt m) An − Ca| < 0.15.
  If F1 passes and F2 fails, An is not checking but is generally less conformist.
- **F3 (adoption):** pooled h(1) for An ≥ 3 × Ca, matched on (n_m, cons_m).
- **F4 (retention is not the cause):** |r_An − r_Ca| < 0.05 (pooled).
- **F5 (decomposition, descriptive):** steady-share formula per arm within ±0.10 of observed.

Readout:
- F1, F2, F3 PASS, F4 PASS: An's advantage is an own-example filter at adoption; Decisions lacks it
  in the full context although it shows it in isolated pairs (R2).
- F1 FAIL: the raw A3 gap is inbox composition, not a filter; look at retention and sources.
- F4 FAIL: An also keeps the rule better; report the share of the J gap each part explains.

## Gate

- Zero live requests: the analysis script asserts no client is constructed.
- Fields: inbox, chosen rule, prev rule, correct flag and private example read from the logged
  run records of each arm; list the paths and fields in `runs/life_an_filter/gate.md`.
- Sanity asserts: J@g10 per arm recomputed from the same records equals the An readout
  (An 0.469, Ca 0.254, B 0.990); the Ca h(1) per seed equals `runs/luna_rule_pref/summary.json` R3
  `logged_h1`; Consistent() on P_e is true for every cell in every seed.
- Commit this file and the script before the first number.

## Artifacts

`runs/life_an_filter/{gate.md, strata.json, readout.md}`; per-situation rows as jsonl.
Always say which J (checklist item 6). No reasoning text is requested or stored.
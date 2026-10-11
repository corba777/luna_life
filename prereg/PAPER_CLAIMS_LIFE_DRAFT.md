# PAPER_CLAIMS — Life with reasoning cells (draft)

**Status:** draft; Life arms closed (`life_1op_close.ok` 2026-10-11). Da 1-op filled in C-L3.
Do not merge into `PAPER_CLAIMS.md` until you pull the post lead + grid sentence. L2/L6 and
mechanism % verified 2026-10-11 against `TASK_LIFE_REASONING_CELLS.md` + `diag_b_mechanism.json`.

Source task: `TASK_LIFE_REASONING_CELLS.md` (seeds `924cabf`), amendments Ca/Da (argmax) and
`AMENDMENT_LIFE_CAS.md` (`def912a`). Model: `gpt-6-luna` (public beta), Responses `effort=medium` for
reasoning cells, Decisions API for one-pass cells. Torus 10×10, sources `SPARSE_SOLVER_IDS` 0/5/50/55,
sparse non-identifying examples, one 10-generation epoch, 5 seeds per depth. J = non-source share holding
P_e, epoch mean. Lock = modal share ≥ 0.5 (registered); 0.6 = post-hoc sensitivity only. CIs = bootstrap
over seeds (cluster = task) unless stated.

## Headline

> Single rules are solved by each reasoning cell alone; two-step rules are solved only collectively, and
> only by cells that can make the intermediate step — by their own reasoning or by an external check.

## Claims

### C-L1 Messages make two-op rules possible, not just faster — **Holds**
- 2-op: B (reasoning + channel) J 0.82, correct lock 5/5 seeds by g2–4; Bs (no channel) J 0.25, no
  correct lock. B − Bs = **+0.574 [+0.547, +0.614]**, ΔAUC +5.38.
- 1-op: B 0.99, Bs 0.93 — each reasoning cell finds a single rule alone; the channel adds little.
- Dense examples (arm A): J ≥ 0.96 at both depths, no false lock — the sparse design, not the task, is what
  forces collective computation.

### C-L2 Collective correction has two stages; one-pass cells have only the second — **Holds**
- Reasoning cells (B, 2-op seeds 1–3; `diag_b_mechanism.json` pooled): inconsistent inbox rules are
  not adopted **97.6%** of the time (reject-on-sight; task text ≈98%). That 0.976 is the **mean of
  per-seed rates** (0.93 / 1.00 / 1.00); by message count 507/511 ≈ 0.99 — the only seed that accepted
  any inconsistent rule is seed 1 (ambiguous task). Among switches off a false-consistent rule,
  **243/258 (94%)** go to P_e; neighbours also offer other consistent rules (~1.5 per cell on average)
  that are almost never taken — P_e wins by multi-neighbour presence and surviving the next feedback.
  Of switches onto P_e, **86.6%** need both "answer was wrong" and P_e in the inbox (≈87%);
  memory-only **6.8%**, neighbours-only **6.6%** (≈7% / 7%); 0% with a correct past answer and empty
  P_e inbox.
- One-pass cells (Ca): in the three traced seeds, all inbox adopters had just been told they were
  wrong (28/28, 21/21, 21/21), but adopted rules inconsistent with their own example as readily as
  consistent ones.
- Channel effect for one-pass cells, 2-op: Ca − Cas = **+0.133 [+0.029, +0.246]** (Cas J 0.00). Stage 2
  alone lets a little truth through. **Prediction CS1 (|Δ| < 0.05) failed.**
- 1-op: Ca − Cas = **+0.335 [+0.196, +0.467]** (CS2 PASS); Ca 0.53, Cas 0.19.

### C-L3 An external check substitutes for the intermediate step — **Holds at both depths (Da)**
- Registered L5 (2-op, point estimate \|lock − lock_B\| ≤ 0.15): **D FAIL** (mean lock 0.40 vs B
  1.00); **Da PASS** (lock 1.00 = B). Sample decode is too noisy for the registered bar; argmax clears it.
- Amendment L5: Da − Ca, **both depths** (`contrast_da_ca.json`):
  - 2-op: **+0.532 [+0.314, +0.696]**; Da J 0.67, Ca 0.13; B 0.82 for reference (slower than
    reasoning cells: g10 ≈ 0.92 vs B ≈ 0.99 — 2-op only).
  - 1-op: **+0.350 [+0.155, +0.561]**; Da J 0.88, Ca 0.53. The check helps even where a single
    operation looks self-checkable: Life chooses among 101 rules from one example (several may fit);
    ✓/✗ on inbox candidates removes that search. Pair-pref with named options (~0.94) is a different task.
- D (sample decode) 2-op J 0.32 — marks still help through noise; not enough for registered L5.

### C-L4 Identical agents agree without communicating — **Holds as observation (n = 1 task)**
- In one 2-op task (`shift_symbols(1);swap(2,3)`), the first operation alone fits 97% of cells' examples.
  It became a false lock in every arm: Bs 10/10 generations (share 0.78), Ca 0.7 even at the 0.6
  threshold, Cas 0.4, Da 0.7 early then recovered, B 0.1 (corrected by messages within a generation).
- Other false locks (Bs seeds 3/5; Ca seeds 2/5/7) sit at shares 0.50–0.56 and vanish at 0.6: threshold
  artefacts of a ~50/50 split between two consistent rules.
- Holders of the false rule hear «неверно» in ~**90%** of generations (answer correct only ~0.10 when
  `swap(2,3)` is a no-op; `false_holder_feedback.json`) — and in Bs still keep it for all 10 gens.
  One «неверно» without an alternative barely moves a cell: only ~7% of B abandons happen with no P_e
  in the inbox (C-L2). Bs has no channel, so P_e never appears and the cell does not rediscover it; it
  stays on the simplest example-compatible rule. Seed 1 vs seed 5 (same first-op prefix, similar «верно»
  rates 0.10 vs 0.13): the difference is how many cells that simple rule fits — **75** holders vs **47** —
  stable lock vs oscillation near 0.5. An engine check tests consistency (the false rule passes); only
  «неверно» + P_e from a neighbour breaks this kind of agreement.
- Methodological consequence: agreement in a homogeneous population is not evidence of communication;
  every emergence claim needs a no-channel control.

### C-L5 Simplicity: Occam in reasoning cells, default-simple in one-pass cells — **Holds**
At g1 (before any message), all five 2-op tasks:
- Reasoning (B+Bs): **95%** of picks consistent with the cell's example [0.90, 0.99]; among consistent
  picks, single-op share exceeds the even-choice base by **+0.30 [+0.17, +0.41]** (≈ 0 on the task where
  almost no single-op rule fits, as Occam predicts).
- One-pass (Ca+Cas): **21%** consistent [0.04, 0.39]; **91%** of inconsistent picks are single-op
  [0.88, 0.95] — the two-op task is not read, not an Occam choice.
- Sample-decoded arms (C, D) are excluded: picks from a flat mass are near-random over 101 options.

## Prediction record (Life)

| ID | prediction | result |
|---|---|---|
| L1 | B − C lock gap ≥ +0.30, CI ≠ 0 | PASS formally; C-sample is decoding noise (flat Decisions mass), so the one-pass reading uses Ca |
| L2 | B `frac_false_lock_epochs` ≤ 0.10 | **FAIL** — pooled 0.20; 2-op 0.40 (seeds 1,3: one brief false-lock gen → whole epoch); 1-op 0.00. FL_gen only 0.04 on 2-op — epoch metric is harsh |
| L3 | infection Δ > 0 (CI ≠ 0) **and** genesis ≤ 0.05 | infection PASS; genesis **FAIL** (B 2-op genesis ≈ 0.24; \|H\| ≈ 2.5) |
| L4 | B − C gap larger on 2-op than 1-op | PASS — 0.68 vs 0.45 (Ca/B reading; registered uses C-sample) |
| L5 | registered: lock within 0.15 of B (point); amendment: Da > Ca on 2-op | **registered D FAIL** — mean lock 0.40 vs B 1.00 (Δ 0.60); seeds 1/3/5 lock 0. **registered Da PASS** — lock 1.00 all five 2-op seeds (Δ 0.00). **amendment PASS** Da−Ca +0.532 [+0.314, +0.696] |
| L6 | A genesis ≥ 0.5 (descriptive) | **PASS** — A genesis 0.94 pooled (1-op 0.99, 2-op 0.89) |
| Bs forecast | Bs 2-op J ≥ 0.6 | **FAIL** — 0.25 |
| Ca forecast | Ca 1-op high | partial — 0.53 |
| CS1 | \|Ca − Cas\| < 0.05 on 2-op | **FAIL** — +0.133 [+0.029, +0.246] |
| CS2 | Ca − Cas > 0 on 1-op | **PASS** — +0.335 [+0.196, +0.467] |
| CS3 | Cas FL_gen ≥ 0.10 on 2-op | **FAIL** — 0.08 (seed 1 only) |
| CS4 | g1 prompt gap (descriptive) | none (Ca ≈ Cas ≈ 0.00 on 2-op; 1-op g1 Δ ≈ 0.04) |

## Caveats

- One model (`gpt-6-luna` beta), one task family, 5 seeds per depth, one 10-generation epoch.
- C-L4 rests on one task; to make it a rate, build a P_e set where a simpler hypothesis is deliberately
  near-indistinguishable on local examples.
- Lock threshold 0.5 registered; 0.6 sensitivity is post-hoc and only used to separate stable consensus
  from 50/50 splits.
- Unsloth V1 heads (for reference, not Life): conversion works in-domain (typed-decisions 0.78–0.83); no
  transfer to L-VERIFY at either depth (0.58 / 0.52); with ready-made checks pairs 0.98 but full-catalog
  choice 0.34–0.67 vs Luna 0.995.

## Artifacts

`runs/life_reasoning_cells/`: `summary_*.json`, `false_lock_all_arms.json`,
`lock_threshold_sensitivity.json`, `false_lock_diagnostics.json`, `diag_b_mechanism.json`,
`false_holder_feedback.json`, `simplicity_pull_all_2op.json`, `simplicity_pull_abc.json`,
`contrast_ca_cas.json`, `contrast_da_ca.json`, `fig_j_by_gen.png`.
# Task — Can one-pass agents be their own verifier?

**Status:** **locked** 2026-10-15. Predictions are locked with this file, before any number of Parts A–C is
computed or read. Part A: no API. Part B: Luna Decisions, small probe. Part C: Luna Decisions grid,
**conditional** on Part B. Follows `DESIGN_CHECKLIST.md` and the standing rules in `PLAN_NEXT.md`.
Parents: `TASK_LIFE_TECH_LEAD.md` (Ca-r, Da-r, Dr, Mx10/25/50), `runs/life_tech_lead/curves_mx.md`,
`runs/life_tech_lead/reviewer_accuracy.json`.

## Why

One-pass (Decisions) populations on 2-op worlds with four sources, 10 generations (J@g10, seed mean):

| arm | check of incoming rules | J@g10 |
|---|---|---:|
| Ca-r | none | 0.24 |
| Mx10 / Mx25 / Mx50 | none for one-pass cells; 10/25/50% reasoning cells | 0.46 / 0.78 / 0.88 |
| Dr | reasoning-model reviewer at every one-pass cell | 0.70 |
| Da-r | engine: reject a rule that contradicts the cell's own example | 0.92 |

The engine check is exact, free and present at every cell. It does not know P_e; it only uses the
receiving cell's own example. Two questions follow:

1. **Distance.** In the Mx arms, do one-pass cells far from any reasoning cell get the true rule
   later or not at all? A rough guide: P(at least one reasoning neighbour of 8) = 1 − (1 − s)^8 is
   0.57 / 0.90 / 0.996 for s = 10 / 25 / 50%.
2. **Self-check.** Searching 101 rules in one pass fails, but checking one rule against one example
   is a yes/no question. Can the one-pass model answer it well enough to replace the engine, so that
   every agent is its own verifier? For a 2-op rule the check still needs both steps applied in one
   pass, which is exactly where one-pass agents fail at search, so the outcome is open.

## Part A — distance to reasoning cells (descriptive, no API)

Data: existing Mx10 / Mx25 / Mx50 runs, seeds 1–5. Reasoning-cell positions from the run manifests
(`LEAD_SEED`). Sources excluded from every denominator.

For each non-source one-pass cell:
- **k** = number of reasoning cells among its 8 Moore neighbours (torus);
- **d** = torus Chebyshev distance to the nearest reasoning cell (1, 2, ≥ 3);
- **t_first** = first generation in which the cell holds P_e (or "never").

Report per arm, pooled over seeds and per seed (seed 2 always also separately):
- J@g10 and J averaged over g1–g10 among one-pass cells, by k (0, 1, 2, ≥ 3) and by d;
- median t_first by d, and the share never reaching P_e by d;
- cell counts in every bin (bins with < 10 cells are reported but not interpreted).

**A-src — distance to sources (no reasoning cells).** Same analysis for Ca-r and Da-r (and the
original Ca 2-op runs, if their logs are available), with distance measured to the nearest source
(`SOURCE_IDS` [0, 5, 50, 55]). On the 10×10 torus with these sources, every non-source cell is at
d = 1 (32 cells, the sources' Moore neighbours) or d = 2 (64 cells). In Ca a one-pass cell never
finds the 2-op rule alone (0.00 without channel), so every P_e holder got it, directly or through
others, from the four sources. Report J@g10 and J averaged over g1–g10 by d, per seed, and the
share of all P_e holders at g10 that are at d = 1.

Expectations (locked):
- **A1:** pooled over Mx10 and Mx25, one-pass J@g10 decreases with distance: d = 1 > d = 2 > d ≥ 3.
- **A2:** in Ca-r, J@g10 at d = 1 from a source exceeds J@g10 at d = 2 (pooled over seeds); in Da-r
  the gap is smaller than in Ca-r.

## Part B — one-pass yes/no check (single agents, no grid)

**Model and estimator.** Luna Decisions, same endpoint as Ca. Two options, `yes` / `no`, presented in
both orders (P = 2); decision = argmax of the mean probability over the two orders. No reasoning
text requested or stored.

**Prompt.** Fixed file `prompts/self_check_yesno.txt`, committed with this task before the first call:
- `{OPS_SPEC}`: the operation definitions block copied **verbatim** from the Life cell prompt;
- `{EXAMPLE_INPUT}`, `{EXAMPLE_OUTPUT}`: the cell's private example, rendered exactly as in the cell
  prompt;
- `{RULE}`: one rule in the catalog text form;
- question: `Does this rule turn the input into exactly this output?`

**Items.** Real checks the engine made: (receiving cell's example, incoming rule, engine verdict)
events from the Da-r logs, generations 2–10, seeds 1–5. Sampled with a committed seed
(`SELF_CHECK_SEED`) into four strata, 100 items each, balanced over world seeds as far as the pool
allows:

| stratum | rule ops | engine verdict |
|---|---|---|
| C1 | 1-op | consistent |
| I1 | 1-op | inconsistent |
| C2 | 2-op | consistent |
| I2 | 2-op | inconsistent |

Plus a **P_e stratum**: up to 40 items per world seed where the incoming rule is that world's P_e
(all consistent by construction). Report pool sizes; if a stratum's pool is < 100, use all of it.

**Metrics.**
- Accuracy per stratum; balanced accuracy for 1-op (C1, I1) and 2-op (C2, I2).
- False-accept rate (I strata) and false-reject rate (C strata).
- False-reject rate on P_e, per world seed (the Dr reviewer rejected P_e in 70% and 62% of
  reviews in worlds 1 and 3).
- Split of 2-op items by whether the two ops commute (as in `reviewer_accuracy.json`).
- Refusals / invalid, counted separately.

**Predictions (locked).**
- **B1:** 1-op balanced accuracy ≥ 0.90.
- **B2 (primary):** 2-op balanced accuracy < 0.80 — a one-pass model cannot reliably check a
  composition it cannot search for.
- **B3 (descriptive):** P_e false-reject rate per world seed; whether any world shows a Dr-like
  blind spot (≥ 0.50).

**Go / no-go for Part C.** Part C runs only if **2-op balanced accuracy ≥ 0.90 and the P_e
false-reject rate is ≤ 0.10 in every world seed.** Otherwise Part C is not run, and the result is
reported as it stands. A design where only some cells verify ("part of the agents as verifiers")
is a separate amendment after Part B, informed by its numbers.

## Part C — Ds-self (conditional)

| arm | cells | check of incoming rules |
|---|---|---|
| **Ds-self** | one-pass (Decisions) | the receiving cell itself: one Part B yes/no call per distinct incoming rule, against its own example; rules answered `no` are removed |

- Everything else exactly as Da-r: 2-op world seeds 1–5, four sources, 10 generations, memory and
  feedback, catalog, cell prompt, P = 4 for the rule choice. The filter sits where the engine
  filter sits in Da-r; accepted rules reach the cell with their neighbour counts.
- Fallback: a yes/no call that fails after one retry counts as `yes` (no filtering for that rule).
  This can only hurt Ds-self. Counted and reported.
- Same Part B prompt file and estimator; nothing else added.

**Gate.**
- Cell-choice payload byte-identical to Da-r for the same seed, cell and history (runner's request
  builder, raw bytes).
- Yes/no payload byte-identical to the Part B prompt for the same (example, rule).
- Runtime masked check at g2 of seed 1 before any g3 request; fresh empty per-arm cache; per-
  generation log of requests, live/cached, fallbacks; fail if g ≥ 2 has 0 live requests.

**Metrics.** J(g), J@g10 per seed and mean; per-rule check accuracy against the engine verdict (as
for Dr); P_e false-reject rate per seed; false locks; cost.

**Predictions (locked, read only if Part C runs).**
- **C1:** Ds-self seed-mean J@g10 ≥ Da-r − 0.10 (Da-r 0.92).
- **C2:** Ds-self J@g10 ≥ Ca-r J@g10 + 0.30 in ≥ 4/5 seeds.

## Cost

Part A: none. Part B: ≤ 600 items × 2 orders ≈ 1,200 Decisions calls, ≈ $1. Part C: one Da-r run
(≈ $1.19 per seed) plus 2–5 yes/no checks per cell per generation × 2 orders; estimate ≈ $3 per
seed, ≈ $15 total; alarm $25. Report actual cost.

## Artifacts

- `prompts/self_check_yesno.txt`, `SELF_CHECK_SEED` (committed before the first call)
- `runs/life_self_check/partA_distance.md` + `.json`
- `runs/life_self_check/partB_probe.json`, `partB_readout.md`
- `runs/life_self_check/Ds_self/seed{n}/`, `summary.json` (if Part C runs)
- `fig_self_check_distance.png` (one-pass J@g10 by d and by k, per Mx arm)

## Constraints

Closed model outputs are not used as training data. No reasoning text requested or stored. New
scripts only; do not edit running scripts. Commit this file before computing Part A. Amendments
before numbers. Part C is not run without a Part B readout reviewed by Artem.
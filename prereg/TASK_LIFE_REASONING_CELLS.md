# Task — Life with reasoning cells: does a population that can verify spread the right rule?

**Status:** locked (budget $80; design check OK). Predictions locked with this file, before
any torus number from these arms. API-only; no GPU. Placement only: Luna trajectories and
messages are never training data for our models.

**Gate:** (1) v1b M_0 pilot JSON reviewed + torus reachability bound (`reachable`, lock by
g=3 — no geometry amendment); (2) seed schedule (stratified 50/50 by n_ops)
**frozen** in `runs/life_reasoning_cells/seed_schedule.json` (2026-10-10: world_seeds
`1,2,3,4,5,6,7,18,22,29` — 5 unique 1-op + 5 unique 2-op P_e); (3) `TASK_LUNA_REASONING_MODES`
closed; (4) `TASK_LUNA_DEPTH` closed (D1–D5 PASS).

## Why

Same weights, `gpt-6-luna`: one-pass Decisions fails two-op verification (pairs 0.59;
follows a named false 2-op rule 0.76), while Responses with medium reasoning
(~300–700 tokens) is near ceiling (pairs 0.995; follows false 0.036, recovers true 0.96).
The knowledge is in the weights; the one-pass format lacks room for the intermediate step.

In Life this predicts a qualitative difference between populations: cells that can verify
should accept a correct rule from a neighbour and reject a false one; one-pass cells should
lock onto whatever arrives first or most often. v1b supplies verification from outside
(engine marks). This task supplies it from inside (reasoning). Together they separate
"external step" from "internal step" on the same board.

## Design issue: genesis must be impossible

In the v1b seeded arm every non-source cell has two identifying private examples. A
reasoning cell can then solve its rule alone, and a high J would be **genesis**, not
communication. Therefore the key arms use **sparse** non-source examples (one
non-identifying example, as in v1a `sparse=True`), with the seeded `SPARSE_SOLVER_IDS`
sources publishing P_e as in v1b. A cell can then succeed only by receiving a candidate
rule and checking it against its one example.

**Design check (no model, before lock):** from the generator, compute for each P_e the
fraction of other catalog rules consistent with a non-source's single example ("false but
consistent" base rate), by n_ops. If it is high, single-example verification cannot
discriminate and the sparse arms are uninformative — stop and amend.

**Design check close (2026-10-09):** `runs/life_reasoning_cells/design_check_consistency.json`
(+ readable `design_check_consistency.md`). 40 worlds, seed0=5401, sparse=True. Pooled mean
frac other-consistent **0.015** (median 0.01, p90 0.03); mean `|H|` ≈ **2.46** (never
identifying); same on 1-op / 2-op. Band **ok** — do not amend.

**Consequence for reading arm B (locked before any arm number):** a lone cell rejects ~98.5%
of false rules but cannot choose among the ~2.5 survivors (`P_e` + 1–2 false-but-consistent).
Neighbours hold different examples, so a false rule that survives my check almost never
survives theirs. If B passes L1 and L3, that is **collective computation** — messages plus
local checks identify `P_e` though no cell has enough private information alone — not merely
"the rule was transmitted." The descriptive filter metric below makes that claim checkable.

## Arms

All arms: v1b engine (board, delivery, TTL, permutation, epochs, sources), seeded sources,
channel on, same seed schedule (first 10 seeds of the v1b main-run schedule: 5×1-op,
5×2-op P_e), same generations/epochs per seed as the v1b main run (pilot fallback: one
epoch of 10 generations).

| arm | cells | non-source examples | k | channel | role |
|---|---|---|---|---|---|
| **A** | Luna Responses, `effort=medium` | dense (2 identifying) | 0 | on | genesis reference |
| **B** | Luna Responses, `effort=medium` | sparse (1 non-identifying) | 0 | on | **main: internal step** |
| **Bs** | Luna Responses, `effort=medium` | sparse (1 non-identifying) | 0 | **off** | **B-silent:** individual learning floor |
| **C** | Luna Decisions (P=4), `decode=sample` | sparse | 0 | on | registered control (M₀ parity); see Ca for paper one-pass reading |
| **Ca** | Luna Decisions (P=4), `decode=argmax` | sparse | 0 | on | **amendment:** one-pass control for L1/L4 interpretation |
| **D** | Luna Decisions (P=4), `decode=sample` | sparse | 1 | on | registered external step; see Da for L5 reading |
| **Da** | Luna Decisions (P=4), `decode=argmax` | sparse | 1 | on | **amendment:** marks substitute under argmax |

Medium, not high: medium is at ceiling on the probes and cheaper. If the Luna modes task
shows high ≫ medium on any probe, amend before running.

### Amendment — B-silent (locked 2026-10-10, after B seeds 1–3, before remaining B / A / C / D readout)

**Trigger (honest, post-hoc):** on the first three B seeds, lock = 1 and retention ≈ 0.98 vs
adoption `p_with` ≈ 0.56–0.86, but **genesis rate ≈ 0.15–0.31** (seed1 0.15, seed2 0.20,
seed3 0.31) — above the pre-registered L3 ceiling of 0.05. Infection Δ is already large
(`p_with − p_without`: seed1 +0.66, seed2 +0.51, seed3 +0.62; both halves in
`metrics.infection`). So L3 may fail on the genesis clause even if the infection clause
passes. The cause matters for how to read lock + retention.

**Two solo channels (besides messages) that can produce genesis under sparse |H|≈2.5:**
1. **Guess among consistent rules** — a cell that picks any example-consistent rule hits
   `P_e` ≈ 1/2.5 of the time with no messages.
2. **Memory feedback** — memory shows `answer` + `correct` (not the rule name unless
   published). A wrong consistent rule fails the query → next generation the cell can
   eliminate it; after 1–2 errors the survivor set collapses to `P_e`. A reasoning cell
   can then find `P_e` alone in a few generations.

If (2) dominates, high retention is “I learned from my own correctness bits,” not
“a verifying population holds knowledge,” and lock can be the sum of individual learning.

**Control Bs (B-silent):** same Luna Responses medium cells, same sparse examples, same
seeded sources present on the board, **`channel=False`** (no delivered messages; sources
still hold `P_e` but cannot publish into anyone’s inbox). Same seed schedule and
generations as B. Cost ≈ one Responses arm (~$7 at smoke scale).

**Bug (2026-10-10 first Bs run — void):** engine `no_channel` parse forbids a
`communication` field; Luna Responses always encoded `Silence` → every non-source
`inferred_rule` logged as `None` → J=0 artifact. Memory from g2 onward was built on
broken decisions, so a log reparse is not enough — full re-run (g1 may cache-hit; g2+
new API). Fix: encode `communication=None` when `channel=False`
(`luna_cells.map_responses_payload`). First reports →
`archive_bs_nochannel_bug_20261010/`. Forecasts above apply to the **re-run**.

**Invariant (acceptance + runtime, all arms):** if the Completer produced a decision, the
engine-facing encode must parse under the active channel mode with a non-`None`
`inferred_rule` — else **raise**, never log `None`. Layers:
1. Acceptance: `test_11_channel_false_rule_logged` (Silence-under-`no_channel` must fail
   parse; correct encode must appear in `rule_history`).
2. Completer: `assert_encode_logs_rule` after every Responses **and** Decisions encode
   (covers C/D even though they run `channel=True`).
3. Runner: after every `sim.step()` in `run_life_reasoning_cells.py`, every non-source
   cell’s logged rule ≠ `None` (A/B/Bs/C/D).

Decisions already sets `communication=None` when `channel=False`
(`decide_from_answers`); only Bs used Responses + channel off. `_FloorCompleter` fixed
the same way.

- **Predictions L1–L6 are not rewritten.** L3 stays as locked (infection Δ CI excludes 0
  **and** genesis ≤ 0.05). Bs is a reading aid if L3’s genesis clause fails.
- Paper/docs line: *added after B seeds 1–3 showed mean genesis ≈ 0.22; not pre-registered.*
- **L1 (B − C) untouched:** C has the same memory feedback; the contrast is whether the
  cell can *use* feedback and messages (reasoning) vs one-pass.

**Bs forecasts — locked 2026-10-10 before any Bs number** (descriptive; not L1–L6).
Committed to this file before Bs seed1 gen1 completed (no `report.json` yet); do not
edit after the first Bs accuracy / J / lock figure exists:

Risk: the solo path (g1 guess among `|H|≈2.5` → see `incorrect` → eliminate → pick among
remaining) can converge in 2–3 generations. In B that path is rare (~7%) only because
neighbours arrive first. So Bs may also reach lock, only **later** — messages would then
buy *speed*, not *possibility*.

| | locked forecast |
|---|---|
| Bs end-of-epoch | `J ≥ 0.6` by g10 (point; per-seed rows) |
| Timing vs B | Bs reaches high J / lock **later** than B |
| **Primary B − Bs** | (1) `gens_to_correct_lock` (B shorter); (2) **area under J(g)** over g=1…10 (B larger). Final lock / final J are secondary. |
| Readout | If Bs locks with AUC/`gens_to` gap → speed story. If Bs stays below J 0.6 / no lock → messages are necessary for possibility on this stand. |

Message contribution = B − Bs on the primary timing metrics first (seed-level; unpaired
Welch). Report lock/J/genesis/retention beside them.

#### Bs close — post-fix re-run (2026-10-10; all 10 seeds)

Artifact: `runs/life_reasoning_cells/summary_Bs.json` (rebuilt from live
`arm_Bs/seed*/report.json`). Void J=0 summary →
`archive_bs_nochannel_bug_20261010/summary_Bs_void_j0.json` (with the void reports).
Contrast CI: `runs/life_reasoning_cells/b_minus_bs_ci.json`.

**Descriptive forecast FAIL (write like L3 genesis):** locked forecast was
`J ≥ 0.6` by g10. On **2-op** (seeds 1–5): **0/5** meet it; **none lock**
(`censor_rate = 1` on `gens_to_correct_lock`). Mean J ≈ **0.25**, retention ≈ **0.64**
(per-seed retain 0.24–0.76; four of five in 0.72–0.76). Solo path via
`incorrect` → eliminate → pick among remaining **does not** converge on this stand.
Cells keep a false-consistent rule; feedback alone is not enough. Matches the B
mechanism split (~**7%** memory-only path to `P_e`).

On **1-op** the same forecast mostly holds (4/5 ≥ 0.6; all five lock). **Seed 7** is
the exception among 1-op: Bs J ≈ **0.69** vs B ≈ **0.93** (Δ ≈ +0.24) — descriptive
only; a hard 1-op where messages also help. Do not average it into the 2-op claim.

**Primary contrast (2-op, n=5, paired by seed):** mean(B − Bs) on epoch J =

| | B | Bs | B − Bs |
|---|---:|---:|---:|
| mean J | 0.822 | 0.248 | **+0.574** |
| lock | 5/5 (g2–g4) | 0/5 | — |
| per-seed ΔJ | | | +0.54…+0.65 (all five > 0) |

- Seed bootstrap 95% CI for mean ΔJ (100k resamples of the five paired Δ’s,
  rng seed 20261010): **[+0.547, +0.614]** — excludes 0 (three-way `>`).
- One-sample *t* on the same Δ’s (df=4): **[+0.520, +0.628]**.
- Sign: 5/5 positive → one-sided *p* = **1/32**, two-sided **1/16**.
- AUC under J(g) (trapz, g=1…10): mean ΔAUC ≈ **+5.38**, bootstrap CI
  **[+5.12, +5.75]** — same direction (primary timing metric from the locked table).

**Paper line (locked for this close):** on 2-op, messages buy **possibility**, not
speed. The population finds the two-op rule; silent individuals with the same examples
and correctness bits do not. That is collective computation under a control, not only
a contagion description. (1-op is near the individual ceiling — not the test case.)

**No-feedback arm:** gated on “if Bs reaches lock.” On 2-op it did not → **do not
queue** the no-correctness-bit arm for this paper unless a later design needs it.

**Figure (after C and D close):** one plot, two panels (1-op / 2-op): J(g) for
B, Bs, C, D plus the ideal-cell reachability upper bound. Central Life figure;
build only once L1 (B vs C) and L5 (D vs B) are read out.

**If Bs reaches lock** (after this run’s readout): for a design where communication is
truly required, add a **separate** arm with no correctness bit in memory (solo stuck near
~1/|H|≈0.4; level-2 of the mechanism loses the memory half — open whether majority among
consistent candidates still works). That arm **does not amend frozen v1a**; only a new
condition after the present A–D+Bs queue.

**Queue:** insert Bs after B finishes and **before** A (then C, D). Do not interpret remaining
B seeds or A/C/D until Bs is at least launched; primary B−Bs contrast waits for n=5+ on both.

**Free diagnostics on existing B `rule_history` (no API):** script
`runs/diag_life_reasoning_b_spread.py` → `runs/life_reasoning_cells/diag_b_spread.json`.

1. **Spatial:** for each non-source cell’s first generation with inferred rule = `P_e`,
   distance (torus Chebyshev) to nearest source. Contagion → shorter distance earlier;
   solo learning → flat in distance.
2. **Genesis by generation:** share of genesis hits (new `P_e`, `P_e` ∉ inbox) at g=1…10.
   Feedback story predicts mass at g2–g3 after the first correctness bit.
3. **At first `P_e` choice:** whether `P_e` was in the delivered inbox this generation and/or
   the previous one. (Memory `previous_correct` is **not** in `rule_history`; Bs is the
   clean measure of solo learning. Optional later: dry replay to recover queries.)

**Infection Δ on B:** always report both `p_with_inbox` and `p_without_inbox` (already in
`metrics.infection`); do not quote adoption alone.

**Mechanism reading from s1–3 diagnostics (descriptive; not a prediction rewrite):**
genesis hits concentrate at **g1** (not g2–g3) → first-gen guess among `|H|≈2.5`, not
memory feedback. L3 genesis ≤ 0.05 was written before the design check and **is not
revised**; that clause will fail honestly; the infection clause is expected to pass with
margin.

**Two-level filter — paper mechanism line (s1–3; `diag_b_mechanism.json`):**

1. **Level 1 — local check.** A rule inconsistent with the cell’s own example is not
   adopted ≈ **98%** of the time (reject-on-sight).
2. **Level 2 — among ~1.5 consistent candidates.** ≈ **87%** of switches onto `P_e` need
   **both** signals: memory says the last answer was wrong, and the inbox carries `P_e`.
   Either alone is rare (~**7%** memory-only, ~**7%** neighbours-only; **0%** with a
   correct past answer and empty `P_e` inbox).

Collective computation in the strict sense: private feedback or messages alone do not
yield the answer; together they do. (False-consistent names cannot be killed by the
example check — that is why level 2 exists.) Bs tests how far memory-only goes when
neighbours never arrive.

v1b `M_0` arms (k=0/1/2) are reported beside these descriptively; they are not part of the
predictions.

## Cell adapter (Responses A/B and Decisions C/D)

Completers return `encode_decision` strings; engine / logs / metrics unchanged.

**B↔C parity (locked before smoke — do not treat residual Δ as “reasoning” if broken):**

| | Responses (B) | Decisions (C/D) |
|---|---|---|
| State | `render_state_v1b` (typed) | same |
| Rule options | 101 bare `fn.description()` keys in prompt | same 101 as choice criteria |
| Abstain | **none** (schema enum = 101 keys) | **none** |
| `say` | bound to chosen rule (no schema field) | bound in `decide_from_answers` |
| `task_answer` | engine `rule.apply(query)` | same |
| Option order | catalog lines shuffled by `order_seed` | P=4 criterion shuffles, averaged |
| Decode | one generative sample (Responses) | registered C/D: `decode=sample` (= `JEV_DECODE`); **Ca/Da:** `argmax` |

- Responses structured JSON (`life_cell_decision_v2`): `inferred_rule` + `communication`
  (`silence` | `publish`+`signal` only). No stand jargon in the instruction block.
- Invalid / truncated → one re-sample (`retried` logged) → else Silence +
  stand-internal `inferred_rule=unsolved` (not a legal model choice); counted per arm.
- Descriptions match L-VERIFY / Luna pair probes (names only, no op definitions) — verified
  before smoke; L1’s 0.995 prior uses that surface.
- Cache: sha256(model, effort, full prompt incl. shuffled catalog, catalog digest, `draw`).
  `draw` = cache-key disambiguator only, not an API sampling seed.
- C/D cost: **P=4 × 3 questions = 12** Decisions API calls per cell per generation
  (rule + communication + signal). Ca/Da share the Decisions **API** cache with C/D
  (`cache_C` / `cache_D`); decode is client-side after P-average — g1 mostly free,
  g2+ diverge and need new calls.

### Amendment — C/D decode: sample vs argmax (locked 2026-10-10, after C sample close, before any Ca/Da number)

**Trigger.** Registered C (`decode=sample`) finished 10/10: mean J ≈ **0.027**, lock **0/10**,
even on 1-op (J ≈ 0.04). Formal L1 (B − C lock = +1.0 on all seeds) **PASS**, but that
contrast is not interpretable as “reasoning vs one-pass.” Luna Decisions on the same
pair probes already verifies single rules well (~**0.94**) and, when the true rule is
named, picks it by **argmax** in ~**0.84** of cases — yet the **mass** on the true rule
is only ~**0.16** (Part-2 smear). Sampling from the P-averaged π over 101 rules is near
noise; J ≈ 0.03 and retention 0.13–0.38 match that. We chose `sample` for M₀ parity;
for Luna the calibration makes sample a different experiment.

**Registered C (and D-sample) stay.** Report them. Do **not** rewrite L1–L6 text. Do
**not** claim “one-pass cannot spread the rule” from C-sample alone.

**New arms (amendment; not rewriting frozen L1–L6):**

| Arm | Same as | Decode | Cache |
|---|---|---|---|
| **Ca** (C-argmax) | C (sparse, k=0, Decisions P=4) | `argmax` | share `cache_C` |
| **Da** (D-argmax) | D (sparse, k=1, Decisions P=4) | `argmax` | share `cache_D` |

D-sample continues / finishes as registered. Da is the parallel decode for L5 reading.
Queue (timing): **Ca runs in parallel with D-sample** (both API-only; Ca shares
finished `cache_C`, so no write race with D). **Da after D-sample** (shares
`cache_D` — avoid concurrent cache writes). D-sample still completes — registered.
No Ca/Da numbers existed when the forecasts below were written (lock = before first
`arm_Ca` / `arm_Da` `report.json`).

**Ca forecasts — locked before any Ca number** (descriptive; paper L1 reading uses these):

| | locked forecast |
|---|---|
| Ca **1-op** | high J / likely lock — single-rule verification ~0.94 on probes; argmax should land near `P_e` often enough to spread |
| Ca **2-op** | low J / no lock — pair probes ~0.59; follows a false consistent rule ~76% |
| **B − Ca** | large on 2-op, small on 1-op — the L4 *shape* (registered L4 on C-sample looks inverted because sample noise flattens both ops) |
| Paper line for “one-pass vs reasoning” | **only Ca**, not C-sample |

**Ca close (after 10/10; honest vs forecast):** 1-op J ≈ **0.53** / lock 0.8; 2-op J ≈ **0.14** / lock 0.4.
B−Ca ΔJ: 1-op ≈ **0.45**, 2-op ≈ **0.68** — L4 *direction* (gap larger on 2-op) holds, but
“1-op high / small B−Ca” is only **partial** (0.53 is mid, not probe-level 0.94). Reading:
pairs = *check* two candidates; Life cell = *search* among 101 from one example — one-pass
search is weaker; messages help but do not restore verification-band J. Artifact:
`summary_Ca.json`, `contrast_life_b_ca.py` → `contrast_b_ca.json`.

**Da / L5 reading:** evaluate L5 (D within 0.15 lock of B) on **Da** as the
marks-substitute contrast; report D-sample beside it. If Da fails while B locks, that
is a marks/one-example limit; if only D-sample fails, that is decode noise again.

**L4 reading:** registered L4 uses C-sample (likely artifactual). The informative L4-shaped
claim is B − Ca by n_ops — secondary to registered L4, stated as amendment.

## Acceptance (before any arm)

Run the v1b acceptance suite with the new Completer in place:
- sources excluded from denominators; sources never call the model;
- model-visible state ↔ logged marks parity (arm D);
- **determinism is redefined for API cells:** replaying a run from cache is byte-identical;
  live re-runs may differ and that is reported, not hidden;
- sparse flag produces exactly one non-identifying example for every non-source cell
  (check against the generator on all seeds).

## Cost / time gate (smoke)

**Budget cap (unchanged):** **$80** list-rate USD for the full A–D run at the pilot
fallback size (10 seeds × 1 epoch × 10 gens), plus the 1-gen smokes. Rates:
Responses input $0.10/M, cached input $0.01/M, cache writes $0.125/M, output incl.
reasoning $0.50/M; Decisions input $0.10/M (no output). Parallelism: **16**.

**Smoke close (2026-10-09)** — artifact `runs/life_reasoning_cells/smoke_cost.json`
(world_seed=5401, 1 gen, 96 model cells; usage only).

| smoke | API calls | tokens (in / out / reason) | $ smoke | $ / cell |
|---|---:|---|---:|---:|
| **B** Responses medium | 96 (0 invalid) | 198k / 48k / 45k | **0.068** | 0.00071 |
| **C** Decisions P=4 | **1152** (=96×12) | 999k / 0 / — | **0.100** | 0.00104 |

Mean Decisions input ≈ **867 tok/request** (rule questions larger; comm/signal smaller —
not 1.3k×4 alone). Wall: B ≈ 43 s; C ≈ 213 s at 16 workers.

**Locked projection to full A–D** (scale smoke $ × cell-steps; no cut):

| piece | scaled $ |
|---|---:|
| A+B (19200 Responses calls) | **13.70** |
| C+D (230400 Decisions calls) | **19.98** |
| **A–D total** | **33.68** |

Within $80 with headroom. Do **not** drop A or shrink seeds on cost grounds. Full run
still gated on: (1) design check ✓; (2) v1b M_0 pilot reviewed + seed schedule; (3) Luna
modes high+CI closed.

## Metrics

v1b `metrics_bundle`: J, `frac_correct_lock_epochs`, `frac_false_lock_epochs`,
`gens_to_correct_lock` (censored), infection Δ (delivered inbox contact), **retention**,
genesis rate — all on non-source cells, all split by n_ops. Statistics: bootstrap over
seeds (cluster = seed/P_e); report per-seed rows. Lock = modal share ≥ 0.5 (registered).

**Upper bound on every torus plot:** the ideal-cell reachable fraction by generation from
`runs/life_verify/reachability_bound.json` (g1: 0, g2: 0.33, g3–g10: 1.0 under current
geometry). Plot real J against that curve; do not read a low J as a geometry failure.

**Descriptive — adoption vs retention (locked before arm numbers; from M_0 pilot):**
- **Adoption** = infection `p_with_inbox` =
  `P(P_e at g+1 | not P_e at g ∧ P_e in delivered inbox at g+1)`.
- **Retention** = `P(P_e at g+1 | P_e at g)` (`metrics.retention_non_source`).

Pilot on the M_0 `seeded_local_k2` pilot (`runs/life_verify/v1b_m0_pilot/retention_adoption.json`):
mean adoption ≈ **0.24**, mean retention ≈ **0.20**. Retention is **not above**
adoption → no accumulation: whether a cell holds P_e next generation barely depends on
holding it now; each generation is a fresh choice from the current inbox. J zigzags;
lock needs almost all neighbours to publish P_e together.

**Memory surface (checked 2026-10-10, before A–D):** constitution text says
“one-step memory of your last answer.” Code (`constitutional_life.cell.memory`,
`_render_memory`):
- Fields: `previous_task_answer`, `previous_correct`, and if published
  `previous_signal` + `previous_say`; else “silence”.
- **`inferred_rule` is excluded on purpose** (module docstring).
- Rendered non-empty line:
  `Previous step: answer=<task string> correct=<bool> published signal=… say='<rule>'`
  or `… silence.`
- So the **rule name enters memory only if the cell published** (`say` is bound to the
  chosen rule). A cell that holds P_e silently sees only last answer + correctness, not
  the rule name. The reachability ideal always publishes, so its “adopt and hold” bound
  is slightly optimistic relative to a silent holder; for a verifying population that
  publishes once majority has P_e, the bound remains the right plot reference.

**Descriptive forecast for arm B (locked before numbers, next to `retention`):**
retention should be **noticeably above** adoption (verifying cell that once chose the
true rule re-confirms it). If B’s retention ≈ adoption (M_0-like), the stand lacks
rule memory for silent holders and the population cannot accumulate knowledge — that is
a **stand amendment**, not an arm-B cell failure. Report adopt vs retain on every arm.

**Descriptive — population filter (arm B primary; C/D beside; locked before numbers):**
for each non-source cell that ends the epoch with inferred rule = `P_e`, ask whether on
the path to that choice it ever held (from a delivered inbox message) a rule that was
*false but consistent with its own single example*, and later abandoned it in favour of
`P_e` (or never adopted it after seeing it). Report
`frac_filtered_false_consistent` = share of such end-correct cells that filtered at least
one false-but-consistent candidate. Also report mean count of distinct false-consistent
candidates seen-and-rejected per end-correct cell. Split by n_ops. Not a prediction gate —
if L1+L3 pass and this fraction is near 0, success may be "lucky first message = `P_e`"
rather than population-level discrimination; if high, the collective-computation reading
is supported.

## Predictions (lock)

- **L1 (primary):** sparse, k=0: `frac_correct_lock_epochs` B − C ≥ **+0.30**, seed-bootstrap
  CI excludes 0. Reasoning cells spread the right rule; one-pass cells with the same
  weights do not.
- **L2:** arm B `frac_false_lock_epochs` ≤ 0.10.
- **L3:** in arm B growth is contagion, not genesis: infection Δ > 0 with CI excluding 0,
  and genesis rate ≤ 0.05.
- **L4:** the B − C gap is larger on 2-op than on 1-op P_e (point estimates).
- **L5 (external vs internal step):** arm D `frac_correct_lock_epochs` is within 0.15 of
  arm B (point estimate) — engine marks substitute for reasoning, to the extent one example
  allows.
- **L6 (descriptive):** arm A is genesis-dominated (genesis rate ≥ 0.5): with identifying
  examples, reasoning cells do not need each other.

## Readout

- L1 + L3 PASS → verification-gated rule spread; with the design-check `|H|≈2.5` and a
  non-trivial `frac_filtered_false_consistent`, read as **collective computation** (no cell
  alone determines `P_e`). The design for "our own" cells follows: a decision model with the
  step amortised (Part C / recursive amortisation), evaluated in arm-B conditions.
- L1 PASS, L3 FAIL → reasoning cells succeed but not through messages; recheck the
  sparse/genesis design check. **With Bs:** if B ≈ Bs, solo learning (guess + memory
  feedback) explains the result; if B ≫ Bs, messages still carry the surplus even when
  absolute genesis on B exceeds 0.05.
- L1 FAIL → verification on the probes does not translate into population behaviour on this
  board (e.g. message routing, TTL or memory limits); compare with v1b k>0 arms to locate
  the bottleneck.
- L5 PASS → engine checks are a cheap substitute for reasoning in Life; v1b is the right
  platform for training. L5 FAIL with L1 PASS → one example is too weak for marks, reasoning
  uses more (memory, multiple messages); report.

## Artifacts

- `runs/life_reasoning_cells/design_check_consistency.json`
- `runs/life_reasoning_cells/sample_prompt_review.md` (+ `.json`) — **review before any API arm** (Responses full prompt + schema; Decisions surface preview; k=1 mark appendix). Regen: `runs/diag_life_reasoning_sample_prompt.py` (no API).
- Completers: `life_verify/v1b/luna_cells.py` (`LunaResponsesCompleter`, `LunaDecisionsCompleter`); sparse+seeded: `SimulationV1b(allow_sparse_seeded=True, sparse=True)`.
- `runs/life_reasoning_cells/smoke_cost.json` (usage only)
- `runs/life_verify/reachability_bound.json` (ideal curve; plot reference)
- `runs/life_verify/v1b_m0_pilot/retention_adoption.json` (M_0 adopt/retain baseline)
- `runs/life_reasoning_cells/arm_{A,B,Bs,C,Ca,D,Da}/seed{n}/report.json` + `rule_history.json`
- `runs/life_reasoning_cells/diag_b_spread.json` (spatial / genesis-by-gen / first-P_e inbox)
- `runs/life_reasoning_cells/diag_b_filter.json` (population filter; s1–3 interim)
- `runs/life_reasoning_cells/diag_b_mechanism.json` (reject-on-sight + abandon buckets)
- `runs/life_reasoning_cells/summary.json` (contrasts with CIs, by n_ops)
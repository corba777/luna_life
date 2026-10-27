# PAPER_CLAIMS — Life with reasoning cells (draft)

**Provenance (2026-10-27).** This file is the closed claims board for the earlier Life world
(several examples, feedback, seeded sources). It is superseded for the arXiv write-up by
`PAPER_LIFE_DRAFT.md`; keep it as the provenance record of locked predictions and outcomes.

2026-10-27. Corrected: e6d80f9 restored the wrong base (pre–2026-10-13 restatements). This
commit restores blob 450c862… then reapplies the provenance fold only.

**Models / modes context:** `CONTEXT_MODELS.md` (SPADE-4B = third-party HF checkpoint; cot/direct
prompt modes; G2/G3 reading; related work). Facts only there; claims stay in this draft /
`PAPER_CLAIMS.md`.

**Status:** Life claims C-L1–C-L8 + W/K/E **closed**; **C-L1 restated 2026-10-13** (own-memory
Bs arms: **M1 PASS / M2 FAIL**); **C-L7 / M3 PASS**; **C-L4 persistence withdrawn (M5)**;
**M4 PASS** (Cas-mem ≈ Cas-r on 2-op). Own-memory **closed** (`summary.json` / `run.ok`).
Tech-lead (C-L9) **closed 2026-10-12**; publish-void **closed 2026-10-13** (V1 PASS / V2 FAIL).
Discovery-echo closed 2026-10-12 (E1 PASS; E2/E3/E5 confounded). **Still open:** Dr-cat
(`TASK_LIFE_TECH_LEAD_CAT.md`) and Ca0/Da0 (`TASK_LIFE_ONEPASS_NO_SOURCE.md`). Do not merge into
`PAPER_CLAIMS.md` until those fold. L2/L6 and mechanism % verified 2026-10-11 against
`TASK_LIFE_REASONING_CELLS.md` + `diag_b_mechanism.json`.

Source task: `TASK_LIFE_REASONING_CELLS.md` (seeds `924cabf`), amendments Ca/Da (argmax) and
`AMENDMENT_LIFE_CAS.md` (`def912a`). Model: `gpt-6-luna` (public beta), Responses `effort=medium` for
reasoning cells, Decisions API for one-pass cells. Torus 10×10, sources `SPARSE_SOLVER_IDS` 0/5/50/55,
sparse non-identifying examples, one 10-generation epoch, 5 seeds per depth. J = non-source share holding
P_e, epoch mean. Lock = modal share ≥ 0.5 (registered); 0.6 = post-hoc sensitivity only. CIs = bootstrap
over seeds (cluster = task) unless stated.

## Headline

> Single rules are solved by each reasoning cell alone. Two-step rules are solved when a reasoning cell
> can see its own previous rule, or via the channel (or an external check) — own-rule memory carries
> most of the two-op gain that was once credited to messages alone (M1 PASS, M2 FAIL).

## Claims

### C-L1 Two-op rules need own-rule memory or the channel — **Withdrawn in prior form; restated (M1 PASS, M2 FAIL)**
- **Prior form withdrawn (2026-10-13):** “Messages make two-op rules possible, not just faster”
  (B − Bs as a pure channel effect). Bs also cleared the cell’s memory of its own previous rule
  (`say` on silence); that contrast confounded messages with own-rule memory.
- **Restatement (registered readout M1 PASS, M2 FAIL):** Reasoning cells solve two-op rules alone
  when they see their own previous rule (Bs-mem J@g10 **0.89** vs Bs-r **0.25**, **5/5** seeds).
  Own-rule memory raises self-revision after `correct=false` (**0.31** vs **0.11**) and retention
  after `correct=true` (**0.997** vs **0.69**). The channel adds about **0.10** at g10 (B **0.99**).
  Artifacts: `runs/life_own_memory/m1_retention_hazard.md`; parents B in
  `runs/life_reasoning_cells/`.
- Numbers kept for provenance (mean J over gens, pre–own-memory): 2-op B 0.82 / Bs 0.25,
  B − Bs = **+0.574 [+0.547, +0.614]**; 1-op B 0.99, Bs 0.93; dense A J ≥ 0.96.
- **Post-hoc (not pre-registered), labelled:**
  - Bs-r equilibrium check: \(h/(h+1-r)\) with Bs-r self-revision hazard \(h\) and retention \(r\)
    ≈ **0.26** vs observed seed-mean J@g10 **0.25**.
  - B’s lower self-revision hazard (**0.04**) vs Bs-mem (**0.31**) is an **open question**
    (selection vs herding); **no claim**.
  - Earlier post-hoc from `hazard_by_prev_publish_B_exact.md` (published vs silence hazards both
    ≈ 0.04 → “discovery does not depend on memory”) is **contradicted** by M1’s controlled
    contrast (Bs-mem vs Bs-r).
- **Channel constitution (every channel-on vs off contrast):** live prompts include
  “You may publish at most one message…” / eight message slots; silent prompts replace that with
  “You cannot send or receive messages” and omit the inbox block
  (`prompts/arm_pair_diff_audit.md`).

### C-L2 Collective correction has two stages; one-pass cells have only the second — **Holds (mechanism on B/Ca); channel Δ vs Cas was confounded with own-rule memory; M4 PASS (2-op |Cas-mem − Cas-r| J@g10 = 0.0167 < 0.05; `runs/life_own_memory/m4_cas_mem.md`)**
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
- **Confound (2026-10-13) / M4 readout:** Cas also lacks own-rule memory. Ca − Cas / CS1–CS2 mix
  channel with that memory. Unconfound arm Cas-mem (`TASK_LIFE_OWN_MEMORY.md`). **M4 PASS:** on
  2-op, seed-mean |Cas-mem − Cas-r| J@g10 = 0.0167 < 0.05 (`runs/life_own_memory/m4_cas_mem.md`,
  `summary.json`); one-pass cells do not gain composition from restoring own-rule memory. 1-op
  contrast descriptive (|Δ| seed-mean 0.0646).
- **Channel constitution:** same “You may publish…” vs “You cannot send…” + inbox block vs none
  (`prompts/arm_pair_diff_audit.md`).

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

### C-L4 Identical agents agree without communicating — **Holds as observation (n = 1 task) for g1 / no-memory silent lock; persistence withdrawn (M5); sustained lock ≠ “without channel”**
- In one 2-op task (`shift_symbols(1);swap(2,3)`), the first operation alone fits 97% of cells' examples.
  **g1 false majority** on `shift_symbols(1)` (~0.76–0.79) appears in B, Bs-r, and Bs-mem alike
  (`c_l4_bs_mem_false_lock_seed1.md`) — example fit / Occam, not a channel effect.
- **Sustained** false lock across the epoch: **Bs-r 10/10** (share ~0.78; no own-rule memory).
  **Bs-mem does not** (false lock **g1 only**, then correct lock on P_e from g2; J@g10 0.84).
  Do **not** restate like K4 (“also present without the channel”): the sustained silent lock was
  the **no-memory** control, not silence alone. Parent Ca / Cas / Da false-lock rates (Ca 0.7 at
  0.6 thresh, Cas 0.4, Da early then recovered; B corrected within a generation) unchanged.
- Other false locks (Bs seeds 3/5; Ca seeds 2/5/7) sit at shares 0.50–0.56 and vanish at 0.6: threshold
  artefacts of a ~50/50 split between two consistent rules.
- Holders of the false rule hear "wrong" in ~**90%** of generations (answer correct only ~0.10 when
  `swap(2,3)` is a no-op; `false_holder_feedback.json`). One "wrong" without an alternative barely
  moves a channel cell: only ~7% of B abandons happen with no P_e in the inbox (C-L2). Seed 1 vs
  seed 5 (same first-op prefix, similar "correct" rates 0.10 vs 0.13): the difference is how many
  cells that simple rule fits — **75** holders vs **47** — stable lock vs oscillation near 0.5. An
  engine check tests consistency (the false rule passes). Breaking the lock: neighbour P_e (B) **or**
  own-rule memory after `correct=false` (Bs-mem) — not only the channel.
- Methodological consequence: agreement in a homogeneous population is not evidence of communication;
  every emergence claim needs a no-channel control — and that control must not also strip own-rule
  memory if the claim is about the channel alone (`DESIGN_CHECKLIST.md`).
- **Persistence restated (M5, seed 1, descriptive):** Silent cells “persist” (Bs-r **0.94**) because,
  without their previous rule in memory, they **re-derive the same rule from the same examples**; with
  own-rule memory, persistence after `correct=false` is **0.08** (Bs-mem). The persistence part of
  C-L4 is **withdrawn as a property of the world** and attributed to the missing memory line
  (`m5_persistence_seed1.md`).

### C-L5 Simplicity: Occam in reasoning cells, default-simple in one-pass cells — **Holds**
At g1 (before any message), all five 2-op tasks:
- Reasoning (B+Bs): **95%** of picks consistent with the cell's example [0.90, 0.99]; among consistent
  picks, single-op share exceeds the even-choice base by **+0.30 [+0.17, +0.41]** (≈ 0 on the task where
  almost no single-op rule fits, as Occam predicts).
- One-pass (Ca+Cas): **21%** consistent [0.04, 0.39]; **91%** of inconsistent picks are single-op
  [0.88, 0.95] — the two-op task is not read, not an Occam choice.
- Sample-decoded arms (C, D) are excluded: picks from a flat mass are near-random over 101 options.

### C-L6 No teacher needed at default evidence — **Holds**
- B0 (no sources): J at g10 0.98–1.00 in 5/5 seeds (W6 PASS). At g1, 23–39% of cells hold P_e
  alone; messages plus checking select it. Seed 1: a 23% minority overturns a 75% false majority
  by g3 (W7 FAIL: I predicted a false lock).
- One-pass cells depend on the source: with an engine check, a single source's rule crosses the
  grid (Da1 J 0.92, W4 PASS; 80% source ancestry); without it the wave dies (Ca1 0.101, W3 FAIL
  by 0.001).

### C-L7 Without any initial holder, the true rule can still appear; at high ambiguity own-rule memory restores silent self-revision — **Holds (E1); M3 PASS restates the silent arm**
- Critical mass: with g1 solo share ≤ 0.05, P_e was modal at g10 in 5/8 runs, including runs with
  zero holders at g1 (K2 FAIL).
- Echo replication at the highest ambiguity: unreceived proposals of P_e, KH-r 47 events / 44 cells /
  4 of 5 seeds vs KHs-r 0 (E1 PASS).
- With a live channel, proposals come from cells extending their own one-op partial rule (47/47 held
  exactly one op of P_e), not from combining a neighbour's other op (0/47; the other op was in the
  inbox in 338 at-risk cases, always among other rules).
- With the channel off and one placebo rule shown (KHp), 6 cells proposed P_e (11 events); in 10/11
  the placebo carried the missing op — recombination happens when the missing piece is presented
  alone.
- **Pre-V1/M3 conjecture (mechanism open / untested when written):** The synthetic-inbox arms are
  confounded with the cell's own publication (E2/E3/E5 not interpretable). Leading hypothesis then:
  a cell that published a rule and was told it was wrong revises; a silent one does not. Supporting
  post-hoc contrast: live cells with a single inbox entry equal to their own rule propose at 3/251,
  KHe (same inbox, silent) at 0/4135. Publish-void / own-memory later tested the publication and
  memory pieces (V1 PASS; M3 PASS).
- **Confound (2026-10-13) → M3 PASS:** KHs-r / KHe silence also cleared own-rule memory. KH-r −
  KHs-r (E1) mixed channel/publication with that memory. **Channel constitution** also differs
  (“You may publish…” vs “You cannot send…”; `prompts/arm_pair_diff_audit.md`). Publish-void:
  **V1 PASS** (KHe-pub hazard ≈ 0.042); **V2 FAIL** — KHv vs KHs-r is **not** memory-only
  (published memory **+** empty inbox block **+** channel constitution). **Clean memory-only
  published contrast:** KHe vs KHe-pub (same synthetic self-echo inbox) — hazard **0 vs ≈ 0.042**.
  **Registered unconfound (M3 PASS):** KHs-mem pooled self-revision hazard **0.039** (142/3642;
  4/5 seeds) ≥ 0.02, vs KHs-r **0** — unreceived proposals at KH ambiguity appear from remembering
  one's own refuted rule without publication. Artifact: `runs/life_own_memory/m3_khs_mem.md`.
- **Descriptive (not a channel claim):** KHs-mem seed-mean J@g10 **0.284** vs KH-r **0.114**
  (higher in **4/5** seeds). KH-r silent cells still lacked their own rule in the memory line, so
  this is not “memory beats the channel.” Clean follow-up (not queued): **KH-r with `held_rule`
  for silent cells**.
- **Descriptive — false majority without a channel:** KHs-mem `frac_false_lock_gens` **0.3–0.5**
  (no correct locks) with the channel off. False majority at KH level arises without communication;
  wording that the channel produces false consensus (**K4** and related) is restated: **also
  present without the channel**.
- **Post-hoc (not pre-registered):** unreceived P_e proposal hazard split by whether the cell
  published at g−1 — `runs/life_discovery_echo/hazard_by_prev_publish.md` (KH-r clear;
  B heuristic not interpretable). Exact B stratum:
  `hazard_by_prev_publish_B_exact.md` (pub ≈ sil ≈ 0.04). That near-equality was briefly read as
  “discovery does not depend on memory”; **contradicted** by own-memory M1 (C-L1 restatement).

### C-L8 At high ambiguity, retention, not discovery, limits convergence — **Observation (post hoc)**
- Share still holding P_e after being told correct: K2 0.97, B0 0.97, K4 0.92, KH 0.82, KH-r 0.61.
- KH-r: when every neighbour holds the one-op half of P_e, 5/33 keep it (0.15); with mixed inboxes
  95/132 (0.72). Most cells told they are right (28/33) abandon the true rule when every neighbour
  shares the simpler one-op rule.
- KH-r J at g10 ≤ 0.37; P_e modal in 0/5 seeds (E4).
- Caveat: 33 eligible events, concentrated in seeds 1 and 5.

### C-L9 A reasoning reviewer fails when the notation is ambiguous — **Holds (T1/T2 FAIL as registered; cause locked post hoc)**
- Tech-lead Dr (prompt v3, no rule catalog): per-rule accuracy **0.896** (T1 FAIL, bar 0.95);
  J@g10 **0.696** vs Da-r **0.923** (T2 FAIL, need ≥ 0.823). T3 PASS (Mx juniors rise with lead
  share); T4 FAIL; T5 descriptive (`runs/life_tech_lead/summary.json`,
  `fig_tech_lead.png` — **reasoning tokens / reasoning-$ only; total-cost version pending
  → see `fig_tech_lead_total_usd.png`**).
- **Cause (logs only; verdicts unchanged):** the reviewer read `swap(i,j)` as **1-based**.
  Among engine-consistent rules with a swap: FR **0/166** when a 1-based reading still fits the
  example, **827/1208 (0.685)** when it fails; FR **0.043** when the swap includes index 0
  (1-based remap invalid). Of 20 false accepts involving a swap, **15** become consistent under
  1-based (`swap_index_diag.md`). Seeds 1 and 3 (P_e with swap without 0) are exactly the
  collapsed runs (P_e FR 0.70 / 0.62).
- **Design error (record as such):** prompt v3 dropped the rule catalog — the only place cells
  (and B) see entries like `swap(0,1)` that fix the 0-based convention. Checking failed because
  the **notation** was underspecified, not because consistency reasoning is hard. Post-hoc
  counterfactual (subtract those 827 FR + 15 FA): accuracy ≈ **0.98** — would clear T1; **not** a
  registered estimand.
- Remaining: **90** non-swap false accepts (mostly seeds 1/3) — separate, smaller error.
- Paper line: a checker is only as reliable as the specification; one missing fact (indices from
  0) turned a near-engine reviewer into a truth-blocker on 2/5 tasks. Ties the Life caveat that
  cells see **rule names**, not op definitions.
- Follow-up (registered separately): `TASK_LIFE_TECH_LEAD_CAT.md` — Dr-cat restores the catalog
  in the reviewer prompt (T1c/T2c/T6); no explicit “from 0” sentence in that arm.

## Prediction record (Life)

| ID | prediction | result |
|---|---|---|
| L1 | B − C lock gap ≥ +0.30, CI ≠ 0 | PASS formally; C-sample is decoding noise (flat Decisions mass), so the one-pass reading uses Ca |
| L2 | B `frac_false_lock_epochs` ≤ 0.10 | **FAIL** — pooled 0.20; 2-op 0.40 (seeds 1,3: one brief false-lock gen → whole epoch); 1-op 0.00. FL_gen only 0.04 on 2-op — epoch metric is harsh |
| L3 | infection Δ > 0 (CI ≠ 0) **and** genesis ≤ 0.05 | infection PASS; genesis **FAIL** (B 2-op genesis ≈ 0.24; \|H\| ≈ 2.5) |
| L4 | B − C gap larger on 2-op than 1-op | PASS — 0.68 vs 0.45 (Ca/B reading; registered uses C-sample) |
| L5 | registered: lock within 0.15 of B (point); amendment: Da > Ca on 2-op | **registered D FAIL** — mean lock 0.40 vs B 1.00 (Δ 0.60); seeds 1/3/5 lock 0. **registered Da PASS** — lock 1.00 all five 2-op seeds (Δ 0.00). **amendment PASS** Da−Ca +0.532 [+0.314, +0.696] |
| L6 | A genesis ≥ 0.5 (descriptive) | **PASS** — A genesis 0.94 pooled (1-op 0.99, 2-op 0.89) |
| Bs forecast | Bs 2-op J ≥ 0.6 | **FAIL** — 0.25; **also confounded with own-rule memory (silent cells' memory line omits their previous rule; see TASK_LIFE_OWN_MEMORY)** |
| Ca forecast | Ca 1-op high | partial — 0.53 |
| CS1 | \|Ca − Cas\| < 0.05 on 2-op | **FAIL** — +0.133 [+0.029, +0.246]; **also confounded with own-rule memory (silent cells' memory line omits their previous rule; see TASK_LIFE_OWN_MEMORY)** |
| CS2 | Ca − Cas > 0 on 1-op | **PASS** — +0.335 [+0.196, +0.467]; **also confounded with own-rule memory (silent cells' memory line omits their previous rule; see TASK_LIFE_OWN_MEMORY)** |
| CS3 | Cas FL_gen ≥ 0.10 on 2-op | **FAIL** — 0.08 (seed 1 only); **also confounded with own-rule memory (silent cells' memory line omits their previous rule; see TASK_LIFE_OWN_MEMORY)** |
| CS4 | g1 prompt gap (descriptive) | none (Ca ≈ Cas ≈ 0.00 on 2-op; 1-op g1 Δ ≈ 0.04) |
| **W1** | B1 J@g10 ≥ 0.80 and correct lock in ≥4/5 seeds | **PASS** — mean J 0.98, lock 5/5 |
| **W2** | B1 median lag vs one-source bound ≤ 1 (received first-holds) | **PASS** — median lag −1.0 |
| **W3** | Ca1 J@g10 ≤ 0.10 (wave dies without check) | **FAIL** — mean J 0.101 (by 0.001) |
| **W4** | Da1 J@g10 ≥ 0.60 (one source + check) | **PASS** — mean J 0.92 |
| **W5** | front exposure: 1 P_e neighbour in ≥60% of B1 switches | **FAIL** — frac_1 0.19 |
| **W6** | B0 J@g10 ≥ 0.70 in ≥3/5 seeds (no sources) | **PASS** — 5/5 (0.98–1.00) |
| **W7** | B0 seed 1 false-locks on `shift_symbols(1)` at g10 | **FAIL** — the 23% minority overturned the 75% false majority by g3 |
| **W8** | descriptive J@g10: B0 vs B1 vs B(4src) vs Bs | descriptive — B0 ≈ B1 ≈ B ≫ Bs |
| **K1** | seed-mean g1 solo share decreases K2 > K4 > KH | **PASS** — 0.33 / 0.042 / 0.00 |
| **K2** | channel-on: Pe modal@g10 in all runs with g1 solo ≥0.15, and in ≤ half with g1 solo ≤0.05 | **FAIL** — low bin 5/8 modal, including runs with zero holders at g1; the readout assumed selection only, but P_e was proposed by cells that never received it |
| **K3** | KH J@g10 > KHs in ≥4/5 seeds | **FAIL** — 3/5; **also confounded with own-rule memory (silent cells' memory line omits their previous rule; see TASK_LIFE_OWN_MEMORY)** |
| **K4** | false locks at g10 grow K2→KH (descriptive) | descriptive — 0 / 0 / 3 false locks; **restated (KHs-mem):** false-lock gens 0.3–0.5 with no channel — false majority at KH is also present without the channel (not a channel-only effect) |
| **M3** | KHs-mem pooled self-revision hazard ≥ 0.02 | **PASS** — 0.039 (142/3642); 4/5 seeds; vs KHs-r 0 (`m3_khs_mem.md`) |
| **E1** | unreceived Pe proposals: KH-r > KHs-r in ≥4/5 seeds; pooled hazard ≥3× | **PASS** — 4/5; 0.0116 vs 0 |
| **E2** | KHc hazard ≥ 0.5 × KH-r (crowd recovers) | **confounded, not interpretable** (also FAIL on numbers: 0 vs 0.0116) |
| **E3** | KHc hazard > KHe (count matters) | **confounded, not interpretable** (also FAIL: both 0) |
| **E4** | descriptive KH-r J@g10 / Pe modal vs critical-mass KH | descriptive — J ≤ 0.37; Pe modal 0/5 |
| **E5** | KHp hazard < KHc (content matters) | **confounded, not interpretable** (also FAIL: 0.0027 ≮ 0) |
| post-hoc: crowd echo | fixed crowd/self echo inbox recovers discovery (E2/E3 story) | **failed guess** — arms confounded with silence; even on numbers KHc/KHe = 0 |
| post-hoc: recombination | complementary one-op in inbox drives proposals | **failed guess for the live channel** — 0/47 proposals complementary; 0/338 complementary at-risk become proposals. Occurs only when the missing op is shown alone (KHp, 10/11) |
| **T1** | Dr per-rule accuracy ≥ 0.95 | **FAIL** — 0.896; cause = 1-based `swap` reading after catalog removed in v3 (`swap_index_diag.md`) |
| **T2** | Dr J@g10 ≥ Da-r − 0.10 (0.823) | **FAIL** — 0.696 vs Da-r 0.923 |
| **T3** | Mx10 < Mx25 < Mx50 junior J@g10 | **PASS** — 0.42 < 0.72 < 0.81 |
| **T4** | Mx50 junior < Dr in ≥4/5 seeds | **FAIL** — 3/5 |
| **T5** | J@g10 vs reasoning $/B (descriptive) | descriptive — B★ at J@g10 0.99; Ca-r/Da-r at $0 on the **reasoning-only** axis (`fig_tech_lead.png`). **Mark: reasoning tokens only; total-cost version → `fig_tech_lead_total_usd.png`** (total API USD / seed; Ca-r/Da-r no longer forced to $0). **Cost axis = P=4 Decisions** (see caveat: ÷4 ≠ equivalent agent) |
| post-hoc: 1-based index | FR concentrates where 1-based reading fails | **confirmed** — FR 0.685 vs 0/166; design error = dropping catalog in v3 |
| post-hoc: ≈0.98 if index fixed | counterfactual accuracy | **descriptive only** — not a registered estimand; Dr-cat tests it |
| **M1** | Bs-mem J@g10 > Bs-r J@g10 in ≥4/5 seeds | **PASS** — 5/5 (`runs/life_own_memory/summary.json`) |
| **M2** | seed-mean J@g10, B − Bs-mem ≥ 0.20 | **FAIL** — Δ = 0.10 (B 0.99 − Bs-mem 0.89) |
| **M4** | on 2-op, seed-mean \|Cas-mem − Cas-r\| J@g10 < 0.05 | **PASS** — 0.0167 (`m4_cas_mem.md`) |
| **M5** | persistence Bs-mem vs Bs-r on seed 1 (descriptive) | descriptive — 0.076 vs 0.938 (`m5_persistence_seed1.md`) |
| **V1** | KHe-pub pooled hazard ≥ 0.006 | **PASS** — ≈ 0.042 (`runs/life_publish_void/summary.json`) |
| **V2** | KHv pooled hazard ≤ 0.002 | **FAIL** — ≈ 0.041 |
| **V3** | KHc-pub vs KHe-pub and live bin (descriptive) | descriptive — KHc-pub ≈ 0.032; KHe-pub ≈ 0.042 |

## Caveats

- Distill-check bank contains only channel-on situations (own previous rule always visible); D0–D5 make no claim about silent cells.
- One model (`gpt-6-luna` beta), one task family, 5 seeds per depth, one 10-generation epoch.
- C-L4 agreement / false lock rests on one task; to make it a rate, build a P_e set where a simpler
  hypothesis is deliberately near-indistinguishable on local examples. Persistence half: withdrawn
  (M5). Sustained silent false lock ≠ K4-style “without channel” — Bs-mem seed 1 breaks it
  (`c_l4_bs_mem_false_lock_seed1.md`).
- Lock threshold 0.5 registered; 0.6 sensitivity is post-hoc and only used to separate stable consensus
  from 50/50 splits.
- Cells see only rule names, not operation definitions; B stage-1 failures are not order-sensitive
  (12 commuting / 7 one-op / 0 order-sensitive, `diag_b_stage1_commute.json`). **C-L9:** the same
  name-only interface, without catalog examples that fix `swap(0,…)`, made the tech-lead reviewer
  read indices as 1-based.
- Cell-generations within a run are not independent; inference is over seeds (5 per arm). Pooled
  counts (e.g. 47/4046) are descriptive, not test statistics.
- Echo E2/E3/E5 manipulate inbox **and** own publication (`silence` vs `published`); do not read as
  fixed-inbox nulls. Hazard numerator (events) ≠ `n_found_alone` (first unreceived holds).
- **Publish-void V2 readout:** KHv vs KHs-r differs in published memory + empty inbox block +
  channel constitution (“You may publish…” vs “You cannot send…”). Do not call V2 a memory-only
  test. Memory-only = KHe vs KHe-pub (0 vs ≈ 0.042).
- Channel-on vs channel-off constitution lines are part of every silent contrast (B/Bs, Ca/Cas,
  KH-r/KHs-r, KHs-r/KHv); listed in `prompts/arm_pair_diff_audit.md`.
- **One-pass Decisions are order-sensitive (descriptive, 2026-10-13):** a single option-order
  permutation disagrees with the 4-permutation argmax in **71% (Cas), 35% (Ca), 19% (Da)** of rule
  decisions (`p1_vs_p4_argmax.md`). **P=4 is needed for stable one-pass decisions**, so the ÷4 cost
  is **not** an equivalent agent; its J is unmeasured. Cost comparisons use **P=4 (total USD)**,
  where reasoning arms are cheaper per seed than one-pass arms in this implementation.
- Unsloth V1 heads (for reference, not Life): conversion works in-domain (typed-decisions 0.78–0.83); no
  transfer to L-VERIFY at either depth (0.58 / 0.52); with ready-made checks pairs 0.98 but full-catalog
  choice 0.34–0.67 vs Luna 0.995.

## Artifacts

`runs/life_reasoning_cells/`: `summary_*.json`, `false_lock_all_arms.json`,
`lock_threshold_sensitivity.json`, `false_lock_diagnostics.json`, `diag_b_mechanism.json`,
`false_holder_feedback.json`, `simplicity_pull_all_2op.json`, `simplicity_pull_abc.json`,
`contrast_ca_cas.json`, `contrast_da_ca.json`, `diag_b_stage1_commute.json`, `fig_j_by_gen.png`.

`runs/life_long_chain/summary.json` (W1–W8); `runs/life_critical_mass/summary.json` (K1–K4);
`runs/life_discovery_echo/` (`summary.json`, `pe_retention_diag.md`, `recombination_diag.md`,
`proposal_multiplicity_diag.md`, `echo_confound_and_crosstab.md`,
`hazard_by_prev_publish.md`, `hazard_by_prev_publish_B_exact.md`).
`runs/life_publish_void/summary.json` (V1/V2/V3); `prompts/arm_pair_diff_audit.md`.

`runs/life_own_memory/` (`summary.json`, `m1_retention_hazard.md`, `bsr_seed1_api_check.md` — Bs
M1/M2; `m3_khs_mem.md` — M3 PASS + descriptive J / false-lock notes; `m4_cas_mem.md`,
`m4_cas_mem.json`; `m5_persistence_seed1.md`, `m5_persistence_seed1.json`;
`c_l4_bs_mem_false_lock_seed1.md` — C-L4 vs Bs-mem seed 1 consistency).

`runs/life_tech_lead/` (`summary.json`, `reviewer_accuracy.json`, `fig_tech_lead.png`
[reasoning-only T5], `fig_tech_lead_total_usd.png` [total API USD],
`swap_index_diag.md`, `noop_fr_diag.md`, `posthoc_diag.md`).
`runs/life_own_memory/cost_readout.md` (own-memory vs $10–14 / $20; compared-arm
total API USD per seed; P=4 Decisions note).
`runs/life_reasoning_cells/p1_vs_p4_argmax.md` (P=1 vs P=4 rule-argmax disagree rates).
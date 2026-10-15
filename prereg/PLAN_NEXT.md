# Plan — next steps (Luna API track and local GPU track)

**Status:** plan for the agent. Each numbered item is either a closing action on an existing task
or a new task to be registered (predictions locked) before any number. Items marked
**[Artem go]** wait for an explicit go. The two tracks run in parallel (API vs GPU).

## Standing rules (apply to every item)

- `DESIGN_CHECKLIST.md` in full, including item 2 as amended: the gate compares the **raw bytes of
  the payload built by the runner's own request builder**, never a reconstruction.
- Runtime masked-template check at g2 of seed 1 for every new Life arm (mask memory values,
  inbox slot contents, query, epoch/generation numbers; catalog compared as a multiset); fail
  before any g3 request.
- Fresh, empty per-arm cache dirs; per-generation log of live / cached / fallback counts; fail if
  g ≥ 2 has 0 live requests or uniform fallback > 2%.
- Commit hash recorded in every arm×seed `report.json`. No resume across code versions.
- Always state which J (J@g10 vs mean J; 96 or 100 cells).
- Cost: API USD (from usage, verified), prefill/output tokens per cell-generation; GPU: measured
  GPU-seconds and tokens/s. Alarms are not stops.
- No closed-model output in any training data. No reasoning text requested or stored from closed
  models. Never edit running scripts; amendments before numbers.

---

## Track A — Luna (API)

### A1. Close Distributed Phase 1 (running)
- When DCs closes: final `summary.json` and readout D1–D5.
- D2 is **FAIL as registered** (DRo 0.56 < 0.80); follow its readout; do not amend D2.
- Post-hoc note (labelled as such): DRo is one call per neighbourhood, so it tests one-shot pooling,
  not information sufficiency (world audit proves ∩ = {P_e}); DR J@g10 mean 0.85 > DRo 0.56.
- D5: DR switches to P_e are 76–92% (a∧b), 0% majority-alone. Report as descriptive.
- DRo details: calls per seed, accuracy per seed, what DRo chose when wrong (1-op member of S_c?
  another candidate?), reasoning tokens per call, truncations.
- Per-seed chance E[1/|S_c|] beside DRs; drop share per arm.

### A2. Register and run `TASK_LIFE_DRO_ITER.md` (new; I will send the file)
Question: does a single agent with all nine neighbourhood examples reach DR's level when it also
gets ten generations and memory of its own rule? Arms: DRo-iter (same neighbourhoods and prompt as
DRo, 10 generations, memory line `rule='…'`, no feedback). Cheap (~$1–2). Runs after A1.

### A3. Article
- Hand `Luna_update_oct13.md` (attached separately) to insert into `article/Luna.md` now: banner,
  one-line note in the Oct 11 update, new section "Update, Oct 13, 2026". Figures:
  `fig_curves_B_Bsmem_Bsr.png`, `fig_curves_onepass.png`. Show me the rendered diff before pushing.
- Distributed results go into a later update, after A1 and A2.

### A4. Parked (not registered; no action)
SO-only distillation (oracle labels); Ca-temp; An/Ca extension to 30 generations; DRo with
`effort=high`.

---

## Track B — local GPU

### B1. Throughput probe for reasoning cells (new, small; run first — GPU is free)
Goal: decide whether Life with local reasoning cells is affordable before registering it.
- Models: `Qwen/Qwen3-4B-Instruct-2507`, SPADE-4B (exact repo id as recorded), `Qwen3.6-35B-A3B-FP8`.
- Prompt: the B-arm Life cell prompt (same builder), cot mode as in the SPADE grid ("Think step by
  step, then give the final answer" + the same final-answer format). Instruct-2507 has no thinking
  mode: reasoning is prompted chain-of-thought. Do **not** constrain decoding to JSON from the first
  token (that removes the reasoning); parse the final answer line strictly, as in the SPADE grid.
- One Life generation's worth of requests (96 cells, synthetic g2 states from the dry builder),
  at concurrency 32, 64 and 96. Sampling = SPADE card settings; per-request seed; SGLang version logged.
- Report per model: decisions/hour, aggregate tokens/s, KV usage, reasoning length distribution,
  truncation share at the cap, invalid share, projected GPU hours for one 5-seed × 10-generation arm.
- Output: `runs/local_reasoning_probe/summary.json`. No prediction; this is a sizing step.

### B2. Unsloth hybrid `TASK_UNSLOTH_DECISION_HYBRID.md` **[Artem go]**
Before ALLOW, add to `GO_REVIEW.md`:
1. Train/test split and metric match the Unsloth docs recipe (docs: 3,000-row test = 2,000
   typed-decisions + 500 BANKING77 + 500 CLINC150). Ours shows train 1,200 / test 400: explain or
   align. The reference comparison must use the docs' eval set.
2. Order: Qwen3.5-4B reference conversion (V1, one seed) first; continue to Qwen3-4B / SPADE only if
   within 0.05 of the docs' number on the same eval set; otherwise stop and report.
3. Truncation assert on every train and eval item; max length logged.
4. V2b traces (if run) are generated on typed-decisions states, not Life items.
5. Note in the file (if not locked) that documented decision models score 73–81%, so U4 ≥ 0.95 is
   ambitious; do not change thresholds after numbers.

### B3. `TASK_LIFE_LOCAL_REASONING.md` **[locked 2026-10-15; gate PASS; GPU after B2]**
Open-model counterpart of **Distributed** DR / DRs (not original B). Paper question: does the
collective effect reproduce on an open 4B? Skipping B-task calibration (~16 GPU-h) — that would
not answer it.
- **SPADE-4B only** (Instruct ~58 GPU-h / trunc 15.6%; 35B ~167 GPU-h — neither fits a full design).
- Arms: **DR-S** (channel) / **DRs-S** (silent). Same Distributed prompt builder as Luna DR; only the
  output-format tail differs (think-then-JSON; no first-token JSON constraint).
- Step 0: one world × both arms (~7 GPU-h); stop if invalid+trunc > 10%. Step 1: five worlds (~32 GPU-h).
- Predictions L1–L4 locked in the task file. Queue row **#2e**.

### B4. Distributed Phase 2 (local cells)
Amendment with predictions after B3 shows the collective effect on SPADE-4B (or records the miss).

### B5. `TASK_LIFE_LOCAL_LONG.md`
After B2 (needs V1/V2 heads). Add a generative reasoning arm (V0) from B3 if affordable.

### B6. Lower priority
- Part B LV cot subsample (16 seeded pairs, concurrency 64): after B2.
- Distillation: stopped at D0 (T stage1 0.863, CI [0.815, 0.901]); note S0 invalid 0.18 scored as
  "not a check" in `phase0_readout.md`. SO-only stays parked (A4).

---

## Order at a glance

| now | next | then |
|---|---|---|
| A1 (running), A3 | A2 | Distributed article update |
| B1 done; B2 GO (hybrid running) | B3 (SPADE Distributed) after hybrid | B4 / B5 |
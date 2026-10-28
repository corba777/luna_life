# Amendment — gpt-oss-120b: an out-of-sample test of the micro → macro model

**Status:** locked 2026-10-27. Local, pre-approved. No call before this file was committed as
locked after a dry build. Basis:
- `AMENDMENT_CONTAGION.md` (locked) and its readouts `runs/contagion/part_ab_readout.md` and
  `runs/contagion/part_b_descriptives.md`;
- `THEORY.md`;
- the gpt-oss-120b battery readout `runs/life_dr_gptoss/qi1/readout.md`;
- `DESIGN_AUDIT_CHECKLIST.md`.

The panel plan does not trigger 120b's full runs (U1 passes), so these runs are added here with that
reason stated.

Dry build 2026-10-27: `runs/oss120/gate.json` (live calls refused; fixed-date pin). Stage-2
prediction gate shown on `--fake-run` in `runs/run_oss120_stage2.py`.

## Why

The committed simulator, driven by battery-measured response curves and measured inputs, predicted
which topology wins for both models it was built on: Luna medium (lattice) and gpt-oss-20b (`all`).
That is in-sample at the model level. Both models were known when the method was designed.

gpt-oss-120b has not been run on either topology. Its battery fingerprints place it in the graded
class, like 20b:
- step S +0.125 (20b +0.200);
- single-line L 0.425 (20b 0.275);
- checking 0.975 (20b 0.875).

So it is a clean out-of-sample test. The prediction is computed and recorded before any full-run
call, and then the runs either match it or do not. It also covers an axis the panel lacks: size
within one family.

## Stage 1 — inputs, no full-run call

**1a. Part A on 120b.** This repeats the locked contagion Part A unchanged:
- the same 1,160 prompts, byte-identical to the Luna and 20b arms;
- the same 2,960 calls and the same draws, including 6 draws at the n = 88 minority shares;
- the gpt-oss-120b battery serving (mem-fraction-static 0.82, max-running-requests 4,
  `runs/life_dr_gptoss/pinned/`) and the battery decoding, with the pinned chat template that
  fixes the Harmony date to 2026-10-22 (`chat_template_date_20261022.jinja`, sha256
  `e6433aba3fb14f310cd55bd516dbbbaa5859f48e5b7a05f605916bb07a9a7387`);
- context 40,960, with I_max for the harmony tokenizer **4,189** (worst-case world-1 `all` round-20
  prompt, cell 9, fixed-date pin; 4,189 + 32,768 = 36,957 ≤ 40,960). Wall time from the 120b
  battery logs: **9.59 h** (2,960 × 11.667 s/call).

The standard sampler gate runs first.

**Date sensitivity on 20b (descriptive, before 1a).** After Qwen Part A and before any 120b call:
200 Part A prompts (all n = 88 adopt shares), each sent under the fixed-date pin and under the
model default template at today's date, 2 draws each (800 calls). Report adopt rates, per-prompt
agreement, and a cell-paired sign-flip on the difference. No conclusion beyond “date sensitivity
is or is not detectable”. Runner: `runs/run_oss20_date_sensitivity.py`.

**1b. Round-1 inputs.** The simulator needs, for each model:
- class-B round-1 holding;
- publication by round and class.

120b has no full run, and using one would make the test in-sample. So:

- **Round 1:** one round-1 pass per topology, `all` and lattice, 100 calls each, with the panel
  full-run builder. The round-1 inbox is empty, so this needs no history. It gives class-B holding
  and round-1 publication. These 200 calls are not part of any full run's cache. The full runs start
  with fresh caches. Wall time from the 120b battery logs: **0.65 h** (200 × 11.667 s/call).
- **Rounds 2–20:** publication is the share of Part A answers that publish, pooled over conditions,
  by direction (adopt arm for E-holders, abandon arm for P_e-holders), applied from round 2 on. It is
  stated as an approximation. The counterfactual swaps showed that publication moves the level and
  not the ranking: the ranking held under both swaps.

**1c. The prediction record.** Run the committed `runs/contagion_sim.py`, unchanged, with the 120b
Part A fits and the 1b inputs: 200 replicates per topology, seed 0. Report the median and the 5th–95th
percentile band of mean x(10–20) per topology, and the median gap x_lattice − x_all. This is
committed as `runs/oss120/prediction.json`, with its hash logged in
`runs/oss120/prediction.sha256`, **before any Stage-2 call**.
The deterministic recursions (`THEORY.md` §3, §4) are recorded beside it.

## Stage 2 — full runs

gpt-oss-120b, world 1, `all` and lattice (Moore), **4 replicates each** (was 2; see dated line
below), 20 rounds, the panel full-run builder: **16,000** calls, wall time **~51.9 h**
(16,000 × 11.667 s/call from the 120b battery logs). Own caches. Same fixed-date pin as 1a and 1b
(Stage 2 crosses midnight; the pin keeps the date line fixed). The tokenize agreement record is
kept, as for 20b. Runner: `runs/run_oss120_stage2.py`.

**2026-10-28 — Stage 2 replicate count 2 → 4 per topology (pre-record).** Locked in
`AMENDMENT_REPLICATES.md` before any prediction record exists. No Stage-1 input changes. O1 uses
the sign of the mean over **4** runs per topology; O2 requires **each of the 4** runs per topology
within the simulated 5–95 % band. Everything else in this amendment is unchanged.

## Predictions (locked now; their numbers come from the Stage-1 record)

- **O1 (ranking, primary):** the sign of the observed mean gap, x_lattice − x_all averaged over the
  **four** replicates per topology, equals the sign of the simulated median gap. If |simulated median
  gap| < 0.10, no sign is predicted, and O1 is reported as "not predicted". The 0.10 is the smallest
  observed absolute gap among models whose sign the simulator got right: 20b's simulated −0.27 and
  observed −0.45, Luna's +0.70 and +0.65. A gap of 0.10 is well inside that, so a smaller simulated
  gap is too close to call.
- **O2 (level, secondary):** in each topology, **each of the four** observed replicates' mean
  x(10–20) lies within the simulated 5th–95th band.
- **O3 (class):** 120b's Part A S88 and E8 are each within the hull of 20b's values, which is the
  family prediction from the battery, and outside Luna's. **Limitation (stated in the 120b
  readout):** O3 compares 120b under the fixed-date pin with 20b under the model's default template
  and a live `strftime` date (see `runs/model_panel/panel_summary.md`, 2026-10-27). The date-
  sensitivity check on 20b is descriptive only.

## Pre-stated readings

- **O1 holds:** the model predicts the topology ranking of a model it was not built on. This is the
  main external validation of the micro → macro claim.
- **O1 fails:** the curve-level model is not sufficient across models. The readout checks:
  - whether the Part A–to–in-situ gap seen for 20b is larger here, by comparing Part A rates with
    the full-run hazards at matched counts;
  - whether 1b's publication approximation is the cause, by re-running the simulator with 120b's
    observed full-run publication. That is a post hoc check, labelled.
- **O1 holds, O2 fails:** the ranking is predictable and the level is not, as for 20b (simulated 0.67
  against observed 0.85–0.87 on `all`). The paper claims the ranking, not the level.
- **O3 fails:** size changes the response rule within the family, which is a finding on its own. O1
  is still read.
- **"Not predicted":** the curves place 120b near the boundary, and the full runs are reported
  descriptively.

## Gates (live calls refused unless stated)

- The 1a prompts are byte-identical to the Luna and 20b Part A sets, checked by the two hashes in
  `runs/contagion/gate.json`: `prompt_sha256`
  `92bc05b0b131fabbecf4f5cdd8f1c1d462717a2f3bae643ef8f96f9a3c0f59d6` and `prompts_sha256`
  `26f015ec9833a4d37b267e22b9ec95208200d3304ff96bcab7179989360c903c` (matched against
  `runs/contagion/part_a_prompts.json` in the dry build).
- The fixed-date pin is used for every 120b call (1a, 1b, Stage 2). Hash
  `e6433aba3fb14f310cd55bd516dbbbaa5859f48e5b7a05f605916bb07a9a7387`. One rendered prompt:

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2026-10-22

Reasoning: medium

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>user<|message|>PROMPT<|end|><|start|>assistant
```

- Context: I_max 4,189 + 32,768 ≤ 40,960 for the harmony tokenizer, and the 120b server starts at
  40,960 with mem-fraction-static 0.82. This is live: the server start is the gate.
- The sampler gate, live, before 1a.
- The prediction record is committed before Stage 2. The Stage-2 runner refuses to start if
  `runs/oss120/prediction.json` is absent or its hash differs from the logged one in
  `runs/oss120/prediction.sha256`. Dry-build fake run (`python runs/run_oss120_stage2.py --fake-run`):
  absent → refused; wrong logged hash → refused; matching hash → accepted (no live call).

## Design audit

1. **Fidelity.** Same prompts, simulator and decoding as before. The only new element is the
   publication approximation in 1b, which is stated. The Harmony date is pinned for every 120b call
   (same pin as the battery); 20b Part A used a live date — stated under O3.
2. **Coverage.** World 1, both topologies.
3. **Controls.** 20b, the same family at another size, on the same prompts and simulator. Luna is the
   opposite class.
4. **Observability.** The cells see their prompts only.
5. **Gate consistency.** All of the above run together before 1a, and the record gate runs before
   Stage 2.
6. **Statistical unit.** Part A: 20 cells. The full runs: **4 replicates per topology** (locked
   2026-10-28, before the prediction record). O1 is a single sign against a pre-recorded prediction.
   This is weak per run and strong as a pre-registered call. Stated.
7. **Pre-stated readings.** Above.

## Queue

After Qwen Part A: 20b date-sensitivity check, then 1a, then 1b, then the prediction record, then
Stage 2 at **4 + 4**, then R-oss20, then Part C (`AMENDMENT_REPLICATES.md`); before wave 2a.
Wall time is not a constraint. Dated order change is in `RESEARCH_ROADMAP.md`.

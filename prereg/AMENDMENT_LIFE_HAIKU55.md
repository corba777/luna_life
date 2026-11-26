# Amendment — Claude Haiku 5.5 on the "Who Speaks First" line: battery, held-out prediction, populations

**Status:** draft v1 (2026-11-25), written by the reviewer for Artem. Artem, 2026-11-25 23:48: «я имел в виду всю линию
«Who Speaks First»»; 23:51: «Ну это на CPU, можно и раньше QX. Если все в $20 уложится, то можно посмотреть». Locked
after the agent's dry build and the reviewer's review; no call before the lock and Artem's go, logged verbatim. API
only; it runs beside the GPU queue (120b core) and touches neither the GPU nor any waiter. The paper carries no dollar
figures.

## Why

The paper's central claim is that a model's response function, measured in a battery outside the population, predicts
which topology the population does better on. The one held-out test so far is gpt-oss-120b, from the same family as
gpt-oss-20b, and its predicted sign held only narrowly (+0.016 against +0.13). Claude Haiku 5.5 is a model from another
developer. In QX it changed its rule almost only on a contradicting result: rule changes without one 0/240 in isolation
(U0), majority step 0/60 at first exposure. In this task messages carry rule names only, so the battery decides whether
names move it at all. It is the cleanest out-of-family check of the claim, and the prediction is made before any
population call, as for gpt-oss-120b.

## Design (only the model changes)

World 1, engine, constitution, prompts, schema (rule name, publication bit, signal 0–7) and conditions exactly as the
runs they mirror; prompts byte-identical to the other models' for the same state. Decoding as in Haiku Stage 0. No
reasoning text stored (closed model); answer text and usage stored.

- **Stage 1 — battery. Claude Haiku 5.5 · world 1 · 20 class-A cells · lattice form (19 conditions, n = 8) and `all`
  form (10 conditions, n = 88) · adopt and abandon directions · 2,960 calls.** Same prompts and draws as the batteries of
  Section 5.1 (mirrors: the gpt-oss-120b battery).
- **Stage 2 — prediction record.** The committed simulator of Section 5.2, unchanged, driven by Haiku's battery fits and
  by publication from the battery's communication field, as for gpt-oss-120b; 2,000 runs per topology. The record
  (sha256) is committed before any population call and gives, per topology, the simulated mean x(10–20), its 5–95 %
  band, the sign of x_lattice − x_all, and the share of cell-bootstrap refits (100) that keep that sign.
- **Stage 3 — populations. Claude Haiku 5.5 · world 1 · lattice and `all` · rule names and signals only (no examples)
  · 20 rounds · 4 runs per topology · 8 runs, 16,000 calls.** Run names `life_haiku55_w1_{lattice,all}_r{1..4}`,
  topologies alternating under one waiter.

## Measures

Battery: S88, M88, R88, E8 as defined in Section 5.1; the lattice fit logit a = c₀ + c₁k + c₂m and the `all` fit
logit α = d₀ + d₁s. Populations: x(t), run outcome mean x(10–20), tip (mean > 0.9); descriptive: witnesses (class B) on
P_e at rounds 1 and 20, publication rate, rules held at round 20 (P_e, E, other), signal use.

## Tests and predictions stated in advance, derived from measured data

- **HL1 (class), descriptive with a locked rule.** Threshold if S88 lies inside Luna's battery interval and outside
  gpt-oss-20b's; graded if inside gpt-oss-20b's (either run) and outside Luna's; stubborn if a ≤ 0.10 at every `all`
  share below 1 (Qwen's definition); otherwise unclassified. Intervals: cell-bootstrap 95 % as for O3.
  **Prediction: stubborn.** Derived from Haiku's QX isolation and population measures: rule changes without a
  contradicting result 0/240 (U0) and majority step 0/60; a class-A cell's own example fits both E and P_e, so no line
  in its inbox contradicts what it holds. Stated risk: QX prompts and this constitution differ; a name-following
  response here would show the QX profile is task-specific.
- **HL2 (sign, B1 form).** The observed sign of mean x_lattice − mean x_all over the 4 + 4 runs equals the sign in the
  Stage-2 record. One-sided exact permutation p over the 70 splits is reported beside it. If the record's simulated gap
  is below 0.02 in absolute value (as for Qwen), HL2 is not scored and the result is reported as "no ranking predicted".
- **HL3 (level).** At least 6 of the 8 runs lie inside the simulated 5–95 % band of their topology.

Expected pattern, before the battery: if HL1 is stubborn, x(10–20) near the witness share (≈ 0.25) on both
topologies and no tip; the Stage-2 record replaces this with derived numbers.

## Readings stated in advance

| pattern | reading |
|---|---|
| stubborn; populations near 0.25 on both topologies | Rule names alone do not move Haiku cells, as in QX; the population keeps the witnesses' rule and nothing spreads. The topology claim has nothing to act on (as for Qwen). |
| threshold or graded; HL2 holds | The battery predicts the ranking for a model outside the OpenAI family: the central claim gains its strongest support. |
| threshold or graded; HL2 fails | The response function measured in isolation does not carry the ranking for this model; stated as a limit of the claim. |
| HL3 fails with HL2 holding | Ranking without level, as for gpt-oss-120b. |

## Money (chat and logs only)

Projection from Haiku's QX cost per call ($0.0007, ≈ 4.7k input and 0.66k output tokens): 18,960 calls ≈ $13. The dry
build replaces it with Anthropic's token count on the actual prompts (shortest and longest of each form; `all` inboxes
hold up to 99 lines). **Ceiling $20 for this line (Artem).** Start rule per stage: spend so far + 1.5 × the stage's
projection ≤ $20. If Stage 3 does not fit at 4 runs per topology, it runs at 2 per topology (8,000 calls), HL2 is
reported without the permutation p, and the deviation is logged before the first population call.

## Gates, order, outputs

Format gate as in the gpt-oss-120b battery (the schema's three fields parse; a failed parse is retried by the stored
rule and counted). Waiters keep stdout and stderr in a log file. Order: Stage 1 → package → reviewer's recheck from raw
calls → Stage 2 record committed and rechecked → **Artem's second go** → Stage 3. Dry build (CPU, no call): run names
and cache keys; battery prompts byte-equal to the gpt-oss-120b battery prompts and population round-1 prompts byte-equal
to the gpt-oss-120b world-1 runs (mismatch counts; only the model field may differ); token counts and the start rule;
the battery readout and HL1 rule, the simulator call and the HL2/HL3 readout run end to end on stub data. Outputs: a
package with SHA256SUMS after Stage 1, the prediction record after Stage 2, one package per finished topology pair
(r_k lattice + r_k `all`) in Stage 3. Nothing enters the paper or a page before the reviewer's recheck; population runs
come with the run viewer if they go on a page.

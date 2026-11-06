# Amendment — a direction in the activations for following the inbox, and steering the response function

**Status:** locked 2026-11-06 (Artem: "Four edits, then lock"). Local, pre-approved. No GPU step
before the 120b continuation's done file exists. CPU dry build done (`runs/witness_direction/dry_build.json`); the GPU-hour figure comes from
the timed HF probe after the 120b continuation and is logged before Stage 1b starts. Stage 1 only
(battery adopt prompts); the full battery and populations need their own amendment (see "Stage 2").

## Basis

`PAPER_LIFE_DRAFT.md` §5 (response classes, B1), `AMENDMENT_CONTAGION.md` Part A (the battery),
`AMENDMENT_QWEN_RESPONSE_TRAINING.md` (the same causal question by training),
`DESIGN_AUDIT_CHECKLIST.md`.

## Why

The paper's claim is that the response function decides the population outcome. The evidence so far
compares models. Post-training one model would change one thing in one model, but it is slow and,
for a model that cannot check, changes checking and response together. A direction in the residual
stream that carries "follow the inbox" would give a cheaper and more targeted intervention: the
weights stay fixed, the response function is moved by a dose, and checking can be measured beside
it. Stage 1 asks whether such a direction exists and whether adding it moves the battery's response
function without breaking own-example checking.

No closed-model output is used anywhere.

## Model and serving

- **Qwen3-4B-Thinking-2507**, the revision, chat template and decoding of the paper's Qwen battery
  and world-1 populations: revision `768f209d9ea81521153ed38c47d515654e938aea`; the model's own chat
  template (no `--chat-template`; generation prompt ends `<|im_start|>assistant\n<think>\n`);
  temperature 0.6, top_p 0.95, top_k 20, min_p 0, presence_penalty 0, max_tokens 32,768, no seed;
  one user message; `response_format` strict JSON schema (`decision_json_schema`) with the qwen3
  reasoning parser, so the final answer was grammar-constrained by the server. Context 36,864 for
  2,756 of the battery's 2,960 calls and 40,960 for the 204 resumed ones (decoding unchanged).
  Dense, 36 layers, hidden size 2,560. Its response class is "stubborn" (a ≤ 0.10 below unanimity,
  a(1.0) = 0.625), so there is room to move it; its own-example fit is 37/40, so checking is present
  to be preserved.
- **Engine:** Hugging Face transformers 5.17.0 (the `stage1-jev` interpreter) with forward hooks
  (activation capture and steering), in bf16, batched generation, the decoding above. **Constrained
  answer:** a `decision_json_schema` logits processor is active from the token after `</think>`
  to the end of the call, as the server's grammar was; reasoning is unconstrained. Reasoning text
  and final text are stored for every generated call (open model; storing reasoning is allowed).
- **Fidelity gate (before any steered call),** against the stored battery, which ran on SGLang
  0.5.18 (image `sha256:223b675fee9ec3020a7b1479a6d1a3d24296f729f2eb6049f69f1e0423118e7e`):
  (i) prompt token ids equal the SGLang tokenization of the same prompts, every prompt (passed in
  the dry build, 1,180 / 1,180); (ii) on the 540 adopt prompts, adoption at α = 0 minus the stored
  battery's adoption, by form (lattice, `all`): passes if, for each form, the 95 % cell-bootstrap
  interval of the difference (20 cells, 2,000 resamples, seed 0; a prompt's stored rate is the mean
  of its stored draws) includes 0. S88 and E8 at α = 0 against the stored values are reported beside,
  descriptive. (iii) At α = 0 every final answer is valid JSON conforming to the schema (580 / 580).
  If (ii) fails, Stage 1b is reported as HF-only and no comparison with the paper's battery is
  claimed; if (iii) fails, the constrained engine is not faithful and Stage 1b does not run.

## Data and folds

- **Prompts:** the Part A battery of world 1 (class-A cells; 20 cells; lattice n = 8 conditions with
  k P_e lines, m prefix lines and empty slots; `all` n = 88 shares), rebuilt by the builder that
  reproduces it byte for byte. Stage 1 uses the **540 adopt prompts with k ≥ 1** (memory rule ≠ P_e;
  27 conditions, one prompt per condition per cell; 18 lattice, 9 `all`), plus the
  **own-example-fit items** of Table 1: 20 world-3 witness prompts, two draws each (40 items, 13
  distinct cells). Abandon prompts are not used in Stage 1.
- **Labels for Stage 1a:** the stored decisions of the Qwen Thinking battery on those prompts (1,400
  draws; none truncated or unparsed; stored adoption 0.125 lattice, 0.062 `all`). The original
  battery is label-only, so labels are taken as stored; each stored draw is one labelled
  observation of its prompt's activation. If the queued Qwen Part A text rerun exists at lock, its
  labels are used and the original's are reported beside.
- **Cross-fitting folds, committed before any activation is read**
  (`runs/witness_direction/folds.json`, sha256 `f64dcb7f…`): the 20 cells ranked by
  `sha256("wdir|cell")`, five folds of 4 cells in rank order (108 adopt prompts each). The 20
  own-example prompts, which belong to no battery cell, are assigned 4 per fold by
  `sha256("wdir-own|replicate|round|cell")` rank. An earlier 60 / 40 split
  (`split.json`, 14 / 6) is superseded and was never used.
- **Per fold f:** layer, probe, d_f, σ_f, d_rand,f and d_k,f come from the other 16 cells only;
  steering of fold f's prompts (its 4 cells' adopt prompts and its 4 own-example prompts) uses fold
  f's directions only. Every scored number is out of fold, over all 20 cells.

## Stage 1a — probe and direction (forward passes only)

- **Activations:** the residual stream after each of the 36 layers at the last prompt token (the
  token before generation starts), for the 540 adopt prompts (540 forward passes).
- **Target:** y = 1 if the stored decision is P_e.
- **The confound and its control.** Adoption depends mostly on k and m, and k and m are visible in
  the activations. A probe that decodes k would look like an adoption probe. So:
  - the **inputs-only baseline** is a logistic regression of y on the condition (k, m, n, form);
  - the scored probe quantity is the **within-condition AUC**: probe scores are compared only
    between adopting and non-adopting observations of the same condition and the same fold (so both
    are scored by the same probe), pooled over strata (Mann–Whitney within stratum, weighted by
    pairs). Pairs are formed between different prompts only; draws of the same prompt are never
    paired.
- **Probe, per fold f:** L2 logistic regression per layer on the 16 training cells; penalty and layer
  L*_f chosen by inner cell-grouped 4-fold CV on those 16 cells (highest inner within-condition AUC).
- **Direction, per fold f:** d_f = the mean over conditions of (mean activation of adopters − mean of
  non-adopters) at L*_f, on the 16 training cells (conditions without both outcomes skipped),
  normalised to unit length. Taking the difference within each condition removes the k and m
  direction by construction. Two control directions of the same norm are fixed at the same time:
  **d_rand,f** (seeded random unit vector, seed f) and **d_k,f** (the within-cell mean difference
  between high-k and low-k adopt prompts, k above vs at or below the median k of the form,
  regardless of the decision: "more P_e lines seen"). σ_f is the standard deviation of the
  projection of the training cells' activations at L*_f on d_f.
- **Reported (descriptive):** L*_f per fold; pairwise cosines of d_1 … d_5 (each pair compared at a
  common layer only if L* agrees, otherwise reported with both layers); per-layer out-of-fold AUC
  curve.

## Stage 1b — steering on the adopt prompts (generation)

- **Intervention:** add α·σ_f·d_f to the residual stream at L*_f, at every position (prompt and
  generated tokens), for prompts of fold f.
- **Scale pilot:** 40 adopt prompts from fold 1's training cells, chosen by
  `sha256("wdir-pilot|condition|cell")` (listed in `folds.json`; 16 cells), steered with d_1. A step
  passes if invalid-JSON share ≤ 5 % and no answer is truncated at max_tokens. +α ladder
  {2, 4, 8, 16}, stopping at the first failure; α⁺ = the last passing rung. Then −α⁺ on the same
  40; if it fails, the next lower rung is tried at −α, downwards, until one passes. α_max = the
  largest rung passing both signs; one α_max for all folds, committed before any Stage 1b call. If
  +2 fails, Stage 1b does not run and this is reported. At most 320 calls (typically 40·(rungs
  passed + 1) + 40). **The pilot readout is blind to adoption:** it reports only invalid-JSON share
  and truncation per rung; no decision or rule counts are printed or logged until the Stage 1b
  readout.
- **Arms, on all 540 adopt prompts and the 40 own-example items (each with its fold's
  directions):** d at −α_max, 0, +α_max; d_rand at +α_max; d_k at +α_max. One sample per prompt per
  arm (two per own-example prompt, as in the battery), the same per-prompt seed across arms.
  **5 × 580 = 2,900 calls.** The α = 0 arm is also the fidelity-gate run. Half-doses, abandon prompts
  and b(s) move to Stage 2.
- **Measures per arm:** a(k, m) on the lattice form, a(s) on `all`, own-example fit (/40),
  invalid-JSON share, reasoning length (tokens).

## Predictions (locked)

Unit: the prompt (own-example: the item), out of fold over all 20 cells, with intervals by cell
bootstrap (2,000 resamples over the 20 cells, seed 0; own-example items resampled with their fold's
cells).

- **P1 (a direction exists):** the out-of-fold within-condition AUC (each fold's probe at its L*_f,
  scored on its held-out cells) has a bootstrap lower bound > 0.5. The inputs-only baseline and the
  full (not within-condition) out-of-fold probe AUC are reported beside.
- **D1+ (primary; dose raises adoption):** pooled adoption on the 540 adopt prompts is higher at
  +α_max than at α = 0; the paired difference has a one-sided bootstrap 95 % lower bound > 0.
- **D1− (secondary; dose lowers adoption):** pooled adoption on the 540 adopt prompts is lower at
  −α_max than at α = 0; the paired difference has a one-sided bootstrap 95 % upper bound < 0.
- **D2 (specific):** the adoption change at +α_max along d exceeds that along d_rand and along d_k,
  paired by prompt, bootstrap lower bound > 0 for each.
- **D3 (checking kept):** own-example fit at +α_max is not significantly below α = 0 (the
  bootstrap upper bound of fit(+α_max) − fit(0) is not below 0). Reported for every arm.

The thresholds are the sampling noise of the battery itself; no effect size is assumed.

## Pre-stated readings

- **P1, D1+, D2 and D3 hold:** a direction in one layer carries following the inbox, separately from
  counting the lines; adding it moves the response function by a dose and leaves checking intact.
  Stage 2 is then worth an amendment.
- **P1 holds, D1+ fails:** the decision is readable at the end of the prompt but not steered from
  there; it may be formed during reasoning. Reported with the per-layer AUC curve.
- **D1+ holds, D1− fails, α = 0 adoption < 0.15:** a floor effect, not a refutation — there is too
  little adoption at α = 0 to lower.
- **D1+ holds, D2 fails against d_k:** the direction acts as "seeing more P_e lines", not as a
  disposition to follow; the response function moves, but not as a separable component.
- **D1+ holds, D3 fails:** steering moves adoption by degrading checking; it cannot isolate the
  response function.
- **P1 fails:** no linear trace of the decision at the last prompt token beyond the condition.
- **Fold directions disagree** (low pairwise cosines or scattered L*_f) while P1 and D1+ hold: the
  effect is real out of fold but the direction is not unique; reported, not a failure.

## Stage 2 (not covered here)

If Stage 1 holds, a separate amendment picks α* (±α_max, with D3 holding), runs the full battery at
α* (adopt and abandon prompts; a(k, m), a(s), b(s), S88, M88, R88, E8 as in Part A), writes a
prediction record with the committed simulator from the steered battery, and runs steered
populations. Steered populations need an engine with the hook at population speed; the engine and
its fidelity gate belong to that amendment. The paper's existing Qwen populations are the unsteered
reference only if their configuration matches.

## CPU dry build (2026-11-05, during the continuation; `runs/witness_direction/dry_build.json`)

- **Prompts:** the Part A builder rebuilds `part_a_prompts.json` byte for byte (1,160 rows, 58
  conditions, sha256 `007f4c66…`); all 2,960 stored answers are on these prompts. Own-example items:
  `qi1m.jobs()` class B, 0/8 rebuilds the Table 1 measure — 20 prompts from world 3, two draws each
  (40 answers, 13 distinct cells), all 40 stored calls present; fit recount 37/40.
- **Token ids:** for all 1,180 prompts, the HF tokenizer (transformers 5.17.0, the HF engine's
  interpreter) gives exactly the ids that SGLang 0.5.18's own default chat path gives inside image
  `223b675f…` (transformers 5.12.1; content format string; no added specials), run CPU-only with no
  GPU device and no network. For the 20 own-example prompts the id count equals the server's stored
  `prompt_tokens` (20/20). Prompt lengths 1,924–4,314 tokens.
- **Folds:** committed (`folds.json`, `f64dcb7f…`) before any activation was read; 5 × 4 cells,
  108 adopt prompts per fold; scale-pilot prompts cover 16 cells.
- **Calls:** Stage 1a 540 forward passes; scale pilot ≤ 320 generated calls; Stage 1b 2,900
  generated calls (the α = 0 arm doubles as the fidelity gate; no extra calls).

## Gates (live calls refused unless stated)

1. Folds file committed before any activation is read; its hash in the readout.
2. Prompt byte identity with the battery; token ids equal to the SGLang 0.5.18 tokenization
   (image `sha256:223b675f…`) — passed in the dry build.
3. Constrained-answer engine: the schema logits processor checked on CPU before the GPU step (a
   tiny model, schema-valid output on stub reasoning); on the GPU, fidelity gate (iii).
4. Budget: the timed HF probe's Stage 1b projection ≤ 4 GPU days, else stop before the scale pilot
   and ask Artem. Scale pilot on fold 1's training cells only, blind to adoption; α_max committed
   before any Stage 1b call.
5. Fidelity gate (ii) and (iii) on the α = 0 arm before any steered arm is read out; the α = 0 arm
   runs first.
6. Item 14–18 checks: launch provenance per call (engine, model revision, fold, layer, α, direction
   hash, seed); every call stores reasoning and final text; exports never synthesise fields.
7. GPU exclusivity: strict precheck and a continuous monitor for every GPU step.

## Design audit

1. **Fidelity.** Same prompts and decoding as the battery, constrained answer included; HF vs SGLang
   0.5.18 (image `sha256:223b675f…`) checked by gate 2 and the fidelity gate.
2. **Coverage.** One model, world 1, class-A adopt prompts; own-example items from world 3.
   gpt-oss-20b is a later replication if Stage 1 holds.
3. **Controls.** α = 0, d_rand, d_k; within-condition AUC against the inputs-only baseline.
4. **Observability.** The model sees only its prompt; steering acts on activations.
5. **Gate consistency.** All gates before the first steered call.
6. **Statistical unit.** The prompt, clustered by cell; directions, layer and scale never from the
   cells they are scored or steered on (cross-fitting; α_max from fold 1's training cells).
7. **Pre-stated readings.** Above.
8. **Recheck.** Package: folds file, activations' summary statistics per layer, d_f, d_rand,f, d_k,f
   and σ_f per fold (as arrays with hashes), probe weights and out-of-fold scores, every generated
   call's text, per-arm measures. I recompute the AUCs from the stored scores and every measure from
   the stored text.

## Queue

CPU work during the 120b continuation (`AMENDMENT_OSS120_CONTINUE80.md`), all done or doable without
the GPU: folds committed; dry build (prompts, token ids, calls); the constrained-answer logits
processor and its CPU check (gate 3); the Stage 1a / 1b runner and readout with stub dry checks.
**No GPU step until the continuation's done file exists.** Then, in one new waiter
(`wait_gpu_free` → `wait_go_witness_direction` → strict precheck): Stage 1a (540 forward passes,
minutes), the timed HF probe (GPU hours logged before Stage 1b; **budget stop:** if it projects
Stage 1b above 4 GPU days, the waiter stops before the scale pilot in a `wait_go_*` step and asks
Artem), the scale pilot, the α = 0 arm with
fidelity gates (ii) and (iii), then the four steered arms, then the automatic CPU readout. Beside the
Unsloth decision conversion and wave 2b where GPU allows; Thinking response training stays at the
end of the queue.

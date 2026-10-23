# Model panel — plan and protocol

**Status:** locked. Approved by Artem. U1 and U2 are locked with this file. Local models only. Each
model's run still gets its own short amendment (pinned revision, settings, dry build, pilot) before
any call. This file fixes the panel logic, the protocol and the cross-model predictions before any
panel result beyond Luna and Qwen is seen.

## Why

Two levels of claim, kept apart:

- **Model-agnostic claims (macro and filter):** evidence-constrained false consensus (the prefix
  held by the cells whose own example fits it), and the own-example filter. Every model is one more
  independent test of these.
- **Model-specific traits (micro response rule):** how a cell responds to its inbox. Luna follows the
  share of visible lines with a step at a strict majority. Qwen holds its example-consistent rule while
  any supporting line is present, and responds to P_e count only when none is. Each model gets a
  fingerprint; the panel is a typology, not a vote.

Models are chosen to span axes, not to accumulate counts.

## Fingerprint battery (every panel model)

QI-1 (880 prompts) plus QI-1b (80 prompts): 960 prompts, the same message content for every model.

| fingerprint | definition | Luna | Qwen3-4B-Thinking |
|---|---|---:|---:|
| S, step | class A: P(5/3) − P(4/4) | 0.675 | -0.050 |
| L, single line | class A: P(1E) − P(1/7) | 0.850 | 0.025 |
| ally | class A: P(7/1) | 1.000 | 0.375 |
| count | class A: P(4E) | 1.000 | 0.425 |
| top | class A: P(8/0) | 1.000 | 0.675 |
| filter | class B: P(prefix \| 0/8) | 0.000 | 0.025 |
| errors | answers neither P_e nor prefix that do not fit own example | — | 9/440 class A |

Classification of each fingerprint against the Luna and Qwen references uses the hull rule of
`AMENDMENT_DR_QI1B.md` (Wilson 95% ∪ cell-cluster bootstrap 95%). As the panel grows, a model may be
"neither"; that is a result, not a failure.

Full runs (`all` and lattice, world 1) are made only for a model that triggers one of:
- it fails U1 (below);
- S or the ally fingerprint is classified "neither";
- it is the reasoning-off member of a pair whose two fingerprints differ in class.

## Protocol (same for every model)

- **Prompt:** byte-identical message content; only the model's own chat template differs.
- **Decoding:** the developer's published recommendation for that model and mode, quoted from the
  model card with its URL in the per-model amendment. No seed. max_tokens 32768 unless the model's
  context forbids it.
- **Reasoning:** the model's default reasoning mode at a medium setting where levels exist; for models
  with on/off modes, see the pairs below.
- **Revision:** pinned by Hugging Face commit hash. License recorded.
- **Remote code:** if the model needs `trust_remote_code`, the agent reads the modelling code before the
  pilot and records the file hashes; native SGLang support is preferred where it exists.
- **Pilot:** 20 calls outside the battery; more than 1 parse failure or truncation stops the model.
- **Scoring:** final answer only, the existing parser, parse failures and truncations counted per cell;
  a cell above 5% failures is reported and not classified.
- **Memory:** a model must fit the host with the Qwen server stopped (about 85 GiB pool). Larger
  models are out of scope.
- **Sources of model facts:** aggregator pages are used only to find candidates; every version, size,
  mode and recommended setting is confirmed on the model card before its amendment.

## Axes and candidates

| model | developer | size / type | reasoning | axis it covers | wave |
|---|---|---|---|---|---|
| gpt-oss-120b | OpenAI | MoE, large | levels | family vs Luna at large size | battery run (880 calls), QI-1b gpt-oss part (80 calls) done; read out 2026-10-23: G1 fail (S Qwen-like), G2 fail (L intermediate), G3 pass; U1 pass, U2 pass |
| Qwen3-4B-Instruct-2507 | Qwen | 4B dense | off | **reasoning off/on**, paired with the Thinking-2507 already run | 1 |
| Spark-X2.6-4B | Spark | 4B | none / low / high | **size-matched to Qwen, other developer**; reasoning none vs high within one model | 1 |
| gpt-oss-20b | OpenAI | MoE, smaller | levels | **size within the OpenAI family** | 1 |
| Qwen3.5-4B | Qwen | 4B | to confirm | **version within the same developer and size** | 2 |
| Gemma 4 (12B; E4B as 4B) | Google | 12B dense; 4B | 12B listed with reasoning; E4B without | another developer; 4B without reasoning | 2 |
| OLMo 3 / 3.1 32B Think | Ai2 | 32B dense | think | **open data and recipe**: a trait can be traced to training | 2 |
| Phi-4-reasoning (or current) | Microsoft | about 14–15B | reasoning | another developer, mid size | 3 |
| Llama 4 Scout | Meta | 109B MoE (17B active) | none listed | large, no reasoning; Llama licence | 3, if it fits |
| Mistral (current open reasoning model) | Mistral | to confirm | to confirm | another developer | 3, once open weights are confirmed |

Not counted as separate developers: distilled models on another developer's base (for example a
reasoning distill on a Qwen base). They count under their base, and are not on the list.

## Reasoning pairs

Two within-model or within-lineage pairs separate the reasoning mode from everything else:

- Qwen3-4B Thinking-2507 (done) against Instruct-2507: same size, developer and release.
- Spark-X2.6-4B at `none` against `high`: the same weights.

Each pair gets its own amendment with a locked prediction before its second member runs.

## Cross-model predictions (locked with this file)

Unit: each model's battery; within a model, the source cell, as in QI-1.

- **U1 (filter is model-agnostic):** for every panel model, class B adopts the prefix under 0/8 in at
  most 0.08 of prompts (the I3 bound).
- **U2 (social influence exists in every model):** for every panel model, class-A adoption of P_e at 8/0
  is greater than at 0/8, one-sided Fisher at α = 0.05, with the cell-level sign-flip beside it.

Both are scored per model and reported as a count of models passing. No model is dropped from the
count after its result is seen. A model whose run fails the protocol (pilot, failures above 5%) is
reported as "not run", with the reason, and not counted either way.

Not predicted: which class each model falls in on S, L, ally and count. Those are the typology.

## Order (proposal)

After gpt-oss-120b (battery and QI-1b): wave 1, then the rest of the Qwen queue (QI-2 … QI-I, moore),
then wave 2, then wave 3. Reason: three or four fingerprints across axes say more about the micro
rule than more depth on one model, and each battery is about one night on the local server.

## Additions

A model may be added later, by a dated line in this file and its own amendment, before its run. Models
are never removed after results are seen. Every model run under this protocol appears in the panel
table.

2026-10-22. Qwen ally 15/40 = 0.375 and count 17/40 = 0.425, filled from the QI-1b readout. These were the queued reference values. U1 and U2 are unchanged.

2026-10-22 errata. The Qwen values for S (0.000), L (0.050) and top (0.650) are QI-1 top-block rates. They are provisional. They are replaced by the QI-1m rates on the redo prompts when that readout exists. Ally, count and the filter are not part of this errata. U1 and U2 are unchanged.

2026-10-22. Qwen S, L and top are the QI-1m rates on the redo prompts, dated from `runs/life_dr_qwen/qi1m/readout.md`: S = -0.050 (-2/40), L = 0.025 (1/40), top = 0.675 (27/40). The provisional top-block values are no longer the reference. U1 and U2 are unchanged. Ally and count are unchanged.

2026-10-22. gpt-oss-120b: not run (serving failed). On the fourth load (SGLang 0.5.22, mem-fraction-static 0.70) the weights loaded in 355 s using 79.97 GB. SGLang then stopped with "Loaded weights leave no GPU memory for the KV cache under --mem-fraction-static=0.7", minimum viable 0.7132. The model never answered, and no pilot, battery or QI-1b call was made. It is not counted for U1 or U2. No further load is attempted without Artem's go.

2026-10-22. W1-spark-high: not run (pilot failed: 2 truncations at 32768 tokens). Failing pilot calls (completion tokens): cell 0: 32768, cell 1: 32768. The pilot was stopped at the second failing call under Artem's go; the locked rule (more than 1 in 20) was already decided. W1-spark-none runs as locked. U1 and U2 count W1-spark-high as not run.

2026-10-23. gpt-oss-120b, fifth load (mem-fraction-static 0.82, max-running-requests 4): served, pilot passed, amendment locked, 880-call battery done; QI-1b gpt-oss part (80 calls) done. Readout pending.

2026-10-23. gpt-oss-120b readout from the cache (`runs/life_dr_gptoss/qi1/readout.md`), as locked in AMENDMENT_DR_GPTOSS_QI1.md. 880 battery calls and 80 QI-1b calls, 0 parse failures, 0 truncations, no cell excluded. G1: S = 12/40 − 7/40 = +0.125, hull [−0.139, +0.367], contains Qwen (−0.050) and excludes Luna (0.675): Qwen-like, fail. G2: L = 17/40 − 0/40 = +0.425, hull [+0.197, +0.578], excludes both Luna (0.850) and Qwen (0.025): intermediate, fail. G3: class B 0/8 prefix 1/40 = 0.025 ≤ 0.08, pass. Pre-stated reading: split, stated as it is, no family claim; the own-example filter holds in gpt-oss. Panel fingerprints: S matches Qwen, L neither, ally 21/40 matches Qwen, count 30/40 neither, top 30/40 matches Qwen, filter undecided. U1 pass (1/40). U2 pass (30/40 against 0/40, Fisher p = 9.6e-14, sign-flip p = 3.8e-06). Three-way per-prompt agreement 382/880 = 0.434 against an independence baseline of 0.157; gpt-oss agrees more with Qwen (0.695) than with Luna (0.594).

2026-10-23. R1, Qwen pair, from the cache (`runs/model_panel/r1_qwen/readout.md`). Class B 0/8 on the enlarged set (20 cells × draws 0–11). Reasoning off, W1-qi-match: 0/240. Reasoning on, Qwen3-4B-Thinking-2507 (QI-1 draws 0–1 plus W1-r1-think draws 2–11): 3/240. One-sided Fisher p = 1, cell-level sign-flip p = 1. R1 fails in the Qwen pair. With the QI-1m Thinking draws in place of the QI-1 draws: 0/240 against 3/240, the same. W1-qi-nat beside it: 0/40 against 3/240. The Spark pair is not scored (W1-spark-high not run), so R1 is stated per pair only.

2026-10-23. For runs after today, two more fingerprints. Own-example fit rate: the share of battery answers, classes A and B, 22 conditions, whose named rule maps the cell's own example to its output. Filter selectivity: P(prefix | class A, 0/8) − P(prefix | class B, 0/8). Classes A and B use different source cells, so the interval is an unpaired cluster bootstrap over cells within each class (2000 draws, numpy Generator seed 0, 95% percentile). Every fingerprint, including these two, is also reported on the subset of answers in {P_e, prefix}, with that subset's share of the parsed answers beside it. For runs already finished, these figures are post hoc, not preregistered. U1, U2 and the locked R1 are unchanged.

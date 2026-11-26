# Amendment — isolation battery for Qwen3.6 and Nemotron with a capped, forced-answer thinking budget

**Status:** draft v2 (2026-11-24), written by the reviewer for Artem. v2 takes in the dry build
(`runs/dry_build_qx_isolation_budget.md`): the end-of-thinking markers, the continuation demonstrated on a
stored answer (not sent), prompt sha256 equal to the earlier builds, time estimates. Locked after the agent's dry build and the
reviewer's review; no call before the lock and Artem's go, logged with his words. Artem, 2026-11-24: «может можно
принудительно сократить output токены, а то как-то ни одна os модель не вписывается, кроме gpt»; on the
reviewer's option 1 (budget forcing): «Я тоже, тогда и Nemotron включить можно будет». This reverses, for this
amendment only, the decision of 00:51 to run Nemotron no further.

## Why

Both open non-OpenAI models were stopped by the format gate of `AMENDMENT_QX_ISOLATION.md` v3 because their
reasoning ran out of its limit: Qwen3.6 11 of 84 answers at 32,768 tokens (median answer 25,055 tokens; 9 of
the 11 in U2), Nemotron 9 of 51 at its 15,000-token budget (all in U1/U2). A gate that drops these answers drops
the hardest cases. Luna and Claude Haiku 5.5 already run under a total output cap of 8,192 tokens that includes
their reasoning. This amendment gives Qwen3.6 and Nemotron a thinking budget inside the same total and forces
an answer when it is used up.

## Decoding (the only change)

- **Thinking budget 7,168 tokens, answer budget 1,024 tokens** (total 8,192, Luna's and Haiku's cap).
- Pass 1: the model's own chat template with thinking on and its card sampling settings (Qwen3.6: temperature
  1.0, top_p 0.95, top_k 20; Nemotron: as in `AMENDMENT_QX2_NEMOTRON_BUDGET.md`, without its own budget
  mechanism), `max_tokens` 7,168, stopping at the model's end-of-thinking token (`</think>`; matched as the
  token or the string `</think>`, not only the template's surrounding newlines, so that a marker written with
  different whitespace still stops pass 1). The continuation then writes the marker exactly as the template
  does (Qwen3.6 `\n</think>\n\n`, Nemotron `</think>`).
- If pass 1 ends its thinking within the budget, generation continues normally up to the total of 8,192.
- If the thinking reaches 7,168 tokens: **forced answer** — the prompt, the thinking so far, then the model's
  end-of-thinking marker exactly as its template writes it, and a continuation of at most 1,024 tokens with the
  same sampling settings. Nothing else is inserted (no added sentence).
- Recorded per call: forced (yes/no), thinking tokens, answer tokens, the full reasoning (open models: stored).
- Label in every table: "Qwen3.6, thinking capped at 7,168 tokens, answer forced" (same for Nemotron).

## Prompts and conditions

Unchanged: the 60 world-0 prompts of v3 (U0–U2) and the 260 prompts of `AMENDMENT_QX_ISOLATION_WORLDS_U3.md`
(world 0 U3; worlds 1–3 U0–U3); three draws. 960 calls per model.

## Smoke (part of the run, first)

20 world-0 prompts (the first 20 of the run order). Pass: every answer parses; the forced path is exercised at
least once, or the dry build shows it on a stored long reasoning. If the smoke fails, nothing else runs and the
result is reported.

## Measures, tests, readings

As in v3 (with the joint addendum) and in the worlds+U3 amendment, per model: the v3 readings on world 0; T-U3
(U3 − U2, consistent, 80 cells, resampled within world), **prediction uncertain** for both models (no population
data); replication across worlds, descriptive. Also reported: forced share per condition and world, and every
measure on unforced answers only (descriptive; a forced answer is an answer).

## Gates

Format gate on the final answers: more than 6 of 180 (world 0) or of 240 (each other world) unparsed stops that
model in that world and is reported. A forced answer that parses is not a failure. GPU exclusivity.

## Dry build (CPU, no model call)

1. The two-pass mechanism in SGLang for each model: the exact end-of-thinking marker from each template, how
   the continuation request is formed, and a demonstration on one stored long reasoning (Qwen3.6 v3, an
   answer that hit 32,768) cut at 7,168 tokens — the continuation prompt shown, not sent.
2. Request bodies per model; prompt sha256 equal to v3 and worlds+U3.
3. A time estimate from the stored v3 timings at ≤ 8,192 tokens per call.
4. The readout on stub answers including forced flags.

## Time (dry build)

At ≤ 8,192 tokens per call and 16 in flight: Qwen3.6 about 17 h for 960 calls (nearly every call is expected
to use the full budget: 81 of 84 v3 answers exceeded 8,192 tokens), Nemotron about 7 h, plus one start-up each.

## Queue

GPU, after calibration round 2. The position relative to the QX-2 continuation and to the gpt-oss part of
worlds+U3 is Artem's call (see the agent's queue report).

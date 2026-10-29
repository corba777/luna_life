# Amendment — Part A batteries rerun with stored text (gpt-oss-120b, gpt-oss-20b, Qwen)

**Status:** locked 2026-10-29, after the dry build (values below; `runs/parta_text_replication/dry_build.json`).
Local, pre-approved. No call before this file is committed as locked. Basis: `AMENDMENT_CONTAGION.md` (Part A,
A1–A4, B1, B1-Qwen), `AMENDMENT_OSS120_PREDICTION.md` (Stage 1a, O1–O3),
`PAPER_LIFE_CHANGELOG.md` (erratum 2026-10-29), `DESIGN_AUDIT_CHECKLIST.md` items 14–17.

## Why

The Part A batteries of gpt-oss-20b, Qwen and gpt-oss-120b stored only the parsed rule. The final
text, `finish_reason` and token counts were not kept, so the parse and the truncation labels cannot
be checked. The rates, fits and the locked verdicts that use them stand as computed from the stored
labels. A rerun cannot recheck the old answers; it is a replication with full records. It tells us
whether the parse is right and whether the measured response functions reproduce.

## Runs

For each model, the full Part A battery again: the same 1,160 prompts and 2,960 calls (sha256 of the
prompt set equal to `runs/contagion/part_a_prompts.json`: file
`007f4c665d4acc0729b4f7cb6eb5ba7daef54b3d2664ae7eaba4621bb4b39d98`; joined prompts
`92bc05b0b131fabbecf4f5cdd8f1c1d462717a2f3bae643ef8f96f9a3c0f59d6`, equal to the Stage 1a value),
the same draws, decoding and server configuration as the original run of that model:
- gpt-oss-120b: as Stage 1a (context 40,960, max-running 4, pinned date template 2026-10-22).
- gpt-oss-20b: as the original battery (context 36,864, its template as recorded).
- Qwen: 40,960 on a single server from start to end (no resume).

Every row stores the final message content, `finish_reason`, `completion_tokens`, served model,
revision and image digest (items 14 and 16). No reasoning text is stored for closed models; these
are open models, and the reasoning field is not needed and not stored. Fresh output directory per
model; a runner that refuses existing output. Resume is not allowed: a partial run is quarantined
and restarted.

Order: after v14 (1b, QXp-oss120), **120b rerun first**, then the 120b prediction record, then the
gpt-oss-20b rerun, then 120b Stage 2, R-oss20, the Qwen rerun, Part C. About **43 h** of GPU in
total for the three reruns.

## Dry build (2026-10-29)

| | I_max (tokenizer, template) | + `max_tokens` 32,768 | context | GPU h (estimate) |
|---|---:|---:|---:|---:|
| gpt-oss-120b | 4,002 (harmony, pinned date template) | 36,770 | 40,960 | 8.6 |
| gpt-oss-20b | 4,002 (harmony, default template) | 36,770 | 36,864 | 3.3 |
| Qwen | 4,314 (Qwen3 default template) | 37,082 | 40,960 | 31.0 |

I_max for the longest Part A prompt (n88, m0, abandon) in each case. gpt-oss-20b fits at 36,864
with 94 tokens to spare; Qwen does not fit at 36,864, which is why the original Qwen run aborted
(inputs of 4,173 and 4,305 tokens). GPU hours are the wall times of the original runs from server
start to last answer, plus the sampler gate: 120b 8.13 h (Stage 1a); 20b 2.87 h; Qwen 24.0 h for
2,756 calls at 36,864 (one restart) plus 7.0 h for 204 calls at 40,960. The Qwen figure is an upper
estimate for a single server. Server launches checked against the original `server_args` lines
(model, revision, image, context, max-running, memory fraction, template).

The sampler gate calls (64 serial + 64 batched, at most one re-pick) store rules only, as in the
original gates. They are a gate, not data, and are not used in R1–R3.

## The 120b prediction record

The record is computed from the original Stage 1a, as locked. The 120b rerun runs before the record
is written, and the record states the rerun's R1 and R2 results beside it. If R1 fails for 120b
(a parse error), the record is computed from the rerun instead, and this is stated. The record is
written before any Stage 2 call in either case.

## Measures and predictions (locked)

- **R1 (parse).** On every rerun row, the runner's stored rule equals the rule obtained from the
  stored text by an independent parser written from the locked parse definition. Expected: all rows
  agree. Any disagreement is listed row by row, and the locked definition decides which is right.
  Truncated and unparsed counts are re-derived from `finish_reason` and text.
- **R2 (replication of the response).** For each model and each of S88, M88, R88 and E8: the
  difference between the original and the rerun value, with a 95 % interval from a cell-cluster
  bootstrap of both runs (20 cells, 20,000 resamples, seed 0). The measure replicates if the
  interval covers 0. There are 12 intervals; about 0.6 would miss 0 by chance alone, so a single
  miss is reported, not read as failure. A miss in two or more measures for the same model is read
  as non-replication for that model.
- **R3 (locked verdicts on the rerun, descriptive).** A1–A4 re-scored with Luna's original battery
  (real text) and the gpt-oss-20b rerun; B1 and B1-Qwen recomputed with the rerun fits (200 locked
  reps, seed 0; 2,000 beside with MC SE). The signs are compared with the locked verdicts. Not
  scored: the locked verdicts stay as they are.

## Pre-stated readings

- **R1 holds, R2 replicates:** the original labels were parsed correctly, and the response functions
  reproduce. The paper keeps the locked verdicts and reports the rerun as a replication with full
  records.
- **R1 fails:** the parser was wrong on some answers. The paper reports the original verdicts as
  locked, gives the rerun values as the corrected ones, and states which verdicts change sign.
- **R1 holds, R2 fails for a model:** the parse is right, but that model's response is not stable
  between runs. The paper reports both runs and widens the stated uncertainty of that model's
  class.

## Gates (live calls refused unless stated)

- Prompt-set hash equal to the original; draws equal.
- Server launch equal to the original run of that model, field by field (items 14 and 15).
- I_max + `max_tokens` ≤ context for each model's tokenizer.
- Sampler gate (live, cell-level prior, top share ≤ 0.8), as for the original runs.
- `--dry-check` plus a stub run: every row has non-empty text, and re-parse reproduces the stored
  fields (item 16).

## Design audit

1. **Fidelity.** Same prompts, decoding and server; only the records are fuller.
2. **Coverage.** All three batteries that lack text. Luna's battery has real text and is not rerun.
3. **Controls.** The original runs.
4. **Observability.** Cells see their prompts only.
5. **Gate consistency.** All gates run together before the first call.
6. **Statistical unit.** The cell for R2; the row for R1.
7. **Pre-stated readings.** Above.
8. **Recheck.** A package per model with real text follows each run.
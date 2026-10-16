# Amendment — ignore unknown extra JSON keys (local reasoning)

**Parent:** `TASK_LIFE_LOCAL_REASONING.md`  
**Also:** `AMENDMENT_LOCAL_REASONING_PARSE.md`, `AMENDMENT_LOCAL_REASONING_MODEL.md`  
**Status:** **locked** 2026-10-16 (OK). Parser-only; Step 0 restarts from scratch after the unit test.  
**Trigger:** Step 0 abort, DR-T world 1 generation 2 — 17/96 first-draw invalids, all
`unexpected task_answer or communication.say`; 16/17 recovered on re-sample; fallback 1/96.
Artifact: `runs/life_local_reasoning/DR_T/seed1/reasoning_diag.jsonl` (to be archived).

## Written after seeing (not used)

Written after seeing DR-T world-1 J at **g1 = 0.17**, **g2 = 0.19** (Step 0, aborted
before g3; DRs-T not started). **L1–L4 unchanged.** Those two numbers are **not**
used to set this rule, the abort threshold, or any prediction.

## Why

Thinking-2507 often adds keys the locked schema does not ask for
(`communication.say`, and the same reject path covers `task_answer`). Required
fields on those 17 draws were otherwise well-formed (`inferred_rule` a catalog
key, `kind=publish`, `signal` in 0–7). Luna never puts the model’s free `say`
string on the channel: published text is the catalog description of the chosen
key. Rejecting the whole draw for an unused extra key spends a re-sample and
trips the 10% abort without changing what the channel would have carried.

## Locked parse (local arms only: DR-T / DRs-T)

Parser-only. Prompt text, gate file, and gate hashes stay as locked
(`AMENDMENT_LOCAL_REASONING_MODEL` dry-check). Content-only channel
(`reasoning_content` is still never the accepted answer).

### Required fields — unchanged and strict

| Field | Rule |
|---|---|
| `inferred_rule` | Catalog key under `AMENDMENT_LOCAL_REASONING_PARSE` (bare `Rnnn`, or `Rnnn: <canonical description>` exact match). Anything else **invalid**. |
| `communication` | Object required. |
| `communication.kind` | Exactly `silence` or `publish`. Else **invalid**. |
| `communication.signal` | When `kind=publish`: integer in **0–7** (bool is not an int). Missing or out of range **invalid**. Not read when `kind=silence` (a `signal` then is an ignored extra key). |

**Duplicate required keys with conflicting values = invalid.** Keys:
`inferred_rule`, `communication.kind`, `communication.signal`. Detect with
`json.JSONDecoder(object_pairs_hook=…)` so the parser sees both occurrences
(default `json.loads` keeps only the last). Same key repeated with the **same**
value is not a conflict. Example that must fail:
`{"inferred_rule":"R004","inferred_rule":"R021","communication":{"kind":"publish","signal":0}}`.

Missing or invalid required field, or a conflicting duplicate → invalid as before:
one re-sample, then unsolved fallback.

### Unknown extra keys — ignore

Any key that is not in the required set above, at any depth in the object
(examples: top-level `task_answer`; `communication.say`; `communication.text`),
is **dropped**. It does not make the draw invalid.

Per generation, log **`extra_keys_ignored`**: count of decisions whose accepted
JSON contained at least one dropped key (and, in the diagnostic row, the key
paths). Descriptive only. Does not enter the abort share.

### Channel

Dropped keys **never reach the channel**. Encode as Luna does today:

- `kind=silence` → silence.
- `kind=publish` → publish `signal` as given, and `say` = the **canonical
  catalog description** of the accepted `inferred_rule` key — not the model’s
  `say` / `text` string.

## Abort (threshold unchanged)

Applied to **remaining** invalids (required-field failures and truncation), not
to ignored extras:

- first-draw invalid + truncated **> 10%** of cell-decisions in a generation → abort
- fallback **≤ 2%** (share **> 2%** → abort)

Same thresholds as Step 0 / smoke today.

## Step 0 restart

After this amendment is locked and the parser + unit test land in a **new
commit**:

- Archive the aborted run (do not resume it):  
  `runs/life_local_reasoning/step0_aborted_3a49e62/`  
  holding `DR_T/seed1/` (`report.json`, `reasoning_diag.jsonl`, `rule_history.json`),
  `step0_readout.md`, `step0_summary.json`, and `step0.log`.
- Fresh caches for DR-T and DRs-T. No Step 1 reuse of world 1 from the aborted
  commit.
- Restart Step 0 from generation 1 (`--step0 --allow-step0`) only after OK.

## Dry-check

Prompt and gate hashes **unchanged** (parser-only). Existing
`runs/life_local_reasoning/dry_check.json` remains the prompt witness; re-run
`--dry-check` must still pass with the same g2 sha16 table.

## Unit test (required before the restart)

The 17 logged first-draw `content` objects (DR-T seed 1, generation 2,
`first_draw_invalid` and error `unexpected task_answer or communication.say`
in `reasoning_diag.jsonl`) must parse, under the new rule, to the same
`inferred_rule` key and the same `communication.kind` / `signal` that the
content states. All 17 are `kind=publish`, `signal=0`, plus ignored
`communication.say`. Key counts (sum 17):

| key | n | cells |
|---|---:|---|
| R004 | **12** | 2, 10, 16, 18, 24, 26, 27, 48, 54, 62, 64, 75 |
| R064 | 3 | 17, 39, 74 |
| R021 | 1 | 3 |
| R086 | 1 | 66 |

The earlier draft listed R004 as 11 (sum 16). The 17th is **cell 75, R004** —
same shape as the other R004 draws (`say` = `shift_symbols(1)`), not a different
schema. It does not differ.

**Fallback (cell 39)** is one of the three R064 first-draws. Its first-draw
content does not differ (R064, publish, signal 0, extra `say`). It fell back
because the **re-sample** also carried `communication.say`
(`inferred_rule` R083, `say` `shift_symbols(5);swap(0,1)`), so both draws were
invalid under the old rule. Under this amendment that re-sample would be
accepted as R083 / publish / signal 0 with `say` ignored.

The model’s `say` string is not the channel text. A fixture copied from those
tails is enough; do not re-query the model.

Also required: one synthetic case with conflicting duplicate `inferred_rule`
(and one with conflicting `communication.kind` or `communication.signal`) →
invalid, via `object_pairs_hook`.

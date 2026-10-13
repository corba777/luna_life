# Task — An with `temperature=0` (An-T0): is the parameter accepted and honoured?

**Status:** locked. Predictions are locked with this file, before any spend. API only
(Luna Responses, `effort=none`), no GPU. Follows `DESIGN_CHECKLIST.md`. Parents:
`TASK_LIFE_LUNA_NONE.md` (An), `TASK_LIFE_CA_SAMPLE.md` (An sampling gate; S1–S3 closed).

**Design checklist:** Gate covers items 1–2 (payload identity: An-T0 vs An differs only by
the presence of `temperature: 0`; commit `prompts/an_t0_gate.md` before spend). Item 3:
this is a single-prompt probe of sampling control, not a group claim. Items 4–6 apply.
Item 7: report API USD + prefill/output tokens per call.

## Why

An’s Life requests omit `temperature` and `top_p`. The Responses API reference documents
`temperature` as optional (0–2) but **does not state a default** and says nothing about
reasoning models or `effort`. Ca-sample (S1 PASS / S2–S3 FAIL) showed that sampling from
Decisions π̄ makes cells mobile but does not recover An’s J@g10. Whether An’s decode is
non-greedy therefore remains open until we know whether `temperature=0` is accepted for
`gpt-6-luna` + `effort=none` and whether it collapses repeat draws.

## Protocol

Fixed Life-shaped Responses prompt (An schema, `effort=none`, same structured
`text.format` as An). One prompt for all calls below. Cache off for honour draws
(each draw must hit the API).

### Step 0 — Feasibility

Send **one** request with `temperature=0` (and `effort=none`).

- **PASS:** HTTP 200, `status=completed`, structured JSON parses to a catalog rule.
- **FAIL:** HTTP 4xx rejecting `temperature`, or incomplete / unparseable output.
- On FAIL: stop; do not run Step 1. Report the error body.

### Step 1 — Honour (5× repeats)

After Step 0 PASS: for the same prompt,

- **A (omit):** 5 independent calls with no `temperature` / `top_p` (An payload).
- **B (`temperature=0`):** 5 independent calls with `temperature=0`.

Score each arm by the number of unique `inferred_rule` values across its 5 draws
(`n_unique`). Also log full response text hashes.

## Gate (before the first call)

1. Dry-render the An-T0 request body vs An: the only allowed payload difference is the
   presence of `"temperature": 0`. Prompt `input`, `reasoning.effort`, `max_output_tokens`,
   and `text` format must be byte-identical.
2. Startup asserts: model `gpt-6-luna`; `effort=none`; no reasoning text requested or
   stored; cache keys include `temperature`.
3. Record the Responses API reference quote for `temperature` (verbatim) in
   `prompts/an_t0_gate.md`. Fact for An when omitted: **no temperature/top_p sent;
   default not stated in the API reference.**

Commit `prompts/an_t0_gate.md` before spend.

## Predictions (lock)

- **T0 (feasibility):** Step 0 PASS.
- **T1 (honoured):** under B, `n_unique = 1` (all five `temperature=0` draws agree).
- **T2 (omit is non-degenerate, descriptive):** under A, report `n_unique`; if A also
  has `n_unique = 1`, temperature alone does not explain An’s mobility vs Ca.

## Readout

- **T0 FAIL:** cannot set temperature on this surface; An’s decode remains undocumented.
- **T0 PASS, T1 PASS, A `n_unique` > 1:** `temperature=0` is accepted and collapses
  sampling; An Life (omit) is a non-greedy decode relative to T=0.
- **T0 PASS, T1 FAIL:** parameter accepted but not honoured as a deterministic decode
  on this model/effort; do not treat An as “temperature-1 sampling” or “temperature-0”.
- **T0 PASS, T1 PASS, A `n_unique` = 1:** both arms deterministic on this prompt; a Life
  rerun with T=0 is needed before claiming a mobility mechanism (not in this task).

## Cost

≤ 11 Responses calls (1 + 5 + 5) on one An-sized prompt. Alarm **$3** (not a stop).
Report actual USD and tokens.

## Queue

**After** the Decisions repeat check closes (`runs/life_decisions_repeat/repeat.ok`).
Before Distributed Phase 1. Independent of Ca-sample / An0 outcomes.

## Artifacts

`prompts/an_t0_gate.md`, `runs/life_an_t0/step0.json`, `runs/life_an_t0/step1.json`,
`runs/life_an_t0/summary.json`, `runs/life_an_t0/readout.md`.

## Constraints

Placement only: no training on outputs; no reasoning text requested or stored. New runner
script; do not edit running Life runners in place. Commit this file before the gate;
amendments before numbers.

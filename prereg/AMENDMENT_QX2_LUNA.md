# Amendment — QX-2: one Luna run per cell, δ ∈ {1/64, 1/8} × B ∈ {1, 4}

**Status:** locked v2 (2026-11-15; v2 adds the two δ = 1/8 cells and sets the spend stop at $10, both Artem's decisions), written by the reviewer for Artem. Dry build passed (no model call); locked after the reviewer's review. No call is made before Artem's
go, logged in the switch log with his words. The run uses the API, so it needs no GPU and may run
beside the GPU queue.

## Why

The gpt-oss-20b pilot (`AMENDMENT_QX2_PILOT_20B.md`, rechecked 2026-11-15) left the main cell
(δ = 1/64, B = 4) at the floor:
- 44 of 400 tests were used;
- none of them was on a δ-input;
- abandonment was 0.01 and recovery 0.

At δ = 1/8, the 20b cells found refutations but almost never shared them. This amendment runs the
same cells on the threshold model, which is the strongest model in the project.
- **At δ = 1/64.** Does the floor belong to the model or to the setting?
- **At δ = 1/8.** Does a model that finds refutations also share them?

## Scope (Artem, 2026-11-15)

The pilot amendment (§5) allowed only δ = 1/64, at an upper estimate of at most $5. Artem widened
the scope to the four cells below and set the limit at $10 (2026-11-15). That decision is recorded
here and in the switch log.

| order | arm | δ | B | replicates | calls |
|---:|---|---|---:|---:|---:|
| 1 | `luna_d64_B4_r1` | 1/64 | 4 | 1 | 1,200 |
| 2 | `luna_d8_B4_r1` | 1/8 | 4 | 1 | 1,200 |
| 3 | `luna_d8_B1_r1` | 1/8 | 1 | 1 | 1,200 |
| 4 | `luna_d64_B1_r1` | 1/64 | 1 | 1 | 1,200 |
| | **total** | | | | **4,800** (+ retries) |

The arms run in this order, the most informative first. Any later Luna run needs its own amendment.

## Unchanged from the pilot

The following are as locked in `AMENDMENT_QX2_PHASE1.md` and used by the pilot:
- the world (seed 0, G = 12), catalog, prompt and schema;
- the mapper, retry and fallback rules;
- the protocol, the engine invariants and the format gate;
- the generation-synchronous order and the cache key.

The prompt bytes are those the pilot renders. Only the model client differs.

## Model and client

- **Model.** `gpt-6-luna` through the Responses API, at reasoning effort medium. The client is the one
  used in QX-1p, including its prompt-cache layout: the fixed prefix is cached and the per-cell part
  is written fresh.
- **Settings.** Temperature and top_p are not sent, as in every Luna run in the project.
- **Reasoning.** Luna's reasoning is closed, so it is never stored. Only the final answer text and the
  usage are kept.
- **Concurrency.** As in QX-1p.
- **Records.** Every call records the model string and the date the API returns.

## Spend stop

- **Running cost.** It is computed after every call from that call's billed usage at the QX-1p unit
  prices.
- **Hard stop at $10.00 in total.**
  - The run stops when the cost reaches $10.00, and it is never resumed without a new amendment line
    and Artem's go.
  - The stop leaves the run's state as is, marked `.aborted`, with the reason.
  - Calls already in flight when the stop fires are allowed to finish and are billed. The overshoot
    is at most the concurrency times the cost of one call, a few cents at the QX-1p settings, and it
    is reported.
  - Arms finished before the stop stand as complete. The interrupted arm is reported as partial,
    with the generation it reached.
- **Expected cost.** It scales `luna_estimate.json` (2,400 calls: $2.07 central, $3.50 upper) to 4,800
  calls: about $4.1, with an upper case of $7.0. That estimate uses 20b completion lengths, and
  Luna's may be longer.
- **Before any call.** The dry build states the envelope left. It is $13.20, so the most the run can
  leave is $3.20.

## Readout (descriptive)

- **As in the pilot readout, §6.** Abandonment and recovery beside the scripted references for the
  same δ and B; first refutation; test quality; the test descriptives (pattern, shape, Hamming); the
  message mix; refuting results shared and relayed; fallback and truncation.
- **The finder breakdown**, as on the QX page:
  - the cells that tested a refuting input, and the rule each ended on;
  - the cells that ended on H_T, and how many of them were finders.
- **Signal use:** the distribution of signals by generation, and by message content.
- **Cost:** per call, per arm and in total.

The readout has no contrast and no p-value. Each arm is one replicate, so nothing is claimed beyond
these two runs.

## Dry build (CPU, no call)

1. **Prompt identity.** The generation-1 prompt for cell 37 is byte-identical to the pilot's for each
   of the four cells (δ, B). The pilot ran δ = 1/8 at both budgets and δ = 1/64 at B = 4. For
   δ = 1/64 at B = 1, the reference is the phase-1 sample `gen1_B1.txt`.
2. **Request body.** It shows the model string, effort medium, and no temperature or top_p.
3. **Spend stop.** On synthetic usage, it fires at the first call that would cross $10.00. The run is
   marked `.aborted` and makes no further call.
4. **Fake client.** It runs the four arms in order through the engine, with every invariant asserted.
5. **Records.** No reasoning field is written.

## Outputs

- Calls (final text and usage), traces and the readout.
- A recheck package with SHA256SUMS.

Nothing enters the QX page before the reviewer's recheck from raw data.

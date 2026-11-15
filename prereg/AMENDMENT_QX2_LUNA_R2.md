# Amendment — QX-2 Luna, second replicate with independent arms

**Status:** locked v1 (2026-11-15), written by the reviewer for Artem. Dry build passed (items 1–5, no
model call); locked after the reviewer's review. No call is made before Artem's go, logged in the
switch log with his words. It uses the API, so it needs no GPU and may run at any time; it does not
enter the GPU queue.

## Why

The first Luna run (`AMENDMENT_QX2_LUNA.md`, rechecked 2026-11-15) has two limits:
- **One run per cell.**
- **Shared openings.** The two δ arms at the same budget share their first generations. The
  client's cache key was the prompt only, so 475 answers in generations 1–4 were served from the
  sibling arm.

This amendment runs every cell once more, with a fresh cache keyed by arm. That gives a second
replicate per cell, and four arms that are independent of each other and of the first run.

## Scope

| order | arm | δ | B | calls |
|---:|---|---|---:|---:|
| 1 | `luna_d64_B4_r2` | 1/64 | 4 | 1,200 |
| 2 | `luna_d8_B4_r2` | 1/8 | 4 | 1,200 |
| 3 | `luna_d8_B1_r2` | 1/8 | 1 | 1,200 |
| 4 | `luna_d64_B1_r2` | 1/64 | 1 | 1,200 |
| | **total** | | | **4,800** (+ retries) |

## Unchanged from the first Luna run

As locked in `AMENDMENT_QX2_LUNA.md`:
- world, catalog, prompt bytes and schema;
- mapper, retry and fallback rules;
- protocol, engine invariants and format gate;
- model `gpt-6-luna` through the Responses API at effort medium, with temperature and top_p not
  sent;
- `max_output_tokens` 8,192;
- closed reasoning, never stored.

## Changes

- **Cache.** A new, empty directory, `runs/qx2_luna_r2/cache`. The key is the prompt, the draw and
  the arm name. No answer from the first run, or from another arm, can be served.
- **Spend.** Counted with the corrected `usage_token_parts`, where uncached = input − cached −
  cache_write.
- **Hard stop at $5.00 in total,** with the same rules as before:
  - no resume without a new amendment line and Artem's go;
  - calls in flight finish and are reported;
  - finished arms stand, and an interrupted arm is reported as partial.
- **Expected cost.** About $2.30, from the first run's corrected cost. More may be spent, because no
  answer is reused. The envelope left is about $10.95.

## Readout (descriptive)

- **Per arm.** The same items as the completed first-run readout.
- **Side by side.** For each cell: r1 and r2 recovery, finders, refuting results shared (own and
  relayed), and the δ-share of tests.
- **The post hoc line on the QX page.** For each run, the cells that reached H_T without a
  counterexample of their own, and how many of them had first seen one shared by a neighbour. It is
  recomputed for r2 and labelled as a replication of a post hoc observation.

There is no test and no p-value. With two runs per cell, the page reports both and their range.

## Dry build (CPU, no call)

1. **Prompt identity.** As before.
2. **Cache key.** It includes the arm. Two arms with an identical prompt get different keys, and the
   r2 cache directory is empty at start.
3. **Spend.** The corrected billing on a stored r1 usage row reproduces that row's corrected cost.
4. **Spend stop.** It fires at $5.00 on synthetic usage.
5. **Fake client.** It runs the four arms in order through the engine, with every invariant asserted.

## Outputs

- Calls (final text and usage), traces and the readout.
- A recheck package with SHA256SUMS.

Nothing enters the QX page before the reviewer's recheck from raw data.

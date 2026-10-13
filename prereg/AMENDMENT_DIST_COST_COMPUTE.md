# Amendment — Distributed Life: cost = price and compute

**Status:** locked. Parent: `TASK_LIFE_DISTRIBUTED.md` (locked). No predictions change.
Applies before Phase 1 API and before any Phase 2 run. Implements `DESIGN_CHECKLIST.md`
item 7 (“Cost: price is not compute”).

## What changes

The Cost section of the parent now requires every readout (Phase 1 and Phase 2) to report:

- **(a) API USD at list price** (Phase 1: Luna list rates; Phase 2: N/A dollars if fully local,
  or list USD if any API surface is used).
- **(b) Compute:** prefill and decode tokens **per cell-generation**, separately.
  Phase 2 (local GPU) also reports **measured GPU-seconds per cell-generation**.

Phase 1 dollar estimates and the $25 alarm in the parent are unchanged. Phase 2 predictions
remain deferred to a separate amendment before its first run; this amendment only fixes the
cost reporting rule for that phase (and for Phase 1 summaries).

## Parent Cost section (replacement text)

```
## Cost

Reporting rule (`DESIGN_CHECKLIST.md` item 7): every readout gives (a) API USD at list price
and (b) compute — prefill and decode tokens per cell-generation, separately; for local runs
also measured GPU-seconds per cell-generation.

Phase 1 (API): DR and DRs ≈ $0.45 per seed each (10 seeds total); DC and DCs ≈ $1.0 per seed
each at P=4 (10 seeds); DRo ≈ 100 calls. Estimate ≈ $16–20; alarm $25 (alarm, not a stop).
Report actual list-price USD per arm and prefill/decode tokens per cell-generation.

Phase 2 (local): same (b) with GPU-seconds per cell-generation; USD only if an API surface is
used. Predictions for Phase 2 remain in a separate amendment before its first run.
```

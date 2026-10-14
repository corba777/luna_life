# Amendment — Distributed DR vs DC allowed prompt diffs

**Status:** locked; **`ALLOW_PHASE1` released** after Ca-sample close (root cause of
Ca-sample INVALID = shared cache + identical seeds, not a key bug). Amends
`TASK_LIFE_DISTRIBUTED.md` gate item 2 (DR vs DC) and the Channel filter paragraph.
Precedent: `TASK_LIFE_LUNA_NONE.md` gate item 2 (An vs Ca).

## 1. DR vs DC — verbatim allowed differences

Pre-catalog **state text** (world + “You see …” + publish paragraph + cell
examples / query / memory / inbox) must be **byte-identical** across DR and DC
for the same seed, cell, and history.

The **only** allowed differences are:

1. **Output-format instruction (JSON / typed constitution tail)**
   - **DR (Responses / JSON):**
     ```
     inferred_rule is required. Write the hidden transformation as you currently understand it.

     Output a single JSON object and nothing else.
     ```
     The strict JSON schema is **not** inlined in the prompt text. It is passed as
     the Responses API parameter `text.format` (`life_cell_decision_v2` via
     `responses_text_format` / `LunaResponsesCompleter.complete_structured`). Do
     **not** require or allow an `Output shape:` block in `input`.
   - **DC (Decisions / typed):**
     ```
     Choose the hidden transformation from the listed options. The engine applies your chosen transformation to your query; that is your answer.
     ```

2. **Option rendering**
   - **DR:** keyed rule catalog in the prompt text (`Rule catalog (choose by key):` /
     `R000: <description>` …); catalog-key enum lives in `text.format` schema, not
     in the user block.
   - **DC:** catalog descriptions as Decisions choice `criteria` (not inlined in the
     prompt text); P=4 option-order average; decode=argmax.

Anything else in the pre-catalog text (including the publish paragraph) must be
unified. The publish paragraph uses the Responses / JSON wording for **both**
DR and DC:

```
You may publish at most one message this generation, or stay silent. A message has an integer signal 0–7 and a short text (at most 96 UTF-8 bytes). Published messages become visible only from the next generation, and only to cells allowed to see them. Your task_answer and inferred_rule are not shown to other cells. Messages may name a transformation; they never carry private examples.
```

DC → DCs and DR → DRs keep the same allowed set as before (channel lines, inbox
present vs absent, memory `published=` value only).

## 2. Channel filter — canonicalize (supersedes exact match)

**Was:** deliver only if published text exactly equals a canonical catalog
description.

**Now:** normalize (strip, lower-case, drop trailing `.`, remove whitespace
inside ops), `parse_program`, `catalog.canonicalize`; if that yields a catalog
rule, deliver the canonical `description()`; otherwise drop (empty slot).

Drop share is reported per **arm × seed × generation** in the Phase 1 readout.

Implementation: `life_verify.distributed.filter_catalog_say`.

## 3. Silent arms — `published=no`

DRs / DCs never publish. Memory always shows `published=no` at g≥2 (g1:
`Previous step: none.`). The `published=yes` lines in an early dry-render were
from a forced shared history used for both channel and silent arms — not a
runtime path. Startup assert: DRs/DCs prompts must not contain
`published=yes`.

## 4. Constitution diffs (gate artifacts)

| pair | artifact |
|---|---|
| DR vs v1b channel | `runs/life_distributed/gate_dry/constitution_v1b_vs_DR.diff` |
| DRs vs v1b no-channel | `runs/life_distributed/gate_dry/constitution_v1b_nochannel_vs_DRs.diff` |
| DCs vs v1b no-channel (typed tail) | `runs/life_distributed/gate_dry/constitution_v1b_nochannel_vs_DCs.diff` |
| DRo vs expected (this amendment) | `runs/life_distributed/gate_dry/constitution_DRo_vs_expected.diff` |

### DRo expected constitution (verbatim)

```
You are one cell among 100 on a wrapping 10×10 grid.

Each cell has its own private task for this epoch: a hidden transformation of 4-symbol strings over A–H. Every cell in the epoch has the same hidden transformation, but different private examples and a different query each generation. There is no shared score.

You see nine private example pairs from one Moore neighbourhood (the centre cell and its eight neighbours), your current query, and a one-step memory of the rule you held last generation (and whether you published it). You are not told whether your last rule was correct.

inferred_rule is required. Write the hidden transformation as you currently understand it. You cannot send or receive messages.

Output a single JSON object and nothing else.
```

## 5. Release gate — `ALLOW_PHASE1` (**released**)

Dry-render accepted. Ca-sample closed on arm C data (`TASK_LIFE_CA_SAMPLE.md`);
marker: `runs/life_distributed/ALLOW_PHASE1`.

Phase 1 runner **must** startup-assert for **every** arm:

1. **Fresh per-arm caches (empty on first launch)** —
   `runs/life_distributed/cache_{DR,DRs,DRo,DC,DCs}/` must not exist or be empty
   at first launch (never share `cache_C` or another arm’s dir). On **resume**,
   keep a per-arm `cache_manifest.json` of keys written by this arm; every cache
   hit must be in that manifest.
2. **Per-generation log** of `live_requests`, `cache_hits`, `outcomes_first` /
   `forced` / `uniform` (and Responses equivalents where applicable).
3. **Fail loud** if **any** arm (DR / DRs / DRo / DC / DCs) at any `g≥2` has
   `live_requests == 0`. Decisions arms (DC / DCs) also fail if
   `outcomes_uniform / n_choose > 0.02`.

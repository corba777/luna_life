# Amendment — Local reasoning `inferred_rule` parse (B3)

**Parent:** `TASK_LIFE_LOCAL_REASONING.md`  
**Status:** locked before Step 0 (no Step 0 number yet).  
**Code:** `life_verify/local_reasoning_prompt.py::normalize_inferred_rule_value`,
`runs/run_life_local_reasoning.py::parse_last_json_object`.

## Why

Smoke (2026-10-15) showed two parse defects that are not prompt-gate changes:

1. **Nested JSON trap.** Scanning every `{` and keeping the last successful
   `raw_decode` selected the nested `communication` object, so a valid
   `"inferred_rule": "R006"` became `ikey=None` and every first draw was
   invalid. Fix: after a successful decode, advance the scan past that object
   so nested braces are not treated as separate top-level objects.

2. **Key-plus-text form.** Models sometimes emit
   `"R027: reverse;swap(2,3)"` instead of a bare catalog key. Silently
   accepting free text would break the keyed catalog contract.

## Locked rule (local arms only)

After extracting the last top-level JSON object:

| `inferred_rule` value | Decision |
|---|---|
| Bare catalog key (`R006`) present in the keyed catalog | accept |
| `"<key>: <rule text>"` where `key` is in the catalog **and** `<rule text>` equals that key’s canonical `description()` (exact string match to the catalog line) | accept; store the bare key |
| Any other string (wrong key, text mismatch, free rule text, empty) | **invalid** (resample once, then unsolved fallback) |

Do **not** fuzzy-match, strip ops, or accept description-only strings.

## Scope

Applies to DR-S / DRs-S local decoding only. Luna Responses schema still forces
an enum key. Does not change rendered prompt text (gate hashes unchanged).

## Smoke abort (same file / runner)

Smoke mode must apply the same abort shares as Step 0/1:

- first-draw truncated + invalid > 10% → **FAIL**
- fallback > 2% → **FAIL**

`smoke_ok: true` with 100% fallback is a hygiene bug (logged in
`runs/spade_grid/CHAIN_HYGIENE.md`).

# Rule-preference gate diffs

**Task:** `TASK_LUNA_RULE_PREFERENCE.md`.  
**Status:** PENDING — run the gate and replace this file before any API spend.  
**Queue:** after An closes; this file must PASS; then API; before Distributed Phase 1.

## Expected differences (checklist item 1; lock text)

Comparison arm: **Ca** (Decisions, channel on, 4 sources) g2 request for the same seed/cell.

### Probe A (prior, no evidence) vs Ca g2

Expected differences **only**:
- The examples block in the state: Ca's private example line(s) → replaced by the single line  
  `No examples are available.`
- Everything else (constitution, memory, inbox, catalog, query, Decisions option rendering,
  P=4 order seeds) unchanged relative to Ca for that cell.

### Probe B (pair, own example) vs Ca g2

Expected differences **only**:
- The option / hypothesis list: full 101-rule catalog → two options only: seed `P_e` vs the
  seed's modal false rule in Ca at g10 (labels and criteria as Decisions).
- Cell's own private example kept (same as Ca). Inbox / memory / constitution unchanged.

### Probe C (adoption replay)

- Request text must be **byte-identical** to the logged Ca request for that cell-generation
  (request hash match). No listed differences. Hash mismatches are reported, not dropped.

## Gate result

Not run yet. Startup asserts when run: Decisions estimator; P=4; no Responses / no reasoning
text; seeds = frozen 2-op schedule 1–5.

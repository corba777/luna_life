# Amendment — QX-1r: QX-1 replication (Qwen3-4B-Thinking)

**Status:** locked 2026-10-27 for tests, before any QX-1r call. Local, pre-approved. No call before
this file is committed as locked. Dry-build prompt identity and aimed gates reuse QX-1p:
`runs/life_dr_qwen/qx1p/dry_build.json` (prompt digest `c58f90b5…`, aimed gates on 4,096 inputs).
Basis: `AMENDMENT_DR_QWEN_QX1.md` (locked), `AMENDMENT_QX1P_PANEL.md` (measures), `QX_TRACK_PLAN.md`.
Mirror: Life surface → `luna_life` `prereg/` when committed.

## Why

QX-1 on Qwen3-4B-Thinking gave a borderline X1 pass (confirming share C1 0.438 vs C0 0.362,
one-sided paired sign-flip p = 0.048). A fresh-draw replication decides whether X1 is stable. After
QX-1 descriptives, **aimed confirming** (confirming minus cross-world null) was defined to separate
tests aimed at the shared hypothesis from constant inputs; the QX-1 Qwen aimed mean shift (+0.0458,
MC sign-flip p ≈ 0.0016) is **post hoc** because that measure post-dates QX-1. QX-1r locks **X1a**
before any QX-1r call so the aimed shift has a confirmatory test.

## Design

Same as QX-1: 480 prompts (3 worlds × 20 class-A cells × C0/C1 × 4 draws), **fresh draws** (new
random seeds per call, not a replay of QX-1 outputs). Byte-identical prompt set to QX-1 (sha256
`c58f90b5328776b450fc182ea1748c2bda33c30caf9c78467269eee2f78c0d8e`, matches
`runs/life_dr_qwen/qx1/MANIFEST.json` and `gate.json`). Model: **Qwen3-4B-Thinking-2507**, local,
Stage 1 DR Qwen settings (own cache, lock, v2 watchdog). Parser, exclusion rule (>5% parse failures
in a condition: reported, not tested), memory line, added sentence and `test=XXXX` field unchanged
from QX-1.

## Measures

As in `AMENDMENT_QX1P_PANEL.md`:

- **confirming:** x_{i_w} = x_{j_w} for the cell's world pair;
- **cross-world null:** mean over the other two worlds' pairs of 1[x_{i_v} = x_{j_v}];
- **aimed confirming:** confirming minus cross-world null, per call; arm-level means pool the three
  worlds.

**Descriptives beside the locked tests (not scored):** pattern distribution (**AAAA** / **ABCD** /
**other**, relabeled first-appearance convention), cross-world confirming null rate, example-structure
retention, Hamming distance from the own example — as in `QX_TRACK_PLAN.md` and the QX-1 readout.

## Predictions (locked)

Unit: the cell (60 cells). One-sided paired Monte Carlo sign-flip over cells, **20,000 flips**,
**seed 0**, **α = 0.05**. Report beside each test the count of cells with a non-zero paired
difference.

- **X1 (original, as in QX-1):** P(confirming | C1) > P(confirming | C0).
- **X1a (aimed shift):** mean aimed confirming in C1 > mean aimed confirming in C0; same test
  settings as X1.

No direction is locked for descriptives. X1 replication direction and α unchanged from QX-1.

**Erratum (Artem, 2026-11-12; before any QX-1r call).** The test settings above are corrected as
follows; direction, unit, α and measures unchanged.

- **X1:** exact one-sided paired sign-flip by full enumeration over cells, as the locked X1 in QX-1
  (correction of 2026-10-28). The Monte Carlo value (20,000 flips, seed 0) is reported beside it.
- **X1a:** Monte Carlo sign-flip (20,000 flips, seed 0) as above; the exact value is reported beside
  it.
- If the two values for a test ever fall on different sides of α = 0.05, the exact value decides.

## Pre-stated readings

- **QX-1r is the confirmatory test of the post-hoc QX-1 aimed shift.** X1a on QX-1r is
  confirmatory; the QX-1 aimed mean diff was exploratory because the measure was defined after QX-1
  was seen.
- **X1 passes on QX-1r:** social consensus again shifts test choice toward confirming inputs;
  combined with QX-1, treat as a finding unless the two runs strongly disagree.
- **X1 fails on QX-1r:** X1 on QX-1 alone was likely a borderline draw; report both runs.
- **X1a passes:** under consensus, the agent chooses inputs specifically aimed at the shared false
  rule (not only constant strings). **X1a fails:** no confirmatory aimed shift at this precision.
- **If the design is the cause:** same neutral sentence and identical C0/C1 wording as QX-1; the
  readout says so.

## Gates

Before live calls, the runner must pass the same checks as QX-1p dry build (live refused,
`no_server_loaded: true` where applicable):

- Prompt identity: digest `c58f90b5…` matches the QX-1 set.
- Aimed confirming on all **4,096** inputs (12,288 world×input evaluations): constant inputs → aimed
  0; uniform / exhaustive means → 0 per world — as in `runs/life_dr_qwen/qx1p/dry_build.json`
  `aimed_gates`.

Rebuilt prompts or schema drift from the gated build → refuse to call.

## Design audit

1. **Fidelity.** Same 480-prompt design and scoring as QX-1; only draw seeds differ. Pass.
2. **Coverage.** Worlds 1, 3, 5; class A; Qwen3-4B-Thinking only. Pass.
3. **Controls.** C0 vs C1 within run; cross-world null within call. Pass.
4. **Observability.** Choice only; no test output returned. Pass.
5. **Gate consistency.** Prompt digest and aimed gates cite QX-1p dry build; run together at QX-1r
   gate time. Pass.
6. **Statistical unit.** Cell; paired sign-flip over 60 cells; X1 and X1a both locked before calls.
   Pass.
7. **Pre-stated readings.** Above. Pass.

## Queue

With **wave 2a** (same window as QXp-qi in `AMENDMENT_QX1P_PANEL.md`). **No QX-1r call until this
amendment is locked and committed.** After QI-I / moore chain as in QX-1 queue; no server loaded for
QX alone.

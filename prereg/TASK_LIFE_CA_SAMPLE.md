# Task — One-pass cells with sampled decisions (Ca-sample): model or readout?

**Status:** locked. Predictions are locked with this file, before any run. API only (Luna
Decisions), no GPU. Runs **after** `TASK_LIFE_AN_NO_SOURCE.md` (An0) closes; does not depend on its
outcome. Follows `DESIGN_CHECKLIST.md`. Parents: `TASK_LIFE_REASONING_CELLS.md` (Ca),
`TASK_LIFE_LUNA_NONE.md` (An), `TASK_LIFE_AN_FILTER.md` (F1–F4 FAIL).

**Design checklist:** Gate covers items 1–2 (Ca-sample vs Ca: g1 request hashes / forced-history
g2 byte-identical; only `choose(..., decode)` changes). Item 3: S1–S3 are readout contrasts
within the same Decisions population, not “group vs individuals”. Items 4–6 apply. Item 7:
API USD + prefill tokens per cell-generation.

## Why

An (Luna Responses, `effort=none`) beats Ca (Decisions) in Life, J@g10 0.47 vs 0.25, while the two
are equal alone (two-op pairs 0.60 vs 0.59). `TASK_LIFE_AN_FILTER` found no own-example filter in
An. What differs is mobility: An adopts the inbox majority more and keeps P_e less
(r 0.71 vs 0.97); Ca is sticky.

Ca's decision is an argmax of probabilities averaged over four option orders: deterministic, a
zero-temperature readout (replays reproduce logged choices exactly, R3 Δ = 0). An produces one
text generation per cell-generation. If An's sampling is not greedy, the An–Ca gap may be a
difference in **how the decision is read out**, not in the model. This task changes only the
readout of Ca.

## Arm

| arm | cells | readout | sources | channel | check | parent |
|---|---|---|---|---|---|---|
| **Ca-sample** | Luna Decisions, P=4 | **sample** rule ~ π̄ | 4 | on | none | Ca |

- π̄ = the same P=4 mean probability vector over catalog options that Ca uses for argmax.
  The rule is drawn from π̄ (no temperature rescaling, no truncation). RNG seeded per
  (world seed, generation, cell) with a committed function; draws are logged.
- 2-op seeds 1–5, 10 generations. Everything else as Ca: prompt, catalog, memory line, sources,
  constitution, validity/fallback rule.
- **References (not rerun):** Ca, An, An0, Ca0, B.

## Gate (before the first call)

1. **Ca-sample vs Ca requests:** g1 requests byte-identical to Ca (same request hashes; expect
   cache hits). From g2 on, request text may differ only through state that follows from different
   earlier choices (inbox, memory line contents); format identical. Dry-render 3 cells at g2 with
   a forced identical history and diff against Ca: must be byte-identical.
2. **Readout code:** the only code difference from the Ca runner is argmax → seeded draw from π̄.
   Show the diff of the decision function in `prompts/ca_sample_gate_diffs.md`.
3. **An sampling parameters:** record from the logged An request payloads the sampling settings
   actually sent (temperature, top_p or their absence). Descriptive; it states what An's readout
   was. Do not invent an API default — the Responses reference does not state one.
4. Startup asserts: 4 sources; channel on; no check; draws logged with RNG seeds.

## Metrics

- J@g10 and mean J (96 non-source cells), labelled; locks; modal rule at g10.
- h(1), r, P(keep rule | prev ≠ P_e), same definitions as `TASK_LIFE_AN_FILTER`.
- Readout diagnostics: share of decisions where the draw ≠ argmax; entropy of π̄ and π̄(argmax),
  by (prev = P_e, correct=true) vs other states.
- Cost: API USD, prefill tokens per cell-generation.

## Predictions (lock)

- **S1 (readout makes cells mobile):** Ca-sample r ≤ 0.85 (Ca 0.97, An 0.71).
- **S2 (mobility helps with sources):** Ca-sample seed-mean J@g10 ≥ Ca + 0.10 (≥ 0.35).
- **S3 (the An–Ca gap is the readout):** |Ca-sample − An| seed-mean J@g10 < 0.10.

## Readout

- **S1, S2, S3 PASS:** the An–Ca difference in Life is a sampling-vs-argmax difference; reasoning
  off and Decisions are the same agent in Life too, read out differently.
- **S1 PASS, S3 FAIL:** sampling makes Ca mobile, but text generation adds something else; compare
  h(1) by inbox stratum with An.
- **S1 FAIL:** π̄ is too sharp for sampling to matter (report the draw ≠ argmax share); An's
  mobility comes from text generation, not from a non-zero temperature alone.

## Cost

Five seeds at Ca rates (~$1 per seed): about $5. Alarm $8 (not a stop). Report the actual cost.

## Artifacts

`prompts/ca_sample_gate_diffs.md`, `runs/life_ca_sample/seed{n}/` (with draw logs),
`runs/life_ca_sample/summary.json` (S1–S3 with Ca, An, An0 alongside), `fig_ca_sample.png`
(J(g) per seed: Ca, Ca-sample, An).

## Constraints

Placement only: no training on outputs; no reasoning text requested or stored. New runner script;
do not edit running scripts in place. Commit this file before the gate; amendments before numbers.

## Not in this task (candidate, unregistered)

Ca0-sample (no sources), crossed with An0, if An0 shows the sources are the engine.
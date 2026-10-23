# Amendment — Luna without reasoning on the fingerprint battery: Responses `effort=none` and Decisions

**Status:** locked 2026-10-23, after the dry build in `runs/model_panel/luna_modes_gate.json`.
No call was made before this lock. Shared envelope: $1.5202 of $10 spent. Basis:
`runs/model_panel/luna_fingerprint_modes_prep.md`, the first article ("Same Weights, Three Ways to
Answer", Oct 9, 2026), `MODEL_PANEL_PLAN.md`, `DESIGN_AUDIT_CHECKLIST.md`.

## Why

The battery has Luna only with reasoning (`effort=medium`). The open models without reasoning
(Qwen3-4B-Instruct, Spark with thinking off) were set against reasoning references. The first article
already established that `gpt-6-luna` does not check two-step rules in one pass: 59% on two-op pairs
with Decisions, and the same with Responses `effort=none` (a difference within 0.10). With reasoning
it scores about 100%. The battery should therefore show this as a drop in the own-example fit rate
when reasoning is off. Luna-none against Luna-medium is the cleanest reasoning pair available: the
same weights and the same request, with only `reasoning.effort` changed.

## Runs

| run | API | request | calls |
|---|---|---|---:|
| LM-none | Responses | the stored Luna redo / QI-1b `input`, byte for byte; only `reasoning.effort` changes, from `medium` to `none`; model, `max_output_tokens` 8192 and the JSON schema unchanged; no temperature | 960 battery + 200 class-B 0/8 filter draws = 1160 |
| LM-dec | Decisions | rule question only, as in the earlier one-pass cells (`life_verify/v1b/luna_cells.py`): the same state text, the catalog as choice criteria, question "Which is the hidden transformation for this epoch?", P = 4 option orderings, argmax of the 4-ordering average | 1160 × 4 = 4640 |

- The communication and signal questions are not asked: the battery scores the named rule only.
- The answer of LM-dec is the argmax rule.
- The reference arm is LM-medium: the existing Luna redo and QI-1b caches. **Dry build:** the
  medium class-B 0/8 draws 2–11 are absent. The Luna redo cache, the QI-1b Luna cache and the
  original Part 0b Luna cache each hold 0 of the 200. The medium arm of the fit and filter tests
  is draws 0–1 only. The readout says so. No medium call is added.
- Costs, recomputed with live calls refused. LM-none is $0.2732: 2,571,372 input tokens from the
  medium caches of these prompts, and 27.62 output tokens per call (the mean of the effort=none
  2-op and 1-op full-seed means). Cap $0.5463. LM-dec is $0.9759, not the $0.50 placeholder. A
  sample of 4,000 Ca Decisions calls separates a heavy third, the rule question, at a mean of
  2,090 input tokens and $0.000209 per cold call; the fingerprint states are 1.006 times the
  An-versus-Ca gate states, and 1,160 prompts × 4 orderings use that unit. Cap $1.9517. The two
  caps sum to $2.498. Remaining envelope $8.4798. The caps fit.
- Own caches, own locks, runtime invariants (expected call count, byte identity of `input` /
  state text at send time, body diff against LM-medium in `reasoning.effort` only for LM-none).

## Measures

- **Fit:** the share of answers whose named rule maps the cell's own example to its output.
  Computed per source cell, over all 22 battery conditions; 40 cells (20 A + 20 B).
- **Composition:** P_e / prefix / neither, per class and condition.
- **Filter selectivity:** P(prefix | A, 0/8) − P(prefix | B, 0/8).
- **Panel fingerprints:** S, L, ally, count, top, filter, each also conditional on answers in
  {P_e, prefix}, with that share beside it.
- **U1 and U2**, as in the panel plan.

## Predictions (locked)

- **LF1 (reasoning makes Luna check):** fit(LM-medium) > fit(LM-none). Primary test: a one-sided
  cell-paired sign-flip over the 40 cells on per-cell fit rates, α = 0.05. Fisher on calls goes
  beside it.
- **LF2 (Decisions and reasoning-off check alike):** the cluster-bootstrap 95% interval of
  fit(LM-none) − fit(LM-dec) lies within ±0.10. The 2000 draws resample the 40 cells, numpy
  Generator seed 0. Basis: the first article's registered control, which required the two APIs with
  reasoning off to differ by less than 0.10 on two-op pairs. It held, at +0.01 [−0.06, +0.08].
- **U1 and U2** for LM-none and LM-dec, counted in the panel as for every model.
- **Not predicted:** the social fingerprints (S, L, ally, count, top) of LM-none and LM-dec. They are
  descriptive. The first article saw reasoning-off Luna weigh neighbours more and drop its own
  answer more easily, but that was in a different world and was not measured on this battery.

## Pre-stated readings

- **LF1 passes:** the battery reproduces the first article's checking gap on Luna. Fingerprints of
  reasoning-off models are then read through their fit rate. A step or ally effect means little in a
  model whose answers mostly fail its own example.
- **LF1 fails:** Luna without reasoning checks its single example about as well as with it. The
  checking gap in the first article was specific to two-op pair choice, and the battery's
  one-example check is easier. The readout says so, and the open-model gaps are reread in that
  light.
- **LF2 passes:** Decisions and reasoning-off Responses check equally on this battery, as on pairs.
  LM-dec is then a valid one-pass reference for the Unsloth decision heads.
- **LF2 fails:** the two reasoning-off modes differ here, and the Unsloth comparison must name which
  one it targets.
- **Social fingerprints:** if LM-none keeps Luna's majority step on answers in {P_e, prefix}, the step
  is a property of the model, not of reasoning. If the step disappears, it belongs to reasoning
  in Luna. Both readings are descriptive.
- **If the design is the cause:** LM-dec does not see the JSON instruction or the keyed catalog in
  the same form, so it is a different presentation by construction. LF2 compares checking, not
  social response, and every LM-dec row says it is the Decisions format. A truncation at 8192
  tokens is not possible without reasoning; parse failures are counted per cell, and cells above 5%
  are reported but not used.

## Design audit

1. **Fidelity.** LM-none: all 1160 payloads have `input` byte-identical to the stored prompt, and
   the only field that differs from the medium body is `reasoning.effort` (`medium` to `none`).
   Draw and temperature are not in the body. LM-dec: on all 1160, the state is the Responses
   input cut at `\n\nRule catalog (choose by key):\n`, and the prompt starts with that state.
   The first battery prompt is 5352 characters of input and 1770 of state. The question is
   `Which is the hidden transformation for this epoch?`. The criteria are the 101 bare catalog
   descriptions. Communication and signal are not asked. Their strings, recorded and unused, are
   `Should this cell publish a message this generation?` with criteria `stay silent this
   generation` / `publish one message this generation`, and `If this cell publishes, which signal
   does the message carry?` with criteria `signal 0` through `signal 7`.
2. **Coverage.** The battery conditions only. Fit is defined for every answer.
3. **Controls.** LM-medium is the existing control on the same prompts. LM-none is the control for
   LM-dec.
4. **Observability.** The cell sees its prompt only. Fit is a function of the named rule and the
   cell's own example.
5. **Gate consistency.** These ran together on 2026-10-23, with live calls refused
   (`runs/gate_panel_luna_modes.py`, `runs/model_panel/luna_modes_gate.json`):
   - byte identity, 1160/1160;
   - the body diff, effort only;
   - the LM-dec state identity, 1160/1160;
   - the medium filter-draw check, absent, so draws 0–1 only;
   - the cost recomputation against the caps;
   - the remaining envelope, caps sum $2.498 inside $8.4798.
6. **Statistical unit.** The source cell, with paired comparisons over the same 40 cells.
7. **Pre-stated readings.** Above.

## Power

Filled from the same dry build. LM-medium fit on the 960 battery answers is 951/960 = 0.991, with
0 failures. Per cell the parsed count is 26 on class A and 22 on class B. Each figure is 2000
simulations.

| check | power |
|---|---:|
| LF1, none fit at 0.6 | 1.000 |
| LF1, none fit at 0.8 | 1.000 |
| LF2, interval inside ±0.10 when the true difference is 0 | 1.000 |

None is below 0.8. The design is unchanged.
# Addendum — R1-fit, own-example fit on the Spark pair

**Status:** locked 2026-10-23, before any W1-spark-low call. Written after the Qwen-pair
answer composition was seen, and before any Spark-low data. W1-spark-low has no cache and
no `run.ok`.

The locked R1 is unchanged. R1 still scores the absolute class-B 0/8 prefix rate. This
addendum adds a separate prediction.

## Prediction

**R1-fit.** On the fingerprint battery (classes A and B, the 22 Part 0b conditions; 40
source cells × 22 × 2 draws), the share of parsed answers whose named rule maps the cell's
own example to its output is higher for W1-spark-low than for W1-spark-none.

A named rule fits when the catalog function with that description maps every private
example in the prompt. Answers equal to P_e or the prefix are checked the same way. Parse
failures and truncations are left out of the rate and out of the Fisher table, and their
counts are reported. QI-1b rows (7/1 and 4E) and the class-B 0/8 draws 2–11 are outside
this prediction.

## Test

The unit is the source cell. A cell is the class together with replicate, world, round and
cell, so the 20 class-A cells and the 20 class-B cells are 40 cells.

Primary: one-sided cell-paired sign-flip on the 40 per-cell fit rates, W1-spark-low minus
W1-spark-none. The test is the exact upper tail of the sum of those differences under
random signs (`sign_flip` in `runs/run_life_dr_tipping_part_h.py`). Zeros are dropped. If
every difference is zero, the p-value is 1. α = 0.05. R1-fit passes only when this p-value
is below 0.05. A cell with no parsed answer on either run is dropped, and the readout says
how many cells remain.

Beside it, not the verdict: one-sided Fisher on parsed calls, `fisher_greater` with the
low run first (`runs/run_life_dr_controls_part0b.py`). Calls inside a cell are repeated
measures, so Fisher does not decide.

## Pre-stated readings

- **Pass:** at effort low, Spark names a rule that fits the cell's own example more often
  than with thinking off. The gain is in that fit rate. It does not rewrite R1.
- **Fail:** the sign-flip does not show a higher fit rate. Say that. Do not read the fail
  as "reasoning does not matter."
- **If the design is the cause:** a higher fit rate can be more P_e, more prefix, or more
  third rules that happen to fit the one example. The readout gives those three shares. If
  W1-spark-low leaves many answers unparsed, the comparison is among parsed answers only,
  and the unparsed count is part of the result. The pilot rule is unchanged: more than one
  parse failure or truncation in the 20 pilot calls stops the run before the battery.

## Design audit

1. **Fidelity.** No new prompt. Both runs use the locked wave-1 battery. W1-spark-low
   differs from W1-spark-none only in `chat_template_kwargs`, as locked in
   `ADDENDUM_PANEL_WAVE1_SPARK_LOW.md`. The example text is the private-example block
   already in those prompts.
2. **Coverage.** The rate is read on every Part 0b battery answer, classes A and B, all 22
   conditions. Draws 2–11 and the QI-1b rows are outside the rate, and the locked text says
   so.
3. **Controls.** W1-spark-none is the same weights, prompts and decoding with thinking off.
   The contrast is effort low against that baseline.
4. **Observability.** The cell sees the private example. The fit is computed from the named
   rule and that example. The prediction does not use a quantity the prompt hides.
5. **Gate.** Before this lock: `runs/model_panel/W1-spark-low/` contains `queue.log`,
   `queue.pid` and `offline_render.json` only. No `run.ok`, no `run.aborted`, no `cache`.
   The waiter, after QX-1 and after the after-panel chain has exited, reads this file's
   header and exits if it is not locked. `run_life_panel_wave1.py` refuses
   `--run W1-spark-low` unless this header and the Spark-low addendum header are locked.
   No call was made for this check.
6. **Statistical unit.** The source cell, 40 cells. The sign-flip is the primary test.
   Fisher on calls is beside it.
7. **Pre-stated readings.** Written above, including the case where unparsed answers or the
   kind of fitting rule, rather than reasoning, would carry the result.

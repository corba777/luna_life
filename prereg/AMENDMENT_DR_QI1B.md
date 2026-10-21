# Amendment — QI-1b: one supporting line, and P_e count without the prefix (Luna, Qwen, gpt-oss-120b)

**Status:** locked before any QI-1b call. Re-locked so classification uses the hull of the Wilson
95% interval and the cluster-bootstrap 95% interval. Approved by Artem. Qwen and gpt-oss calls are
local. The Luna part is 80 calls. The dry-build cost is $0.0383, inside the shared Luna envelope
(cumulative spend so far $1.49 of $10; below $10 no new go is needed). No call was made before this
re-lock.
Parents: `runs/life_dr_qwen/qi1/readout.md` (with its 8/0 addendum),
`runs/life_dr_tipping/redo/redo_readout.md`, `AMENDMENT_DR_GPTOSS_QI1.md`, `DESIGN_AUDIT_CHECKLIST.md`.

## Why

Class-A adoption of P_e on the QI-1 battery (out of 40):

| P_e / prefix | 2/6 | 3/5 | 4/4 | 5/3 | 6/2 | 8/0 | 1 P_e + 7 empty |
|---|---:|---:|---:|---:|---:|---:|---:|
| Luna (redo) | 0 | 2 | 5 | 32 | 39 | 40 | 34 |
| Qwen | 0 | 1 | 8 | 8 | 9 | 26 | 3 |

Luna follows the share of visible lines: there is a step at a strict majority, and one P_e line among
empty slots (share 1) is enough. Qwen stays near 0.2 as long as any prefix line is present, even at
6/2. With no prefix line, its adoption rises with the number of P_e lines: 3/40 with one line, 26/40
with eight. Two rules fit Qwen:

- **Ally rule:** any line supporting the cell's own (example-consistent) rule holds it. This is
  analogous to the ally effect in Asch's conformity studies, where one dissenter largely removes
  conformity.
- **Smooth rule:** adoption rises gradually with the P_e share or count, and 6/2 → 8/0 is part of a
  steep but continuous curve.

The battery has no condition between 6/2 and 8/0, and none with several P_e lines and empty slots.
QI-1b adds one of each.

## Conditions

Class A only. The same 20 source cells and 2 draws per cell as QI-1, built by the same builder as the
QI-1 class-A conditions: positions from the redo hash, signals as that builder assigns them, and empty
slots rendered exactly as in the `1 P_e + 7 empty` condition.

- **7/1:** 7 P_e lines and 1 prefix line.
- **4E:** 4 P_e lines and 4 empty slots.

2 conditions × 20 cells × 2 draws = 80 prompts per model. The models are:

- **Luna**, on the redo settings.
- **Qwen**, on the Stage 1 settings.
- **gpt-oss-120b**, on the settings of `AMENDMENT_DR_GPTOSS_QI1.md`. Its part runs only if that
  amendment's pilot passed and it was locked; otherwise it is reported as "not run".

Each model has its own cache under its run directory. Queue:

- **Qwen:** right after QI-T, on the same server, before the switch to gpt-oss.
- **gpt-oss:** right after its QI-1 battery, on the same server.
- **Luna:** any time after the lock. It is an API job with its own lock and does not touch the local
  server.

## Reference values (from the counts above; fixed now)

Qwen:

- a_ally = P(6/2) = 9/40 = 0.225: the 7/1 value expected under the ally rule (prefix present).
- a_smooth = (P(6/2) + P(8/0)) / 2 = (0.225 + 0.650) / 2 = 0.4375: the 7/1 value expected if
  adoption is linear in share between 6/2 (share 0.75) and 8/0 (share 1.0).
- c_count = P(1E) + (3/7)·(P(8/0) − P(1E)) = 0.075 + (3/7)·0.575 = 0.3214: the 4E value expected if,
  with no prefix line, adoption is linear in the number of P_e lines between 1 and 8.
- c_floor = P(1E) = 3/40 = 0.075: the 4E value expected if only a full P_e inbox moves Qwen.

Luna:

- l_71 = P(6/2) = 39/40 = 0.975: the 7/1 value under Luna's share rule (share 0.875, above the
  step).
- l_4E = P(1E) = 34/40 = 0.850: the 4E value under the share rule (share 1, as in 1E).

## Statistics (fixed now)

The unit is the source cell (20 cells, both draws pooled within a cell). Each rate gets a 95% cluster
bootstrap interval over cells, 2000 draws, `numpy` Generator seed 0. Wilson intervals are reported
beside it.

**Classification interval (re-lock revision, before any call):** the hull of the Wilson 95% interval
and the cluster-bootstrap 95% interval, from the lower of the two lower bounds to the higher of the two
upper bounds. Reason: at a rate of 0 or 1 within a condition the percentile bootstrap collapses to a
point, for example [1, 1] at 40/40. Such an interval excludes a reference of 0.975 that is true by
construction. The first lock used the bootstrap interval alone, and its dry-build power for B3 (0.6655)
came from that collapse: 0.975^40 ≈ 0.36. The hull is never degenerate and is never narrower than
either interval.

A rate is classified against two reference values:

- It matches reference X if its interval contains X and excludes the other reference.
- It is **undecided** if the interval contains both.
- It is **neither** if the interval excludes both.

## Predictions (locked)

- **B1 (Qwen, ally):** Qwen P(7/1) matches a_ally = 0.225 against a_smooth = 0.4375.
- **B2 (Qwen, count without the prefix):** Qwen P(4E) matches c_count = 0.3214 against
  c_floor = 0.075.
- **B3 (Luna, share rule):** Luna P(7/1) has an interval containing l_71 = 0.975, and Luna P(4E) has
  an interval excluding c_count = 0.3214. Both must hold.
- **gpt-oss (descriptive, not scored):** both rates classified against the Qwen references and
  against the Luna references, and reported beside the S and L classes of its QI-1 battery.

## Pre-stated readings

- **B1 passes:** for Qwen, one supporting line is enough to hold a cell's evidence-consistent rule.
  Qwen's resistance is the ally effect, not a weak response to share. B1 is undecided or "smooth":
  Qwen's 6/2 → 8/0 jump is part of a steep curve in share, and "ally" is not claimed.
- **B2 passes:** with no opposing line, Qwen counts P_e lines. Its rule then has two factors: support
  for its own rule blocks it, and P_e count drives it when nothing blocks. B2 matches c_floor: only
  near-unanimity moves Qwen, and the 1E → 8/0 rise is not gradual.
- **B3 passes:** Luna's response is a share rule that extends to these new conditions. B3 fails:
  Luna's threshold is not a function of share alone, and the redo curve is reread with that in mind.
- **Across models:** if Qwen is "ally" and Luna is "share", the two models differ in what a single
  line does. For Luna one line of the newcomer is decisive (1E). For Qwen one line for the incumbent
  is decisive (7/1). In the package this is the clearest form of the micro difference, and it is
  stated as two measured response rules, not as a trait of either model.
- **If the design is the cause:** 7/1 places a single prefix line by the redo hash, so its position
  varies. If B1 passes, the readout breaks 7/1 adoption down by that line's slot (1–8). If the effect
  sits only at one slot, such as the first line, that is an order effect, and it is reported as one.
  Parse failures and truncations are counted per cell. If they exceed 5% in a condition, it is
  reported and not classified.

## Design audit

1. **Fidelity.** Prompts are built by the QI-1 builder (`inbox_block` and `replace_inbox`), and the
   redo hash (`redo-pe`, `follow_rule="keep"`) chooses which filled slots say P_e. Outside the inbox
   block, every 7/1 and 4E prompt is byte-identical to the QI-1 prompt of the same cell and draw.
   Asserted: 80 of 80. The inbox has 8 slots. Asserted counts: 7/1 is 7 P_e lines and 1 prefix line
   on all 20 cells; 4E is 4 P_e lines and 4 empty slots on all 20 cells. No other say appears.
   Every empty line is `  {slot}. empty`, and the bytes after the slot number are `empty`, the same
   bytes as every empty line of the rebuilt 1E condition. The single prefix line in 7/1 falls in
   slots 1, 2, 3, 5, 6, 7 and 8 (counts 1, 7, 3, 1, 2, 3, 3). Slot 4 is unused. The position varies.
2. **Coverage.** The references come from conditions on both sides of each new one: 6/2 and 8/0
   around 7/1, and 1E and 8/0 around 4E. Nothing is extrapolated beyond the measured range.
3. **Controls.** 6/2, 8/0 and 1E are already measured on the same cells and the same builder, and
   they are not re-run. The Luna and Qwen QI-1 caches still serve those prompts. The sample is the
   20 class-A cells at 6/2, draw 0. Their prompt sha256 is
   `201dc5f7ad40f78f24b5404217967bdf18ec553f25937c829dfd1546cdd6588a`. Those 20, and the same cells
   at 8/0 and at 1E, both draws (120 prompts), are present in the Luna Part 0b cache and in the
   Qwen QI-1 cache.
4. **Observability.** The cell sees only the lines, empty slots, example and memory line. The ally
   and count rules are stated in terms of visible lines only.
5. **Gate consistency.** Pre-lock gates, run together with live calls refused:
   - byte identity outside the inbox (80 prompts);
   - inbox counts;
   - empty-slot rendering;
   - builder-unchanged hash check;
   - Luna cost estimate below the remaining envelope. The mean of the 440 class-A redo calls is
     $0.000478, so 80 calls are $0.0383. The remaining envelope is $8.51. This is below it.
   - power, recorded below. All six gates passed with live calls refused. The re-lock recomputed
     the power under the hull. The other five gates are the same build.

   Launch gates per model, checked by each runner at start: lock free; for the local models, no other
   server job.
6. **Statistical unit.** The source cell, with the bootstrap over 20 cells.
7. **Pre-stated readings.** Above, including the order-effect reading of 7/1.

## Power

Simulate 20 cells × 2 draws. For B1, set the true rate to a_ally, then to a_smooth. For B2, set it to
c_count, then to c_floor. For B3, use Luna's l_71 and l_4E. Use the per-cell spread of the QI-1
conditions nearest each case (6/2 and 8/0 for 7/1; 1E and 8/0 for 4E). Run 2000 simulations each and
record how often each classification is correct. If any is below 0.8, the readout says so, and B1 or
B2 may come out undecided at this size. The design is not changed after seeing that number unless
this amendment is re-locked.

The spread is the average, across the two nearest conditions, of each cell's deviation from that
condition's mean rate. Cell probabilities are the true rate plus that deviation, scaled by the
largest factor in (0, 1] that keeps every probability inside [0, 1], so the mean stays at the true
rate. The scale is 0.5143 at a_ally, 1 at a_smooth, 0.8867 at c_count, 0.2069 at c_floor, and 1 at
both Luna rates. Each simulation draws Binomial(2, p_i). The classified interval is the hull: Wilson
on the 40 prompts with z = 1.96, and the 95% percentile interval from a 2000-draw cell bootstrap.
The bootstrap index matrix comes from one `numpy` Generator with seed 0 and is shared. The outcome
draws use a separate Generator with seed 0, restarted for each truth. c_count is the exact value
0.32142857. B3 is correct only when the 7/1 interval contains 0.975 and the 4E interval excludes
0.32142857.

| truth | correct classification |
|---|---:|
| B1, a_ally | 0.8195 |
| B1, a_smooth | 0.6875 |
| B2, c_count | 0.9450 |
| B2, c_floor | 0.9900 |
| B3, both clauses | 0.9995 |

B1 at a_smooth is below 0.8. At a_smooth, 611 of the 2000 intervals contain both references, so B1
may come out undecided. B3 contains 0.975 in 1999 of 2000 simulations, and the 4E interval excludes
0.32142857 in all of them. The readout says so for B1. The design is unchanged.
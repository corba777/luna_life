# Amendment — full Stage 1 runs triggered by U1 failures

**Status:** locked 2026-10-23, after the dry build. Approved by Artem on 2026-10-23: LM-none in `all` and lattice, LM-dec in
lattice only, and W1-oss20 and W1-spark-none in `all` and lattice. The Luna arms run inside the $20
envelope; the local arms are pre-approved. No call was made before this lock. The dry-build values
were computed from existing data, with live calls refused. Basis: `MODEL_PANEL_PLAN.md` (the U1 trigger),
`runs/model_panel/full_runs_prep.md` (runners, costs, references), `runs/model_panel/full_runs_gate.json`,
the fingerprint readouts, and `DESIGN_AUDIT_CHECKLIST.md`.

## Why

Four panel arms fail U1 on the battery: a class-B cell, whose own example rules the prefix out, still
names the prefix under 8 prefix lines.

| arm | class-B 0/8 prefix | own-example fit, battery |
|---|---:|---:|
| LM-none | 24/40 | 0.80 |
| LM-dec | 34/40 | 0.83 |
| W1-oss20 | 4/40 | high (class B: 27/28 of third rules fit) |
| W1-spark-none | 7/40 | low |

The locked plan runs such models in the population. The question is whether the micro failure
reaches the macro level. On the lattice, Luna with reasoning wins through its witnesses: the class-B
cells refuse the prefix and pass P_e on. That gives a mean x over rounds 10–20 of 0.86 and 0.97, with
25/25 class-B cells on P_e at round 20. A witness that yields to its neighbours cannot do this.

## Runs

The grid is world 1, 2 replicates, 20 rounds and 100 cells, with no scripted sources. The prompt
text comes from the Qwen Stage 1 builder, and `all` and lattice differ only in the inbox block and
the slot-count sentence. All seven arms are as in `full_runs_prep.md`.

| arm | topology | agent |
|---|---|---|
| LM-none-all, LM-none-lattice | `all`, lattice | Luna Responses, `effort=none`, max_output_tokens 8192 |
| LM-dec-lattice | lattice | Luna Decisions, P=4 × 3 questions, decode argmax (the earlier one-pass cell, `luna_cells.py`) |
| W1-oss20-all, W1-oss20-lattice | `all`, lattice | gpt-oss-20b, the wave-1 serving and decoding |
| W1-spark-none-all, W1-spark-none-lattice | `all`, lattice | Spark-X2.6-4B, thinking off, the wave-1 serving and decoding |

LM-dec in `all` is recorded as "triggered, not run: cost".

**Order.** The Luna arms run now, in parallel with the local chain, since they do not use the GPU:
LM-none-lattice, LM-none-all, then LM-dec-lattice. The local arms queue after W1-spark-low and before
moore: W1-spark-none (about 1 h), then W1-oss20 (about 11.5 h).

**Spend.** The cap per Luna arm is twice its estimate, and the shared envelope stops at $20. The
runner computes spend from the returned token counts at list rates (`usd_from_usage`). A cap read
from a report field would miss the forced-publisher Decisions runs, whose reports carry
`usd_list_rate = 0`.

**Dry build, stored row (2026-10-23, live calls refused).**
`runs/life_distributed/cache_DC/baedbc9ce34a6711ad5a891922b298a9cfb64d28e389507788c5643010ba1b0c.json`
has `input_tokens` 2106, `output_tokens` 0, and cached tokens 0. `usd_from_usage` on that usage is
$0.0002106. The row has no `usd_list_rate` field.

## Measures (per replicate)

- **x(g):** the share of the 100 cells holding P_e. Plus mean x over rounds 10–20.
- **Class B at round 20:** cells on P_e, cells on the prefix, and cells on other rules, out of 25.
- **Class-B h_out and h_in:** the Stage 1 definitions, transitions into rounds 2–20.
- **Own-example fit:** the share of all cell decisions in rounds 1–20 whose rule fits the cell's own
  example.

## Reference values and derived thresholds (fixed now)

From `full_runs_prep.md`:

- Luna medium lattice: mean x(10–20) 0.86 (r1) and 0.97 (r2). Class B on P_e at g20: 25/25, 25/25.
- Luna medium `all`: mean x(10–20) 0.232 and 0.307.
- **Witness plateau:** 0.25, the share of x that class-B cells alone can supply.
- **Replicate noise:** the absolute difference between Luna's two replicates, 0.11 on the lattice and
  0.075 in `all`.

Derived:

- **t_lat** = min(Luna lattice) − lattice noise = 0.86 − 0.11 = **0.75**.
- **t_all** = min(Luna `all`) − `all` noise = 0.232 − 0.075 = **0.157**.
- **k_B = 6.** It is 1 + the 95th percentile of Binomial(25, w), where w = 0.088 is the Wilson 95%
  upper bound of Luna medium's battery rate (0/40). The computed Wilson upper bound is 0.08762,
  which rounds to 0.088. The 95th percentile at w = 0.088 is 5 (cdf 0.981; the cdf at 4 is 0.937).
  This is the most class-B prefix holders a population as resistant as Luna medium would plausibly
  show.

## Predictions (locked)

Each prediction must hold in **both** replicates. There are only 2 replicates, so there is no
interval.

- **F1 (witnesses yield, LM-none and LM-dec, lattice):** class-B cells holding the prefix at g20 ≥ k_B.
- **F2 (the minority loses the lattice, LM-none and LM-dec):** mean x(10–20) < t_lat.
- **F3 (LM-none, `all`):** mean x(10–20) < t_all. Basis: conformist witnesses lower the plateau below
  Luna medium's.
- **F4 (no spread without checking, W1-spark-none, both topologies):** mean x(10–20) < 0.25, the
  witness plateau. Basis: low own-example fit, and class-B adoption of P_e of 0.2–0.35 on the
  battery.
- **W1-oss20:** no locked prediction. Its witnesses resist (selectivity 0.90), and its response to a
  single line is intermediate. It is reported descriptively against the Luna references and t_lat.

## Pre-stated readings

- **F1 and F2 pass:** a micro failure measured on the battery (yielding against one's own evidence)
  removes the minority's veto in the population. The lattice win of Luna medium needs its reasoning.
  This is the clearest micro → macro link in the project.
- **F1 passes and F2 fails:** witnesses yield, yet the population still reaches P_e. Spread then does
  not need resistant witnesses. The h_in/h_out pattern says how.
- **F1 fails:** on the lattice the witnesses hold despite the battery rate. Eight prefix lines at once
  is a harsher condition than a lattice neighbourhood. The readout then compares the class-B inboxes
  seen on the lattice with the battery's 0/8.
- **F3:** pass or fail, read with F1.
- **F4 fails:** a population of non-checkers still lifts x above the witness plateau. This is
  reported, together with the fit rate, as spread without checking.
- **If the design is the cause:** LM-dec answers in a different format by construction (Decisions,
  P=4), so it is compared on outcomes, not on prompts. Parse or invalid fallbacks are counted per
  round. If more than 2% of decisions in a replicate fail, its predictions are reported with that
  caveat.

## Design audit

1. **Fidelity.** The prompt text is the Qwen Stage 1 builder. `effort` is the only change between
   none and medium. LM-dec state equals the Stage 1 prompt with the catalog block removed, with the
   questions quoted. Gate: `runs/gate_panel_full_runs.py`, rerun 2026-10-23 with this file's status
   line still `draft for lock`. The same gate passed again after this status line was set to locked.
   The machine result is `runs/model_panel/full_runs_gate.json`.
2. **Coverage.** World 1 only, 20 rounds, and the same grid as the references.
3. **Controls.** Luna medium and Qwen-Thinking in the same world and grid are the existing references.
   There is no Qwen-Thinking lattice yet; moore is queued.
4. **Observability.** Cells see only their prompt. The class-B list for world 1 is fixed.
5. **Gate consistency.** These run together with live calls refused:
   - prompt identity;
   - the LM-dec layout;
   - the local launch argv;
   - the token-based spend on the stored Decisions row above, $0.0002106;
   - the envelope after the estimates: $2.2010 already spent + $2.50 (LM-none) + $4.62
     (LM-dec lattice) = **$9.32 of $20**. With no Decisions cache hits the lattice term is $6.16,
     and the same sum is **$10.86 of $20**. Both sit inside the envelope.

   Launch gates (lock free, no other GPU job) apply to the local arms.
6. **Statistical unit.** The replicate. Two replicates per arm, and each prediction must hold in both.
   This is weak, and stated.
7. **Pre-stated readings.** Above.
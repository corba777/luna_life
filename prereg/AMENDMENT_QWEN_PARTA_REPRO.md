# Reproducibility check of the stored Qwen Part A battery (SGLang)

**Status.** Written before any call of this check. **Nothing in the paper changes until Artem decides on
the readout.** Artem approved it in two steps on 2026-11-11:

1. The plan, with one change: a 99% interval per measure, Bonferroni over five.
2. Three further changes, made before the go:
   - the standard-mode canary uses the locked rule (a) form against HF;
   - the 36,864 stored launch is compared with the 40,960 launch, and the diff is recorded here;
   - 6 run-side draws per cell on the S88 and E8 conditions.

The first waiter (`queue_qwen_parta_repro.sh`, manifest `2fceec05…`) was stopped at its go wait, with no
call made, and replaced by `queue_qwen_parta_repro_v2.sh`. The v2 waiter was also stopped at its go wait, with
no call made, only to remove two private commit references from this file; it is replaced by
`queue_qwen_parta_repro_v3.sh`. The design is unchanged.

## Why

v23b's α = 0 arm (witness direction, SGLang deterministic mode) did not match the stored battery:

- Gate (ii) on the lattice: +0.056, 95% interval [+0.014, +0.101].
- Descriptives: S88 0.25 vs stored 0.025; E8 0.20 vs stored 0.025.

The patched α = 0 launches were bit-identical to the unpatched server on the canary, so the steering code
is not the cause. This check asks two questions:

- Does the stored battery reproduce on its own engine configuration?
- Does deterministic mode shift it?

## Engine

- SGLang 0.5.18, image `sha256:223b675f…`, **unpatched** (no `jev_steer` mount or environment).
  - The image is labelled `lmsysorg/sglang:v0.5.18`, build commit `71de97b2…`.
  - `importlib.metadata` inside the image reports `sglang 0.5.18`.
  - The witness gate requires zero witness files.
  - The argv equals the battery's recorded 40,960 launch (`runs/contagion/local_qwen/resume_40960_launch.json`),
    plus `--enable-deterministic-inference` in the deterministic arm.
- Qwen3-4B-Thinking-2507, revision `768f209d…`.
- The battery request body (`run_life_panel_wave1.request_body`, `W1-r1-think`): temperature 0.6, top-k 20,
  top-p 0.95, `max_tokens` 32,768, strict json_schema, reasoning parser qwen3, no seed.
- Concurrency 64, memory fraction 0.6.
- Context 40,960.

### The stored battery's two launches (checked in the dry check, `stored_launch_diff`)

The stored battery ran in two launches:

- 2,756 answers in the **36,864** launch, started 2026-10-27 08:28:17 UTC (container time).
- 204 answers in the **40,960** resume launch, started 2026-10-28 05:42:45 UTC.

The serve log `runs/model_panel/W1-r1-think/sglang.log` gives each launch's chat requests and its full
`ServerArgs` dump:

| launch | chat requests served |
|---|---|
| 36,864 | 2,960: the 2,756 answers plus the 204 rejected for context length |
| 40,960 | 460: the 204 resumed calls plus the 256-call sampler gate |

**ServerArgs (478 fields).** They are equal except:

| field | 36,864 launch | 40,960 launch |
|---|---|---|
| `context_length` | 36864 | 40960 |
| `random_seed` | 224912764 | 541543088 |

`random_seed` is drawn by SGLang at each launch when none is given; neither launch set it, and neither does
this check. Both launches had `enable_deterministic_inference=False`, flashinfer attention and sampling
backends, `disable_radix_cache=False`, `chunked_prefill_size` 8192 and `schedule_policy` fcfs.

**Docker argv.**

- The 36,864 launch has no recorded argv file. It was started by `run_life_panel_wave1.launch_argv`, whose
  code (with `request_body` and the `W1-r1-think` spec) is unchanged since its commit of 2026-10-24.
  - The only later change is the process check and `--guard-check`, committed on 2026-11-10.
- Rebuilt with that code at 36,864, the argv differs from the recorded 40,960 argv in exactly one element:
  index 34, `--context-length` 36864 vs 40960.
- So the image (`223b675f…`), mounts, environment, model, revision, memory fraction, concurrency and
  parser are the same.
- Startup preambles in the serve log (image licence banner and launcher warnings) are identical for the
  two launches.

Context length limits only admission. No stored call was truncated.

## Arms (in this order; one launch each; a launch that dies is resumed once, keeping calls on file)

1. **standard:** no seed, as the battery.
2. **deterministic:** `--enable-deterministic-inference`.
   - Seed per call: `int(sha256("repro-parta|<id>|<draw>")[:8], 16) & 0x7FFFFFFF`.
   - This is not the witness-direction seed.

**Canary gate** (before any call; the v23 references are reused after a sha256 check):

| mode | rule | v23 values |
|---|---|---|
| deterministic | bit-identical to the v23 unpatched deterministic reference (`3766467e…`) | — |
| standard | locked rule (a) form against HF: mean\|SG_std − HF(0)\| ≤ 1.5 × gap0_std + 0.005, where gap0_std = mean\|v23 standard reference (`02bbabee…`) − HF(0)\| | HF(0) from `hf.npz` (`25926bb1…`); gap0_std = 0.02074, so the limit is **0.03610** |

In standard mode, bit-identity to the v23 reference is reported beside the gate, descriptive only. A failed
witness or canary gate stops the queue.

## Prompts and draws

The stored battery's own prompts, with ids `A|<condition>|<cell>`. The stored draw indices are reused; on
the four S88 and E8 conditions, new indices follow the stored ones.

| block | conditions | draws per cell (run side) | calls per arm |
|---|---|---:|---:|
| lattice adopt, k ≥ 1 (gate (ii)), except k1m0 and k1m7 | 16 | 2 | 640 |
| lattice adopt k1m0, k1m7 (E8; also in the lattice measure) | 2 | **6** (stored 2) | 240 |
| `all` adopt 0.40 / 0.60 (S88) | 2 | **6** (stored 2) | 240 |
| `all` adopt 0.10 / 0.20 / 0.30 (M88) | 3 | 6 | 360 |
| `all` abandon 0.30 (R88) | 1 | 6 | 120 |
| **total** | | | **1,600** (3,200 for both arms) |

- The stored side is unchanged; S88 and E8 have 40 stored answers per condition.
- The extra run draws are draw indices 2–5 on the four conditions: 320 calls per arm.
- All other measures have the stored battery's n on the run side.

## Outcome and measures

**Outcome.** As in the battery (`readout_contagion_part_ab.load_answers`):

- adopt = the answer is P_e;
- abandon = the answer is the prefix;
- a truncated or unparsed answer counts 0.

**Measures.** The unit is the cell (20 cells). Per cell, each condition's rate is the mean over that
condition's draws in that cell.

- **lattice:** mean over the 18 lattice conditions of P(adopt). Each condition weighs the same whatever its
  draw count. This is gate (ii)'s measure, which the dry check reproduces exactly.
- **S88:** P(adopt | 0.60) − P(adopt | 0.40).
- **E8:** P(adopt | k1m0) − P(adopt | k1m7).
- **M88:** mean of P(adopt | 0.10, 0.20, 0.30).
- **R88:** P(abandon | 0.30).

## Rule (locked)

**Primary rule.**

- Per arm and measure, take the per-cell difference d_c = run_c − stored_c.
- Value = mean over cells.
- **99% percentile cell bootstrap:** 2,000 resamples of the 20 cells, numpy `default_rng(0)`; both sides
  are resampled together by cell.
- A measure **passes** if the interval contains 0.
- An arm **reproduces** the battery if all five measures pass (Bonferroni over five).

**Beside, descriptive only.** Whether the stored value lies inside the run's own battery interval: the
hull, Wilson ∪ 95% cell bootstrap, `hull_rate` / `hull_diff`.

- S88 and E8 use all run draws.
- The pooled lattice hull uses only the run's stored-index draws (2 per cell). Otherwise the extra k1m0 and
  k1m7 draws would weigh those two conditions three times as much in the run's pool as in the stored value:
  in simulation that unequal weighting pushed the beside false alarm on the lattice to 0.18.

### Calibration (dry check, `runs/contagion/qwen_parta_repro_dry_check.json`)

Both sides were simulated from the stored per-(condition, cell) rates: the run side with the run's n
(including the 6 draws above), the stored side with the stored n. The earlier design (2 run draws on the
four conditions) is shown beside.

**Null (1,000 simulations).**

| | this design | earlier design |
|---|---:|---:|
| family-wise false alarm | **0.062** | 0.049 |
| lattice | 0.030 | 0.024 |
| R88 | 0.033 | 0.025 |
| S88 / E8 / M88 | 0.000 | 0.000 |
| beside rule, per measure | 0.000–0.029 | 0–0.03 |

- Monte Carlo SE of the family rate is about 0.008.
- The 20-cell percentile bootstrap under-covers on the lattice and R88: about 3% false alarm each against
  a nominal 1%.
- S88, E8 and M88 sit near 0 because most of their stored cells are 0/2 or 0/6, so the null spread there is
  understated.
- The family rate is therefore about 5–6%, not exactly 5%.

**Power (300 simulations; probability the rule flags the shift).**

| shift | 99% rule | beside rule | earlier design: 99% / beside |
|---|---:|---:|---|
| lattice +0.056 (the size of the v23b gate (ii) shift) | 0.96 | 0.88 | 0.97 / 0.91 |
| S88 +0.20 | **0.91** | 0.94 | 0.60 / 0.44 |
| S88 +0.10 | 0.49 | 0.45 | 0.25 / 0.07 |
| E8 +0.175 (v23b's size) | **0.96** | 1.00 | 0.69 / 0.37 |
| M88 +0.05 | 0.86 | 0.97 | 0.84 / 0.97 |
| R88 −0.10 | 0.31 | 0.37 | 0.31 / 0.33 |

R88 still has little power at this n. A pass on R88 (or on S88 for a shift of 0.10) means "no shift of
this size detected", not "the same".

**At 99%, v23b's own lattice difference** (one draw per prompt) has the interval [−0.00001, +0.117]. The
99% rule would therefore pass it by a hair, where gate (ii) at 95% failed it. This check has at least twice
v23b's draws on the lattice.

## Pre-stated readings

| standard | deterministic | reading |
|---|---|---|
| reproduces | reproduces | v23b's gate (ii) failure is sampling noise, not the engine or the mode. |
| reproduces | does not | Deterministic mode shifts the answer distribution. The stored battery stands; v23b's gate (ii) failure reads as a mode effect. |
| does not | either | The stored battery is not reproduced on its own configuration. The paper's Qwen numbers wait for Artem's decision. |

## Budget

3,200 calls. At v23b's measured 38.65 s per call (launches included), that is about **17.2 h per arm**, or
**34.4 GPU-hours** in total. Standard mode was not timed separately.

## Code and queue

| component | file / name |
|---|---|
| runner | `runs/run_qwen_parta_repro.py` (prepare, arm MODE, readout, dry) |
| waiter | `runs/queue_qwen_parta_repro_v3.sh` |
| go file and switch-log phrase | `go_qwen_parta_repro_v3`, `qwen_parta_repro_v3 GO (Artem` |
| output | `runs/contagion/qwen_parta_repro/` |

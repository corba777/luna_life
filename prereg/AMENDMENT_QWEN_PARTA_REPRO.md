# Reproducibility check of the stored Qwen Part A battery (SGLang)

**Status.** Plan approved by Artem on 2026-11-11, with one change: a 99% interval per measure, Bonferroni
over five. Written before any call of this check. **Nothing in the paper changes until Artem decides on the
readout.**

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
  - The witness gate requires zero witness files.
  - The argv equals the battery's recorded launch (`runs/contagion/local_qwen/resume_40960_launch.json`),
    plus `--enable-deterministic-inference` in the deterministic arm.
- Qwen3-4B-Thinking-2507, revision `768f209d…`.
- The battery request body (`run_life_panel_wave1.request_body`, `W1-r1-think`): temperature 0.6, top-k 20,
  top-p 0.95, `max_tokens` 32,768, strict json_schema, reasoning parser qwen3.
- Concurrency 64, memory fraction 0.6.
- Context 40,960.
  - The stored battery ran 2,756 calls at 36,864 and 204 at 40,960.
  - Context length only limits admission; no stored call was truncated.

## Arms (in this order; one launch each; a launch that dies is resumed once, keeping calls on file)

1. **standard:** no seed, as the battery.
2. **deterministic:** `--enable-deterministic-inference`.
   - Seed per call: `int(sha256("repro-parta|<id>|<draw>")[:8], 16) & 0x7FFFFFFF`.
   - This is not the witness-direction seed.

**Canary gate** (before any call; the v23 unpatched references are reused after a sha256 check):

| mode | reference | rule |
|---|---|---|
| deterministic | `3766467e…` | bit-identical |
| standard | `02bbabee…` | mean \|Δ\| ≤ 0.005; bit-identity reported |

A failed witness or canary gate stops the queue.

## Prompts and draws (the stored battery's own prompts; ids `A|<condition>|<cell>`; the stored draw indices)

| block | conditions | draws per cell | calls per arm |
|---|---|---:|---:|
| lattice adopt, k ≥ 1 (gate (ii); includes E8's k1m0, k1m7) | 18 | 2 | 720 |
| `all` adopt 0.10 / 0.20 / 0.30 (M88) | 3 | 6 | 360 |
| `all` adopt 0.40 / 0.60 (S88) | 2 | 2 | 80 |
| `all` abandon 0.30 (R88) | 1 | 6 | 120 |
| **total** | | | **1,280** (2,560 for both arms) |

Each measure has the stored battery's n.

## Outcome and measures

**Outcome.** As in the battery (`readout_contagion_part_ab.load_answers`):

- adopt = the answer is P_e;
- abandon = the answer is the prefix;
- a truncated or unparsed answer counts 0.

**Measures.** The unit is the cell (20 cells).

- **lattice:** mean over the 18 lattice conditions of P(adopt). Gate (ii)'s measure, which the dry check
  reproduces exactly.
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
- An arm **reproduces** the battery if all five measures pass (Bonferroni: family-wise false alarm ≈ 5%).

**Beside, descriptive only.** Whether the stored value lies inside the run's own battery interval: the
hull, Wilson ∪ 95% cell bootstrap, `hull_rate` / `hull_diff`.

### Calibration (dry check, `runs/contagion/qwen_parta_repro_dry_check.json`)

Both sides were simulated from the stored per-(condition, cell) rates with the stored n.

**Null (1,000 simulations).**

- Family-wise false alarm: **0.049**.
- Per measure: lattice 0.024, R88 0.025, S88 / E8 / M88 0.000.
  - The last three are near zero because most of their stored cells are 0/2 or 0/6, so the null spread
    there is understated.
- Beside rule (stored outside the run's hull): 0–3% per measure.

**Power (300 simulations; probability the rule flags the shift).**

| shift | 99% rule | beside rule |
|---|---:|---:|
| lattice +0.056 (the size of the v23b gate (ii) shift) | 0.97 | 0.91 |
| S88 +0.20 | 0.60 | 0.44 |
| S88 +0.10 | 0.25 | 0.07 |
| E8 +0.175 (v23b's size) | 0.69 | 0.37 |
| M88 +0.05 | 0.84 | 0.97 |
| R88 −0.10 | 0.31 | 0.33 |

S88, E8 and R88 have little power at these n. A pass on them means "no shift of this size detected", not
"the same".

**At 99%, v23b's own lattice difference** (one draw per prompt) has the interval [−0.00001, +0.117]. The
99% rule would therefore pass it by a hair, where gate (ii) at 95% failed it. This check has twice v23b's
draws on the lattice.

## Pre-stated readings

| standard | deterministic | reading |
|---|---|---|
| reproduces | reproduces | v23b's gate (ii) failure is sampling noise, not the engine or the mode. |
| reproduces | does not | Deterministic mode shifts the answer distribution. The stored battery stands; v23b's gate (ii) failure reads as a mode effect. |
| does not | either | The stored battery is not reproduced on its own configuration. The paper's Qwen numbers wait for Artem's decision. |

## Budget

2,560 calls. At v23b's measured 38.65 s per call (launches included), that is about **13.7 h per arm**, or
**27.5 GPU-hours** in total. Standard mode was not timed separately.

## Code and queue

| component | file / name |
|---|---|
| runner | `runs/run_qwen_parta_repro.py` (prepare, arm MODE, readout, dry) |
| waiter | `runs/queue_qwen_parta_repro.sh` |
| go file and switch-log phrase | `go_qwen_parta_repro`, `qwen_parta_repro GO (Artem` |
| output | `runs/contagion/qwen_parta_repro/` |

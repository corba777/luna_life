# Witness direction, Stage 1 — aggregate (Qwen3-4B-Thinking-2507, world 1)

Pre-registration: `prereg/AMENDMENT_WITNESS_DIRECTION.md` (locked 2026-11-06), the attention note,
the gate (iii) clarification of 2026-11-09 and the SGLang clarification
`prereg/AMENDMENT_WITNESS_DIRECTION.sglang.md` (accepted 2026-11-10). Stage 1a and the fit ran on
Hugging Face transformers; the timed probe, the blind scale pilot and Stage 1b (5 arms × 580 calls)
ran on SGLang 0.5.18 with a steering model class, deterministic mode (seeded per prompt, the same seed
in every arm). Finished 2026-11-11.

## Result

| Prediction | Value | Holds |
|---|---|---|
| P1 within-condition AUC (one-sided 95 % lower bound) | 0.634 (0.490) | no |
| D1+ adoption(+16) − adoption(0) | −0.033, one-sided bounds [−0.063, −0.006] | no |
| D1− adoption(−16) − adoption(0) | −0.015, upper bound +0.015 | no |
| D2 vs d_rand / vs d_k | −0.015 / −0.022 | no |
| D3 fit(+16) − fit(0) | −0.125 (34/40 vs 39/40), upper bound −0.050 | no |

Pre-stated reading: P1 fails — no linear trace of the decision at the last prompt token beyond the
condition (full out-of-fold probe AUC 0.821 vs inputs-only 0.798). Fidelity gate (ii) failed on the
lattice form (+0.056, 95 % [+0.014, +0.101]; `all` passes): by the locked rule Stage 1b is reported as
"HF-only" — on its own run, with no comparison to the stored battery claimed. Gate (iii) passed (580/580 valid, 0 truncated).

## Files

- `readout.json` / `readout.md` — every locked quantity, per-arm measures, L*_f and fold cosines,
  descriptive S88 / E8 beside fidelity, the engine block.
- `fidelity.json` — gates (ii) and (iii) on the α = 0 arm.
- `probe_deterministic.json`, `mode.json` — timed probe and mode rule; `pilot_readout.json`,
  `alpha_max.json` — the blind scale pilot (α_max = 16).
- `gpu_checks.json` — CUDA graphs on vs off, prefix cache (disabled in deterministic mode).
- `launches_summary.json` — per launch: vector, layer, witness gate, canary gate (a, b, c).

Per-call texts, activations and the fit are in the recheck package (not mirrored here).

# Witness direction — Stage 1 readout

- P1 within-condition AUC 0.634, one-sided lower 0.490 -> fails; full OOF 0.821; inputs-only 0.798
- L*_f {'1': 5, '2': 32, '3': 5, '4': 5, '5': 5}; alpha_max 16
- D1+ -0.033 (lower -0.063) -> False
- D1- -0.015 (upper +0.015) -> False
- D2 vs rand -0.015 (lower -0.039); vs k -0.022 (lower -0.054) -> False
- D3 fit(+) - fit(0) -0.125 (upper -0.050) -> False
- fidelity: (iii) 580/580 closed-and-stopped calls valid, 0 EOS in reasoning, 0 truncated of 580 (non-adoption, non-fit; not a gate failure) -> pass True; (ii) pass False

## Arms

- alpha0: adoption 0.1537037037037037, fit 39/40, invalid 0.0, truncated 0, reasoning tokens 6556.446551724138
- minus: adoption 0.1388888888888889, fit 39/40, invalid 0.0, truncated 0, reasoning tokens 6446.325862068966
- plus: adoption 0.12037037037037036, fit 34/40, invalid 0.0, truncated 0, reasoning tokens 6625.560344827586
- rand: adoption 0.13518518518518519, fit 37/40, invalid 0.0, truncated 0, reasoning tokens 6374.91724137931
- dk: adoption 0.1425925925925926, fit 36/40, invalid 0.0, truncated 0, reasoning tokens 6682.313793103448

## Engine

- SGLang 0.5.18 (image 223b675f) with the jev_steer package; clarification AMENDMENT_WITNESS_DIRECTION.sglang.md sha256 9135fff98a8e
- deterministic
- Arms are paired by prompt. Deterministic mode: each call sends seed = sha256('wdir-seed|id|draw'), the same in every arm; SGLang samples by Gumbel noise keyed on (seed, position, column), common random numbers across arms.
- Battery request: temperature 0.6, top-k 20, top-p 0.95, min-p 0, presence penalty 0, max_tokens 32,768, strict json_schema, reasoning parser qwen3, context 40,960.
- Gate (ii) compares the alpha = 0 arm with the stored battery on the same engine.
- alpha0: {'calls': 580, 'retried': 0, 'resumed': 0, 'finish_reasons': {'stop': 580}}
- minus: {'calls': 580, 'retried': 0, 'resumed': 0, 'finish_reasons': {'stop': 580}}
- plus: {'calls': 580, 'retried': 0, 'resumed': 0, 'finish_reasons': {'stop': 580}}
- rand: {'calls': 580, 'retried': 0, 'resumed': 0, 'finish_reasons': {'stop': 580}}
- dk: {'calls': 580, 'retried': 0, 'resumed': 0, 'finish_reasons': {'stop': 580}}

## Pre-stated readings

- P1 fails: no linear trace of the decision at the last prompt token beyond the condition.
- Fidelity gate (ii) failed: Stage 1b is reported as HF-only; no comparison with the paper's battery.

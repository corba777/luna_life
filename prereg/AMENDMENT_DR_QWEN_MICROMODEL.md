# Amendment — TASK_LIFE_DR_MICROMODEL: Qwen support bound

**Status:** locked before the Qwen micromodel fit. Local, no API cost. Parent:
`TASK_LIFE_DR_MICROMODEL.md`.

## Support

The Luna adoption fit contains only inboxes with `n_opp` ≤ 8. There is no 88-line adoption condition
in that fit. The locked support rule restricted which rules may appear. It did not bound `n_opp`.

The Qwen fit uses the same model. Its support rule must also keep `n_opp` inside the range of its own
fit set. Live rows outside that range, including long-inbox `all` and `allshuf` rows, are an
extrapolation and are not scored as a test of the fitted model.

M1–M3 for Qwen stay as written in the task: they are re-locked in the amendment that precedes that
fit, after QI-1m, QI-G and Qwen Stage 1. This note does not start that fit.

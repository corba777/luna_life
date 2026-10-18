# Amendment — Pin the epoch and rerun DRc rounds 11–30

**Status:** locked before any live call of the pinned runner.
Parent predictions: `TASK_LIFE_DR_CLEAN_EXT.md`. They are not edited.

## Why

The first continuation of DRc from round 11 to round 30 is invalid. `Simulation.step` rolls the epoch every 10 generations (CHAIN_HYGIENE §26). After round 10, and again after round 20, the world function and every cell's examples are replaced. Those rounds are not a continuation of the published world. E1–E4 were not evaluated on that run.

## What this rerun changes

- The epoch is pinned. The new runner sets `EPOCH_LENGTH` to 31, which is at least 30, before it builds the simulation. Rounds 1–30 stay in epoch 0. The world-audit function and the examples from round 10 stay in place. The 10-round DRc runner is not edited.
- E1, E2, E3 and E4 are re-applied unchanged to the pinned run. The same six climbers, the same two lost runs, the same noise band 0.23, and the same comparison with 0.75.
- Rounds 11–30 of the first extension stay invalid and are not used. Their cache entries are not read. Each replicate gets a fresh cache for rounds 11–30.

## Cost

The budget is cumulative for this task, including the $7.62 already spent on the invalid extension. Alarm at $15. Stop at $20.

Closed-model outputs are not used as training data. No reasoning text is requested or stored.

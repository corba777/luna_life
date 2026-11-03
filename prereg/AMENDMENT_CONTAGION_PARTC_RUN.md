# Amendment — Part C run configuration (contagion, gpt-oss-20b, worlds 3 and 5)

**Status:** locked 2026-11-03 (Artem, with the C2 line as worded below). Adds the run settings that
`AMENDMENT_CONTAGION.md` Part C (locked 2026-10-25) leaves to "the panel full-run builder and
settings", to the standard of R-oss20 (`AMENDMENT_REPLICATES.md`). Part C's runs, references,
C1 and readings are unchanged; C2's unstated replicate pairing is resolved under "Storage and
readout".

## Runs

- gpt-oss-20b, worlds 3 and 5, `all` and Moore lattice, replicates r1 and r2, 20 rounds: 8 runs,
  16,000 calls, about 21.1 h at 4.74 s per call.
- Order, alternating so that drift is shared: w3 lattice r1, w3 `all` r1, w5 lattice r1, w5 `all`
  r1, then the same four for r2.
- Fresh cache per run (`runs/contagion/part_c/w<world>/<topology>/r<n>/`). No resume.

## Configuration

Identical to the W1-oss20 full runs and to R-oss20; the world is the only change.

- Builder: `run_life_panel_full._build` / `_make_inner` (W1-oss20 surface), with the builder's
  `WORLD` constant bound to 3 or 5 for the build only; `sim.world_seed` is asserted. k = 0, no
  sources, EPOCH_LENGTH 21 asserted before every round.
- Request: `run_life_panel_wave1.request_body("W1-oss20")` — temperature 1, top_p 1, max_tokens
  32,768, reasoning effort medium, strict json_schema `life_cell_decision_v2`.
- Server: `launch_argv("W1-oss20", context_length=40960)` — image `sha256:223b675f…` (SGLang
  0.5.18), revision `6cee5e81…`, mem 0.70, 16 running requests, reasoning parser gpt-oss, default
  chat template with its live date (recorded per round).
- Tokenize agreement per call; a mismatch stops the queue and quarantines the run.

## Sampler gate (item 12)

The R-oss20 gate, unchanged: W1-oss20 full-run `all` round-1 cell 0 (prompt sha256 `0fcd2042…`),
prior over the two W1-oss20 replicates top share 0.5, 64 serial + 64 batched, concurrency 16. Pass
= verdict open and serial top share ≤ 0.8. No re-pick: on fail the queue stops. No gpt-oss-20b
answers exist yet in worlds 3 and 5 to build a world-specific prior; the gate checks the sampler of
the same server configuration.

## Gates (dry check, no live call)

- **Prompt identity, `all`:** this runner replays Luna medium's world-3 and world-5 `all` references
  r1 and r2 for 20 rounds, answering only from Luna's cache by Luna's key of the prompt it builds; a
  miss aborts; rules must equal Luna's every round.
- **Prompt identity, lattice:** round 1 against Luna's r8 runs, r1 and r2 (empty inboxes at round 1;
  Moore and r8 differ from round 2 by design, as the Part C text states).
- **World 1:** the W1-oss20 lattice and `all` r1 originals replayed from their own caches.
- Class B (bookkeeping only; the builder does not use it): cells whose co-fitting set lacks the first
  op of the world's own P_e, from `world_audit.json`. The same 25 ids in worlds 1, 3 and 5 (0, 3, 6,
  9, 11, 14, 17, 30, 33, 36, 39, 41, 44, 47, 60, 63, 66, 69, 71, 74, 77, 90, 93, 96, 99).
- I_max for worlds 3 and 5 (4,189 in both) + max_tokens 32,768 ≤ context 40,960; launch arguments
  equal to the original W1-oss20 launches; stubs for refusal, tamper detection, tokenize abort and
  quarantine.

## Storage and readout

- Per call: final text only (item 16), finish reason, usage, sampling fields of the body sent,
  model id, revision, image and image id. Per round: cell states with the rendered date.
- Health monitor during the runs: counts only (calls, truncated, unparsed, empty text, tokenize
  mismatches, retries, server restarts), alert above 1 %. No x, rule shares or readout numbers
  before the readout job has run on all 8 runs.
- Readout (CPU job beside the waiter, `runs/readout_part_c.py`): C1 and C2 per world, with Luna's
  `all` level beside, and Luna's r8 lattice levels as labelled descriptives; recheck export. C1 / C2
  are scored only after Artem's recheck.
- **C1, as locked:** each `all` replicate of the world has x(10–20) > 0.5 (r1 and r2).
- **C2, fixed here before any Part C call:** the locked text requires C2 to hold in both replicates
  but does not say how `all` and lattice replicates pair. C2 therefore holds in a world only if every
  `all` run has a higher x(10–20) than every lattice run of that world: min(`all` r1, r2) >
  max(lattice r1, r2). This holds under any pairing. Pairing by replicate index and the comparison
  of means are reported beside it, descriptive.

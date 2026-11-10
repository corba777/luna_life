# Amendment — Qwen3-4B-Thinking `all` runs continued from round 20 to round 80

**Status:** LOCKED 2026-11-09 (Artem: "Lock AMENDMENT_QWEN_CONTINUE80.md as agreed but do not arm
its waiter; it runs only when the GPU would otherwise be idle."). No waiter armed; Queue below.
Draft history: DRAFT 2026-11-09 (Artem chose the scope: both `all` runs to round 80). Facts from
stored files (counts, run facts, code paths) filled 2026-11-09, CPU only, rounds 1–20 only.
Artem's decisions on the open items are in place (2026-11-09: context 40,960, gate 2 with prompt
identity through the cache, restore in the dry build, image by digest, small-cell rules, the M1
remark). Additions 2026-11-09 after review: M1′ with its reading; the outputs per run. Dry check
built and passed 2026-11-09 (CPU only); its values are filled below. No x or other outcome after
round 20 exists yet. Basis: `AMENDMENT_OSS120_CONTINUE80.md` (locked,
scored 2026-11-09: K1, K2, K3 fail), its recheck (`PAPER_LIFE_CHANGELOG.md`, v1.17), and the Qwen
population runs scored under B1-Qwen.

## Why

The Qwen populations were run for 20 rounds. On `all` they sit near the witness plateau
(x(10–20) = 0.164 in r1 and 0.195 in r2; `runs/life_dr_qwen/stage1_readout.md`, recomputed from the
rule histories). The gpt-oss-120b continuation showed that a 20- or 40-round
window can mislead: both frozen 120b `all` runs left the plateau late (x crossed 0.5 at rounds 41
and 69) and ended near 0.86. The recheck traced the simulator's miss to the tails of the
battery's logistic fits: at a saturated inbox the population abandoned P_e about twice as often as
fitted, and near a P_e share of 0.5–0.6 it adopted more often than fitted.

Qwen's battery puts it far from any such escape: adoption below unanimity is at most 0.10 at every
`all` share (0.017 on average at shares 0.10–0.30) and abandonment at share 0.30 is 0.76
(Section 5.1). Proposition 3's lower bound on the fixed point, ε / (ε + β̄), is then small, which
neither promises nor forbids an escape. The question is direct: is the stubborn responder's
witness plateau absorbing over 80 rounds, where the graded 120b's was not? The answer also decides
whether the witness-direction work (`AMENDMENT_WITNESS_DIRECTION.md`) is looking at a model that
lacks a usable adoption response or at one that only shows it late.

Scope (Artem, 2026-11-09): `all` r1 and r2 only. The lattice runs are not continued now.

## Runs

- Qwen3-4B-Thinking-2507 (revision 768f209d…), world 1, `all` r1 and r2: rounds 1–20 restored by
  replay from each run's stored cache (no call), rounds 21–80 live, 2 × 6,000 = 12,000 calls.
  Stored runs (arm `dist/qwen4bT.local/all/none`, world 1, `MANIFEST.json` of `runs/life_dr_qwen/`,
  sha256 `9539764f…`):

  | run | history | cache | entries |
  |---|---|---|---:|
  | r1 | `runs/life_dr_qwen/all/r1/seed1/rule_history.json` (`d3588698…`); `rounds.json` (`af42491d…`, rounds 1–5 only) | `runs/life_dr_qwen/cache_stage1_all_r1/` | 2,000 |
  | r2 | `runs/life_dr_qwen/all/r2/seed1/rule_history.json` (`df6d9059…`); no `rounds.json` | `runs/life_dr_qwen/cache_stage1_all_r2/` | 2,000 |

  Cache sha256 over the concatenated entries in file-name order: r1 `3c051c05…`, r2 `c65dacdd…`. Every
  entry: `finish_reason` stop, not truncated, non-empty text (4,000 / 4,000). These files are not in
  git; the dry build commits their hashes. **There are no `cell_states.jsonl` or `records.jsonl`:**
  the Qwen Stage 1 runner kept per round only the rule history (held rule, inbox says, checks and
  source mask per cell), so gate 2 compares against that. Publication in round t is visible only as
  the round-(t + 1) inbox, so **round-20 publication bits are not in any stored file**. They come
  from the restore, which the dry build runs (CPU, no call; Restore below).

  How the 20 rounds were played: r1 rounds 1–5 by the probe (`runs/run_life_dr_qwen_stage1.py`,
  commit `42e4a4c1`, `stage1.log`); round 6 by the first `all` process (commit `d0c6c674`), which made
  its 100 calls and then aborted on a record count before writing the history (`stage1_all.log`,
  `stage1_all.aborted`); round 6 written from cache by the resume dry run (100 / 100 hits,
  `stage1_all_resume_dry.log`); rounds 7–20 live and r2 rounds 1–20 live by
  `runs/run_life_dr_qwen_stage1_all_resume.py` (commit `4633d696`, `stage1_all_resume.log`,
  `stage1_all_resume.ok`). The resume replayed r1 rounds 1–6 from cache with the logged P_e counts
  (7, 7, 9, 13, 12, 13) before going live.
- Same server, image, revision, chat template, request body, sampling and builder as the stored
  runs; **one difference: context length 40,960** (Artem, 2026-11-09). Reason: at the stored 36,864
  with max_tokens 32,768, the prompt may use at most 4,096 tokens. The largest stored prompt is
  3,845, a headroom of 251 (gate 4), and rounds 21–80 can carry longer inboxes than any stored
  round. Qwen Part A hit the same limit at 36,864 and was resumed at 40,960 with decoding
  unchanged (`runs/contagion/local_qwen/resume_40960_note.md`). max_tokens stays 32,768.
  Context length is not part of the cache key (below), so it changes no stored key and no request
  body. As recorded for the stored runs (`MANIFEST.json` settings, `runs/run_life_dr_qwen.py`
  constants, `stage1_all_resume.log` server line, per-entry `served_model` / `model_revision` in
  the caches): SGLang 0.5.18; context length 36,864; max_tokens 32,768; temperature 0.6, top_p 0.95, top_k 20,
  min_p 0, presence_penalty 0; reasoning parser `qwen3` with `REASONING=1`, thinking
  `template_default`, no separate thinking budget; `--mem-fraction-static 0.6`; concurrency 64;
  schema `decision_json_schema`; client `SglangDrcClient`. **Image: not recorded as a digest.** The
  runs started `runs/spade_grid/serve_sglang.sh`, whose default is the tag
  `lmsysorg/sglang:latest-cu130`; that tag resolves today to `sha256:223b675f…` (created
  2026-08-21, the Part A image), which is not a record of 2026-10-19. **This run is launched by
  image ID `sha256:223b675fee9ec3020a7b1479a6d1a3d24296f729f2eb6049f69f1e0423118e7e`** (local image
  ID; registry digest `lmsysorg/sglang@sha256:9e148f5ac788e856a06166bd6347a831831eb9fcfab4d1770874823a7c29a1a1`),
  passed as `SGLANG_IMAGE` and checked on the running container by `docker inspect`. Before the
  first call, the server must report SGLang 0.5.18 and the sampler gate must pass; otherwise no
  call is made (gate 4).
  EPOCH_LENGTH pinned to 81 in every place it is read (`v1a.EPOCH_LENGTH` and `eng.EPOCH_LENGTH`
  via `pin_epoch`, and `run_life_dr_qwen_stage1.PINNED_EPOCH`, which renders the
  "generation t of this epoch" header; stored value 21), set after the build, asserted before every
  round, with a pin test, as in CONTINUE80.
- Cost (per-round wall from `stage1_all_resume.log` and `all/r1/seed1/rounds.json`; r1 round 6 has
  no logged wall):

  | run | mean wall rounds 2–10 | mean wall rounds 11–20 | slope | rounds 21–80 at 11–20 rate | linear trend |
  |---|---:|---:|---:|---:|---:|
  | r1 | 3,682 s (8 rounds) | 3,700 s | +1.3 s / round | 61.7 h | 62.4 h |
  | r2 | 3,811 s | 3,955 s | +3.5 s / round | 65.9 h | 67.1 h |
  | both | | | | **127.6 h (5.3 d)** | **129.4 h (5.4 d)** |

  Stored rounds 1–20 took 19.5 h (r1, 19 logged rounds) and 21.4 h (r2). This is above the earlier
  estimate of 4.5–5 GPU days.
- Fresh cache per continued run; no resume; final text, reasoning (open model: stored), finish
  reason and launch fields per call; per-round cell states.
- Outputs per run: the runner writes `cell_states.jsonl`, `records.jsonl` and the rule history for
  every round 1–80; rounds 1–20 come from the replay, rounds 21–80 from the live calls. The
  recheck package therefore matches CONTINUE80's (Design audit 8).
- Progress: x may be reported during the run (as for CONTINUE80, Artem 2026-11-06); no run is
  stopped or changed on it. Health counts per run as before (calls, empty texts, retries,
  truncations, tokenize mismatches).

**Restore.** As in CONTINUE80: rounds 1–20 are replayed through the stored runs' builder at
EPOCH_LENGTH 81, every answer served from the run's own cache under its cache key; a miss aborts.
The replayed rule history must equal the stored one, and every stored key must be used, before
round 21 (gate 2). Runner: **`runs/run_qwen_continue80.py`** (new file). It imports the stored
builder (`run_life_dr_qwen_stage1._build`, `_stamp`, `_check_round`) and plays the resume's round
body; the stored client `SglangDrcClient` is subclassed only for the cache location and the
per-call fields: its key (`_disk_key`) and request (`_post`) are used unchanged. `run_oss120_continue80.py` is
not reused: it wraps the Stage 2 / `panel_full` builder with the pinned date template, which these
runs never used.

**Prompt identity through the cache.** The cache key is the sha256 of the canonical JSON of
{model, revision, the full rendered prompt, draw, catalog digest, answer schema, sampling,
max_tokens, thinking mode} (`SglangDrcClient._disk_key`, `runs/run_life_dr_qwen.py`). Context
length is not in it. A replayed prompt that differs from the stored one by any byte therefore has a
different key. Under `forbid_live` the stored `GuardedClient` raises `replay cache miss; no live call
was made` before any POST (`runs/run_life_dr_qwen_stage1.py`). So gate 2 has two parts:
1. rule history equal, every round 1–20 (held rules, inbox says, checks, source mask per cell);
2. every replayed call a hit, with the set of keys used equal to the 2,000 files of the run's
   cache (no miss, no unused entry). Since there are 2,000 calls and 2,000 entries, every stored
   prompt is reproduced exactly once.

No records were stored, so there is no separate record comparison.

**Restore in the dry build (Artem, 2026-11-09).** The dry build runs this restore for both runs on
the CPU (no server, live calls forbidden). From the restored state it takes:
- the round-20 holdings and publication bits, which are M1's and M0's start state;
- the round-20 publication of every cell, which completes the publication rates over rounds 2–20;
- the largest round-20 inbox.

M1, M1′ and M0 are then computed and written into this amendment before the lock (done: Dry
check; Predictions table).

## Gates (live calls refused unless stated)

1. **Continuation identity (CPU, stub).** Three arms per run as in CONTINUE80 gate 1: the stored
   runner for 20 rounds; 25 rounds without a break at 81; a fresh process that restores the first
   by replay and plays rounds 21–25 live. Prompts of rounds 21–25 byte-identical between the last
   two; full engine and completer state byte-identical at rounds 20 and 25.
2. **Restored round 20 equals the stored round 20,** both runs, every round 1–20. Two parts:
   (a) rule history equal;
   (b) prompt identity through the cache: every replayed call a hit, and the set of keys used
   equal to the run's 2,000 cache files (Restore).
   A miss aborts before any POST. Run in the dry build, and repeated at the start of each live run.
3. **Horizon.** Stub run of rounds 1–80 at EPOCH_LENGTH 81: rounds 1–20 byte-identical to the
   stored build; one template; every header "Epoch 0, generation t"; no horizon word (the
   CONTINUE80 list).
4. **Context.** Worst-case prompt over rounds 21–80 (`all` render, every other cell publishing the
   longest catalog rule) + max_tokens ≤ context length, with the headroom stated. Stored facts:
   context 36,864 − max_tokens 32,768 leaves **4,096** prompt tokens; the largest stored prompt is
   3,753 (r1) and 3,845 (r2) tokens (`usage.prompt_tokens` over the 4,000 cache entries; round-1–20
   inboxes had at most 82 lines), headroom 251. Qwen Part A hit this limit at 36,864 (prompts of
   4,173 and 4,305 tokens, `runs/contagion/local_qwen/run.aborted`). This run therefore uses
   context **40,960** (Runs). Gate: I_max over rounds 21–80, computed in the dry build with the
   Qwen tokenizer, + 32,768 ≤ 40,960, headroom stated. **Dry build: I_max = 4,622 tokens** (every
   round 21–80 gives the same maximum; cell 14, 99 inbox lines of `rotate_left(3);shift_symbols(7)`,
   signal 7). 4,622 + 32,768 = 37,390 ≤ 40,960, **headroom 3,570**. At the stored 36,864 this
   prompt would not fit (limit 4,096).
   At server start: the server reports SGLang 0.5.18 and the container's image is
   `sha256:223b675f…` (`docker inspect`). Then the sampler gate passes. The stored Stage 1 runs
   ran no sampler gate (no gate in `runs/run_life_dr_qwen_stage1*.py` or their logs); this run uses
   the Qwen gate of the Part A rerun at 40,960 (`run_parta_text_replication.sampler_gate("qwen")`,
   arm `qwen_posthoc_40960`), with its output in this run's directory. Otherwise no call is made.
5. **GPU exclusivity.** Strict precheck (manifest of this dry build matches the logged one; no GPU
   compute process; no other model server; open-webui off) and the continuous log-only monitor
   from the waiter's start; request count per run against the server log, as in CONTINUE80.
   This waiter must not start while any other waiter holds the GPU or may resume onto it; if the
   witness-direction queue is in `wait_go_witness_budget`, its waiter is idle and the GPU is free,
   but the two waiters' order is logged with Artem's go.

## Dry check (2026-11-09, CPU, no live call)

`python runs/run_qwen_continue80.py dry` → `runs/qwen/continue80/dry_check.json` (sha256
`135af17e…`, runner sha256 `54252781…`; the runner reads the lock from the switch log, so locking
does not change it). The stored `MANIFEST.json` is unchanged by it
(`9539764f…` before and after). All parts pass:

1. **Gate 1 (stub).** Stored arm: `stage1._build` at EPOCH_LENGTH 21 and the resume's `_play`, 20
   rounds. Uninterrupted arm: build at 81, rounds 1–80 in one process. Continued arm: fresh process,
   restore of rounds 1–20 from the stored arm's cache, rounds 21–25 through `SglangDrcClient._post`
   (stub transport). Prompts and rule history of rounds 1–20 at 81 equal the stored arm's at 21.
   Prompts of rounds 21–25 are identical; cell states of rounds 1–25 are identical; the full engine
   and completer state is byte-identical at round 20 (11.4 MB) and round 25 (14.3 MB). All 2,032
   cache entries of the stored arm were used (the stub's 32 retries included); one request body
   apart from the prompt.
2. **Gate 2 (stored runs).** Both runs:

   | run | rule history 1–20 equal | keys used / cache files | live calls | Qwen tokenizer vs stored `prompt_tokens`, round 20 | round-21 header |
   |---|---|---:|---:|---:|---|
   | r1 | yes (20 / 20 rounds) | 2,000 / 2,000 | 0 | 100 / 100 equal | "Epoch 0, generation 21 of this epoch." × 100 |
   | r2 | yes (20 / 20 rounds) | 2,000 / 2,000 | 0 | 100 / 100 equal | same |

   Replay takes about 25 s per run. Restored cell states (`dry_work/restore_r1/`, `restore_r2/`):
   r1 `4c7b0462…`, r2 `6596480c…`; records r1 `d638c029…`, r2 `0e2be193…`. Publication from the
   records equals the publishers recovered from the next round's inbox in every round 1–19 of both runs.
3. **Gate 3 (horizon, stub).** Rounds 1–20 at 81 byte-identical to the stored build; one template
   over rounds 1–80 (`88455637…`); every header "Epoch 0, generation t of this epoch."; examples
   and catalog entries constant; no horizon word; epoch 0 and P_e unchanged through round 80.
   Against round 20, rounds 21, 22 and 80 differ only in round state (header, query, previous step,
   visible messages, catalog order).
4. **Gate 4.** I_max 4,622, headroom 3,570 (above); the worst-case prompt has the run's template.
5. **Pin test.** Pins (engine, v1a, slots_for) 10 / 10 / 21 at import, 81 / 81 / 81 after the build;
   resetting any one of them to 21 is caught by the per-round assertion.

Not covered by the dry check: the server start (image, version), the sampler gate and the request
count; they are checked live before the first call (gates 4–5).

## Model used for the predictions

Lesson from 120b: the battery's logistic fits are calibrated in the middle of the share range
and wrong at the ends. The primary model therefore uses Qwen's own population rates where they
are measured, and the battery only where the population has not been. In rounds 2–20 Qwen's
population never reached s ≥ 0.3, and only 20 class-A cell-rounds started on P_e. M1 therefore
equals M0 above s = 0.3 and in every abandon bin, and the 120b tail lesson cannot be tested on
Qwen's own data.

**M1 (primary).** The record's simulator update on `all`, run from each run's stored round-20
state (holdings and publication bits), 2,000 replicates, seed 0, MC SE.
- Witnesses: hazards h_in, h_out measured in Qwen's `all` runs, rounds 2–20, both runs pooled
  (Proposition 4b), as in CONTINUE80: **h_out = 104 / 637 = 0.163, h_in = 111 / 313 = 0.355**
  (r1 53 / 279 and 57 / 196; r2 51 / 358 and 54 / 117), the pooled counts of
  `stage1_readout.md`, recomputed from the rule histories with the same result. The 25 witnesses
  (class B) are cells 0, 3, 6, 9, 11, 14, 17, 30, 33, 36, 39, 41, 44, 47, 60, 63, 66, 69, 71, 74, 77,
  90, 93, 96, 99.
- Class A: flip probability by the P_e share s of the cell's inbox (lines from cells that
  published in round t − 1 and held P_e, over all published lines), in ten bins [0, 0.1), …,
  [0.9, 1.0]. Adopt (cell off P_e) and abandon (cell on P_e) separately. In a bin with at least 30
  class-A cell-rounds of that direction in rounds 2–20 (both runs pooled), the empirical rate; in
  any other bin, Qwen's battery fit (`n88_adopt` / `n88_abandon`, logistic in s) evaluated at the
  bin midpoint. The table of the twenty rates, their source (population or battery) and counts is
  part of the lock.

  Counts: class-A transitions into rounds 2–20, both runs (2 × 19 × 75 = 2,850). s is the cell's
  inbox share as defined above. Round-(t − 1) publishers and their lines are recovered from the
  round-t inboxes: a publisher's inbox lacks its own line. In every round 1–19 each recovered line
  equals the publisher's held rule (0 mismatches), so "lines saying P_e" gives the same table.
  Battery fits are from `runs/contagion/qwen_part_a_readout.json` (2,960 answers, after the 40,960
  resume): `n88_adopt` β = (−5.8191, 5.9889), `n88_abandon` β = (1.7524, −2.7249), both not
  separated. The export copy `exports/contagion_qwen_part_ab_artem_recheck_2026-10-27/` has the
  same β.

  | bin s | adopt: flips / n | adopt rate used | source | abandon: flips / n | abandon rate used | source |
  |---|---:|---:|---|---:|---:|---|
  | [0.0, 0.1) | 0 / 225 | 0.0000 | population | 0 / 0 | 0.8343 | battery |
  | [0.1, 0.2) | 11 / 1,620 | 0.0068 | population | 8 / 12 | 0.7931 | battery |
  | [0.2, 0.3) | 5 / 985 | 0.0051 | population | 6 / 8 | 0.7448 | battery |
  | [0.3, 0.4) | 0 / 0 | 0.0236 | battery | 0 / 0 | 0.6897 | battery |
  | [0.4, 0.5) | 0 / 0 | 0.0421 | battery | 0 / 0 | 0.6286 | battery |
  | [0.5, 0.6) | 0 / 0 | 0.0741 | battery | 0 / 0 | 0.5631 | battery |
  | [0.6, 0.7) | 0 / 0 | 0.1272 | battery | 0 / 0 | 0.4953 | battery |
  | [0.7, 0.8) | 0 / 0 | 0.2096 | battery | 0 / 0 | 0.4277 | battery |
  | [0.8, 0.9) | 0 / 0 | 0.3255 | battery | 0 / 0 | 0.3627 | battery |
  | [0.9, 1.0] | 0 / 0 | 0.4676 | battery | 0 / 0 | 0.3023 | battery |

  Fit values at the three adopt population bins, beside: 0.0040, 0.0072, 0.0131. Every class-A
  inbox in rounds 2–20 had s < 0.3. Only 20 class-A cell-rounds started on P_e (no abandon bin
  reaches 30), so all ten abandon rates are the battery's.
- Publication: by class and by held rule (P_e, prefix, other), rounds 2–20, both runs pooled.
  Small cells (Artem, 2026-11-09): the locked rule for class-A flips stands as written (< 30
  cell-rounds → battery). For publication, a (class, held rule) cell with < 30 cell-rounds uses its
  class's rate pooled over all held rules. Rounds 2–20 from the restored cell states (published =
  the round's record has a `say_key`; in rounds 1–19 this equals the publishers recovered from the
  next round's inbox in every round, both runs). Round 20 adds 79 (r1) and 75 (r2) publications to
  the 2–19 counts of the draft.

  | class | held rule | published / cell-rounds (2–20) | rate used |
  |---|---|---:|---:|
  | A | prefix `shift_symbols(1)` | 2,038 / 2,827 | 0.721 |
  | A | P_e | 15 / 22 | class A pooled 2,054 / 2,850 = 0.721 |
  | A | other | 1 / 1 | class A pooled 0.721 |
  | B | P_e | 472 / 644 | 0.733 |
  | B | other (not prefix) | 229 / 302 | 0.758 |
  | B | prefix | 0 / 4 | class B pooled 701 / 950 = 0.738 |

  The simulator tracks a cell's held rule as P_e, prefix or other. A cell that leaves P_e takes its
  class's majority non-P_e rule in rounds 2–20 (class A prefix, class B other); a cell that adopts
  P_e holds P_e.

**M1′ (descriptive, not scored).** M1 with each run's own witness hazards instead of the pooled
ones: r1 h_in = 57 / 196 = 0.291 [0.232, 0.358], h_out = 53 / 279 = 0.190; r2 h_in = 54 / 117 =
0.462 [0.374, 0.552], h_out = 51 / 358 = 0.142 (Wilson 95 %; same counts as above). Everything else
as M1. Reason: the two runs' witness hazards differ (h_in intervals do not overlap), and M1 pools
them as locked for CONTINUE80. Median and 5–95 % band reported beside M1.

**M0 (descriptive).** The same update with the battery fits everywhere (the record's convention
apart from the witness hazards). Reported beside M1; not scored.

Counts (rounds 1–20, stored rule histories): `runs/qwen_continue80_counts.py` →
`runs/qwen/continue80_counts_rounds_1_20.json`. Simulator (built with the dry check):
`runs/sim_qwen_continue80.py`. Its round loop is the `all` update of
`runs/sim_oss120_continue80.run` (inbox = every other cell's round-(t − 1) publication; per round
the class-A uniforms, then the class-B uniforms, then the publication uniforms; numpy
`default_rng(0)` per run and model), with the probability lookups of M1 / M1′ / M0 in place of
the record's fits; the summary helpers are imported from that file. It recomputes every count
above from the restored cell states (witness transitions, class-A table, publication 2–20) and
aborts unless they equal the tables here. Its start state is the restored round 20. Output
`runs/qwen/continue80_sim.json` with its sha256. Window x(70–80): mean over rounds 70–80 inclusive
of the share of 100 cells holding P_e, class B included.

| run | x(20) | witnesses on P_e at 20 (of 25) | M1 median x(70–80) [p05, p95] | M1 P(x(70–80) < 0.5) | M1′ median x(70–80) [p05, p95] | M0 median x(70–80) [p05, p95] | M0 P(x(70–80) < 0.5) |
|---|---:|---:|---|---:|---|---|---:|
| `all` r1 | 0.11 | 11 | 0.177 [0.158, 0.195] | 1.000 | 0.157 [0.136, 0.178] | 0.180 [0.159, 0.200] | 1.000 |
| `all` r2 | 0.19 | 17 | 0.177 [0.158, 0.195] | 1.000 | 0.196 [0.180, 0.213] | 0.180 [0.159, 0.200] | 1.000 |

`runs/qwen/continue80_sim.json` (sha256 `73e5efad…`), 2,000 replicates per run and model, seed 0.
MC SE of each median ≤ 0.0005 (bootstrap). In no model did any replicate of either run reach
x ≥ 0.5 in any round 21–80 (0 / 2,000 per run). With zero events the 95 % upper bound on
P(x(70–80) ≥ 0.5) is 3 / 2,000 = 0.0015 per run.

Restored round 20 (dry build), the start state:
- r1: x 0.11, witnesses on P_e 11, class-A cells on P_e 0, prefix 75, published 79 (19 witnesses).
- r2: x 0.19, witnesses on P_e 17, class-A cells on P_e 2, prefix 74, published 75 (16 witnesses).
- Largest round-20 inbox: 71 lines (r1) and 69 lines (r2).

M1 gives the same band for r1 and r2. Under M1, class-A cells almost never adopt (≤ 0.007 per
round at the shares reached), and the 25 witnesses mix with pooled hazards to a stationary share
of about 0.355 / (0.355 + 0.163) ≈ 0.69, i.e. 17 witnesses. Both runs use seed 0, so the same
uniforms drive both, and the two simulated populations coalesce: in 1,997 of 2,000 replicates the
r1 and r2 trajectories are identical cell by cell over rounds 70–80. The window no longer depends
on the round-20 state. M1′ separates the runs only through their own hazards (stationary witness
share 0.60 in r1, 0.76 in r2). M0 differs from M1 only through class-A adoption at s < 0.3
(battery logistic, 0.004–0.013 at the bin midpoints, against the population's 0–0.007).

## Predictions (to lock)

Unit: the run.

- **Q1 (plateau).** The statement is fixed by M1 before any call: if M1's P(both runs have
  x(70–80) < 0.5) ≥ 0.5, Q1 is "both runs stay below 0.5"; otherwise Q1 is "at least one run
  reaches x(70–80) ≥ 0.5". Locked with M1's probability for the chosen statement (product of the
  two per-run probabilities; delta-method MC SE).
  **Q1 (locked): both runs have x(70–80) < 0.5. M1 probability 1.000** (0 of 2,000 replicates
  reach 0.5 in either run; MC SE 0; by the zero-event bound, P ≥ 1 − 2 × 0.0015 = 0.997).
- **Q2 (level).** Each run's x(70–80) lies inside its M1 5–95 % band. Scored per run; Q2 holds if
  both are inside. Locked bands: r1 [0.158, 0.195], r2 [0.158, 0.195].
- **Q3 (descriptive).** Per run: x(80); the first round with x ≥ 0.5 (or none); witness share per
  round; class-A adopt and abandon rates by share bin in rounds 21–80 against rounds 2–20 and
  against the battery fits (the comparison made for 120b in v1.17); the same beside the two 120b
  `all` runs that escaped.

## Pre-stated readings

- **Both runs stay below 0.5, as M1 predicts:** the stubborn responder's plateau held for 80
  rounds where the graded 120b's did not. Response class decides not only the ranking in a window
  but whether the plateau is left at all. The witness-direction search is then a search for a
  response the model barely has.
- **A run reaches 0.5 against M1:** Qwen's plateau is not absorbing either. Reported with the
  class-A rates near s = 0.5 (where 120b's escapes crossed) and the round of the crossing; the
  stubborn class is then a slow class, not a stuck one.
- **Q2 fails with Q1 holding:** the plateau holds at a level M1 misses; reported with the rates by
  bin, as for 120b.
- Q2 fails for a run whose x(70–80) lies inside its M1′ band: the miss is witness heterogeneity
  between runs, not class A.

## Design audit

1. **Fidelity.** Same populations and configuration; the horizon is longer (gates 1–3) and the
   context length is 40,960 instead of 36,864 (Runs; max_tokens and the request body unchanged).
   **Limitation:** the stored runs' image digest on 2026-10-19 was not recorded, only the tag
   `lmsysorg/sglang:latest-cu130` and SGLang 0.5.18. This run uses `sha256:223b675f…`, the
   digest that tag names today; the match is inferred, not shown.
2. **Coverage.** Qwen `all` only; lattice not continued (scope).
3. **Controls.** None within this amendment; the comparison is with the 120b `all` continuation.
4. **Observability.** Cells see their prompts only; the channel audit (Appendix D) applies.
5. **Gate consistency.** All gates before the first call.
6. **Statistical unit.** The run; per-run predictions from the run's own round-20 state.
7. **Pre-stated readings.** Above.
8. **Recheck.** Package as for CONTINUE80 (cell states 1–80, records, call texts with reasoning,
   restore files, server log, monitor, simulator inputs and output); I recompute x, the scores,
   the rates by bin and the request counts from the raw files.

## Queue

GPU job. Order relative to the witness-direction queue (v22d) is Artem's call: if v22d stops for
budget, this run can use the idle GPU while the budget decision is open. The waiter is a new file
armed only after this amendment is locked: `wait_gpu_free` → `wait_go_qwen_continue80` (Artem's go,
logged with his words) → strict precheck (gate 5) → server start and sampler gate → `all` r1, then
`all` r2 → automatic CPU readout and recheck package.

At lock (Artem, 2026-11-09): the waiter is not armed. This run is filler: it takes the GPU only when
the GPU would otherwise be idle, and only after Artem's go.
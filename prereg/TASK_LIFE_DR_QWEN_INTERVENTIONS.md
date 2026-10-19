# Task — Qwen interventions on the Part 0b prompts

**Status:** locked. Predictions are locked with this file, before any Qwen call. Local model
via SGLang, no API cost. Parent: `TASK_LIFE_DR_CONTROLS.md` (Part 0b and its amendment) and
`TASK_LIFE_DR_QWEN.md`.

## Agent

Qwen3-4B-Thinking-2507, the same weights, SGLang version, thinking mode, sampling and max-token
limit as Qwen Stage 1. The runner copies them from `runs/life_dr_qwen/MANIFEST.json` and records
them. At the lock those values are: revision `768f209d9ea81521153ed38c47d515654e938aea`, SGLang
0.5.18, thinking mode `template_default`, reasoning parser `qwen3`, temperature 0.6, top_p 0.95,
top_k 20, min_p 0, presence_penalty 0, max tokens 32768, context length 36864, mem-fraction-static
0.6, concurrency 64.

Separate cache namespace from Stage 0, Stage 1, and from every Luna cache. A read of another
cache aborts.

Parse failures and truncations are reported, excluded from n, and counted. Qwen thinking text
may be stored locally for debugging only. It is not training data. No reasoning text from a
closed model is requested or stored.

## Part QI-1 — Part 0b replay

The Part 0b builder rebuilds the prompts. Before any call, each rebuilt prompt is checked
byte-identical to the Luna Part 0b prompt for the same cell, condition and draw. A mismatch
aborts the run.

The controls task named ten inbox conditions and 800 calls. The Part 0b amendment added
condition `1/7` (1 P_e line and 7 prefix lines), because I2's second arm is not among those
ten, and Luna sent 880 prompts. I2q is that contrast, and the descriptive curve is the curve
Luna reported, which has the eleventh row. The locked replay is those **880** prompts: the
same 40 source cells, the ten conditions plus `1/7`, and the same 2 draws. The 800 are the
ten-condition subset of that set.

**Predictions (locked), the same tests as Part 0b:**

- **I1q.** Class A, P(adopt P_e | 5/3) > P(adopt P_e | 3/5). One-sided Fisher exact test,
  α = 0.05.
- **I2q.** Class A, P(adopt P_e | 1 P_e line, 7 empty) > P(adopt P_e | 1 P_e line, 7 prefix
  lines). One-sided Fisher exact test, α = 0.05.
- **I3q.** Class B under 8 prefix lines, the share adopting the prefix ≤ 0.08. The bound is
  the Luna floor. Qwen Stage 0 refuting cells held the prefix in 1 of 100.
- **Descriptive.** The full curve by class, next to Luna's on the same prompts. Per-prompt
  agreement between the two models: the parsed rule, matched by cell, condition and draw.
  A prompt that failed to parse on either model is counted and left out of the agreement
  denominator.

Each draw is an outcome, as in the Part 0b Fisher tests. A condition's n is at most 40
(20 cells × 2 draws) after failures are removed.

## Part QI-2 — signal, causal

Class A source prompts from QI-1. Those cells do not hold P_e. The Part 0b selection has 20
class-A cells, so the locked set is 20 × 2 conditions × 2 draws = **80** calls. The count
40 × 2 × 2 = 160 includes the 20 class-B cells. Class B is not in S1.

The inbox has 2 P_e lines and 6 prefix lines, all 8 slots filled. The P_e lines are at
signal 7. Two conditions: the 6 prefix lines all at signal 1, or all at signal 7. Draws use
the QI-2 cache.

- **S1.** P(adopt P_e | prefix at signal 1) > P(adopt P_e | prefix at signal 7). One-sided
  Fisher exact test, α = 0.05. Post hoc origin: the effect was seen in Luna logs, not tested
  causally there.

n is at most 40 (20 cells × 2 draws) per condition after failures are removed.

## Schedule

Not launched with this lock.

Stage 0 wall time, concurrency 64, five worlds of 100 live calls: mean 40.39 s per decision
(range 35.36–45.79). That is 1.122 h per 100 calls.

| part | calls | wall hours |
|---|---:|---:|
| QI-1 | 880 | 9.87 |
| QI-2 | 80 | 0.90 |
| together | 960 | 10.8 |

The ten-condition 800 plus a 160-call QI-2 is the same 960 calls and the same 10.8 h. Stage 0
is an empty inbox. The Stage 1 `all` probe at round 5, a long inbox, was 29.8 s per decision,
inside that band. No pad is added.

Queue QI-1 and QI-2 after Qwen Stage 1 `all` finishes and before any moore run, unless Artem
says to run them concurrently. At this lock, Stage 1 `all` is aborted (`stage1_all.aborted`,
`RuntimeError: r1 records 600`) and is not running. This task does not restart it.

New runner, with a lock file on its run directory that aborts a second writer. Do not edit
the Stage 1 runner or any running Stage 1 process.

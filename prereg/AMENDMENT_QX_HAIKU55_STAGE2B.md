# Amendment — Claude Haiku 5.5, Stage 2B: silence (T-SH) and four tests per cell (T-H4)

**Status:** draft v2 (2026-11-24), written by the reviewer for Artem. v2 takes in the dry build
(`runs/dry_build_qx_haiku55_stage2b.md`): run names, rebuilt prompts (0 mismatches against the stored Luna and
gpt-oss-20b prompts), token counts, the projection, the T-SH comparison traces by sha256. Stage 2 of `AMENDMENT_QX_HAIKU55.md`
(v2, locked `c5d7488d…`). Artem, 2026-11-24 12:20: «Пиши». Money ceiling for Haiku: $72 in all (Artem,
2026-11-24 10:52: «$50 я считал сверху этих $22»). Locked after the agent's dry build and the reviewer's review;
no call before the lock and Artem's go.

## Why

Stage 2A (entry 19) showed, for Claude Haiku 5.5 at δ 1/8: rule names alone moved no cell without its own
counterexample (x̄_nf ≤ 0.004 in four worlds), while a few shared results carried H_T to most of the grid. Two
questions remain that the Luna and gpt-oss-20b programme asked: do rule names add anything over silence
(entry 10, entry 15), and do names carry the error once there are many finders (entry 9, four tests per cell)?

## Design (only the model changes)

Prompts, schemas, engine, worlds, traces and measures as in the original amendments; decoding as in Stage 0
(adaptive thinking, effort medium, max_tokens 8192, Luna's schema, prompt bytes as rendered for Luna).

- **Part S — silence.** As `AMENDMENT_QX3_SILENT.md` (locked): **Claude Haiku 5.5 · δ 1/8 · B 1 · no messages
  delivered (S) · G 24 · worlds 0–3**, 4 runs, 9,600 calls, `qx3s_haiku55_d8_B1_S_w{0..3}`. The rule-only
  comparison runs are the four Stage 2A R runs, not rerun: `qx3w_haiku55_d8_B1_R_w0` `b1563755…`, `_w1` `291594c0…`,
  `_w2` `e0efe4b8…`, `_w3` `d1d3492a…` (sha256 of the trace files; reviewer's copies match).
- **Part L — four tests.** As `AMENDMENT_QX3_B4.md` (locked): **Claude Haiku 5.5 · δ 1/64 · rule only · G 24 ·
  worlds 0–3 · B 4 and B 1**, 8 runs, 19,200 calls, `qx3b4_haiku55_d64_B4_R_w{0..3}` and
  `qx3w_haiku55_d64_B1_R_w{0..3}` (Haiku has no δ 1/64 runs yet, so the B 1 comparison runs are part of this
  stage).

Order: S_w0–S_w3, then per world B1 then B4 (B1_w0, B4_w0, B1_w1, …), so a stop leaves complete pairs.

## Tests (one-sided exact permutation on x̄, four runs against four, 70 splits, ties against rejection, α 0.05,
p ≤ 3/70; a missing or partial run leaves the test not decided)

**T-SH: rule only above silent, δ 1/8.** **Prediction: does not hold.** Basis: in Stage 2A rule-only runs no cell
without its own counterexample reached H_T (x̄_nf 0–0.004), so rule-only and silent should differ only through
finders. Stated risk: for gpt-oss-20b the same prediction held only narrowly (p = 6/70), and rule-only runs had
more finders and more tests on the region than silent ones (post hoc, entry 15).

**T-H4: B = 4 above B = 1, rule only, δ 1/64.** **Prediction: holds.** Basis: with four tests a cell tests the
region about four times as often, and Haiku updates on its own counterexample almost always (isolation U1, 238
of 240), so finders alone raise x̄ above the B = 1 values — the same reasoning that held for Luna (T-L4, p = 1/70).

## Readings stated in advance

| pattern | reading |
|---|---|
| T-SH does not hold, ranges overlap | For Haiku, rule names add nothing measurable over silence at this δ; its spread comes from evidence (entry 19). |
| T-SH holds | Names add something; read with x̄_nf and finders (names may move tests rather than rules, as for Luna and gpt-oss-20b). |
| T-H4 holds, x̄_nf ≈ 0 | Four tests let more cells find the error themselves; names still do not move cells without evidence. |
| T-H4 holds, x̄_nf clearly above 0 | With many finders naming H_T, cells without evidence follow; read with the majority step. |
| T-H4 does not hold | Too few finders even with four tests, or finders do not reach H_T (per-finder table). |
| x̄_nf in silent clearly above 0 | Some cells reach H_T with no evidence or message; that rate is the floor. |

Also reported, no test: x̄_nf, finders (independent/following), tests on the region split by whether a neighbour
named H_T in the previous generation (test guidance, as in entries 17–18), the per-finder table of
`AMENDMENT_QX3_B4.md` (rule two generations after the first own counterexample; U-refuting own result), the
majority-step counts on the rule-only runs.

## Money (internal; no dollar figures on the page)

Dry build: input 4,365.5 (silent) and 4,486 (B 4/B 1) tokens per call, output 490 (Stage 2A mean); 28,800 calls
≈ $19.86. **Hard stop $29.80**; stop + $14.19 spent ≈ $44.0, under $72.

## Gates and outputs

As in Stage 2A (format gate per run; API retry once; > 2 % failed calls stops the run). Packages per part (S; each
B1/B4 world pair) with traces, calls with usage, output tokens and USD, no reasoning text; readouts with T-SH and
T-H4. A page entry with the runs in the run viewer after the reviewer's recheck.

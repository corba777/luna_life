# Amendment — Claude Haiku 5.5, signal-mark probe on its "Who Speaks First" populations

**Status:** draft v2 (2026-11-26; v1 `e66e532b…` corrected after the dry build: detection threshold and battery signals), written by the reviewer for Artem. Artem, 2026-11-26 10:26–10:27: «Проба с ненулевой
меткой у P_e. — сколько будет стоить?», «Давай, пиши». Locked after the agent's dry build and the reviewer's review; no
call before the lock and Artem's go, logged verbatim. API only; it touches neither the GPU nor any waiter. Part of the
Haiku line under its ceiling ($25, Artem).

## Why

In Haiku's eight populations (`AMENDMENT_LIFE_HAIKU55.md`, Stage 3) 96 % of published messages carry signal 0, no run
forms a convention, and class-A cells take P_e in only six single cell-rounds. On gpt-oss-20b a non-zero mark on P_e
lines raised adoption (`AMENDMENT_SIGNAL_INTERVENTION.md`); on gpt-oss-120b what mattered was that the two rules carried
different numbers. Haiku's populations never produced such a mark, so the question is the reverse one: does a mark that
nobody in its population set move a Haiku cell toward P_e? This separates "Haiku reads only the share of rule names"
from "Haiku would read a mark if one existed".

## Design (only the signal numbers in the inbox change)

**Claude Haiku 5.5 · world 1 · re-asked cells from Stage 3, rounds 10–20 · lattice and `all` · rule names and signals
only · one fresh draw per item and arm.** Prompts, schema and decoding exactly as Stage 3 (Haiku Stage 0 envelope); no
reasoning stored.

- **Items.** A state (run, round t, cell) from the eight Stage-3 runs with: class A; rule at round t − 1 not P_e; at least
  one P_e line in the round-t inbox. Per topology, the 200 eligible items ranked first by
  `sha256("hk_sigmark|topology|run|round|cell")`; if fewer are eligible, all of them, and the count is stated in the dry
  build.
- **Arms (same items):**
  - `orig` — the inbox as stored;
  - `mark` — every P_e line carries signal 3; every other line carries 0;
  - `rand` — every line carries a number drawn uniformly from 0–7 (seed from the item hash).
- 3 arms × 2 topologies × 200 items = **1,200 calls**.

## Measure and tests

Share of answers naming P_e, per arm and topology. Contrasts `mark − orig` and `rand − orig`, per topology, paired on
items: one-sided exact sign test on discordant items (P_e in the edited arm and not in `orig`, against the reverse),
each at 1 − 0.05/4 = 98.75 %. **SM1** (`mark` raises adoption) and **SM2** (`rand` raises adoption), each scored on
both topologies.

## Prediction stated in advance, derived from measured data

**SM1 and SM2: not detected on either topology.** Derivation: in the battery a P_e minority never moved Haiku —
`all` shares 0.10–0.30: 0 of 120 calls on P_e (M88 = 0); one P_e line among silent ones: E8 = 0 — and the inboxes of
eligible items hold P_e at ≈ 0.25 (`all`) or at most 3 of 8 lines (lattice), inside that range. In Stage 3 the observed
rate is 4 of about 3,300 class-A cell-rounds on `all` in rounds 10–20 (0.001) and 0 on the lattice. With 200 items
the sign test at 98.75 % needs at least 7 discordant items, all in the edited arm's favour (0.035 in rate; at 200
discordant items, 117 of them); the dry build lists the threshold for every count. The battery's inboxes carried
non-zero numbers (1,156 of 1,160 prompts; digits 7, 0, 4, 1 most common), so the battery's M88 = 0 was measured with
marks present; whether a mark tied to P_e alone moves Haiku is what this probe adds. Stated risk: the battery's numbers
may not have been tied to P_e lines the way `mark` ties them.

## Readings stated in advance (per topology)

| mark | rand | reading |
|---|---|---|
| not detected | not detected | Haiku's response is carried by the rule names; a number on P_e lines does not move it at this precision. |
| detected | not detected | A mark tied to P_e moves Haiku: its populations lacked a convention, not the ability to read one. |
| detected | detected | Any non-zero numbers move it; the effect is not tied to P_e. |
| not detected | detected | Numbers in general, not a P_e mark, move it. |

## Money (chat and logs only)

Projection: 1,200 calls at Stage 3's measured cost per call; stop 1.5 ×. The dry build states the line's spend so far
and the start rule (spend so far + 1.5 × projection ≤ $25). The page and paper carry no dollar figures.

## Gates, dry build, outputs

Format gate as in Stage 3. Waiter with stdout and stderr in a log file. Dry build (CPU, no call): item counts and the
200 chosen per topology; for every item the rebuilt `orig` prompt equal to the stored Stage-3 request (sha or request
hash; mismatch count must be 0); the `mark` and `rand` prompts differing from `orig` only in signal digits (diff check);
the battery's inbox signal values (counts per digit); token counts, projection and start rule; the readout (SM1, SM2,
sign tests) run end to end on stub answers. Output: calls (usage, answer text), answers per arm, readout, a package with
SHA256SUMS in the same message as the finish. Nothing enters a page or the paper before the reviewer's recheck.
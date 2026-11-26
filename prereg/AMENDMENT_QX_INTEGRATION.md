# Amendment — QX evidence integration in isolation: two results from different sources, δ 1/64

**Status:** draft v4 (2026-11-26; v3 `92e9a9f4…` with two editorial points from a second ChatGPT review: INT2
readings, limits; v2 `8b8a10c9…` with the predictions fixed from the dry build `c3cccd66…`; v1 `40f1a754…`
clarified after a ChatGPT review: paired resampling, full consistent sets, provenance, name of the effect), written by
the reviewer for Artem. Artem, 2026-11-26 12:32, on the proposal that
followed a ChatGPT review of the page: «Давай, но и luna не забывай». Locked after the agent's dry build and the
reviewer's review; no call before the lock and Artem's go, logged verbatim.

## Why

Entry 24: with four tests per cell and shared results, Claude Haiku 5.5 populations at δ 1/64 reached H_T, and 129 of
the 189 cells that first held H_T had in memory both a received counterexample to H_F and their own result that the
unconditional substitution U gets wrong. That is an observation in populations, not a cause. At δ 1/64 neither result
alone singles out H_T: a counterexample fits U as well as H_T, and a U-refuting result fits H_F. Only together do they
leave H_T. This amendment fixes one cell, its rule and every line of its prompt, and changes only which two results it
holds and where each came from. It asks whether a model combines two results from different sources into the rule
neither result implies (Michal Valko's two pieces of evidence found by different agents).

## Design

Rendered by the QX-3 engine as in the isolation battery (`AMENDMENT_QX_ISOLATION_WORLDS_U3.md`: generation 6, B 1
spent, rule + chosen result, previous and published rule H_F, all eight neighbours named H_F in generation 5, the
first-slot neighbour carries one result and names H_F), with **δ 1/64**: the world files, catalog, examples and keys
of the four-tests worlds (entries 17, 20, 24). Cells: the same 20 per world as the isolation battery.

| world | H_F | U (= H_T at δ 1/8) | H_T (δ 1/64) | counterexample to H_F | U-refuting result |
|---:|---|---|---|---|---|
| 0 | K026 | K047 | K014 | `DGAA -> FHBB` | `DAAA -> EBBB` |
| 1 | K035 | K034 | K057 | `CAAC -> DBBE` | `AAAC -> BBBD` |
| 2 | K114 | K015 | K100 | `EAAC -> BBBD` | `EAAA -> FBBB` |
| 3 | K028 | K043 | K107 | `AEAD -> BFBC` | `AAAD -> BBBE` |

Counterexample: H_T and U give the output, H_F does not. U-refuting result: H_T and H_F give the output, U does not
(the reviewer's pre-check; repeated in the dry build with the full consistent sets). Neutral results `AAAA -> BBBB`
and `CAAA -> DBBB` fit all three rules in every world.

| condition | own result | received result (sender names H_F) |
|---|---|---|
| N control | `AAAA -> BBBB` | `CAAA -> DBBB` |
| A received counterexample only | `AAAA -> BBBB` | counterexample |
| B own U-refuting result only | U-refuting result | `CAAA -> DBBB` |
| C both: received counterexample, own U-refuting | U-refuting result | counterexample |
| D both, sources swapped | counterexample | U-refuting result |

Three draws. Per model 5 × 4 × 20 × 3 = **1,200 calls**. Models and decoding exactly as in the isolation battery for
each: Luna, Claude Haiku 5.5 (API, first); gpt-oss-20b, gpt-oss-120b, Qwen3.6-35B-A3B with the capped thinking budget
of `AMENDMENT_QX_ISOLATION_BUDGET.md` (GPU, after the 120b core runs). Open models' reasoning stored; closed models' not.

## Measures

Per model, world and condition, by cell (draws nested): shares naming H_T, U, H_F, other; *consistent* (a rule that
fits every result in the prompt); the result attached to the published message (counterexample, U-refuting, none).
The dry build lists, for every world and condition, the full set of catalog rules consistent with the prompt's
results. If C or D leave rules besides H_T, the readout reports *consistent* beside the H_T share, and a cell naming
such a rule is counted as consistent, not as an error.

## Tests (per model; pooled over the four worlds, 80 cells; 95 % paired cell bootstrap: resample cells within world
with replacement, each drawn cell carrying its answers in all five conditions, its three draws averaged within the
cell; 2,000 resamples, seed 0)

- **INT1 (integration):** H_T share in C minus the larger of the H_T shares in A and B (the larger one re-chosen in
  every resample). Holds if the interval's lower end is above 0.
- **INT2 (source), descriptive:** H_T share in D minus C, with its interval.

The effect is named the **evidence-integration advantage**. A positive INT1 shows that the two results together move
the cell to H_T more than either alone; it does not show which computation inside the model produces that.

## Predictions stated in advance, derived from measured data

**Claude Haiku 5.5: INT1 holds.** From its Stage-2F populations (δ 1/64, B 4, rule + chosen result, four worlds),
decisions of cells whose previous rule was H_F, by what their memory held (`int_derive.py`): received counterexample,
no U-refuting result: H_T 0.25, U 0.62, H_F 0.12 (n = 146); own U-refuting result only: H_F 1.00 (n = 2,784);
received counterexample with own U-refuting result: H_T 0.74, U 0.14, H_F 0.12 (n = 188). Expected C − max(A, B)
≈ +0.49. Stated risk: in the populations senders also named H_T or U; here the sender names H_F, which may lower A
and C alike.

**Luna, gpt-oss-20b, gpt-oss-120b:** the same table, the same code, from each model's stored δ 1/64 rule-plus-result
runs; INT1 "holds" if C − max(A, B) is above 0.10 with at least 30 decisions in each memory state, "uncertain"
otherwise. Fixed from the dry build (`runs/qx_integration/dry_build.json` `c3cccd66…`; gpt-oss-20b and Luna worlds 1–3
recomputed by the reviewer from the source traces, `int_derive2.py`):

| model (source runs, sha256 in the dry build) | A: H_T / U / H_F (n) | B: H_F (n) | C: H_T / U / H_F (n) | C − max(A, B) | INT1 |
|---|---|---|---|---:|---|
| Luna (entry 8: `qx3_luna_d64_B1_RE_r2`, `qx3w_luna_d64_B1_RE_w1–w3`) | 0.04 / 0.70 / 0.26 (50) | 1.00 (106) | 0.39 / 0.06 / 0.56 (18) | +0.35 | **uncertain** (C has 18 decisions) |
| gpt-oss-20b (entry 17: `qx3b4_20b_d64_B4_RE_w0–w3`) | 0.12 / 0.22 / 0.60 (83) | 1.00 (845) | 0.47 / 0.03 / 0.50 (38) | +0.35 | **holds** |
| gpt-oss-120b | — | — | — | — | computed by the same rule from its Part-B traces once rechecked, and fixed in a later version before any gpt-oss-120b call |

Provenance: every prediction comes only from population runs stored before this amendment; no isolation outcome of
this design exists before the lock.

**Qwen3.6: uncertain** (no δ 1/64 population run).

## Readings stated in advance (per model)

| pattern | reading |
|---|---|
| INT1 holds; A mostly U, B mostly H_F | The model combines a received counterexample with its own U-refuting result into the rule neither result implies: entry 24's mechanism shown with everything else fixed. |
| INT1 holds; D − C interval covers 0 | No effect of which result came from the neighbour is detected; equivalence is not established. |
| INT1 holds; D − C interval below 0 | The combination works better when the counterexample comes from the neighbour and the U-refuting result is the cell's own. |
| INT1 holds; D − C interval above 0 | The combination works better when the counterexample is the cell's own. |
| INT1 does not hold; C mostly U | Two results do not narrow the rule: the model takes the first rule that fits the counterexample and does not check it against its own result. |
| INT1 does not hold; C mostly H_F | The received counterexample is not taken when an own result is present. |

## Limits

- Four fixed worlds of one task family: the bootstrap resamples cells, not worlds, so a positive INT1 holds for these
  four worlds and is not an estimate for other tasks.
- One cell state (generation 6, rule H_F, all neighbours on H_F); other states are not tested.

## Money (chat and logs only)

Luna: 1,200 calls at its isolation cost per call (≈ $0.00035) ≈ $0.42, from the remaining Luna authorization.
Claude Haiku 5.5: ≈ $0.00075 per call ≈ $0.90, under the QX Haiku ceiling ($80; ≈ $5.9 left). Stop 1.5 × each; start
rule as before. Pages carry no dollar figures.

## Gates, dry build, outputs

Format gate as in the isolation battery. Waiters keep stdout and stderr in a log file. Dry build (CPU, no call): the
rendered prompts for all five conditions; a diff showing that conditions differ only in the two result slots (and D
only in their order of origin); for each world the consistent sets of N, A, B, C, D against the catalog (C and D must
contain H_T and not H_F or U); the prediction tables for Luna, gpt-oss-20b and gpt-oss-120b; token counts and cost
projections; the readout (INT1, INT2, descriptive tables) run end to end on stub answers. Outputs per model: calls
(usage; reasoning for open models), answers, readout, a package with SHA256SUMS in the same message as the finish.
Nothing enters the page before the reviewer's recheck; the entry comes with the cell grids in the isolation viewer.
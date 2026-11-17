# Amendment — QX-2 ladder, Nemotron with a thinking budget

**Status:** locked v2 (2026-11-17), written by the reviewer for Artem. v2 corrects the answer lengths
found in the dry build of v1. Dry build passed (no model call) and the reviewer's review. No call is made before
Artem's go, logged in the switch log with his words.

## Why

In the QX-2 ladder (`AMENDMENT_QX2_LADDER.md`, locked v1), NVIDIA Nemotron 3.5 Lightning 30B-A3B
failed the locked format gate on its first arm, `nemo_d64_B4_r1`, at the model card's
`max_tokens` 16,000. The gate counts a decision as bad if any of its calls is truncated. Five
decisions in the first 271 were bad. All five were truncations of the first draw inside the
reasoning, with no answer text; each retry gave a valid answer. That result stands and is reported
as it is. The ladder's other Nemotron arms did not start.

Artem decided (2026-11-17) to try Nemotron again with its reasoning length bounded. The pinned
engine supports this: with `--enable-strict-thinking` and a thinking budget, the server forces the
end-of-thinking sequence once the budget is used, and the JSON schema then constrains the answer.
This is a model-specific setting. Results are reported as **"Nemotron with a thinking budget of
15,000 tokens"**, a condition of this model, not as Nemotron at its card settings, and not as an
equal comparison with the other models. The prompt is the same as for every other model.

## The budget

**B_think = 15,000 tokens**, with `max_tokens` 16,000 as on the card. The number is derived from
the measured calls, not chosen by eye:

- In `nemo_d64_B4_r1`, 300 of 305 calls ended on their own. The longest reasoning among them was
  14,292 tokens. In the 20 smoke calls the longest was 11,683.
- An answer after the reasoning took 23–50 tokens in the 300 self-ended calls, and 27–43 in the
  smoke calls.
- A budget of 15,000 is above every reasoning length that ended on its own in the measured calls,
  so in that sample it changes only the five calls that ran to the cap. It leaves 1,000 tokens for
  the answer, twenty times the longest answer seen.

The budget therefore cuts runaway reasoning and, in the sample measured so far, nothing else.
Calls in later generations, which see counterexamples, may reason longer; the forced closes are
counted and reported (below).

## Engine and request

Unchanged from the ladder: the pinned image `lmsysorg/sglang@sha256:06441be3…` (v0.5.22), the
NVFP4 weights at revision `bee7596271d1495f6992ae224aefde4410e816b8`, `--reasoning-parser
nemotron_3`, the pinned chat template, temperature 1.0, top_p 0.95, `enable_thinking` true,
`max_tokens` 16,000, the strict QX-2 schema, reasoning stored for every call.

Changed, and only these:
- **Launch:** `--enable-strict-thinking`, and `SGLANG_MAX_THINK_TOKENS=15000` in the server
  environment. The environment value is what turns the token filter on for Nemotron, whose parser
  has no excluded think tokens.
- **Request:** `custom_params: {"thinking_budget": 15000}`, the same number, so the budget does
  not depend on the default.

Checked in the pinned image without a server (agent's report, 2026-11-17): a per-request integer
budget replaces the environment value; after the forced `</think>` the JSON schema constrains the
answer from its first token; a call that ends its reasoning before the budget is sampled unchanged.

## Runs

The four cells of the ladder, in the ladder's order, one run each, G = 12, under new names so that
no answer is shared with the stopped arm:

| order | arm | δ | B | calls |
|---:|---|---|---:|---:|
| 1 | `nemotb_d64_B4_r1` | 1/64 | 4 | 1,200 |
| 2 | `nemotb_d8_B4_r1` | 1/8 | 4 | 1,200 |
| 3 | `nemotb_d8_B1_r1` | 1/8 | 1 | 1,200 |
| 4 | `nemotb_d64_B1_r1` | 1/64 | 1 | 1,200 |

The stopped arm `nemo_d64_B4_r1` is kept as it is and is not reused.

**GPU time.** The stopped arm ran 305 calls in 117 minutes, 23 s of wall time per call. At that
rate the four arms take about 31 hours. **Queue:** after the QX-3 main phase on gpt-oss-20b,
before the QX-2 continuation and the Qwen temperature battery, unless Artem orders otherwise.

## Gates

- **Smoke check (first live step).** The ladder's 20 smoke prompts, plus the five prompts whose
  first draw was truncated in `nemo_d64_B4_r1`, at the same draw index. Pass if no call is
  truncated, at most 2 of 25 answers fail the schema, and the five former truncations end with a
  valid answer. Report each call's reasoning tokens and whether the budget forced the close.
- **Format gate:** as locked for QX-2: more than 4 fallbacks or truncations in the first 400
  decisions stops Nemotron's arms. It is unchanged; the budget makes a truncation unlikely but
  does not exempt it.
- **Forced closes:** counted for every call (a call whose reasoning reaches 15,000 tokens). No gate.
  In the readout, decisions that followed a forced close are listed with their answers.
- **GPU:** the usual precheck and monitor; manifest checked in precheck.

## Readout (descriptive)

As in the ladder: abandonment and recovery beside the scripted references, first refutation, test
descriptives and the δ-share, the message mix, refuting results shared, the finder breakdown, signal
use, calls and GPU time. Added: the distribution of reasoning tokens per arm and the number of
forced closes. One table puts Nemotron with the budget beside the other ladder models per cell,
with its label. No contrast and no p-value.

## Dry build (CPU, no model call)

1. The launch argv and environment differ from the ladder's Nemotron launch only in
   `--enable-strict-thinking` and `SGLANG_MAX_THINK_TOKENS=15000`.
2. The request body differs from the ladder's only in `custom_params`.
3. Prompt identity with the ladder's pinned generation-1 prompts.
4. Distinct cache keys for the four new arms and the 25 smoke calls.
5. The fake client runs the four arms through the engine, with every invariant asserted.
6. The five smoke prompts for the former truncations, with their draw indices.
7. GPU time at the measured rate.

## Outputs

Calls (final text, reasoning and usage), traces, the smoke report and the readout, in a recheck
package with SHA256SUMS. Nothing enters the QX page before the reviewer's recheck from raw data.

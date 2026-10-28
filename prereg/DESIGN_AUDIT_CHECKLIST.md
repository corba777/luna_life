# Design audit checklist — required before any task or amendment is locked

Every new task or amendment that runs calls (API or local) or fits a model passes this audit before
it is committed as locked. The audit is written into the task file as a section "Design audit", item
by item, with the evidence for each answer. A "no" or "not checked" blocks the lock.

Preferably the audit is done by a separate agent that has not seen how the design was drafted. It
checks what the file says, not what was meant.

## Why this exists

Four design errors in one day, all found by our own audits, all of one kind: conditions were
specified without checking that they cover the space on which the result is read.
- Parts 0b, 0c, D: rebuilt inboxes placed P_e lines as a top block; live inboxes interleave them.
- Part 0b: no empty-inbox control, so "completion from the prefix" had no baseline.
- Part G: two gates that could not both hold.
- Micromodel: the test support bounded rule types but not inbox length, so the adoption model was
  scored on inbox lengths it was never fitted on.

## The items

1. **Fidelity to live data.** For every constructed prompt: line order, signals, line count, header,
   slot sentence, memory line and generation are compared with real prompts of the same arm and
   round. Every difference is listed and justified, or removed.
2. **Coverage.** For every factor of a design and every feature of a model: the range in the
   fit or intervention set against the range in the set on which results are read. Anything outside
   the range is excluded from scoring in the locked text, or the design is extended to cover it.
3. **Controls.** Every effect has a baseline condition without the manipulation (empty inbox, zero
   signal, no prefix line, untouched state), inside the same design.
4. **Observability.** Every mechanism a prediction relies on is something the agent can see in its
   prompt. (Example: memory is one step, so a cell cannot see how long it has held a rule; an effect
   of holding time must be read as selection or state, not as memory, unless shown otherwise.)
5. **Gate consistency.** All gates are run on a dry build before the lock, and they pass together.
   Example of a gate checked on a dry build: P_e positions are set by the redo hash. Report, per
   condition, the number of inboxes whose P_e lines form a block starting at slot 1, against its
   expectation under uniform placement; the gate fails only if that number exceeds the 95%
   binomial upper bound.
6. **Statistical unit.** The unit of each test is stated; repeated calls on the same cell are not
   counted as independent without a cell-level test beside them.
7. **Pre-stated readings.** Each prediction states what its pass and its fail would mean, including
   the reading if the design itself turns out to be the cause.
8. **Chat-template date/time (from 2026-10-27).** For every future model: check whether its chat
   template injects a date or time (for example Harmony `strftime_now`, or any `Current date` /
   clock line). If it does, pin that value for the run as a standard gate, the same way gpt-oss-120b
   uses `runs/life_dr_gptoss/pinned/chat_template_date_20261022.jinja`. Do not leave a live clock in
   a multi-hour arm.
9. **Independent recheck before the paper (Artem’s go, 2026-10-27).** No result enters
   `PAPER_LIFE_DRAFT.md` until an independent recheck has reproduced it from raw data. For each
   readout that feeds the paper, the agent exports a recheck package: raw final-answer text per call
   with its key, selection, world and catalog definitions, the parser, and the readout for comparison
   only. The package has a sha256 list. The reviewer recomputes with separate code. The readout
   records the recheck date and any differences. Gate status is printed per condition before any
   verdict and applies to every test that uses that condition.
10. **Simulator reference sample size (from 2026-10-27).** Every simulator-derived reference value
    written into an amendment (tip rates, dry-build bands, expected shares used as locked thresholds)
    uses at least **2,000** Monte Carlo replicates and reports the Monte Carlo SE (or an equivalent
    binomial/Wilson interval at that *n*). A 200-replicate seed-0 draw is not enough to lock a
    reference rate.
11. **Serve context vs prompt set (from 2026-10-28).** Every dry build that prepares local model
    calls checks, for each model’s full prompt set and that model’s own tokenizer (chat-template
    count), that `I_max + max_tokens ≤` the intended server `--context-length`. Fail the dry build
    if any prompt overflows. Contagion Qwen Part A’s HTTP 400 at context 36864
    (`I_max + 32768 > 36864` on n=88 high-k) is the motivating case; same class as
    `ADDENDUM_PANEL_FULL_RUNS_CONTEXT.md`.

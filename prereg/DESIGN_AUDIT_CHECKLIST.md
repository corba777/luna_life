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
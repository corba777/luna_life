# Amendment — filter form in the calibration choice model

**Parent:** `TASK_LIFE_CALIBRATION.md`  
**Status:** locked before any Part 1–3 number.  
**Unchanged:** D1–D3 and R1–R4. Part 1 events stay as locked: k is counted on the inbox the cell saw.

## Why

`TASK_LIFE_PHONE.md` specified the phone check as Da-r, and as removal before the cell sees the inbox. The runs differ.

- **Da-r** is a marking filter. Every delivered Moore message stays in the prompt. The engine appends ✓ or ✗ for the cell's checked example. An inconsistent rule is shown. It is not removed from the choice set.
- **R8c and Allc** are removal filters. A message that fails the check is dropped before the prompt. R8c leaves an empty slot. Allc omits the slot. The prompt has no ✓/✗. The cell does not see the inconsistent rule.
- **Ca-r, R8, All** have neither mark nor removal.

For a non-source cell the check predicate is the same in Da-r and in the phone check: one private example. The difference is what the prompt does with a failure.

## Part 2

Model each arm's filter as it ran.

Ca-r is unchanged: candidates are the cell's own rule, every rule in the Moore inbox, and one "other" option. No mark term.

Da-r does not delete inconsistent rules before the logit. The candidate set is the inbox the cell saw, including rules marked ✗. Two mark terms:

  U(ρ) = β₁·log(1 + count(ρ)) + β₂·share(ρ) + β₃·[ρ is own] + β₄·[ρ is own]·[own feedback wrong]
         + β₅·log prior(ρ) + β₆·[ρ marked ✓] + β₇·[ρ marked ✗]

Both indicators are 0 on Ca-r, where the prompt has no marks. With one term, a ✗ rule in Da-r would be silently set equal to an unmarked rule in Ca-r. Report β₆ and β₇ with standard errors. The joint Ca-r / Da-r fit is the same β, with the mark terms present only on Da-r. Alone-fits and the likelihood-ratio test on β stay as in Part 2.

No Phone data enters this fit.

## Part 3

The retrodiction uses the filter the phone arm actually ran. R8 and All have no filter. An empty R8c slot is not a candidate. The pass rules R1–R4 are unchanged.

R8c and Allc remove inconsistent rules. Applying the Da-r–fitted model to them treats removal as the limit β₇ → −∞. This is an assumption. If R1–R4 fail only in the check arms, this transfer is the first suspect, and the readout says so.

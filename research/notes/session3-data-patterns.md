# Session 3: Data Pattern Analysis

Date: 2026-03-19

## Distribution
- Normal: 1000 problems (500 TRUE, 500 FALSE = 50/50)
- Hard: 200 problems (74 TRUE=37%, 126 FALSE=63%)

## The "Lone Variable Absent" Rule — A PERFECT RULE

For Eq1 of form `v = T(...)` where v does NOT appear in T:

| Subset | TRUE | FALSE | Accuracy |
|--------|------|-------|----------|
| Normal | 243/243 | 0/0 | **100%** |
| Hard | 0 | 0 | N/A (no such cases in hard) |

This is a zero-false-positive rule on normal problems. 243/500 = **48.6%** of all normal TRUE
problems are solved perfectly by this single rule.

## The "Lone Variable Present" Pattern

For Eq1 of form `v = T(v, ...)` where v appears in T:

| Subset | TRUE | FALSE |
|--------|------|-------|
| Normal | 216/483 = 45% | 267/483 = 55% |
| Hard | 63/140 = 45% | 77/140 = 55% |

This is where real reasoning is needed. Near coin-flip baseline.

## "No Lone Variable" Pattern

Eq1 has no lone variable (both sides are composite, e.g. `x*y = ...`):

| Subset | TRUE | FALSE |
|--------|------|-------|
| Normal | 41 TRUE, 233 FALSE = 15% TRUE |
| Hard | 11/60 = 18% TRUE |

Lean FALSE here is correct most of the time.

## Implications for Cheatsheet

1. **"Lone var absent" is the #1 rule** — encode it crystal clear with examples.
   It alone gives 243/1000 correct answers for free (on normal).

2. **"Lone var present" is the hard part** — this is where models disagree.
   Need heuristics: substitution, synchronization, counterexample testing.

3. **"No lone var" → lean FALSE** — 85% of the time correct.

4. **Hard problems deliberately exclude "lone var absent"** — they test the harder cases.
   The competition likely weights hard more or uses similarly-filtered test sets.

## Strategy

The cheatsheet should:
- State the "lone var absent = TRUE always" rule extremely clearly
- Give precise heuristics for "lone var present" (the 45/55 split)
- Teach counterexample checking (LZ/RZ) for "no lone var" and "lone var present"
- NOT over-assert rules that would cause false positives on the harder cases

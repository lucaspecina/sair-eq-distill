# Sudoku Analogy — Elimination and Forced Moves

Date: 2026-03-19

## The analogy

Sudoku solving strategies map to our cheatsheet strategies:

### Forced moves (HIGH confidence, decide immediately):
- Eq1 == Eq2 → TRUE
- Eq2 == "x = x" → TRUE
- Eq1 forces x = y → TRUE
- Substitution match found → TRUE
- Counterexample found → FALSE

### Eliminations (MEDIUM confidence, narrow options):
- Eq2 has more variables → lean FALSE
- Eq1 has more free RHS vars → lean TRUE
- Eq1 forces constant/projection → likely TRUE

### Heuristics (LOW confidence, tiebreaker):
- Default FALSE (63% base rate)
- Structure similarity → lean TRUE
- Complexity difference → lean toward more restrictive

## How v6 uses this (implicitly):
1. Fast checks = forced moves (immediate decisions)
2. Substitution = highest-confidence forced move
3. Forced operations = medium-confidence eliminations
4. Counterexample = forced move (definitive FALSE)
5. Default FALSE = lowest-confidence heuristic

## Possible improvement:
Make the CONFIDENCE of each step explicit in the cheatsheet.
"Steps 1-2 give definitive answers. Steps 3-4 are strong signals.
Step 5 is a last resort."

But v6 already does this naturally through ordering.
Not clear this would help — adding meta-commentary increases text
and we know that hurts accuracy.

## Status: documented as theoretical insight, no actionable change.

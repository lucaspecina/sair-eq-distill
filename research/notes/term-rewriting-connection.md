# Term Rewriting Systems — Connection to our Approach

Date: 2026-03-19

## The connection

v6's substitution-based approach IS an informal term rewriting system:
- v6 "rewrite rules": the equation Eq1 oriented as a rule (LHS1 → RHS1)
- v6 "rewriting": substitute variables in Eq1 to derive Eq2
- v6 "normal form": simplify until you either match Eq2 or get stuck
- Birkhoff completeness = the TRS approach is complete for equational theories

## What formal TRS adds

1. **Orientation**: orient equation as LHS→RHS (not bidirectional)
2. **Termination ordering**: ensure rewriting terminates (no infinite loops)
3. **Confluence**: the order of applying rules doesn't matter
4. **Normal forms**: a canonical representative for each equivalence class

## Could we teach this to the model?

Partially. The model can:
- Orient equations (always rewrite LHS→RHS or vice versa)
- Apply rewrite steps (substitution, which it already does)
- Check if two terms match after rewriting

The model CAN'T:
- Guarantee termination (might loop)
- Systematically try all orderings
- Compute completions (Knuth-Bendix is complex)

## Practical insight

v6 already captures the essence of TRS in natural language.
Making it MORE formal (like v8 pseudocode) didn't help — the model
works better with informal instructions than formal algorithms.

The takeaway: v6 IS the optimal "informal TRS" for this problem.
Formalizing it further hurts performance (lost in formalism).

## One useful idea from TRS

**Orientation strategy**: the model should always try to rewrite from
the MORE COMPLEX side to the LESS COMPLEX side. This is a common
TRS heuristic (reduce complexity) that v6 implicitly uses but doesn't
explicitly state. Could be a micro-improvement.

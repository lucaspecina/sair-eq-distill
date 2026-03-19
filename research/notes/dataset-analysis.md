# Dataset Analysis — First Pass

Date: 2026-03-18

## Equation Structure

4694 equations total. Format: `LHS = RHS` using variables x,y,z,w,u,v and operation ◇.

### Key stats:
- **91.3%** of equations have exactly 4 operations (the maximum)
- **66.9%** have a single variable as LHS (e.g., `x = ...`)
- Variable counts: mostly 3 vars (44.5%) or 4 vars (30.8%)
- Max nesting depth: 0-3 levels
- Only 2 equations with 0 operations: `x = x` (tautology) and `x = y` (collapse)

### Finding: normal and hard problems are syntactically identical
Normal problems: avg 3.9 ops, 25.9 chars
Hard problems: avg 3.8-4.0 ops, 25.2-26.2 chars

**The difficulty is NOT in equation complexity. It's in the structural relationship.**

## Implication Matrix

4694 × 4694 matrix. Values: 3 (true), -3 (false), 4 (hard-true), -4 (hard-false).

### Distribution:
- True (3): 8,167,622 (37.1%)
- False (-3): 13,268,432 (60.2%)
- Hard-true (4): 10,657 (0.05%)
- Hard-false (-4): 586,925 (2.7%)

**~63% of pairs are FALSE. A default "False" heuristic gets 63% accuracy.**

### CRITICAL FINDING: Transitivity is 100%

Tested 1206 random transitive triples (A→B and B→C). In ALL cases A→C.
This means **implication is a preorder** (reflexive + transitive).
With equivalence classes, it's a **partial order on equivalence classes**.

This is a HUGE structural constraint. It means:
- If we know the partial order on classes, we know ALL implications
- The graph has NO cycles (except within equivalence classes)
- Reachability in the quotient DAG = the answer to any question

### Equivalence Classes

1415 total classes, 270 non-trivial (size > 1).

Top classes by size:
| Size | Example equations |
|------|-------------------|
| 1496 | x = y, x = y ◇ y, x = y ◇ z (all "collapse" equations) |
| 419 | x ◇ y = z ◇ w (all "constant operation" equations) |
| 112 | x = y ◇ (x ◇ x) variants |
| 112 | x = (x ◇ x) ◇ y variants |
| 76 | x = y ◇ (x ◇ (x ◇ x)) variants |

The biggest class (1496 equations, 31.9%) is all equations equivalent to x = y.
These are the "maximally restrictive" — they force all elements to be equal.

### Per-equation stats
- Most powerful (implies the most): Eq 2 (x = y) → implies ALL 4694
- Eq 1 (x = x) → implies only itself (tautology, weakest)
- Most implied: Eq 1 (x = x) → implied by all 4694

### Hard problems
- Hard-true: 10,657 (very rare — only 0.13% of true implications are hard)
- Hard-false: 586,925 (8.7% of false implications are hard)
- ALL equations participate in hard problems — not a subset issue

## Isomorphisms — this is a REACHABILITY problem

The question "does A imply B?" is exactly "is B reachable from A in the
implication DAG?" This connects to:

1. **Graph reachability / transitive closure**: well-studied problem. Can we
   encode the DAG structure compactly in 10KB?
2. **Partial order compression**: the quotient of equivalence classes forms a
   DAG. How many nodes does this DAG have? (1415). Can we describe it?
3. **Chain decomposition / antichain structure**: Dilworth's theorem — what's
   the minimum number of chains that cover the partial order?

## Open questions for next analysis
- [ ] What does the quotient DAG (1415 nodes) look like?
- [ ] Can we identify features that predict reachability in the DAG?
- [ ] What's the relationship between equation syntax and position in the DAG?
- [ ] Can we describe the partial order with rules rather than enumeration?
- [ ] What percentage of problems can a simple "syntactic substitution" rule solve?

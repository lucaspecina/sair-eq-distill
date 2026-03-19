# ETP Hard Implication Techniques

Date: 2026-03-19

## From the ETP paper (arxiv 2512.07087)

### Standard techniques (resolve 99.99% of implications):
1. Brute-force search of small finite magmas (size 2-4)
2. Vampire prover (saturation-based + finite model building)

### Advanced techniques (for the last ~1000 cases):
1. **Greedy table construction**: fill the multiplication table iteratively,
   choosing values that satisfy Eq1 while trying to violate Eq2
2. **Translation-invariant models**: models on groups where x*y = f(y-x)
3. **Twisting semigroups**: algebraic technique using size comparison
4. **Magma modification**: take an existing magma, modify few entries
5. **Ad hoc**: infinite trees, polynomial rings, prime factorization models

### For the very hardest (infinite magma required):
- Graph-theoretic interpretations
- Functional equation analysis
- "The hardest case took several months and 4000+ lines of Lean code"

## Applicability to our cheatsheet

### What could work:
- **Greedy construction** (simplified): "Fill the table row by row satisfying
  Eq1, then check Eq2." This is too complex for a small model to do reliably,
  but the CONCEPT (try to build a counterexample constructively) could help.
- **Small magma check** already in v6 (2-element magmas)
- **3-element magmas** would catch more cases but the model can't reliably
  check 27 operation tables mentally

### What's too complex:
- Translation-invariant models
- Twisting semigroups
- Infinite constructions
- Anything requiring >10 mental computation steps

### KEY INSIGHT: the hard cases in the competition are NOT the same as
the hard cases in the ETP. The ETP hard cases require infinite magmas.
The competition hard cases are selected from the 22M resolved implications —
they're hard for LLMs, not hard for mathematicians/provers.

The competition's "hard" problems are ones where the answer is known but
syntactic heuristics don't work. They still have finite counterexamples
or finite substitution proofs — they're just less obvious.

This means the strategies should focus on:
1. MORE CREATIVE substitution attempts (not giving up too easily)
2. Checking MORE small magmas (not just 2 tables)
3. Recognizing when equations force specific operation types

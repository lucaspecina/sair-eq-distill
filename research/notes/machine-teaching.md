# Machine Teaching — Theoretical Framework for Cheatsheet Design

Date: 2026-03-19

## The connection

Our problem is a machine teaching problem:
- Student: small LLM
- Concept: the 22M implication function
- Teaching budget: 10KB text
- Objective: maximize student's accuracy

## Key concepts from machine teaching

### Teaching dimension
The minimum number of examples/rules needed to teach a concept.
For normal problems, v6 shows the teaching dimension is LOW —
a few rules cover 96.7% accuracy.

### Idealization
"Limited-capacity learners benefit from lower variability in the
training sets" — simplified, idealized presentations work better.
This explains why v6 (simplified) beats v5 (comprehensive).

### One-shot machine teaching
"Costs very few examples to converge faster." Our cheatsheet IS a
one-shot teaching set — the model gets ONE chance to read it.

## Implications for cheatsheet design

1. **Fewer, clearer rules >> many detailed rules** (confirmed empirically)
2. The optimal teaching set focuses on BOUNDARY cases, not typical cases
3. For the model, the "boundary" between TRUE and FALSE is:
   - Can the implication be proved by substitution?
   - Does Eq1 force a trivial operation?
4. Teaching the model to SEARCH (try substitutions) is more valuable
   than teaching it FACTS about specific equations

## Research direction
Can we formalize the "teaching dimension" of the implication function
for a specific LLM? This would give us the theoretical limit of
what 10KB can achieve.

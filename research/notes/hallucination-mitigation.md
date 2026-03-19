# Hallucination Mitigation Ideas for Hard Problems

Date: 2026-03-19

## The problem

On hard FALSE problems, mini fabricates proofs 70.4% of the time.
Common pattern: "Equation 1 forces x*y = y" → followed by hallucinated steps.

## Ideas to mitigate (ranked by feasibility)

### 1. Step count heuristic (LOW risk)
"If your proof requires more than 3 substitution steps to reach the
conclusion, verify each step by writing out the full term on both sides."

Risk: might discourage some correct multi-step proofs on normal.
Expected impact: moderate — long proofs are more likely to be wrong.

### 2. Projection verification (MEDIUM risk)
"If you conclude that the operation is right projection (x*y=y) or
left projection (x*y=x), verify by explicitly showing how Eq1 gives
e*x = x for a SPECIFIC element e, then show EVERY element behaves as e."

Risk: adds ~50 bytes, might confuse on simple cases.
Expected impact: could catch many fabricated projection proofs.

### 3. "Red flag" patterns (LOW risk)
"Red flags that your proof might be wrong:
- Using the word 'clearly' or 'obviously' to skip steps
- Claiming Eq1 'forces' something without explicit substitution
- Arriving at a very strong conclusion (like x=y) from a weak-looking Eq1"

Risk: minimal — just awareness, no change to procedure.
Expected impact: uncertain — model might not act on warnings.

### 4. Two-phase approach (MEDIUM risk)
"Phase 1: Try to prove TRUE (substitution). Stop after 2 minutes.
Phase 2: Try to prove FALSE (counterexample). If neither works, FALSE."

Risk: the "2 minutes" concept is weird for an LLM.
Expected impact: could balance the TRUE/FALSE attempt ratio.

### 5. Confidence calibration (HIGH risk)
"Rate your confidence 1-10 before giving your verdict.
If confidence < 7, default to FALSE."

Risk: adds complexity, might change behavior unpredictably.
Expected impact: uncertain — models are bad at self-calibration.

## Assessment

None of these are likely to produce the same dramatic improvement as
v6 did over v0 (+25 points on normal). The hallucination problem is
FUNDAMENTAL to the model architecture, not a knowledge gap.

The best strategy remains: maximize normal accuracy (v6) and accept
modest hard accuracy as the cost. The 5:1 ratio of normal:hard makes
this the right trade-off.

## For the evolutionary approach (OpenEvolve):

These mitigation ideas are exactly what OpenEvolve could test:
generate 20 variants of v6 with different mitigation wordings,
evaluate each, select the best. This is where evolution shines —
testing subtle wording changes that humans can't easily reason about.

# Creative Approaches — Ideas to Explore

Date: 2026-03-19

## Approach 1: Compression with Noisy Decoder

Our problem: compress 22M bits into 10KB text. The decoder (LLM) is noisy.

Isomorphism with **rate-distortion theory**:
- Source: 22M implication results
- Channel: 10KB text → LLM → TRUE/FALSE
- Distortion: classification error rate

Questions:
- What's the theoretical minimum error rate for 10KB budget?
- Are we close to it? (v6 at 96.7% on normal ≈ 3.3% error)
- Can we estimate the "channel capacity" of a 10KB → LLM decoder?

## Approach 2: Error-Correcting Codes for Rules

Instead of trying to get every prediction right, design rules that are
"robust to model interpretation errors".

Example: "If Eq1 has more variables → TRUE" is a simple rule.
Even if the model misapplies it sometimes, the base rate helps.

A set of rules is like a "code" — we want rules that are:
- Individually noisy but collectively accurate
- Diverse (cover different cases)
- Redundant enough that if one rule fails, others compensate

This is related to **ensemble methods** in ML.

## Approach 3: Negative Space

Instead of listing when to say TRUE, list when to say FALSE.
Since FALSE is the majority class (63%), if we can precisely identify
ALL the FALSE cases, everything else is TRUE.

FALSE indicators from our analysis:
1. Eq2 has more variables than Eq1
2. Eq1 has low restrictiveness (satisfied by many magmas)
3. Eq2 has high restrictiveness (satisfied by few magmas) — reversed direction
4. Counterexample found in 2-element magma

If NONE of these apply → lean TRUE.

This is the inverse of what v6 does (v6 teaches TRUE-seeking).
Could complement v6 with a "FALSE-seeking" section?

## Approach 4: Teach the Model to be a Term Rewrite System

The model is essentially a text-processing engine. Equational reasoning IS
text rewriting (by Birkhoff). Can we frame the cheatsheet as a "rewrite
system" that the model can follow mechanically?

Rules:
- "x = A" means "replace x with A everywhere"
- "A = B" means "replace A with B or B with A"
- "Apply Rule N" means "use equation N to rewrite"

This is closer to how Vampire and Prover9 work — systematic rewriting.

## Approach 5: Meta-Learning from the Benchmark

We have 25 models × 200 problems × 3 repeats = 15,000 responses.
Can we find the "consensus" among models?

If most models agree on a problem → the answer is clear.
If models disagree → the problem is genuinely hard.

We could include in the cheatsheet: "For problems where models typically
disagree, look for [specific patterns]."

## Approach 6: Curriculum-Based Cheatsheet

Instead of one monolithic cheatsheet, design it as a "curriculum":
1. First, teach the simplest concept (reflexivity, tautology)
2. Then build on it (substitution)
3. Then harder concepts (forced operations, counterexamples)

The model processes text sequentially — curriculum ordering might help.

## Which to try next?

Priority based on expected impact vs effort:
1. Approach 3 (negative space) — could combine with v6 easily
2. Approach 4 (term rewrite) — aligns with Birkhoff, testable
3. Approach 5 (meta-learning from benchmark) — data is available
4. Approach 6 (curriculum) — v6 already does this somewhat

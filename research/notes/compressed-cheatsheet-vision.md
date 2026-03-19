# Vision: Compressed Mathematical Knowledge Cheatsheet

Date: 2026-03-19

## The insight

Current cheatsheet (v6) = behavioral tutorial ("try substitution", "be concise")
Winning cheatsheet = compressed mathematical knowledge base

The model already knows HOW to reason (93% on normal without help).
What it needs is WHAT to know — patterns, rules, shortcuts from the 22M dataset.

## Target format

```
[Header: 2-3 lines explaining how to read the rules below]
[Dense compressed rules with mathematical patterns]
```

### Example of target density:

```
HOW TO USE: Apply rules top-down. First match = verdict.
Eq1 implies Eq2 over magmas (set + binary op *, NO axioms).

== INSTANT VERDICTS ==
EQ1==EQ2 → T | EQ2="x=x" → T | EQ1 forces x=y → T

== STRUCTURAL SIGNALS ==
LHS1=single_var & depth(RHS1)>2 & vars⊆ → T[0.92]
rhs_only_vars(EQ1) > rhs_only_vars(EQ2)+1 → T[0.80]
no_shared_vars(EQ1_sides) → constant_op → T[0.90]
vars(EQ2) ⊃ vars(EQ1) → F[0.75]

== SUBSTITUTION (if no structural match) ==
Try y:=x, y:=x*z, z:=x*x. Apply EQ1 repeatedly.
NOT associative! Never rewrite (a*b)*c as a*(b*c).

== COUNTEREXAMPLE MAGMAS ==
{0,1} [0,0,0,1]: 3.5% of eqs | [1,0,0,0]: 2.9%
Satisfies EQ1 but not EQ2? → F

== DEFAULT: F (63% base rate) ==
```

~600 bytes of dense information. Leaves 9.4KB for more patterns.

## What to encode in the remaining 9.4KB

### Tier 1: Structural decision rules (~500 bytes)
- Operation count asymmetry rules
- Depth comparison rules
- Variable distribution rules
- LHS/RHS symmetry patterns

### Tier 2: Common equation class signatures (~2KB)
- The x=y equivalence class (1496 equations, 31.9%) — signs to detect
- Constant operation signatures
- Projection operation signatures
- Idempotent signatures

### Tier 3: Substitution recipe library (~2KB)
- For "x = f(y,...)" forms: specific substitution sequences that work
- For "x*y = g(...)" forms: different strategy
- Common multi-step patterns (substitute → apply → substitute again)

### Tier 4: Counterexample library (~1KB)
- All 16 two-element magma tables with which equations they satisfy
- 3-element magmas for harder problems
- Quick check patterns

### Tier 5: Confidence calibration (~500 bytes)
- Bayesian-style rules: "if structural signal + substitution attempt fails → F with high confidence"
- Edge cases and when to override defaults

## The key constraint

Adding content to v6 historically HURT accuracy. But v6 was adding PROSE.
The hypothesis: adding COMPRESSED MATHEMATICAL RULES (not prose) will help
because it gives the model actual information to work with, not more
instructions to follow.

This needs to be tested. The format itself is the experiment.

## Automation requirement

Manual iteration (write variant → eval → analyze → repeat) is too slow.
Need OpenEvolve-style loop:
1. Define building blocks (the rules above)
2. Program generates combinations/variants
3. Automated eval ranks them
4. Selection + mutation
5. Repeat

## Refined vision (from user discussion)

The cheatsheet has TWO parts:
1. **Decoder**: explains the vocabulary/notation used below. Not generic intro —
   specifically teaches how to USE the compressed content that follows.
2. **Payload**: dense compressed abstract rules and patterns. NOT explicit per-case
   instructions but GENERAL PRINCIPLES that apply across many equation types.

Key: rules should be ABSTRACT and GENERAL, not specific to individual cases.
"More restrictive equations imply less restrictive ones" > "if var_count(EQ1) > var_count(EQ2) then TRUE"

## Evolutionary optimization of tokens

The cheatsheet tokens ARE the parameters. This is a discrete optimization problem.

### Relevant frameworks:
- **AlphaEvolve** (DeepMind, May 2025): evolutionary coding agent, LLM generates
  variants, evaluator scores them, population evolves. 75% SOTA on math problems.
  https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- **EvoPrompt** (ICLR 2024): treats prompts as discrete optimization targets.
  GA + Differential Evolution. LLMs = mutation operators. +25% on BBH.
  https://arxiv.org/abs/2309.08532
- **OpenEvolve** (open source AlphaEvolve): +23% on HotpotQA.
  https://github.com/algorithmicsuperintelligence/openevolve
- **ShinkaEvolve** (Sakana AI): more sample-efficient than AlphaEvolve.
  Bandit-based LLM ensemble + novelty rejection.
  https://github.com/SakanaAI/ShinkaEvolve

### Our setup maps perfectly:
- **Program to evolve** = cheatsheet text (≤10KB)
- **Fitness function** = eval_robust.py (accuracy on normal+hard, multi-model)
- **Mutation operators** = LLM generates variants (rephrase, compress, add/remove rules)
- **Population** = pool of cheatsheet variants
- **Selection** = keep top-K by fitness score

### What to evolve:
1. The decoder section (vocabulary, notation, reading instructions)
2. The payload content (which rules, how compressed, what notation)
3. The balance between sections
4. The level of abstraction (specific rules vs general principles)

### Critical: need robust eval FIRST
Evolutionary optimization on a noisy fitness function = Goodharting noise.
Must use large enough sample (200+ problems) and multiple models.

## Status: vision refined, evolutionary approach researched, ready to implement

# Codex Strategy Review — Session 2

Date: 2026-03-19

## Context
Asked Codex to critically review our approach after overnight autoresearch session.

## Key findings from Codex

### 1. The cheatsheet is a PROGRAM, not a database
- More text = more branches, more interference, more artificial bias
- In already-good models, long prompts OVERWRITE useful priors
- "Unused budget" is not waste — it's restraint
- v6 wins not because of what it says, but because of what it DOESN'T say

### 2. We're Goodharting our proxy
- 30 problems, fixed seed=42, 1 model = reading noise as law
- Must fix eval BEFORE any optimization
- Required: normal+hard mix, multiple seeds, 2+ models, holdout

### 3. Anti-hallucination: surgical, not verbose
- One audit line: "Only say TRUE if you can write explicit substitution chain"
- Too strict → kills good TRUEs on normal
- Fundamental model limitation — prompt can mitigate, not fix

### 4. Evolutionary optimization: NOT YET
- Micro-mutating v6 on bad eval = selecting lucky prompts, not better ones
- Order: (1) fix eval → (2) test format families → (3) micro-mutations
- Format families to test: natural language, decision-list, mini-DSL, rewrite-DSL

### 5. Cross-model robustness is critical
- Competition uses UNKNOWN model mix
- Cryptic encodings: risky — may work on GPT, break on open-source
- Semi-cryptic OK (IF/THEN lists), fully opaque NOT OK (lookup tables)

### 6. Risks we're underestimating
- v6 may be local optimum of our proxy, not real benchmark
- 63% FALSE base rate may be overfit to public set
- Improving hard can hurt normal (net negative)

## Action items from this review
1. ✅ Created eval/eval_robust.py — mixes normal+hard, random seeds, per-difficulty breakdown
2. [ ] Run robust eval on v6 to get real baseline
3. [ ] Test v6 on SAIR playground (the only real test)
4. [ ] Try ONE variant: v6 + 1 proof-audit line
5. [ ] Try ONE format family: decision-list or mini-DSL
6. [ ] Do NOT fill the 7.3KB budget without evidence it helps

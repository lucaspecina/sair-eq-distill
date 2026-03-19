# Evolutionary Cheatsheet Optimization Strategy

Date: 2026-03-18

## The challenge with LLM-based evaluation

Each evaluation costs:
- 30 problems × 2 models × ~30s = ~30 minutes
- Plus API costs (~$0.01-0.05 per eval)
- For 50 iterations of OpenEvolve = 25 hours + $2.50

This is too slow for fast evolution. We need cheaper evaluation.

## Proposed: Cascade evaluation

### Stage 1: Static analysis (free, instant)
Analyze the cheatsheet TEXT without running any LLM:
- Does it mention key techniques? (substitution, left identity, projection)
- Does it include variable analysis rules?
- Is it within 10KB?
- Does it have clear structure (numbered steps, decision tree)?
- Score: 0-100 based on feature presence

### Stage 2: Proxy model (cheap, fast)
Run the cheatsheet against our multi-feature predictor:
- The predictor achieves 85.4% on normal problems without any LLM
- If the cheatsheet's rules MATCH the predictor's logic → good sign
- Alternatively: use a very cheap/fast model (gpt-4.1-nano?) for quick check

### Stage 3: Full LLM evaluation (expensive, definitive)
Only for the top candidates from Stage 1+2:
- Run against gpt-5-nano + gpt-5-mini with full reasoning tokens
- This is the ground truth metric

### Cascade flow:
```
Population of N cheatsheets
    │
    ├─ Stage 1: static analysis → filter to top N/2
    │
    ├─ Stage 2: proxy eval → filter to top N/4
    │
    └─ Stage 3: full LLM eval → select best
```

## Alternative: LLM-as-judge for cheatsheet quality

Instead of running problems, use a strong model to RATE the cheatsheet:
"Given this cheatsheet, would a small model be able to solve equational
implication problems? Rate quality on 1-10 and explain weaknesses."

This is faster (~1 API call vs 60) but less accurate.

## What to implement first

1. **Static quality scorer** (Stage 1) — can be built now
2. **OpenEvolve integration** with static scorer — fast iteration
3. **Periodic LLM validation** — every 10 iterations
4. Compare evolved cheatsheet vs hand-crafted v4

## Cost estimate

With cascade:
- 50 iterations × (N/4 Stage 3 evals) = ~12 full evals = ~6 hours + $0.60
- Much more manageable than 25 hours

## Connection to Track 3 (modular cheatsheet)

If we modularize the cheatsheet, each module can be evolved independently:
- Module A: variable analysis rules
- Module B: proof techniques
- Module C: counterexample strategy
- Module D: decision tree

OpenEvolve can evolve ONE module at a time while keeping others fixed.
This reduces search space dramatically.

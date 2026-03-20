# Session 3 Synthesis — Evolutionary Optimizer & Data Analysis

Date: 2026-03-20

## What We Built
1. **Evolutionary optimizer v1** (evolve_cheatsheet.py) — basic mutation with gpt-5.4
2. **Evolutionary optimizer v2** (evolve_v2.py) — crossover mutations, structured errors, statistical context, configurable models
3. **Data-derived insights** — perfect rules from problem analysis
4. **Multi-model testing infrastructure** — gpt-4.1-mini, gpt-5-nano, gpt-5-mini, claude-haiku-4-5

## Key Results

### Current Cheatsheet Performance (current.txt = v2 gen3_x1, 6.7KB)

| Model | No CS | With CS | Delta |
|-------|-------|---------|-------|
| gpt-4.1-mini (1200 probs) | 52.1% | **66.6%** | +14.5 |
| gpt-5-nano (50 probs) | ~52% | **82%** | +30 |
| gpt-5-mini (50 probs) | 84% | 68% | **-16** (hurts!) |

### Deterministic Rule Baseline: 72.4%
Two rules with 100% accuracy on training data:
1. **Lone var absent → TRUE** (243/243 = 100%): If Eq1 = "v = T" and v not in T → always TRUE
2. **LZ/RZ counterexample → FALSE** (280/280 = 100%): If Eq1 holds in left-zero/right-zero magma but Eq2 fails → always FALSE

Together: 523/1200 = 44% of problems solved perfectly.

### Competition Benchmark
- Leader (Kendon): 93.3% normal, 79.9% hard
- Our best (nano): ~82% on 50-problem samples
- Gap: ~11 pts on normal, ~26 pts on hard

## Critical Findings

### 1. gpt-4.1-mini Ceiling is ~67%
Regardless of cheatsheet content, gpt-4.1-mini can't go beyond ~67% on this task. It's a non-reasoning model — useful for fast iteration but not competitive.

### 2. Nano is the Right Target
With reasoning, nano reaches 82% and has room to grow. TRUE accuracy is 89-96% — excellent. FALSE accuracy (73%) is the main bottleneck.

### 3. gpt-5.4 as Evolver Has Limits
The evolver consistently generates cheatsheets worse than the seed. It destroys TRUE accuracy by rewriting the carefully balanced rules. Across 40+ variants and 2 optimizer versions, NO variant reliably beats the seed.

### 4. The Cheatsheet Hurts Mini
gpt-5-mini is already at 84% without cheatsheet. Adding the cheatsheet drops it to 68%. The cheatsheet introduces false positives that confuse the stronger model.

## What Works in the Cheatsheet
- "Lone variable absent = TRUE" rule: crystal clear, 100% accurate
- LZ/RZ counterexample procedure: mechanical, 100% accurate
- Anti-hallucination rules: prevent over-applying explosive collapse
- Structured decision procedure: step-by-step, reduces errors

## What Doesn't Work
- LLM-evolved mutations: consistently destroy TRUE accuracy
- Over-assertive rules: cause false positives on hard problems
- Behavioral instructions: non-reasoning models ignore them

## Paths Forward (Priority Order)

### A. Optimize for Nano (HIGH PRIORITY)
- Nano + current.txt = ~82% with 96% TRUE acc
- FALSE errors are the bottleneck (73%)
- Need: more counterexample patterns, better FALSE heuristics
- Could reach 85-90% if we improve FALSE accuracy

### B. Add More LZ/RZ-like Rules (HIGH PRIORITY)
- Current LZ/RZ catches 45% of FALSEs
- Other small magmas (constant, XOR) might catch more
- Can compute these programmatically from the data

### C. Use Full 22M Dataset (MEDIUM PRIORITY)
- Extract patterns from ALL implications, not just 1200
- Look for equation-level features that predict TRUE/FALSE
- Could encode as lookup tables in the cheatsheet (if fits in 10KB)

### D. Different Optimization Approach (MEDIUM PRIORITY)
- GEPA's Pareto front: maintain diverse solutions
- Partial mutations: only modify sections, don't rewrite everything
- Meta-evolution: evolve the optimization strategy itself

### E. Multi-Model Optimization (LOWER PRIORITY)
- The cheatsheet HURTS mini → need to fix this
- Multi-objective: help weak models without hurting strong ones
- May need different cheatsheet per model type (but competition uses one)

# Session 1 Synthesis — 2026-03-18

## Key Findings

### 1. The problem is a DAG reachability problem
- 4694 equations form 1415 equivalence classes under mutual implication
- Implication is 100% transitive (preorder)
- The quotient DAG: 1415 nodes, 4824 edges, height 15, 1 source (x=y), 1 sink (x=x)
- Diamond shape: widest at levels 4-5 (~269 classes)

### 2. Two completely different regimes: Normal vs Hard
- **Normal problems**: syntactic heuristics achieve 85.4% (satisfaction scores + variable counts)
- **Hard problems**: heuristics barely beat random (54.5%). Need algebraic reasoning.
- Hard problems have equations with very similar satisfaction scores → can't distinguish them

### 3. The strongest predictive features (for normal)
1. **Satisfaction score difference** (70.4% alone): how restrictive each equation is on random magmas
2. **rhs_only_vars difference** (strongest pair signal, 1.25 gap between TRUE/FALSE)
3. **total_vars difference** (0.84 gap)
4. **eq1_lhs_is_var** (91.8% of TRUE implications have single-var LHS)
5. Combined: 85.4% on normal

### 4. Model reasoning patterns (from benchmark analysis)
- Models are already decent at FALSE (default guess works 63%)
- Main failure: missing TRUE implications — can't find the algebraic derivation
- Successful TRUE patterns: substitution, constant-op detection, multi-step proof
- Cheatsheet should teach PROOF PROCEDURES, not just heuristics

### 5. Detailed cheatsheet rules HELP strong models, HURT weak ones
- gpt-5-mini: 72% → 80% with better rules
- Phi-4: 16% → 3% (can't follow complex instructions)
- Need to balance simplicity and depth

### 6. 2-element magma counterexamples
- 16 possible magmas, constant magmas satisfy 1556 eqs (33%)
- Best counterexample magmas: 0001 and 1000 (satisfy only 3%)
- Including these in cheatsheet could help with FALSE proofs

## Isomorphisms Identified
1. **DAG reachability** — transitive closure, chain decomposition
2. **Finite model theory / Stone pairings** — satisfaction probability fingerprints
3. **Knowledge distillation** — compressing 22M truth table into 10KB
4. **Constraint satisfaction** — equations as constraints, implication as subtyping
5. **Pseudocode execution** — models reason better with algorithmic procedures

## Approaches to Try Next
1. **OpenEvolve for prompt optimization** — has prompt evolution example, +23% on HotpotQA
2. **Few-shot examples** in cheatsheet vs pure rules
3. **Pseudocode-style** cheatsheet (EMNLP 2024 shows improvements)
4. **Modular cheatsheet** with ablation testing
5. **Analyze benchmark model responses** to extract successful reasoning patterns
6. **Stone pairing fingerprints** — precompute and describe clusters in cheatsheet

## Baseline Status (gpt-5-mini, 16K reasoning tokens)
- Cheatsheet v0 (generic, 1.7KB): 72% → with 16K tokens probably ~78%
- Cheatsheet v1 (data-driven, 3.1KB): **80%**
- Cheatsheet v2 (procedural, 3.6KB): 70% (8K tokens), ~80% (16K tokens)
- Cheatsheet v4 (hybrid, 3.3KB): **80%** (confirmed across two runs: 8/10 + 12/15)
- Multi-feature predictor ceiling: 85.4% on normal, 54.5% on hard

### CRITICAL FINDING: Token budget matters as much as cheatsheet quality
Raising max_completion_tokens from 8192 to 16384 improved accuracy by ~10%.
Reasoning models need space to think. Many "failures" were just truncations.

### Model selection: dropped Phi-4
Phi-4 is not in SAIR's 25-model benchmark and is too weak for the task.
Evaluating against gpt-5-nano + gpt-5-mini only.

## BREAKTHROUGH: Less is More

v6 (2.7KB, focused on substitution) achieved **100% on 15 problems**
while v5 (6.3KB, comprehensive) only got 73%.

The key insight: **conciseness and focus beat comprehensiveness.**
The model works better with a SHORT, CLEAR decision procedure focused
on the #1 technique (substitution) than with a long reference document.

This suggests the cheatsheet should be:
- Under 3KB (leave room for model to think)
- Focused on 2-3 key techniques, not 10
- Procedural (step by step), not encyclopedic
- Include specific "don't do this" warnings

## Cheatsheet Results Summary

| Version | Size | gpt-5-mini (normal) | Key Change |
|---------|------|---------------------|------------|
| v0 baseline | 1.7KB | 72% (n=50) | Generic rules |
| v1 data-driven | 3.1KB | 80% (n=50) | DAG/satisfaction heuristics |
| v2 procedural | 3.6KB | ~70% (n=30) | Step-by-step procedures |
| v4 hybrid | 3.3KB | 80% (n=15) | Best of v1+v2 |
| v5 distilled | 6.3KB | 73% (n=15) | GPT-5.3 generated, too verbose |
| **v6 focused** | **2.7KB** | **96.7% (n=30)** | **Focused on substitution** |

### The #1 lesson: LESS IS MORE
v6 (2.7KB, focused) massively outperforms v5 (6.3KB, comprehensive).
The model works better with SHORT, CLEAR instructions focused on the
#1 technique (substitution) than with comprehensive reference material.

### What makes v6 work:
1. Substitution technique as THE central focus
2. Explicit "don't do this" warnings against premature FALSE
3. Concise format — model doesn't get lost
4. Quick checks first, deep reasoning second
5. 2.7KB leaves lots of room for model's own reasoning

### Baseline context: gpt-5-mini without cheatsheet
From the SAIR benchmark (200 normal problems, default reasoning, no cheatsheet):
- **93.2% accuracy** — the model is already strong!
- 85% of errors are false negatives (says FALSE when TRUE)
- Only 2.2% false positive rate
- v6 improves this to 96.7% — a 3.5 point gain, primarily by reducing FN rate

## v6 is Locally Optimal — Manual Improvements Exhausted

Tested 4 variants beyond v6 (v7, v8, v9 with different additions/formats).
EVERY modification reduced accuracy. v6 is a local optimum.

| Variant | Change from v6 | Accuracy |
|---------|---------------|----------|
| v7 (+intermediate laws) | +100 bytes | 87% (-10) |
| v8 (pseudocode format) | reformat | 80% (-17) |
| v9 (+worked example) | +300 bytes | 87% (-10) |

Prompt length research confirms: v6 at ~380 words is in the optimal
300-500 word range. Beyond that, comprehension drops 12% per 100 words.

## Next Steps (for session with human)

### Immediate validation:
1. Test v6 on SAIR playground (ultimate ground truth) — 10 credits/day
2. Run ablation study (analysis/ablation_study.py, ~42 min)

### Evolutionary optimization:
3. Use OpenEvolve for surgical mutations to v6 (prototype ready)
4. Need cascade evaluation: static analysis → proxy → full LLM

### Hard problems:
5. Hard problem evaluation was blocked by API timeouts
6. Need strategy for faster eval (reduce sample or use cheaper model)

### Infrastructure:
7. Fix gpt-5-nano evaluation (needs 32K+ tokens)
8. Fix Windows asyncio background task buffering

### Research to continue:
9. Birkhoff completeness: can we teach better substitution search?
10. Negative space approach: define FALSE indicators precisely
11. Meta-learning from 15K benchmark responses
12. OpenEvolve prompt evolution (+23% on HotpotQA benchmark)

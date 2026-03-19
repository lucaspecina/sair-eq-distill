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

## Approaches to Try Next
1. **Confirm v6 on larger sample** (30+ problems) — pending
2. **Test v6 on hard problems** — pending
3. **Test v6 on gpt-5-nano** — pending
4. **OpenEvolve** to evolve v6 further — promising now that we have a good starting point
5. **Modular cheatsheet**: evolve each section independently
6. **Ablation study**: remove sections one by one to find most valuable parts

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

## Baseline Status
- Cheatsheet v0 (generic): 50.7% avg (nano:64%, mini:72%, Phi-4:16%)
- Cheatsheet v1 (data-driven): 48.9% avg (nano:63%, mini:80%, Phi-4:3%)
- Cheatsheet v2 (procedural): pending evaluation
- Multi-feature predictor ceiling: 85.4% on normal, 54.5% on hard

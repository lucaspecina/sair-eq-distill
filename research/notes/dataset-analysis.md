# Dataset Analysis — First Pass

Date: 2026-03-18

## Equation Structure

4694 equations total. Format: `LHS = RHS` using variables x,y,z,w,u,v and operation ◇.

### Key stats:
- **91.3%** of equations have exactly 4 operations (the maximum)
- **66.9%** have a single variable as LHS (e.g., `x = ...`)
- Variable counts: mostly 3 vars (44.5%) or 4 vars (30.8%)
- Max nesting depth: 0-3 levels
- Only 2 equations with 0 operations: `x = x` (tautology) and `x = y` (collapse)

### Finding: normal and hard problems are syntactically identical
Normal problems: avg 3.9 ops, 25.9 chars
Hard problems: avg 3.8-4.0 ops, 25.2-26.2 chars

**The difficulty is NOT in equation complexity. It's in the structural relationship.**

## Implication Matrix

4694 × 4694 matrix. Values: 3 (true), -3 (false), 4 (hard-true), -4 (hard-false).

### Distribution:
- True (3): 8,167,622 (37.1%)
- False (-3): 13,268,432 (60.2%)
- Hard-true (4): 10,657 (0.05%)
- Hard-false (-4): 586,925 (2.7%)

**~63% of pairs are FALSE. A default "False" heuristic gets 63% accuracy.**

### CRITICAL FINDING: Transitivity is 100%

Tested 1206 random transitive triples (A→B and B→C). In ALL cases A→C.
This means **implication is a preorder** (reflexive + transitive).
With equivalence classes, it's a **partial order on equivalence classes**.

This is a HUGE structural constraint. It means:
- If we know the partial order on classes, we know ALL implications
- The graph has NO cycles (except within equivalence classes)
- Reachability in the quotient DAG = the answer to any question

### Equivalence Classes

1415 total classes, 270 non-trivial (size > 1).

Top classes by size:
| Size | Example equations |
|------|-------------------|
| 1496 | x = y, x = y ◇ y, x = y ◇ z (all "collapse" equations) |
| 419 | x ◇ y = z ◇ w (all "constant operation" equations) |
| 112 | x = y ◇ (x ◇ x) variants |
| 112 | x = (x ◇ x) ◇ y variants |
| 76 | x = y ◇ (x ◇ (x ◇ x)) variants |

The biggest class (1496 equations, 31.9%) is all equations equivalent to x = y.
These are the "maximally restrictive" — they force all elements to be equal.

### Per-equation stats
- Most powerful (implies the most): Eq 2 (x = y) → implies ALL 4694
- Eq 1 (x = x) → implies only itself (tautology, weakest)
- Most implied: Eq 1 (x = x) → implied by all 4694

### Hard problems
- Hard-true: 10,657 (very rare — only 0.13% of true implications are hard)
- Hard-false: 586,925 (8.7% of false implications are hard)
- ALL equations participate in hard problems — not a subset issue

## Isomorphisms — this is a REACHABILITY problem

The question "does A imply B?" is exactly "is B reachable from A in the
implication DAG?" This connects to:

1. **Graph reachability / transitive closure**: well-studied problem. Can we
   encode the DAG structure compactly in 10KB?
2. **Partial order compression**: the quotient of equivalence classes forms a
   DAG. How many nodes does this DAG have? (1415). Can we describe it?
3. **Chain decomposition / antichain structure**: Dilworth's theorem — what's
   the minimum number of chains that cover the partial order?

## Quotient DAG Structure

The quotient DAG (equivalence classes with edges from transitive reduction):

- **1415 nodes** (equivalence classes)
- **4824 edges** (transitive reduction from 28442 full DAG edges)
- **1 source**: x = y (class of size 1496 — the strongest equations)
- **1 sink**: x = x (the tautology — the weakest equation)
- **Height: 15** — only 15 levels from top to bottom

### Width by level (diamond shape):
```
Level  0:    1 (x = y, the source)
Level  1:   46
Level  2:   64
Level  3:  131
Level  4:  268  ← widest
Level  5:  269  ← widest
Level  6:  167
Level  7:  202
Level  8:  155
Level  9:   58
Level 10:   15
Level 11:   17
Level 12:   10
Level 13:    7
Level 14:    4
Level 15:    1 (x = x, the sink)
```

### Degree stats:
- Out-degree: min=0, max=46, mean=3.4, median=3
- In-degree: min=0, max=57, mean=3.4, median=2

### Implications for the cheatsheet:
This is a very structured DAG. If we can teach the model:
1. How to identify which equivalence class an equation belongs to
2. The partial order relationship between classes
Then the model can deduce any implication by checking reachability.

The challenge: 1415 classes × 4824 edges is too much to enumerate in 10KB.
We need RULES that describe the DAG, not the DAG itself.

## Substitution Analysis

Testing if "B is a substitution instance of A" predicts "A implies B":

| Dataset | Detected | Precision | Coverage |
|---------|----------|-----------|----------|
| normal | 68/1000 | 86.8% | 6.8% |
| hard1 | 6/69 | 16.7% | 8.7% |

Substitution is a valid rule (87% precision on normal) but:
- Very low coverage (only 6.8% of problems)
- Almost useless on hard problems (17% precision)
- Hard problems require deeper reasoning than syntactic matching

## Multi-Feature Predictor Results

Combining satisfaction scores + variable heuristics + rhs_only_vars:

| Dataset | Multi-feature | Sat+vars | Always False |
|---------|--------------|----------|--------------|
| normal | **85.4%** | 83.8% | 50.0% |
| hard | 54.5% | 46.0% | 63.0% |
| hard1 | 53.6% | 46.4% | 65.2% |
| hard2 | 54.5% | 53.5% | 50.0% |

### KEY INSIGHT: Two completely different regimes
- **Normal problems**: syntactic heuristics work great (85% ceiling)
- **Hard problems**: heuristics barely beat random (55%). These require
  genuine algebraic reasoning, not pattern matching.

The cheatsheet needs TWO strategies:
1. Fast heuristics for normal problems (variable counts, satisfaction)
2. Algebraic reasoning guidelines for hard problems (counterexamples,
   proof strategies, structural properties)

### Satisfaction Score Distribution:
- 1558 equations (33.2%): never satisfied → equiv to x=y
- 1146 equations (24.4%): satisfaction 1-5%
- 1511 equations (32.2%): satisfaction 5-10%
- 402 equations (8.6%): satisfaction 10-20%
- 74 equations (1.6%): satisfaction 20-50%
- 3 equations: satisfaction > 50%
- 1 equation: always satisfied (x = x)

Satisfaction score as sole predictor: 70.4% on normal, 55.5% on hard2.

## Cheatsheet Evaluation Results

### Baseline cheatsheet (v0, generic rules, 1.7KB):
- gpt-5-nano: 64.0% | gpt-5-mini: 72.0% | Phi-4: 16.0% | **avg: 50.7%**

### Data-driven cheatsheet (v1, with DAG/vars heuristics, 3.1KB):
- gpt-5-nano: 63.3% | gpt-5-mini: **80.0%** | Phi-4: 3.3% | **avg: 48.9%**

### KEY INSIGHT: Detailed rules help capable models but HURT weak ones
- gpt-5-mini improved from 72% → 80% with more detailed rules
- Phi-4 collapsed from 16% → 3.3% — too weak to follow complex instructions
- The cheatsheet must be simple enough for weak models but informative for strong ones

### Model inclusion decision:
Phi-4 is NOT in SAIR's 25-model benchmark. The weakest models there are:
- Llama 3.1 8B: 36-52%
- GPT-5 Nano: 60-77%
- Claude Haiku 4.5: 47-62%

We should consider dropping Phi-4 from our eval or weighting it less.

## 2-Element Magma Analysis

All 16 possible 2-element magmas ({0,1}):

| Magma | Satisfies | Description |
|-------|-----------|-------------|
| 0000 | 1556 (33%) | Constant: x*y=0 always |
| 1111 | 1556 (33%) | Constant: x*y=1 always |
| 0011 | 1214 (26%) | Right projection: x*y=y |
| 0101 | 1214 (26%) | Left projection: x*y=x |
| 0110 | 663 (14%) | XOR-like |
| 1001 | 663 (14%) | XNOR-like |
| 0001 | 164 (3.5%) | Good for counterexamples |
| 1000 | 138 (2.9%) | Best counterexample magma |

Constant magmas (0000, 1111) satisfy the same 1556 equations = the x=y equiv class.
Left/right projections satisfy 1214 equations each.

For counterexamples: magmas 0001 and 1000 satisfy very few equations — if
either satisfies Eq1 but not Eq2, that's a quick FALSE proof.

## Evaluation Infrastructure Issues

### gpt-5-nano needs high max_completion_tokens
Both gpt-5-nano and gpt-5.3-chat are reasoning models that spend tokens on
internal "thinking". With max_completion_tokens=4096, nano often returns EMPTY
responses (all tokens consumed by reasoning, nothing left for output).
Must use max_completion_tokens=8192 or higher.

### Evaluation speed
Each eval call takes 15-40 seconds (reasoning models). 20 problems × 2 models
= 40 calls = 5-13 minutes per evaluation. This limits iteration speed.

### Implication for autoresearch
The autoresearch hill-climbing loop would take ~10 min per iteration.
8 hours overnight = ~48 iterations. Manageable but not fast.
For evolutionary approach (OpenEvolve), need even smaller sample sizes.

## Open questions
- [ ] Can few-shot examples in cheatsheet help more than rules?
- [ ] What's the optimal balance of rules vs examples in 10KB?
- [ ] Should we include specific magma tables in the cheatsheet?
- [ ] Can OpenEvolve be used to evolve the cheatsheet text?

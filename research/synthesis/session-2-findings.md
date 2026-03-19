# Session 2 Findings — Robust Evaluation & Iterative Optimization

Date: 2026-03-19

## Critical Discovery: The 96.7% Was a Mirage

Our previous "96.7% accuracy" was inflated by:
- Fixed seed=42 (lucky sample)
- Only normal problems (no hard)
- Single model (gpt-5-mini only)

Real accuracy with robust eval (random seed, normal+hard mix):
- v6 on mini: ~84% weighted
- v6 on nano: ~57% weighted
- Baseline (no cheatsheet) on nano: ~54%

## Controlled A/B Test Results (seed=12345, 50 normal + 15 hard)

| Cheatsheet | Size | nano | mini | Avg |
|---|---|---|---|---|
| Empty (no cheatsheet) | 0 | 54.4% | 81.7% | 68.1% |
| **v6 (current)** | 2.7KB | 57.2% | 81.7% | 69.5% |
| **v15 (+ "Be concise")** | 2.8KB | **65.6%** | **83.9%** | **74.7%** |
| v16 (+ proof replay) | 2.6KB | 60.6% | 81.7% | 71.1% |
| v12 (proof audit gate) | 2.9KB | — | 78.9% | — |
| v13 (decision list format) | 1.5KB | — | 68.3% | — |
| v14 (ultra-minimal) | 934B | — | 70.0% | — |

Winner: **v15** (+5.3 pts over v6, +6.6 over baseline)

## Phi-4 Finding

Phi-4 is DESTROYED by cheatsheets (53% → 6%). Too weak to follow instructions.
Not in SAIR's 25-model benchmark. Excluded from optimization.

## Error Analysis (v6, seed=12345)

### gpt-5-mini (77% accuracy, 15 errors):
- **11 false positives** (10 hard, 1 normal) — fabricates substitution proofs (91%)
- 3 false negatives, 1 parse error

### gpt-5-nano (54% accuracy, 30 errors):
- **28 parse errors** = empty responses (runs out of 16K reasoning tokens)
- 1 false positive, 1 false negative
- Conciseness instruction (v15) reduced empty responses from 28 → 18

### Opposite model biases (from SAIR benchmark, no cheatsheet):
- mini: TRUE bias on hard (89.6% TRUE acc, 29.6% FALSE acc)
- nano: FALSE bias on hard (33.8% TRUE acc, 75.9% FALSE acc)
- Optimal cheatsheet must CALIBRATE, not push in one direction

## What We Learned About Cheatsheet Design

### What DOESN'T work:
1. **Adding restrictions** (v12 proof gate): blocks valid TRUE answers more than invalid ones
2. **Changing format** (v13 decision list, v14 minimal): natural prose > mechanical rules for current models
3. **Adding more prose** (v5, v7 from session 1): more text = more interference
4. **Proof replay** (v16): wastes tokens without benefit

### What DOES work:
1. **Conciseness instruction** (v15): +5.3 pts — reduces nano's token exhaustion
2. **Substitution teaching** (v6 core): helps nano find TRUE proofs (+8 normal)
3. **Default FALSE** (v6): aligns with 63% base rate

### The fundamental limitation of v6:
v6 is a BEHAVIORAL tutorial — it teaches HOW to think but doesn't contain
MATHEMATICAL KNOWLEDGE. The winning cheatsheet will contain compressed
mathematical patterns, not instructions.

## Competition Intelligence

### From Tao's blog (March 13, 2026):
- Models: "cheap" / "open-source" — not disclosed
- Baseline without cheatsheet: ~50%
- Best with cheatsheet on public benchmark: ~55-60%
- Public test: 1000 normal + 200 hard
- Private test: different subset of 22M
- Top 1000 advance to Stage 2
- Stage 2 requires formal proofs (Lean) + probability estimates
- Deadline: April 20, 2026

### Our position:
- nano + v15 = 65.6% weighted → above the 55-60% benchmark range
- But we haven't tested on the actual playground
- Different models may perform very differently

## 16 Mathematical Rules Identified for Encoding

### NOT in v6 (high priority to add):
| # | Rule | Signal | Bytes |
|---|------|--------|-------|
| 5 | RHS-only vars: if EQ1 has more → T | Strongest pair feature | ~100 |
| 12 | Magmas NOT associative warning | #1 weak-model error | ~80 |
| 2 | Satisfaction ordering (restrictive → less restrictive = T) | 70.4% alone | ~120 |
| 16 | Rewrite complex → simple (TRS principle) | Sound heuristic | ~60 |
| 6 | Single-var LHS: 91.8% of TRUE have EQ1 = "x = ..." | Very predictive | ~80 |

### Already in v6 (keep):
| # | Rule | Signal |
|---|------|--------|
| 1 | Substitution proof (Birkhoff completeness) | 4x correct:wrong |
| 3 | Default FALSE (63% base rate) | 63% floor |
| 7 | Constant operation detection | 27% of correct TRUE |
| 8 | Identity/projection detection | 36% of correct TRUE |
| 10 | 2-element counterexamples | Best discriminators |

## The Vision for the Winning Cheatsheet

Current v6 = tutorial (behavioral instructions)
Winning cheatsheet = compressed knowledge base:

```
[Short header: how to read this] + [Dense compressed mathematical rules and patterns]
```

Key principles:
- Every byte = mathematical information, not prose
- Semi-cryptic format that LLMs can parse (not human-readable prose)
- Structural rules with confidence scores
- Substitution patterns for common equation forms
- Counterexample magma tables
- Decision rules extracted from dataset analysis

Budget: 10KB. Current useful content: ~800 bytes of rules.
Remaining: ~9.2KB for more mathematical patterns.

## Next Steps

1. Build v17: compressed mathematical rules format
2. Automate the iteration loop (OpenEvolve-style)
3. Test on SAIR playground (the only real validation)
4. Extract more patterns from the 22M dataset for encoding

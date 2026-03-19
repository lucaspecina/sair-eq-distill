# Hypothesis: Cheatsheet May HARM Normal Accuracy

Date: 2026-03-19

## The alarming data point

SAIR benchmark (official, n=200, no cheatsheet):
- gpt-5-mini normal: **93.2%**
- gpt-5-mini hard: **51.8%**

Our robust eval (n=40-50, with v6 cheatsheet):
- gpt-5-mini normal: **80-90%** (varies by seed)
- gpt-5-mini hard: **30-60%** (varies by seed)

## Possible explanations

### 1. The cheatsheet genuinely hurts normal (WORST CASE)
- Adding text overwrites useful model priors
- The substitution focus biases toward TRUE, causing errors
- "63% FALSE base rate" shifts the model's prior incorrectly
- Codex warned: "more text = more interference"

### 2. Sample size noise (MOST LIKELY)
- Our n=50 has ±14pt error bars (Codex calculated)
- SAIR benchmark uses n=200 with controlled conditions
- Different random samples can swing 10+ points
- 80% on n=50 could be 90% on n=200 (within error)

### 3. Different evaluation conditions
- SAIR benchmark may use different prompt templates
- SAIR may use different reasoning/completion settings
- Their "200 normal" may be curated differently

## How to resolve

Running A/B comparison with SAME seed, SAME problems:
- v6 (cheatsheet) vs empty_baseline (no cheatsheet)
- seed=12345, n=50 normal + n=15 hard

If empty > v6 on normal: we have a fundamental problem.
If v6 > empty on normal: our cheatsheet helps, noise explains the gap.

## Status: CRITICAL — waiting for baseline results

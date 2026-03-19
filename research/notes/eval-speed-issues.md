# Evaluation Speed Issues

Date: 2026-03-19

## Current timings (gpt-5-mini with 16K max_completion_tokens)

| Problem type | Time per problem | Concurrent | 10 problems |
|-------------|-----------------|------------|-------------|
| Normal | ~30-40 sec | 3 | ~2-3 min |
| Hard | >120 sec | 1 | >10 min (timeouts) |

## Why hard is slower

Hard problems trigger longer reasoning chains:
- Reasoning tokens: 4000-16000 (vs 1000-4000 for normal)
- The model "thinks harder" on problems it finds difficult
- Some problems exhaust the 16K token budget

## Impact on workflow

- Normal eval (15 problems): ~6-9 min → workable
- Hard eval (5 problems): >10 min → frequent timeouts
- Full eval (30 normal + 10 hard): >20 min → too slow for iteration

## Solutions

### Short-term:
1. Increase timeout to 900s (15 min) for eval scripts
2. Run hard evals with run_in_background
3. Use smaller hard samples (3-5 problems)

### Medium-term:
1. Deploy gpt-4.1-nano for fast proxy eval (~1 sec/problem)
2. Use static feature predictor (85.4% on normal, instant)
3. Cascade: static → cheap model → full model

### Long-term:
1. Set up evaluation infrastructure with proper queue/retry
2. Use Azure Foundry batch API for bulk evaluation
3. Pre-compute model responses and cache them

## For the competition:
The SAIR playground has 10 credits/day. Each credit evaluates the
cheatsheet against the full 1200 problem set. That's the definitive test.
Our local eval is a proxy — don't over-optimize for it.

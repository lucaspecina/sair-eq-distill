# Session 3: Full 1200-Problem Evaluation

Date: 2026-03-20

## Setup
- Model: gpt-4.1-mini (non-reasoning, fast)
- Cheatsheet: current.txt (gen4_v0 from run1, 5.7KB)
- Problems: ALL 1200 public (1000 normal + 200 hard)
- SAIR template (cheatsheet inline in user message)

## Results

| Config | Total | Normal | Hard | TRUE acc | FALSE acc |
|--------|-------|--------|------|----------|-----------|
| No cheatsheet | 52.1% | 50.0% | 62.5% | 0.2% | 99.7% |
| current.txt | **67.3%** | **69.9%** | **54.5%** | **65.7%** | **68.8%** |
| Deterministic floor | 72.4% | 74.3% | 63.0% | 42.3% | 100% |
| **Leader (Kendon)** | **~89%** | **93.3%** | **79.9%** | ? | ? |

## Analysis

1. Cheatsheet adds +15.2 pts overall. Massive TRUE improvement (0→66%).
2. On hard: cheatsheet HURTS (-8 pts) by introducing false positives.
3. We're 5 pts below the deterministic floor on normal (69.9 vs 74.3).
4. Gap to leader: ~22 pts. Most of this is in TRUE accuracy on harder cases.

## Key Bottlenecks

1. **gpt-4.1-mini can't apply LZ/RZ check reliably** — the deterministic check
   gives 100% accuracy but the model doesn't execute it mechanically.
2. **Hard FALSE problems**: cheatsheet makes model say TRUE when it shouldn't.
3. **Self-referential TRUE**: these require multi-step reasoning the weak model can't do.

## Paths Forward

1. **Better LZ/RZ instruction**: make the cheatsheet's LZ/RZ procedure even more mechanical
2. **Reasoning model (nano/mini)**: may apply rules more reliably, especially substitution
3. **Data-derived patterns**: extract more rules from 22M dataset
4. **Competition template**: use "free-form prompt template" option if available

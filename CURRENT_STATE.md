# Current State

## Overview

Cheatsheet v6 achieves **96.7% accuracy** on normal problems with gpt-5-mini (29/30).
This is the best result so far, up from 72% baseline. The key insight: a focused,
concise cheatsheet (2.7KB) outperforms comprehensive ones (6.3KB).

Extensive research completed on dataset structure, model reasoning patterns,
and potential optimization approaches (evolutionary, modular, data-driven).

## Modules / Components

| Module | Purpose | Status |
|--------|---------|--------|
| `analysis/` | Dataset exploration scripts | 5 scripts, major findings documented |
| `cheatsheets/` | Cheat sheet versions | v6 is current best (96.7%) |
| `eval/` | Multi-model evaluation pipeline | Working (gpt-5-nano, gpt-5-mini) |
| `optim/` | Optimization strategies | OpenEvolve prototype ready |
| `research/` | Research notes and synthesis | 7 documents, synthesis complete |
| `data/raw/` | ETP data + HuggingFace datasets | Complete |

## Key APIs

- `eval/evaluate.py` — `python eval/evaluate.py --sample N --models "model1,model2"`
  Evaluates cheatsheet against problem set. Reports per-model + average accuracy.
  Parses `VERDICT: TRUE/FALSE` from model responses.

## Test coverage

No automated tests yet. Validation is via evaluation accuracy.

## Known limitations

- gpt-5-nano produces empty responses (reasoning token exhaustion) with ≤16K tokens
- Hard problems timeout with current API speed (~2-5 min per problem)
- Background asyncio tasks don't flush output on Windows
- Haven't tested on SAIR playground yet (10 credits/day)
- Haven't confirmed results with gpt-5-nano at 32K+ tokens

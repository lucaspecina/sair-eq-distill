# Model Bias Analysis — Opposite Biases in Hard Problems

Date: 2026-03-19

## CRITICAL FINDING

gpt-5-mini and gpt-5-nano have OPPOSITE biases on hard problems:

### gpt-5-mini (hard, no cheatsheet):
- TRUE accuracy: **89.6%** (strong!)
- FALSE accuracy: **29.6%** (terrible!)
- **BIAS: says TRUE too much** → needs help rejecting false TRUE claims

### gpt-5-nano (hard, no cheatsheet):
- TRUE accuracy: **33.8%** (terrible!)
- FALSE accuracy: **75.9%** (strong!)
- **BIAS: says FALSE too much** → needs help finding TRUE implications

### Normal problems (mini, no cheatsheet):
- TRUE: 89.3%, FALSE: 97.8%
- Much more balanced → cheatsheet adds ~3.5 points

## Implications for cheatsheet design

### The dilemma:
- v6 teaches "try substitution before saying FALSE" → corrects nano's FALSE bias
- But v6 might WORSEN mini's TRUE bias on hard problems (makes it even more likely to say TRUE)

### Possible solution: teach CALIBRATION, not direction
Instead of pushing toward TRUE or FALSE, teach the model to be more CAREFUL:
- "If substitution works → TRUE (be confident)"
- "If substitution fails after 3 attempts → FALSE (also be confident)"
- "If partially works → re-examine, don't guess"

### Alternative: different cheatsheets for different model sizes?
The competition probably evaluates on multiple models with different biases.
A cheatsheet that CALIBRATES (makes both biases less extreme) would be
optimal for the average across models.

## Data

| Model | Dataset | Reasoning | TRUE acc | FALSE acc | Overall |
|-------|---------|-----------|----------|-----------|---------|
| mini | normal | default | 89.3% | 97.8% | 93.2% |
| mini | hard | default | 89.6% | 29.6% | 51.8% |
| mini | hard | low | 73.4% | 35.7% | 49.7% |
| nano | hard | default | 33.8% | 75.9% | 60.3% |

## Next steps
1. Test v6 on hard with mini — does it improve FALSE accuracy or worsen it?
2. Design a "calibration-focused" cheatsheet variant
3. Consider if the competition weights models equally or by capability

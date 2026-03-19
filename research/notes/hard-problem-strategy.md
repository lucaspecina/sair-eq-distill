# Hard Problem Strategy — The Next Frontier

Date: 2026-03-19

## Current state

v6 achieves 96.7% on normal but only 60% on hard (gpt-5-mini).
The SAIR benchmark shows mini without cheatsheet gets 51.8% on hard.
So v6 adds ~8 points on hard — modest improvement.

## Why hard is hard

### For gpt-5-mini on hard (no cheatsheet):
- TRUE accuracy: 89.6% → strong at finding TRUE
- FALSE accuracy: 29.6% → terrible at rejecting FALSE
- The model has a massive TRUE bias on hard problems

### With v6 cheatsheet:
- v6 teaches "try substitution before saying FALSE"
- This REINFORCES the TRUE bias on hard problems!
- v6 is optimized for normal (where the bias is toward FALSE)
- On hard, the opposite intervention is needed

## The fundamental tension

| Problem type | Model bias (mini) | v6 intervention | Effect |
|-------------|-------------------|-----------------|--------|
| Normal | FALSE bias (FN=10.7%) | Push toward TRUE | GOOD (+24 pts) |
| Hard | TRUE bias (FP=70.4%) | Push toward TRUE | BAD (reinforces bias) |

## Potential solutions

### 1. Conditional strategy in cheatsheet
"For problems where substitution PARTIALLY works but isn't complete:
- On simple equations (few operations): lean TRUE
- On complex equations (many operations): lean FALSE and try counterexample"

### 2. Teach self-verification
"After arriving at TRUE, verify your proof:
- Can you write each step explicitly?
- Does each step follow from the previous by legitimate substitution?
- If any step is a 'hand wave' → reconsider and try FALSE"

### 3. Teach counterexample construction for hard cases
"If the equations are complex and substitution only partially works:
- Try 3-element magmas (27 operation tables to check)
- Use the greedy construction: fill the table row by row satisfying Eq1
- Check if Eq2 can be violated"

### 4. Separate cheatsheets for normal vs hard
Not practical — the competition uses one cheatsheet for all problems.
But the cheatsheet could say: "For complex-looking equations with
many nested operations, be MORE skeptical of TRUE claims."

## Priority assessment

The competition mixes normal and hard problems. Normal is 1000, hard is 200.
If scoring is uniform: (1000 × normal_acc + 200 × hard_acc) / 1200.

With v6: (1000 × 0.967 + 200 × 0.60) / 1200 = (967 + 120) / 1200 = 90.6%

If we improve hard to 70%: (967 + 140) / 1200 = 92.3%
If we improve hard to 80%: (967 + 160) / 1200 = 93.9%

Even large hard improvements only add ~3 points to overall.
Normal accuracy is 5x more impactful due to 5:1 ratio.

**Conclusion: protect normal accuracy. Only touch hard if it doesn't hurt normal.**

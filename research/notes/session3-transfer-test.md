# Session 3: Transfer Test Results

Date: 2026-03-19

## Setup
- Cheatsheet: current.txt (gen4_v0, evolved from empty seed, 5.7KB)
- Evolved using gpt-4.1-mini as evaluator, gpt-5.4 as evolver
- Test: 50 problems (40 normal + 10 hard), seed=777, SAIR template

## Results

| Model | No CS | With CS | Delta | TRUE acc | FALSE acc |
|-------|-------|---------|-------|----------|-----------|
| gpt-4.1-mini | 60% | 60% | 0 | 1→9/21 | 29→21/29 |
| gpt-5-nano | 52% | 56% | +4 | 8→10/21 | 18→18/29 |
| gpt-5-mini | 84% | 68% | **-16** | 20→14/21 | 22→20/29 |

## Key Findings

1. **gpt-4.1-mini**: Without CS, says FALSE to everything (1/21 TRUE). With CS, starts
   identifying TRUEs (9/21) but loses some FALSE accuracy. Net zero on total but
   fundamentally changed behavior — now actually using the cheatsheet.

2. **gpt-5-nano**: Small improvement. Still has 18-20 None responses (token exhaustion).
   The cheatsheet helps TRUEs slightly without hurting FALSEs.

3. **gpt-5-mini**: CHEATSHEET HURTS. -16 points! Mini is already very good (84%) and
   the cheatsheet introduces false positives and confuses its reasoning.

## Implications for Competition

- The competition uses a MIX of models. If they use mini-level models, our cheatsheet
  is actively harmful.
- We need a cheatsheet that helps weak models WITHOUT hurting strong ones.
- The "explosive rule" (lone variable = collapse) may be too aggressively stated,
  causing mini to over-apply it and generate false TRUEs.
- Alternative: make the cheatsheet more conservative / precise, or add caveats that
  a strong model would use to moderate the rules.

## Next Steps
- Analyze specific errors: which problems does CS break on mini?
- Consider multi-model optimization: eval on both 4.1-mini AND mini
- Consider softer/more precise rules that don't confuse strong models

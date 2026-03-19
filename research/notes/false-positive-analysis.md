# False Positive Analysis — The Core Problem for Hard

Date: 2026-03-19

## THE FINDING

On hard FALSE problems, gpt-5-mini says TRUE 70.4% of the time (should be 0%).

81% of these wrong TRUE answers mention "substitution"
80% mention "identity"
50% mention "forces"

**The model INVENTS incorrect proofs.** It claims substitution works when it
doesn't. It says "Equation 1 forces x*y = y" when that's NOT actually derivable.

## Example wrong proof

Problem: x = y * (y * ((x * y) * x)) → x * y = ((z * x) * w) * y
Model says: "Equation 1 forces x*y = y for all x,y"
Reality: This is NOT derivable from Eq1. The model fabricated the derivation.

## Why this happens

1. The model has been taught (by v6 and naturally) to look for substitution proofs
2. When it partially sees a pattern, it fills in the gaps with hallucinated steps
3. The model can't reliably verify its own algebraic derivations
4. On hard problems, the patterns are suggestive but misleading

## Implication for cheatsheet design

### What helps on normal (correct):
"Try substitution" → model finds genuine proofs → accuracy improves

### What hurts on hard (incorrect):
"Try substitution" → model fabricates proofs → accuracy drops

### The dilemma:
- Teaching substitution: +25 pts on normal, -8 pts on hard
- Net effect: (1000 × 0.25 - 200 × 0.08) / 1200 ≈ +20 pts overall
- Still overwhelmingly positive — v6's approach is correct for the competition

### Potential fix for hard:
Add: "After deriving TRUE, VERIFY your proof by checking each step.
If ANY step requires 'clearly' or 'obviously' without explicit algebra,
your proof is likely wrong. Reconsider FALSE."

But adding text to v6 has consistently hurt accuracy...

## KEY INSIGHT:
The cheatsheet CANNOT teach the model to verify proofs — that requires
a fundamentally different capability (meta-reasoning about its own output).
The best we can do is:
1. Maximize normal accuracy (where substitution teaching works)
2. Accept modest hard accuracy (60%) as a known limitation
3. Focus competition strategy on normal problems (5x weight)

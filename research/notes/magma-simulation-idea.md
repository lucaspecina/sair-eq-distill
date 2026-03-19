# Idea: Teach the Model to Simulate Small Magmas

Date: 2026-03-18

## The insight

The most powerful technique for proving FALSE implications is finding a
counterexample magma. But models are bad at constructing novel magmas from
scratch. What if we teach them to CHECK specific pre-computed magmas?

## The approach

Include in the cheatsheet a set of "canonical" 2-element magma tables and
instructions for how to CHECK an equation against them:

```
Magma A: 0*0=0, 0*1=0, 1*0=0, 1*1=0 (constant zero)
Magma B: 0*0=0, 0*1=1, 1*0=0, 1*1=1 (right projection)
Magma C: 0*0=0, 0*1=0, 1*0=1, 1*1=1 (left projection)
Magma D: 0*0=0, 0*1=1, 1*0=1, 1*1=0 (XOR)
```

For each magma, include a lookup table of 16 expressions:
```
For Magma D (XOR):
  0*0=0, 0*1=1, 1*0=1, 1*1=0
  (0*0)*0=0, (0*0)*1=1, (0*1)*0=1, ...
```

This lets the model "execute" the check mentally by looking up values.

## Space budget

4 magmas × table entries ≈ 200 bytes
Instructions ≈ 200 bytes
Total: ~400 bytes — fits easily in the 6.6KB remaining

## Expected impact

Currently, the model mentions "counterexample" in 37% of wrong TRUE answers
(trying to disprove when it should prove). If we give it concrete tables to
check, it can:
1. Quickly verify whether Eq1 holds for a given magma
2. If yes, quickly check if Eq2 also holds
3. If Eq1 holds but Eq2 doesn't → definitive FALSE

This is like giving the model a "calculator" for small magma verification.

## Limitation

This only helps for FALSE implications. For TRUE implications, we still need
substitution and algebraic techniques.

## Priority

Medium. The bigger gain is in TRUE implications (where models fail more).
But this could help with precision on FALSE calls.

# Information Theory Analysis

Date: 2026-03-19

## How much information is in the problem?

- Entropy: 0.95 bits/pair → 2,559 KB total for all 22M pairs
- This is WAY more than 10KB → can't encode everything

## How much information is in the DAG?

- Binary encoding of DAG: 12.2 KB (barely over budget)
- Text encoding: ~97 KB (10x over budget)
- The DAG is the COMPRESSED representation — still too large for text

## What does v6 capture?

v6 at 2.7KB captures enough rules to achieve 96.7% on normal.
That's ~2.7KB text ≈ ~22K bits of effective information.

For 1000 normal problems:
- 967 correct → 33 errors
- Each error costs ~1 bit of "missing information"
- So v6 is missing ~33 bits of information for normal problems
- That's remarkably efficient — 22K bits to solve 97% of 1M+ possible pairs

## Theoretical limits

For 10KB text (~80K bits, but in practice ~10-20K effective bits):
- Normal problems: likely achievable to ~99% with optimal encoding
- Hard problems: unclear — may need fundamentally different information
- Overall (1000 normal + 200 hard): theoretical max probably ~95-98%

## What this means for optimization

1. v6 is already near the text-compression limit for normal problems
2. The remaining 3% on normal might require specific case knowledge
3. Hard problems need fundamentally different approach (not more rules)
4. The 10KB budget is surprisingly generous for rules but too small for data
5. Evolutionary optimization (OpenEvolve) might squeeze out 1-2% more

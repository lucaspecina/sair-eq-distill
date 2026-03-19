# A/B Test Results — Session 2

Date: 2026-03-19

## Setup
- Model: gpt-5-mini
- Seed: 12345 (fixed for all variants)
- Sample: 50 normal + 15 hard = 65 problems
- All variants tested on SAME questions

## Results

| Cheatsheet | Size | Normal | Hard | Weighted |
|---|---|---|---|---|
| Empty (no cheatsheet) | 1B | 92.0% | 33.3% | 82.2% |
| **v6 (current)** | **2.7KB** | **92.0%** | **46.7%** | **84.4%** |
| v12_audit (proof gate) | 2.9KB | 88.0% | 33.3% | 78.9% |
| v13 (decision list) | 1.5KB | 74.0% | 40.0% | 68.3% |
| v14 (ultra-minimal) | 934B | 80.0% | 20.0% | 70.0% |

## Key findings

### 1. v6 is the clear winner
- Only variant that doesn't hurt normal accuracy
- Only variant that improves total weighted score
- +13.4 pts on hard, neutral on normal, +2.2 weighted

### 2. Shorter is NOT better
- v14 (934B, ultra-minimal) is 14.4 pts worse than v6 (2.7KB)
- v13 (1.5KB, decision list) is 16.1 pts worse than v6
- There's a sweet spot in length and format

### 3. Format matters more than content
- v13 has the same ideas as v6 but in IF/THEN format → catastrophic
- Natural prose > mechanical rules for this model
- The model reads prose as "instructions", IF/THEN as "constraints"

### 4. Adding restrictions hurts
- v12 added proof-validity gate → -4 normal, -13.4 hard
- The gate blocks valid TRUE answers more than it blocks invalid ones
- "Unconfirmed TRUE ≠ FALSE" (Codex insight)

### 5. Statistical caveats
- n=15 hard has ±25% error bars — directional only
- n=50 normal has ±14% error bars
- These are indicative, not decision-grade
- Need n=200+ for confident conclusions

## Next steps
- [ ] Test on gpt-5-nano (running)
- [ ] Test top variant on SAIR playground
- [ ] Try softer anti-hallucination: "restate proof as explicit substitutions"
- [ ] Consider: can v6 be improved without changing format?

## Conclusion

v6's prose format is well-calibrated. The improvement path is NOT:
- Adding more content (v5, v7 failed previously)
- Adding restrictions (v12 failed)
- Changing format (v13, v14 failed)

The path might be:
- Micro-tuning wording (evolutionary)
- Adding 1-2 high-value sentences (surgical)
- Testing on the right models (weaker/open-source)
- Playground validation (the real test)

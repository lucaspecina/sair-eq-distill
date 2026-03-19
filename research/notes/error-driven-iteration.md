# Error-Driven Iterative Cheatsheet Optimization

Date: 2026-03-19

## The approach

User-proposed methodology for systematic cheatsheet improvement:

### Loop:
1. **Evaluate** on a diagnostic subset (mixed normal+hard)
2. **Collect errors** — save per-problem results with model responses
3. **Group errors by type** — false positives, false negatives, parse errors
4. **For each error group (ordered by impact)**:
   a. Analyze WHY the error happens (read model reasoning)
   b. Design a targeted cheatsheet fix
   c. Test the fix on BOTH the error cases + a fresh holdout
5. **Accept/reject** based on net weighted score impact
6. **Iterate** with new diagnostic set

### Three-bucket evaluation (from Codex review):
- **Diagnosis set**: inspect errors, design fixes (changes each round)
- **Regression set**: old failures + matched controls (grows over time)
- **Fresh holdout**: untouched until checkpoint (final validation)

### Key rules:
- Fix MECHANISMS, not individual cases
- Normal improvement is 5x more valuable than hard improvement
- Only accept a hard-focused change if: hard_gain > 5 × normal_loss
- Replace text, don't append (v6 is near optimal length)

## Current error profile (from robust eval, n=50)

| Error Type | Normal | Hard | Total |
|---|---|---|---|
| False positive | 2 | 5 | 7 |
| False negative | 2 | 0 | 2 |
| Parse error | 0 | 2 | 2 |
| **Total** | **4** | **7** | **11** |

### Error priority (by weighted impact):
1. **Normal false positives** (2 errors × 5 weight = 10 impact units)
2. **Normal false negatives** (2 errors × 5 weight = 10 impact units)
3. **Hard false positives** (5 errors × 1 weight = 5 impact units)
4. **Hard parse errors** (2 errors × 1 weight = 2 impact units)

→ Normal errors are the priority even though hard has MORE errors.

## First iteration: v12_audit

v12 replaces "Common Mistakes" (which encouraged TRUE-bias) with "Proof Validity Check":
- Explicit proof invalidity criteria
- "Magmas are NOT associative" — catches illegal rebracketing
- ">4 steps = almost always wrong" — length heuristic
- Forces FALSE if proof has gaps

A/B test running: v6 vs v12 on same 65 problems, same model.

## Statistical note

With n=50, 95% CI is ±14 points. We need n=200+ for decision-grade comparisons.
Multiple seeds averaging helps but doesn't substitute for larger samples.

## Status: in progress — waiting for A/B results

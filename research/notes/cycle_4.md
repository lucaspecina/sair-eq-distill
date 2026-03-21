# Cycle 4 Notes — Data-Driven Rule Refinement + Composite Rules

Date: 2026-03-20
Cycle: 4
Starting score: 83.5% (200 problems, gpt-5-nano)
Starting cheatsheet: 7.3KB

## Approach

Deep analysis of the 490 unresolved problems (after Rule 1 + all 2x2 magmas)
to find new features that split TRUE from FALSE better. Focus areas:

1. **Composite equations** (both sides compound, no lone variable)
2. **n_other_vars refinements** (fresh variables in Eq2, boundary type)
3. **LM/RM computation errors** (model's #1 failure mode)
4. **Token exhaustion** (model runs out of reasoning tokens)

## Key Data Findings

### Unresolved problem distribution (490 problems)
- TRUE: 331 (67.6%), FALSE: 159 (32.4%)
- Default TRUE = 86.8% overall accuracy
- Current cheatsheet rules = 90.5% deterministic accuracy

### Error analysis of current rules (114 total errors on 1200 problems)
- **sr_n=2_xocc<3**: 52 errors (predicting TRUE, 27% wrong)
- **composite_both**: 52 errors (predicting FALSE, 49% are TRUE)
- **n_other>=3**: Only 2 exceptions (98% accurate)

### New pattern: Composite rules (eq1_vars vs eq2_vars)
- eq1_vars=2: 8% TRUE (almost always FALSE)
- eq1_vars=3: 62% TRUE
- eq1_vars>=4: 88% TRUE
- eq1_vars>=5: 100% TRUE (13/13)

Best composite rules:
  C1. eq1_vars >= 5 => TRUE (100%)
  C2. eq1_vars >= 4 AND eq2_vars <= eq1_vars => TRUE
  C3. eq1_vars > eq2_vars + 1 => TRUE
  C4. Otherwise => FALSE

### Fresh variable analysis (n_other=2 selfref)
- fresh>=1 AND non-rm boundary => 100% TRUE (53/53)
- rm boundary: unreliable (36-100% TRUE depending on subcase)

### n_other=3 refinement
- no_boundary: 100% TRUE (86/86)
- with boundary: 92% TRUE (22/24, 2 exceptions)

### Token exhaustion analysis
- In eval runs, 2-5 out of 30 problems get None responses
- Mostly on n_other=1/0 cases (model loops trying to find counterexample)
- Also on composite cases (model doesn't know quick answer)

## What I Built

### Scripts created
- `optim/cycle4_analysis.py` — Deep feature analysis of unresolved problems
- `optim/generate_cheatsheet_cycle4.py` — v1: with fresh variable rules (7.2KB)
- `optim/generate_cheatsheet_cycle4b.py` — v2: compact version (4.5KB)
- `optim/generate_cheatsheet_cycle4c.py` — v3: simplified (6.4KB)
- `optim/generate_cheatsheet_cycle4d.py` — v4: final with LM/RM emphasis (6.8KB)

### Cheatsheet changes (v4 = final, in current.txt)
1. **Added composite equation rules** (Step 3C) — catches 52 previously-missed TRUEs
2. **Added step-by-step LM/RM examples** for deeply nested terms
3. **Added "LZ VERIFICATION PROCEDURE"** — explicit 2-step check process
4. **Added RZ counterexample worked example** (Example 3)
5. **Added Example 6** showing step-by-step LM computation on complex nested term
6. **Simplified n=2 selfref rules** (removed "fresh" variable complexity)
7. **Added "COMMON MISTAKE" warning** about LM/RM computation
8. **Added extra Node 1 examples** including tricky cases

### Theoretical accuracy improvements
- Cycle 3 rules: 90.5% (1086/1200)
- Cycle 4 v4 rules: 91.6% (1099/1200), +1.1pp from composite rules
- Full v1 rules with fresh: 92.1% (1105/1200), but more complex

## Quick Eval Results (30 problems each, high variance)
| Version | Score | TRUE% | FALSE% | Notes |
|---------|-------|-------|--------|-------|
| v1 (7.2KB) | 90.0% | 93% | 88% | First run, lucky sample |
| v1 (7.2KB) | 76.7% | 86% | 69% | Second run, bad sample |
| v3 (6.4KB) | 80.0% | 100% | 62% | Compact version |
| v4 (6.8KB) | 83.3% | 100% | 69% | Final version |

Average across all runs: ~82.5%. Consistent with previous cycle's 83.5%.

## Model Error Patterns
1. **LM/RM computation errors** (3/6 errors in run 3): Model miscalculates
   leftmost/rightmost variable in deeply nested terms. Added more examples
   and step-by-step procedure to address this.
2. **Token exhaustion** (2-5 per 30-problem eval): Model runs out of
   reasoning tokens on complex cases. Added "shortcut" for n_other<2.
3. **n_other=3 exceptions** (1/5 errors recurring): normal_0026 keeps
   appearing. Eq1 has x on LM boundary with n_other=3, which is one of
   only 2 exceptions to the 98% rule. Can't easily fix without hurting
   the other 108 correct predictions.

## Insights for Next Cycle

### What works
- 7KB cheatsheet size is optimal (2-5KB scores worse, 10KB risks token exhaustion)
- Composite rules are a genuine improvement (+1.1pp deterministic)
- 100% TRUE accuracy shows Node 1 is well-communicated
- The decision tree structure works well for the model

### What doesn't work
- 30-problem evals have ~8% variance — need 200+ for reliable comparison
- Adding "fresh variable" rules increases complexity without clear model benefit
- Compact cheatsheets (< 5KB) consistently underperform

### Suggested approaches for cycle 5
1. **Mine the 22M dataset** for equation-pair level lookup: encode specific
   equation implications as a compressed table
2. **LLM-generated worked examples** for the exact problem types the model
   gets wrong (use gpt-5.4 to generate, then add to cheatsheet)
3. **Model error analysis at scale**: run a 200-problem eval, then build a
   system that analyzes all errors and generates targeted fixes
4. **Different encoding format**: instead of natural language rules, try a
   more algorithmic/pseudocode format that reasoning models might follow
   more reliably
5. **Focus on hard problems**: the competition leader has 79.9% on hard.
   Our hard coverage may be worse. Analyze hard.jsonl specifically.

## API Calls
- 4 quick evals x 30 problems = 120 API calls to gpt-5-nano
- 0 calls to other models

## Files Modified
- `cheatsheets/current.txt` — updated to v4 (6.8KB)
- `cheatsheets/cycle4_v1.txt` — backup of v1
- `cheatsheets/cycle4_v2.txt` — backup of v2
- `cheatsheets/cycle4_v3.txt` — backup of v3
- `cheatsheets/cycle4_v4.txt` — backup of v4
- `cheatsheets/session_backup.txt` — backup of cycle3 version

# Cycle 5 Notes -- Minimal Surgical Edits + Stop-Early Instruction

Date: 2026-03-20
Cycle: 5
Starting score: 83.5% (200 problems, gpt-5-nano)
Starting cheatsheet: 7.3KB (7301 bytes)

## Approach

**"Less is more" -- targeted micro-surgery instead of adding complexity.**

Key insight from previous cycles:
- Cycles that KEPT (2,3) made small, targeted improvements
- Cycles that REVERTED (1,4) tried radical rewrites/additions
- Cycle 4 proved that deterministically better rules (+1.1pp) can HURT the model (-2pp) if they add complexity

Strategy: Make exactly 4 surgical changes to the existing cheatsheet, each addressing a specific identified issue. Total change: ~130 bytes added.

## Changes Made

### Change 1: Composite equation refinement
- OLD: "composite = composite => lean FALSE" (blanket rule)
- NEW: "composite, eq1 has >=5 vars => TRUE (92%)" + "composite, eq1 has <5 vars => FALSE"
- Impact: Affects ~13 unresolved composite problems on training data
- Accuracy: 92% on 1200 problems (12 TRUE, 1 FALSE)
- On hard problems: 3 TRUE, 1 FALSE (75%)

### Change 2: STOP-EARLY instruction
- Added after Node 3A, before counterexample details:
  "IMPORTANT: Once you reach a verdict via the decision tree above,
   OUTPUT IT IMMEDIATELY. Do not re-verify with magma computations.
   The rules are pre-validated. Trust them and save reasoning tokens."
- Hypothesis: Reduces token exhaustion by preventing the model from
  re-deriving answers it already reached via the decision tree
- **This appears to be the most impactful change** -- None responses
  dropped from 4/30 to 1-2/30

### Change 3: Example rule citation fix
- Examples 3 and 5 said "n_other >= 2 => Answer: TRUE"
- Fixed to "n_other >= 3 => Answer: TRUE" (matches actual rule threshold)
- Both examples have n_other=3, so the result was already correct
- The fix prevents the model from misinterpreting the rule as
  "n_other >= 2 => always TRUE" (which would miss x_occ>=3 exception)

## Data Analysis Findings

### Token exhaustion patterns (from last 200-problem eval)
- 17 None responses: 6 composite, 6 selfref_n2, 2 selfref_n1, 2 selfref_n3, 1 other
- 9 TRUE expected, 8 FALSE expected
- Token exhaustion is model-dependent and varies between runs

### Composite equation analysis (1200 training problems)
- 334 total composite problems: 16% TRUE, 84% FALSE
- After magma checks: 107 unresolved, 49% TRUE, 51% FALSE
- By n_vars in Eq1:
  - n=2: 0% TRUE (4 problems)
  - n=3: 36% TRUE (47 problems)
  - n=4: 53% TRUE (43 problems)
  - n=5: 92% TRUE (13 problems)
- n1-n2 analysis: diff>=2 is 85% TRUE (13 problems)

### Key error patterns in wrong answers (20 from last 200-run)
- 13 FALSE->TRUE (model predicts TRUE, answer FALSE): mostly selfref_n2
- 7 TRUE->FALSE (model predicts FALSE, answer TRUE): selfref_n2,n3 + composite
- Persistent errors: normal_0026 (n3 exception), normal_0433/0755 (composite n4)

## Quick Eval Results (30 problems each, seed=42, same sample)

| Version | Score | None | Wrong | TRUE% | FALSE% | Notes |
|---------|-------|------|-------|-------|--------|-------|
| v1 (composite only) | 76.7% | 4 | 3 | 79% | 75% | Stop-early absent |
| v2 (+ stop-early) | 90.0% | 1 | 2 | 79% | 100% | Best single run |
| v2 (rerun) | 86.7% | 1 | 3 | 86% | 88% | Model variance |
| v3 (+ example fix) | 86.7% | 2 | 2 | 86% | 88% | Final version |

Average v2/v3: 87.8% on 30 problems (vs cycle 3's 70-73% on same 30).
But 30-problem evals have ~8% variance from model non-determinism.

## Key Insight: STOP-EARLY Instruction

The biggest signal from this cycle is that adding "OUTPUT IT IMMEDIATELY"
after the decision tree significantly reduces token exhaustion:
- v1 (no stop-early): 4 None out of 30
- v2/v3 (with stop-early): 1-2 None out of 30

The model appears to be spending many reasoning tokens re-verifying its
answer with magma computations even after the decision tree has decided.
Telling it to stop and output immediately saves those tokens.

If this scales to 200 problems, reducing Nones from ~14 to ~5 would mean
~5 additional correct answers (from probabilistic default), which is +2.5%.

## Scripts Created

- `optim/generate_cheatsheet_cycle5.py` -- v1 generator (composite only)
- `optim/generate_cheatsheet_cycle5b.py` -- v2 generator (+ stop-early)
- `optim/generate_cheatsheet_cycle5c.py` -- v3 generator (+ example fix)

## Files Modified

- `cheatsheets/current.txt` -- updated to v3 (7426 bytes = 7.3KB)
- `cheatsheets/cycle5_v1.txt` -- backup of v1
- `cheatsheets/cycle5_v2.txt` -- backup of v2
- `cheatsheets/cycle5_v3.txt` -- backup of v3
- `cheatsheets/session_backup.txt` -- backup of cycle 3 version (starting point)

## API Calls

- 4 quick evals x 30 problems = 120 API calls to gpt-5-nano
- 0 calls to other models

## Insights for Next Cycle

### What works
- STOP-EARLY instruction reduces token exhaustion significantly
- Minimal changes are safer than complex additions
- Composite n_vars>=5 rule is high-precision (92%) with minimal complexity cost
- The decision tree format works well for the model

### What to try next
1. **Reduce cheatsheet size further**: The worked examples section is 23% of
   the cheatsheet. If some examples could be compressed, there's room for
   more targeted content. But examples were added in cycles 2-3 which KEPT,
   so they're likely valuable.

2. **Hard problem focus**: Hard problems have no "lone var absent" cases.
   The competition leader has 79.9% on hard. Analyzing our hard coverage
   specifically could reveal opportunities.

3. **XOR magma clarity**: The model may not be using XOR effectively. Adding
   a worked example of XOR catching a FALSE could help.

4. **Variable substitution**: The model might benefit from a note about
   variable renaming -- if Eq1 uses {x,y,z} and Eq2 uses {x,y,z,w}, the
   model needs to understand that Eq2 introduces a fresh variable.

5. **Duality exploitation**: If A=>B then dual(A)=>dual(B). This could
   help the model on problems where the dual is easier to reason about.

### What NOT to try
- DO NOT add more complex rules (composite n_vars=3,4 splits are too noisy)
- DO NOT rewrite the entire cheatsheet (cycles 1,4 showed this hurts)
- DO NOT add motivational text or behavioral instructions (waste of bytes)
- DO NOT try evolutionary optimization (tried 3 times, never beats seed)

---
name: experiment
description: "Run a cheatsheet optimization loop using SheetEvolve or hill-climbing. Use when user says 'experiment', 'iterate', 'optimize cheatsheet', or 'run SheetEvolve'."
disable-model-invocation: true
---

# Experiment — Cheatsheet Optimization

Run optimization experiments on the cheatsheet. Primary tool: SheetEvolve.

## Prerequisites
- `eval/evaluate.py` must exist and work
- `cheatsheets/current.txt` must exist (baseline)
- conda env `eq-distill` activated

## Option A: SheetEvolve (preferred)

```bash
# Dry run first (1 gen, 1 variant, small sample)
conda run -n eq-distill python optim/sheetevolve.py --stage1 --variants 1

# Full run
conda run -n eq-distill python optim/sheetevolve.py
```

## Option B: Manual hill-climbing loop

```
LOOP:
1. Read state: git log, results.tsv, current cheatsheet, active issue
2. Propose ONE atomic change to cheatsheets/current.txt
3. Validate size ≤10KB
4. Run: conda run -n eq-distill python eval/evaluate.py --cheatsheet cheatsheets/current.txt
5. Parse accuracy from RESULT line
6. If accuracy improved → keep change, present to user for approval
7. If accuracy same or worse → revert change
8. Log to results.tsv
9. Update issue Status header
10. Repeat
```

## results.tsv format
```
commit	accuracy	status	description
a1b2c3d	0.8900	keep	SheetEvolve gen2 best
```

## After experiment
- Update active issue Status header with results
- If new best → present to user, WAIT for approval before commit (I-NNN ref)
- If no improvement → document in issue Log why
- Log run in results.tsv

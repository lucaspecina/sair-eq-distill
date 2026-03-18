---
name: experiment
description: "Run a cheatsheet optimization loop (hill-climbing). Use when user says 'experiment', 'iterate on cheat sheet', or 'optimize cheatsheet'."
disable-model-invocation: true
---

# Experiment — Cheatsheet Optimization Loop

This is ONE approach (hill-climbing / Karpathy loop) for improving the cheatsheet.
It is NOT the only approach — see docs/RESEARCH.md for other tracks.

## Prerequisites
- `eval/evaluate.py` must exist and work
- `cheatsheets/current.txt` must exist (baseline)

## The Loop

```
LOOP:
1. Read state: git log, results.tsv, current cheatsheet
2. Propose ONE atomic change to cheatsheets/current.txt
3. Validate size ≤10KB
4. git commit -m "experiment: <description>"
5. Run: python eval/evaluate.py --cheatsheet cheatsheets/current.txt
6. Parse accuracy from RESULT line
7. If accuracy improved → keep commit
8. If accuracy same or worse → git reset HEAD~1
9. Log to results.tsv: commit, accuracy, status, description
10. Repeat
```

## results.tsv format
```
commit	accuracy	status	description
a1b2c3d	0.5000	keep	baseline
b2c3d4e	0.5520	keep	add commutativity rule
c3d4e5f	0.5100	discard	replace with verbose explanations
```

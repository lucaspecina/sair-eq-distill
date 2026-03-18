---
name: experiment
description: "Run the autoresearch experiment loop. Use when user says 'experiment', 'autoresearch', 'run loop', or 'iterate on cheat sheet'."
disable-model-invocation: true
---

# Experiment — Autoresearch Loop

Run the Karpathy-style autoresearch loop on the cheat sheet.

## Prerequisites
- `eval/evaluate.py` must exist and work
- `cheatsheets/current.txt` must exist (baseline)
- `program.md` must exist with instructions

## The Loop

Read `program.md` for full instructions. The core loop:

```
LOOP FOREVER:
1. Read state: git log, results.tsv, current cheatsheet
2. Propose ONE atomic change to cheatsheets/current.txt
3. Validate size ≤10KB
4. git commit -m "experiment: <description>"
5. Run: python eval/evaluate.py --cheatsheet cheatsheets/current.txt
6. Parse accuracy from output
7. If accuracy improved → keep commit
8. If accuracy same or worse → git reset HEAD~1
9. Log to results.tsv: commit, accuracy, status, description
10. NEVER STOP
```

## Rules
- ONE change per iteration. Atomic.
- Always validate ≤10KB before running.
- If experiment crashes: fix trivial errors, skip fundamental ones.
- Simpler is better at equal accuracy.
- Log EVERYTHING to results.tsv (including discards and crashes).

## results.tsv format
```
commit	accuracy	status	description
a1b2c3d	0.5000	keep	baseline
b2c3d4e	0.5520	keep	add commutativity rule
c3d4e5f	0.5100	discard	replace with verbose explanations
```

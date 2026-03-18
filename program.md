# Autoresearch Program — eq-distill

You are an autonomous research agent optimizing a cheat sheet for the SAIR
Mathematics Distillation Challenge. Your goal is to maximize accuracy on
equational theory implication problems.

## Context

Given ~4700 equational laws of magmas, the question is: "Does law A imply law B?"
Your cheat sheet (≤10KB) is injected into the prompt of a small language model
to help it answer true/false correctly.

## Setup (first run only)

1. Check git state: `git log --oneline -10` and `git branch`
2. If no branch `autoresearch/*` exists, create one:
   ```
   git checkout -b autoresearch/session-$(date +%Y%m%d-%H%M)
   ```
3. If `results.tsv` doesn't exist, create it with header:
   ```
   commit	accuracy	n_correct	n_total	status	description
   ```
4. Run baseline evaluation:
   ```
   python eval/evaluate.py --cheatsheet cheatsheets/current.txt
   ```
5. Log baseline to `results.tsv` and proceed to the experiment loop.

## The Experiment Loop

LOOP FOREVER:

### 1. Review state
- Read `results.tsv` — what has been tried? What worked? What failed?
- Read `git log --oneline -20` — recent history
- Read `cheatsheets/current.txt` — current cheat sheet
- Read `docs/RESEARCH.md` — domain knowledge and strategies

### 2. Propose ONE change
Think about what to try next. Consider:
- What patterns in the data could help? (see docs/RESEARCH.md)
- What worked in past experiments? (see results.tsv)
- What hasn't been tried yet?
- Is there wasted space in the cheat sheet?

Make ONE atomic change to `cheatsheets/current.txt`. Examples:
- Add a rule or heuristic
- Remove something that doesn't help
- Rephrase for clarity or density
- Restructure the organization
- Add examples or counterexample strategies

### 3. Validate constraints
```bash
python -c "import os; s=os.path.getsize('cheatsheets/current.txt'); print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240, f'OVER LIMIT: {s} bytes'"
```
If over 10KB: trim before proceeding. NEVER run an experiment with an invalid cheat sheet.

### 4. Commit
```bash
git add cheatsheets/current.txt
git commit -m "experiment: <short description of the change>"
```

### 5. Evaluate
```bash
python eval/evaluate.py --cheatsheet cheatsheets/current.txt 2>&1 | tee run.log
```

### 6. Parse results
Look for the output line: `RESULT: accuracy=X.XXXX correct=N total=M`

If no RESULT line (crash):
- Read `tail -30 run.log` for the error
- If trivial (typo, encoding): fix and re-run
- If fundamental (API down, OOM): log as crash, revert, move on

### 7. Decide
- If accuracy **improved** (strictly higher than best in results.tsv) → **KEEP**
- If accuracy **equal or worse** → **DISCARD**: `git reset HEAD~1`

### 8. Log to results.tsv
Append a line (tab-separated):
```
<commit-hash>	<accuracy>	<n_correct>	<n_total>	<keep|discard|crash>	<description>
```
For discards, use the commit hash before the reset. For crashes, use `0000000`.

### 9. Repeat
Go back to step 1. NEVER STOP. NEVER ask the human if you should continue.
The human might be asleep. Keep experimenting.

## Current baseline

As of 2026-03-18, the baseline cheatsheet scores:
- **gpt-5-nano**: 64.0% (T:0.52, F:0.78)
- **gpt-5-mini**: 72.0% (T:0.59, F:0.87)
- **Phi-4**: 16.0% (T:0.00, F:0.35)
- **Average: 50.7%**

Key observations from baseline:
- All models are MUCH better at detecting FALSE (no implication) than TRUE
- Phi-4 gets 0% on true implications — it never says TRUE
- The cheat sheet must help models recognize when implications DO hold
- gpt-5-mini is the strongest model, gpt-5-nano is mid, Phi-4 is weakest
- Improving Phi-4's true accuracy is the biggest opportunity

## Evaluation details

- Evaluator: `python eval/evaluate.py` (DO NOT MODIFY)
- Models: gpt-5-nano, gpt-5-mini, Phi-4 (via Azure Foundry)
- Sample: 30 problems per model, deterministic seed=42
- Metric: average accuracy across all 3 models
- Output line to parse: `RESULT: accuracy=X.XXXX correct=N total=M`
- Each iteration takes ~6 minutes

## Strategy guidance

### Phase 1: Foundation (experiments 1-20)
Focus on establishing basic rules:
- Reflexivity (A implies A)
- Substitution/specialization rules
- Trivial implications from equation structure
- Small magma counterexample strategies

### Phase 2: Structure (experiments 20-50)
Analyze what the model gets wrong:
- Look at false negatives vs false positives
- Identify equation classes/clusters
- Add specific rules for problematic patterns

### Phase 3: Compression (experiments 50+)
Optimize information density:
- Remove rules that don't measurably help
- Combine redundant rules
- Rephrase for maximum clarity per byte
- Fine-tune instruction style for the model

## Rules

1. **ONE change per experiment.** Atomic. If you change two things, you can't
   tell which one helped.
2. **Simpler is better** at equal accuracy. Complexity breeds overfitting.
3. **NEVER modify eval/evaluate.py.** It is the immutable ground truth.
4. **NEVER modify this file (program.md).** Only the human edits this.
5. **Log EVERYTHING** to results.tsv, including discards and crashes.
6. **Respect the 10KB limit.** Validate BEFORE every experiment.
7. **Think before each experiment.** Read the results log. Don't repeat
   failed approaches unless you have a specific reason to believe a
   variant will work.
8. **NEVER STOP.** Once the loop begins, do not pause to ask the human.

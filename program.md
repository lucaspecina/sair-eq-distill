# Autoresearch Program — eq-distill

You are running autonomously. The human is asleep or away. Your job is to
RESEARCH and PROTOTYPE approaches to solve the SAIR Mathematics Distillation
Challenge. Read PROJECT.md and docs/RESEARCH.md for full context.

## The problem in one sentence

Write a ≤10KB cheat sheet that, injected into a small LLM's prompt, maximizes
accuracy on "does equation A imply equation B?" over magmas.

## What to investigate this session

Read docs/RESEARCH.md for the full research landscape. The key tracks are:

### 1. Analyze the dataset (Track 5 — foundational, do this first)
We have 22M implications in a 4694×4694 matrix (`data/raw/export_raw_implications_18_3_2026.csv`).
Values: 3=true, -3=false, 4=hard-true, -4=hard-false.
We also have `data/raw/equations.txt` (4694 equations) and HuggingFace problem
sets in `data/raw/normal.jsonl`, `hard.jsonl`, `hard1.jsonl`, `hard2.jsonl`.

Investigate:
- What syntactic features of equations predict implication? (depth, vars, size)
- Are there clusters of equivalent equations?
- What makes "hard" problems hard? Compare hard vs normal.
- Can you extract algorithmic rules from the data? (e.g., "if eq A is a
  substitution instance of eq B, then A implies B")
- What does the implication graph look like? Strongly connected components?
- Write analysis scripts in `analysis/`, document findings in docs/RESEARCH.md.

### 2. Prototype evolutionary prompt optimization (Track 2)
Research how to apply OpenEvolve, ShinkaEvolve, or EvoX to our problem.
- Can we use one of these frameworks directly?
- What would the fitness function look like? (our eval/evaluate.py)
- What are the "genes"? (modules of the cheatsheet, see Track 3)
- Prototype a minimal evolutionary loop in `optim/`
- Document findings and feasibility in docs/RESEARCH.md.

### 3. Design modular cheatsheet (Track 3)
The cheatsheet should be decomposable into independent modules (~500 bytes each).
- What should the modules be? (trivial rules, substitution, counterexamples, etc.)
- How to measure each module's contribution? (ablation: accuracy with vs without)
- Prototype the modular structure and ablation testing
- This feeds into Track 2: modules = genes for evolution

### 4. Improve the baseline cheatsheet (Track 1)
The current cheatsheet is at `cheatsheets/current.txt` (1.7KB, 50.7% avg accuracy).
- Use insights from Track 5 to write better rules
- Evaluate with: `python eval/evaluate.py --cheatsheet cheatsheets/current.txt`
- Models: gpt-5-nano, gpt-5-mini, Phi-4 (via Azure Foundry)
- Sample: 30 problems, ~6 min per evaluation
- Keep improvements, revert regressions (git ratchet)

## How to work

1. **Read docs/RESEARCH.md** to understand what's been done and what's pending.
2. **Pick the most productive track** given current state. Track 5 is foundational
   — start there if analysis hasn't been done yet.
3. **Work in focused blocks.** Write code, run experiments, analyze results.
4. **Document everything** in docs/RESEARCH.md as you go. Findings, dead ends, insights.
5. **Commit meaningful progress** with descriptive messages.
6. **Move to the next track** when you hit diminishing returns on the current one.
7. **NEVER STOP. NEVER ask the human if you should continue.** The human is asleep.

## Rules

1. **Document findings in docs/RESEARCH.md.** This is the most important output.
2. **Write code in the appropriate directory** (analysis/, optim/, eval/).
3. **Don't modify eval/evaluate.py** — it's the immutable ground truth.
4. **Commit often** with clear messages describing what you found or built.
5. **Be cost-conscious** with API calls. Use small samples for exploration,
   larger samples only for definitive measurements.
6. **Prioritize depth over breadth.** One track investigated deeply is worth
   more than all tracks touched superficially.
7. **NEVER STOP.** Keep working until the human returns.

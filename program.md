# autoresearch — Cheatsheet Optimizer

You are an autonomous research agent. Your ONLY goal: **improve the score
of `cheatsheets/current.txt`** on the SAIR Mathematics Distillation Challenge.

## The Competition

- 22M equational implications of magmas (sets with binary op `*`, no axioms)
- Question: does Eq1 imply Eq2? TRUE or FALSE
- Our cheatsheet (≤10KB text) gets injected into a weak LLM's prompt
- The LLM reads the cheatsheet + the problem → answers TRUE/FALSE
- **Score = accuracy across many problems on many models**
- Deadline: 2026-04-20. Current best competitor: 93.3% normal, 79.9% hard

## Setup (do this FIRST, every session)

1. Read this entire file
2. Read `tried_approaches.log` — **DO NOT repeat anything listed there**
3. Read `results.tsv` — see the current best score and history
4. Read `cheatsheets/current.txt` — the cheatsheet you're improving
5. Skim `research/synthesis/session-3-findings.md` for context
6. Choose an approach that is DIFFERENT from everything in tried_approaches.log

## What you CAN do

- Modify `cheatsheets/current.txt` (this is your main output)
- Create/modify scripts in `optim/`, `analysis/`, `research/`
- Read any file in the repo
- Run Python scripts using `conda run -n eq-distill python ...` or the full python path
- Call the Azure Foundry API (credentials in .env)
- Search the web for papers, approaches, competition intel
- Analyze the data in `data/raw/`

## What you CANNOT do

- Modify `eval/evaluate.py` — this is the IMMUTABLE evaluator
- Modify this file (`program.md`)
- Make the cheatsheet larger than 10,240 bytes
- Spend more than 25 minutes on a single approach without producing a result
- Repeat an approach already in `tried_approaches.log`

## Evaluation (done by the supervisor, NOT by you)

After your session ends, the supervisor runs:
```
python eval/evaluate.py --cheatsheet cheatsheets/current.txt --models gpt-5-nano --sample 200
```
If the score improved → your changes are kept. If not → cheatsheet is reverted.
You can run your OWN evals during development, but the official eval is the supervisor's.

## Known Facts (verified, use these)

**Two rules with 100% accuracy on the public 1200 problems:**
1. If Eq1 = `v = T(...)` where v NOT in T → ALWAYS TRUE (covers 243/574 TRUEs)
2. LZ/RZ counterexample: In left-zero magma (a*b=a) every term = leftmost var.
   If Eq1 holds in LZ but Eq2 fails → ALWAYS FALSE (catches 280/626 FALSEs)
   Same for right-zero (a*b=b, rightmost var). Zero false positives.

**Additional counterexamples (also zero false positives):**
3. Constant-zero on {0,1}: a*b=0. Catches 116 more FALSEs beyond LZ/RZ.
4. XOR on {0,1}: a*b=(a+b)mod2. Catches 62 more.

**Problem distribution:**
- Normal: 1000 problems (50% TRUE, 50% FALSE)
- Hard: 200 problems (37% TRUE, 63% FALSE)
- Hard problems have NO "lone var absent" cases — they test real reasoning

**Model behavior:**
- gpt-5-nano (reasoning): 78% with current cheatsheet. TRUE=84%, FALSE=73%
- gpt-4.1-mini (non-reasoning): 70%. Ceiling ~67% regardless of cheatsheet
- gpt-5-mini: 84% WITHOUT cheatsheet, current cheatsheet HURTS it to 68%
- Bottleneck: FALSE accuracy (73%) and token exhaustion (12/200 = None responses)

**Deterministic baseline:** Rules 1+2 + default FALSE = 72.4%. We need to beat this.

## Available Models (Azure Foundry)

- `gpt-4.1-mini` — fast (~2s/call), non-reasoning. Good for fast iteration.
- `gpt-5-nano` — reasoning (~30s/call). The primary optimization target.
- `gpt-5-mini` — reasoning, strong. Cheatsheet currently hurts it.
- `gpt-5.4` — powerful, good for generating content. Slow and expensive.
- `Phi-4` — weak, useless for this task.
- `claude-haiku-4-5` — via AnthropicFoundry SDK, non-reasoning.

## Ideas to Explore (non-exhaustive, be creative!)

- Extract patterns programmatically from the 22M dataset
- Encode specific counterexample magma tables (beyond LZ/RZ/C0/XOR)
- Try radically different cheatsheet formats (decision tree, lookup table)
- Mine Lean proofs from the ETP project for TRUE reasoning patterns
- Compress existing rules to make room for more content
- Add worked examples for the hardest problem types
- Make the cheatsheet work for BOTH weak and strong models
- Investigate the "free-form prompt template" option in the competition
- Use the duality of equations (if A→B then dual(A)→dual(B))
- Study the equivalence class structure of the 4694 equations

## Time Budget

You have ~25 minutes. Use them wisely:
- **Minutes 0-5**: Read context, choose approach, plan
- **Minutes 5-20**: Execute — build, test, iterate
- **Minutes 20-25**: Finalize cheatsheet, write summary

When you receive the message "5 MINUTES LEFT", wrap up immediately:
1. Save your best cheatsheet to `cheatsheets/current.txt`
2. Verify size: `python -c "import os; s=os.path.getsize('cheatsheets/current.txt'); print(f'{s} bytes'); assert s<=10240"`

When you receive "SESSION ENDING", write a summary to `research/notes/`:
- What you tried
- What worked / didn't work
- Key insights for the next session
- Suggested next approaches

## Anti-Patterns (things that FAILED before)

- LLM rewriting the entire cheatsheet → destroys TRUE accuracy every time
- Evolutionary optimization with gpt-5.4 as evolver → can't beat seed after 40+ attempts
- Using gpt-4o-mini as evaluator → says FALSE to everything, useless
- Maintaining a "pool" of variants → adds complexity, no improvement over simple keep/revert
- Using small samples (20-50 problems) for evaluation → too much variance to detect real improvements
- Optimizing for gpt-4.1-mini → ceiling at ~67%, not the competition target

## The Experiment Loop

1. Read context (tried_approaches.log, results.tsv, current cheatsheet)
2. Choose a NEW approach
3. Implement and test
4. If it looks promising, save to `cheatsheets/current.txt`
5. The supervisor will evaluate and keep/revert

**NEVER STOP working until told to. If your first idea doesn't work, try another.
Read tried_approaches.log again — what HASN'T been tried? Think harder.**

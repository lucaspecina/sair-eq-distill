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
5. **BACKUP current.txt immediately:** `cp cheatsheets/current.txt cheatsheets/session_backup.txt`
6. Reset API logger: `python -c "import sys; sys.path.insert(0,'.'); from optim.api_logger import reset_log; reset_log()"`
7. Skim `research/synthesis/session-3-findings.md` for context
8. Choose an approach that is DIFFERENT from everything in tried_approaches.log

**IMPORTANT:** Only overwrite `cheatsheets/current.txt` with a version that scored
BETTER than the backup on a quick eval. If nothing beats it, restore the backup
before your session ends.

## CRITICAL: Build Systems, Don't Edit By Hand

**DO NOT manually edit `cheatsheets/current.txt`.** Instead, build a script or
system that GENERATES a better cheatsheet. Your output is a PROGRAM that
produces the cheatsheet, not the cheatsheet itself.

Examples of what you SHOULD do:
- Write a Python script that analyzes error patterns and generates improved rules
- Build an optimizer that calls an LLM to rewrite specific sections based on errors
- Create a data pipeline that extracts patterns from the 22M dataset and encodes them
- Write a script that compresses existing rules to make room for new content
- Build a system that tests N variants and picks the best one

Examples of what you should NOT do:
- Open current.txt and manually rewrite a paragraph
- Copy-paste a new version of the cheatsheet you wrote yourself
- "Tweak" the wording by hand

**Why?** Manual edits are not reproducible, not measurable, and don't scale.
A system can iterate, test, and improve beyond what manual editing can achieve.

Your final step: your script writes the result to `cheatsheets/current.txt`.
The supervisor will then evaluate it with the official eval.

## What you CAN do

- **Create/modify scripts** in `optim/`, `analysis/`, `research/`
- Read any file in the repo
- Run Python: `/c/Users/YT40432/miniconda3/envs/eq-distill/python.exe -u script.py`
- Call Azure Foundry LLMs (see below for API details)
- Search the web for papers, approaches, competition intel
- Analyze the data in `data/raw/` (normal.jsonl, hard.jsonl — 1200 problems total)
- Study existing optimizers in `optim/` for inspiration (evolve_append.py, evolve_v2.py, etc.)

## What you CANNOT do

- Modify `eval/evaluate.py` — this is the IMMUTABLE evaluator
- Modify this file (`program.md`)
- Make the cheatsheet larger than 10,240 bytes
- Spend more than 25 minutes on a single approach without producing a result
- Repeat an approach already in `tried_approaches.log`
- Manually edit `cheatsheets/current.txt` by hand (build a system instead!)

## Azure Foundry API — How to Call Models

**MANDATORY: Use the logged client for ALL API calls.** This logs every call
to `api_calls.log` so we can track API spend.

```python
import sys; sys.path.insert(0, '.')
from optim.api_logger import get_logged_client, get_logged_async_client, get_call_count, reset_log

# FIRST THING: reset the log at session start
reset_log()

# Sync client:
client = get_logged_client()
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[{"role": "user", "content": "your prompt here"}],
    max_completion_tokens=16384,
)
print(response.choices[0].message.content)

# Check how many calls you've made:
print(f"API calls so far: {get_call_count()}")
```

For async (parallel calls):
```python
import sys; sys.path.insert(0, '.')
from optim.api_logger import get_logged_async_client, get_call_count
import asyncio

client = get_logged_async_client()

async def call(prompt):
    r = await client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=16384,
    )
    return r.choices[0].message.content

# Run many in parallel:
results = asyncio.run(asyncio.gather(*[call(p) for p in prompts]))
```

### Available Models

| Model | Speed | Type | Use for |
|-------|-------|------|---------|
| `gpt-4.1-mini` | ~2s/call | non-reasoning | Fast iteration, screening |
| `gpt-5-nano` | ~30s/call | reasoning | **Primary optimization target** |
| `gpt-5-mini` | ~10s/call | reasoning | Strong, but current CS hurts it |
| `gpt-5.4` | ~60s/call | powerful | Generating content, analysis |
| `gpt-5.2-codex` | ~10s/call | code-focused | Code generation tasks |
| `Phi-4` | ~2s/call | weak | Useless for this task |
| `claude-haiku-4-5` | ~3s/call | non-reasoning | Alternative perspective |

There are also larger models (gpt-5.4-pro, claude-opus-4-6) but they are expensive.
Use gpt-5.4 for content generation and gpt-5-nano for evaluation.

## How Evaluation Works

Understanding this is critical — it's the ONLY thing that decides if your work is kept.

### The mechanism

1. The eval script loads problems from `data/raw/normal.jsonl` + `data/raw/hard.jsonl`
2. It samples N problems (default 200: 160 normal + 40 hard, random each time)
3. For each problem, it builds a prompt using the **SAIR competition template**:
   ```
   You are a mathematician specializing in equational theories of magmas.
   Your task is to determine whether Equation 1 ({eq1}) implies Equation 2 ({eq2}).
   {cheatsheet_content}
   Output format: VERDICT: TRUE or FALSE, REASONING, PROOF/COUNTEREXAMPLE.
   ```
4. The cheatsheet is injected **inline** in the user message — it's just text the model reads
5. The model responds, the script parses `VERDICT: TRUE/FALSE`, compares to ground truth
6. Score = correct / total

### Official eval (done by the supervisor after your session)

```bash
/c/Users/YT40432/miniconda3/envs/eq-distill/python.exe -u eval/evaluate.py \
  --cheatsheet cheatsheets/current.txt \
  --models gpt-5-nano \
  --sample 200 --concurrent 20
```
- Model: **gpt-5-nano** (reasoning, ~30s/call) — the primary competition target
- 200 problems, random sample each time
- Output line: `RESULT: accuracy=0.XXXX correct=N total=N`
- This is the ONLY score that decides keep or revert

### Intermediate eval (for you, during development)

Same script, fewer problems = faster. Use this to test your work during the session:

```bash
# Quick check: 30 problems, ~5 min
/c/Users/YT40432/miniconda3/envs/eq-distill/python.exe -u eval/evaluate.py \
  --cheatsheet cheatsheets/current.txt \
  --models gpt-5-nano \
  --sample 30 --concurrent 20
```

With 30 problems the variance is high (~±10%), but it's enough to detect if you
broke something or if your approach is in the right direction.

### API BUDGET — CRITICAL

**You may ONLY run 30-problem evals** (--sample 30). NEVER run 200-problem evals.
The coordinator will run the official 200-problem eval AFTER your session ends.

Maximum evals per session: **5 quick evals** (5 × 30 = 150 API calls max).
Each eval costs real money. Be strategic about when you evaluate.

### Importing eval functions in your scripts
```python
import sys; sys.path.insert(0, '.')
from eval.evaluate import build_prompt, load_problems, parse_verdict
```

## Existing Optimizers (study these!)

There are working optimizer scripts in `optim/` you can study, modify, or extend:

- **`optim/evolve_append.py`** — Appends new sections without rewriting base.
  Shows errors to gpt-5.4, which generates a new section to append.
- **`optim/evolve_v2.py`** — Full evolutionary optimizer with crossover mutations.
  Pool of variants, tournament selection, error-driven mutation.
- **`optim/evolve_cheatsheet.py`** — Original v1 optimizer. Simple mutation only.

These import from `eval/evaluate.py` and use the Azure Foundry API.
You can fork them, combine ideas, or build something completely new.

## What the Cheatsheet Should Contain

The cheatsheet is read by an LLM that needs to solve MATH PROBLEMS.
The core should be **mathematical hints and rules** that help it get specific problems right.

**The bulk — mathematical content:**
- Rules for determining TRUE/FALSE (e.g., "if lone variable absent → TRUE")
- Counterexample magma tables (LZ, RZ, constant-zero, XOR, others)
- Decision procedures (step-by-step: check rule 1, then rule 2, etc.)
- Worked examples of tricky cases
- Mathematical patterns extracted from data
- Compressed encodings of proven relationships

**Also OK — basic behavioral framing:**
- A brief header explaining what the cheatsheet is about
- Instructions like "check these rules in order" (it's a procedure)
- Warnings like "do NOT assume TRUE without proof"

**Avoid — things that waste bytes:**
- Long explanations of what a magma is (the LLM already knows)
- Motivational text ("think carefully", "be systematic")
- Statistical patterns ("70% of problems are FALSE") — the LLM should reason, not guess

Think of it as: **a reference card a math student would use during an exam**.
Mostly formulas, rules, and examples. A few words of guidance on how to use them.

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
- Use an LLM to analyze errors and generate targeted fixes (then encode as rules)
- Build a search over cheatsheet formats: same content, different structure
- Use gpt-5.4 to generate candidate rules, then validate programmatically

## Time Budget

You have ~25 minutes. You will be KILLED without warning at 25 min.
- **Minutes 0-3**: Read context, choose approach, plan. Be FAST here.
- **Minutes 3-18**: Execute — build, test, iterate.
- **Minutes 18-20**: Save best cheatsheet to `cheatsheets/current.txt`, verify size.
- **Minutes 20-23**: Write summary to `research/notes/cycle_N.md`. MANDATORY.

**You will NOT receive any warning.** Document proactively before minute 20.
Write to `research/notes/cycle_N.md` (use next available number):
- What approach you tried
- What worked / didn't work (with eval numbers)
- Key insights for the next worker
- Suggested next approaches
- **API calls made** (run: `python -c "print(open('api_calls.log').read())"`)
- **Scripts created** (list any new files you wrote)

## Anti-Patterns (things that FAILED before)

- **Manually editing the cheatsheet** → not reproducible, doesn't scale
- LLM rewriting the entire cheatsheet → destroys TRUE accuracy every time
- Evolutionary optimization with gpt-5.4 as evolver → can't beat seed after 40+ attempts
- Using gpt-4o-mini as evaluator → says FALSE to everything, useless
- Maintaining a "pool" of variants → adds complexity, no improvement over simple keep/revert
- Using small samples (20-50 problems) for evaluation → too much variance to detect real improvements
- Optimizing for gpt-4.1-mini → ceiling at ~67%, not the competition target

## The Experiment Loop

1. Read context (tried_approaches.log, results.tsv, current cheatsheet)
2. Choose a NEW approach
3. **Build a system** (script) that implements it
4. Test with quick eval (gpt-5-nano, 30 problems)
5. If promising, run your script to write `cheatsheets/current.txt`
6. The supervisor will evaluate with the official eval and keep/revert

**NEVER STOP working until told to. If your first idea doesn't work, try another.
Read tried_approaches.log again — what HASN'T been tried? Think harder.**

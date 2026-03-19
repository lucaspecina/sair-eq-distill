"""Ablation study: which parts of v6 cheatsheet contribute most?

Creates variants of v6 with one section removed at a time,
evaluates each, and reports the accuracy drop.
"""

import os
import sys
import json
import asyncio
import re
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

ENDPOINT = os.getenv("AZURE_FOUNDRY_BASE_URL", "")
API_KEY = os.getenv("AZURE_INFERENCE_CREDENTIAL", "")
MODEL = "gpt-5-mini"
SAMPLE_SIZE = 15
MAX_TOKENS = 16384

EVAL_PROMPT = """You are a mathematician specializing in equational theories of magmas. \
Your task is to determine whether Equation 1 ({eq1}) implies Equation 2 ({eq2}) over all magmas.
{cheatsheet}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise."""


def parse_verdict(text):
    match = re.search(r"VERDICT:\s*(TRUE|FALSE)", text, re.IGNORECASE)
    if match:
        return match.group(1).upper() == "TRUE"
    return None


async def eval_cheatsheet(cheatsheet_text, problems):
    """Evaluate a cheatsheet variant on a set of problems."""
    client = AsyncOpenAI(base_url=ENDPOINT, api_key=API_KEY)
    sem = asyncio.Semaphore(3)

    async def eval_single(p):
        prompt = EVAL_PROMPT.format(
            eq1=p["equation1"], eq2=p["equation2"], cheatsheet=cheatsheet_text
        )
        async with sem:
            try:
                r = await client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_completion_tokens=MAX_TOKENS,
                )
                text = r.choices[0].message.content or ""
                pred = parse_verdict(text)
                return pred == p["answer"]
            except Exception:
                return False

    tasks = [eval_single(p) for p in problems]
    results = await asyncio.gather(*tasks)
    return sum(1 for r in results if r) / len(results)


# Define v6 sections
V6_SECTIONS = {
    "header": """# Magma Equation Implication — Decision Guide

Given Eq1 and Eq2, decide: does Eq1 imply Eq2 over all magmas?
A magma is a set with a binary operation *. Eq1 implies Eq2 means every magma satisfying Eq1 also satisfies Eq2.

## STATISTICS: 37% TRUE, 63% FALSE""",

    "fast_checks": """## FAST CHECKS (do first, takes seconds):
- Eq1 and Eq2 identical? → TRUE
- Eq2 is "x = x"? → TRUE
- Eq1 has form "x = y" or forces all elements equal? → TRUE (implies everything)
- Eq2 uses more distinct variables than Eq1? → lean FALSE
- Eq1 has more "free" variables (RHS vars not in LHS) than Eq2? → lean TRUE""",

    "substitution": """## THE KEY TECHNIQUE: SUBSTITUTION PROOF (spend most time here)

This is how 40% of TRUE implications are proven. ALWAYS try this before saying FALSE.

Since Eq1 holds for ALL values of its variables, you can replace any variable with ANY term.

### How to do it:
1. Write down Eq1: LHS1 = RHS1
2. Look at Eq2: LHS2 = RHS2. What do you need to show?
3. Try substituting variables in Eq1 to make it look like Eq2:
   - Set y := x (identify variables)
   - Set y := x*z (replace with a product)
   - Set z := x*x (replace with a self-product)
4. Apply Eq1 multiple times if needed.
5. If you can derive LHS2 = RHS2 → TRUE.

### Common successful patterns:
- Set all extra variables equal to x → simplifies to fewer variables
- Substitute the LHS of Eq2 into Eq1 → may produce RHS of Eq2
- If Eq1 has form "x = f(y,...)", substitute f(y,...) for x in Eq1 again""",

    "forced_ops": """## DETECTING FORCED OPERATIONS

If Eq1 forces the operation into one of these forms, most equations follow:

### Constant operation (x*y = c for all x,y):
If Eq1 has no shared variables between LHS and RHS → constant → TRUE for most Eq2.
Example: "x*y = z*w" forces constant operation.

### Right projection (x*y = y for all x,y):
If Eq1 lets you show some element e has e*x = x (left identity),
and then ALL elements are left identities → x*y = y.
Then check: does right projection satisfy Eq2? Usually yes → TRUE.

### Left projection (x*y = x for all x,y):
Similar but with right identity (x*e = x).""",

    "counterexample": """## IF SUBSTITUTION FAILS: COUNTEREXAMPLE

Only after trying substitution. Check 2-element magma {0,1}:

Table 1: 0*0=0, 0*1=0, 1*0=0, 1*1=1 (satisfies few equations)
Table 2: 0*0=1, 0*1=0, 1*0=0, 1*1=0 (satisfies very few equations)

For each table: satisfies Eq1 but not Eq2? → FALSE.""",

    "warnings": """## COMMON MISTAKES TO AVOID
- Saying FALSE without trying substitution (the #1 error!)
- Saying FALSE because "I can't see how" — try harder at substitution
- Building counterexample tables BEFORE trying to prove TRUE
- Claiming the implication is "trivially false" — this is rarely correct

## DEFAULT: If truly uncertain after all steps → FALSE (63% base rate)""",
}


async def main():
    # Load problems
    random.seed(42)
    with open("data/raw/normal.jsonl") as f:
        problems = [json.loads(line) for line in f]
    problems = random.sample(problems, SAMPLE_SIZE)

    # Full v6
    full = "\n\n".join(V6_SECTIONS.values())
    print(f"Full v6: {len(full)} bytes")

    # Evaluate full v6
    print("\nEvaluating full v6...")
    t0 = time.time()
    full_acc = await eval_cheatsheet(full, problems)
    print(f"  Full v6: {full_acc:.1%} ({time.time()-t0:.0f}s)")

    # Evaluate with each section removed
    for section_name in V6_SECTIONS:
        variant = "\n\n".join(
            text for name, text in V6_SECTIONS.items() if name != section_name
        )
        print(f"\nEvaluating without '{section_name}' ({len(V6_SECTIONS[section_name])} bytes removed)...")
        t0 = time.time()
        acc = await eval_cheatsheet(variant, problems)
        drop = full_acc - acc
        print(f"  Without {section_name}: {acc:.1%} (drop: {drop:+.1%}) ({time.time()-t0:.0f}s)")

    # Evaluate with NO cheatsheet
    print("\nEvaluating with empty cheatsheet...")
    t0 = time.time()
    empty_acc = await eval_cheatsheet("", problems)
    print(f"  No cheatsheet: {empty_acc:.1%} ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    asyncio.run(main())

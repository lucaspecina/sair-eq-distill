"""
Prototype for using OpenEvolve to evolve the cheatsheet.

The cheatsheet text is the "program" with EVOLVE-BLOCK markers.
The evaluator runs our multi-model accuracy pipeline.

NOTE: This is a PROTOTYPE. Not yet ready to run — needs config tuning.
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_initial_cheatsheet():
    """Create the initial cheatsheet with EVOLVE-BLOCK markers."""
    # The entire cheatsheet is evolvable
    content = """# Equational Implication Solver
# EVOLVE-BLOCK-START

Determine if Equation 1 implies Equation 2 over all magmas.
"Eq1 implies Eq2" = every magma satisfying Eq1 must also satisfy Eq2.

## KEY FACTS
- About 37% of pairs are TRUE, 63% FALSE. When uncertain, lean FALSE.
- Implication is transitive: if A→B and B→C then A→C.
- Equations with MORE distinct variables are generally STRONGER.
- Variables on the RHS not appearing on LHS = "free" = MORE restrictive.

## PROCEDURE
1. Equations identical? → TRUE. Eq2 is "x = x"? → TRUE.
2. Does Eq1 force projection (x*y=y) or constant operation? → likely TRUE.
3. Can you substitute variables in Eq1 to derive Eq2? → TRUE.
4. Does Eq2 have free variables Eq1 can't constrain? → likely FALSE.
5. Check 2-element magma {0,1} with table 01/10: satisfies Eq1 but not Eq2? → FALSE.
6. Default → FALSE.

## PROOF TECHNIQUE: Left Identity
If Eq1 lets you construct an element e where e*x = x for all x,
then the operation is right-projection (x*y = y), and most equations follow.

# EVOLVE-BLOCK-END
"""
    return content


def create_evaluator_script():
    """Create the evaluator script that OpenEvolve will call."""
    script = '''
import json
import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

MODELS = os.getenv("EVAL_MODELS", "gpt-5-nano,gpt-5-mini").split(",")
ENDPOINT = os.getenv("AZURE_FOUNDRY_BASE_URL", "")
API_KEY = os.getenv("AZURE_INFERENCE_CREDENTIAL", "")
SAMPLE_SIZE = 20  # Small sample for fast evolution
MAX_CONCURRENT = 6
MAX_TOKENS = int(os.getenv("EVAL_MAX_TOKENS", "4096"))

PROMPT_TEMPLATE = """You are a mathematician specializing in equational theories of magmas. \\
Your task is to determine whether Equation 1 ({equation1}) implies Equation 2 ({equation2}) over all magmas.
{cheatsheet}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise."""

import re
def parse_verdict(text):
    match = re.search(r"VERDICT:\\s*(TRUE|FALSE)", text, re.IGNORECASE)
    if match:
        return match.group(1).upper() == "TRUE"
    return None

async def evaluate_single(client, model, cheatsheet, problem, sem):
    prompt = PROMPT_TEMPLATE.format(
        equation1=problem["equation1"],
        equation2=problem["equation2"],
        cheatsheet=cheatsheet,
    )
    async with sem:
        try:
            r = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=MAX_TOKENS,
            )
            text = r.choices[0].message.content or ""
            pred = parse_verdict(text)
            return pred == problem["answer"]
        except:
            return False

async def evaluate(cheatsheet_path):
    cs = Path(cheatsheet_path).read_text(encoding="utf-8")
    # Strip EVOLVE-BLOCK markers
    cs = cs.replace("# EVOLVE-BLOCK-START", "").replace("# EVOLVE-BLOCK-END", "").strip()

    # Check size
    cs_bytes = len(cs.encode("utf-8"))
    if cs_bytes > 10240:
        return {"score": 0.0, "error": f"Over 10KB: {cs_bytes} bytes"}

    # Load problems
    import random
    random.seed(42)
    with open("data/raw/normal.jsonl") as f:
        problems = [json.loads(line) for line in f]
    problems = random.sample(problems, SAMPLE_SIZE)

    client = AsyncOpenAI(base_url=ENDPOINT, api_key=API_KEY)
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    tasks = []
    for model in MODELS:
        for p in problems:
            tasks.append(evaluate_single(client, model, cs, p, sem))

    results = await asyncio.gather(*tasks)
    accuracy = sum(1 for r in results if r) / len(results)

    return {
        "score": accuracy,
        "accuracy": accuracy,
        "n_correct": sum(1 for r in results if r),
        "n_total": len(results),
        "cheatsheet_bytes": cs_bytes,
    }

if __name__ == "__main__":
    cheatsheet_path = sys.argv[1]
    result = asyncio.run(evaluate(cheatsheet_path))
    print(json.dumps(result))
'''
    return script


def create_config():
    """Create OpenEvolve configuration for cheatsheet evolution."""
    config = {
        "max_iterations": 50,
        "random_seed": 42,
        "llm": {
            "models": [
                {
                    "name": "gpt-5.3-chat",  # Use a strong model for mutations
                    "provider": "openai",
                    "api_key": os.getenv("AZURE_INFERENCE_CREDENTIAL", ""),
                    "base_url": os.getenv("AZURE_FOUNDRY_BASE_URL", ""),
                    "temperature": 0.7,
                    "weight": 1.0,
                }
            ]
        },
        "database": {
            "population_size": 20,
            "num_islands": 2,
            "migration_interval": 10,
        },
        "evaluator": {
            "timeout": 600,  # 10 min per evaluation
            "cascade_evaluation": False,
        },
        "prompt": {
            "system_message": (
                "You are evolving a cheat sheet for equational theory implication problems. "
                "The cheat sheet must be ≤10KB and help small LLMs determine if one equation "
                "implies another over all magmas. Focus on: proof techniques (substitution, "
                "left identity, constant operation detection), counterexample strategies, "
                "and variable structure analysis. Be creative but precise."
            ),
        },
    }
    return config


if __name__ == "__main__":
    print("OpenEvolve Cheatsheet Evolution Setup")
    print("=" * 50)

    # Create files
    cs = create_initial_cheatsheet()
    ev = create_evaluator_script()
    cfg = create_config()

    # Save
    Path("optim/oe_cheatsheet.txt").write_text(cs, encoding="utf-8")
    Path("optim/oe_evaluator.py").write_text(ev, encoding="utf-8")
    with open("optim/oe_config.yaml", "w") as f:
        import yaml
        yaml.dump(cfg, f, default_flow_style=False)

    print(f"Created: optim/oe_cheatsheet.txt ({len(cs)} bytes)")
    print(f"Created: optim/oe_evaluator.py")
    print(f"Created: optim/oe_config.yaml")
    print(f"\nTo run:")
    print(f"  openevolve optim/oe_cheatsheet.txt optim/oe_evaluator.py --config optim/oe_config.yaml")

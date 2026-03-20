"""
Evolutionary cheatsheet optimizer — AlphaEvolve-inspired.

Architecture:
- EVALUATOR MODEL (nano): takes the exam, cheap and fast
- EVOLVER MODEL (mini): reads exam results, improves the cheatsheet

Loop:
1. Nano takes exam with cheatsheet → score + raw errors
2. Mini sees: cheatsheet + nano's wrong answers → generates improved cheatsheet
3. Nano takes NEW exam with new cheatsheet (fresh random problems)
4. If score improves → enters pool
5. Repeat

Usage:
    python optim/evolve_cheatsheet.py --seed cheatsheets/v15_concise.txt
    python optim/evolve_cheatsheet.py --seed cheatsheets/v15_concise.txt --generations 10 --variants 5
"""

import argparse
import asyncio
import json
import os
import random
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.evaluate import build_prompt, evaluate_single, load_problems, parse_verdict

load_dotenv()

DEFAULT_ENDPOINT = os.getenv("AZURE_FOUNDRY_BASE_URL", "")
DEFAULT_API_KEY = os.getenv("AZURE_INFERENCE_CREDENTIAL", "")

# Models
EVAL_MODEL = "gpt-4.1-mini"    # the "student" — takes the exam (fast, no reasoning)
EVOLVER_MODEL = "gpt-5.4"      # the "teacher" — improves the cheatsheet

# Eval config
EVAL_NORMAL = 80
EVAL_HARD = 20
EVAL_CONCURRENT = 50  # aggressive parallelism

# Evolution config
POOL_SIZE = 5
VARIANTS_PER_GEN = 3

# Data paths
NORMAL_PATH = "data/raw/normal.jsonl"
HARD_PATH = "data/raw/hard.jsonl"


async def evaluate_cheatsheet(
    client: AsyncOpenAI,
    cheatsheet_text: str,
    problems: list[dict],
    model: str = EVAL_MODEL,
) -> dict:
    """Evaluate cheatsheet on given problems. Returns score + per-problem details."""
    sem = asyncio.Semaphore(EVAL_CONCURRENT)
    tasks = [
        evaluate_single(client, model, cheatsheet_text, p, sem)
        for p in problems
    ]
    results = await asyncio.gather(*tasks)

    correct = sum(1 for r in results if r.get("correct"))
    total = len(results)
    errors = [r for r in results if not r.get("correct")]

    return {
        "score": correct / total if total > 0 else 0,
        "correct": correct,
        "total": total,
        "errors": errors,
        "all_results": results,
    }


def format_errors_for_evolver(errors: list[dict], max_errors: int = 8) -> str:
    """Format raw errors into context for the evolver LLM."""
    if not errors:
        return "No errors — perfect score!"

    # Sample diverse errors if too many
    if len(errors) > max_errors:
        errors = random.sample(errors, max_errors)

    lines = []
    for e in errors:
        eid = e.get("id", "?")
        expected = "TRUE" if e.get("expected") else "FALSE"
        predicted = "TRUE" if e.get("predicted") else ("FALSE" if e.get("predicted") is False else "NO_ANSWER")
        raw = (e.get("raw_response") or "(empty — model ran out of tokens)")[:300]
        lines.append(
            f"Problem {eid}: correct={expected}, model_said={predicted}\n"
            f"  Model reasoning: {raw}\n"
        )
    return "\n".join(lines)


def sample_problems(normal: list, hard: list, n_normal: int, n_hard: int) -> list:
    """Sample problems with random seed (fresh each time)."""
    sampled = random.sample(normal, min(n_normal, len(normal)))
    sampled += random.sample(hard, min(n_hard, len(hard)))
    random.shuffle(sampled)
    return sampled


EVOLVER_PROMPT = """You are improving a cheatsheet (≤10KB) that helps a weak LLM predict whether one equational law implies another over magmas (binary operation *, no axioms like associativity).

CURRENT CHEATSHEET (score: {score:.0%} — {correct}/{total} correct):
---
{cheatsheet}
---

HERE ARE THE PROBLEMS THE MODEL GOT WRONG (with its reasoning):
{error_details}

The cheatsheet should have two parts:
1. A short decoder section explaining any notation or vocabulary you use
2. Dense, compressed mathematical rules and patterns that help solve these problems

Generate an improved version. Focus on fixing the failure patterns you see above.
Keep it under 10KB. Output ONLY the cheatsheet text."""


async def evolve_variant(
    client: AsyncOpenAI,
    parent_text: str,
    parent_score: float,
    parent_correct: int,
    parent_total: int,
    error_details: str,
) -> str:
    """Ask the evolver model to generate an improved cheatsheet."""
    prompt = EVOLVER_PROMPT.format(
        cheatsheet=parent_text,
        score=parent_score,
        correct=parent_correct,
        total=parent_total,
        error_details=error_details,
    )
    try:
        resp = await client.chat.completions.create(
            model=EVOLVER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=8192,
        )
        text = (resp.choices[0].message.content or "").strip()
        # Strip markdown fences
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        text = text.strip()

        size = len(text.encode("utf-8"))
        if size > 10240:
            text = text[:10240].rsplit("\n", 1)[0]
        if size < 50:
            return ""
        return text
    except Exception as e:
        print(f"    Evolution failed: {e}")
        return ""


async def run_evolution(
    seed_path: str,
    n_variants: int,
    n_generations: int,
    endpoint: str,
    api_key: str,
    output_dir: str,
):
    """Main evolutionary loop."""
    client = AsyncOpenAI(base_url=endpoint, api_key=api_key)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load problems
    all_normal = load_problems(NORMAL_PATH)
    all_hard = load_problems(HARD_PATH)
    print(f"Loaded {len(all_normal)} normal + {len(all_hard)} hard problems")

    # Load seed
    seed_text = Path(seed_path).read_text(encoding="utf-8")
    print(f"\n=== EVOLUTIONARY CHEATSHEET OPTIMIZER ===")
    print(f"Seed: {seed_path} ({len(seed_text.encode('utf-8'))} bytes)")
    print(f"Evaluator: {EVAL_MODEL} | Evolver: {EVOLVER_MODEL}")
    print(f"Per eval: {EVAL_NORMAL} normal + {EVAL_HARD} hard, concurrency {EVAL_CONCURRENT}")
    print(f"Variants/gen: {n_variants} | Generations: {n_generations}")

    # Evaluate seed
    print(f"\n--- Evaluating seed ---")
    seed_problems = sample_problems(all_normal, all_hard, EVAL_NORMAL, EVAL_HARD)
    seed_result = await evaluate_cheatsheet(client, seed_text, seed_problems)
    print(f"Seed: {seed_result['score']:.0%} ({seed_result['correct']}/{seed_result['total']})")

    # Init pool
    pool = [{
        "text": seed_text,
        "score": seed_result["score"],
        "name": "seed",
        "size": len(seed_text.encode("utf-8")),
    }]
    best_ever = pool[0].copy()
    history = [{"gen": 0, "name": "seed", "score": seed_result["score"]}]

    for gen in range(1, n_generations + 1):
        t0 = time.time()
        print(f"\n{'='*60}")
        print(f"GEN {gen}/{n_generations} | Best: {best_ever['score']:.0%} | Pool: {len(pool)}")
        print(f"{'='*60}")

        # 1. Sample problems for this generation (SAME set for parents AND variants)
        gen_problems = sample_problems(all_normal, all_hard, EVAL_NORMAL, EVAL_HARD)
        print(f"  Evaluating parents on {len(gen_problems)} problems...")
        parent_evals = []
        eval_tasks = [
            evaluate_cheatsheet(client, p["text"], gen_problems)
            for p in pool
        ]
        eval_results = await asyncio.gather(*eval_tasks)
        for p, result in zip(pool, eval_results):
            p["last_score"] = result["score"]
            parent_evals.append((p, result))
            print(f"    {p['name']}: {result['score']:.0%} ({result['correct']}/{result['total']})")

        # 2. Generate variants IN PARALLEL
        print(f"\n  Generating {n_variants} variants...")
        evolve_tasks = []
        for i in range(n_variants):
            # Pick parent (biased toward better scores)
            parent, result = random.choice(parent_evals)
            error_details = format_errors_for_evolver(result["errors"])
            evolve_tasks.append(
                evolve_variant(
                    client, parent["text"], result["score"],
                    result["correct"], result["total"], error_details,
                )
            )
        variant_texts = await asyncio.gather(*evolve_tasks)
        variants = []
        for i, text in enumerate(variant_texts):
            if text:
                variants.append({
                    "text": text,
                    "name": f"gen{gen}_v{i}",
                    "size": len(text.encode("utf-8")),
                })
                print(f"    gen{gen}_v{i}: {len(text.encode('utf-8'))} bytes")

        if not variants:
            print("  No valid variants, skipping")
            continue

        # 3. Evaluate variants on SAME problems as parents (fair comparison)
        print(f"\n  Evaluating {len(variants)} variants on same {len(gen_problems)} problems...")
        var_eval_tasks = [
            evaluate_cheatsheet(client, v["text"], gen_problems)
            for v in variants
        ]
        var_results = await asyncio.gather(*var_eval_tasks)
        for v, result in zip(variants, var_results):
            v["score"] = result["score"]
            print(f"    {v['name']}: {v['score']:.0%} ({result['correct']}/{result['total']}, {v['size']} bytes)")
            history.append({"gen": gen, "name": v["name"], "score": v["score"]})

        # 4. Update pool: merge + keep top POOL_SIZE
        all_candidates = pool + variants
        all_candidates.sort(key=lambda x: x["score"], reverse=True)
        pool = all_candidates[:POOL_SIZE]

        # Update best
        if pool[0]["score"] > best_ever["score"]:
            best_ever = pool[0].copy()
            (out / "best.txt").write_text(best_ever["text"], encoding="utf-8")
            print(f"\n  *** NEW BEST: {best_ever['score']:.0%} ({best_ever['name']}) ***")
        else:
            print(f"\n  No improvement. Best: {best_ever['score']:.0%}")

        elapsed = time.time() - t0
        print(f"  Gen time: {elapsed:.0f}s")

    # Save everything
    print(f"\n{'='*60}")
    print(f"DONE | Seed: {seed_result['score']:.0%} -> Best: {best_ever['score']:.0%}")
    print(f"{'='*60}")

    (out / "best.txt").write_text(best_ever["text"], encoding="utf-8")
    (out / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    for i, p in enumerate(pool):
        (out / f"pool_{i}_{p['name']}.txt").write_text(p["text"], encoding="utf-8")
    print(f"Saved to {out}/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="cheatsheets/v15_concise.txt")
    parser.add_argument("--variants", type=int, default=VARIANTS_PER_GEN)
    parser.add_argument("--generations", type=int, default=5)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    parser.add_argument("--output", default="optim/evolve_runs/run1")
    args = parser.parse_args()

    if not args.endpoint or not args.api_key:
        print("ERROR: Set AZURE_FOUNDRY_BASE_URL and AZURE_INFERENCE_CREDENTIAL", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_evolution(
        seed_path=args.seed,
        n_variants=args.variants,
        n_generations=args.generations,
        endpoint=args.endpoint,
        api_key=args.api_key,
        output_dir=args.output,
    ))


if __name__ == "__main__":
    main()

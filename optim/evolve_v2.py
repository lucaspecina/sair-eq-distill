"""
Evolutionary cheatsheet optimizer v2 — with crossover and reflective analysis.

Improvements over v1:
- Crossover mutations: combine ideas from 2 parents
- Reflective analysis: evolver first analyzes error patterns, then improves
- Structured error breakdown: TRUE/FALSE accuracy shown separately
- Statistical context: evolver knows the problem distribution

Usage:
    python optim/evolve_v2.py --seed cheatsheets/current.txt --generations 20
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
EVAL_MODELS = ["gpt-4.1-mini"]
EVOLVER_MODEL = "gpt-5.4"

# Eval config
EVAL_NORMAL = 160
EVAL_HARD = 40
EVAL_CONCURRENT = 50

# Evolution config
POOL_SIZE = 6
VARIANTS_PER_GEN = 5  # 3 mutations + 2 crossovers

NORMAL_PATH = "data/raw/normal.jsonl"
HARD_PATH = "data/raw/hard.jsonl"


async def evaluate_cheatsheet(client, cheatsheet_text, problems, models=None):
    """Evaluate cheatsheet across all eval models."""
    if models is None:
        models = EVAL_MODELS
    sem = asyncio.Semaphore(EVAL_CONCURRENT)

    # Build lookup for equation text by problem id
    eq_lookup = {p.get("id", ""): p for p in problems}

    all_tasks = []
    for model in models:
        for p in problems:
            all_tasks.append(evaluate_single(client, model, cheatsheet_text, p, sem))
    all_results = await asyncio.gather(*all_tasks)

    # Enrich results with equation text
    for r in all_results:
        pid = r.get("id", "")
        if pid in eq_lookup:
            r["equation1"] = eq_lookup[pid].get("equation1", "")
            r["equation2"] = eq_lookup[pid].get("equation2", "")

    per_model = {}
    for r in all_results:
        m = r.get("model", models[0])
        per_model.setdefault(m, []).append(r)

    model_scores = []
    all_errors = []
    for m in models:
        results = per_model.get(m, [])
        correct = sum(1 for r in results if r.get("correct"))
        total = len(results)
        model_scores.append(correct / total if total > 0 else 0)
        all_errors.extend(r for r in results if not r.get("correct"))

    avg_score = sum(model_scores) / len(model_scores) if model_scores else 0

    # Compute TRUE/FALSE breakdown
    true_correct = sum(1 for r in all_results if r.get("correct") and r.get("expected") == True)
    true_total = sum(1 for r in all_results if r.get("expected") == True)
    false_correct = sum(1 for r in all_results if r.get("correct") and r.get("expected") == False)
    false_total = sum(1 for r in all_results if r.get("expected") == False)

    return {
        "score": avg_score,
        "correct": sum(1 for r in all_results if r.get("correct")),
        "total": len(all_results),
        "errors": all_errors,
        "true_acc": true_correct / true_total if true_total > 0 else 0,
        "false_acc": false_correct / false_total if false_total > 0 else 0,
        "true_n": true_total,
        "false_n": false_total,
    }


def format_errors_structured(errors, max_errors=10):
    """Format errors with structured breakdown."""
    if not errors:
        return "No errors!"

    # Classify errors
    false_pos = [e for e in errors if e.get("expected") == False and e.get("predicted") == True]
    false_neg = [e for e in errors if e.get("expected") == True and e.get("predicted") == False]
    no_answer = [e for e in errors if e.get("predicted") is None]

    lines = [f"Error summary: {len(false_pos)} false positives (said TRUE, was FALSE), "
             f"{len(false_neg)} false negatives (said FALSE, was TRUE), "
             f"{len(no_answer)} no answer (model ran out of tokens or parse failure)"]

    # Sample diverse errors
    sampled = []
    for group, label in [(false_pos, "FALSE_POS"), (false_neg, "FALSE_NEG"), (no_answer, "NO_ANSWER")]:
        n = min(len(group), max(1, max_errors // 3))
        sampled.extend((e, label) for e in random.sample(group, n))

    for e, label in sampled[:max_errors]:
        eid = e.get("id", "?")
        expected = "TRUE" if e.get("expected") else "FALSE"
        raw = (e.get("raw_response") or "(empty)")[:250]
        lines.append(f"\n[{label}] Problem {eid}: correct={expected}")
        lines.append(f"  Eq1: {e.get('equation1', '?')}")
        lines.append(f"  Eq2: {e.get('equation2', '?')}")
        lines.append(f"  Model reasoning: {raw}")

    return "\n".join(lines)


MUTATION_PROMPT = """You are improving a cheatsheet (<=10KB) that helps LLMs predict whether one equational law implies another over magmas (binary operation *, no axioms).

STATISTICAL FACTS (use these to prioritize):
- Normal: 50% TRUE, 50% FALSE. Hard: 37% TRUE, 63% FALSE.
- If Eq1 is "v = T(...)" where v NOT in T -> ALWAYS TRUE (100% accuracy, covers 49% of TRUE normals).
- If Eq1 is "v = T(v,...)" where v IS in T -> 45% TRUE. Needs careful reasoning.
- If Eq1 has no lone variable -> 15% TRUE. Lean FALSE.
- Counter-models: left-zero (a*b=a, term=leftmost var), right-zero (a*b=b, term=rightmost var).

CURRENT CHEATSHEET (score: {score:.0%}, TRUE acc: {true_acc:.0%}, FALSE acc: {false_acc:.0%}):
---
{cheatsheet}
---

ERRORS:
{error_details}

Generate an improved cheatsheet. Rules must be PRECISE with conditions AND limitations.
Keep under 10KB. Output ONLY the cheatsheet text."""

CROSSOVER_PROMPT = """You are creating a new cheatsheet by combining the best ideas from two existing ones.

PARENT A (score: {score_a:.0%}, TRUE: {true_a:.0%}, FALSE: {false_a:.0%}, {size_a} bytes):
---
{cheatsheet_a}
---

PARENT B (score: {score_b:.0%}, TRUE: {true_b:.0%}, FALSE: {false_b:.0%}, {size_b} bytes):
---
{cheatsheet_b}
---

STATISTICAL FACTS:
- If Eq1 is "v = T(...)" where v NOT in T -> ALWAYS TRUE (100% accuracy).
- If Eq1 is "v = T(v,...)" where v IS in T -> 45% TRUE.
- If no lone variable -> 15% TRUE.
- Counter-models: left-zero (a*b=a), right-zero (a*b=b).

Combine the strongest rules from both parents into a single cheatsheet.
Take the best ideas from each — don't just concatenate. Synthesize.
Keep under 10KB. Output ONLY the cheatsheet text."""


async def mutate(client, parent_text, score, true_acc, false_acc, error_details):
    """Standard mutation: improve one parent based on errors."""
    prompt = MUTATION_PROMPT.format(
        cheatsheet=parent_text, score=score,
        true_acc=true_acc, false_acc=false_acc,
        error_details=error_details,
    )
    try:
        resp = await client.chat.completions.create(
            model=EVOLVER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=8192,
        )
        text = (resp.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        text = text.strip()
        size = len(text.encode("utf-8"))
        if size > 10240:
            text = text[:10240].rsplit("\n", 1)[0]
        return text if size >= 50 else ""
    except Exception as e:
        print(f"    Mutation failed: {e}")
        return ""


async def crossover(client, parent_a, result_a, parent_b, result_b):
    """Crossover: combine ideas from two parents."""
    prompt = CROSSOVER_PROMPT.format(
        cheatsheet_a=parent_a["text"], score_a=result_a["score"],
        true_a=result_a["true_acc"], false_a=result_a["false_acc"],
        size_a=parent_a["size"],
        cheatsheet_b=parent_b["text"], score_b=result_b["score"],
        true_b=result_b["true_acc"], false_b=result_b["false_acc"],
        size_b=parent_b["size"],
    )
    try:
        resp = await client.chat.completions.create(
            model=EVOLVER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=8192,
        )
        text = (resp.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        text = text.strip()
        size = len(text.encode("utf-8"))
        if size > 10240:
            text = text[:10240].rsplit("\n", 1)[0]
        return text if size >= 50 else ""
    except Exception as e:
        print(f"    Crossover failed: {e}")
        return ""


def sample_problems(normal, hard, n_normal, n_hard):
    sampled = random.sample(normal, min(n_normal, len(normal)))
    sampled += random.sample(hard, min(n_hard, len(hard)))
    random.shuffle(sampled)
    return sampled


async def run_evolution(seed_path, n_variants, n_generations, endpoint, api_key, output_dir):
    client = AsyncOpenAI(base_url=endpoint, api_key=api_key)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    all_normal = load_problems(NORMAL_PATH)
    all_hard = load_problems(HARD_PATH)
    print(f"Loaded {len(all_normal)} normal + {len(all_hard)} hard problems")

    seed_text = Path(seed_path).read_text(encoding="utf-8")
    print(f"\n=== EVOLUTIONARY OPTIMIZER v2 (crossover + structured errors) ===")
    print(f"Seed: {seed_path} ({len(seed_text.encode('utf-8'))} bytes)")
    print(f"Evaluators: {', '.join(EVAL_MODELS)} | Evolver: {EVOLVER_MODEL}")
    print(f"Per eval: {EVAL_NORMAL} normal + {EVAL_HARD} hard, concurrency {EVAL_CONCURRENT}")
    print(f"Variants/gen: {n_variants} (mutations + crossovers) | Generations: {n_generations}")

    # Evaluate seed
    print(f"\n--- Evaluating seed ---")
    seed_problems = sample_problems(all_normal, all_hard, EVAL_NORMAL, EVAL_HARD)
    seed_result = await evaluate_cheatsheet(client, seed_text, seed_problems)
    print(f"Seed: {seed_result['score']:.0%} (T:{seed_result['true_acc']:.0%} F:{seed_result['false_acc']:.0%})")

    pool = [{
        "text": seed_text, "score": seed_result["score"], "name": "seed",
        "size": len(seed_text.encode("utf-8")),
    }]
    best_ever = pool[0].copy()
    history = [{"gen": 0, "name": "seed", "score": seed_result["score"]}]

    for gen in range(1, n_generations + 1):
        t0 = time.time()
        print(f"\n{'='*60}")
        print(f"GEN {gen}/{n_generations} | Best: {best_ever['score']:.0%} | Pool: {len(pool)}")
        print(f"{'='*60}")

        # 1. Sample problems for this generation
        gen_problems = sample_problems(all_normal, all_hard, EVAL_NORMAL, EVAL_HARD)
        print(f"  Evaluating {len(pool)} parents on {len(gen_problems)} problems...")
        parent_evals = []
        eval_tasks = [evaluate_cheatsheet(client, p["text"], gen_problems) for p in pool]
        eval_results = await asyncio.gather(*eval_tasks)
        for p, result in zip(pool, eval_results):
            p["last_score"] = result["score"]
            parent_evals.append((p, result))
            print(f"    {p['name']}: {result['score']:.0%} (T:{result['true_acc']:.0%} F:{result['false_acc']:.0%})")

        # 2. Generate variants: mutations + crossovers
        n_mutations = max(1, n_variants - 2)
        n_crossovers = n_variants - n_mutations
        print(f"\n  Generating {n_mutations} mutations + {n_crossovers} crossovers...")

        evolve_tasks = []
        variant_names = []

        # Mutations
        for i in range(n_mutations):
            parent, result = random.choice(parent_evals)
            error_details = format_errors_structured(result["errors"])
            evolve_tasks.append(
                mutate(client, parent["text"], result["score"],
                       result["true_acc"], result["false_acc"], error_details)
            )
            variant_names.append(f"gen{gen}_m{i}")

        # Crossovers
        for i in range(n_crossovers):
            if len(parent_evals) >= 2:
                pa, ra = random.choice(parent_evals)
                pb, rb = random.choice(parent_evals)
                while pb["name"] == pa["name"] and len(parent_evals) > 1:
                    pb, rb = random.choice(parent_evals)
                evolve_tasks.append(crossover(client, pa, ra, pb, rb))
            else:
                parent, result = parent_evals[0]
                error_details = format_errors_structured(result["errors"])
                evolve_tasks.append(
                    mutate(client, parent["text"], result["score"],
                           result["true_acc"], result["false_acc"], error_details)
                )
            variant_names.append(f"gen{gen}_x{i}")

        variant_texts = await asyncio.gather(*evolve_tasks)
        variants = []
        for name, text in zip(variant_names, variant_texts):
            if text:
                variants.append({
                    "text": text, "name": name,
                    "size": len(text.encode("utf-8")),
                })
                print(f"    {name}: {len(text.encode('utf-8'))} bytes")

        if not variants:
            print("  No valid variants, skipping")
            continue

        # 3. Evaluate variants on SAME problems
        print(f"\n  Evaluating {len(variants)} variants on same {len(gen_problems)} problems...")
        var_eval_tasks = [evaluate_cheatsheet(client, v["text"], gen_problems) for v in variants]
        var_results = await asyncio.gather(*var_eval_tasks)
        for v, result in zip(variants, var_results):
            v["score"] = result["score"]
            print(f"    {v['name']}: {v['score']:.0%} (T:{result['true_acc']:.0%} F:{result['false_acc']:.0%}, {v['size']}B)")
            history.append({"gen": gen, "name": v["name"], "score": v["score"]})

        # 4. Update pool
        all_candidates = pool + variants
        all_candidates.sort(key=lambda x: x["score"], reverse=True)
        pool = all_candidates[:POOL_SIZE]

        if pool[0]["score"] > best_ever["score"]:
            best_ever = pool[0].copy()
            (out / "best.txt").write_text(best_ever["text"], encoding="utf-8")
            print(f"\n  *** NEW BEST: {best_ever['score']:.0%} ({best_ever['name']}) ***")
        else:
            print(f"\n  No improvement. Best: {best_ever['score']:.0%}")

        elapsed = time.time() - t0
        print(f"  Gen time: {elapsed:.0f}s")

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
    parser.add_argument("--seed", default="cheatsheets/current.txt")
    parser.add_argument("--variants", type=int, default=VARIANTS_PER_GEN)
    parser.add_argument("--generations", type=int, default=20)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    parser.add_argument("--output", default="optim/evolve_runs/run_v2")
    args = parser.parse_args()

    if not args.endpoint or not args.api_key:
        print("ERROR: Set AZURE_FOUNDRY_BASE_URL and AZURE_INFERENCE_CREDENTIAL", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_evolution(
        seed_path=args.seed, n_variants=args.variants,
        n_generations=args.generations, endpoint=args.endpoint,
        api_key=args.api_key, output_dir=args.output,
    ))


if __name__ == "__main__":
    main()

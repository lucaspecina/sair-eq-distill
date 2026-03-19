"""
Robust evaluation wrapper for competition-realistic testing.

Addresses the flaws in our evaluation:
1. Mixes normal + hard problems (competition does both)
2. Uses random seeds (not fixed 42)
3. Reports per-difficulty breakdown
4. Weighted scoring matching competition ratio (5:1 normal:hard)
5. Runs multiple seeds for statistical confidence

Usage:
    python eval/eval_robust.py --cheatsheet cheatsheets/current.txt
    python eval/eval_robust.py --cheatsheet cheatsheets/current.txt --seeds 3
    python eval/eval_robust.py --cheatsheet cheatsheets/current.txt --full
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

# Reuse core functions from evaluate.py
sys.path.insert(0, str(Path(__file__).parent))
from evaluate import (
    build_prompt,
    compute_metrics,
    evaluate_single,
    load_problems,
    parse_verdict,
)

load_dotenv()

# --- Config ---
DEFAULT_ENDPOINT = os.getenv("AZURE_FOUNDRY_BASE_URL", os.getenv("AZURE_FOUNDRY_ENDPOINT", ""))
DEFAULT_API_KEY = os.getenv("AZURE_INFERENCE_CREDENTIAL", "")
MAX_CONCURRENT = int(os.getenv("EVAL_MAX_CONCURRENT", "10"))

# Competition-realistic defaults
NORMAL_PATH = "data/raw/normal.jsonl"
HARD_PATH = "data/raw/hard.jsonl"
DEFAULT_NORMAL_SAMPLE = 25  # 5:1 ratio with hard
DEFAULT_HARD_SAMPLE = 5
DEFAULT_MODELS = os.getenv("EVAL_MODELS", "gpt-5-nano,gpt-5-mini").split(",")


def sample_mixed(
    normal: list[dict],
    hard: list[dict],
    n_normal: int,
    n_hard: int,
    seed: int,
) -> tuple[list[dict], list[dict]]:
    """Sample from normal and hard with given seed."""
    rng = random.Random(seed)
    sampled_normal = rng.sample(normal, min(n_normal, len(normal)))
    sampled_hard = rng.sample(hard, min(n_hard, len(hard)))
    return sampled_normal, sampled_hard


async def evaluate_problems(
    client: AsyncOpenAI,
    model: str,
    cheatsheet: str,
    problems: list[dict],
    semaphore: asyncio.Semaphore,
) -> list[dict]:
    """Evaluate a batch of problems with one model."""
    tasks = [
        evaluate_single(client, model, cheatsheet, p, semaphore)
        for p in problems
    ]
    return await asyncio.gather(*tasks)


async def run_single_seed(
    client: AsyncOpenAI,
    models: list[str],
    cheatsheet: str,
    normal_problems: list[dict],
    hard_problems: list[dict],
    n_normal: int,
    n_hard: int,
    seed: int,
    max_concurrent: int,
) -> dict:
    """Run evaluation for a single seed across all models."""
    sampled_normal, sampled_hard = sample_mixed(
        normal_problems, hard_problems, n_normal, n_hard, seed
    )
    all_problems = sampled_normal + sampled_hard

    semaphore = asyncio.Semaphore(max_concurrent)
    t0 = time.time()

    # Run all models
    model_results = {}
    for model in models:
        results = await evaluate_problems(
            client, model, cheatsheet, all_problems, semaphore
        )
        model_results[model] = results

    elapsed = time.time() - t0

    # Compute metrics per model, per difficulty
    seed_summary = {
        "seed": seed,
        "elapsed": round(elapsed, 1),
        "n_normal": len(sampled_normal),
        "n_hard": len(sampled_hard),
        "models": {},
    }

    for model in models:
        results = model_results[model]
        normal_results = [r for r in results if any(
            r["id"] == p.get("id") for p in sampled_normal
        )]
        hard_results = [r for r in results if any(
            r["id"] == p.get("id") for p in sampled_hard
        )]

        # Easier: tag by difficulty from source problems
        normal_ids = {p.get("id") for p in sampled_normal}
        hard_ids = {p.get("id") for p in sampled_hard}

        normal_res = [r for r in results if r["id"] in normal_ids]
        hard_res = [r for r in results if r["id"] in hard_ids]
        all_res = results

        normal_metrics = compute_metrics(normal_res, model) if normal_res else None
        hard_metrics = compute_metrics(hard_res, model) if hard_res else None
        all_metrics = compute_metrics(all_res, model)

        # Weighted score: 5:1 normal:hard (matching competition ratio)
        if normal_metrics and hard_metrics:
            weighted = (
                5 * normal_metrics["accuracy"] + 1 * hard_metrics["accuracy"]
            ) / 6
        elif normal_metrics:
            weighted = normal_metrics["accuracy"]
        else:
            weighted = all_metrics["accuracy"]

        seed_summary["models"][model] = {
            "overall": all_metrics,
            "normal": normal_metrics,
            "hard": hard_metrics,
            "weighted_score": round(weighted, 4),
            "per_problem": results,  # raw per-problem results
        }

    return seed_summary


async def run_robust_evaluation(
    cheatsheet_path: str,
    models: list[str],
    endpoint: str,
    api_key: str,
    n_normal: int,
    n_hard: int,
    n_seeds: int,
    max_concurrent: int,
    fixed_seed: int | None = None,
) -> dict:
    """Run robust evaluation with multiple seeds."""
    # Load cheat sheet
    cheatsheet_text = Path(cheatsheet_path).read_text(encoding="utf-8")
    cs_size = len(cheatsheet_text.encode("utf-8"))
    if cs_size > 10240:
        print(f"ERROR: Cheat sheet is {cs_size} bytes (limit: 10240)", file=sys.stderr)
        sys.exit(1)

    # Load all problems
    normal_problems = load_problems(NORMAL_PATH)
    hard_problems = load_problems(HARD_PATH)

    print(f"=== ROBUST EVALUATION ===")
    print(f"Cheat sheet: {cs_size} bytes ({cs_size/1024:.1f}KB)")
    print(f"Models: {', '.join(models)}")
    print(f"Per seed: {n_normal} normal + {n_hard} hard = {n_normal + n_hard} problems")
    print(f"Seeds: {n_seeds} (total: {(n_normal + n_hard) * n_seeds * len(models)} API calls)")
    print(f"Available: {len(normal_problems)} normal, {len(hard_problems)} hard")
    print()

    client = AsyncOpenAI(base_url=endpoint, api_key=api_key)

    # Run each seed
    seed_results = []
    for i in range(n_seeds):
        seed = fixed_seed if fixed_seed is not None else random.randint(1, 999999)
        print(f"--- Seed {i+1}/{n_seeds} (seed={seed}) ---")
        result = await run_single_seed(
            client, models, cheatsheet_text,
            normal_problems, hard_problems,
            n_normal, n_hard, seed, max_concurrent,
        )
        seed_results.append(result)

        # Print per-seed summary
        for model, data in result["models"].items():
            n_m = data["normal"]
            h_m = data["hard"]
            n_acc = f"{n_m['accuracy']:.1%}" if n_m else "N/A"
            h_acc = f"{h_m['accuracy']:.1%}" if h_m else "N/A"
            print(
                f"  {model:.<25s} normal={n_acc}  hard={h_acc}  "
                f"weighted={data['weighted_score']:.1%}  "
                f"({result['elapsed']:.0f}s)"
            )

    # Collect all per-problem results for error analysis
    all_raw_results = []
    for sr in seed_results:
        for model, data in sr["models"].items():
            for r in data.get("per_problem", []):
                r["seed"] = sr["seed"]
                all_raw_results.append(r)

    # Aggregate across seeds
    print(f"\n{'='*60}")
    print(f"AGGREGATE RESULTS ({n_seeds} seeds)")
    print(f"{'='*60}")

    final_scores = {}
    for model in models:
        weighted_scores = [
            sr["models"][model]["weighted_score"]
            for sr in seed_results
            if model in sr["models"]
        ]
        normal_accs = [
            sr["models"][model]["normal"]["accuracy"]
            for sr in seed_results
            if model in sr["models"] and sr["models"][model]["normal"]
        ]
        hard_accs = [
            sr["models"][model]["hard"]["accuracy"]
            for sr in seed_results
            if model in sr["models"] and sr["models"][model]["hard"]
        ]

        avg_weighted = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0
        avg_normal = sum(normal_accs) / len(normal_accs) if normal_accs else 0
        avg_hard = sum(hard_accs) / len(hard_accs) if hard_accs else 0

        # Standard deviation for confidence
        if len(weighted_scores) > 1:
            mean = avg_weighted
            std = (sum((x - mean)**2 for x in weighted_scores) / (len(weighted_scores) - 1)) ** 0.5
        else:
            std = 0

        final_scores[model] = {
            "weighted": round(avg_weighted, 4),
            "normal": round(avg_normal, 4),
            "hard": round(avg_hard, 4),
            "std": round(std, 4),
        }

        print(
            f"  {model:.<25s} weighted={avg_weighted:.1%} (±{std:.1%})  "
            f"normal={avg_normal:.1%}  hard={avg_hard:.1%}"
        )

    # Cross-model average (the competition metric)
    all_weighted = [v["weighted"] for v in final_scores.values()]
    competition_score = sum(all_weighted) / len(all_weighted) if all_weighted else 0

    print(f"\n{'='*60}")
    print(f"COMPETITION SCORE (cross-model avg): {competition_score:.1%}")
    print(f"{'='*60}")

    # Save details (including per-problem results for error analysis)
    details = {
        "competition_score": round(competition_score, 4),
        "cheatsheet_bytes": cs_size,
        "cheatsheet_path": cheatsheet_path,
        "n_seeds": n_seeds,
        "n_normal_per_seed": n_normal,
        "n_hard_per_seed": n_hard,
        "models": models,
        "final_scores": final_scores,
        "seed_results": seed_results,
        "all_per_problem_results": all_raw_results,
    }
    results_path = Path("eval/last_robust_run.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2, default=str)
    print(f"Details saved to: {results_path}")

    return details


def main():
    parser = argparse.ArgumentParser(description="Robust competition-realistic evaluation")
    parser.add_argument("--cheatsheet", default="cheatsheets/current.txt")
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--normal-sample", type=int, default=DEFAULT_NORMAL_SAMPLE)
    parser.add_argument("--hard-sample", type=int, default=DEFAULT_HARD_SAMPLE)
    parser.add_argument("--seeds", type=int, default=1, help="Number of random seeds")
    parser.add_argument("--concurrent", type=int, default=MAX_CONCURRENT)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    parser.add_argument("--seed", type=int, default=None, help="Fixed random seed for reproducible comparison")
    parser.add_argument("--full", action="store_true", help="Use all problems (no sampling)")

    args = parser.parse_args()

    if not args.endpoint:
        print("ERROR: Set AZURE_FOUNDRY_BASE_URL", file=sys.stderr)
        sys.exit(1)
    if not args.api_key:
        print("ERROR: Set AZURE_INFERENCE_CREDENTIAL", file=sys.stderr)
        sys.exit(1)

    models = [m.strip() for m in args.models.split(",") if m.strip()]

    if args.full:
        # Use all 1000 normal + 200 hard
        args.normal_sample = 9999
        args.hard_sample = 9999
        args.seeds = 1

    asyncio.run(
        run_robust_evaluation(
            cheatsheet_path=args.cheatsheet,
            models=models,
            endpoint=args.endpoint,
            api_key=args.api_key,
            n_normal=args.normal_sample,
            n_hard=args.hard_sample,
            n_seeds=args.seeds,
            max_concurrent=args.concurrent,
            fixed_seed=args.seed,
        )
    )


if __name__ == "__main__":
    main()

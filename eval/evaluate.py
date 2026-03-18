"""
Evaluator for eq-distill cheat sheets.

Matches the SAIR competition evaluation prompt as closely as possible.
Runs against MULTIPLE models and reports per-model + average accuracy.
The average accuracy is the metric optimized by autoresearch.

THIS FILE IS IMMUTABLE DURING AUTORESEARCH. Only the human edits it.
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# --- Config ---
DEFAULT_ENDPOINT = os.getenv("AZURE_FOUNDRY_BASE_URL", os.getenv("AZURE_FOUNDRY_ENDPOINT", ""))
DEFAULT_API_KEY = os.getenv("AZURE_INFERENCE_CREDENTIAL", "")
DEFAULT_PROBLEMS = "data/raw/normal.jsonl"
DEFAULT_CHEATSHEET = "cheatsheets/current.txt"
MAX_CONCURRENT = int(os.getenv("EVAL_MAX_CONCURRENT", "10"))
DEFAULT_SAMPLE_SIZE = int(os.getenv("EVAL_SAMPLE_SIZE", "200"))

# Models to evaluate against — should span the range SAIR likely uses
EVAL_MODELS = os.getenv(
    "EVAL_MODELS",
    "gpt-5-nano,gpt-5-mini,Phi-4,claude-haiku-4-5",
).split(",")

# --- Prompt template matching SAIR competition ---
EVAL_PROMPT_TEMPLATE = """You are a mathematician specializing in equational theories of magmas. \
Your task is to determine whether Equation 1 ({equation1}) implies Equation 2 ({equation2}) over all magmas.
{cheatsheet_block}
Output format (use exact headers without any additional text or formatting):
VERDICT: must be exactly TRUE or FALSE (in the same line).
REASONING: must be non-empty.
PROOF: required if VERDICT is TRUE, empty otherwise.
COUNTEREXAMPLE: required if VERDICT is FALSE, empty otherwise."""


def build_prompt(equation1: str, equation2: str, cheatsheet: str) -> str:
    """Build the evaluation prompt matching SAIR's Jinja2 template."""
    cheatsheet_block = cheatsheet if cheatsheet.strip() else ""
    return EVAL_PROMPT_TEMPLATE.format(
        equation1=equation1,
        equation2=equation2,
        cheatsheet_block=cheatsheet_block,
    )


def parse_verdict(response_text: str) -> bool | None:
    """Parse VERDICT: TRUE/FALSE from model response."""
    match = re.search(r"VERDICT:\s*(TRUE|FALSE)", response_text, re.IGNORECASE)
    if match:
        return match.group(1).upper() == "TRUE"
    for line in reversed(response_text.strip().split("\n")):
        line = line.strip().upper()
        if line == "TRUE":
            return True
        if line == "FALSE":
            return False
    return None


def load_problems(path: str) -> list[dict]:
    """Load problems from JSONL or JSON file."""
    problems = []
    p = Path(path)
    if p.suffix == ".jsonl":
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    problems.append(json.loads(line))
    else:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                problems = data
            else:
                raise ValueError(f"Unexpected JSON format in {path}")
    return problems


async def evaluate_single(
    client: AsyncOpenAI,
    model: str,
    cheatsheet: str,
    problem: dict,
    semaphore: asyncio.Semaphore,
) -> dict:
    """Evaluate a single problem with a single model."""
    prompt = build_prompt(
        equation1=problem["equation1"],
        equation2=problem["equation2"],
        cheatsheet=cheatsheet,
    )
    expected = problem["answer"]

    async with semaphore:
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=8192,
            )
            answer_text = response.choices[0].message.content or ""
            predicted = parse_verdict(answer_text)

            return {
                "id": problem.get("id", ""),
                "model": model,
                "expected": expected,
                "predicted": predicted,
                "correct": predicted == expected,
                "raw_response": answer_text[:300],
                "error": None,
            }
        except Exception as e:
            return {
                "id": problem.get("id", ""),
                "model": model,
                "expected": expected,
                "predicted": None,
                "correct": False,
                "raw_response": "",
                "error": str(e),
            }


def compute_metrics(results: list[dict], model: str) -> dict:
    """Compute accuracy metrics for a set of results."""
    n_total = len(results)
    n_correct = sum(1 for r in results if r["correct"])
    n_errors = sum(1 for r in results if r["error"])
    n_ambiguous = sum(1 for r in results if r["predicted"] is None and not r["error"])
    accuracy = n_correct / n_total if n_total > 0 else 0.0

    true_problems = [r for r in results if r["expected"] is True]
    false_problems = [r for r in results if r["expected"] is False]
    true_acc = (
        sum(1 for r in true_problems if r["correct"]) / len(true_problems)
        if true_problems
        else 0.0
    )
    false_acc = (
        sum(1 for r in false_problems if r["correct"]) / len(false_problems)
        if false_problems
        else 0.0
    )

    return {
        "model": model,
        "accuracy": accuracy,
        "n_correct": n_correct,
        "n_total": n_total,
        "n_errors": n_errors,
        "n_ambiguous": n_ambiguous,
        "true_accuracy": true_acc,
        "false_accuracy": false_acc,
        "n_true": len(true_problems),
        "n_false": len(false_problems),
    }


async def run_evaluation(
    cheatsheet_path: str,
    problems_path: str,
    models: list[str],
    endpoint: str,
    api_key: str,
    sample_size: int,
    max_concurrent: int,
) -> dict:
    """Run evaluation across multiple models. Returns combined summary."""
    # Load cheat sheet
    cheatsheet_text = Path(cheatsheet_path).read_text(encoding="utf-8")
    cs_size = len(cheatsheet_text.encode("utf-8"))
    if cs_size > 10240:
        print(f"ERROR: Cheat sheet is {cs_size} bytes (limit: 10240)", file=sys.stderr)
        sys.exit(1)

    # Load problems
    problems = load_problems(problems_path)

    # Sample if needed
    if sample_size and 0 < sample_size < len(problems):
        import random

        random.seed(42)
        problems = random.sample(problems, sample_size)

    print(f"Evaluating {len(problems)} problems x {len(models)} models")
    print(f"Models: {', '.join(models)}")
    print(f"Cheat sheet: {cs_size} bytes ({cs_size/1024:.1f}KB)")
    print(f"Problems source: {problems_path}")

    client = AsyncOpenAI(base_url=endpoint, api_key=api_key)
    semaphore = asyncio.Semaphore(max_concurrent)

    # Run all models in parallel
    t0 = time.time()
    all_tasks = []
    for model in models:
        for p in problems:
            all_tasks.append(evaluate_single(client, model, cheatsheet_text, p, semaphore))
    all_results = await asyncio.gather(*all_tasks)
    elapsed = time.time() - t0

    # Group results by model
    results_by_model = {}
    for r in all_results:
        m = r["model"]
        if m not in results_by_model:
            results_by_model[m] = []
        results_by_model[m].append(r)

    # Compute per-model metrics
    model_metrics = []
    for model in models:
        if model in results_by_model:
            metrics = compute_metrics(results_by_model[model], model)
            model_metrics.append(metrics)

    # Compute average accuracy across models
    avg_accuracy = (
        sum(m["accuracy"] for m in model_metrics) / len(model_metrics)
        if model_metrics
        else 0.0
    )
    total_correct = sum(m["n_correct"] for m in model_metrics)
    total_problems = sum(m["n_total"] for m in model_metrics)
    total_errors = sum(m["n_errors"] for m in model_metrics)

    # Print per-model results
    print(f"\n{'='*60}")
    for m in model_metrics:
        status = "OK" if m["n_errors"] == 0 else f"{m['n_errors']} errors"
        print(
            f"  {m['model']:.<30s} {m['accuracy']:.4f} "
            f"({m['n_correct']}/{m['n_total']}) "
            f"T:{m['true_accuracy']:.2f} F:{m['false_accuracy']:.2f} "
            f"[{status}]"
        )

    # Print the RESULT line — this is what autoresearch parses
    print(f"{'='*60}")
    print(f"RESULT: accuracy={avg_accuracy:.4f} correct={total_correct} total={total_problems}")
    print(f"{'='*60}")
    print(f"  Average across {len(model_metrics)} models: {avg_accuracy:.4f}")
    print(f"  Total errors: {total_errors}  Time: {elapsed:.1f}s")
    print(f"  Cheat sheet: {cs_size} bytes ({cs_size/1024:.1f}KB)")

    # Save detailed results
    details = {
        "summary": {
            "avg_accuracy": avg_accuracy,
            "models": [m["model"] for m in model_metrics],
            "per_model": model_metrics,
            "elapsed_seconds": round(elapsed, 1),
            "cheatsheet_bytes": cs_size,
            "n_problems": len(problems),
            "sample_size": sample_size,
        },
        "results": all_results,
    }
    results_path = Path("eval/last_run_details.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(details, f, indent=2, default=str)
    print(f"  Details saved to: {results_path}")

    return {"accuracy": avg_accuracy, "n_correct": total_correct, "n_total": total_problems, "n_errors": total_errors}


def main():
    parser = argparse.ArgumentParser(description="Evaluate a cheat sheet across multiple models")
    parser.add_argument("--cheatsheet", default=DEFAULT_CHEATSHEET, help="Path to cheat sheet")
    parser.add_argument("--problems", default=DEFAULT_PROBLEMS, help="Path to problems JSONL/JSON")
    parser.add_argument(
        "--models",
        default=",".join(EVAL_MODELS),
        help="Comma-separated model names (default: from EVAL_MODELS env var)",
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT, help="Foundry endpoint")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="API key")
    parser.add_argument(
        "--sample", type=int, default=DEFAULT_SAMPLE_SIZE, help="Sample size per model (0=all)"
    )
    parser.add_argument(
        "--concurrent", type=int, default=MAX_CONCURRENT, help="Max concurrent requests"
    )
    args = parser.parse_args()

    if not args.endpoint:
        print("ERROR: Set AZURE_FOUNDRY_BASE_URL env var or pass --endpoint", file=sys.stderr)
        sys.exit(1)
    if not args.api_key:
        print("ERROR: Set AZURE_INFERENCE_CREDENTIAL env var or pass --api-key", file=sys.stderr)
        sys.exit(1)

    models = [m.strip() for m in args.models.split(",") if m.strip()]

    summary = asyncio.run(
        run_evaluation(
            cheatsheet_path=args.cheatsheet,
            problems_path=args.problems,
            models=models,
            endpoint=args.endpoint,
            api_key=args.api_key,
            sample_size=args.sample,
            max_concurrent=args.concurrent,
        )
    )

    sys.exit(0 if summary["n_errors"] < summary["n_total"] * 0.5 else 1)


if __name__ == "__main__":
    main()

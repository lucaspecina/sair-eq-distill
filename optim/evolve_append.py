"""
Evolutionary optimizer v3 — APPEND mode.

Instead of rewriting the entire cheatsheet, the evolver ADDS a new section
to the existing cheatsheet. This preserves what works and only adds content.

The approach:
1. Evaluate current cheatsheet on nano
2. Show errors to evolver
3. Evolver generates ONLY a new section (≤3KB) to append
4. Evaluate current + appended section
5. If better, keep the appended version

This avoids the problem where the evolver destroys the careful balance
of the existing cheatsheet by rewriting everything.
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

EVAL_MODELS = os.getenv("EVAL_MODELS", "gpt-4.1-mini").split(",")
EVOLVER_MODEL = "gpt-5.4"

EVAL_NORMAL = int(os.getenv("EVAL_NORMAL", "80"))
EVAL_HARD = int(os.getenv("EVAL_HARD", "20"))
EVAL_CONCURRENT = int(os.getenv("EVAL_CONCURRENT", "50"))

NORMAL_PATH = "data/raw/normal.jsonl"
HARD_PATH = "data/raw/hard.jsonl"


async def evaluate_cheatsheet(client, cheatsheet_text, problems, models=None):
    if models is None:
        models = EVAL_MODELS
    sem = asyncio.Semaphore(EVAL_CONCURRENT)
    eq_lookup = {p.get("id", ""): p for p in problems}

    all_tasks = []
    for model in models:
        for p in problems:
            all_tasks.append(evaluate_single(client, model, cheatsheet_text, p, sem))
    all_results = await asyncio.gather(*all_tasks)

    for r in all_results:
        pid = r.get("id", "")
        if pid in eq_lookup:
            r["equation1"] = eq_lookup[pid].get("equation1", "")
            r["equation2"] = eq_lookup[pid].get("equation2", "")

    correct = sum(1 for r in all_results if r.get("correct"))
    total = len(all_results)
    errors = [r for r in all_results if not r.get("correct")]

    true_correct = sum(1 for r in all_results if r.get("correct") and r.get("expected") == True)
    true_total = sum(1 for r in all_results if r.get("expected") == True)
    false_correct = sum(1 for r in all_results if r.get("correct") and r.get("expected") == False)
    false_total = sum(1 for r in all_results if r.get("expected") == False)

    return {
        "score": correct / total if total > 0 else 0,
        "correct": correct, "total": total, "errors": errors,
        "true_acc": true_correct / true_total if true_total > 0 else 0,
        "false_acc": false_correct / false_total if false_total > 0 else 0,
    }


def format_errors(errors, max_errors=8):
    if not errors:
        return "No errors!"
    false_pos = [e for e in errors if e.get("expected") == False and e.get("predicted") == True]
    false_neg = [e for e in errors if e.get("expected") == True and e.get("predicted") == False]
    no_answer = [e for e in errors if e.get("predicted") is None]

    lines = [f"Errors: {len(false_pos)} false positives, {len(false_neg)} false negatives, {len(no_answer)} no answer"]

    sampled = []
    for group, label in [(false_pos, "FP"), (false_neg, "FN"), (no_answer, "NA")]:
        n = min(len(group), max(1, max_errors // 3))
        if group:
            sampled.extend((e, label) for e in random.sample(group, n))

    for e, label in sampled[:max_errors]:
        expected = "TRUE" if e.get("expected") else "FALSE"
        lines.append(f"[{label}] correct={expected}  Eq1: {e.get('equation1','?')}  Eq2: {e.get('equation2','?')}")
        raw = (e.get("raw_response") or "(empty)")[:150]
        lines.append(f"  Reasoning: {raw}")

    return "\n".join(lines)


APPEND_PROMPT = """You are adding a NEW SECTION to an existing cheatsheet that helps LLMs predict magma equation implications.

The existing cheatsheet already works well (score: {score:.0%}, TRUE: {true_acc:.0%}, FALSE: {false_acc:.0%}).
DO NOT rewrite or modify the existing content. You are ONLY generating NEW content to APPEND.

The main weakness is FALSE accuracy ({false_acc:.0%}). The model says TRUE too often when it should be FALSE.

KEY FACTS about counterexample magmas (use these!):
- Left-zero (a*b=a): term = leftmost variable
- Right-zero (a*b=b): term = rightmost variable
- Constant-zero on {{0,1}} (a*b=0): any product = 0, but lone vars keep value
- XOR on {{0,1}} (a*b = a+b mod 2)
- These 4 magmas catch ~69% of FALSE problems with zero errors

HERE ARE THE ERRORS the model made:
{error_details}

Generate ONLY a new section (max 3KB) to append. Focus on:
1. Additional counterexample checking procedures
2. Patterns that distinguish TRUE from FALSE in self-referential equations
3. Common false-positive traps to avoid

Output ONLY the new section text (will be appended after the existing cheatsheet)."""


async def generate_appendix(client, base_text, score, true_acc, false_acc, error_details):
    prompt = APPEND_PROMPT.format(
        score=score, true_acc=true_acc, false_acc=false_acc,
        error_details=error_details,
    )
    try:
        resp = await client.chat.completions.create(
            model=EVOLVER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4096,
        )
        text = (resp.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        text = text.strip()

        # Limit to 3KB
        if len(text.encode("utf-8")) > 3072:
            text = text[:3072].rsplit("\n", 1)[0]

        # Check total doesn't exceed 10KB
        total = base_text + "\n\n" + text
        if len(total.encode("utf-8")) > 10240:
            # Trim to fit
            budget = 10240 - len(base_text.encode("utf-8")) - 2
            text = text.encode("utf-8")[:budget].decode("utf-8", errors="ignore").rsplit("\n", 1)[0]

        return text if len(text) >= 50 else ""
    except Exception as e:
        print(f"    Append generation failed: {e}")
        return ""


def sample_problems(normal, hard, n_normal, n_hard):
    sampled = random.sample(normal, min(n_normal, len(normal)))
    sampled += random.sample(hard, min(n_hard, len(hard)))
    random.shuffle(sampled)
    return sampled


async def run_append_evolution(seed_path, n_iterations, endpoint, api_key, output_dir):
    client = AsyncOpenAI(base_url=endpoint, api_key=api_key)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    all_normal = load_problems(NORMAL_PATH)
    all_hard = load_problems(HARD_PATH)
    print(f"Loaded {len(all_normal)} normal + {len(all_hard)} hard problems")

    base_text = Path(seed_path).read_text(encoding="utf-8")
    current_text = base_text
    print(f"\n=== APPEND-MODE OPTIMIZER ===")
    print(f"Base: {seed_path} ({len(base_text.encode('utf-8'))} bytes)")
    print(f"Evaluators: {', '.join(EVAL_MODELS)} | Evolver: {EVOLVER_MODEL}")
    print(f"Iterations: {n_iterations}")

    best_score = 0
    best_text = current_text

    for it in range(1, n_iterations + 1):
        t0 = time.time()
        print(f"\n{'='*60}")
        print(f"ITERATION {it}/{n_iterations} | Current size: {len(current_text.encode('utf-8'))} bytes")
        print(f"{'='*60}")

        # Evaluate current
        problems = sample_problems(all_normal, all_hard, EVAL_NORMAL, EVAL_HARD)
        result = await evaluate_cheatsheet(client, current_text, problems)
        print(f"  Current: {result['score']:.0%} (T:{result['true_acc']:.0%} F:{result['false_acc']:.0%})")

        if result["score"] > best_score:
            best_score = result["score"]
            best_text = current_text

        # Generate 3 appendices in parallel
        error_details = format_errors(result["errors"])
        append_tasks = [
            generate_appendix(client, base_text, result["score"],
                            result["true_acc"], result["false_acc"], error_details)
            for _ in range(3)
        ]
        appendices = await asyncio.gather(*append_tasks)
        appendices = [a for a in appendices if a]

        if not appendices:
            print("  No valid appendices generated")
            continue

        # Evaluate each appended version on SAME problems
        candidates = []
        for i, appendix in enumerate(appendices):
            candidate = base_text + "\n\n" + appendix
            size = len(candidate.encode("utf-8"))
            cand_result = await evaluate_cheatsheet(client, candidate, problems)
            print(f"  Append_{i}: {cand_result['score']:.0%} (T:{cand_result['true_acc']:.0%} F:{cand_result['false_acc']:.0%}, {size}B)")
            candidates.append((candidate, cand_result["score"], appendix, size))

        # Pick best
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_cand = candidates[0]

        if best_cand[1] > result["score"]:
            current_text = best_cand[0]
            base_text = current_text  # Next iteration appends to the new version
            print(f"\n  *** IMPROVED: {result['score']:.0%} -> {best_cand[1]:.0%} ({best_cand[3]}B) ***")
            (out / "best.txt").write_text(current_text, encoding="utf-8")

            if best_cand[1] > best_score:
                best_score = best_cand[1]
                best_text = current_text
        else:
            print(f"\n  No improvement. Best remains: {best_score:.0%}")

        elapsed = time.time() - t0
        print(f"  Time: {elapsed:.0f}s")

    print(f"\n{'='*60}")
    print(f"DONE | Best: {best_score:.0%} ({len(best_text.encode('utf-8'))} bytes)")
    print(f"{'='*60}")

    (out / "best.txt").write_text(best_text, encoding="utf-8")
    print(f"Saved to {out}/")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", default="cheatsheets/current.txt")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--api-key", default=DEFAULT_API_KEY)
    parser.add_argument("--output", default="optim/evolve_runs/run_append")
    args = parser.parse_args()

    if not args.endpoint or not args.api_key:
        print("ERROR: Set AZURE_FOUNDRY_BASE_URL and AZURE_INFERENCE_CREDENTIAL", file=sys.stderr)
        sys.exit(1)

    asyncio.run(run_append_evolution(
        seed_path=args.seed, n_iterations=args.iterations,
        endpoint=args.endpoint, api_key=args.api_key,
        output_dir=args.output,
    ))


if __name__ == "__main__":
    main()

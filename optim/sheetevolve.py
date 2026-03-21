"""
SheetEvolve — Evolutionary cheatsheet optimizer.

Fixes over the failed v1 evolutionary optimizer:
1. gpt-5-nano evaluator (competition target) instead of gpt-4.1-mini
2. seed=42 fixed problem sets (fair comparison across generations)
3. Parent eval caching (don't re-evaluate already-scored parents)
4. Diversity rejection (reject variants <20% different from pool)
5. Cascaded eval: 50-problem quick filter, then 200-problem full eval

Usage:
    python optim/sheetevolve.py --seed cheatsheets/best.txt --generations 3
"""

import argparse
import asyncio
import json
import random
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from eval.evaluate import evaluate_single, load_problems
from optim.api_logger import get_logged_async_client, get_call_count, reset_log

# --- Configuration ---
EVOLVER_MODEL = "gpt-5.4"
EVALUATOR_MODEL = "gpt-5-nano"
POOL_SIZE = 5
VARIANTS_PER_GEN = 3
STAGE1_SIZE = 50
STAGE1_CUTOFF = 0.75
STAGE2_SIZE = 200
DIVERSITY_THRESHOLD = 0.80  # SequenceMatcher.ratio() > this = too similar
CONCURRENCY = 20
PROBLEM_SEED = 42
NORMAL_PATH = "data/raw/normal.jsonl"
HARD_PATH = "data/raw/hard.jsonl"

# --- Evolver prompt ---
EVOLVER_PROMPT = """You are a professor helping improve a "cheatsheet" that a weak LLM student reads before answering math exam questions about equational implications of magmas.

The student reads the cheatsheet, then for each problem determines if Equation 1 implies Equation 2 (TRUE/FALSE). The student is not very smart — it needs explicit, unambiguous rules.

CURRENT CHEATSHEET (score: {score:.0%}, TRUE acc: {true_acc:.0%}, FALSE acc: {false_acc:.0%}, {size} bytes):
---
{cheatsheet}
---

THE STUDENT'S ERRORS (with its reasoning):
{errors}

YOUR TASK:
1. Read the errors carefully. Understand WHY the student got each one wrong.
2. Identify which rules are unclear, misleading, missing, or being misapplied.
3. Generate an IMPROVED version of the cheatsheet that fixes these issues.

CONSTRAINTS:
- Keep under 10KB (10240 bytes).
- DO NOT remove the core proven rules (Node 1: lone variable absent → TRUE, Node 2: LZ/RZ/C0/XOR counterexamples → FALSE). These are mathematically proven with 100% accuracy. Only clarify how they are explained.
- Focus changes on the areas that caused errors. Don't rewrite everything.
- Mathematical correctness is paramount. Don't add rules that are wrong.
- Be explicit, use examples, avoid ambiguity.

Output ONLY the improved cheatsheet text. No explanations, no markdown fences."""


async def evaluate_problems(client, cheatsheet_text, problems):
    """Evaluate cheatsheet on a list of problems. Returns detailed results."""
    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [
        evaluate_single(client, EVALUATOR_MODEL, cheatsheet_text, p, sem)
        for p in problems
    ]
    results = await asyncio.gather(*tasks)

    correct = sum(1 for r in results if r.get("correct"))
    total = len(results)
    true_correct = sum(
        1 for r in results if r.get("correct") and r.get("expected") is True
    )
    true_total = sum(1 for r in results if r.get("expected") is True)
    false_correct = sum(
        1 for r in results if r.get("correct") and r.get("expected") is False
    )
    false_total = sum(1 for r in results if r.get("expected") is False)

    errors = [r for r in results if not r.get("correct")]

    # Enrich errors with equation text
    prob_lookup = {p.get("id", ""): p for p in problems}
    for e in errors:
        pid = e.get("id", "")
        if pid in prob_lookup:
            e["equation1"] = prob_lookup[pid].get("equation1", "")
            e["equation2"] = prob_lookup[pid].get("equation2", "")

    return {
        "score": correct / total if total > 0 else 0,
        "correct": correct,
        "total": total,
        "true_acc": true_correct / true_total if true_total > 0 else 0,
        "false_acc": false_correct / false_total if false_total > 0 else 0,
        "true_n": true_total,
        "false_n": false_total,
        "errors": errors,
    }


def format_errors(errors, max_errors=15):
    """Format errors with equations and reasoning for the evolver."""
    if not errors:
        return "No errors — perfect score!"

    false_pos = [
        e
        for e in errors
        if e.get("expected") is False and e.get("predicted") is True
    ]
    false_neg = [
        e
        for e in errors
        if e.get("expected") is True and e.get("predicted") is False
    ]
    no_answer = [e for e in errors if e.get("predicted") is None]

    lines = [
        f"Total errors: {len(errors)}",
        f"  False positives (said TRUE, was FALSE): {len(false_pos)}",
        f"  False negatives (said FALSE, was TRUE): {len(false_neg)}",
        f"  No answer (token exhaustion/parse failure): {len(no_answer)}",
        "",
    ]

    # Sample errors proportionally
    sampled = []
    for group, label in [
        (false_pos, "SAID_TRUE_WAS_FALSE"),
        (false_neg, "SAID_FALSE_WAS_TRUE"),
        (no_answer, "NO_ANSWER"),
    ]:
        n = min(len(group), max(1, max_errors * len(group) // max(len(errors), 1)))
        if group:
            sampled.extend(
                (e, label) for e in random.sample(group, min(n, len(group)))
            )

    for e, label in sampled[:max_errors]:
        eq1 = e.get("equation1", "?")
        eq2 = e.get("equation2", "?")
        expected = "TRUE" if e.get("expected") else "FALSE"
        raw = (e.get("raw_response") or "(empty)")[:300]
        lines.append(
            f"[{label}] Eq1: {eq1}  |  Eq2: {eq2}  |  Correct answer: {expected}"
        )
        lines.append(f"  Student reasoning: {raw}")
        lines.append("")

    return "\n".join(lines)


def check_diversity(new_text, pool):
    """Return (is_diverse, max_similarity) — True if different enough from all pool members."""
    max_sim = 0.0
    for member in pool:
        ratio = SequenceMatcher(None, new_text, member["text"]).ratio()
        max_sim = max(max_sim, ratio)
        if ratio > DIVERSITY_THRESHOLD:
            return False, ratio
    return True, max_sim


async def generate_variant(client, parent_text, parent_result):
    """Use the evolver (gpt-5.4) to generate an improved cheatsheet."""
    error_details = format_errors(parent_result["errors"])
    prompt = EVOLVER_PROMPT.format(
        cheatsheet=parent_text,
        score=parent_result["score"],
        true_acc=parent_result["true_acc"],
        false_acc=parent_result["false_acc"],
        size=len(parent_text.encode("utf-8")),
        errors=error_details,
    )

    try:
        resp = await client.chat.completions.create(
            model=EVOLVER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=8192,
        )
        text = (resp.choices[0].message.content or "").strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:])
        if text.endswith("```"):
            text = "\n".join(text.split("\n")[:-1])
        text = text.strip()

        size = len(text.encode("utf-8"))
        if size > 10240:
            text = text[:10240].rsplit("\n", 1)[0]
            size = len(text.encode("utf-8"))

        return text if size >= 100 else ""
    except Exception as e:
        print(f"    Evolver error: {e}")
        return ""


def sample_fixed_problems(all_normal, all_hard, n_normal, n_hard, seed):
    """Sample a fixed set of problems using a specific seed."""
    rng = random.Random(seed)
    problems = rng.sample(all_normal, min(n_normal, len(all_normal)))
    problems += rng.sample(all_hard, min(n_hard, len(all_hard)))
    rng.shuffle(problems)
    return problems


async def run_sheetevolve(
    seed_path, n_generations, output_dir,
    n_variants=VARIANTS_PER_GEN, n_stage1=STAGE1_SIZE, n_stage2=STAGE2_SIZE,
):
    """Main evolution loop."""
    reset_log()
    client = get_logged_async_client()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Load all problems
    all_normal = load_problems(NORMAL_PATH)
    all_hard = load_problems(HARD_PATH)
    print(f"Loaded {len(all_normal)} normal + {len(all_hard)} hard problems")

    # Sample FIXED problem sets (deterministic, same every run)
    # Split 80/20 normal/hard like the official eval
    s1_normal = int(n_stage1 * 0.8)
    s1_hard = n_stage1 - s1_normal
    s2_normal = int(n_stage2 * 0.8)
    s2_hard = n_stage2 - s2_normal
    stage1_problems = sample_fixed_problems(
        all_normal, all_hard, s1_normal, s1_hard, PROBLEM_SEED
    )
    stage2_problems = sample_fixed_problems(
        all_normal, all_hard, s2_normal, s2_hard, PROBLEM_SEED + 1
    )

    print(f"Stage 1: {len(stage1_problems)} problems (filter, cutoff {STAGE1_CUTOFF:.0%})")
    print(f"Stage 2: {len(stage2_problems)} problems (full eval)")

    # Load seed cheatsheet
    seed_text = Path(seed_path).read_text(encoding="utf-8")
    seed_size = len(seed_text.encode("utf-8"))

    print(f"\n{'='*60}")
    print(f"SHEETEVOLVE")
    print(f"{'='*60}")
    print(f"Seed: {seed_path} ({seed_size} bytes)")
    print(f"Evolver: {EVOLVER_MODEL} | Evaluator: {EVALUATOR_MODEL}")
    print(f"Pool: {POOL_SIZE} | Variants/gen: {n_variants} | Gens: {n_generations}")
    print(f"Stage 1: {n_stage1} probs, cutoff {STAGE1_CUTOFF:.0%}")
    print(f"Stage 2: {n_stage2} probs (full eval)")
    print(f"Diversity: reject if similarity > {DIVERSITY_THRESHOLD:.0%}")
    print(f"{'='*60}")

    # --- Gen 0: Evaluate seed on stage 2 (full) ---
    print(f"\n--- Gen 0: Evaluating seed on {len(stage2_problems)} problems ---")
    t_start = time.time()
    t0 = time.time()
    seed_result = await evaluate_problems(client, seed_text, stage2_problems)
    print(
        f"Seed: {seed_result['score']:.1%} "
        f"({seed_result['correct']}/{seed_result['total']}) "
        f"T:{seed_result['true_acc']:.1%} F:{seed_result['false_acc']:.1%}"
    )
    print(f"  Errors: {len(seed_result['errors'])} | Time: {time.time()-t0:.0f}s")
    print(f"  API calls: {get_call_count()}")

    # Initialize pool
    pool = [
        {
            "text": seed_text,
            "name": "seed",
            "size": seed_size,
            "score": seed_result["score"],
            "result": seed_result,
        }
    ]
    best_ever = {
        "text": seed_text,
        "name": "seed",
        "size": seed_size,
        "score": seed_result["score"],
    }
    history = [
        {
            "gen": 0,
            "name": "seed",
            "score": seed_result["score"],
            "true_acc": seed_result["true_acc"],
            "false_acc": seed_result["false_acc"],
        }
    ]

    # Save seed results
    (out / "seed_result.json").write_text(
        json.dumps(
            {
                "score": seed_result["score"],
                "correct": seed_result["correct"],
                "total": seed_result["total"],
                "true_acc": seed_result["true_acc"],
                "false_acc": seed_result["false_acc"],
                "n_errors": len(seed_result["errors"]),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # --- Evolution loop ---
    for gen in range(1, n_generations + 1):
        t_gen = time.time()
        pool_str = ", ".join(
            f"{p['name']}={p['score']:.1%}" for p in pool
        )
        print(f"\n{'='*60}")
        print(f"GENERATION {gen}/{n_generations}")
        print(f"Pool: [{pool_str}]")
        print(f"Best ever: {best_ever['name']} = {best_ever['score']:.1%}")
        print(f"{'='*60}")

        # Step 1: Select parents (weighted by rank)
        weights = [POOL_SIZE - i for i in range(len(pool))]
        parents = []
        for _ in range(n_variants):
            parent = random.choices(pool, weights=weights[: len(pool)])[0]
            parents.append(parent)

        print(f"\nStep 1 — Selected parents:")
        for i, p in enumerate(parents):
            print(f"  Variant {i}: {p['name']} ({p['score']:.1%})")

        # Step 2: Get parent errors (CACHED — 0 API calls)
        print(f"\nStep 2 — Parent errors (cached, 0 new API calls)")
        for p in set(pp["name"] for pp in parents):
            match = next(x for x in pool if x["name"] == p)
            print(f"  {p}: {len(match['result']['errors'])} errors cached")

        # Step 3: Generate variants with the evolver
        print(f"\nStep 3 — Generating {n_variants} variants with {EVOLVER_MODEL}...")
        evolve_tasks = [
            generate_variant(client, p["text"], p["result"]) for p in parents
        ]
        variant_texts = await asyncio.gather(*evolve_tasks)

        variants = []
        for i, text in enumerate(variant_texts):
            if text:
                vname = f"gen{gen}_v{i}"
                vsize = len(text.encode("utf-8"))
                variants.append(
                    {"text": text, "name": vname, "size": vsize}
                )
                print(f"  {vname}: {vsize} bytes")
            else:
                print(f"  gen{gen}_v{i}: FAILED (empty)")

        if not variants:
            print("  No valid variants. Skipping generation.")
            continue

        print(f"  API calls so far: {get_call_count()}")

        # Step 4a: Stage 1 — quick filter
        print(
            f"\nStep 4a — Stage 1 filter "
            f"({len(stage1_problems)} probs, cutoff {STAGE1_CUTOFF:.0%})..."
        )
        s1_tasks = [
            evaluate_problems(client, v["text"], stage1_problems) for v in variants
        ]
        s1_results = await asyncio.gather(*s1_tasks)

        passed = []
        for v, result in zip(variants, s1_results):
            status = "PASS" if result["score"] >= STAGE1_CUTOFF else "FAIL"
            print(
                f"  {v['name']}: {result['score']:.1%} "
                f"({result['correct']}/{result['total']}) — {status}"
            )
            if result["score"] >= STAGE1_CUTOFF:
                passed.append(v)

        print(f"  {len(passed)}/{len(variants)} passed | API calls: {get_call_count()}")

        if not passed:
            print("  No variants passed stage 1. Skipping.")
            continue

        # Step 4b: Stage 2 — full evaluation
        print(f"\nStep 4b — Stage 2 full eval ({len(stage2_problems)} probs)...")
        s2_tasks = [
            evaluate_problems(client, v["text"], stage2_problems) for v in passed
        ]
        s2_results = await asyncio.gather(*s2_tasks)

        for v, result in zip(passed, s2_results):
            v["score"] = result["score"]
            v["result"] = result  # Cache for future use as parent
            print(
                f"  {v['name']}: {result['score']:.1%} "
                f"({result['correct']}/{result['total']}) "
                f"T:{result['true_acc']:.1%} F:{result['false_acc']:.1%}"
            )
            history.append(
                {
                    "gen": gen,
                    "name": v["name"],
                    "score": result["score"],
                    "true_acc": result["true_acc"],
                    "false_acc": result["false_acc"],
                }
            )

        print(f"  API calls: {get_call_count()}")

        # Step 5: Diversity check
        print(f"\nStep 5 — Diversity check (reject if > {DIVERSITY_THRESHOLD:.0%} similar)...")
        diverse = []
        for v in passed:
            is_div, sim = check_diversity(v["text"], pool)
            if is_div:
                diverse.append(v)
                print(f"  {v['name']}: DIVERSE (max similarity: {sim:.0%})")
            else:
                print(f"  {v['name']}: TOO SIMILAR ({sim:.0%}) — rejected")

        if not diverse:
            print("  No diverse variants. Pool unchanged.")
            continue

        # Step 6: Update pool
        print(f"\nStep 6 — Updating pool...")
        all_candidates = pool + diverse
        all_candidates.sort(key=lambda x: x["score"], reverse=True)
        pool = all_candidates[:POOL_SIZE]

        print(f"  New pool:")
        for i, p in enumerate(pool):
            marker = " ***" if p["score"] > best_ever["score"] else ""
            print(f"    {i+1}. {p['name']}: {p['score']:.1%} ({p['size']}B){marker}")

        if pool[0]["score"] > best_ever["score"]:
            best_ever = {
                "text": pool[0]["text"],
                "name": pool[0]["name"],
                "size": pool[0]["size"],
                "score": pool[0]["score"],
            }
            (out / "best.txt").write_text(best_ever["text"], encoding="utf-8")
            print(f"\n  *** NEW BEST: {best_ever['name']} = {best_ever['score']:.1%} ***")

        # Save pool variants to disk
        for i, p in enumerate(pool):
            fname = f"pool_{i}_{p['name']}.txt"
            (out / fname).write_text(p["text"], encoding="utf-8")

        # Save generation state
        gen_state = {
            "gen": gen,
            "pool": [
                {"name": p["name"], "score": p["score"], "size": p["size"]}
                for p in pool
            ],
            "best": {"name": best_ever["name"], "score": best_ever["score"]},
            "api_calls": get_call_count(),
            "elapsed_s": round(time.time() - t_gen, 1),
        }
        (out / f"gen{gen}_state.json").write_text(
            json.dumps(gen_state, indent=2), encoding="utf-8"
        )

        elapsed_gen = time.time() - t_gen
        print(f"\n  Gen {gen}: {elapsed_gen:.0f}s | Total API calls: {get_call_count()}")

    # --- Final summary ---
    total_time = time.time() - t_start
    print(f"\n{'='*60}")
    print(f"SHEETEVOLVE COMPLETE")
    print(f"{'='*60}")
    print(f"Seed: {history[0]['score']:.1%} -> Best: {best_ever['score']:.1%}")
    print(f"Best variant: {best_ever['name']}")
    print(f"Total API calls: {get_call_count()}")
    print(f"Total time: {total_time:.0f}s ({total_time/60:.1f}min)")

    final_pool_str = ", ".join(
        f"{p['name']}={p['score']:.1%}" for p in pool
    )
    print(f"Final pool: [{final_pool_str}]")
    print(f"{'='*60}")

    # Save final outputs
    (out / "best.txt").write_text(best_ever["text"], encoding="utf-8")
    (out / "history.json").write_text(
        json.dumps(history, indent=2), encoding="utf-8"
    )
    summary = {
        "seed_score": history[0]["score"],
        "best_score": best_ever["score"],
        "best_name": best_ever["name"],
        "generations": n_generations,
        "api_calls": get_call_count(),
        "total_seconds": round(total_time, 1),
        "pool_final": [
            {"name": p["name"], "score": p["score"]} for p in pool
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(f"Outputs saved to {out}/")
    return best_ever


def main():
    parser = argparse.ArgumentParser(
        description="SheetEvolve — evolutionary cheatsheet optimizer"
    )
    parser.add_argument(
        "--seed", default="cheatsheets/best.txt", help="Seed cheatsheet"
    )
    parser.add_argument(
        "--generations", type=int, default=3, help="Number of generations"
    )
    parser.add_argument(
        "--variants", type=int, default=VARIANTS_PER_GEN, help="Variants per generation"
    )
    parser.add_argument(
        "--stage1", type=int, default=STAGE1_SIZE, help="Stage 1 problem count"
    )
    parser.add_argument(
        "--stage2", type=int, default=STAGE2_SIZE, help="Stage 2 problem count"
    )
    parser.add_argument(
        "--output", default="optim/evolve_runs/v2", help="Output directory"
    )
    args = parser.parse_args()

    best = asyncio.run(
        run_sheetevolve(
            seed_path=args.seed,
            n_generations=args.generations,
            output_dir=args.output,
            n_variants=args.variants,
            n_stage1=args.stage1,
            n_stage2=args.stage2,
        )
    )

    seed_score = 0.835  # known baseline
    if best["score"] > seed_score:
        print(f"\nImprovement found! Copying best to cheatsheets/current.txt")
        Path("cheatsheets/current.txt").write_text(best["text"], encoding="utf-8")
    else:
        print(f"\nNo improvement over seed ({seed_score:.1%}). current.txt unchanged.")


if __name__ == "__main__":
    main()

"""
Error analysis tool for iterative cheatsheet optimization.

Reads eval results, groups errors by type, and outputs actionable insights.
Used in the error-driven iteration loop:
  1. eval_robust.py → last_robust_run.json
  2. analyze_errors.py → error groups + patterns
  3. Human/Claude designs fix
  4. Re-eval → compare

Usage:
    python eval/analyze_errors.py
    python eval/analyze_errors.py --file eval/last_robust_run.json
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def classify_error(result: dict) -> str | None:
    """Classify a single result into error type or None if correct."""
    if result.get("correct"):
        return None
    if result.get("error"):
        return "api_error"
    if result.get("predicted") is None:
        return "parse_error"
    if result["expected"] is True and result["predicted"] is False:
        return "false_negative"
    if result["expected"] is False and result["predicted"] is True:
        return "false_positive"
    return "unknown"


def extract_reasoning_patterns(raw: str) -> list[str]:
    """Extract key phrases from model response."""
    patterns = []
    raw_lower = raw.lower()
    if "substitut" in raw_lower:
        patterns.append("substitution")
    if "counterexample" in raw_lower:
        patterns.append("counterexample")
    if "constant" in raw_lower:
        patterns.append("constant_op")
    if "projection" in raw_lower:
        patterns.append("projection")
    if "clearly" in raw_lower or "obviously" in raw_lower:
        patterns.append("vague_reasoning")
    if "forces" in raw_lower:
        patterns.append("forces_claim")
    if "associat" in raw_lower:
        patterns.append("mentions_associativity")
    if "identity" in raw_lower:
        patterns.append("identity")
    if "trivial" in raw_lower:
        patterns.append("trivial_claim")
    if not raw.strip():
        patterns.append("empty_response")
    return patterns


def analyze(results_path: str):
    """Main analysis."""
    data = json.loads(Path(results_path).read_text(encoding="utf-8"))

    all_results = data.get("all_per_problem_results", [])
    if not all_results:
        # Try to find in seed_results
        for sr in data.get("seed_results", []):
            for model, mdata in sr.get("models", {}).items():
                for r in mdata.get("per_problem", []):
                    r["model"] = model
                    all_results.append(r)

    if not all_results:
        print("No per-problem results found!")
        return

    # Separate by model
    by_model = defaultdict(list)
    for r in all_results:
        by_model[r.get("model", "unknown")].append(r)

    print(f"Total results: {len(all_results)}")
    print(f"Models: {list(by_model.keys())}")
    print()

    for model, results in sorted(by_model.items()):
        print(f"{'='*60}")
        print(f"MODEL: {model} ({len(results)} problems)")
        print(f"{'='*60}")

        # Basic accuracy
        correct = sum(1 for r in results if r.get("correct"))
        print(f"Accuracy: {correct}/{len(results)} = {correct/len(results):.1%}")

        # Error classification
        errors = []
        for r in results:
            etype = classify_error(r)
            if etype:
                difficulty = "hard" if "hard" in r.get("id", "") else "normal"
                patterns = extract_reasoning_patterns(r.get("raw_response", ""))
                errors.append({
                    "id": r.get("id"),
                    "type": etype,
                    "difficulty": difficulty,
                    "expected": r.get("expected"),
                    "predicted": r.get("predicted"),
                    "patterns": patterns,
                    "response_preview": r.get("raw_response", "")[:150],
                })

        if not errors:
            print("  No errors!")
            continue

        # Group by type × difficulty
        print(f"\nError breakdown ({len(errors)} errors):")
        type_diff = Counter((e["type"], e["difficulty"]) for e in errors)
        for (etype, diff), count in sorted(type_diff.items()):
            print(f"  {etype:.<20s} {diff:.<10s} {count}")

        # Pattern analysis per error type
        print(f"\nReasoning patterns in errors:")
        for etype in ["false_positive", "false_negative", "parse_error", "api_error"]:
            type_errors = [e for e in errors if e["type"] == etype]
            if not type_errors:
                continue
            all_patterns = []
            for e in type_errors:
                all_patterns.extend(e["patterns"])
            pattern_counts = Counter(all_patterns)
            if pattern_counts:
                print(f"  {etype}:")
                for p, c in pattern_counts.most_common(5):
                    print(f"    {p}: {c}/{len(type_errors)} ({c/len(type_errors):.0%})")

        # Show specific errors
        print(f"\nDetailed errors:")
        for e in errors:
            marker = "FP" if e["type"] == "false_positive" else \
                     "FN" if e["type"] == "false_negative" else \
                     "PE" if e["type"] == "parse_error" else "??"
            print(f"  [{marker}] {e['id']} ({e['difficulty']}) "
                  f"exp={e['expected']} pred={e['predicted']}")
            if e["response_preview"]:
                preview = e["response_preview"].replace("\n", " ")[:120]
                print(f"       {preview}")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="eval/last_robust_run.json")
    args = parser.parse_args()
    analyze(args.file)


if __name__ == "__main__":
    main()

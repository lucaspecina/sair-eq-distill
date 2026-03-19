"""Compute satisfaction probability for each equation on random finite magmas.

Inspired by "The latent space of equational theories" (arxiv 2601.20759).
For each equation, we check: what fraction of random magmas satisfy it?
This gives a "restrictiveness score" — lower = more restrictive = stronger.
"""

import json
import sys
import random
import re

sys.stdout.reconfigure(encoding="utf-8")

random.seed(42)


def parse_equation_to_func(eq_str):
    """Convert equation string to a Python function that checks satisfaction.

    Returns a function: (op_table, n) -> bool
    where op_table[i][j] is the result of i ◇ j.
    """
    eq = eq_str.replace("\u25c7", "*")
    lhs, rhs = eq.split(" = ", 1)

    def eval_expr(expr, assignment, op):
        """Evaluate an expression given variable assignment and operation."""
        expr = expr.strip()
        # Try to parse as a single variable
        if len(expr) == 1 and expr in "xyzwuv":
            return assignment[expr]

        # Find the main operator (not inside parentheses)
        depth = 0
        main_op_pos = -1
        for i, c in enumerate(expr):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif c == "*" and depth == 0:
                main_op_pos = i
                break

        if main_op_pos >= 0:
            left = expr[:main_op_pos].strip()
            right = expr[main_op_pos + 1 :].strip()
            l_val = eval_expr(left, assignment, op)
            r_val = eval_expr(right, assignment, op)
            return op[l_val][r_val]

        # Strip outer parentheses
        if expr.startswith("(") and expr.endswith(")"):
            return eval_expr(expr[1:-1], assignment, op)

        raise ValueError(f"Cannot parse: {expr}")

    def check(op_table, n):
        """Check if the equation holds for ALL assignments in magma of size n."""
        variables = sorted(set(c for c in eq_str if c in "xyzwuv"))
        # Generate all assignments
        from itertools import product

        for vals in product(range(n), repeat=len(variables)):
            assignment = dict(zip(variables, vals))
            try:
                l_val = eval_expr(lhs, assignment, op_table)
                r_val = eval_expr(rhs, assignment, op_table)
                if l_val != r_val:
                    return False
            except (KeyError, IndexError, RecursionError):
                return False
        return True

    return check


def random_magma(n):
    """Generate a random magma of size n (random operation table)."""
    return [[random.randint(0, n - 1) for _ in range(n)] for _ in range(n)]


def main():
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines()]

    # Compile all equations
    print("Compiling equations...")
    checkers = []
    compile_errors = 0
    for eq in equations:
        try:
            checkers.append(parse_equation_to_func(eq))
        except Exception as e:
            checkers.append(None)
            compile_errors += 1
    print(f"Compiled: {len(checkers) - compile_errors}, errors: {compile_errors}")

    # Sample random magmas
    N_MAGMAS = 200
    MAGMA_SIZES = [2, 2, 2, 3, 3, 3, 4, 4, 5, 5]  # mix of sizes, small biased

    print(f"Generating {N_MAGMAS} random magmas...")
    magmas = []
    for i in range(N_MAGMAS):
        size = MAGMA_SIZES[i % len(MAGMA_SIZES)]
        magmas.append((size, random_magma(size)))

    # Test first few equations to make sure it works
    print("Testing equation 1 (x = x)...")
    if checkers[0]:
        n_sat = sum(1 for size, m in magmas if checkers[0](m, size))
        print(f"  Satisfied by {n_sat}/{N_MAGMAS} magmas (should be all)")

    print("Testing equation 2 (x = y)...")
    if checkers[1]:
        n_sat = sum(1 for size, m in magmas if checkers[1](m, size))
        print(f"  Satisfied by {n_sat}/{N_MAGMAS} magmas (should be very few)")

    # Compute satisfaction probabilities for ALL equations
    # This is O(n_equations * n_magmas * n_assignments) — can be slow
    # Let's do a subset first
    print(f"\nComputing satisfaction probabilities for all {len(equations)} equations...")
    print("(This may take a while...)")

    scores = []
    for eq_idx in range(len(equations)):
        if eq_idx % 500 == 0:
            print(f"  Progress: {eq_idx}/{len(equations)}")
        checker = checkers[eq_idx]
        if checker is None:
            scores.append(-1)
            continue
        n_sat = 0
        for size, m in magmas:
            try:
                if checker(m, size):
                    n_sat += 1
            except Exception:
                pass
        scores.append(n_sat / N_MAGMAS)

    # Analyze scores
    print(f"\n=== SATISFACTION SCORES ===")
    # Group by score ranges
    ranges = [(0, 0.01), (0.01, 0.05), (0.05, 0.1), (0.1, 0.2),
              (0.2, 0.5), (0.5, 0.8), (0.8, 1.0), (1.0, 1.01)]
    for lo, hi in ranges:
        count = sum(1 for s in scores if lo <= s < hi)
        print(f"  [{lo:.2f}, {hi:.2f}): {count} equations")

    # Extremes
    nonzero = [(i, s) for i, s in enumerate(scores) if 0 < s < 1]
    nonzero.sort(key=lambda x: x[1])
    print(f"\n  Equations with score = 0.0 (never satisfied): {sum(1 for s in scores if s == 0)}")
    print(f"  Equations with score = 1.0 (always satisfied): {sum(1 for s in scores if s >= 1.0)}")

    if nonzero:
        print(f"\n  Least satisfied (nonzero):")
        for i, s in nonzero[:5]:
            print(f"    Eq {i+1} ({s:.3f}): {equations[i]}")
        print(f"\n  Most satisfied (<1.0):")
        for i, s in nonzero[-5:]:
            print(f"    Eq {i+1} ({s:.3f}): {equations[i]}")

    # Save scores
    with open("data/processed/satisfaction_scores.json", "w") as f:
        json.dump({"scores": scores, "n_magmas": N_MAGMAS, "magma_sizes": MAGMA_SIZES}, f)
    print(f"\nSaved to data/processed/satisfaction_scores.json")

    # Key question: does satisfaction score predict implication?
    print("\n=== DOES SCORE PREDICT IMPLICATION? ===")
    for dataset in ["normal", "hard2"]:
        with open(f"data/raw/{dataset}.jsonl") as f:
            problems = [json.loads(line) for line in f]

        # Map problem equations to equation indices
        eq_index = {eq: i for i, eq in enumerate(equations)}

        correct = 0
        total = 0
        for p in problems:
            eq1_str = p["equation1"].replace("*", "\u25c7")
            eq2_str = p["equation2"].replace("*", "\u25c7")

            if eq1_str in eq_index and eq2_str in eq_index:
                s1 = scores[eq_index[eq1_str]]
                s2 = scores[eq_index[eq2_str]]

                # Heuristic: if eq1 is more restrictive (lower score),
                # it's more likely to imply eq2 (higher score)
                if s1 < s2:
                    prediction = True
                elif s1 > s2:
                    prediction = False
                else:
                    prediction = False  # default

                if prediction == p["answer"]:
                    correct += 1
                total += 1

        if total > 0:
            print(f"  {dataset}: score heuristic accuracy = {correct/total:.2%} ({correct}/{total})")
        else:
            print(f"  {dataset}: could not map equations")


if __name__ == "__main__":
    main()

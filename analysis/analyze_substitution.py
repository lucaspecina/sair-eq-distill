"""Test if syntactic substitution predicts implication.

Key hypothesis: If equation B can be obtained from equation A by substituting
variables with terms, then A implies B. This is a fundamental rule in
equational logic. How much of the implication matrix does this explain?
"""

import csv
import json
import re
import sys
from itertools import product

sys.stdout.reconfigure(encoding="utf-8")

# Parse an equation into a tree structure
def tokenize(s):
    """Tokenize an equation side into tokens."""
    tokens = []
    i = 0
    while i < len(s):
        if s[i] in "xyzwuv":
            tokens.append(s[i])
            i += 1
        elif s[i] == "\u25c7":  # ◇
            tokens.append("op")
            i += 1
        elif s[i] in "()":
            tokens.append(s[i])
            i += 1
        else:
            i += 1  # skip spaces
    return tokens


def parse_expr(tokens, pos=0):
    """Parse tokens into a tree. Returns (tree, next_pos)."""
    if pos >= len(tokens):
        return None, pos

    # Check for parenthesized expression or simple variable
    if tokens[pos] == "(":
        left, pos = parse_expr(tokens, pos + 1)
        if pos < len(tokens) and tokens[pos] == "op":
            pos += 1  # skip op
            right, pos = parse_expr(tokens, pos)
            if pos < len(tokens) and tokens[pos] == ")":
                pos += 1
            return ("op", left, right), pos
        if pos < len(tokens) and tokens[pos] == ")":
            pos += 1
        return left, pos
    elif tokens[pos] in "xyzwuv":
        var = tokens[pos]
        pos += 1
        # Check if followed by op (without parens)
        if pos < len(tokens) and tokens[pos] == "op":
            pos += 1
            right, pos = parse_expr(tokens, pos)
            return ("op", var, right), pos
        return var, pos
    return None, pos


def parse_equation(eq_str):
    """Parse equation string into (lhs_tree, rhs_tree)."""
    lhs, rhs = eq_str.split(" = ", 1)
    lhs_tokens = tokenize(lhs)
    rhs_tokens = tokenize(rhs)
    lhs_tree, _ = parse_expr(lhs_tokens)
    rhs_tree, _ = parse_expr(rhs_tokens)
    return lhs_tree, rhs_tree


def tree_to_str(tree):
    """Convert tree back to string for debugging."""
    if isinstance(tree, str):
        return tree
    if tree is None:
        return "?"
    op, left, right = tree
    return f"({tree_to_str(left)} \u25c7 {tree_to_str(right)})"


def match_pattern(pattern, target, bindings=None):
    """Check if target is an instance of pattern via variable substitution.

    Returns dict of variable -> subtree bindings, or None if no match.
    """
    if bindings is None:
        bindings = {}

    # If pattern is a variable, it can match anything
    if isinstance(pattern, str) and pattern in "xyzwuv":
        if pattern in bindings:
            # Must match previous binding
            return bindings if bindings[pattern] == target else None
        bindings[pattern] = target
        return bindings

    # Both must be operations
    if not isinstance(pattern, tuple) or not isinstance(target, tuple):
        return None

    _, p_left, p_right = pattern
    _, t_left, t_right = target

    bindings = match_pattern(p_left, t_left, bindings)
    if bindings is None:
        return None
    return match_pattern(p_right, t_right, bindings)


def is_substitution_instance(eq_a, eq_b):
    """Check if eq_b is a substitution instance of eq_a.

    eq_a: (lhs_a, rhs_a) as trees
    eq_b: (lhs_b, rhs_b) as trees

    Returns True if there exists a substitution sigma such that
    sigma(lhs_a) = lhs_b AND sigma(rhs_a) = rhs_b.
    """
    lhs_a, rhs_a = eq_a
    lhs_b, rhs_b = eq_b

    bindings = match_pattern(lhs_a, lhs_b)
    if bindings is None:
        return False
    bindings = match_pattern(rhs_a, rhs_b, bindings)
    return bindings is not None


def main():
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines()]

    # Parse all equations
    print("Parsing equations...")
    parsed = []
    parse_errors = 0
    for eq in equations:
        try:
            parsed.append(parse_equation(eq))
        except Exception:
            parsed.append(None)
            parse_errors += 1
    print(f"Parsed: {len(parsed) - parse_errors}, errors: {parse_errors}")

    # Test substitution on the problem datasets
    for dataset_name in ["normal", "hard1"]:
        with open(f"data/raw/{dataset_name}.jsonl") as f:
            problems = [json.loads(line) for line in f]

        n_subst_true = 0
        n_subst_false = 0
        n_correct = 0
        n_total = 0

        for p in problems:
            # Find equation indices
            # Problems use * instead of ◇, need to find matching equations
            eq1_str = p["equation1"]
            eq2_str = p["equation2"]
            expected = p["answer"]

            # Parse problem equations (they use * instead of ◇)
            try:
                eq1 = parse_equation(eq1_str.replace("*", "\u25c7"))
                eq2 = parse_equation(eq2_str.replace("*", "\u25c7"))
            except Exception:
                continue

            n_total += 1

            # Check if eq2 is a substitution instance of eq1
            # (if yes, eq1 implies eq2)
            is_subst = is_substitution_instance(eq1, eq2)

            if is_subst:
                n_subst_true += 1
                if expected:
                    n_correct += 1
            else:
                n_subst_false += 1
                # If not a substitution instance, we can't conclude anything
                # (implication might still hold for other reasons)

        print(f"\n=== {dataset_name} ({n_total} problems) ===")
        print(f"Substitution detected: {n_subst_true}")
        print(f"  Of which correct (actually implies): {n_correct}/{n_subst_true if n_subst_true else 1}")
        print(f"No substitution: {n_subst_false}")
        if n_subst_true > 0:
            precision = n_correct / n_subst_true
            print(f"Substitution precision: {precision:.2%}")


if __name__ == "__main__":
    main()

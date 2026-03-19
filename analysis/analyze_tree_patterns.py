"""Analyze equation parse tree patterns and their relation to implications.

Key question: can we identify structural tree patterns that predict implication?
"""

import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")


def parse_to_tree(expr):
    """Parse an equation expression into a nested tuple tree."""
    expr = expr.strip()
    if len(expr) == 1 and expr in "xyzwuv":
        return expr

    # Strip outer parens
    if expr.startswith("(") and expr.endswith(")"):
        # Check if these are the outermost matching parens
        depth = 0
        is_outer = True
        for i, c in enumerate(expr):
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            if depth == 0 and i < len(expr) - 1:
                is_outer = False
                break
        if is_outer:
            return parse_to_tree(expr[1:-1])

    # Find main operator (not inside parens)
    depth = 0
    for i, c in enumerate(expr):
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == "\u25c7" and depth == 0:
            left = expr[:i].strip()
            right = expr[i + 1 :].strip()
            return ("op", parse_to_tree(left), parse_to_tree(right))

    return expr


def tree_signature(tree, var_map=None):
    """Compute a canonical signature for a tree, normalizing variable names.

    Returns a string signature where variables are numbered by first appearance.
    """
    if var_map is None:
        var_map = {}

    if isinstance(tree, str) and tree in "xyzwuv":
        if tree not in var_map:
            var_map[tree] = f"v{len(var_map)}"
        return var_map[tree]

    if isinstance(tree, tuple) and tree[0] == "op":
        left_sig = tree_signature(tree[1], var_map)
        right_sig = tree_signature(tree[2], var_map)
        return f"({left_sig}*{right_sig})"

    return str(tree)


def tree_shape(tree):
    """Get the shape of a tree (ignoring variable names).

    Returns a string like "(v*(v*v))" describing the nesting structure.
    """
    if isinstance(tree, str) and tree in "xyzwuv":
        return "v"
    if isinstance(tree, tuple) and tree[0] == "op":
        return f"({tree_shape(tree[1])}*{tree_shape(tree[2])})"
    return "?"


def main():
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines()]

    # Parse all equations into trees
    trees = []
    for eq in equations:
        lhs, rhs = eq.split(" = ", 1)
        lhs_tree = parse_to_tree(lhs)
        rhs_tree = parse_to_tree(rhs)
        trees.append((lhs_tree, rhs_tree))

    # Compute signatures for all equations
    sigs = []
    for lhs_tree, rhs_tree in trees:
        var_map = {}
        lhs_sig = tree_signature(lhs_tree, var_map)
        rhs_sig = tree_signature(rhs_tree, var_map)
        sig = f"{lhs_sig}={rhs_sig}"
        sigs.append(sig)

    # How many unique signatures?
    sig_counts = collections.Counter(sigs)
    print(f"Unique equation signatures: {len(sig_counts)} (out of {len(equations)})")
    print(f"Top signatures:")
    for sig, count in sig_counts.most_common(10):
        print(f"  {count:>4}x: {sig}")

    # Compute shapes (ignoring ALL variable identity)
    shapes = []
    for lhs_tree, rhs_tree in trees:
        lhs_shape = tree_shape(lhs_tree)
        rhs_shape = tree_shape(rhs_tree)
        shapes.append(f"{lhs_shape}={rhs_shape}")

    shape_counts = collections.Counter(shapes)
    print(f"\nUnique equation shapes: {len(shape_counts)}")
    print(f"Top shapes:")
    for shape, count in shape_counts.most_common(10):
        print(f"  {count:>4}x: {shape}")

    # Analyze problem datasets by shape
    for dataset in ["normal", "hard2"]:
        with open(f"data/raw/{dataset}.jsonl") as f:
            problems = [json.loads(line) for line in f]

        print(f"\n=== {dataset} ===")
        eq_to_sig = {eq: sig for eq, sig in zip(equations, sigs)}

        # For TRUE implications, do the signatures relate?
        true_same_shape = 0
        false_same_shape = 0
        true_total = 0
        false_total = 0

        for p in problems:
            eq1 = p["equation1"].replace("*", "\u25c7")
            eq2 = p["equation2"].replace("*", "\u25c7")

            lhs1, rhs1 = eq1.split(" = ", 1)
            lhs2, rhs2 = eq2.split(" = ", 1)

            shape1 = f"{tree_shape(parse_to_tree(lhs1))}={tree_shape(parse_to_tree(rhs1))}"
            shape2 = f"{tree_shape(parse_to_tree(lhs2))}={tree_shape(parse_to_tree(rhs2))}"

            if p["answer"]:
                true_total += 1
                if shape1 == shape2:
                    true_same_shape += 1
            else:
                false_total += 1
                if shape1 == shape2:
                    false_same_shape += 1

        print(f"  TRUE same shape: {true_same_shape}/{true_total} ({true_same_shape/true_total*100:.1f}%)")
        print(f"  FALSE same shape: {false_same_shape}/{false_total} ({false_same_shape/false_total*100:.1f}%)")


if __name__ == "__main__":
    main()

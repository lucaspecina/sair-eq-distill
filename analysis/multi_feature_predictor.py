"""Build a multi-feature predictor for equational implications.

This tells us the ceiling of what rule-based approaches can achieve,
and which features are most informative for the cheatsheet.
"""

import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")


def load_equations():
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]


def load_satisfaction_scores():
    with open("data/processed/satisfaction_scores.json") as f:
        data = json.load(f)
    return data["scores"]


def eq_features(eq_str, sat_scores, eq_index):
    """Extract features from a single equation."""
    eq_canon = eq_str.replace("*", "\u25c7")
    lhs, rhs = eq_canon.split(" = ", 1)

    vars_l = set(c for c in lhs if c in "xyzwuv")
    vars_r = set(c for c in rhs if c in "xyzwuv")
    all_vars = vars_l | vars_r

    ops_l = lhs.count("\u25c7")
    ops_r = rhs.count("\u25c7")

    depth_l = 0
    max_depth_l = 0
    for c in lhs:
        if c == "(":
            depth_l += 1
            max_depth_l = max(max_depth_l, depth_l)
        elif c == ")":
            depth_l -= 1

    depth_r = 0
    max_depth_r = 0
    for c in rhs:
        if c == "(":
            depth_r += 1
            max_depth_r = max(max_depth_r, depth_r)
        elif c == ")":
            depth_r -= 1

    # Get satisfaction score if available
    sat = -1
    if eq_canon in eq_index:
        idx = eq_index[eq_canon]
        if idx < len(sat_scores):
            sat = sat_scores[idx]

    return {
        "n_vars": len(all_vars),
        "vars_lhs": len(vars_l),
        "vars_rhs": len(vars_r),
        "shared_vars": len(vars_l & vars_r),
        "lhs_only_vars": len(vars_l - vars_r),
        "rhs_only_vars": len(vars_r - vars_l),
        "ops_lhs": ops_l,
        "ops_rhs": ops_r,
        "total_ops": ops_l + ops_r,
        "depth_lhs": max_depth_l,
        "depth_rhs": max_depth_r,
        "max_depth": max(max_depth_l, max_depth_r),
        "lhs_is_var": len(lhs.strip()) == 1,
        "satisfaction": sat,
    }


def predict(f1, f2):
    """Rule-based predictor using multiple features.
    Returns True if we predict eq1 implies eq2.
    """
    # Rule 1: If both satisfaction scores are known, use them
    if f1["satisfaction"] >= 0 and f2["satisfaction"] >= 0:
        s1, s2 = f1["satisfaction"], f2["satisfaction"]
        # If eq1 is never satisfied (score=0), it implies everything
        # (vacuously true for the equivalence class of x=y)
        if s1 == 0:
            return True
        # If eq2 is always satisfied (score=1), everything implies it
        if s2 >= 1.0:
            return True
        # Strong signal: if eq1 is much more restrictive than eq2
        if s1 < s2 - 0.05:
            return True
        if s1 > s2 + 0.05:
            return False

    # Rule 2: rhs_only_vars difference (strongest pair feature)
    rhs_diff = f1["rhs_only_vars"] - f2["rhs_only_vars"]
    if rhs_diff > 1:
        return True
    if rhs_diff < -1:
        return False

    # Rule 3: total variable count
    var_diff = f1["n_vars"] - f2["n_vars"]
    if var_diff > 1:
        return True
    if var_diff < -1:
        return False

    # Rule 4: If eq1 has single-var LHS and eq2 doesn't, slight lean true
    if f1["lhs_is_var"] and not f2["lhs_is_var"]:
        # But check satisfaction scores
        if f1["satisfaction"] >= 0 and f2["satisfaction"] >= 0:
            if f1["satisfaction"] <= f2["satisfaction"]:
                return True

    # Default: FALSE (63% base rate)
    return False


def predict_v2(f1, f2):
    """Simpler version: satisfaction score + variable heuristic."""
    s1, s2 = f1["satisfaction"], f2["satisfaction"]

    # Satisfaction-based prediction
    if s1 >= 0 and s2 >= 0:
        if s1 == 0:
            return True  # vacuously true
        if s2 >= 1.0:
            return True  # tautology
        if s1 < s2 - 0.02:
            return True
        if s1 > s2 + 0.02:
            return False

    # Variable-based fallback
    var_diff = f1["n_vars"] - f2["n_vars"]
    rhs_diff = f1["rhs_only_vars"] - f2["rhs_only_vars"]
    score = var_diff * 2 + rhs_diff * 3

    if score > 2:
        return True
    if score < -1:
        return False

    return False  # default


def main():
    equations = load_equations()
    sat_scores = load_satisfaction_scores()
    eq_index = {eq: i for i, eq in enumerate(equations)}

    for dataset in ["normal", "hard", "hard1", "hard2"]:
        with open(f"data/raw/{dataset}.jsonl") as f:
            problems = [json.loads(line) for line in f]

        results = {"v1": 0, "v2": 0, "always_false": 0, "total": 0}

        for p in problems:
            f1 = eq_features(p["equation1"], sat_scores, eq_index)
            f2 = eq_features(p["equation2"], sat_scores, eq_index)
            expected = p["answer"]

            results["total"] += 1
            if predict(f1, f2) == expected:
                results["v1"] += 1
            if predict_v2(f1, f2) == expected:
                results["v2"] += 1
            if not expected:
                results["always_false"] += 1

        n = results["total"]
        print(f"=== {dataset} ({n} problems) ===")
        print(f"  Multi-feature v1:     {results['v1']/n:.2%} ({results['v1']}/{n})")
        print(f"  Satisfaction + vars:  {results['v2']/n:.2%} ({results['v2']}/{n})")
        print(f"  Always false:         {results['always_false']/n:.2%}")
        print()


if __name__ == "__main__":
    main()

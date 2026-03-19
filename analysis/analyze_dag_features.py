"""Analyze what syntactic features predict position in the quotient DAG."""

import json
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")


def extract_features(eq_str):
    """Extract syntactic features from an equation string."""
    lhs, rhs = eq_str.split(" = ", 1)

    def side_features(s):
        ops = s.count("\u25c7")
        variables = set(c for c in s if c in "xyzwuv")
        depth = 0
        max_depth = 0
        for c in s:
            if c == "(":
                depth += 1
                max_depth = max(max_depth, depth)
            elif c == ")":
                depth -= 1
        # Is it a single variable?
        is_var = len(s.strip()) == 1 and s.strip() in "xyzwuv"
        return {
            "ops": ops,
            "vars": variables,
            "n_vars": len(variables),
            "depth": max_depth,
            "is_var": is_var,
            "len": len(s),
        }

    l = side_features(lhs)
    r = side_features(rhs)
    all_vars = l["vars"] | r["vars"]

    # Shared variables between LHS and RHS
    shared_vars = l["vars"] & r["vars"]

    # Variables only on one side
    lhs_only_vars = l["vars"] - r["vars"]
    rhs_only_vars = r["vars"] - l["vars"]

    return {
        "total_ops": l["ops"] + r["ops"],
        "lhs_ops": l["ops"],
        "rhs_ops": r["ops"],
        "total_vars": len(all_vars),
        "shared_vars": len(shared_vars),
        "lhs_only_vars": len(lhs_only_vars),
        "rhs_only_vars": len(rhs_only_vars),
        "max_depth": max(l["depth"], r["depth"]),
        "lhs_depth": l["depth"],
        "rhs_depth": r["depth"],
        "lhs_is_var": l["is_var"],
        "depth_diff": abs(l["depth"] - r["depth"]),
        "ops_diff": abs(l["ops"] - r["ops"]),
    }


def main():
    # Load equations
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines()]

    # Load quotient DAG data
    with open("data/processed/quotient_dag.json", encoding="utf-8") as f:
        dag = json.load(f)

    # Map equation index to class and level
    classes = dag["classes"]
    eq_to_level = {}
    eq_to_class_size = {}
    for cls in classes:
        level = cls["dag_level"]
        size = cls["size"]
        # We need to map back to equation indices
        # The classes contain equation IDs (1-based in first 5)
        # But we need the full mapping. Let's use representative equation
        rep_eq = cls["representative"]
        # Find this equation in our list
        for i, eq in enumerate(equations):
            if eq == rep_eq:
                eq_to_level[i] = level
                eq_to_class_size[i] = size
                break

    # Actually, let's reload the full class membership
    # For now, just analyze representatives
    print(f"Mapped {len(eq_to_level)} representative equations to levels")

    # Feature correlation with level
    print("\n=== FEATURES vs DAG LEVEL ===")

    features_by_level = collections.defaultdict(list)
    for eq_idx, level in eq_to_level.items():
        feats = extract_features(equations[eq_idx])
        features_by_level[level].append(feats)

    for feat_name in ["total_ops", "total_vars", "max_depth", "lhs_is_var",
                       "shared_vars", "lhs_only_vars", "rhs_only_vars",
                       "depth_diff", "ops_diff"]:
        print(f"\n{feat_name} by level:")
        for level in sorted(features_by_level.keys()):
            feats = features_by_level[level]
            vals = [f[feat_name] for f in feats]
            if isinstance(vals[0], bool):
                avg = sum(1 for v in vals if v) / len(vals)
                print(f"  Level {level:2d} ({len(feats):>4} classes): {avg:.2%} True")
            else:
                avg = sum(vals) / len(vals)
                print(f"  Level {level:2d} ({len(feats):>4} classes): avg={avg:.2f}")

    # Analyze the problem datasets: what level are the equations in?
    print("\n=== PROBLEM EQUATIONS vs DAG LEVEL ===")
    for dataset in ["normal", "hard1", "hard2"]:
        with open(f"data/raw/{dataset}.jsonl") as f:
            problems = [json.loads(line) for line in f]

        # For each problem, find features of both equations
        true_probs = [p for p in problems if p["answer"]]
        false_probs = [p for p in problems if not p["answer"]]

        for label, probs in [("TRUE", true_probs), ("FALSE", false_probs)]:
            feats1 = [extract_features(p["equation1"].replace("*", "\u25c7")) for p in probs]
            feats2 = [extract_features(p["equation2"].replace("*", "\u25c7")) for p in probs]

            # Compare features between eq1 and eq2
            ops_diffs = [f1["total_ops"] - f2["total_ops"] for f1, f2 in zip(feats1, feats2)]
            var_diffs = [f1["total_vars"] - f2["total_vars"] for f1, f2 in zip(feats1, feats2)]
            depth_diffs = [f1["max_depth"] - f2["max_depth"] for f1, f2 in zip(feats1, feats2)]

            avg_ops = sum(ops_diffs) / len(ops_diffs) if ops_diffs else 0
            avg_vars = sum(var_diffs) / len(var_diffs) if var_diffs else 0
            avg_depth = sum(depth_diffs) / len(depth_diffs) if depth_diffs else 0

            print(f"\n  {dataset} {label} ({len(probs)} problems):")
            print(f"    ops(eq1)-ops(eq2):   avg={avg_ops:+.2f}")
            print(f"    vars(eq1)-vars(eq2): avg={avg_vars:+.2f}")
            print(f"    depth(eq1)-depth(eq2): avg={avg_depth:+.2f}")

    # Key question: for TRUE implications, does eq1 tend to have more vars/ops?
    # (i.e., is it "stronger"?)
    print("\n=== STRONGEST PREDICTORS ===")
    for dataset in ["normal", "hard2"]:
        with open(f"data/raw/{dataset}.jsonl") as f:
            problems = [json.loads(line) for line in f]

        correct = 0
        total = 0
        for p in problems:
            f1 = extract_features(p["equation1"].replace("*", "\u25c7"))
            f2 = extract_features(p["equation2"].replace("*", "\u25c7"))

            # Heuristic: if eq1 has more vars or deeper nesting, it's "stronger"
            # and more likely to imply eq2
            strength1 = f1["total_vars"] * 10 + f1["max_depth"]
            strength2 = f2["total_vars"] * 10 + f2["max_depth"]

            if strength1 > strength2:
                prediction = True  # stronger implies weaker
            elif strength1 < strength2:
                prediction = False
            else:
                prediction = False  # default to false when tied

            if prediction == p["answer"]:
                correct += 1
            total += 1

        print(f"  {dataset}: vars+depth heuristic accuracy = {correct/total:.2%} ({correct}/{total})")

        # Try: just predict "False" always
        n_false = sum(1 for p in problems if not p["answer"])
        print(f"  {dataset}: always-False baseline = {n_false/total:.2%} ({n_false}/{total})")


if __name__ == "__main__":
    main()

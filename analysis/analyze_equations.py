"""Analyze the structure of the 4694 equational laws."""

import collections
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def parse_equation(eq_str):
    """Parse an equation string into structured data."""
    lhs, rhs = eq_str.split(" = ", 1)

    def analyze_side(s):
        ops = s.count("\u25c7")  # ◇
        parens = s.count("(")
        variables = set(c for c in s if c in "xyzwuv")
        max_depth = 0
        depth = 0
        for c in s:
            if c == "(":
                depth += 1
                max_depth = max(max_depth, depth)
            elif c == ")":
                depth -= 1
        return {
            "ops": ops,
            "parens": parens,
            "vars": variables,
            "n_vars": len(variables),
            "depth": max_depth,
            "len": len(s),
        }

    l = analyze_side(lhs)
    r = analyze_side(rhs)
    all_vars = l["vars"] | r["vars"]

    return {
        "raw": eq_str,
        "lhs": lhs,
        "rhs": rhs,
        "total_ops": l["ops"] + r["ops"],
        "lhs_ops": l["ops"],
        "rhs_ops": r["ops"],
        "total_vars": len(all_vars),
        "vars": sorted(all_vars),
        "lhs_depth": l["depth"],
        "rhs_depth": r["depth"],
        "max_depth": max(l["depth"], r["depth"]),
        "total_len": len(eq_str),
    }


def main():
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Total equations: {len(equations)}")

    parsed = [parse_equation(eq) for eq in equations]

    # Basic stats
    print(f"\n=== STRUCTURAL STATS ===")
    for key in ["total_ops", "total_vars", "max_depth", "total_len"]:
        vals = [p[key] for p in parsed]
        dist = dict(sorted(collections.Counter(vals).items()))
        print(f"{key}: {dist}")

    # LHS vs RHS asymmetry
    print(f"\n=== LHS vs RHS ===")
    lhs_ops = collections.Counter(p["lhs_ops"] for p in parsed)
    rhs_ops = collections.Counter(p["rhs_ops"] for p in parsed)
    print(f"LHS ops: {dict(sorted(lhs_ops.items()))}")
    print(f"RHS ops: {dict(sorted(rhs_ops.items()))}")

    # How many have LHS = single variable?
    single_var_lhs = sum(1 for p in parsed if p["lhs_ops"] == 0 and len(p["lhs"].strip()) == 1)
    print(f"Equations with single-variable LHS: {single_var_lhs} ({single_var_lhs/len(parsed)*100:.1f}%)")

    # Variable patterns
    print(f"\n=== VARIABLE PATTERNS ===")
    var_patterns = collections.Counter(tuple(p["vars"]) for p in parsed)
    print(f"Unique variable sets: {len(var_patterns)}")
    for pattern, count in var_patterns.most_common(10):
        print(f"  {pattern}: {count}")

    # Special equations
    print(f"\n=== SPECIAL EQUATIONS ===")
    print(f"Eq 1 (tautology): {equations[0]}")
    print(f"Eq 2 (collapse): {equations[1]}")

    # Equations with 0 ops (trivial)
    trivial = [i for i, p in enumerate(parsed) if p["total_ops"] == 0]
    print(f"Equations with 0 ops: {len(trivial)} -> {[equations[i] for i in trivial]}")

    # Save parsed data for further analysis
    for p in parsed:
        p["vars"] = list(p["vars"])
    with open("data/processed/equations_parsed.json", "w", encoding="utf-8") as f:
        json.dump(parsed, f, indent=2, ensure_ascii=False)
    print(f"\nSaved parsed data to data/processed/equations_parsed.json")


if __name__ == "__main__":
    main()

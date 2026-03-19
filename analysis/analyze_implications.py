"""Analyze the 4694x4694 implication matrix."""

import csv
import collections
import json
import sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")


def load_matrix(path: str) -> np.ndarray:
    """Load the raw implications CSV as numpy matrix."""
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append([int(x) for x in row])
    return np.array(rows, dtype=np.int8)


def main():
    print("Loading implication matrix...")
    M = load_matrix("data/raw/export_raw_implications_18_3_2026.csv")
    print(f"Shape: {M.shape}")
    N = M.shape[0]

    # Value distribution
    print(f"\n=== VALUE DISTRIBUTION ===")
    for val in [3, -3, 4, -4]:
        count = np.sum(M == val)
        label = {3: "true", -3: "false", 4: "hard-true", -4: "hard-false"}[val]
        print(f"  {val:>3} ({label:>10}): {count:>12,} ({count/(N*N)*100:.2f}%)")

    # Derive boolean matrix: true implications (3 or 4)
    T = (M == 3) | (M == 4)  # true implication
    n_true = np.sum(T)
    n_false = N * N - n_true
    print(f"\nTrue implications: {n_true:,} ({n_true/(N*N)*100:.1f}%)")
    print(f"False implications: {n_false:,} ({n_false/(N*N)*100:.1f}%)")

    # Per-equation stats
    implies_count = np.sum(T, axis=1)  # how many equations does eq i imply?
    implied_by_count = np.sum(T, axis=0)  # how many equations imply eq j?

    print(f"\n=== IMPLICATIONS PER EQUATION ===")
    print(f"Implies others:  min={implies_count.min()}, max={implies_count.max()}, "
          f"median={np.median(implies_count):.0f}, mean={implies_count.mean():.1f}")
    print(f"Implied by:      min={implied_by_count.min()}, max={implied_by_count.max()}, "
          f"median={np.median(implied_by_count):.0f}, mean={implied_by_count.mean():.1f}")

    # Most/least powerful equations (imply the most)
    print(f"\n=== MOST POWERFUL (imply the most) ===")
    top_implies = np.argsort(implies_count)[::-1][:10]
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines()]
    for idx in top_implies:
        print(f"  Eq {idx+1} ({implies_count[idx]:>4} implications): {equations[idx]}")

    # Most implied (implied by the most)
    print(f"\n=== MOST IMPLIED BY (easiest to satisfy) ===")
    top_implied = np.argsort(implied_by_count)[::-1][:10]
    for idx in top_implied:
        print(f"  Eq {idx+1} (implied by {implied_by_count[idx]:>4}): {equations[idx]}")

    # Least implied (hardest to satisfy / most restrictive)
    print(f"\n=== LEAST IMPLIED BY (most restrictive) ===")
    bot_implied = np.argsort(implied_by_count)[:10]
    for idx in bot_implied:
        print(f"  Eq {idx+1} (implied by {implied_by_count[idx]:>4}): {equations[idx]}")

    # Equivalence classes: equations that imply each other
    print(f"\n=== EQUIVALENCE CLASSES ===")
    equiv_matrix = T & T.T  # mutual implication
    # Find connected components via simple BFS
    visited = set()
    classes = []
    for i in range(N):
        if i in visited:
            continue
        # BFS from i
        queue = [i]
        component = set()
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            component.add(node)
            for j in range(N):
                if j not in visited and equiv_matrix[i, j] and equiv_matrix[j, i]:
                    queue.append(j)
        classes.append(sorted(component))

    non_trivial = [c for c in classes if len(c) > 1]
    print(f"Total equivalence classes: {len(classes)}")
    print(f"Non-trivial (size > 1): {len(non_trivial)}")
    sizes = sorted([len(c) for c in non_trivial], reverse=True)
    print(f"Largest classes: {sizes[:20]}")

    # Show a few equivalence classes
    for cls in sorted(non_trivial, key=len, reverse=True)[:5]:
        eqs = [equations[i] for i in cls[:5]]
        suffix = f"... +{len(cls)-5} more" if len(cls) > 5 else ""
        print(f"  Size {len(cls)}: {eqs} {suffix}")

    # Hard problems analysis
    hard_true = np.sum(M == 4)
    hard_false = np.sum(M == -4)
    print(f"\n=== HARD PROBLEMS ===")
    print(f"Hard-true (4): {hard_true:,}")
    print(f"Hard-false (-4): {hard_false:,}")

    # Which equations are involved in hard problems?
    hard_rows = set()
    hard_cols = set()
    for i in range(N):
        for j in range(N):
            if abs(M[i, j]) == 4:
                hard_rows.add(i)
                hard_cols.add(j)
    print(f"Equations involved as LHS in hard: {len(hard_rows)}")
    print(f"Equations involved as RHS in hard: {len(hard_cols)}")

    # Transitivity check: if A->B and B->C, does A->C hold?
    print(f"\n=== TRANSITIVITY SAMPLE ===")
    # Sample 1000 random triples and check
    rng = np.random.default_rng(42)
    n_checked = 0
    n_transitive = 0
    for _ in range(10000):
        a, b, c = rng.integers(0, N, size=3)
        if T[a, b] and T[b, c]:
            n_checked += 1
            if T[a, c]:
                n_transitive += 1
    print(f"Checked {n_checked} transitive triples (A->B, B->C)")
    print(f"A->C holds: {n_transitive} ({n_transitive/n_checked*100:.1f}%)")

    # Save summary stats
    stats = {
        "n_equations": N,
        "n_true": int(n_true),
        "n_false": int(n_false),
        "pct_true": round(n_true / (N * N) * 100, 2),
        "hard_true": int(hard_true),
        "hard_false": int(hard_false),
        "n_equiv_classes": len(classes),
        "n_nontrivial_equiv": len(non_trivial),
        "largest_equiv_class": max(len(c) for c in classes),
        "implies_count_stats": {
            "min": int(implies_count.min()),
            "max": int(implies_count.max()),
            "median": float(np.median(implies_count)),
            "mean": float(implies_count.mean()),
        },
    }
    with open("data/processed/implication_stats.json", "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nSaved stats to data/processed/implication_stats.json")

    # Save per-equation implication counts
    eq_stats = []
    for i in range(N):
        eq_stats.append({
            "id": i + 1,
            "equation": equations[i],
            "implies": int(implies_count[i]),
            "implied_by": int(implied_by_count[i]),
        })
    with open("data/processed/equation_stats.json", "w") as f:
        json.dump(eq_stats, f, indent=2, ensure_ascii=False)
    print(f"Saved per-equation stats to data/processed/equation_stats.json")


if __name__ == "__main__":
    main()

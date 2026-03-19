"""Analyze the quotient DAG of equivalence classes."""

import csv
import json
import sys
import numpy as np
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def load_matrix(path: str) -> np.ndarray:
    """Load the raw implications CSV as numpy matrix."""
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append([int(x) for x in row])
    return np.array(rows, dtype=np.int8)


def find_equivalence_classes(T: np.ndarray) -> list[list[int]]:
    """Find equivalence classes (mutual implication)."""
    N = T.shape[0]
    equiv = T & T.T  # mutual implication
    visited = set()
    classes = []
    for i in range(N):
        if i in visited:
            continue
        component = {i}
        queue = [i]
        while queue:
            node = queue.pop(0)
            for j in range(N):
                if j not in visited and j not in component and equiv[node, j]:
                    component.add(j)
                    queue.append(j)
            visited.add(node)
        classes.append(sorted(component))
    return classes


def main():
    print("Loading matrix...")
    M = load_matrix("data/raw/export_raw_implications_18_3_2026.csv")
    T = (M == 3) | (M == 4)
    N = T.shape[0]

    print("Finding equivalence classes...")
    classes = find_equivalence_classes(T)
    print(f"Classes: {len(classes)}")

    # Map each equation to its class
    eq_to_class = {}
    for ci, cls in enumerate(classes):
        for eq in cls:
            eq_to_class[eq] = ci

    # Build quotient DAG: class i -> class j if any eq in i implies any eq in j
    # (and they're different classes)
    print("Building quotient DAG...")
    n_classes = len(classes)
    dag = np.zeros((n_classes, n_classes), dtype=bool)

    # Use representatives: just check first element of each class
    for ci in range(n_classes):
        rep_i = classes[ci][0]
        for cj in range(n_classes):
            if ci == cj:
                dag[ci, cj] = True  # reflexive
                continue
            rep_j = classes[cj][0]
            if T[rep_i, rep_j]:
                dag[ci, cj] = True

    n_edges = np.sum(dag) - n_classes  # exclude self-loops
    print(f"Quotient DAG: {n_classes} nodes, {n_edges} edges")

    # Compute transitive reduction (remove edges implied by transitivity)
    print("Computing transitive reduction...")
    # Simple approach: for each edge (i,j), check if there's a path i->k->j
    reduction = dag.copy()
    for i in range(n_classes):
        for j in range(n_classes):
            if i == j or not dag[i, j]:
                continue
            # Check if there's an intermediate k
            for k in range(n_classes):
                if k == i or k == j:
                    continue
                if dag[i, k] and dag[k, j]:
                    reduction[i, j] = False
                    break

    n_red_edges = np.sum(reduction) - n_classes
    print(f"Transitive reduction: {n_red_edges} edges (from {n_edges})")

    # DAG statistics
    out_degree = np.sum(reduction, axis=1) - 1  # exclude self
    in_degree = np.sum(reduction, axis=0) - 1
    print(f"\nOut-degree: min={out_degree.min()}, max={out_degree.max()}, "
          f"mean={out_degree.mean():.1f}, median={np.median(out_degree):.0f}")
    print(f"In-degree: min={in_degree.min()}, max={in_degree.max()}, "
          f"mean={in_degree.mean():.1f}, median={np.median(in_degree):.0f}")

    # Sources (no incoming except self) and sinks (no outgoing except self)
    sources = [i for i in range(n_classes) if in_degree[i] == 0]
    sinks = [i for i in range(n_classes) if out_degree[i] == 0]
    print(f"Sources (top of partial order): {len(sources)}")
    print(f"Sinks (bottom of partial order): {len(sinks)}")

    # Longest chain
    print("\nComputing longest chain (height of DAG)...")
    # Topological sort + longest path
    topo_order = []
    visited = set()
    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for j in range(n_classes):
            if j != node and reduction[node, j]:
                dfs(j)
        topo_order.append(node)
    for i in range(n_classes):
        dfs(i)
    topo_order.reverse()

    longest_path = np.zeros(n_classes, dtype=int)
    for node in topo_order:
        for j in range(n_classes):
            if j != node and reduction[node, j]:
                longest_path[j] = max(longest_path[j], longest_path[node] + 1)
    height = longest_path.max()
    print(f"Height of DAG (longest chain): {height}")

    # Width at each level
    levels = defaultdict(int)
    for i in range(n_classes):
        levels[int(longest_path[i])] += 1
    print(f"Width by level: {dict(sorted(levels.items())[:20])}")

    # Load equations for annotation
    with open("data/raw/equations.txt", encoding="utf-8") as f:
        equations = [line.strip() for line in f.readlines()]

    # Print the chain structure
    print(f"\n=== TOP OF PARTIAL ORDER (sources) ===")
    for s in sources[:10]:
        rep = classes[s][0]
        print(f"  Class {s} (size {len(classes[s])}): {equations[rep]}")

    print(f"\n=== BOTTOM OF PARTIAL ORDER (sinks) ===")
    for s in sinks[:10]:
        rep = classes[s][0]
        print(f"  Class {s} (size {len(classes[s])}): {equations[rep]}")

    # Key question: how much of the DAG can be described by simple rules?
    # E.g., does "more variables = higher in the order" hold?
    print(f"\n=== VARIABLE COUNT vs DAG LEVEL ===")
    for ci in range(n_classes):
        rep = classes[ci][0]
        eq = equations[rep]
        n_vars = len(set(c for c in eq if c in "xyzwuv"))
        # This is a rough heuristic

    # Save quotient DAG data
    dag_data = {
        "n_classes": n_classes,
        "n_edges_full": int(n_edges),
        "n_edges_reduction": int(n_red_edges),
        "height": int(height),
        "n_sources": len(sources),
        "n_sinks": len(sinks),
        "classes": [
            {
                "id": ci,
                "size": len(cls),
                "representative": equations[cls[0]],
                "equations": [cls[0] + 1 for eq in cls[:5]],
                "dag_level": int(longest_path[ci]),
            }
            for ci, cls in enumerate(classes)
        ],
    }
    with open("data/processed/quotient_dag.json", "w", encoding="utf-8") as f:
        json.dump(dag_data, f, indent=2, ensure_ascii=False)
    print(f"\nSaved quotient DAG data to data/processed/quotient_dag.json")


if __name__ == "__main__":
    main()

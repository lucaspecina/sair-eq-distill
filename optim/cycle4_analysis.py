"""
Cycle 4: Deep analysis of unresolved problems to find new features.

Strategy:
1. Analyze the 490 unresolved problems more deeply
2. Look at Eq2's structure (not just Eq1)
3. Find features that split TRUE/FALSE better
4. Look at variable overlap, depth ratios, symmetry patterns
5. Find new magma tables beyond 2x2 that catch more FALSEs
"""

import json
import sys
import os
from pathlib import Path
from itertools import product as iter_product
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from optim.analyze_and_generate import (
    parse_equation, get_vars, leftmost_var, rightmost_var,
    is_lone_var_absent, holds_in_magma, Var, Op, MAGMAS
)
from optim.compute_features import (
    extract_features, is_selfref_form, term_depth, term_size,
    count_var, all_var_counts, load_problems
)


def analyze_eq2_structure(problems):
    """Look at Eq2 features among unresolved problems."""
    unresolved = []

    for p in problems:
        eq1, eq2 = p['equation1'], p['equation2']
        answer = p['answer']

        if is_lone_var_absent(eq1):
            continue

        caught = False
        for a00 in range(2):
            for a01 in range(2):
                for a10 in range(2):
                    for a11 in range(2):
                        table = [[a00, a01], [a10, a11]]
                        try:
                            if holds_in_magma(eq1, table) and not holds_in_magma(eq2, table):
                                caught = True
                                break
                        except:
                            pass
                    if caught: break
                if caught: break
            if caught: break
        if caught:
            continue

        features = extract_features(eq1, eq2)
        unresolved.append({
            'id': p['id'],
            'eq1': eq1, 'eq2': eq2,
            'answer': answer,
            'difficulty': p.get('difficulty', 'normal'),
            'features': features,
        })

    return unresolved


def analyze_eq2_selfref(unresolved):
    """Check if Eq2 is also self-referential and how that interacts."""
    print("\n=== EQ2 SELF-REFERENCE ANALYSIS ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        eq2 = d['eq2']
        answer = d['answer']

        is_sr2, x2, t2, orient2 = is_selfref_form(eq2)

        is_sr1 = d['features']['eq1_is_selfref']

        key = f"eq1_sr={is_sr1}, eq2_sr={is_sr2}"
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def analyze_var_overlap(unresolved):
    """Look at variable set overlap between Eq1 and Eq2."""
    print("\n=== VARIABLE OVERLAP ANALYSIS ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        eq1, eq2 = d['eq1'], d['eq2']
        answer = d['answer']

        lhs1, rhs1 = parse_equation(eq1)
        lhs2, rhs2 = parse_equation(eq2)

        vars1 = get_vars(lhs1) | get_vars(rhs1)
        vars2 = get_vars(lhs2) | get_vars(rhs2)

        fresh_vars = vars2 - vars1
        n_fresh = len(fresh_vars)
        n_shared = len(vars1 & vars2)

        # Also check Eq2 structure
        eq2_lhs_var = isinstance(lhs2, Var)
        eq2_rhs_var = isinstance(rhs2, Var)
        eq2_compound = isinstance(lhs2, Op) and isinstance(rhs2, Op)

        key = f"fresh={n_fresh}"
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def analyze_eq2_form(unresolved):
    """Analyze the form of Eq2 (compound=compound vs var=term etc.)."""
    print("\n=== EQ2 FORM ANALYSIS ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        eq2 = d['eq2']
        answer = d['answer']

        lhs2, rhs2 = parse_equation(eq2)

        if isinstance(lhs2, Var) and isinstance(rhs2, Var):
            form = "var=var"
        elif isinstance(lhs2, Var) or isinstance(rhs2, Var):
            form = "var=compound"
        else:
            form = "compound=compound"

        if answer:
            categories[form]['true'] += 1
        else:
            categories[form]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def analyze_combined_eq1_eq2(unresolved):
    """Combine Eq1 self-ref features with Eq2 form."""
    print("\n=== COMBINED EQ1(selfref) x EQ2(form) ANALYSIS ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        eq1, eq2 = d['eq1'], d['eq2']
        answer = d['answer']
        f = d['features']

        lhs2, rhs2 = parse_equation(eq2)

        # Eq1 category
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                eq1_cat = "both_bound"
            elif f['eq1_no_boundary']:
                eq1_cat = "no_bound"
            else:
                eq1_cat = "one_bound"
        elif f['eq1_composite_both']:
            eq1_cat = "composite"
        else:
            eq1_cat = "other"

        # Eq2 category
        if isinstance(lhs2, Var) or isinstance(rhs2, Var):
            eq2_cat = "has_var"
        else:
            eq2_cat = "compound"

        n_other = f['eq1_n_other_vars']

        key = f"eq1={eq1_cat}(n={n_other}), eq2={eq2_cat}"
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def analyze_depth_and_size(unresolved):
    """Look at depth/size ratios between Eq1 and Eq2."""
    print("\n=== DEPTH/SIZE ANALYSIS ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        f = d['features']
        answer = d['answer']

        eq1_depth = f['eq1_depth']
        eq2_depth = f['eq2_depth']
        eq1_size = f['eq1_size']
        eq2_size = f['eq2_size']

        # Deeper/shallower Eq2
        if eq2_depth > eq1_depth:
            depth_cat = "eq2_deeper"
        elif eq2_depth < eq1_depth:
            depth_cat = "eq2_shallower"
        else:
            depth_cat = "eq2_same_depth"

        key = depth_cat
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def analyze_eq2_selfref_features(unresolved):
    """Deep analysis of Eq2 self-ref forms and their features."""
    print("\n=== EQ2 SELF-REF DETAILED ANALYSIS ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        eq2 = d['eq2']
        answer = d['answer']
        f = d['features']

        is_sr2, x2, t2, orient2 = is_selfref_form(eq2)

        if is_sr2:
            n_other2 = len(get_vars(t2) - {x2})
            x_occ2 = count_var(t2, x2)
            lm2 = leftmost_var(t2)
            rm2 = rightmost_var(t2)
            both_bound2 = lm2 == x2 and rm2 == x2

            if both_bound2:
                eq2_cat = f"sr_both(n={n_other2})"
            else:
                eq2_cat = f"sr_other(n={n_other2})"
        else:
            lhs2, rhs2 = parse_equation(eq2)
            if isinstance(lhs2, Var) and isinstance(rhs2, Var):
                eq2_cat = "var=var"
            elif isinstance(lhs2, Var) or isinstance(rhs2, Var):
                # Var absent case for Eq2
                if isinstance(lhs2, Var):
                    v2 = lhs2.name
                    t2_ast = rhs2
                else:
                    v2 = rhs2.name
                    t2_ast = lhs2
                if v2 not in get_vars(t2_ast):
                    eq2_cat = "lone_absent"
                else:
                    eq2_cat = "var_present_not_sr"  # shouldn't happen if is_selfref_form works
            else:
                eq2_cat = "compound=compound"

        key = eq2_cat
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def analyze_n_vars_combo(unresolved):
    """Look at n_vars in Eq1 vs Eq2."""
    print("\n=== N_VARS EQ1 vs EQ2 ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        f = d['features']
        answer = d['answer']

        n1 = f['eq1_n_vars']
        n2 = f['eq2_n_vars']

        key = f"eq1_vars={n1}, eq2_vars={n2}"
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        if total >= 5:  # Only show significant categories
            print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def find_3x3_magma_catches(problems):
    """Test some hand-picked 3-element magma tables for catching FALSE cases."""
    print("\n=== 3-ELEMENT MAGMA ANALYSIS ===")

    # Interesting 3-element magmas
    # Projection magmas
    magmas_3 = {
        'LZ3': [[0,0,0],[1,1,1],[2,2,2]],  # a*b = a on {0,1,2}
        'RZ3': [[0,1,2],[0,1,2],[0,1,2]],  # a*b = b on {0,1,2}
        'C0_3': [[0,0,0],[0,0,0],[0,0,0]], # constant 0
        'C1_3': [[1,1,1],[1,1,1],[1,1,1]], # constant 1
        'MIN': [[0,0,0],[0,1,1],[0,1,2]],  # min(a,b)
        'MAX': [[0,1,2],[1,1,2],[2,2,2]],  # max(a,b)
    }

    # Check how many unresolved FALSE problems each catches
    unresolved_false = []
    for p in problems:
        eq1, eq2 = p['equation1'], p['equation2']
        if p['answer'] or is_lone_var_absent(eq1):
            continue

        caught = False
        for a00 in range(2):
            for a01 in range(2):
                for a10 in range(2):
                    for a11 in range(2):
                        table = [[a00, a01], [a10, a11]]
                        try:
                            if holds_in_magma(eq1, table) and not holds_in_magma(eq2, table):
                                caught = True
                                break
                        except:
                            pass
                    if caught: break
                if caught: break
            if caught: break
        if not caught:
            unresolved_false.append(p)

    print(f"  Unresolved FALSE problems: {len(unresolved_false)}")

    for name, table in magmas_3.items():
        caught_count = 0
        for p in unresolved_false:
            eq1, eq2 = p['equation1'], p['equation2']
            try:
                if holds_in_magma(eq1, table) and not holds_in_magma(eq2, table):
                    caught_count += 1
            except:
                pass
        if caught_count > 0:
            print(f"  {name}: catches {caught_count} additional FALSEs")


def analyze_boundary_and_eq2_interplay(unresolved):
    """The key insight: combine eq1 boundary type with eq2 features."""
    print("\n=== EQ1 BOUNDARY x EQ2 FRESH VARS x N_OTHER ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0})

    for d in unresolved:
        f = d['features']
        answer = d['answer']

        if not f['eq1_is_selfref']:
            continue  # Skip non-selfref for now

        n_other = f['eq1_n_other_vars']
        x_occ = f['eq1_x_count']
        fresh = f['eq2_n_fresh_vars']

        if f['eq1_both_boundary']:
            bound = "both"
        elif f['eq1_no_boundary']:
            bound = "none"
        elif f['eq1_lm_only']:
            bound = "lm"
        else:
            bound = "rm"

        key = f"bound={bound}, n_other={n_other}, fresh={fresh}"
        if answer:
            categories[key]['true'] += 1
        else:
            categories[key]['false'] += 1

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        if total >= 3:  # Only show meaningful categories
            print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")


def propose_better_rules(unresolved):
    """Try many rule combinations to find best accuracy."""
    print("\n=== TESTING NEW RULE COMBINATIONS ===")

    def rule_tree_v1(d):
        """Current cheatsheet rules (approximation)."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            if n >= 3:
                return True
            if n == 2:
                if f['eq1_x_count'] >= 3:
                    return False
                return True
            return False  # n_other < 2
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v2(d):
        """Add Eq2 features."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            if n >= 3:
                return True
            if n == 2:
                if f['eq1_x_count'] >= 3:
                    return False
                return True
            if n == 1:
                # New: check Eq2 features
                if f['eq2_n_fresh_vars'] == 0 and f['eq2_has_lone_var']:
                    return True
                return False
            return False  # n_other = 0
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v3(d):
        """Incorporate depth and Eq2 self-ref."""
        f = d['features']
        eq2 = d['eq2']

        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            if n >= 3:
                return True
            if n == 2:
                if f['eq1_x_count'] >= 3:
                    return False
                return True
            if n == 1:
                # Check if Eq2 is also self-ref with similar strength
                is_sr2, x2, t2, orient2 = is_selfref_form(eq2)
                if is_sr2:
                    n_other2 = len(get_vars(t2) - {x2})
                    if n_other2 <= 1:
                        return True  # Weak Eq2 => easier to imply
                return False
            return False
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v4(d):
        """Default TRUE for n_other=1 selfref non-both."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            if n >= 3:
                return True
            if n == 2:
                if f['eq1_x_count'] >= 3:
                    return False
                return True
            if n == 1:
                return True  # Just default TRUE
            return False  # n_other = 0
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v5(d):
        """n_other=1 + boundary check."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            x_occ = f['eq1_x_count']
            if n >= 3:
                return True
            if n == 2:
                if x_occ >= 3:
                    return False
                return True
            if n == 1:
                if f['eq1_no_boundary']:
                    return True  # Strong position
                if x_occ <= 1:
                    return True
                return False
            return False  # n_other = 0
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v6(d):
        """Use eq1 term size as signal."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            x_occ = f['eq1_x_count']
            t_size = f['eq1_t_size']
            if n >= 3:
                return True
            if n == 2:
                if x_occ >= 3:
                    return False
                return True
            if n == 1:
                # Larger terms are more constraining
                if t_size >= 7:
                    return True
                return False
            return False
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v7(d):
        """Try: for all selfref non-both, default TRUE."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            return True
        if f['eq1_composite_both']:
            return False
        return False

    def rule_tree_v8(d):
        """n_other=1: use x_occ to decide."""
        f = d['features']
        if f['eq1_is_selfref']:
            if f['eq1_both_boundary']:
                return False
            n = f['eq1_n_other_vars']
            x_occ = f['eq1_x_count']
            if n >= 3:
                return True
            if n == 2:
                if x_occ >= 3:
                    return False
                return True
            if n == 1:
                if x_occ >= 2:
                    return False
                return True  # x_occ=1, n_other=1 means decent constraint
            return False  # n_other = 0
        if f['eq1_composite_both']:
            return False
        return False

    rules = [
        ("current_approx", rule_tree_v1),
        ("v2_eq2_features", rule_tree_v2),
        ("v3_eq2_selfref", rule_tree_v3),
        ("v4_n1_true", rule_tree_v4),
        ("v5_n1_boundary", rule_tree_v5),
        ("v6_term_size", rule_tree_v6),
        ("v7_all_nonboth_true", rule_tree_v7),
        ("v8_n1_xocc", rule_tree_v8),
    ]

    problems = load_problems()

    for name, rule_fn in rules:
        # Count with Rule 1 + 2x2 magmas + this rule for rest
        rule1_correct = 0
        magma_correct = 0
        rule_correct = 0
        rule_wrong = 0
        total = len(problems)

        for p in problems:
            eq1 = p['equation1']
            answer = p['answer']

            if is_lone_var_absent(eq1):
                rule1_correct += 1
                continue

            caught = False
            for a00 in range(2):
                for a01 in range(2):
                    for a10 in range(2):
                        for a11 in range(2):
                            table = [[a00, a01], [a10, a11]]
                            try:
                                if holds_in_magma(eq1, table) and not holds_in_magma(p['equation2'], table):
                                    caught = True
                                    break
                            except:
                                pass
                            if caught: break
                        if caught: break
                    if caught: break
                if caught: break
            if caught:
                magma_correct += 1
                continue

            # Use the rule
            d_item = None
            for u in unresolved:
                if u['id'] == p['id']:
                    d_item = u
                    break

            if d_item:
                pred = rule_fn(d_item)
                if pred == answer:
                    rule_correct += 1
                else:
                    rule_wrong += 1

        total_correct = rule1_correct + magma_correct + rule_correct
        acc = total_correct / total
        print(f"  {name:30s}: {total_correct}/{total} = {acc:.1%} (rule_correct={rule_correct}, rule_wrong={rule_wrong})")


def analyze_n1_selfref_detail(unresolved):
    """Deep dive into n_other=1 selfref problems, the biggest opportunity area."""
    print("\n=== N_OTHER=1 SELFREF DETAILED BREAKDOWN ===")

    categories = defaultdict(lambda: {'true': 0, 'false': 0, 'examples_t': [], 'examples_f': []})

    for d in unresolved:
        f = d['features']
        answer = d['answer']

        if not f['eq1_is_selfref'] or f['eq1_n_other_vars'] != 1:
            continue

        x_occ = f['eq1_x_count']
        bound = "both" if f['eq1_both_boundary'] else "none" if f['eq1_no_boundary'] else "lm" if f['eq1_lm_only'] else "rm"
        t_size = f['eq1_t_size']
        t_depth = f['eq1_t_depth']

        key = f"bound={bound}, x_occ={x_occ}, depth={t_depth}"
        if answer:
            categories[key]['true'] += 1
            if len(categories[key]['examples_t']) < 2:
                categories[key]['examples_t'].append((d['eq1'], d['eq2']))
        else:
            categories[key]['false'] += 1
            if len(categories[key]['examples_f']) < 2:
                categories[key]['examples_f'].append((d['eq1'], d['eq2']))

    for key, counts in sorted(categories.items()):
        total = counts['true'] + counts['false']
        true_pct = counts['true'] / total * 100 if total > 0 else 0
        print(f"  {key}: TRUE={counts['true']} FALSE={counts['false']} (TRUE%={true_pct:.0f}%, n={total})")
        for ex in counts['examples_t'][:1]:
            print(f"    TRUE example: {ex[0]} => {ex[1]}")
        for ex in counts['examples_f'][:1]:
            print(f"    FALSE example: {ex[0]} => {ex[1]}")


def main():
    print("Loading problems...")
    problems = load_problems()

    print(f"Total problems: {len(problems)}")

    unresolved = analyze_eq2_structure(problems)
    print(f"Unresolved: {len(unresolved)}")

    analyze_eq2_form(unresolved)
    analyze_eq2_selfref(unresolved)
    analyze_var_overlap(unresolved)
    analyze_eq2_selfref_features(unresolved)
    analyze_n_vars_combo(unresolved)
    analyze_depth_and_size(unresolved)
    analyze_boundary_and_eq2_interplay(unresolved)
    analyze_n1_selfref_detail(unresolved)

    print("\n" + "="*60)
    propose_better_rules(unresolved)

    # Find 3x3 magma catches
    find_3x3_magma_catches(problems)


if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)
    main()

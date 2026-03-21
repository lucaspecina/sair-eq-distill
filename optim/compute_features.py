"""
Compute structural features for ALL problems and find the best
data-derived decision rules for the unresolved cases.

Goal: find features that, when combined with Rule 1 + LZ/RZ/C0/XOR,
maximize accuracy on the 1200 training problems.
"""

import json
import sys
import os
from pathlib import Path
from itertools import product as iter_product
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from optim.analyze_and_generate import (
    parse_equation, get_vars, leftmost_var, rightmost_var,
    is_lone_var_absent, holds_in_magma, Var, Op, MAGMAS
)


def term_depth(ast):
    if isinstance(ast, Var):
        return 0
    return 1 + max(term_depth(ast.left), term_depth(ast.right))

def term_size(ast):
    if isinstance(ast, Var):
        return 1
    return 1 + term_size(ast.left) + term_size(ast.right)

def count_var(ast, name):
    if isinstance(ast, Var):
        return 1 if ast.name == name else 0
    return count_var(ast.left, name) + count_var(ast.right, name)

def all_var_counts(ast):
    """Count occurrences of each variable."""
    counts = Counter()
    if isinstance(ast, Var):
        counts[ast.name] = 1
    else:
        for k, v in all_var_counts(ast.left).items():
            counts[k] += v
        for k, v in all_var_counts(ast.right).items():
            counts[k] += v
    return counts


def is_selfref_form(eq_str):
    """Check if equation is x = T where x appears in T. Return (True, x, T, orientation) or (False, ...)."""
    lhs, rhs = parse_equation(eq_str)
    if isinstance(lhs, Var) and lhs.name in get_vars(rhs):
        return True, lhs.name, rhs, 'normal'
    if isinstance(rhs, Var) and rhs.name in get_vars(lhs):
        return True, rhs.name, lhs, 'flipped'
    return False, None, None, None


def extract_features(eq1_str, eq2_str):
    """Extract structural features from a problem."""
    lhs1, rhs1 = parse_equation(eq1_str)
    lhs2, rhs2 = parse_equation(eq2_str)

    vars1 = get_vars(lhs1) | get_vars(rhs1)
    vars2 = get_vars(lhs2) | get_vars(rhs2)

    features = {}

    # Eq1 form
    features['eq1_lhs_is_var'] = isinstance(lhs1, Var)
    features['eq1_rhs_is_var'] = isinstance(rhs1, Var)
    features['eq1_has_lone_var'] = isinstance(lhs1, Var) or isinstance(rhs1, Var)
    features['eq1_composite_both'] = isinstance(lhs1, Op) and isinstance(rhs1, Op)

    # Self-reference analysis
    is_sr, x_var, t_ast, orient = is_selfref_form(eq1_str)
    features['eq1_is_selfref'] = is_sr

    if is_sr:
        lm = leftmost_var(t_ast)
        rm = rightmost_var(t_ast)
        features['eq1_lm_is_x'] = lm == x_var
        features['eq1_rm_is_x'] = rm == x_var
        features['eq1_no_boundary'] = lm != x_var and rm != x_var
        features['eq1_both_boundary'] = lm == x_var and rm == x_var
        features['eq1_lm_only'] = lm == x_var and rm != x_var
        features['eq1_rm_only'] = rm == x_var and lm != x_var
        features['eq1_x_count'] = count_var(t_ast, x_var)
        features['eq1_t_depth'] = term_depth(t_ast)
        features['eq1_t_size'] = term_size(t_ast)
        features['eq1_n_other_vars'] = len(get_vars(t_ast) - {x_var})
    else:
        features['eq1_lm_is_x'] = False
        features['eq1_rm_is_x'] = False
        features['eq1_no_boundary'] = False
        features['eq1_both_boundary'] = False
        features['eq1_lm_only'] = False
        features['eq1_rm_only'] = False
        features['eq1_x_count'] = 0
        features['eq1_t_depth'] = 0
        features['eq1_t_size'] = 0
        features['eq1_n_other_vars'] = 0

    # Eq2 analysis
    features['eq2_has_lone_var'] = isinstance(lhs2, Var) or isinstance(rhs2, Var)
    features['eq2_composite_both'] = isinstance(lhs2, Op) and isinstance(rhs2, Op)
    features['eq2_n_fresh_vars'] = len(vars2 - vars1)
    features['eq2_depth'] = max(term_depth(lhs2), term_depth(rhs2))
    features['eq2_size'] = term_size(lhs2) + term_size(rhs2)
    features['eq2_n_vars'] = len(vars2)

    # Eq1 overall
    features['eq1_depth'] = max(term_depth(lhs1), term_depth(rhs1))
    features['eq1_size'] = term_size(lhs1) + term_size(rhs1)
    features['eq1_n_vars'] = len(vars1)

    # LZ/RZ analysis
    features['eq1_lz_holds'] = leftmost_var(lhs1) == leftmost_var(rhs1)
    features['eq1_rz_holds'] = rightmost_var(lhs1) == rightmost_var(rhs1)
    features['eq2_lz_holds'] = leftmost_var(lhs2) == leftmost_var(rhs2)
    features['eq2_rz_holds'] = rightmost_var(lhs2) == rightmost_var(rhs2)

    return features


def load_problems():
    problems = []
    for path in ['data/raw/normal.jsonl', 'data/raw/hard.jsonl']:
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    problems.append(json.loads(line))
    return problems


def find_best_rules():
    """Find the best decision rules for unresolved problems."""
    problems = load_problems()

    # Classify each problem
    data = []
    for p in problems:
        eq1, eq2 = p['equation1'], p['equation2']
        answer = p['answer']

        # Rule 1
        if is_lone_var_absent(eq1):
            continue  # Already handled

        # Check all 2x2 magmas
        caught_by_magma = False
        for a00 in range(2):
            for a01 in range(2):
                for a10 in range(2):
                    for a11 in range(2):
                        table = [[a00, a01], [a10, a11]]
                        try:
                            if holds_in_magma(eq1, table) and not holds_in_magma(eq2, table):
                                caught_by_magma = True
                                break
                        except:
                            pass
                    if caught_by_magma:
                        break
                if caught_by_magma:
                    break
            if caught_by_magma:
                break
        if caught_by_magma:
            continue  # Already handled

        features = extract_features(eq1, eq2)
        data.append({
            'id': p['id'],
            'difficulty': p.get('difficulty', 'normal'),
            'answer': answer,
            'features': features,
        })

    print(f"Unresolved problems (after Rule 1 + all 2x2 magmas): {len(data)}")
    true_count = sum(1 for d in data if d['answer'])
    false_count = sum(1 for d in data if not d['answer'])
    print(f"  TRUE: {true_count}, FALSE: {false_count}")

    # Try various decision rules
    print(f"\n=== TESTING DECISION RULES ===")

    rules = [
        # (name, prediction_function)
        ("default_TRUE", lambda f: True),
        ("default_FALSE", lambda f: False),
        ("selfref_strong_TRUE_else_FALSE", lambda f: f['eq1_no_boundary']),
        ("selfref_any_nonboth_TRUE_else_FALSE", lambda f: f['eq1_is_selfref'] and not f['eq1_both_boundary']),
        ("selfref_strong_or_lm_TRUE_else_FALSE", lambda f: f['eq1_no_boundary'] or f['eq1_lm_only']),
        ("selfref_nonboth_and_no_fresh_TRUE", lambda f: (f['eq1_is_selfref'] and not f['eq1_both_boundary'] and f['eq2_n_fresh_vars'] == 0)),
        ("selfref_nonboth_and_le1_fresh_TRUE", lambda f: (f['eq1_is_selfref'] and not f['eq1_both_boundary'] and f['eq2_n_fresh_vars'] <= 1)),
        ("selfref_strong_TRUE_moderate_check_fresh", lambda f: (
            f['eq1_no_boundary'] or
            (f['eq1_lm_only'] and f['eq2_n_fresh_vars'] <= 1) or
            (f['eq1_rm_only'] and f['eq2_n_fresh_vars'] == 0)
        )),
        ("selfref_strong_TRUE_rm_FALSE", lambda f: (
            f['eq1_no_boundary'] or f['eq1_lm_only']
        )),
        ("combined_v1", lambda f: (
            (f['eq1_no_boundary'] and f['eq2_n_fresh_vars'] <= 1) or
            (f['eq1_lm_only'] and f['eq2_n_fresh_vars'] == 0 and f['eq2_has_lone_var'])
        )),
        ("combined_v2", lambda f: (
            f['eq1_no_boundary'] or
            (f['eq1_lm_only'] and f['eq2_n_fresh_vars'] == 0)
        )),
        ("combined_v3_with_depth", lambda f: (
            (f['eq1_no_boundary'] and f['eq1_t_depth'] >= 2) or
            (f['eq1_lm_only'] and f['eq2_n_fresh_vars'] == 0 and f['eq1_t_depth'] >= 3)
        )),
        ("selfref_xcount_gt1", lambda f: (
            f['eq1_is_selfref'] and f['eq1_x_count'] >= 2 and not f['eq1_both_boundary']
        )),
        ("no_boundary_or_composite_eq2_lonevar", lambda f: (
            f['eq1_no_boundary'] or
            (f['eq1_is_selfref'] and not f['eq1_both_boundary'] and f['eq2_has_lone_var'] and f['eq2_n_fresh_vars'] == 0)
        )),
    ]

    best_name = None
    best_acc = 0

    for name, pred_fn in rules:
        correct = 0
        fn_count = 0
        fp_count = 0
        for d in data:
            predicted = pred_fn(d['features'])
            if predicted == d['answer']:
                correct += 1
            elif predicted and not d['answer']:
                fp_count += 1
            elif not predicted and d['answer']:
                fn_count += 1
        acc = correct / len(data) if data else 0
        print(f"  {name:45s}: {correct}/{len(data)} = {acc:.1%}  FP={fp_count} FN={fn_count}")
        if acc > best_acc:
            best_acc = acc
            best_name = name

    print(f"\nBest rule: {best_name} ({best_acc:.1%})")

    # Also compute overall accuracy including Rule 1 + magmas
    total_problems = len(problems)
    rule1_count = sum(1 for p in problems if is_lone_var_absent(p['equation1']))
    print(f"\n=== OVERALL PROJECTED ACCURACY ===")
    print(f"Total problems: {total_problems}")
    print(f"Rule 1 (TRUE): {rule1_count}")
    print(f"Magma (FALSE): {total_problems - rule1_count - len(data)}")
    print(f"Unresolved: {len(data)}")

    # With best rule
    for name, pred_fn in rules:
        resolved_correct = rule1_count + (total_problems - rule1_count - len(data))
        unresolved_correct = sum(1 for d in data if pred_fn(d['features']) == d['answer'])
        total_correct = resolved_correct + unresolved_correct
        total_acc = total_correct / total_problems
        if total_acc > 0.73:  # only print promising ones
            print(f"  {name:45s}: {total_correct}/{total_problems} = {total_acc:.1%}")


if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)
    find_best_rules()

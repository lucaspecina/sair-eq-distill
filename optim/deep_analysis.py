"""
Deep analysis of unresolved problems to find discriminating features.
Focus on self-referential equations where current rules disagree.
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
    is_lone_var_absent, holds_in_magma, eval_in_magma,
    Var, Op, MAGMAS
)


def load_problems():
    problems = []
    for path in ['data/raw/normal.jsonl', 'data/raw/hard.jsonl']:
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    problems.append(json.loads(line))
    return problems


def term_depth(ast):
    """Max nesting depth of an AST."""
    if isinstance(ast, Var):
        return 0
    return 1 + max(term_depth(ast.left), term_depth(ast.right))


def term_size(ast):
    """Number of nodes in AST."""
    if isinstance(ast, Var):
        return 1
    return 1 + term_size(ast.left) + term_size(ast.right)


def count_var_occurrences(ast, var_name):
    """Count how many times a variable appears."""
    if isinstance(ast, Var):
        return 1 if ast.name == var_name else 0
    return count_var_occurrences(ast.left, var_name) + count_var_occurrences(ast.right, var_name)


def var_positions(ast, var_name, path=""):
    """Get structural positions of a variable in the AST."""
    if isinstance(ast, Var):
        return [path] if ast.name == var_name else []
    left_pos = var_positions(ast.left, var_name, path + "L")
    right_pos = var_positions(ast.right, var_name, path + "R")
    return left_pos + right_pos


def ast_to_skeleton(ast):
    """Convert AST to a skeleton string (variables replaced by *)."""
    if isinstance(ast, Var):
        return "*"
    return f"({ast_to_skeleton(ast.left)}o{ast_to_skeleton(ast.right)})"


def is_selfref(eq_str):
    """Check if equation is x = T where x appears in T."""
    lhs, rhs = parse_equation(eq_str)
    if isinstance(lhs, Var) and lhs.name in get_vars(rhs):
        return True, lhs.name, rhs, 'normal'
    if isinstance(rhs, Var) and rhs.name in get_vars(lhs):
        return True, rhs.name, lhs, 'flipped'
    return False, None, None, None


def classify_unresolved():
    """Deep classify unresolved problems."""
    problems = load_problems()

    # Get unresolved (not caught by rule 1 or any standard magma)
    all_2x2_magmas = {}
    for a00 in range(2):
        for a01 in range(2):
            for a10 in range(2):
                for a11 in range(2):
                    table = [[a00, a01], [a10, a11]]
                    key = f"M{a00}{a01}{a10}{a11}"
                    all_2x2_magmas[key] = table

    unresolved = []
    for p in problems:
        eq1 = p['equation1']
        eq2 = p['equation2']

        if is_lone_var_absent(eq1):
            continue

        caught = False
        for mname, table in all_2x2_magmas.items():
            try:
                if holds_in_magma(eq1, table) and not holds_in_magma(eq2, table):
                    caught = True
                    break
            except:
                pass
        if caught:
            continue
        unresolved.append(p)

    print(f"Unresolved problems: {len(unresolved)}")
    true_unresolved = [p for p in unresolved if p['answer'] == True]
    false_unresolved = [p for p in unresolved if p['answer'] == False]
    print(f"  TRUE: {len(true_unresolved)}, FALSE: {len(false_unresolved)}")

    # Analyze self-referential patterns
    print(f"\n=== SELF-REF ANALYSIS ===")
    selfref_true = []
    selfref_false = []
    non_selfref = []

    for p in unresolved:
        is_sr, x_var, t_ast, orientation = is_selfref(p['equation1'])
        if is_sr:
            lm = leftmost_var(t_ast)
            rm = rightmost_var(t_ast)
            x_count = count_var_occurrences(t_ast, x_var)
            x_pos = var_positions(t_ast, x_var)
            n_vars = len(get_vars(t_ast))
            depth = term_depth(t_ast)
            size = term_size(t_ast)

            info = {
                'p': p,
                'x_var': x_var,
                'lm': lm, 'rm': rm,
                'lm_is_x': lm == x_var,
                'rm_is_x': rm == x_var,
                'x_count': x_count,
                'n_vars': n_vars,
                'depth': depth,
                'size': size,
                'x_positions': x_pos,
            }

            if p['answer']:
                selfref_true.append(info)
            else:
                selfref_false.append(info)
        else:
            non_selfref.append(p)

    print(f"Self-ref TRUE: {len(selfref_true)}")
    print(f"Self-ref FALSE: {len(selfref_false)}")
    print(f"Non self-ref: {len(non_selfref)}")

    # Find discriminating features between TRUE and FALSE self-ref
    print(f"\n=== DISCRIMINATING FEATURES (self-ref, non-boundary) ===")

    # Focus on no_boundary cases (where both LM and RM != x)
    nb_true = [s for s in selfref_true if not s['lm_is_x'] and not s['rm_is_x']]
    nb_false = [s for s in selfref_false if not s['lm_is_x'] and not s['rm_is_x']]
    print(f"No-boundary (LM!=x, RM!=x): TRUE={len(nb_true)}, FALSE={len(nb_false)}")

    # Check Eq2 features for these
    print(f"\n  -- Eq2 features when Eq1 is self-ref no-boundary --")
    for label, group in [('TRUE', nb_true), ('FALSE', nb_false)]:
        eq2_lone_var = 0
        eq2_composite = 0
        eq2_selfref = 0
        eq2_fresh_vars = []
        for info in group:
            p = info['p']
            lhs2, rhs2 = parse_equation(p['equation2'])
            vars1 = get_vars(parse_equation(p['equation1'])[0]) | get_vars(parse_equation(p['equation1'])[1])
            vars2 = get_vars(lhs2) | get_vars(rhs2)
            fresh = vars2 - vars1
            eq2_fresh_vars.append(len(fresh))

            if isinstance(lhs2, Var) or isinstance(rhs2, Var):
                eq2_lone_var += 1
                is_sr2, _, _, _ = is_selfref(p['equation2'])
                if is_sr2:
                    eq2_selfref += 1
            else:
                eq2_composite += 1

        print(f"  {label}: lone_var_in_eq2={eq2_lone_var}, composite_eq2={eq2_composite}, selfref_eq2={eq2_selfref}")
        if eq2_fresh_vars:
            print(f"    Fresh vars in eq2: avg={sum(eq2_fresh_vars)/len(eq2_fresh_vars):.1f}, 0={eq2_fresh_vars.count(0)}, 1={eq2_fresh_vars.count(1)}, 2+={sum(1 for x in eq2_fresh_vars if x>=2)}")

    # LM-only and RM-only analysis
    lm_true = [s for s in selfref_true if s['lm_is_x'] and not s['rm_is_x']]
    lm_false = [s for s in selfref_false if s['lm_is_x'] and not s['rm_is_x']]
    rm_true = [s for s in selfref_true if not s['lm_is_x'] and s['rm_is_x']]
    rm_false = [s for s in selfref_false if not s['lm_is_x'] and s['rm_is_x']]
    both_true = [s for s in selfref_true if s['lm_is_x'] and s['rm_is_x']]
    both_false = [s for s in selfref_false if s['lm_is_x'] and s['rm_is_x']]

    print(f"\n  LM-only (LM=x, RM!=x): TRUE={len(lm_true)}, FALSE={len(lm_false)}")
    print(f"  RM-only (RM=x, LM!=x): TRUE={len(rm_true)}, FALSE={len(rm_false)}")
    print(f"  Both (LM=x, RM=x): TRUE={len(both_true)}, FALSE={len(both_false)}")

    # Non self-ref analysis
    print(f"\n=== NON SELF-REF ANALYSIS ===")
    non_sr_true = [p for p in non_selfref if p['answer']]
    non_sr_false = [p for p in non_selfref if not p['answer']]
    print(f"Non self-ref: TRUE={len(non_sr_true)}, FALSE={len(non_sr_false)}")

    # Check if composite=composite in eq1
    comp_true = 0
    comp_false = 0
    for p in non_selfref:
        lhs1, rhs1 = parse_equation(p['equation1'])
        if isinstance(lhs1, Op) and isinstance(rhs1, Op):
            if p['answer']:
                comp_true += 1
            else:
                comp_false += 1
    print(f"  composite=composite in Eq1: TRUE={comp_true}, FALSE={comp_false}")
    if comp_true + comp_false > 0:
        print(f"    FALSE rate: {comp_false/(comp_true+comp_false):.1%}")

    # Summary: what's the best simple rule for unresolved?
    print(f"\n=== BASELINE STRATEGIES FOR UNRESOLVED ===")
    total_unresolved = len(unresolved)
    n_true = len(true_unresolved)
    n_false = len(false_unresolved)
    print(f"  Default TRUE: {n_true}/{total_unresolved} = {n_true/total_unresolved:.1%}")
    print(f"  Default FALSE: {n_false}/{total_unresolved} = {n_false/total_unresolved:.1%}")

    # Compute accuracy of "self-ref non-boundary -> TRUE, else FALSE"
    correct = 0
    for p in unresolved:
        is_sr, x_var, t_ast, _ = is_selfref(p['equation1'])
        if is_sr:
            lm = leftmost_var(t_ast)
            rm = rightmost_var(t_ast)
            if lm != x_var or rm != x_var:
                # Predict TRUE
                if p['answer'] == True:
                    correct += 1
            else:
                # Both boundary -> predict FALSE
                if p['answer'] == False:
                    correct += 1
        else:
            # Not self-ref -> predict FALSE
            if p['answer'] == False:
                correct += 1
    print(f"  'Self-ref non-boundary->TRUE, else FALSE': {correct}/{total_unresolved} = {correct/total_unresolved:.1%}")

    # More nuanced: self-ref non-boundary -> TRUE, composite=composite -> FALSE, else depend
    correct2 = 0
    for p in unresolved:
        is_sr, x_var, t_ast, _ = is_selfref(p['equation1'])
        if is_sr:
            lm = leftmost_var(t_ast)
            rm = rightmost_var(t_ast)
            if lm != x_var and rm != x_var:
                predicted = True
            elif lm == x_var and rm == x_var:
                predicted = False
            else:
                # One boundary only
                predicted = True  # still lean TRUE
        else:
            lhs1, rhs1 = parse_equation(p['equation1'])
            if isinstance(lhs1, Op) and isinstance(rhs1, Op):
                predicted = False
            else:
                predicted = True  # has a lone var side but var is in T -> lean TRUE
        if predicted == p['answer']:
            correct2 += 1
    print(f"  'Nuanced rule': {correct2}/{total_unresolved} = {correct2/total_unresolved:.1%}")

    # What if we also consider eq2's fresh variables?
    correct3 = 0
    for p in unresolved:
        is_sr, x_var, t_ast, _ = is_selfref(p['equation1'])
        vars1 = get_vars(parse_equation(p['equation1'])[0]) | get_vars(parse_equation(p['equation1'])[1])
        lhs2, rhs2 = parse_equation(p['equation2'])
        vars2 = get_vars(lhs2) | get_vars(rhs2)
        fresh = len(vars2 - vars1)

        if is_sr:
            lm = leftmost_var(t_ast)
            rm = rightmost_var(t_ast)
            if lm != x_var and rm != x_var:
                if fresh >= 2:
                    predicted = False  # too many fresh vars even for strong eq1
                else:
                    predicted = True
            elif lm == x_var and rm == x_var:
                predicted = False
            else:
                if fresh >= 2:
                    predicted = False
                else:
                    predicted = True
        else:
            lhs1, rhs1 = parse_equation(p['equation1'])
            if isinstance(lhs1, Op) and isinstance(rhs1, Op):
                predicted = False
            else:
                if fresh >= 2:
                    predicted = False
                else:
                    predicted = True
        if predicted == p['answer']:
            correct3 += 1
    print(f"  'Nuanced + fresh var check': {correct3}/{total_unresolved} = {correct3/total_unresolved:.1%}")

    # Print some FALSE examples that the nuanced rule gets wrong (predicted TRUE but actual FALSE)
    print(f"\n=== FALSE POSITIVES OF NUANCED RULE (predicted TRUE, actual FALSE) ===")
    fp_count = 0
    for p in unresolved:
        is_sr, x_var, t_ast, _ = is_selfref(p['equation1'])
        if is_sr:
            lm = leftmost_var(t_ast)
            rm = rightmost_var(t_ast)
            if (lm != x_var and rm != x_var) or (lm != x_var or rm != x_var):
                # Would predict TRUE
                if p['answer'] == False:
                    lhs2, rhs2 = parse_equation(p['equation2'])
                    vars1 = get_vars(parse_equation(p['equation1'])[0]) | get_vars(parse_equation(p['equation1'])[1])
                    vars2 = get_vars(lhs2) | get_vars(rhs2)
                    fresh = vars2 - vars1
                    print(f"  {p['id']} ({p.get('difficulty','?')}): {p['equation1']} => {p['equation2']}  fresh={fresh}")
                    fp_count += 1
                    if fp_count >= 20:
                        break


if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)
    classify_unresolved()

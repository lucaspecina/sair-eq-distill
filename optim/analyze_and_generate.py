"""
Error-pattern analysis + programmatic cheatsheet generator.

Approach:
1. Parse all 1200 equations into ASTs
2. Evaluate each equation in multiple finite magmas programmatically
3. Classify TRUE/FALSE using deterministic rules
4. Analyze what gaps remain (what the deterministic rules can't solve)
5. Generate a more compact cheatsheet with data-derived rules

This is NOT an LLM-based optimizer. It uses pure computation to find patterns.
"""

import json
import sys
import os
from pathlib import Path
from itertools import product as iter_product
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

# ---- AST Parsing ----

class Var:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name
    def __hash__(self):
        return hash(('Var', self.name))

class Op:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def __repr__(self):
        return f"({self.left} * {self.right})"
    def __eq__(self, other):
        return isinstance(other, Op) and self.left == other.left and self.right == other.right
    def __hash__(self):
        return hash(('Op', self.left, self.right))


def tokenize(s):
    """Tokenize an equation side."""
    tokens = []
    i = 0
    s = s.strip()
    while i < len(s):
        c = s[i]
        if c in '()*':
            tokens.append(c)
            i += 1
        elif c.isalpha():
            j = i
            while j < len(s) and s[j].isalpha():
                j += 1
            tokens.append(s[i:j])
            i = j
        elif c.isspace():
            i += 1
        else:
            i += 1
    return tokens


def parse_expr(tokens, pos):
    """Parse an expression, handling * as left-associative binary op."""
    left, pos = parse_atom(tokens, pos)
    while pos < len(tokens) and tokens[pos] == '*':
        pos += 1  # skip *
        right, pos = parse_atom(tokens, pos)
        left = Op(left, right)
    return left, pos


def parse_atom(tokens, pos):
    """Parse an atom: variable or parenthesized expression."""
    if pos >= len(tokens):
        raise ValueError(f"Unexpected end of tokens")
    if tokens[pos] == '(':
        pos += 1  # skip (
        expr, pos = parse_expr(tokens, pos)
        if pos < len(tokens) and tokens[pos] == ')':
            pos += 1
        return expr, pos
    else:
        return Var(tokens[pos]), pos + 1


def parse_equation(eq_str):
    """Parse 'LHS = RHS' into (lhs_ast, rhs_ast)."""
    parts = eq_str.split('=', 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid equation: {eq_str}")
    lhs_tokens = tokenize(parts[0])
    rhs_tokens = tokenize(parts[1])
    lhs, _ = parse_expr(lhs_tokens, 0)
    rhs, _ = parse_expr(rhs_tokens, 0)
    return lhs, rhs


# ---- AST Analysis ----

def get_vars(ast):
    """Get all variables in an AST."""
    if isinstance(ast, Var):
        return {ast.name}
    return get_vars(ast.left) | get_vars(ast.right)


def leftmost_var(ast):
    """Get the leftmost variable."""
    if isinstance(ast, Var):
        return ast.name
    return leftmost_var(ast.left)


def rightmost_var(ast):
    """Get the rightmost variable."""
    if isinstance(ast, Var):
        return ast.name
    return rightmost_var(ast.right)


def is_lone_var_absent(eq_str):
    """Check Rule 1: v = T where v not in T."""
    lhs, rhs = parse_equation(eq_str)
    # Check if LHS is a single variable not in RHS
    if isinstance(lhs, Var):
        if lhs.name not in get_vars(rhs):
            return True
    # Check if RHS is a single variable not in LHS
    if isinstance(rhs, Var):
        if rhs.name not in get_vars(lhs):
            return True
    return False


def eval_in_magma(ast, assignment, table):
    """Evaluate AST in a finite magma given by multiplication table.
    table[a][b] = a*b for elements 0..n-1."""
    if isinstance(ast, Var):
        return assignment[ast.name]
    left_val = eval_in_magma(ast.left, assignment, table)
    right_val = eval_in_magma(ast.right, assignment, table)
    return table[left_val][right_val]


def holds_in_magma(eq_str, table):
    """Check if equation holds for ALL assignments in magma."""
    lhs, rhs = parse_equation(eq_str)
    vars_list = sorted(get_vars(lhs) | get_vars(rhs))
    n = len(table)

    for vals in iter_product(range(n), repeat=len(vars_list)):
        assignment = dict(zip(vars_list, vals))
        try:
            lhs_val = eval_in_magma(lhs, assignment, table)
            rhs_val = eval_in_magma(rhs, assignment, table)
            if lhs_val != rhs_val:
                return False
        except (KeyError, IndexError):
            return False
    return True


# ---- Magma Definitions ----

# Left-zero: a*b = a
LZ = [[0, 0], [1, 1]]

# Right-zero: a*b = b
RZ = [[0, 1], [0, 1]]

# Constant-zero: a*b = 0
C0 = [[0, 0], [0, 0]]

# Constant-one: a*b = 1
C1 = [[1, 1], [1, 1]]

# XOR: a*b = (a+b) mod 2
XOR = [[0, 1], [1, 0]]

# AND: a*b = a AND b
AND = [[0, 0], [0, 1]]

# OR: a*b = a OR b
OR = [[0, 1], [1, 1]]

# Left-proj-right: a*b = a for first, then b
# "Average" magma: a*b = (a+b)//2
AVG = [[0, 0], [0, 1]]  # same as AND actually

# NAND: a*b = NOT(a AND b)
NAND = [[1, 1], [1, 0]]

# NOR: a*b = NOT(a OR b)
NOR = [[1, 0], [0, 0]]

# Projections with 3 elements
LZ3 = [[0,0,0],[1,1,1],[2,2,2]]
RZ3 = [[0,1,2],[0,1,2],[0,1,2]]

# Constant magmas with 3 elements
C0_3 = [[0,0,0],[0,0,0],[0,0,0]]

# Cyclic group Z3: a*b = (a+b) mod 3
Z3 = [[(a+b)%3 for b in range(3)] for a in range(3)]

# Min/Max magmas on {0,1}
MIN2 = [[0,0],[0,1]]  # = AND
MAX2 = [[0,1],[1,1]]  # = OR

# Unique magmas on {0,1}: a*b = 1-a (ignore b, flip a)
FLIP_L = [[1,1],[0,0]]  # a*b = 1-a
FLIP_R = [[1,0],[1,0]]  # a*b = 1-b

# Small interesting magma: a*b = a*a on {0,1} = a (since 0*0=0, 1*1=1)
# Actually let me try max(a,b)+1 mod 2
TWIST = [[1,1],[1,0]]

MAGMAS = {
    'LZ': LZ, 'RZ': RZ, 'C0': C0, 'C1': C1,
    'XOR': XOR, 'AND': AND, 'OR': OR,
    'NAND': NAND, 'NOR': NOR,
    'FLIP_L': FLIP_L, 'FLIP_R': FLIP_R,
    'TWIST': TWIST,
    'LZ3': LZ3, 'RZ3': RZ3, 'C0_3': C0_3, 'Z3': Z3,
}


def load_problems():
    """Load all problems."""
    problems = []
    for path in ['data/raw/normal.jsonl', 'data/raw/hard.jsonl']:
        with open(path, 'r') as f:
            for line in f:
                if line.strip():
                    problems.append(json.loads(line))
    return problems


def analyze_all():
    """Analyze all problems with all magmas."""
    problems = load_problems()
    print(f"Loaded {len(problems)} problems")

    # Classify using deterministic rules
    rule1_true = 0  # lone var absent
    magma_false = {}  # magma_name -> count of FALSE detected
    unresolved = []

    results = []

    for p in problems:
        eq1 = p['equation1']
        eq2 = p['equation2']
        answer = p['answer']
        pid = p['id']
        difficulty = p.get('difficulty', 'normal')

        # Rule 1: lone variable absent
        r1 = is_lone_var_absent(eq1)

        # Check counterexample magmas
        counterexamples_found = []
        for mname, table in MAGMAS.items():
            try:
                eq1_holds = holds_in_magma(eq1, table)
                eq2_holds = holds_in_magma(eq2, table)
                if eq1_holds and not eq2_holds:
                    counterexamples_found.append(mname)
            except Exception:
                pass

        # Determine prediction
        if r1:
            predicted = True
            rule_used = 'rule1_lone_var'
            rule1_true += 1
        elif counterexamples_found:
            predicted = False
            rule_used = f'counterexample:{",".join(counterexamples_found)}'
            for m in counterexamples_found:
                magma_false[m] = magma_false.get(m, 0) + 1
        else:
            predicted = None
            rule_used = 'unresolved'

        correct = predicted == answer if predicted is not None else None
        results.append({
            'id': pid,
            'difficulty': difficulty,
            'eq1': eq1, 'eq2': eq2,
            'answer': answer,
            'predicted': predicted,
            'correct': correct,
            'rule_used': rule_used,
            'counterexamples': counterexamples_found,
        })

    # Stats
    resolved = [r for r in results if r['predicted'] is not None]
    unresolved = [r for r in results if r['predicted'] is None]
    correct = [r for r in resolved if r['correct']]
    wrong = [r for r in resolved if not r['correct']]

    print(f"\n=== DETERMINISTIC RULE ANALYSIS ===")
    print(f"Total problems: {len(results)}")
    print(f"Resolved: {len(resolved)} ({len(resolved)/len(results):.1%})")
    print(f"Correct: {len(correct)} ({len(correct)/len(results):.1%} of total)")
    print(f"Wrong: {len(wrong)}")
    print(f"Unresolved: {len(unresolved)} ({len(unresolved)/len(results):.1%})")

    print(f"\nRule 1 (lone var absent -> TRUE): {rule1_true}")
    print(f"\nCounterexample magma catches:")
    for m, count in sorted(magma_false.items(), key=lambda x: -x[1]):
        print(f"  {m}: {count}")

    # Analyze unresolved problems
    unresolved_true = [r for r in unresolved if r['answer'] == True]
    unresolved_false = [r for r in unresolved if r['answer'] == False]
    print(f"\nUnresolved breakdown:")
    print(f"  TRUE: {len(unresolved_true)}")
    print(f"  FALSE: {len(unresolved_false)}")

    # Analyze unresolved by difficulty
    unresolved_normal = [r for r in unresolved if r['difficulty'] == 'normal']
    unresolved_hard = [r for r in unresolved if r['difficulty'] == 'hard']
    print(f"  Normal: {len(unresolved_normal)} ({len([r for r in unresolved_normal if r['answer']])} TRUE, {len([r for r in unresolved_normal if not r['answer']])} FALSE)")
    print(f"  Hard: {len(unresolved_hard)} ({len([r for r in unresolved_hard if r['answer']])} TRUE, {len([r for r in unresolved_hard if not r['answer']])} FALSE)")

    # Analyze wrong predictions
    if wrong:
        print(f"\nWRONG predictions ({len(wrong)}):")
        for w in wrong:
            print(f"  {w['id']}: predicted={w['predicted']}, actual={w['answer']}, rule={w['rule_used']}")

    # Analyze structural features of unresolved problems
    print(f"\n=== STRUCTURAL ANALYSIS OF UNRESOLVED ===")
    analyze_unresolved(unresolved)

    return results


def analyze_unresolved(unresolved):
    """Analyze structural features of unresolved problems."""
    features = Counter()

    for r in unresolved:
        eq1 = r['eq1']
        eq2 = r['eq2']
        answer = r['answer']
        label = 'TRUE' if answer else 'FALSE'

        lhs1, rhs1 = parse_equation(eq1)
        lhs2, rhs2 = parse_equation(eq2)

        # Feature: is Eq1 of form x = T(x,...)?
        if isinstance(lhs1, Var) and lhs1.name in get_vars(rhs1):
            features[f'{label}_eq1_selfref'] += 1
            # Sub-feature: boundary analysis
            lm = leftmost_var(rhs1)
            rm = rightmost_var(rhs1)
            x = lhs1.name
            if lm == x and rm == x:
                features[f'{label}_eq1_selfref_both_boundary'] += 1
            elif lm == x:
                features[f'{label}_eq1_selfref_lm_only'] += 1
            elif rm == x:
                features[f'{label}_eq1_selfref_rm_only'] += 1
            else:
                features[f'{label}_eq1_selfref_no_boundary'] += 1
        elif isinstance(rhs1, Var) and rhs1.name in get_vars(lhs1):
            features[f'{label}_eq1_selfref_flipped'] += 1
        elif isinstance(lhs1, Var) or isinstance(rhs1, Var):
            features[f'{label}_eq1_has_lone_var_in_T'] += 1
        else:
            features[f'{label}_eq1_composite_both'] += 1

        # Feature: does Eq2 have a lone variable side?
        if isinstance(lhs2, Var) or isinstance(rhs2, Var):
            features[f'{label}_eq2_has_lone_var'] += 1
        else:
            features[f'{label}_eq2_composite'] += 1

        # Feature: variable overlap
        vars1 = get_vars(lhs1) | get_vars(rhs1)
        vars2 = get_vars(lhs2) | get_vars(rhs2)
        fresh = vars2 - vars1
        if len(fresh) >= 2:
            features[f'{label}_eq2_2plus_fresh_vars'] += 1
        elif len(fresh) == 1:
            features[f'{label}_eq2_1_fresh_var'] += 1
        else:
            features[f'{label}_eq2_no_fresh_vars'] += 1

    for feat, count in sorted(features.items()):
        print(f"  {feat}: {count}")


def find_additional_magmas():
    """Try to find magmas that catch currently unresolved FALSE problems."""
    problems = load_problems()

    # First, identify unresolved FALSE problems
    unresolved_false = []
    for p in problems:
        if p['answer'] == False:
            eq1 = p['equation1']
            # Check if already caught by standard magmas
            caught = False
            for mname in ['LZ', 'RZ', 'C0', 'XOR']:
                table = MAGMAS[mname]
                try:
                    if holds_in_magma(eq1, table) and not holds_in_magma(p['equation2'], table):
                        caught = True
                        break
                except:
                    pass
            if not caught:
                unresolved_false.append(p)

    print(f"\nFALSE problems not caught by LZ/RZ/C0/XOR: {len(unresolved_false)}")

    # Try additional magmas on {0,1} - there are 16 possible 2x2 tables
    additional_catches = {}
    for a00 in range(2):
        for a01 in range(2):
            for a10 in range(2):
                for a11 in range(2):
                    table = [[a00, a01], [a10, a11]]
                    key = f"M({a00}{a01}{a10}{a11})"
                    catches = 0
                    false_positives = 0
                    for p in unresolved_false:
                        try:
                            eq1_holds = holds_in_magma(p['equation1'], table)
                            eq2_holds = holds_in_magma(p['equation2'], table)
                            if eq1_holds and not eq2_holds:
                                catches += 1
                        except:
                            pass
                    # Check for false positives on TRUE problems
                    for p in problems:
                        if p['answer'] == True:
                            try:
                                eq1_holds = holds_in_magma(p['equation1'], table)
                                eq2_holds = holds_in_magma(p['equation2'], table)
                                if eq1_holds and not eq2_holds:
                                    false_positives += 1
                            except:
                                pass
                    if catches > 0:
                        additional_catches[key] = {
                            'catches': catches,
                            'false_positives': false_positives,
                            'table': table,
                        }

    print(f"\nAdditional 2x2 magmas with catches (beyond LZ/RZ/C0/XOR):")
    for key, info in sorted(additional_catches.items(), key=lambda x: -x[1]['catches']):
        if info['catches'] > 0:
            print(f"  {key}: catches={info['catches']}, false_pos={info['false_positives']}, table={info['table']}")


def analyze_with_3elem_magmas():
    """Try 3-element magmas for additional coverage. Only test a subset of unresolved."""
    problems = load_problems()

    # Identify unresolved FALSE problems (not caught by any 2x2 magma)
    unresolved_false = []
    for p in problems:
        if p['answer'] == False:
            caught = False
            # Check ALL 16 2x2 magmas
            for a00 in range(2):
                for a01 in range(2):
                    for a10 in range(2):
                        for a11 in range(2):
                            table = [[a00, a01], [a10, a11]]
                            try:
                                if holds_in_magma(p['equation1'], table) and not holds_in_magma(p['equation2'], table):
                                    caught = True
                                    break
                            except:
                                pass
                    if caught:
                        break
                if caught:
                    break
            if not caught:
                unresolved_false.append(p)

    print(f"\nFALSE problems not caught by ANY 2x2 magma: {len(unresolved_false)}")

    # Print sample
    for p in unresolved_false[:10]:
        print(f"  {p['id']}: {p['equation1']} => {p['equation2']}")

    return unresolved_false


if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)

    print("=== Phase 1: Analyze all problems ===")
    results = analyze_all()

    print("\n\n=== Phase 2: Find additional magmas ===")
    find_additional_magmas()

    print("\n\n=== Phase 3: Analyze 3-element coverage ===")
    analyze_with_3elem_magmas()

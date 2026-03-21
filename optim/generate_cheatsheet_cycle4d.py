"""
Cycle 4d cheatsheet generator.

Final version combining best elements:
1. From v3: simplified self-ref rules (no fresh var complexity)
2. New: Add LZ/RZ verification emphasis (model keeps miscalculating)
3. New: More LM/RM worked examples for complex nested terms
4. Keep composite rules
5. Target ~7KB (sweet spot from prior experiments)
"""

import os
import sys
from pathlib import Path


def generate_cheatsheet():
    """Generate final cycle 4 cheatsheet."""

    cheatsheet = """Magma implication cheatsheet: does Eq1 => Eq2?
(every magma satisfying Eq1 also satisfies Eq2)

================================================================
***CRITICAL*** NODE 1 — CHECK THIS FIRST BEFORE ANYTHING ELSE
================================================================

Is Eq1 of form "v = T" (or "T = v") where v is a single variable
that does NOT appear ANYWHERE in T?
  => Answer TRUE immediately. ZERO exceptions. Do NOT check magmas.

How to check: If one side of Eq1 is a single variable (like x),
scan the OTHER side for that variable. If x does not appear there
at all, even once, the answer is TRUE. Stop immediately.

Examples of Node 1 matches (all TRUE):
  x = y*(z*w)           — x absent from RHS => TRUE
  x = y*((z*(z*w))*z)   — x absent from RHS => TRUE
  x = y*(y*(z*(z*y)))   — x absent from RHS => TRUE
  x = (y*z)*(y*(w*z))   — x absent from RHS => TRUE
  y*((z*(z*w))*z) = x   — x absent from LHS => TRUE (flipped)

WARNING: Do NOT skip Node 1! If v is absent from T, answer TRUE.
This rule has ZERO exceptions. Do NOT continue to Node 2.

================================================================
NODE 2 — COUNTEREXAMPLE MAGMAS (find FALSE)
================================================================

Test these magmas. If Eq1 HOLDS but Eq2 FAILS => Answer FALSE.
CRITICAL: First verify Eq1 holds. If Eq1 fails, skip that magma.

--- Left-Zero (LZ): a*b = a ---
  Every term = its leftmost variable (LM).
  LM(var)=var. LM(A*B)=LM(A). Always follow LEFT.
  Equation holds in LZ iff LM(left side) = LM(right side).

--- Right-Zero (RZ): a*b = b ---
  Every term = its rightmost variable (RM).
  RM(var)=var. RM(A*B)=RM(B). Always follow RIGHT.
  Equation holds in RZ iff RM(left side) = RM(right side).

--- Constant-Zero (C0): a*b = 0 on {0,1} ---
  Compound term (with *) = 0. Lone variable = itself.
  Holds iff both sides are same lone var, or both contain *.

--- XOR: a*b = (a+b) mod 2 on {0,1} ---
  Term value = sum of all variable occurrences mod 2.
  Holds iff each variable has same parity on both sides.

ONLY use LZ, RZ, C0, XOR. Do NOT invent other magmas.
If none gives counterexample, go to Node 3.

================================================================
HOW TO COMPUTE LM AND RM — STUDY THIS CAREFULLY
================================================================

LM: at each *, go LEFT. RM: at each *, go RIGHT.

LM(x) = x                    RM(x) = x
LM(A*B) = LM(A)              RM(A*B) = RM(B)

Step-by-step for deeply nested terms:
  (((x*y)*z)*x)*z: LM = LM((x*y)*z)*x) = LM((x*y)*z) = LM(x*y) = x
  (((x*y)*z)*x)*z: RM = RM(z) = z

  (y*(y*(y*y)))*x: LM = LM(y*(y*(y*y))) = LM(y) = y
  (y*(y*(y*y)))*x: RM = RM(x) = x

  ((y*x)*y)*(z*w): LM = LM((y*x)*y) = LM(y*x) = y
  ((y*x)*y)*(z*w): RM = RM(z*w) = w

  y*(z*(w*(y*z))): LM=y  RM=z
  (x*(y*x))*((y*y)*z): LM=x  RM=z

COMMON MISTAKE: LM(A*B) is NOT B, it is LM(A). Always go LEFT.
For RZ: RM(A*B) is NOT A, it is RM(B). Always go RIGHT.

LZ VERIFICATION PROCEDURE:
  1. Compute LM of Eq1's LHS and RHS. Are they equal?
     If yes: Eq1 holds in LZ. Continue to step 2.
     If no: Eq1 fails in LZ. Skip LZ entirely.
  2. Compute LM of Eq2's LHS and RHS. Are they equal?
     If no: Eq2 fails in LZ => LZ is a counterexample => FALSE.
     If yes: Eq2 also holds in LZ => LZ is not useful.

Same procedure for RZ using RM instead of LM.

================================================================
NODE 3 — CLASSIFY EQ1 AND APPLY RULES
================================================================

STEP 3A: Determine Eq1's form:
  (i)   "x = T" where x appears in T => SELF-REFERENTIAL. Go to 3B.
  (ii)  Both sides are compound terms (neither is a lone variable)
        => COMPOSITE. Go to 3C.
  (iii) Other forms => Answer FALSE.

STEP 3B: Self-referential analysis (x = T, x in T):
  Compute:
    LM(T) = leftmost var of T
    RM(T) = rightmost var of T
    n_other = distinct vars in T excluding x
    x_occ = times x appears in T

  Rules (apply in order, stop at first match):
  B1. LM(T)=x AND RM(T)=x => FALSE (both boundaries)
  B2. n_other >= 3 => TRUE
  B3. n_other = 2, x_occ >= 3 => FALSE
  B4. n_other = 2 => TRUE
  B5. n_other < 2 => FALSE (weak equation, answer immediately)

  Computing n_other and x_occ:
    x = y*((z*z)*(x*w)) => vars={y,z,w,x}, n_other=3, x_occ=1
    x = (y*x)*(x*(x*z)) => vars={y,x,z}, n_other=2, x_occ=3
    x = y*(x*(x*y))      => vars={y,x}, n_other=1, x_occ=2
    x = x*(x*(x*x))      => vars={x}, n_other=0, x_occ=4

STEP 3C: Composite equation analysis (both sides compound):
  Count eq1_vars = total distinct variables in Eq1.
  Count eq2_vars = total distinct variables in Eq2.
  C1. eq1_vars >= 5 => TRUE
  C2. eq1_vars >= 4 AND eq2_vars <= eq1_vars => TRUE
  C3. eq1_vars > eq2_vars + 1 => TRUE
  C4. Otherwise => FALSE

================================================================
WORKED EXAMPLES
================================================================

EXAMPLE 1: TRUE via Node 1 (lone variable absent)
  Eq1: x = y*(z*(w*(y*z)))   Eq2: x = ((x*(x*y))*y)*x
  x absent from RHS. Node 1 => TRUE.

EXAMPLE 2: FALSE via LZ counterexample
  Eq1: x = x*((y*z)*w)   Eq2: x = y*(z*(x*w))
  LZ: LM(x)=x, LM(x*((y*z)*w))=x. Same => Eq1 holds.
  LM(x)=x, LM(y*(z*(x*w)))=y. Different => Eq2 fails.
  LZ counterexample found => FALSE.

EXAMPLE 3: FALSE via RZ counterexample
  Eq1: x = (y*(y*(y*y)))*x   Eq2: x = (y*(z*x))*(z*w)
  RZ: RM(x)=x, RM((y*(y*(y*y)))*x)=RM(x)=x. Same => Eq1 holds.
  RM(x)=x, RM((y*(z*x))*(z*w))=RM(z*w)=w. Different => Eq2 fails.
  RZ counterexample found => FALSE.

EXAMPLE 4: TRUE via Node 3B (n_other=3)
  Eq1: x = y*((z*z)*(x*w))   Eq2: x*y = (z*(w*z))*y
  Node 1: x in T. Node 2: Eq1 fails LZ (LM=y!=x) and RZ.
  n_other=3 ({y,z,w}). Rule B2 => TRUE.

EXAMPLE 5: FALSE via Node 3B (n_other=1)
  Eq1: x = (y*(y*(x*y)))*y   Eq2: x*y = (y*x)*(z*z)
  No counterexample. n_other=1 ({y}). Rule B5 => FALSE.

EXAMPLE 6: Avoiding LZ computation error
  Eq1: x = (((x*y)*z)*x)*z   Eq2: x = ((y*(y*z))*z)*y
  LZ: LM(x)=x. LM(RHS): LM((((x*y)*z)*x)*z) = LM(((x*y)*z)*x)
  = LM((x*y)*z) = LM(x*y) = x. Eq1 holds (x=x).
  LM(((y*(y*z))*z)*y) = LM((y*(y*z))*z) = LM(y*(y*z)) = y.
  x != y => Eq2 fails. LZ counterexample => FALSE.

================================================================
QUICK REFERENCE
================================================================
v=T, v absent from T              => ALWAYS TRUE
counterexample magma found         => ALWAYS FALSE
self-ref, both boundary (LM=RM=x) => FALSE
self-ref, n_other >= 3             => TRUE
self-ref, n_other=2, x_occ >= 3   => FALSE
self-ref, n_other=2               => TRUE
self-ref, n_other < 2             => FALSE
composite, eq1_vars >= 5           => TRUE
composite, eq1_vars >= 4, eq2v<=eq1v => TRUE
composite, eq1v > eq2v + 1        => TRUE
composite (other)                  => FALSE
LM(A*B) = LM(A).  RM(A*B) = RM(B)."""

    return cheatsheet.strip()


def main():
    cheatsheet = generate_cheatsheet()

    size = len(cheatsheet.encode('utf-8'))
    print(f"Cheatsheet size: {size} bytes ({size/1024:.1f}KB)")
    assert size <= 10240, f"Too large: {size} bytes"

    output_path = Path("cheatsheets/current.txt")
    output_path.write_text(cheatsheet, encoding='utf-8')
    print(f"Written to {output_path}")

    backup_path = Path("cheatsheets/cycle4_v4.txt")
    backup_path.write_text(cheatsheet, encoding='utf-8')
    print(f"Backup saved to {backup_path}")


if __name__ == '__main__':
    os.chdir(Path(__file__).parent.parent)
    main()

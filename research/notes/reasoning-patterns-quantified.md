# Quantified Reasoning Pattern Analysis

Date: 2026-03-18

## gpt-5-nano on hard TRUE problems (default reasoning)

75 correct, 147 wrong out of 222 attempts.

### What correct answers do that wrong ones DON'T:

| Technique | In Correct | In Wrong | Ratio |
|-----------|-----------|----------|-------|
| Substitution | 40% | 10% | 4x |
| Left identity | 36% | 8% | 4.5x |
| Projection | 21% | 3% | 7x |
| Constant operation | 27% | 10% | 2.7x |

### What wrong answers do that correct ones DON'T:

| Technique | In Wrong | In Correct | Ratio |
|-----------|----------|-----------|-------|
| Operation table | 37% | 3% | 12x |
| "Trivial" claim | 39% | 7% | 5.5x |

### Interpretation:
- Wrong answers on TRUE problems try to build counterexamples (37% mention tables)
  when they should be trying substitution/identity detection
- Wrong answers overuse the word "trivial" — they make overconfident FALSE claims
- Correct answers successfully apply algebraic techniques: substitution (40%),
  left identity detection (36%), projection identification (21%)

### Implications for cheatsheet:
1. MUST teach substitution technique explicitly (most impactful)
2. MUST teach left identity detection (second most impactful)
3. SHOULD warn: "Before constructing a counterexample, try substitution first"
4. SHOULD warn: "Don't dismiss implications as 'trivially false' — try proving TRUE"
5. The cheatsheet should bias toward TRUE-seeking strategies since the default
   error is FALSE (models already lean FALSE naturally)

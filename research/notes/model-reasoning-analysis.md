# Model Reasoning Analysis

Date: 2026-03-18

## How models solve equational implication problems

Analyzed benchmark responses from 25 models on hard problems (200 problems).

### Successful reasoning patterns for FALSE implications:
1. **Free variable detection**: "Eq2 has extra variables z,w not constrained by Eq1"
2. **Counterexample by construction**: "Take the 2-element magma with table..."
3. **Independence argument**: "nothing in Eq1 forces the RHS of Eq2"

### Successful reasoning patterns for TRUE implications:
1. **Variable substitution**: "instantiate y:=x, z:=x in Eq1 to get Eq2"
2. **Constant operation detection**: "Eq1 forces the operation to be constant"
3. **Multi-step derivation**: use Eq1 multiple times with different instantiations
4. **Structure analysis**: "Eq1 forces every element to be a square"

### Common errors (answering FALSE when TRUE):
- Model can't find the derivation → defaults to FALSE
- Model claims counterexample exists but doesn't construct one
- Model gives vague reasoning without algebraic steps

### Key insight for cheatsheet:
The main failure mode is NOT recognizing TRUE implications. Models are
already decent at detecting FALSE (they guess FALSE by default and are right 63%).

The cheatsheet should focus on TEACHING THE MODEL HOW TO PROVE TRUE implications:
1. Show substitution technique explicitly with steps
2. Show how to detect "forces constant operation" patterns
3. Show multi-step derivation technique
4. Show how to detect "forces one element" (x=y equivalents)

### Benchmark analysis:
- gpt-5-mini gets 362/600 TRUE hard problems correct across 3 repeats
- But gets 82/600 WRONG (says FALSE when TRUE)
- The 82 wrong ones are cases where the derivation is non-obvious

### Performance by reasoning mode:
- "low_or_none" reasoning: models are much worse → they need to THINK
- "default" reasoning: significantly better → reasoning tokens help

This suggests our cheatsheet should GUIDE the reasoning process, not just
provide facts. The model needs a PROCEDURE to follow.

## Best vs Worst Model Comparison (hard problems, default reasoning)

Gemini 3.1 Pro: 90.2% accuracy (best)
Llama 3.1 8B: 46.7% accuracy (worst)

48 problems only the best model gets right.

### What the best model does:
- Constructs SPECIFIC counterexamples (e.g., "Steiner loops")
- Detects right projection reliably
- Shows concrete algebraic steps

### What the worst model does WRONG:
- **Assumes associativity** — magmas are NOT associative!
- Uses "Knuth-Bendix" as buzzword without execution
- Claims "equational reasoning" vaguely without steps
- Says TRUE with weak justification

### CRITICAL INSIGHT:
Small models often ASSUME ASSOCIATIVITY in magmas (because they're trained
on group/ring theory where associativity holds). This leads to wrong proofs.

**Possible cheatsheet improvement**: add warning "magmas are NOT associative
or commutative — do not assume (x*y)*z = x*(y*z) unless derived from Eq1."

But adding content to v6 hurts accuracy... Could REPLACE a less valuable
section with this warning? Would need ablation to determine.

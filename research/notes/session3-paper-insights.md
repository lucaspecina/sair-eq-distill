# Session 3: Paper & Competition Insights

Date: 2026-03-19

## Competition Intel

From Tao's blog comments:
- **93.3% normal / 79.9% hard** reported by "Kendon" using weak models
- "Static lists of laws" is a common but criticized approach
- The final test set uses DIFFERENT problems from the public 1200
- Full 22M dataset downloadable for testing (prevents overfitting to public set)
- Stage 2 needs Lean proofs or counterexamples + probability estimates
- Claude Opus 4.6 constructed a counterexample to the sample in ~3 min

## Relevant Papers & Approaches

### GEPA (ICLR 2026 Oral)
- **Reflective prompt evolution**: uses natural language reflection on why prompts fail
- **Pareto front**: maintains diverse non-dominated solutions, not just top-K by score
- **35x fewer rollouts** than RL baselines while outperforming them
- **Key insight for us**: instead of greedy best selection, maintain Pareto front of
  cheatsheets that are good at DIFFERENT things (e.g., one good at TRUE, one good at hard)

### EvoPrompt (ICLR 2024)
- Connects LLMs with evolutionary algorithms (GA and DE)
- Uses LLM itself as the mutation/crossover operator
- **Key insight for us**: crossover mutations — combine ideas from multiple parents

### C-Evolve (2025)
- Consensus-based evolution for prompt groups
- Evolves a GROUP of prompts that work together

### Imbue's Darwinian Evolver (2026)
- LLM-based evolution as universal optimizer
- Meta-evolution: the evolutionary strategy itself can evolve

## Ideas to Implement

1. **Crossover mutations**: some variants should combine ideas from 2 different parents
2. **Reflective analysis**: before generating variant, analyze error patterns in NL first
3. **Pareto front**: instead of top-K by score, keep diverse solutions
   - E.g., one cheatsheet best on TRUE, another best on FALSE
4. **Two-phase evolution**: first evolve on gpt-4.1-mini (fast), then fine-tune on nano/mini
5. **Meta-prompting**: let the evolver also evolve its own improvement strategy
6. **Use the full 22M dataset**: could we extract patterns programmatically?

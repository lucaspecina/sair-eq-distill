# TODO

## Estado actual (2026-03-21)
- Deadline: 20 abril 2026 (~30 días)
- current.txt: 7.9KB, **89% on gpt-5-nano** (200 problems, official eval)
- Leader (Kendon): 93.3% normal, 79.9% hard
- Gap: ~4 pts on normal
- SheetEvolve optimizer: WORKING, produced 89% in 2 generations

### Immediate
1. [ ] Run more SheetEvolve generations to push past 89%
2. [ ] Validate best cheatsheet on SAIR playground (10 credits/day)

### Medium-term
5. [ ] Validate best cheatsheet on SAIR playground (10 credits/day)
6. [ ] Extract patterns from full 22M dataset for harder cases
7. [ ] Investigate "free-form prompt template" option in competition
8. [ ] Test cheatsheet on gpt-5-mini — find version that doesn't hurt it
9. [ ] Study what Kendon's 93% approach might be doing differently

### Research lines (para workers)
- [ ] Explore duality rule: if A→B then dual(A)→dual(B)
- [ ] More 2-element magma counterexamples beyond LZ/RZ/C0/XOR
- [ ] Programmatic rule extraction from 22M dataset
- [ ] Radically different formats: decision tree, lookup table
- [ ] Mine Lean proofs from ETP for TRUE reasoning patterns
- [ ] Compress existing rules to make room for more content

## Done
- [x] Autoresearch infrastructure: coordinator.md, program.md, watch.sh, tried_approaches.log — 2026-03-20
- [x] Append-mode optimizer (evolve_append.py) — 2026-03-20
- [x] Definitive nano eval: 78% on 200 problems — 2026-03-20
- [x] C0/XOR counterexample battery added to cheatsheet — 2026-03-20
- [x] Investigate competition and resources — 2026-03-18
- [x] Bootstrap project structure — 2026-03-18
- [x] Download datasets — 2026-03-18
- [x] Implement multi-model evaluator — 2026-03-18
- [x] Baseline: 72% (gpt-5-mini, v0) — 2026-03-18
- [x] Dataset analysis: DAG (1415 nodes, height 15), features, equivalences — 2026-03-18
- [x] Multi-feature predictor: 85.4% on normal — 2026-03-18
- [x] Satisfaction scores for all 4694 equations — 2026-03-18
- [x] Model reasoning pattern analysis (25 models × benchmark) — 2026-03-18
- [x] 2-element magma analysis (16 tables) — 2026-03-18
- [x] 5 isomorphisms identified — 2026-03-18
- [x] Tree pattern analysis (dead end: shape doesn't predict) — 2026-03-18
- [x] Prototype OpenEvolve integration — 2026-03-18
- [x] v6 cheatsheet: 96.7% on normal (gpt-5-mini) — 2026-03-19 (later found inflated)
- [x] Fixed token budget: 16K tokens needed for reasoning models — 2026-03-19
- [x] Research synthesis session 1 — 2026-03-19
- [x] Robust evaluation infrastructure (eval_robust.py, analyze_errors.py) — 2026-03-19
- [x] Controlled A/B tests: v6 vs v12-v16, 5 variants — 2026-03-19
- [x] v15 (+"Be concise") = best: +5.3 pts over v6 — 2026-03-19
- [x] Error analysis: nano=token exhaustion, mini=hallucinated proofs — 2026-03-19
- [x] Identified 16 mathematical rules for cheatsheet encoding — 2026-03-19
- [x] Competition intel from Tao blog + benchmark analysis — 2026-03-19
- [x] Codex strategy reviews (3 sessions) — 2026-03-19
- [x] SheetEvolve optimizer built and validated — 2026-03-21
- [x] 89% on gpt-5-nano (200 probs) — best ever, +5.5 pts — 2026-03-21
- [x] Evolutionary optimizer designed (AlphaEvolve-inspired) — 2026-03-19
- [x] Research synthesis session 2 — 2026-03-19
- [x] Evolutionary optimizer v1 (evolve_cheatsheet.py) — 2026-03-19
- [x] Evolutionary optimizer v2 with crossover (evolve_v2.py) — 2026-03-20
- [x] gpt-4.1-mini deployed and validated as fast evaluator — 2026-03-20
- [x] claude-haiku-4-5 connected via AnthropicFoundry SDK — 2026-03-20
- [x] SAIR template confirmed (cheatsheet inline in user message) — 2026-03-20
- [x] Data analysis: 2 perfect rules (lone-var-absent, LZ/RZ) = 72.4% floor — 2026-03-20
- [x] Data analysis: C0 + XOR catch 178 more FALSEs = 78% floor — 2026-03-20
- [x] Full 1200-problem eval: 67% on gpt-4.1-mini, ~82% on nano — 2026-03-20
- [x] Transfer test: cheatsheet helps 4.1-mini/nano, hurts mini — 2026-03-20
- [x] Paper research: GEPA, EvoPrompt, competition intel — 2026-03-20
- [x] Research synthesis session 3 — 2026-03-20

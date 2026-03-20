# TODO

## PLAN DE ACCIÓN — Sesión 4

### Estado actual (2026-03-20)
- Deadline: 20 abril 2026 (~1 mes)
- current.txt: v2 gen3_x1, 6.7KB, evolved from empty seed
- Scores: 67% on gpt-4.1-mini (1200 probs), ~82% on nano (50 probs)
- Leader (Kendon): 93.3% normal, 79.9% hard
- Gap: ~11 pts on normal, ~26 pts on hard
- Deterministic rule floor: 72.4% (lone-var + LZ/RZ), extendable to ~78% (+ C0 + XOR)

### Immediate priorities
1. [ ] Run nano optimizer with C0/XOR knowledge — see if evolver can improve
2. [ ] Validate best cheatsheet on SAIR playground (10 credits/day)
3. [ ] Add constant-zero and XOR counterexample procedures to cheatsheet via evolution
4. [ ] Test cheatsheet on gpt-5-mini (reasoning, strong) — find version that doesn't hurt

### Medium-term
5. [ ] Extract patterns from full 22M dataset for harder cases
6. [ ] Implement partial mutation (modify sections, not full rewrite)
7. [ ] Try GEPA-style Pareto front for maintaining diverse cheatsheets
8. [ ] Investigate "free-form prompt template" option in competition
9. [ ] Test on nano with full 1200 problems (slow but definitive)

### Research lines
- [ ] Explore duality rule: if A→B then dual(A)→dual(B)
- [ ] Investigate more 2-element magma counterexamples (16 tables analyzed)
- [ ] Study what Kendon's 93% approach might be doing differently
- [ ] Look into programmatic rule extraction vs LLM evolution

## Done
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

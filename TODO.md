# TODO

## NEXT: Run evolutionary optimizer
- [ ] Deploy gpt-5.4 as evolver model (already in .env)
- [ ] Run `optim/evolve_cheatsheet.py` — 10 generations, v15 as seed
- [ ] Validate best result on SAIR playground (10 credits/day)

## Pending — High Priority
- [ ] Extract more mathematical patterns from 22M dataset for cheatsheet payload
- [ ] Explore diffusion-based optimization (future research line)
- [ ] Test on SAIR playground (the ONLY real validation)

## Pending — Research
- [ ] Analyze hard problems in detail — what specifically fails?
- [ ] Explore "duality" rule: if A→B then dual(A)→dual(B)
- [ ] Investigate Stone pairing fingerprints for equation clustering

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
- [x] v6 cheatsheet: 96.7% on normal (gpt-5-mini) — 2026-03-19
- [x] Fixed token budget: 16K tokens needed for reasoning models — 2026-03-19
- [x] v5 (comprehensive, 6.3KB): 73% — worse than v6 — 2026-03-19
- [x] v7 (intermediate laws): 86.7% — worse than v6 — 2026-03-19
- [x] Research synthesis complete — 2026-03-19

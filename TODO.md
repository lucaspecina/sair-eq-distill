# TODO

## In progress
- [ ] Test v6 on hard problems (API timeouts — need strategy)
- [ ] Investigate OpenEvolve for v6 optimization

## Pending — Highest Priority
- [ ] Run v6 on SAIR playground (10 credits/day — ultimate validation)
- [ ] Run ablation study on v6 (analysis/ablation_study.py, ~42 min)
- [ ] Test v6 with gpt-5-nano at 32K+ tokens
- [ ] Investigate why adding content to v6 HURTS accuracy (v7 was worse)
- [ ] Explore if v6 format works on other models (Claude Haiku, Llama, etc.)

## Pending — Research
- [ ] Implement modular cheatsheet (v6 sections as independently evolvable modules)
- [ ] Run OpenEvolve with cascade evaluation on v6
- [ ] Analyze hard problems in detail — what specifically fails?
- [ ] Explore "duality" rule: if A→B then dual(A)→dual(B)
- [ ] Investigate Stone pairing fingerprints for equation clustering
- [ ] Explore if pseudocode-style format improves model execution
- [ ] Search for more isomorphisms with other fields

## Pending — Infrastructure
- [ ] Fix background asyncio tasks on Windows (output buffering issue)
- [ ] Investigate API rate limits and cost tracking
- [ ] Set up gpt-5-nano evaluation with 32K tokens

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

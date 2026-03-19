# TODO

## In progress
- [ ] Evaluate cheatsheet v2 (procedural) — waiting for API results
- [ ] Investigate OpenEvolve for prompt evolution

## Pending

### Immediate (highest impact)
- [ ] Try few-shot examples in cheatsheet (worked examples of TRUE derivations)
- [ ] Try pseudocode-style cheatsheet (EMNLP 2024 approach)
- [ ] Drop Phi-4 from eval, focus on gpt-5-nano + gpt-5-mini
- [ ] Analyze benchmark model responses in detail — extract winning patterns
- [ ] Test cheatsheet on hard problems specifically

### Track 2: Evolutionary prompt optimization
- [ ] Install OpenEvolve, adapt for cheatsheet optimization
- [ ] Define modular cheatsheet structure (modules = genes)
- [ ] Set up fitness function (multi-model accuracy)
- [ ] Run evolutionary loop

### Track 5: Deeper data analysis
- [ ] What syntactic features predict DAG edges? (not just level)
- [ ] Analyze 3-element magmas as discriminators
- [ ] Compute Stone pairing with more/larger magmas for better resolution
- [ ] Investigate if equation "duality" (x↔y swap) affects implication patterns

### Track 4: Large model distillation
- [ ] Use GPT-5.4 to analyze errors and propose cheatsheet improvements
- [ ] Extract proof strategies from top benchmark models' responses

### Infrastructure
- [ ] Resolve evaluation speed — consider reducing max_completion_tokens for faster iters
- [ ] Investigate Zulip for competition updates and other approaches

## Done
- [x] Investigate the competition and available resources — 2026-03-18
- [x] Investigate autoresearch patterns (Karpathy et al.) — 2026-03-18
- [x] Bootstrap project (documents, structure, skills) — 2026-03-18
- [x] Download HuggingFace datasets (normal, hard, hard1, hard2) — 2026-03-18
- [x] Implement multi-model evaluator (gpt-5-nano, gpt-5-mini, Phi-4) — 2026-03-18
- [x] Run baseline: 50.7% avg accuracy — 2026-03-18
- [x] Research evolutionary frameworks (AlphaEvolve, OpenEvolve, ShinkaEvolve, EvoX) — 2026-03-18
- [x] Document 5 research tracks — 2026-03-18
- [x] Analyze equation structure (4694 eqs, features, complexity) — 2026-03-18
- [x] Analyze implication matrix (22M cells, 37% true, 100% transitive) — 2026-03-18
- [x] Build quotient DAG (1415 nodes, height 15, diamond shape) — 2026-03-18
- [x] Test substitution as predictor (87% precision normal, useless on hard) — 2026-03-18
- [x] Compute satisfaction scores for all equations — 2026-03-18
- [x] Build multi-feature predictor (85.4% on normal, 54.5% on hard) — 2026-03-18
- [x] Analyze benchmark model reasoning patterns — 2026-03-18
- [x] Analyze all 16 two-element magmas — 2026-03-18
- [x] Identify 5 isomorphisms with other fields — 2026-03-18
- [x] Write session 1 synthesis — 2026-03-18

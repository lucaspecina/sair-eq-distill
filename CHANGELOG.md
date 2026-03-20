# Changelog

## 2026-03-19 (session 3 — evolutionary optimizer running)
- **Evolutionary optimizer working end-to-end** with gpt-4.1-mini as evaluator, gpt-5.4 as evolver
- Key fix: same problem set within each generation for fair comparison (different between gens)
- 100 problems per eval (80 normal + 20 hard), concurrency 50
- **gen4_v0 = new current.txt** (5.7KB, avg ~71% on gpt-4.1-mini across 7 evals)
- Seed (empty) 50% → Best 70% in 10 generations
- gpt-4o-mini tested: says FALSE to everything with SAIR template, useless as evaluator
- gpt-4.1-mini deployed and validated: non-reasoning, fast (~2s/call), uses cheatsheet
- claude-haiku-4-5 connected via AnthropicFoundry SDK on Azure
- SAIR template confirmed: cheatsheet goes inline in user message (Jinja2 from competition page)
- Old cheatsheets (v5-v16) deleted, clean start

## 2026-03-19 (session 2 — robust eval, iteration & evolutionary optimizer)
- **CRITICAL: 96.7% was inflated** (fixed seed, normal only). Real: ~84% mini, ~57% nano
- Created eval/eval_robust.py — mixes normal+hard, random seeds, per-difficulty breakdown
- Created eval/analyze_errors.py — error classification and pattern analysis
- Controlled A/B test: v6 vs v12-v16, 5 variants on same seed=12345
- **v15 (+"Be concise") = best: +5.3 pts** over v6 (74.7% cross-model avg)
- Phi-4 destroyed by cheatsheets (53%→6%) — too weak, excluded
- nano primary error: empty responses (28/30 = token exhaustion)
- mini primary error: false positives on hard (91% fabricated substitution proofs)
- Identified 16 mathematical rules for encoding, 5 NOT in v6
- Competition intel: Tao says baseline 50%, best 55-60%, "cheap/open-source models"
- Vision: winning cheatsheet = [decoder] + [compressed math payload], NOT tutorial
- **Evolutionary optimizer** designed (AlphaEvolve-inspired):
  - nano = alumno (toma examen), gpt-5.4 = profesor (mejora cheatsheet)
  - Pool con diversidad, datos frescos cada eval, todo en paralelo
  - `optim/evolve_cheatsheet.py` implementado y listo para correr
- Codex reviews (3 sessions): strategy, error methodology, format families
- 8 new research notes + session-2 synthesis
- CLAUDE.md updated with competition-winning mandate and cheatsheet vision

## 2026-03-19 (overnight autoresearch session 1)
- **Cheatsheet v6: 96.7%** on 30 normal problems (gpt-5-mini) — best result (later found inflated)
- Tested 11 cheatsheet versions (v0-v11), v6 is locally optimal
- Key insight: concise focused (2.7KB) >> comprehensive (6.3KB)
- Raised max_completion_tokens to 16384 (reasoning models need space)
- Dropped Phi-4 from eval (not in SAIR benchmark, too weak)
- v6 on hard2: 60% (mini has TRUE bias on hard, opposite of normal)
- gpt-5-nano: 40-50% even with 32K tokens (too weak)
- Dataset analysis: DAG (1415 nodes, height 15), satisfaction scores, equivalence classes
- Multi-feature predictor: 85.4% ceiling on normal
- Quantified reasoning patterns from 25-model benchmark (substitution 4x more in correct)
- 14 research notes + 1 synthesis document
- Information theory: v6 near text-compression limit for normal problems
- Birkhoff completeness validates substitution as complete technique
- OpenEvolve prototype ready but needs API access for evolutionary runs
- Competition hard ≠ ETP hard (finite proofs exist, just non-obvious)
- Model biases: mini=TRUE bias on hard, nano=FALSE bias (opposite!)

## 2026-03-18
- Bootstrap del proyecto: estructura de directorios, documentos estándar, skills
- Investigación de la competencia SAIR: reglas, playground, datos disponibles
- Investigación de autoresearch: patrón Karpathy, RALPH, mejores prácticas
- Dataset analysis: 22M implications, 1415 equivalence classes, DAG height 15
- Multi-feature predictor: 85.4% on normal (ceiling for heuristics)
- Identified 5 isomorphisms with other fields
- Quantified reasoning patterns from 25-model benchmark
- Prototyped OpenEvolve integration for prompt evolution

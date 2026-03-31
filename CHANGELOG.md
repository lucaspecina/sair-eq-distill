# Changelog

## 2026-03-31 — Workflow alignment (I-004)
- Alineado repo completo con user-level skills (dev-workflow, project-bootstrap)
- PROJECT.md: agregado LA PREGUNTA, removido architecture section
- CLAUDE.md: reescrito a formato canónico (~130 líneas, trigger table, issue tracking)
- TODO.md: convertido a NOW/NEXT/BLOCKED/LATER con I-NNN refs
- CURRENT_STATE.md: actualizado a estado real (89% nano, SheetEvolve)
- AUTORESEARCH.md: creado config formal (OFF)
- issues/: creado sistema de tracking (I-001 a I-004)
- experiments/, research/archive/: directorios creados
- Skills actualizados (test, status, experiment) con trigger keywords y conda env
- Cleanup: eliminados 23 scripts obsoletos (generate_cheatsheet_*.py, old evolvers)
- coordinator.md y program.md movidos a research/archive/

## 2026-03-21 — SheetEvolve: 89% best ever (I-002)
- **SheetEvolve optimizer built** (`optim/sheetevolve.py`): evolutionary cheatsheet optimizer
  - gpt-5-nano evaluator (competition target), gpt-5.4 evolver
  - Fixed seed=42 problem sets, parent eval caching, diversity rejection
  - Cascaded evaluation: 50-problem quick filter → 200-problem full eval
- **89.0% on official eval** — best ever (+5.5 pts over 83.5% previous best)
  - TRUE accuracy: 98% (was 84%), FALSE accuracy: 82% (was 73%)
  - Key insight found by evolver: Node 3B rule
  - 2 generations, 1706 API calls, 36.5 min
- Playground models discovered: gpt-oss-120b, llama3.3-70b, gemini-flash-lite, grok-4.1-fast (I-003)

## 2026-03-20 — Autoresearch infrastructure (I-002)
- Autoresearch system built: coordinator + program + watch.sh + tried_approaches.log
- Append-mode optimizer (evolve_append.py): 88% peak but high variance
- Definitive nano eval: current.txt = 78% on 200 problems
- Cheatsheet upgraded with C0/XOR counterexample battery
- Key insight: gpt-5.4 evolver destroys TRUE accuracy when rewriting — append-only safer
- $158 spent overnight on evolutionary approaches with no sustained improvement

## 2026-03-19 — Robust eval + evolutionary optimizer (I-002)
- **CRITICAL: 96.7% was inflated** (fixed seed, normal only). Real: ~84% mini, ~57% nano
- Created eval_robust.py, analyze_errors.py
- v15 (+"Be concise") = best: +5.3 pts over v6
- Evolutionary optimizer v1+v2 designed and implemented
- Competition intel: Tao says baseline 50%, best 55-60%
- Vision: cheatsheet = decoder + compressed math payload

## 2026-03-18 — Bootstrap (I-001)
- Proyecto bootstrappeado: estructura, documentos, skills
- Investigación de competencia SAIR y datasets
- Dataset analysis: 22M implications, 1415 equiv classes, DAG height 15
- Multi-feature predictor: 85.4% ceiling
- Baseline: 72% con gpt-5-mini

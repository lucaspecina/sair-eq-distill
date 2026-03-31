---
id: 2
title: Optimización del cheat sheet para máxima accuracy
status: active
type: research
created: 2026-03-18
closed:
related: [I-001]
---

# I-002: Optimización del cheat sheet para máxima accuracy

## Status
- **Estado:** SheetEvolve produjo 89% en nano. Pausado esperando dirección.
- **Hipótesis actual:** Evolutionary optimization + datos del ETP pueden superar 90%
- **Último resultado:** 89% en 200 probs gpt-5-nano (best ever, +5.5 pts)
- **Último commit:** 4430013 (2026-03-21)
- **Próximo paso:** Más generaciones de SheetEvolve, validar en playground SAIR

## Pregunta
¿Cómo maximizar la accuracy del cheat sheet en la evaluación de SAIR?
Incluye: formato óptimo, contenido matemático, estrategias de optimización.

## Log

### 2026-03-18 · RESEARCH — Investigación inicial y baseline
- Competencia analizada: reglas, playground, modelos
- Dataset: 22M implications, 1415 equiv classes, DAG height 15
- Baseline: 72% con gpt-5-mini, cheatsheet v0
- Multi-feature predictor: 85.4% ceiling para heurísticas

### 2026-03-19 · EXP — Iteración manual de cheatsheets (v0-v16)
- 11 versiones probadas, v6 = localmente óptimo
- Key insight: conciso (2.7KB) >> comprehensivo (6.3KB)
- 96.7% reportado pero INFLADO (fixed seed, normal only)
- Real: ~84% mini, ~57% nano
- v15 (+"Be concise") = best: +5.3 pts sobre v6

### 2026-03-19 · DISEÑO — Optimizer evolutivo
- AlphaEvolve-inspired: nano=alumno, gpt-5.4=profesor
- evolve_cheatsheet.py v1 implementado
- Vision: cheatsheet = decoder + compressed math payload

### 2026-03-20 · EXP — Evolutionary optimizer v1 + v2
- $158 gastados overnight con approach evolutivo directo
- Resultado: NO funciona — evolver destruye TRUE accuracy consistentemente
- Key insight: append-only es más seguro que rewrite
- evolve_append.py: 88% peak pero alta varianza
- Autoresearch infrastructure creada (coordinator, program, watch)

### 2026-03-21 · EXP — SheetEvolve optimizer
- **SheetEvolve** built: cascaded eval (50→200 probs), diversity rejection,
  parent caching, fixed seed=42 comparison
- **89% en 200 probs** — best ever (+5.5 pts)
- TRUE accuracy: 98% (was 84%), FALSE: 82% (was 73%)
- Key insight del evolver: Node 3B — non-self-ref equations with no counterexample → TRUE
- 2 generaciones, 1706 API calls, 36.5 min

### 2026-03-21 · RESEARCH — Modelos del playground
- Descubrimiento CRÍTICO: playground usa modelos distintos
- gpt-oss-120b, llama3.3-70b, gemini-flash-lite, grok-4.1-fast
- NO son gpt-5-nano ni gpt-5-mini

## Conclusión
(pendiente — issue activo)

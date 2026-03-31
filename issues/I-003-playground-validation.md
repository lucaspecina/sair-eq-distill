---
id: 3
title: Validación en playground SAIR con modelos reales
status: open
type: task
created: 2026-03-21
closed:
related: [I-002]
blocked-by: []
---

# I-003: Validación en playground SAIR con modelos reales

## Status
- **Estado:** Abierto, no empezado
- **Hipótesis actual:** El cheatsheet de 89% local puede tener accuracy muy diferente en los modelos del playground
- **Último resultado:** Descubrimiento de que playground usa modelos distintos (gpt-oss-120b, llama3.3-70b, gemini-flash-lite, grok-4.1-fast)
- **Último commit:** —
- **Próximo paso:** Submitar cheatsheet actual al playground y medir accuracy real

## Pregunta
¿Cuánto accuracy real tiene nuestro cheatsheet en los modelos del playground SAIR?
¿Necesitamos optimizar para modelos distintos a gpt-5-nano?

## Log

### 2026-03-21 · RESEARCH — Descubrimiento de modelos
Los modelos del playground son DISTINTOS a los que evaluamos localmente.
Documentado en `research/notes/playground-models-discovery.md`.
10 créditos/día disponibles.

## Conclusión
(pendiente — issue abierto)

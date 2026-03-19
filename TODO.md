# TODO

## PLAN DE ACCIÓN — Sesión 3

### Contexto
- Deadline: 20 abril 2026 (~1 mes)
- Mejor cheatsheet: v15 (74.7% cross-model avg, +5.3 pts sobre v6)
- Benchmark público: 55-60%. Nuestro nano+v15: 65.6%. Estamos arriba pero sin validar en playground.
- El cheatsheet actual es un tutorial de comportamiento. El ganador será conocimiento matemático comprimido.

### Fase 1: Correr el evolutionary optimizer (~1-2 horas)
1. Verificar que gpt-5.4 funciona como evolver (test rápido)
2. Correr `optim/evolve_cheatsheet.py` con v15 como seed, 10 generaciones
   - nano = alumno (toma examen, 20 problemas por eval, max paralelismo)
   - gpt-5.4 = profesor (ve errores crudos del alumno, mejora cheatsheet)
   - Cada gen: evaluar parents → generar variantes → evaluar variantes → seleccionar
   - Todo en paralelo, seeds random frescos cada eval
3. Analizar resultados: ¿mejoró? ¿qué tipo de cheatsheet genera gpt-5.4?
4. Si mejoró: guardar best como nuevo current.txt

### Fase 2: Validar en playground SAIR (~10 min)
5. Subir el mejor cheatsheet al playground de SAIR
6. Usar 1-2 créditos (de 10/día) para validar score real
7. Comparar score playground vs score local → calibrar nuestro eval

### Fase 3: Iterar según resultados
- Si el optimizer evoluciona bien → correr más generaciones, explorar
- Si el optimizer se estanca → analizar por qué, ajustar el prompt del evolver
- Si el playground score es muy diferente al local → recalibrar evaluación
- Explorar si podemos extraer más patrones del dataset de 22M para el payload

### Fase 4: Líneas futuras (si hay tiempo)
- Diffusion-based optimization
- Extraer patterns del dataset completo de 22M implicaciones
- Modular cheatsheet (secciones independientemente evolucionables)

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

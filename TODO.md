# TODO

## In progress
- [ ] Sesión autoresearch overnight — investigar tracks del RESEARCH.md

## Pending

### Track 5: Análisis del dataset (fundacional)
- [ ] Analizar features sintácticas que predicen implicación (profundidad, variables, largo)
- [ ] Buscar clusters de ecuaciones equivalentes en la matriz
- [ ] Comparar problemas "hard" vs "normal" — ¿qué los hace difíciles?
- [ ] Extraer reglas algorítmicas de la data (sustitución, etc.)
- [ ] Analizar la estructura del grafo de implicaciones (SCCs, etc.)
- [ ] Investigar datos de Vampire prover del repo ETP

### Track 3: Cheat sheet modular
- [ ] Diseñar la estructura modular (~20 módulos de 500 bytes)
- [ ] Prototipar sistema de ablation (accuracy con vs sin cada módulo)
- [ ] Generar módulos iniciales basados en análisis del dataset

### Track 2: Prompt evolutivo con población
- [ ] Evaluar factibilidad de OpenEvolve / ShinkaEvolve / EvoX para nuestro caso
- [ ] Prototipar loop evolutivo mínimo en optim/
- [ ] Definir fitness function multi-modelo
- [ ] Definir operadores de mutación y crossover para módulos de texto

### Track 1: Mejorar baseline cheatsheet
- [ ] Incorporar hallazgos del análisis al cheatsheet
- [ ] Evaluar con eval/evaluate.py (baseline actual: 50.7%)
- [ ] Iterar mejoras con git ratchet

### Track 4: Destilación modelo grande → chico
- [ ] Experimentar con GPT-5.4 analizando errores del baseline
- [ ] Probar compresión guiada por modelo grande

### Infraestructura
- [ ] Resolver Claude Haiku en Azure Foundry (api_not_supported)
- [ ] Investigar Zulip de la competencia para más detalles
- [ ] Validar baseline en playground SAIR (10 créditos/día)

## Done
- [x] Investigar la competencia y recursos disponibles — 2026-03-18
- [x] Investigar buenas prácticas de autoresearch (Karpathy et al.) — 2026-03-18
- [x] Bootstrap del proyecto (documentos, estructura, skills) — 2026-03-18
- [x] Descargar datasets de HuggingFace (normal, hard, hard1, hard2) — 2026-03-18
- [x] Implementar evaluador multi-modelo (gpt-5-nano, gpt-5-mini, Phi-4) — 2026-03-18
- [x] Correr baseline: 50.7% avg accuracy — 2026-03-18
- [x] Investigar frameworks evolutivos (AlphaEvolve, OpenEvolve, ShinkaEvolve, EvoX) — 2026-03-18
- [x] Documentar 5 tracks de investigación en RESEARCH.md — 2026-03-18

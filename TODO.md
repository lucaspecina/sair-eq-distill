# TODO

## In progress
- [ ] Registrarse en competition.sair.foundation y explorar el playground
- [ ] Configurar evaluador local (elegir modelo chico, bajar datos)

## Pending

### Setup
- [ ] Bajar ecuaciones y datos del ETP (equations.txt, implicaciones, magmas)
- [ ] Bajar dataset completo de implicaciones (CSV de 22M pares)
- [ ] Identificar qué modelo chico usa la competencia (investigar Zulip)
- [ ] Configurar evaluación local con modelo chico (Llama 3 8B, Phi-3, o similar)
- [ ] Escribir `eval/evaluate.py` — evalúa cheatsheet contra subset de problemas
- [ ] Crear `program.md` para loop autoresearch

### Análisis del dataset
- [ ] Distribución de implicaciones true/false
- [ ] Clusters de leyes que se comportan igual
- [ ] Features sintácticas predictivas (largo, profundidad, variables)
- [ ] Análisis de qué patrones usan los provers automáticos

### Baseline
- [ ] Escribir primer cheat sheet manual basado en intuición matemática
- [ ] Evaluar baseline en evaluador local
- [ ] Validar baseline en playground SAIR (usar créditos con cuidado)

### Optimización
- [ ] Implementar loop autoresearch (patrón Karpathy)
- [ ] Probar prompt optimization (GEPA/DSPy/evolutivo)
- [ ] Estrategias híbridas (manual + automático)

## Done
- [x] Investigar la competencia y recursos disponibles — 2026-03-18
- [x] Investigar buenas prácticas de autoresearch (Karpathy et al.) — 2026-03-18
- [x] Bootstrap del proyecto (documentos, estructura, skills) — 2026-03-18

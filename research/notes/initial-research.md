# Research

## Index

- [Competencia SAIR](#competencia-sair) — Reglas, recursos, evaluación
- [Equational Theories Project (ETP)](#equational-theories-project-etp) — Datos disponibles, formato
- [Autoresearch](#autoresearch) — Patrón Karpathy, mejores prácticas para iteración autónoma
- [Estrategias de optimización](#estrategias-de-optimización) — GEPA, evolutivo, heurísticas

---

## Competencia SAIR

### Reglas
- **Cheat sheet máximo:** 10KB de texto
- **Stage 1 (deadline 2026-04-20):** Responder true/false. Accuracy binaria.
- **Stage 2 (top 1000):** Generar prueba formal o contraejemplo. Score por log-loss.
- **Test set final:** Privado. Subset de los 22M de implicaciones.

### Playground
- **URL:** https://playground.sair.foundation/playground/mathematics-distillation-challenge-equational-theories-stage1
- **Créditos:** 10 gratis por día
- **Problemas públicos:** 1200 (1000 fáciles + 200 difíciles)
- Los difíciles fueron seleccionados para "resistir estrategias obvias"

### Benchmarks
- **URL:** https://benchmark.sair.foundation/benchmarks/mathematics-distillation-challenge-equational-theories-stage1
- Sin cheat sheet: ~50% accuracy (random)
- Con cheat sheet decente: 55-60%

### Modelo de evaluación
- No se sabe exactamente cuál es. Descripto como "modelo chico/barato open-source"
- **Acción pendiente:** Investigar Zulip de la competencia para detalles

### Coordinación
- Canal de Zulip (registro abierto)
- **Acción pendiente:** Registrarse y explorar

### Open questions
- ¿Qué modelo chico exacto se usa?
- ¿Cómo se ponderan los problemas fáciles vs difíciles en el score final?
- ¿El cheat sheet se inyecta como system prompt o user prompt?
- ¿Hay rate limits adicionales en el playground?

---

## Equational Theories Project (ETP)

### Datos disponibles

| Archivo | Contenido | URL |
|---------|-----------|-----|
| `equations.txt` | 4694 leyes ecuacionales (hasta 4 ops) | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/equations.txt) |
| `eq_size5.txt` | Ecuaciones de tamaño 5 | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/eq_size5.txt) |
| `duals.json` | Ecuaciones duales | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/duals.json) |
| `smallest_magma.txt` | Magma más chico que satisface cada ecuación (hasta N=5) | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/smallest_magma.txt) |
| `small_magma_examples.txt` | Ejemplos de magmas | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/small_magma_examples.txt) |
| `2025-08-11-vampire.json.gz` | Resultados de Vampire prover (0=refuted, 1=proven, 2=unknown) | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/) |
| `Higman-Neumann.json` | 213 ecuaciones clasificadas (HN-equivalent, finite-equivalent, unknown) | [GitHub](https://github.com/teorth/equational_theories/blob/main/data/) |
| Implication graph (CSV) | 22M de pares con resultado true/false | [ETP site](https://teorth.github.io/equational_theories/implications/) |

### Formato de ecuaciones
Enumeradas secuencialmente. Formato: `x ◇ y = y ◇ x`. Variables: x, y, z, w. Operador: ◇ (binario).
Complejidad progresiva desde identidades simples (`x = x`) hasta expresiones con nesting profundo.

### Herramientas del ETP
- **Equation Explorer:** Exploración interactiva de implicaciones
- **Graphiti:** Visualización del grafo de implicaciones
- **Dashboard:** Estadísticas actualizadas

### Open questions
- ¿Cuántas implicaciones son true vs false? (distribución)
- ¿Hay estructura de clusters en el grafo?
- ¿Los resultados de Vampire correlacionan con la dificultad en la competencia?

---

## Autoresearch

### Patrón Karpathy (el estándar)

**Repo:** https://github.com/karpathy/autoresearch (41.6k stars)

**Concepto central:** Loop infinito donde el agente hace UN cambio atómico, mide con métrica fija, y decide keep/discard. Git como memoria persistente.

#### Arquitectura de 3 archivos
| Archivo | Quién lo toca | Rol |
|---|---|---|
| `prepare.py` | Nadie (inmutable) | Infraestructura: datos, evaluación |
| `train.py` | Solo el agente | Espacio de búsqueda |
| `program.md` | Solo el humano | Instrucciones en inglés — "el producto" |

#### El loop
```
LOOP FOREVER:
1. Leer estado (git log, results.tsv, código actual)
2. Proponer UN cambio atómico
3. git commit
4. Ejecutar experimento (budget fijo, ej: 5 min)
5. Parsear métrica
6. Si mejoró → keep. Si no → git reset HEAD~1
7. Loguear en results.tsv (commit, métrica, status, descripción)
8. NEVER STOP — el humano puede estar durmiendo
```

#### Resultados de referencia
- 700 experimentos en 2 días → 20 mejoras retenidas → 11% speedup
- Throughput: ~12 experimentos/hora, ~100 overnight
- Tobias Lutke (Shopify): 37 experimentos overnight → 19% gain

#### Mejores prácticas
1. **program.md ES el producto** — humanos escriben inglés, agentes escriben código
2. **Métrica única, archivo único, budget fijo** — sin ambigüedad
3. **Git como memoria** — ratchet pattern (keep improvements, reset failures)
4. **results.tsv como journal** — archivo untracked con TODOS los experimentos
5. **NEVER STOP** — crítico para runs overnight
6. **tmux** para persistencia ante desconexiones
7. **`--dangerously-skip-permissions`** para autonomía total
8. **Session reports** — el agente escribe resumen como GitHub Discussion

#### Formato de results.tsv
```
commit    val_bpb     memory_gb   status    description
a1b2c3d   0.997900    44.0        keep      baseline
b2c3d4e   0.993200    44.2        keep      increase LR to 0.04
c3d4e5f   1.005000    44.0        discard   switch to GeLU activation
```

### Adaptación a nuestro caso

| Karpathy | Nosotros |
|---|---|
| `train.py` (mutable) | `cheatsheets/current.txt` (mutable, ≤10KB) |
| `prepare.py` (inmutable) | `eval/evaluate.py` (inmutable — modelo + accuracy) |
| `program.md` (instrucciones) | `program.md` (instrucciones de investigación) |
| val_bpb (lower is better) | accuracy % (higher is better) |
| 5 min per experiment | Depende del evaluador local |

### Otros proyectos relevantes

- **RALPH** (github.com/frankbria/ralph-claude-code): Loop con circuit breaker (3 loops sin progreso → pausa), session management, `.ralphrc` config
- **uditgoenka/autoresearch**: Skill generalizada para Claude Code. 8 fases por ciclo. Guard feature (dual-gate safety).
- **ARIS** (Auto-Research-In-Sleep): Cross-model review (Claude ejecuta, GPT revisa). 4 workflows: discovery → experiment → review → writing.
- **Driveline autoresearch-claude-code**: Port como Claude Code skill con hooks. Mid-loop steering.

### Open questions
- ¿Cómo adaptar el timeout? Nuestro "experimento" es evaluar un cheatsheet, no entrenar un modelo.
- ¿Evaluación local vs playground? Local para iteración rápida, playground para validación.
- ¿Qué modelo chico usar para evaluación local que sea proxy del modelo de la competencia?

---

## Estrategias de optimización

### Track 1: Autoresearch (hill-climbing) — YA IMPLEMENTADO
El loop Karpathy: un cambio atómico al cheat sheet → evaluar → keep/discard.
- **Pro:** Simple, funciona overnight, ya listo
- **Contra:** Se puede quedar en óptimos locales, conservador
- **Status:** Implementado. Baseline 50.7% (3 modelos). Listo para correr.

### Track 2: Prompt evolutivo con población — LÍNEA PRIORITARIA

Inspirado en AlphaEvolve, OpenEvolve, ShinkaEvolve, EvoX. En vez de un solo
cheat sheet que mejora linealmente, mantener una **población** que evoluciona.

#### Frameworks de referencia

**AlphaEvolve** (Google DeepMind, 2025)
- Diff-based code evolution + MAP-Elites para quality-diversity
- LLM ensemble: Flash (throughput) + Pro (breakthroughs)
- Evaluation cascade: tests baratos primero, caros solo para survivors
- Resultados: mejoró Strassen (1969), recuperó 0.7% compute de Google
- Cerrado. Paper: https://arxiv.org/abs/2506.13131

**OpenEvolve** (community OSS)
- Reimplementación open-source de AlphaEvolve
- MAP-Elites + 5 islands con ring-topology migration
- Two-phase: exploration → plateau-breaking
- Multi-provider LLM (OpenAI, Gemini, local)
- Repo: https://github.com/algorithmicsuperintelligence/openevolve

**ShinkaEvolve** (Sakana AI, 2025)
- Foco en **sample efficiency** — SOTA con ~150 evaluaciones
- Novelty rejection-sampling (embeddings + LLM judge) para evitar duplicados
- UCB bandit para selección dinámica de LLM
- Meta-scratchpad: acumula conocimiento across generaciones
- Self-evolving prompts: las instrucciones de mutación también evolucionan
- Repo: https://github.com/SakanaAI/ShinkaEvolve

**EvoX** (UC Berkeley / SkyDiscover, 2026)
- **Meta-evolución**: co-evoluciona soluciones Y las estrategias de búsqueda
- La estrategia de búsqueda se adapta automáticamente (early: explorar, mid: variar, late: refinar)
- <$1 costo LLM vs $7-15 de competidores
- 196 tareas benchmark, 34% mejora mediana vs OpenEvolve/GEPA/ShinkaEvolve
- Paper: https://arxiv.org/abs/2602.23413
- Repo: https://github.com/skydiscover-ai/skydiscover

#### Aplicación a nuestro caso

El cheatsheet como "programa" a evolucionar:
- `EVOLVE-BLOCK` markers en el texto del cheat sheet
- Fitness function = accuracy promedio across modelos chicos
- Población de cheat sheets con diversidad (MAP-Elites)
- LLM grande genera mutaciones, modelos chicos evalúan

#### Qué framework usar?
- **OpenEvolve**: el más maduro OSS, fácil de adaptar
- **ShinkaEvolve**: si queremos sample efficiency (importante — cada eval cuesta API calls)
- **EvoX/SkyDiscover**: el más avanzado (meta-evolución) pero más complejo

### Track 3: Cheat sheet modular — COMPLEMENTARIO

Descomponer el cheat sheet en **módulos independientes** (~500 bytes cada uno):
```
[Módulo: reglas triviales] [Módulo: sustitución] [Módulo: contraejemplos]
[Módulo: patrones comunes] [Módulo: heurísticas default] [Módulo: ...]
```
- 10KB = ~20 módulos de 500 bytes
- Cada módulo se evalúa por **ablation**: accuracy CON vs SIN el módulo
- Los módulos que no aportan se eliminan, se reemplazan por otros
- Compatible con Track 2: los módulos son los "genes" del evolutivo
- Crossover = combinar módulos de diferentes cheat sheets
- Mutación = reescribir un módulo manteniendo los demás

### Track 4: Destilación con modelo grande → chico

1. Darle a un modelo grande (GPT-5.4) el dataset + problemas que fallan
2. Que identifique patrones compresibles y útiles
3. Comprimir en el cheat sheet
4. Evaluar con modelos chicos
5. Feedback loop: errores → grande refina → comprimir

Variante RL-like: el reward es la accuracy post-compresión.

### Track 5: Análisis del dataset + data-driven rules

Antes de optimizar, entender la estructura:
- Distribución true/false (37% true, 63% false en la matriz completa)
- Features sintácticas que predicen implicación (profundidad, variables, largo)
- Clusters de ecuaciones equivalentes
- Patrones de los provers automáticos (datos de Vampire en el repo ETP)
- Reglas algorítmicas extraídas directamente de la data

Las reglas data-driven podrían ser los "módulos" iniciales del Track 3.

### Approach recomendado: Pipeline

```
Track 5 (análisis) → Track 3 (módulos iniciales) → Track 2 (evolución)
     ↓                                                     ↓
Track 1 (autoresearch overnight como baseline)    Track 4 (destilación puntual)
```

1. **Ahora:** Correr Track 1 overnight para tener un baseline fuerte
2. **Próximo:** Track 5 — analizar la data, extraer reglas
3. **Después:** Track 3 + 2 — modularizar el cheatsheet, evolucionar con framework

### References
- GEPA: ICLR 2026 oral, 35x menos rollouts que GRPO — https://arxiv.org/abs/2507.19457
- EvoPrompt: ICLR 2024 — https://arxiv.org/abs/2309.08532
- PromptBreeder: self-referential self-improvement — https://arxiv.org/abs/2309.16797
- MCTS-OPS: MCTS para prompt sequences — https://arxiv.org/abs/2508.05995
- AlphaEvolve: https://arxiv.org/abs/2506.13131
- OpenEvolve: https://github.com/algorithmicsuperintelligence/openevolve
- ShinkaEvolve: https://github.com/SakanaAI/ShinkaEvolve
- EvoX: https://arxiv.org/abs/2602.23413
- SkyDiscover (EvoX impl): https://github.com/skydiscover-ai/skydiscover
- Cursor self-summarization: https://cursor.com/blog/self-summarization
- ETP paper: https://arxiv.org/abs/2512.07087
- Karpathy autoresearch: https://github.com/karpathy/autoresearch
- Competencia: https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage1/overview
- Blog de Tao: https://terrytao.wordpress.com/2026/03/13/mathematics-distillation-challenge-equational-theories/

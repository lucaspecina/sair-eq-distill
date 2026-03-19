# eq-distill — Claude Code Configuration

## START HERE — Read these docs first
1. **PROJECT.md** — Visión y propósito (north star)
2. **CURRENT_STATE.md** — Qué funciona hoy
3. **TODO.md** — Tareas pendientes y completadas
4. **CHANGELOG.md** — Historial de cambios
5. **research/README.md** — Índice de investigación, hallazgos, estrategias

## PRIME DIRECTIVE — GANAR ESTA COMPETENCIA

**TODO lo que hacemos debe responder a UNA pregunta: ¿esto nos acerca a ganar?**

- Entender EXACTAMENTE cómo evalúa SAIR (modelos, mix normal/hard, scoring)
- Cada decisión técnica se justifica contra el método de evaluación
- No optimizar para nuestro eval local — optimizar para el playground SAIR
- Si un approach no impacta el score de competencia, NO importa
- El cheatsheet debe funcionar en MÚLTIPLES modelos, no solo gpt-5-mini
- Explorar formatos crípticos/comprimidos que empaqueten más info en ≤10KB
- Usar evolutionary search para encontrar formulaciones que humanos no pensarían
- **Vision del cheatsheet ganador**: [header explicativo corto] + [reglas comprimidas
  con patrones matemáticos reales]. No prosa tutorial — información densa. Cada byte
  debe contener conocimiento matemático, no instrucciones de comportamiento.

## Project overview

Competencia Mathematics Distillation Challenge (SAIR Foundation, Terence Tao).
Destilar 22M de implicaciones de álgebra universal en un cheat sheet ≤10KB que
maximice la accuracy de un modelo chico prediciendo "¿ley A implica ley B?".

## Cómo trabajamos — autoresearch

**Autoresearch es nuestro workflow, NO un approach para resolver el problema.**
Es la metodología de trabajo: Claude Code corre autónomamente (overnight o en
sesiones largas), investigando, prototipando, y experimentando. El humano
revisa resultados, da dirección, y relanza.

- `watch.sh` relanza Claude si se cae
- `TODO.md` define qué hay que hacer (Claude lee esto al arrancar)
- Los hallazgos se documentan en `research/`
- El progreso se trackea en `TODO.md` y `CHANGELOG.md`

### El workflow concreto

Es UNA sesión continua. El watcher solo interviene si crasheo.

**Loop de trabajo:**
1. Leo TODO.md, elijo la tarea de mayor prioridad
2. Investigo / prototipo / experimento
3. Cuando tengo un hallazgo (positivo o negativo), lo documento en `research/notes/`
4. Si el hallazgo toca el cheatsheet, lo aplico y mido accuracy
5. Actualizo TODO.md (completar, agregar nuevas tareas que surjan)
6. Commit con mensaje descriptivo
7. Siguiente tarea

**Cuándo pivotar de una línea de investigación:**
- Si estoy girando en círculos sin producir hallazgos documentables → pivotar
- Si estoy en algo prometedor pero necesito más tiempo → SEGUIR, no abandonar
  por un timer arbitrario
- Si llegué a una conclusión clara (funciona o no funciona) → documentar y pivotar
- Ante la duda: documentar el estado actual, pivotar, se puede volver después

**Tracking de experimentos:**
- `results.tsv` — runs cuantitativos del evaluador (accuracy numérica)
- `research/notes/` — hallazgos, dead ends, ideas, exploraciones
- `research/synthesis/` — conclusiones consolidadas con evidencia
- `TODO.md` — qué se hizo, qué falta

**Manejo del contexto:**
- Documentar hallazgos a archivos INMEDIATAMENTE, no dejarlos solo en memoria
- Commitear frecuentemente — cada hallazgo significativo = commit
- Cada tanto, compactar: releer lo acumulado, limpiar notas redundantes
- El output principal de autoresearch es CONOCIMIENTO documentado en archivos

## Mindset de investigación — SER CREATIVO

No estamos haciendo ingeniería incremental. Estamos INVESTIGANDO. Eso significa:

- **Buscar isomorfismos.** ¿Qué otros problemas se parecen a este? ¿Cómo los
  resuelven? Compresión de información, knowledge distillation, prompt optimization,
  evolutionary search, information theory, graph compression... ¿qué ideas de
  otros campos aplican acá?
- **No tener miedo de probar cosas locas.** Si una idea suena interesante,
  prototipala. Es más barato experimentar que debatir.
- **Profundizar, no surfear.** Mejor investigar UN approach a fondo que 5
  superficialmente. Pero si algo no va, pivotar sin culpa.
- **Usar Codex (MCP) como sparring partner.** Debatir ideas, pedir code review,
  desafiar conclusiones.
- **Documentar TODO.** Cada hallazgo, cada dead end, cada insight va a
  `research/`. El output principal de autoresearch es CONOCIMIENTO documentado.

## Environment setup

```bash
# Conda environment
conda activate eq-distill

# Si no existe, crearlo:
conda create -n eq-distill python=3.11 -y
conda activate eq-distill
pip install openai python-dotenv pandas httpx pytest ruff huggingface_hub
```

**IMPORTANTE:** Siempre usar `conda run -n eq-distill python ...` o activar
el env antes de correr scripts. El watch.sh debe correr dentro del env.

## Tech stack
- **Python 3.11+** — lenguaje principal
- **conda** — environment manager (env: `eq-distill`)
- **openai** — SDK para Azure Foundry API
- **pandas** — análisis de datos del ETP
- **httpx** — llamadas HTTP
- **pytest** — tests
- **ruff** — linting y formatting
- **huggingface_hub** — descarga de datasets

## Project structure

```
eq-distill/
├── PROJECT.md              # Visión y propósito
├── CLAUDE.md               # Este archivo
├── TODO.md                 # Task tracking
├── CURRENT_STATE.md        # Estado actual del sistema
├── CHANGELOG.md            # Historial
├── watch.sh                # Watcher que relanza Claude overnight
├── results.tsv             # Journal de experimentos (untracked)
├── data/
│   ├── raw/                # Datos crudos del ETP
│   └── processed/          # Datos procesados para evaluación
├── analysis/               # Scripts/notebooks de exploración
├── cheatsheets/            # Versiones del cheat sheet
│   └── current.txt         # Cheat sheet activo (≤10KB)
├── eval/
│   ├── evaluate.py         # Evaluador local (INMUTABLE en modo autoresearch)
│   └── playground.py       # Interfaz con playground SAIR
├── optim/                  # Estrategias de optimización
│   ├── evolutionary.py     # Approach evolutivo
│   └── analysis_based.py   # Heurísticas desde análisis
├── research/
│   ├── README.md           # Índice de investigación
│   ├── notes/              # Exploraciones, análisis, ideas
│   └── synthesis/          # Conclusiones consolidadas
└── .claude/skills/         # Skills de Claude Code
```

## Code conventions

- Comunicación: **Español**
- Docstrings y comentarios en código: inglés
- Type hints en funciones públicas
- Archivos ≤300 líneas; si crece, dividir
- Cheat sheet: siempre verificar ≤10KB antes de commit

## Commands

```bash
# Tests
pytest

# Lint
ruff check .
ruff format .

# Evaluar un cheat sheet (multi-modelo: gpt-5-nano, gpt-5-mini, Phi-4)
python eval/evaluate.py --cheatsheet cheatsheets/current.txt

# Validar tamaño del cheat sheet
python -c "import os; s=os.path.getsize('cheatsheets/current.txt'); print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240"
```

## Quality assurance

- **Level 1 (pre-commit):** pytest + ruff + cheat sheet ≤10KB
- **Level 2 (periódico):** Evaluación local contra subset de problemas
- **Level 3 (validación externa):** Playground SAIR (10 créditos/día, usar con criterio)

## Commit workflow — MANDATORY

1. Tests + validación (pytest, ruff, size check)
2. Presentar al usuario (SIEMPRE, ESPERAR aprobación)
3. Actualizar docs afectados (ver trigger table)
4. Commit + push. Incluir Co-Authored-By.
5. Sugerir próximos pasos

## Document maintenance — trigger table

| Qué cambió | Documentos a actualizar |
|---|---|
| Completé una tarea | `TODO.md` marcar [x]. `CHANGELOG.md` agregar entry. `CURRENT_STATE.md` si cambió capability. |
| Agregué/borré archivo o módulo | `CLAUDE.md` project structure. `CURRENT_STATE.md` modules. |
| Cambié una API | `CURRENT_STATE.md` Key APIs |
| Cambié tests | `CURRENT_STATE.md` test coverage |
| Agregué dependencia | `pyproject.toml` Y `CLAUDE.md` tech stack |
| Cambié convención | `CLAUDE.md` actualizar |
| Cambió el scope/visión | `PROJECT.md` primero, propagar a `CLAUDE.md` y `TODO.md` |
| Nueva exploración/debate | `research/notes/` + actualizar `research/README.md` |
| Conclusión consolidada | `research/synthesis/` + actualizar `research/README.md` |

## Git conventions

- Branch principal: `main`
- Branches de autoresearch: `autoresearch/<tag>`
- Commits descriptivos en inglés
- results.tsv: **NO commitear** (untracked, journal completo)

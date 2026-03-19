# eq-distill — Claude Code Configuration

## START HERE — Read these docs first
1. **PROJECT.md** — Visión y propósito (north star)
2. **CURRENT_STATE.md** — Qué funciona hoy
3. **TODO.md** — Tareas pendientes y completadas
4. **CHANGELOG.md** — Historial de cambios
5. **docs/RESEARCH.md** — Investigación, hallazgos, estrategias

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
- Los hallazgos se documentan en `docs/RESEARCH.md`
- El progreso se trackea en `TODO.md` y `CHANGELOG.md`

## Mindset de investigación — SER CREATIVO

No estamos haciendo ingeniería incremental. Estamos INVESTIGANDO. Eso significa:

- **Buscar isomorfismos.** ¿Qué otros problemas se parecen a este? ¿Cómo los
  resuelven? Compresión de información, knowledge distillation, prompt optimization,
  evolutionary search, information theory, graph compression... ¿qué ideas de
  otros campos aplican acá?
- **No tener miedo de probar cosas locas.** Si una idea suena interesante,
  prototipala. Es más barato experimentar que debatir.
- **Profundizar, no surfear.** Mejor investigar UN approach a fondo que 5
  superficialmente.
- **Usar Codex (MCP) como sparring partner.** Debatir ideas, pedir code review,
  desafiar conclusiones.
- **Documentar TODO.** Cada hallazgo, cada dead end, cada insight va a
  docs/RESEARCH.md. El output principal de autoresearch es CONOCIMIENTO documentado.

## Manejo de contexto y reinicios

El watcher (`watch.sh`) relanza Claude Code cuando se cae o se queda sin
contexto. Cada restart es un Claude nuevo que reconstruye estado desde archivos:

1. Lee CLAUDE.md (este archivo) → entiende cómo trabajar
2. Lee TODO.md → ve qué está pendiente
3. Lee docs/RESEARCH.md → ve qué se investigó
4. Lee git log → ve qué se hizo recientemente
5. Continúa desde donde quedó

**Reglas para sobrevivir reinicios:**
- **Commitear frecuentemente.** Cada hallazgo significativo = commit. Así el
  próximo Claude ve el progreso en git log.
- **Documentar en docs/RESEARCH.md ANTES de que se llene el contexto.** Si
  descubriste algo, escribilo al archivo inmediatamente. No lo dejes solo en
  la conversación.
- **TODO.md como checkpoint.** Marcar tareas completadas y agregar las nuevas
  que surjan. El próximo Claude lee esto para saber dónde retomar.
- **No depender de la memoria conversacional.** Todo lo importante va a archivos.

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
├── docs/
│   └── RESEARCH.md         # Investigación y hallazgos
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
| Nuevos hallazgos de investigación | `docs/RESEARCH.md` |

## Git conventions

- Branch principal: `main`
- Branches de autoresearch: `autoresearch/<tag>`
- Commits descriptivos en inglés
- results.tsv: **NO commitear** (untracked, journal completo)

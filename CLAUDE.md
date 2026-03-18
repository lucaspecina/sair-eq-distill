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
Patrón de trabajo: autoresearch (iteración autónoma, medición, keep/discard).

## Environment setup

```bash
# Python con uv
uv sync
# O con pip
pip install -r requirements.txt
```

## Tech stack
- **Python 3.11+** — lenguaje principal
- **uv** — package manager
- **pandas** — análisis de datos del ETP
- **httpx** — llamadas a APIs de modelos
- **pytest** — tests
- **ruff** — linting y formatting

## Project structure

```
eq-distill/
├── PROJECT.md              # Visión y propósito
├── CLAUDE.md               # Este archivo
├── TODO.md                 # Task tracking
├── CURRENT_STATE.md        # Estado actual del sistema
├── CHANGELOG.md            # Historial
├── program.md              # Instrucciones autoresearch (solo humano edita)
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

# Evaluar un cheat sheet
python eval/evaluate.py --cheatsheet cheatsheets/current.txt --problems data/processed/problems.json

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

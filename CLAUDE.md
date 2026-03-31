# eq-distill — Claude Code Configuration

## START HERE — Read these docs first
1. **PROJECT.md** — Estrella polar: visión, LA PREGUNTA, principles
2. **CURRENT_STATE.md** — Qué funciona hoy (friendly)
3. **TODO.md** — Board operativo (qué sigue)
4. **CHANGELOG.md** — Historial de cambios
5. **research/README.md** — Índice de investigación y hallazgos

## LA PREGUNTA
> **¿Esto nos acerca a ganar la competencia?**
> Aplicar al evaluar, diseñar, priorizar, y revisar.
> Si un approach no impacta el score, NO importa.

## Where to find what
| I need to... | Go to... |
|---|---|
| Understand vision and principles | PROJECT.md |
| See what works TODAY | CURRENT_STATE.md |
| Know what's next | TODO.md |
| See change history | CHANGELOG.md |
| See work in progress | issues/ (active issues) |
| Find research findings | research/notes/ and research/synthesis/ |
| How to work on this project | This file (CLAUDE.md) |

## Project overview
Competencia Mathematics Distillation Challenge (SAIR Foundation, Terence Tao).
Destilar 22M de implicaciones de álgebra universal en un cheat sheet ≤10KB que
maximice la accuracy de un modelo chico prediciendo "¿ley A implica ley B?".

## Environment setup
```bash
conda activate eq-distill
# Si no existe: conda create -n eq-distill python=3.11 -y && pip install openai python-dotenv pandas httpx pytest ruff huggingface_hub
```
Siempre usar `conda run -n eq-distill python ...` o activar el env antes de scripts.

## Tech stack
- **Python 3.11+** — lenguaje principal
- **openai** — SDK para Azure Foundry API
- **pandas** — análisis de datos del ETP
- **httpx** — llamadas HTTP
- **pytest / ruff** — tests y linting
- **huggingface_hub** — descarga de datasets

## Project structure
```
eq-distill/
├── PROJECT.md, CLAUDE.md, TODO.md, CURRENT_STATE.md, CHANGELOG.md
├── AUTORESEARCH.md         # Config autoresearch (ON/OFF + run params)
├── issues/                 # Work threads con Status + Log (I-NNN)
├── experiments/            # Experiment artifacts con manifest.yaml
├── data/raw/, data/processed/
├── analysis/               # Scripts de exploración del dataset
├── cheatsheets/            # Versiones del cheat sheet (current.txt = activo)
├── eval/evaluate.py        # Evaluador local multi-modelo
├── optim/sheetevolve.py    # Optimizer evolutivo (herramienta principal)
├── research/notes/         # Research dumps (referenced from issues)
├── research/synthesis/     # Conclusiones consolidadas
├── research/archive/       # Docs superseded
└── .claude/skills/         # Project skills
```

## Code conventions
- Comunicación: **Español**
- Docstrings y comentarios: inglés
- Type hints en funciones públicas
- Archivos ≤300 líneas
- Cheat sheet: verificar ≤10KB antes de commit

## Commands
```bash
pytest                                          # Tests
ruff check . && ruff format .                   # Lint + format
python eval/evaluate.py --cheatsheet cheatsheets/current.txt  # Eval multi-modelo
python -c "import os; s=os.path.getsize('cheatsheets/current.txt'); print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240"  # Size check
```

## Quality assurance
- **Level 1 (pre-commit):** pytest + ruff + cheat sheet ≤10KB
- **Level 2 (periódico):** Evaluación local contra subset de problemas
- **Level 3 (validación externa):** Playground SAIR (10 créditos/día)

## Issue tracking
- Issues en `issues/I-NNN-slug.md` con Status header + Log
- Cross-ref con `I-NNN` en commits, código, docs
- Experiments en `experiments/ENNN-slug/` con manifest.yaml
- TODO.md = board operativo (NOW/NEXT/BLOCKED/LATER)
- Status header = memoria que sobrevive compactación de contexto

## Commit workflow — MANDATORY
1. VALIDATE — pytest + ruff + size check
2. PRESENT — explicar al usuario en español, ESPERAR aprobación
3. DOCS — actualizar docs afectados (ver trigger table)
4. COMMIT — con Co-Authored-By e I-NNN refs
5. NEXT — sugerir próximos pasos

## Autoresearch
- Config en `AUTORESEARCH.md` (ON/OFF + run params)
- Branch: `autoresearch/<topic>-<date>` desde branch base explícita
- Status header en issues = memoria persistente
- Stop conditions obligatorias
- NO modificar PROJECT.md ni CURRENT_STATE.md en branch de autoresearch

## Document maintenance — trigger table
| What changed | Update |
|---|---|
| Started/completed issue step | `issues/I-NNN.md` Status + Log |
| Completed a task | `TODO.md` move to DONE. `CHANGELOG.md` entry. |
| Closed an issue | `issues/I-NNN.md` Conclusión. `TODO.md` DONE. |
| Added/removed file or module | `CLAUDE.md` structure. `CURRENT_STATE.md`. |
| Changed an API | `CURRENT_STATE.md` |
| Added dependency | `pyproject.toml` AND `CLAUDE.md` tech stack |
| Changed convention | `CLAUDE.md` |
| Changed scope/vision | `PROJECT.md` first, propagate |
| Research done | `research/notes/` + ref from issue |
| Research conclusion | `research/synthesis/` + close/update issue |
| Ran experiment | `experiments/ENNN/manifest.yaml` + issue ref |

## Cleanup rules
- "Updating" = docs + skills + memories + scripts + configs
- If code/tests/scripts become obsolete → **DELETE** (git has history)
- If docs reference deleted things → **FIX** the reference
- After milestones: cleanup pass (stale refs, dead code, orphaned files)

## Git conventions
- Branch principal: `main`
- Branches de autoresearch: `autoresearch/<tag>-<date>`
- Commits descriptivos en inglés con I-NNN refs
- results.tsv: **NO commitear** (journal local)

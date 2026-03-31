# eq-distill — SAIR Mathematics Distillation Challenge

Competencia de Terence Tao / SAIR Foundation. Objetivo: destilar 22M de
implicaciones de álgebra universal en un cheatsheet de ≤10KB que maximice
la accuracy de un modelo chico prediciendo "Eq1 ⇒ Eq2?" (TRUE/FALSE).

**Deadline:** 20 abril 2026. **Mejor resultado local:** 89% en gpt-5-nano (200 probs).

## Quick start

```bash
# Activar environment
conda activate eq-distill

# Evaluar el cheatsheet actual
python eval/evaluate.py --cheatsheet cheatsheets/current.txt

# Correr SheetEvolve (optimizer evolutivo)
python optim/sheetevolve.py --stage1 --variants 1

# Validar tamaño
python -c "import os; s=os.path.getsize('cheatsheets/current.txt'); print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240"
```

## Estructura del proyecto

```
eq-distill/
├── PROJECT.md              # Visión y propósito (north star)
├── CLAUDE.md               # Config de Claude Code, workflow, convenciones
├── TODO.md                 # Board operativo (NOW/NEXT/BLOCKED/LATER)
├── CURRENT_STATE.md        # Qué funciona hoy (friendly)
├── CHANGELOG.md            # Historial de cambios con I-NNN refs
├── AUTORESEARCH.md         # Config autoresearch (ON/OFF)
├── watch.sh                # Supervisor que relanza Claude si crashea
├── issues/                 # Work threads con Status + Log (I-NNN)
├── experiments/            # Experiment artifacts con manifest.yaml
├── cheatsheets/
│   └── current.txt         # Cheatsheet activo (≤10KB)
├── eval/
│   └── evaluate.py         # Evaluador local multi-modelo
├── optim/
│   └── sheetevolve.py      # Optimizer evolutivo (herramienta principal)
├── research/
│   ├── notes/              # Research dumps
│   ├── synthesis/          # Conclusiones consolidadas
│   └── archive/            # Docs superseded
└── data/
    └── raw/                # Datos del ETP (22M implications)
```

## Más info

- `CLAUDE.md` — Cómo trabajar en este proyecto
- `PROJECT.md` — Visión, LA PREGUNTA, principios
- `TODO.md` — Qué sigue
- `research/README.md` — Índice de investigación

# Current State

## Overview

Proyecto recién bootstrapeado. Estructura de documentos y directorios creada. No hay código funcional todavía. La investigación inicial sobre la competencia y el patrón autoresearch está completa.

## Modules / Components

| Module | Purpose | Status |
|--------|---------|--------|
| `data/` | Datos del ETP (ecuaciones, implicaciones, magmas) | Vacío — pendiente descarga |
| `analysis/` | Exploración y análisis del dataset | No iniciado |
| `cheatsheets/` | Versiones del cheat sheet | No iniciado |
| `eval/` | Pipeline de evaluación local | No iniciado |
| `optim/` | Estrategias de optimización | No iniciado |

## Key APIs

Ninguna implementada aún. Planeadas:

- `eval/evaluate.py` — `evaluate(cheatsheet_path, problems_path, model) -> accuracy`
- `optim/evolutionary.py` — Loop evolutivo sobre cheat sheets
- Playground SAIR — Web UI en playground.sair.foundation (10 créditos/día)

## Test coverage

Sin tests. Se necesita:
- Tests para el evaluador local
- Validación de formato del cheat sheet (≤10KB)

## Known limitations

- No sabemos qué modelo chico usa la competencia exactamente
- El playground da solo 10 créditos/día — evaluación local es crítica
- No tenemos acceso al Zulip de la competencia aún

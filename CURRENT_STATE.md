# Current State

## Qué es esto?

Estamos compitiendo en el Mathematics Distillation Challenge de la SAIR Foundation.
El desafío: comprimir 22 millones de implicaciones matemáticas en un "cheat sheet"
de máximo 10KB que ayude a un modelo de lenguaje chico a predecir si una ley
ecuacional implica otra.

Nuestro cheat sheet se inyecta en el prompt del modelo evaluador. El modelo lee
el cheat sheet + la pregunta, y responde TRUE o FALSE.

## Qué funciona hoy

- **Cheat sheet actual:** `cheatsheets/current.txt` — 7.9KB, **89% accuracy** en
  200 problemas con gpt-5-nano (evaluación oficial local)
- **SheetEvolve** (`optim/sheetevolve.py`): optimizer evolutivo que usa gpt-5-nano
  como evaluador y gpt-5.4 como evolucionador. Produjo el 89% en 2 generaciones.
  Es nuestra herramienta principal de optimización.
- **Evaluador local** (`eval/evaluate.py`): evalúa cheatsheets contra subsets de
  problemas. Multi-modelo (gpt-5-nano, gpt-5-mini, etc.). Parsea `VERDICT: TRUE/FALSE`.
- **Research extenso:** 30+ notas de investigación, 3 synthesis documents, análisis
  de dataset, patrones de razonamiento de modelos, estrategias de optimización.
- **Datos del ETP:** dataset completo descargado y procesado (ecuaciones, implicaciones,
  magmas, DAG de 1415 nodos).

## Qué NO funciona todavía

- **Playground SAIR:** Descubrimos que usa modelos DISTINTOS a los que evaluamos
  localmente (gpt-oss-120b, llama3.3-70b, gemini-flash-lite, grok-4.1-fast).
  Necesitamos validar ahí.
- **Hard problems:** El cheat sheet está optimizado para problemas normales. Los
  hard problems (~30% del score) necesitan más trabajo.
- **Generalización multi-modelo:** El cheat sheet ayuda a nano pero puede perjudicar
  a otros modelos (ej: gpt-5-mini).

## Cómo probarlo

```bash
# Activar environment
conda activate eq-distill

# Evaluar el cheat sheet actual
python eval/evaluate.py --cheatsheet cheatsheets/current.txt

# Correr SheetEvolve (1 generación de prueba)
python optim/sheetevolve.py --stage1 --variants 1

# Verificar tamaño del cheat sheet
python -c "import os; s=os.path.getsize('cheatsheets/current.txt'); print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240"
```

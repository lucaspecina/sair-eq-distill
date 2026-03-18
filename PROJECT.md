# eq-distill

## What is this?

Proyecto para competir en el **Mathematics Distillation Challenge** de la SAIR Foundation (organizado por Terence Tao y Damek Davis). El objetivo es destilar 22 millones de resultados del Equational Theories Project (ETP) en un "cheat sheet" compacto (≤10KB) que ayude a un modelo de lenguaje chico a resolver problemas de álgebra universal (¿la ley A implica la ley B?).

## Key concepts

- **Magma:** Conjunto con una operación binaria (◇) sin axiomas adicionales. La estructura algebraica más básica.
- **Leyes ecuacionales:** Identidades como `x ◇ y = y ◇ x`. El ETP trabaja con 4694 leyes de hasta 4 operaciones.
- **Implicación:** A → B es verdadero si todo magma que cumple A necesariamente cumple B.
- **Cheat sheet:** Texto ≤10KB inyectado en el prompt de un modelo chico para guiar sus predicciones.
- **Autoresearch:** Nuestro workflow de trabajo. Claude Code corre autónomamente investigando, prototipando y experimentando. NO es un approach — es cómo trabajamos.

## Design principles

1. **Métrica sobre intuición** — Cada cambio al cheat sheet se evalúa con accuracy medible. Sin métricas no hay progreso.
2. **Generalización sobre memorización** — El test set final es privado. Optimizar para entender patrones, no para memorizar respuestas del set público.
3. **Densidad de información** — 10KB es muy poco. Cada byte debe aportar. Preferir reglas generales sobre listas de casos.
4. **Iteración rápida** — Evaluar ideas rápido, descartar lo que no funciona, profundizar lo que sí.
5. **Simplicidad** — A igual accuracy, el cheat sheet más simple gana (menos riesgo de overfitting).

## Architecture overview

```
[Datos ETP] → [Análisis] → [Cheat Sheet candidato] → [Evaluador local] → [Accuracy]
                                     ↑                        |
                                     +--- keep/discard -------+

[Playground SAIR] → Validación final (10 créditos/día)
```

Componentes:
- **data/**: Datos crudos y procesados del ETP (ecuaciones, implicaciones, magmas)
- **analysis/**: Scripts y notebooks de exploración del dataset
- **cheatsheets/**: Versiones del cheat sheet (el artefacto que se submite)
- **eval/**: Pipeline de evaluación local (modelo chico + subset de problemas)
- **optim/**: Estrategias de optimización (evolutivo, GEPA, heurísticas)

## What success looks like

1. **Stage 1 (deadline: 2026-04-20):** Maximizar accuracy en true/false. Entrar al top 1000.
2. **Stage 2:** Generar pruebas formales o contraejemplos (requiere entendimiento más profundo).
3. **Meta-goal:** Descubrir qué técnicas de distilación funcionan para problemas matemáticos.

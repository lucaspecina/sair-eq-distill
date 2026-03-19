# Changelog

## 2026-03-19
- Cheatsheet v6 achieves 96.7% on 30 normal problems (gpt-5-mini)
- Key insight: concise focused cheatsheet (2.7KB) >> comprehensive (6.3KB)
- Raised max_completion_tokens to 16384 (reasoning models need space)
- Dropped Phi-4 from eval (not in SAIR benchmark, too weak)

## 2026-03-18
- Bootstrap del proyecto: estructura de directorios, documentos estándar, skills
- Investigación de la competencia SAIR: reglas, playground, datos disponibles
- Investigación de autoresearch: patrón Karpathy, RALPH, mejores prácticas
- Dataset analysis: 22M implications, 1415 equivalence classes, DAG height 15
- Multi-feature predictor: 85.4% on normal (ceiling for heuristics)
- Identified 5 isomorphisms with other fields
- Quantified reasoning patterns from 25-model benchmark
- Prototyped OpenEvolve integration for prompt evolution

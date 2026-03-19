# Changelog

## 2026-03-19 (overnight autoresearch session)
- **Cheatsheet v6: 96.7%** on 30 normal problems (gpt-5-mini) — best result
- Tested 11 cheatsheet versions (v0-v11), v6 is locally optimal
- Key insight: concise focused (2.7KB) >> comprehensive (6.3KB)
- Raised max_completion_tokens to 16384 (reasoning models need space)
- Dropped Phi-4 from eval (not in SAIR benchmark, too weak)
- v6 on hard2: 60% (mini has TRUE bias on hard, opposite of normal)
- gpt-5-nano: 40-50% even with 32K tokens (too weak)
- Dataset analysis: DAG (1415 nodes, height 15), satisfaction scores, equivalence classes
- Multi-feature predictor: 85.4% ceiling on normal
- Quantified reasoning patterns from 25-model benchmark (substitution 4x more in correct)
- 14 research notes + 1 synthesis document
- Information theory: v6 near text-compression limit for normal problems
- Birkhoff completeness validates substitution as complete technique
- OpenEvolve prototype ready but needs API access for evolutionary runs
- Competition hard ≠ ETP hard (finite proofs exist, just non-obvious)
- Model biases: mini=TRUE bias on hard, nano=FALSE bias (opposite!)

## 2026-03-18
- Bootstrap del proyecto: estructura de directorios, documentos estándar, skills
- Investigación de la competencia SAIR: reglas, playground, datos disponibles
- Investigación de autoresearch: patrón Karpathy, RALPH, mejores prácticas
- Dataset analysis: 22M implications, 1415 equivalence classes, DAG height 15
- Multi-feature predictor: 85.4% on normal (ceiling for heuristics)
- Identified 5 isomorphisms with other fields
- Quantified reasoning patterns from 25-model benchmark
- Prototyped OpenEvolve integration for prompt evolution

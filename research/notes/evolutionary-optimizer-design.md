# Evolutionary Cheatsheet Optimizer — Design (inspirado en AlphaEvolve)

Date: 2026-03-19

## Arquitectura

Inspirado en AlphaEvolve (DeepMind, 2025). Adaptado para optimizar texto
(cheatsheet ≤10KB) en vez de código.

### Roles de los modelos

| Rol | Modelo | Función |
|-----|--------|---------|
| **Alumno** (evaluador) | gpt-5-nano | Toma el examen usando el cheatsheet. Simula la competencia. Barato, rápido. |
| **Profesor** (evolver) | gpt-5.4 | Mira las respuestas del alumno, mejora el cheatsheet. Inteligente, caro. |

nano no genera cheatsheets — nano USA el cheatsheet para responder preguntas de math.
gpt-5.4 no responde math — gpt-5.4 MEJORA el material de estudio viendo los errores del alumno.

### Loop evolutivo

```
1. nano toma examen con el cheatsheet actual
   → score + respuestas incorrectas con el razonamiento del modelo
2. gpt-5.4 ve: cheatsheet + errores crudos del alumno
   → genera versión mejorada del cheatsheet (solo dice "mejoralo")
3. nano toma examen NUEVO (problemas random frescos) con el cheatsheet nuevo
   → score del nuevo cheatsheet
4. Si mejoró → entra al pool de candidatos
5. Repetir desde 1
```

### Componentes clave (de AlphaEvolve)

**Pool con diversidad**: No solo top-K por score. Mantener variantes que sean
diferentes entre sí (en formato, largo, enfoque). Previene convergencia prematura.

**Inspiraciones**: Al evolver no solo le mostramos el parent, sino también
otros cheatsheets buenos del pool (distintos al parent) como "inspiración".
AlphaEvolve hace esto para fomentar combinación de ideas.

**Evaluación con datos frescos**: Cada evaluación usa un seed random
diferente (problemas distintos). Previene overfitting a problemas específicos.

**Paralelismo**: Todo lo que se pueda correr en paralelo, se corre en paralelo:
- Generación de variantes: en paralelo
- Evaluación de variantes: en paralelo
- Evaluación de parents: en paralelo

### Lo que NO copiamos de AlphaEvolve

- MAP-Elites con islas: demasiado complejo para nuestro caso. Pool simple con
  diversidad es suficiente.
- Ensemble de modelos para mutación: usamos solo gpt-5.4. Podríamos agregar
  nano como generador de breadth si necesitamos más variantes baratas.
- Cascada de evaluación multi-stage: por ahora evaluación simple con nano.
  Si el costo es problema, agregar un filtro rápido.

## Velocidad estimada

- Evaluación nano (20 problemas, concurrencia 20): ~1-2 min
- Generación gpt-5.4 (1 variante): ~30 seg
- 3 variantes por generación: ~5 min total (paralelo)
- 10 generaciones: ~50 min

## Formato target del cheatsheet

El evolver sabe que el cheatsheet ideal tiene:
1. **Decoder**: sección corta explicando la notación/vocabulario
2. **Payload**: reglas matemáticas densas, abstractas, generales

NO es un tutorial de comportamiento. Es conocimiento matemático comprimido.

## Implementación

`optim/evolve_cheatsheet.py` — script listo para correr.

## Referencias

- AlphaEvolve: https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- EvoPrompt (ICLR 2024): https://arxiv.org/abs/2309.08532
- OpenEvolve (open source): https://github.com/algorithmicsuperintelligence/openevolve
- ShinkaEvolve (Sakana AI): https://github.com/SakanaAI/ShinkaEvolve

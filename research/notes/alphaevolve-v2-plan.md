# AlphaEvolve v2 — Plan de implementación

Date: 2026-03-20

## Qué es esto

Un optimizer evolutivo para el cheatsheet, inspirado en AlphaEvolve pero
con los fixes que aprendimos del intento anterior (que fracasó con 40+
variantes sin superar el seed).

**Esto es un MÉTODO, no autoresearch.** Es una herramienta que un worker
(o nosotros directamente) ejecuta para optimizar el cheatsheet.

## Qué falló la primera vez y qué cambiamos

| Problema v1 | Fix v2 |
|---|---|
| Evaluaba con gpt-4.1-mini (ceiling 67%) | Evaluar con **gpt-5-nano** (el target real) |
| Problemas random cada generación (fitness ruidosa) | **Seed fijo** (mismo set siempre, comparación justa) |
| Pool solo por score (convergencia prematura) | **Diversidad**: rechazar variantes demasiado similares |
| Re-evaluaba padres cada generación (gasto innecesario) | **Cache de resultados**: padres ya evaluados no se re-evalúan |
| El evolver reescribía todo | Pendiente: mutaciones parciales (NO implementamos ahora) |
| No protegía TRUE accuracy | Pendiente: hard cutoffs (NO implementamos ahora) |

## Cómo funciona — explicación paso a paso

### Conceptos base

Hay dos modelos con roles distintos:

- **Alumno** (gpt-5-nano): toma exámenes. No es muy inteligente pero es el
  modelo de la competencia. Le damos una "hoja de fórmulas" (cheatsheet) y
  le pedimos que resuelva problemas de matemáticas.
- **Profesor** (gpt-5.4): no toma exámenes. Su trabajo es leer los errores
  del alumno y mejorar la hoja de fórmulas.

Y hay un **pool** — una colección de cheatsheets rankeados por score.
Al principio solo tiene el seed (nuestro best actual, 83.5%).

### Una generación, paso a paso

#### Paso 1: Elegir padres

Agarramos cheatsheets del pool como "padres". Elegimos 3 (pueden repetirse,
preferimos los de mejor score). Para cada padre vamos a generar un "hijo".

```
Padre 1: seed (83.5%)
Padre 2: seed (83.5%)  ← sí, puede repetirse
Padre 3: variante_A (81%)
```

#### Paso 2: Obtener los errores del padre

Necesitamos saber en qué se equivocó el alumno usando cada padre. Pero si
ya evaluamos a ese padre antes (en una generación anterior), **reutilizamos
esos resultados** — no gastamos API calls de nuevo.

Solo evaluamos padres que nunca fueron evaluados. Como el seed=42 da siempre
los mismos problemas, los resultados previos son válidos.

```
seed: ya evaluado en Gen 0 → reutilizar (0 calls)
variante_A: ya evaluada en Gen 1 → reutilizar (0 calls)
```

Si un padre es nuevo y nunca fue evaluado (no debería pasar, porque entró al
pool tras ser evaluado), recién ahí lo evaluamos.

#### Paso 3: El profesor genera variantes

Le mandamos a gpt-5.4 (el profesor) para cada padre:
- El cheatsheet padre completo
- Los errores del alumno CON su razonamiento (por qué se equivocó)
- Instrucciones de qué mejorar

gpt-5.4 lee todo, entiende dónde el alumno se confunde, y genera una versión
mejorada. Hace esto 3 veces (una por padre), en paralelo.

```
gpt-5.4 genera:
  hijo_1 (del seed): 6.2KB — cambió la sección de LZ/RZ
  hijo_2 (del seed): 7.1KB — agregó más ejemplos
  hijo_3 (de variante_A): 5.8KB — comprimió las reglas
```

Costo: 3 calls a gpt-5.4, ~3 min.

#### Paso 4: Eval cascada — filtro rápido (stage 1)

Evaluamos los 3 hijos con 50 problemas (seed=42, siempre los mismos).

```
hijo_1: 78% (39/50) — pasa el filtro (>= 75%)
hijo_2: 72% (36/50) — NO pasa → descartado
hijo_3: 84% (42/50) — pasa el filtro
```

Costo: 3 × 50 = 150 calls a nano, ~3 min.

#### Paso 5: Eval cascada — eval completa (stage 2)

Solo los que pasaron el filtro se evalúan con 200 problemas. Esto da un
score más confiable.

```
hijo_1: 200 problemas → 80.5% (161/200)
hijo_3: 200 problemas → 85.0% (170/200)  ← ¡mejoró!
```

Costo: 2 × 200 = 400 calls a nano, ~10 min.

Nota: guardamos los errores detallados de cada evaluación. Así, si este
hijo se convierte en padre en la próxima generación, ya tenemos sus errores
listos — no hace falta re-evaluarlo.

#### Paso 6: Check de diversidad

Antes de meter un hijo al pool, verificamos que sea suficientemente
**diferente** a lo que ya tenemos. Si es casi idéntico a otro cheatsheet
del pool (< 20% de diferencia en texto), lo rechazamos.

Esto previene que el pool se llene de variantes casi iguales (convergencia
prematura) y fuerza al profesor a explorar direcciones distintas.

```
hijo_1 vs pool: 35% diferente → OK, entra
hijo_3 vs pool: 42% diferente → OK, entra
```

Costo: 0 (comparación de strings, no usa API).

#### Paso 7: Actualizar el pool

Metemos los hijos al pool, ordenamos por score, nos quedamos con top 5.

```
Pool ANTES:  [seed: 83.5%, variante_A: 81%, variante_B: 80%]
+ nuevos:    [hijo_3: 85%, hijo_1: 80.5%]

Pool DESPUÉS (top 5):
  [hijo_3: 85%, seed: 83.5%, variante_A: 81%, hijo_1: 80.5%, variante_B: 80%]

★ NUEVO BEST: hijo_3 (85%)
```

#### Fin de la generación → siguiente

Logueamos todo y arrancamos la siguiente generación. Ahora el pool tiene
más variantes y el profesor puede tomar a hijo_3 (el nuevo best) como padre.

### Las 3 generaciones se verían así

```
Gen 0: Evaluar seed → Pool = [seed: 83.5%]
Gen 1: Pool = [hijo_3: 85%, seed: 83.5%, hijo_1: 80.5%]
Gen 2: Pool = [nieto_2: 86%, hijo_3: 85%, seed: 83.5%]
Gen 3: Pool = [bisnieto_1: 87%, nieto_2: 86%, hijo_3: 85%, seed: 83.5%]
```

O podría no mejorar nada. Pero con los fixes (nano, seed fijo, diversidad,
cache), las chances son mejores que la v1.

## Costos estimados (con cache de padres)

### Por generación
- 3 calls a gpt-5.4 (evolver): ~3 calls
- 3 evals stage 1 (50 probs cada una): 150 calls nano
- ~1-2 evals stage 2 (200 probs): 200-400 calls nano
- Padres: 0 calls (reutilizamos resultados previos)
- **Total por gen: ~350-550 calls, ~15-25 min**

### 3 generaciones (primera prueba)
- ~1000-1500 calls a gpt-5-nano
- ~9 calls a gpt-5.4
- ~45-75 min de tiempo
- + eval inicial del seed (50 probs): 50 calls

### Comparación con v1
- v1 gastó ~750 calls en un solo ciclo de autoresearch con peores resultados
- v2 gasta ~1200 calls en 3 generaciones pero con evaluación confiable

## Arquitectura

```
                    ┌─────────────────────────────────┐
                    │  POOL (top 5 por score)          │
                    │  + cache de errores por entrada  │
                    │  [seed: 83.5%] [v1] [v2]...     │
                    └──────┬──────────────┬────────────┘
                           │ selección    │ inserción
                           ▼              │
                    ┌──────────────┐      │
                    │ EVOLVER      │      │
                    │ (gpt-5.4)    │      │
                    │              │      │
                    │ Recibe:      │      │
                    │ - parent CS  │      │
                    │ - errores    │      │
                    │ - reasoning  │      │
                    │              │      │
                    │ Genera:      │      │
                    │ - variante   │      │
                    └──────┬───────┘      │
                           │              │
                           ▼              │
                    ┌──────────────┐      │
                    │ EVALUADOR    │      │
                    │ (gpt-5-nano) │──────┘
                    │              │
                    │ Cascada:     │
                    │ 1) 50 probs  │
                    │    < 75%? →  │ descarta
                    │ 2) 200 probs │
                    │    → score   │ + guarda errores
                    └──────────────┘
```

## Parámetros

- **Evolver model**: gpt-5.4
- **Evaluator model**: gpt-5-nano
- **Pool size**: 5
- **Variantes por generación**: 3
- **Generaciones**: 3 (primera prueba)
- **Eval stage 1**: 50 problemas, seed=42, cutoff < 75%
- **Eval stage 2**: 200 problemas, seed=42
- **Concurrencia**: 20
- **Diversidad**: rechazar si distancia de edición < 20% vs pool
- **Cache**: guardar errores detallados de cada eval para reutilizar

## Seed (cheatsheet inicial)

`cheatsheets/best.txt` — el cheatsheet actual que da 83.5%.

## Output esperado

- `optim/evolve_runs/v2/best.txt` — mejor cheatsheet encontrado
- `optim/evolve_runs/v2/history.json` — historial de scores por generación
- `optim/evolve_runs/v2/pool_*.txt` — variantes del pool final

## Criterio de éxito

Si el mejor cheatsheet del pool supera 83.5% en eval de 200 problemas
con seed=42, lo adoptamos como nuevo best. Si no, descartamos.

## Qué NO hacemos (por ahora)

- Mutaciones parciales por sección
- Hard cutoff de TRUE accuracy
- MAP-Elites con dimensiones de diversidad
- Múltiples modelos evaluadores

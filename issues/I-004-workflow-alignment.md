---
id: 4
title: Alinear repo con workflow estándar (skills de usuario)
status: closed
type: task
created: 2026-03-31
closed: 2026-03-31
---

# I-004: Alinear repo con workflow estándar (skills de usuario)

## Status
- **Estado:** Completo — todos los docs, issues, skills y cleanup hechos
- **Último resultado:** Repo alineado con dev-workflow, project-bootstrap, issue-tracking
- **Último commit:** 259cf43
- **Próximo paso:** Cerrado. Continuar con I-002 o I-003

## Pregunta
Alinear toda la estructura del repo con las user-level skills (dev-workflow,
project-bootstrap, issue-tracking, etc.) para tener un workflow consistente.

## Log

### 2026-03-31 · TASK — Reestructuración completa
Cambios planificados:
1. PROJECT.md → agregar LA PREGUNTA, quitar architecture
2. CLAUDE.md → reescribir a formato canónico (80-250 líneas)
3. TODO.md → NOW/NEXT/BLOCKED/LATER con I-NNN refs
4. CURRENT_STATE.md → actualizar a estado real (89%, no 96.7%)
5. AUTORESEARCH.md → crear config formal
6. issues/ → crear sistema de tracking retroactivo
7. experiments/, research/archive/ → crear directorios
8. Skills de proyecto → actualizar a design rules
9. Cleanup → eliminar 18+ scripts obsoletos

### 2026-03-31 · TASK — Ejecución completada
Todos los 9 pasos ejecutados:
1. ✓ PROJECT.md: LA PREGUNTA, architecture removido
2. ✓ CLAUDE.md: formato canónico ~130 líneas con trigger table, issue tracking
3. ✓ TODO.md: NOW/NEXT/BLOCKED/LATER con I-NNN refs
4. ✓ CURRENT_STATE.md: estado real (89% nano, SheetEvolve, modelos playground)
5. ✓ AUTORESEARCH.md: config formal OFF
6. ✓ issues/: I-001 a I-004 creados
7. ✓ experiments/, research/archive/: directorios creados
8. ✓ Skills: test, status, experiment actualizados con triggers y conda
9. ✓ Cleanup: 23 scripts eliminados, coordinator/program a archive

## Conclusión
Repo completamente alineado con las user-level skills (dev-workflow,
project-bootstrap, issue-tracking). Sistema de issues con Status headers,
AUTORESEARCH.md formal, trigger table canónica, cleanup de 23 archivos obsoletos.
El workflow ahora es consistente entre este proyecto y el estándar del usuario.

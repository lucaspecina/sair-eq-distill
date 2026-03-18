---
name: status
description: Show project status overview. Use when user asks about project status, progress, or current state.
disable-model-invocation: true
---

# Status

Show a quick overview of the project state.

## Steps

1. Read `CURRENT_STATE.md` and `TODO.md`

2. Check if cheat sheet exists and its size:
```bash
ls -la cheatsheets/ 2>/dev/null
```

3. Check results.tsv for experiment history:
```bash
wc -l results.tsv 2>/dev/null && tail -5 results.tsv 2>/dev/null || echo "No experiments yet"
```

4. Check git state:
```bash
git log --oneline -5
git status -s
```

5. Present to user in Spanish:
   - Tareas in progress y pending (from TODO.md)
   - Estado de módulos (from CURRENT_STATE.md)
   - Últimos experimentos (from results.tsv)
   - Último accuracy conocido

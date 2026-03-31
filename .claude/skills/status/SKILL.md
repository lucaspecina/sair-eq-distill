---
name: status
description: "Show project status overview: current accuracy, active issues, TODO board, recent experiments. Use when user asks 'status', 'qué onda', 'cómo estamos', or 'dónde estamos'."
disable-model-invocation: true
---

# Status

Show a quick overview of the project state.

## Steps

1. Read `CURRENT_STATE.md` and `TODO.md`

2. Read active issues:
```bash
grep -l "status: active" issues/*.md 2>/dev/null | head -5
```

3. Check cheat sheet size:
```bash
ls -la cheatsheets/current.txt 2>/dev/null
```

4. Check results.tsv for experiment history:
```bash
wc -l results.tsv 2>/dev/null && tail -5 results.tsv 2>/dev/null || echo "No experiments yet"
```

5. Check git state:
```bash
git log --oneline -5
git status -s
```

6. Present to user in Spanish:
   - Issues activos (Status header de cada uno)
   - Tareas NOW y NEXT (from TODO.md)
   - Último accuracy conocido
   - Últimos experimentos (from results.tsv)

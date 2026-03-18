---
name: test
description: Run tests and validate cheat sheet constraints. Use when testing code or validating a cheat sheet.
disable-model-invocation: true
---

# Test

Run the project's test suite and validations.

## Steps

1. Run pytest:
```bash
pytest -v
```

2. Run linting:
```bash
ruff check .
```

3. Validate cheat sheet size (if exists):
```bash
python -c "import os; p='cheatsheets/current.txt'; s=os.path.getsize(p) if os.path.exists(p) else 0; print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240, f'OVER LIMIT: {s} bytes'"
```

4. Report results to user.

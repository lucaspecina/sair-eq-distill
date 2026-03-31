---
name: test
description: "Run tests, lint, and validate cheat sheet constraints. Use when testing code, validating a cheat sheet, or before committing."
disable-model-invocation: true
---

# Test

Run the project's test suite and validations.

## Steps

1. Run pytest:
```bash
conda run -n eq-distill pytest -v
```

2. Run linting:
```bash
conda run -n eq-distill ruff check .
```

3. Validate cheat sheet size (if exists):
```bash
conda run -n eq-distill python -c "import os; p='cheatsheets/current.txt'; s=os.path.getsize(p) if os.path.exists(p) else 0; print(f'{s} bytes ({s/1024:.1f}KB)'); assert s<=10240, f'OVER LIMIT: {s} bytes'"
```

4. Report results to user.

"""Download SAIR competition datasets from HuggingFace."""

import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent / "raw"
RAW_DIR.mkdir(exist_ok=True)

BASE_URL = "hf://datasets/SAIRfoundation/equational-theories-selected-problems/data"
DATASETS = ["normal", "hard", "hard1", "hard2"]

for name in DATASETS:
    out_path = RAW_DIR / f"{name}.jsonl"
    if out_path.exists():
        print(f"  {name}: already exists, skipping")
        continue
    print(f"Downloading {name}...")
    try:
        df = pd.read_json(f"{BASE_URL}/{name}.jsonl", lines=True)
        df.to_json(out_path, orient="records", lines=True)
        n_true = df["answer"].sum()
        n_false = len(df) - n_true
        print(f"  {name}: {len(df)} problems ({n_true} true, {n_false} false)")
    except Exception as e:
        print(f"  {name}: FAILED - {e}")

print("\nDone.")

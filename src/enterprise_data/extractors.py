from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.enterprise_data.config import JSON_ROOTS, CsvSource, WAREHOUSE_DIR


def extract_csv(source: CsvSource) -> pd.DataFrame:
    if not source.path.is_file():
        raise FileNotFoundError(f"Warehouse source not found: {source.path}")
    return pd.read_csv(source.path)


def discover_json_sources() -> list[Path]:
    paths = []
    for root in JSON_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            try:
                path.resolve().relative_to(WAREHOUSE_DIR.resolve())
                continue
            except ValueError:
                pass
            paths.append(path)
    return sorted(set(paths))


def extract_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))

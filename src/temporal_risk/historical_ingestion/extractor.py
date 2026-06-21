from __future__ import annotations

import pandas as pd

from src.temporal_risk.historical_ingestion.contracts import HistoricalContractError


def extract_source(path, source_format: str) -> pd.DataFrame:
    normalized = source_format.strip().upper()
    try:
        if normalized == "CSV":
            return pd.read_csv(path)
        if normalized == "PARQUET":
            return pd.read_parquet(path)
    except Exception as exc:
        raise HistoricalContractError(f"Historical source could not be read: {exc}") from exc
    raise HistoricalContractError(f"Unsupported historical source format: {source_format}")

from __future__ import annotations

import hashlib
import json

import pandas as pd

from src.temporal_risk.historical_ingestion.contracts import CANONICAL_FIELDS


DATE_FIELDS = (
    "observation_date",
    "reporting_date",
    "origination_date",
    "default_date",
    "cure_date",
    "recovery_date",
    "maturity_date",
)
NUMERIC_FIELDS = ("pd", "lgd", "ead", "credit_score", "utilization")


def canonical_schema_hash(frame: pd.DataFrame) -> str:
    payload = [
        {
            "column": str(column),
            "dtype": str(frame[column].dtype),
            "nullable": bool(frame[column].isna().any()),
        }
        for column in frame.columns
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def normalize_frame(
    frame: pd.DataFrame,
    mappings: list[dict],
) -> pd.DataFrame:
    normalized = pd.DataFrame(index=frame.index)
    mapped = {item["canonical_column"]: item["source_column"] for item in mappings}
    for canonical in CANONICAL_FIELDS:
        normalized[canonical] = frame[mapped[canonical]] if canonical in mapped else None
    for column in DATE_FIELDS:
        normalized[column] = pd.to_datetime(
            normalized[column],
            errors="coerce",
        ).dt.date
    for column in NUMERIC_FIELDS:
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    normalized["source_row_number"] = range(1, len(frame) + 1)
    normalized["source_payload_json"] = [
        json.dumps(
            {
                str(key): None if pd.isna(value) else str(value)
                for key, value in row.items()
            },
            sort_keys=True,
        )
        for row in frame.to_dict(orient="records")
    ]
    return normalized


def inventory_values(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame:
        return []
    return sorted(
        {
            str(value)
            for value in frame[column].dropna().tolist()
            if str(value).strip()
        }
    )

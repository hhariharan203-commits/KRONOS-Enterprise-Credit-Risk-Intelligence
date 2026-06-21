from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.config import ROOT_DIR
from src.temporal_risk.connection import file_sha256
from src.temporal_risk.contracts import SYNTHETIC_BASELINE


def repository_relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def semantic_role(column: str) -> str:
    return {
        "borrower_id": "SOURCE_ENTITY_IDENTIFIER",
        "run_id": "EXECUTION_IDENTIFIER",
        "model_version": "MODEL_EXECUTION_METADATA",
        "timestamp": "PROCESS_TIMESTAMP",
        "scoring_status": "EXECUTION_STATUS",
    }.get(column, "BASELINE_ATTRIBUTE")


def temporal_role(column: str) -> str:
    return "PROCESS_TIME_ONLY" if column == "timestamp" else "NON_TEMPORAL"


def profile_source(path: Path) -> dict:
    source_hash_before = file_sha256(path)
    frame = pd.read_csv(path)
    source_hash_after = file_sha256(path)
    columns = []
    for position, column in enumerate(frame.columns, start=1):
        columns.append(
            {
                "column_name": str(column),
                "ordinal_position": position,
                "source_dtype": str(frame[column].dtype),
                "observed_nullable": bool(frame[column].isna().any()),
                "semantic_role": semantic_role(str(column)),
                "temporal_role": temporal_role(str(column)),
                "provenance_classification": (
                    "SOURCE_PROCESS_METADATA"
                    if column in {"run_id", "model_version", "timestamp", "scoring_status"}
                    else "SOURCE_BASELINE_FIELD"
                ),
            }
        )
    schema_payload = json.dumps(columns, sort_keys=True, separators=(",", ":"))
    schema_hash = hashlib.sha256(schema_payload.encode("utf-8")).hexdigest().upper()
    timestamps = sorted(frame["timestamp"].dropna().astype(str).unique().tolist())
    run_ids = sorted(frame["run_id"].dropna().astype(str).unique().tolist())
    model_versions = sorted(
        frame["model_version"].dropna().astype(str).unique().tolist()
    )
    scoring_status = {
        str(key): int(value)
        for key, value in frame["scoring_status"].value_counts(dropna=False).items()
    }
    return {
        "path": path,
        "relative_path": repository_relative(path),
        "sha256_before": source_hash_before,
        "sha256_after": source_hash_after,
        "size_bytes": path.stat().st_size,
        "modified_at": datetime.fromtimestamp(
            path.stat().st_mtime,
            tz=timezone.utc,
        ),
        "row_count": int(len(frame)),
        "column_count": int(len(frame.columns)),
        "columns": columns,
        "canonical_schema_hash": schema_hash,
        "distinct_borrower_count": int(frame["borrower_id"].nunique(dropna=True)),
        "borrower_null_count": int(frame["borrower_id"].isna().sum()),
        "run_ids": run_ids,
        "model_versions": model_versions,
        "timestamps": timestamps,
        "scoring_status": scoring_status,
        "all_timestamps_parseable": bool(
            pd.to_datetime(frame["timestamp"], errors="coerce", utc=True).notna().all()
        ),
        "all_timestamps_timezone_aware": bool(
            frame["timestamp"]
            .astype(str)
            .str.contains(r"(?:Z|[+-]\d{2}:\d{2})$", regex=True)
            .all()
        ),
    }


def register_source(connection, profile: dict) -> str:
    source_asset_id = stable_id(profile["relative_path"], profile["sha256_before"])
    now = utc_now()
    connection.execute(
        """
        INSERT OR IGNORE INTO control.source_asset (
            source_asset_id, logical_source_name, relative_path, source_type,
            source_system, evidence_classification, authoritative_baseline,
            sha256, size_bytes, modified_at, row_count, column_count,
            canonical_schema_hash, first_seen_at, last_seen_at
        ) VALUES (?, 'scored_portfolio', ?, 'CSV', 'KRONOS_MASTER',
                  ?, TRUE, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            source_asset_id,
            profile["relative_path"],
            SYNTHETIC_BASELINE,
            profile["sha256_before"],
            profile["size_bytes"],
            profile["modified_at"],
            profile["row_count"],
            profile["column_count"],
            profile["canonical_schema_hash"],
            now,
            now,
        ],
    )
    connection.execute(
        "UPDATE control.source_asset SET last_seen_at = ? WHERE source_asset_id = ?",
        [now, source_asset_id],
    )
    for column in profile["columns"]:
        column_id = stable_id(source_asset_id, column["column_name"])
        connection.execute(
            """
            INSERT OR IGNORE INTO control.source_column (
                source_column_id, source_asset_id, column_name,
                ordinal_position, source_dtype, observed_nullable,
                semantic_role, temporal_role, provenance_classification
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                column_id,
                source_asset_id,
                column["column_name"],
                column["ordinal_position"],
                column["source_dtype"],
                column["observed_nullable"],
                column["semantic_role"],
                column["temporal_role"],
                column["provenance_classification"],
            ],
        )
    return source_asset_id


def serializable_profile(profile: dict) -> dict:
    return {
        key: (
            value.isoformat()
            if isinstance(value, datetime)
            else str(value)
            if isinstance(value, Path)
            else value
        )
        for key, value in profile.items()
    }

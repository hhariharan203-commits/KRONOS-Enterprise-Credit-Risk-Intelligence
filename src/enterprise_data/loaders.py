from __future__ import annotations

import json
import re
from datetime import datetime, timezone

import pandas as pd

from src.enterprise_data.audit import record_step
from src.enterprise_data.config import CSV_SOURCES
from src.enterprise_data.extractors import discover_json_sources, extract_csv, extract_json
from src.enterprise_data.schema_manager import table_columns, table_exists
from src.enterprise_data.source_registry import (
    register_json_source,
    register_source_asset,
)


VALID_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TECHNICAL_COLUMNS = [
    "etl_batch_id",
    "source_asset_id",
    "source_sha256",
    "loaded_at",
]


class WarehouseSchemaDriftError(RuntimeError):
    """Raised when a source schema changes without an approved migration."""


def _qualified_staging_table(table_name: str) -> str:
    if not VALID_NAME.fullmatch(table_name):
        raise ValueError(f"Invalid staging table name: {table_name}")
    return f"staging.{table_name}"


def _ensure_staging_table(connection, table_name: str, frame: pd.DataFrame) -> None:
    qualified = _qualified_staging_table(table_name)
    connection.register("_incoming_staging_frame", frame)
    try:
        if not table_exists(connection, "staging", table_name):
            connection.execute(
                f"CREATE TABLE {qualified} AS "
                "SELECT * FROM _incoming_staging_frame WHERE FALSE"
            )
        existing = table_columns(connection, "staging", table_name)
        incoming = list(frame.columns)
        if existing != incoming:
            raise WarehouseSchemaDriftError(
                f"Schema drift detected for {qualified}. "
                f"Expected {existing}; received {incoming}."
            )
    finally:
        connection.unregister("_incoming_staging_frame")


def load_csv_source(connection, batch_id: str, source) -> dict:
    frame = extract_csv(source)
    source_record = register_source_asset(connection, source, frame)
    qualified = _qualified_staging_table(source.staging_table)
    existing_rows = 0
    if table_exists(connection, "staging", source.staging_table):
        existing_rows = connection.execute(
            f"SELECT COUNT(*) FROM {qualified} WHERE source_asset_id = ?",
            [source_record["source_asset_id"]],
        ).fetchone()[0]
    if existing_rows:
        record_step(
            connection,
            batch_id,
            f"LOAD_{source.source_name}",
            status="SKIPPED",
            row_count=existing_rows,
            message="Identical source hash already loaded.",
        )
        return {**source_record, "status": "SKIPPED", "staging_table": qualified}

    loaded_at = datetime.now(timezone.utc)
    staged = frame.copy()
    staged["etl_batch_id"] = batch_id
    staged["source_asset_id"] = source_record["source_asset_id"]
    staged["source_sha256"] = source_record["sha256"]
    staged["loaded_at"] = loaded_at
    _ensure_staging_table(connection, source.staging_table, staged)

    connection.register("_incoming_staging_frame", staged)
    try:
        connection.execute(
            f"INSERT INTO {qualified} BY NAME SELECT * FROM _incoming_staging_frame"
        )
    finally:
        connection.unregister("_incoming_staging_frame")

    record_step(
        connection,
        batch_id,
        f"LOAD_{source.source_name}",
        status="SUCCESS",
        row_count=len(staged),
    )
    return {**source_record, "status": "LOADED", "staging_table": qualified}


def load_all_csv_sources(connection, batch_id: str) -> list[dict]:
    return [
        load_csv_source(connection, batch_id, source)
        for source in CSV_SOURCES
    ]


def load_json_sources(connection, batch_id: str) -> list[dict]:
    results = []
    for path in discover_json_sources():
        payload = extract_json(path)
        source_record = register_json_source(connection, path, payload)
        existing = connection.execute(
            """
            SELECT COUNT(*) FROM staging.stg_json_artifact
            WHERE source_asset_id = ?
            """,
            [source_record["source_asset_id"]],
        ).fetchone()[0]
        if existing:
            results.append({**source_record, "status": "SKIPPED"})
            continue
        connection.execute(
            """
            INSERT INTO staging.stg_json_artifact (
                source_asset_id, etl_batch_id, relative_path,
                source_sha256, payload_json, loaded_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                source_record["source_asset_id"],
                batch_id,
                source_record["relative_path"],
                source_record["sha256"],
                json.dumps(payload, default=str),
                datetime.now(timezone.utc),
            ],
        )
        results.append({**source_record, "status": "LOADED"})

    record_step(
        connection,
        batch_id,
        "LOAD_JSON_ARTIFACTS",
        status="SUCCESS",
        row_count=len(results),
    )
    return results

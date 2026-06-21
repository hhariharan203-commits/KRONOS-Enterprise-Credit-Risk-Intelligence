from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.enterprise_data.config import CsvSource, ROOT_DIR


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_asset_id(path: Path, sha256: str) -> str:
    payload = f"{relative_path(path)}|{sha256}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:32]


def dataframe_schema(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "column_name": str(column),
            "ordinal_position": position,
            "source_dtype": str(frame[column].dtype),
            "nullable": bool(frame[column].isna().any()),
        }
        for position, column in enumerate(frame.columns, start=1)
    ]


def register_source_asset(
    connection,
    source: CsvSource,
    frame: pd.DataFrame,
) -> dict:
    path = source.path
    sha256 = file_sha256(path)
    asset_id = source_asset_id(path, sha256)
    now = utc_now()
    schema = dataframe_schema(frame)
    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    connection.execute(
        """
        UPDATE control.source_asset
        SET is_current = FALSE
        WHERE relative_path = ?
        """,
        [relative_path(path)],
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO control.source_asset (
            source_asset_id, source_name, source_domain, relative_path,
            file_type, sha256, size_bytes, modified_at, row_count,
            schema_json, first_seen_at, last_seen_at, is_current
        ) VALUES (?, ?, ?, ?, 'CSV', ?, ?, ?, ?, ?, ?, ?, TRUE)
        """,
        [
            asset_id,
            source.source_name,
            source.source_domain,
            relative_path(path),
            sha256,
            path.stat().st_size,
            modified_at,
            len(frame),
            json.dumps(schema),
            now,
            now,
        ],
    )
    connection.execute(
        """
        UPDATE control.source_asset
        SET last_seen_at = ?, row_count = ?, schema_json = ?,
            size_bytes = ?, modified_at = ?, is_current = TRUE
        WHERE source_asset_id = ?
        """,
        [
            now,
            len(frame),
            json.dumps(schema),
            path.stat().st_size,
            modified_at,
            asset_id,
        ],
    )

    for column in schema:
        snapshot_id = hashlib.sha256(
            f"{asset_id}|{column['column_name']}".encode("utf-8")
        ).hexdigest()[:32]
        connection.execute(
            """
            INSERT OR IGNORE INTO control.schema_snapshot (
                schema_snapshot_id, source_asset_id, column_name,
                ordinal_position, source_dtype, nullable, captured_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                snapshot_id,
                asset_id,
                column["column_name"],
                column["ordinal_position"],
                column["source_dtype"],
                column["nullable"],
                now,
            ],
        )

    return {
        "source_asset_id": asset_id,
        "sha256": sha256,
        "row_count": len(frame),
        "schema": schema,
        "relative_path": relative_path(path),
    }


def register_json_source(connection, path: Path, payload: object) -> dict:
    sha256 = file_sha256(path)
    asset_id = source_asset_id(path, sha256)
    now = utc_now()
    modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    schema_summary = {
        "payload_type": type(payload).__name__,
        "top_level_keys": list(payload) if isinstance(payload, dict) else [],
        "item_count": len(payload) if hasattr(payload, "__len__") else None,
    }

    connection.execute(
        """
        UPDATE control.source_asset
        SET is_current = FALSE
        WHERE relative_path = ?
        """,
        [relative_path(path)],
    )
    connection.execute(
        """
        INSERT OR IGNORE INTO control.source_asset (
            source_asset_id, source_name, source_domain, relative_path,
            file_type, sha256, size_bytes, modified_at, row_count,
            schema_json, first_seen_at, last_seen_at, is_current
        ) VALUES (?, ?, 'GOVERNANCE', ?, 'JSON', ?, ?, ?, ?, ?, ?, ?, TRUE)
        """,
        [
            asset_id,
            path.stem,
            relative_path(path),
            sha256,
            path.stat().st_size,
            modified_at,
            len(payload) if hasattr(payload, "__len__") else None,
            json.dumps(schema_summary),
            now,
            now,
        ],
    )
    connection.execute(
        """
        UPDATE control.source_asset
        SET last_seen_at = ?, size_bytes = ?, modified_at = ?,
            row_count = ?, schema_json = ?, is_current = TRUE
        WHERE source_asset_id = ?
        """,
        [
            now,
            path.stat().st_size,
            modified_at,
            len(payload) if hasattr(payload, "__len__") else None,
            json.dumps(schema_summary),
            asset_id,
        ],
    )
    return {
        "source_asset_id": asset_id,
        "sha256": sha256,
        "relative_path": relative_path(path),
    }

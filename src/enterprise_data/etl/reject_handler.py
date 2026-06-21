from __future__ import annotations

import hashlib
from datetime import datetime, timezone


def log_reject(
    connection,
    *,
    batch_id: str,
    job_id: str | None,
    source_asset_id: str | None,
    source_name: str,
    record_identifier,
    column_name: str,
    invalid_value,
    rejection_reason: str,
    source_row_number: int | None = None,
    payload_json: str | None = None,
) -> str:
    rejected_at = datetime.now(timezone.utc)
    rejected_id = hashlib.sha256(
        (
            f"{batch_id}|{job_id}|{source_name}|{record_identifier}|"
            f"{column_name}|{invalid_value}|{rejection_reason}"
        ).encode("utf-8")
    ).hexdigest()[:32]
    connection.execute(
        """
        INSERT OR IGNORE INTO control.rejected_record (
            rejected_record_id, etl_batch_id, source_asset_id,
            source_row_number, rejection_reason, payload_json, rejected_at,
            job_id, source_name, record_identifier, column_name,
            invalid_value, rejected_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            rejected_id,
            batch_id,
            source_asset_id,
            source_row_number,
            rejection_reason,
            payload_json,
            rejected_at,
            job_id,
            source_name,
            None if record_identifier is None else str(record_identifier),
            column_name,
            None if invalid_value is None else str(invalid_value),
            rejected_at,
        ],
    )
    return rejected_id


def count_batch_rejects(connection, batch_id: str) -> int:
    return int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM control.rejected_record
            WHERE etl_batch_id = ?
            """,
            [batch_id],
        ).fetchone()[0]
    )

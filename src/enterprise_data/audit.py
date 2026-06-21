from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


WAREHOUSE_VERSION = "4A.1"


def utc_now():
    return datetime.now(timezone.utc)


def start_batch(connection) -> str:
    now = utc_now()
    connection.execute(
        """
        UPDATE control.etl_batch
        SET completed_at = ?, status = 'ABANDONED',
            error_message = 'Previous warehouse process ended before batch completion.'
        WHERE status = 'RUNNING'
        """,
        [now],
    )
    batch_id = uuid4().hex
    connection.execute(
        """
        INSERT INTO control.etl_batch (
            etl_batch_id, started_at, status, warehouse_version
        ) VALUES (?, ?, 'RUNNING', ?)
        """,
        [batch_id, now, WAREHOUSE_VERSION],
    )
    return batch_id


def finish_batch(
    connection,
    batch_id: str,
    *,
    status: str,
    source_count: int = 0,
    loaded_source_count: int = 0,
    skipped_source_count: int = 0,
    error_message: str | None = None,
) -> None:
    connection.execute(
        """
        UPDATE control.etl_batch
        SET completed_at = ?, status = ?, source_count = ?,
            loaded_source_count = ?, skipped_source_count = ?,
            error_message = ?
        WHERE etl_batch_id = ?
        """,
        [
            utc_now(),
            status,
            source_count,
            loaded_source_count,
            skipped_source_count,
            error_message,
            batch_id,
        ],
    )


def record_step(
    connection,
    batch_id: str,
    step_name: str,
    *,
    status: str,
    row_count: int | None = None,
    message: str | None = None,
) -> None:
    now = utc_now()
    connection.execute(
        """
        INSERT INTO control.etl_step_run (
            step_run_id, etl_batch_id, step_name, started_at,
            completed_at, status, row_count, message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [uuid4().hex, batch_id, step_name, now, now, status, row_count, message],
    )

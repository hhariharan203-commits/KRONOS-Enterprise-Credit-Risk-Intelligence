from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.enterprise_data.config import WAREHOUSE_DB


RECOVERABLE_BATCH_STATUSES = {
    "FAILED",
    "PARTIAL_SUCCESS",
    "ABANDONED",
}


def validate_recovery_source(connection, batch_id: str) -> str:
    row = connection.execute(
        """
        SELECT status
        FROM control.etl_batch
        WHERE etl_batch_id = ?
        """,
        [batch_id],
    ).fetchone()
    if row is None:
        raise ValueError(f"Recovery source batch does not exist: {batch_id}")
    status = str(row[0])
    if status not in RECOVERABLE_BATCH_STATUSES:
        raise ValueError(
            f"Batch {batch_id} has status {status}; recovery requires "
            f"{sorted(RECOVERABLE_BATCH_STATUSES)}."
        )
    return status


def completed_jobs(connection, batch_id: str) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            """
            SELECT job_name
            FROM control.etl_job_run
            WHERE etl_batch_id = ? AND status = 'SUCCESS'
            """,
            [batch_id],
        ).fetchall()
    }


def _copy_quality_controls(
    connection,
    source_batch_id: str,
    recovery_batch_id: str,
) -> None:
    summary = connection.execute(
        """
        SELECT quality_score, quality_status, rule_count, passed_rule_count,
               warning_rule_count, failed_rule_count, quality_details
        FROM control.etl_quality_summary
        WHERE etl_batch_id = ?
        """,
        [source_batch_id],
    ).fetchone()
    if summary is not None:
        summary_id = hashlib.sha256(
            f"{recovery_batch_id}|INHERITED_QUALITY".encode("utf-8")
        ).hexdigest()[:32]
        connection.execute(
            """
            INSERT INTO control.etl_quality_summary (
                quality_summary_id, etl_batch_id, job_id, quality_score,
                quality_status, rule_count, passed_rule_count,
                warning_rule_count, failed_rule_count, quality_details,
                evaluated_at
            ) VALUES (?, ?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (etl_batch_id) DO UPDATE SET
                job_id = EXCLUDED.job_id,
                quality_score = EXCLUDED.quality_score,
                quality_status = EXCLUDED.quality_status,
                rule_count = EXCLUDED.rule_count,
                passed_rule_count = EXCLUDED.passed_rule_count,
                warning_rule_count = EXCLUDED.warning_rule_count,
                failed_rule_count = EXCLUDED.failed_rule_count,
                quality_details = EXCLUDED.quality_details,
                evaluated_at = EXCLUDED.evaluated_at
            """,
            [
                summary_id,
                recovery_batch_id,
                *summary,
                datetime.now(timezone.utc),
            ],
        )
    rows = connection.execute(
        """
        SELECT source_asset_id, check_name, check_scope, status,
               actual_value, expected_value, details
        FROM control.data_quality_result
        WHERE etl_batch_id = ?
        """,
        [source_batch_id],
    ).fetchall()
    for row in rows:
        result_id = hashlib.sha256(
            f"{recovery_batch_id}|INHERITED|{row[1]}".encode("utf-8")
        ).hexdigest()[:32]
        connection.execute(
            """
            INSERT OR IGNORE INTO control.data_quality_result (
                quality_result_id, etl_batch_id, source_asset_id, check_name,
                check_scope, status, actual_value, expected_value, details,
                checked_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                result_id,
                recovery_batch_id,
                *row,
                datetime.now(timezone.utc),
            ],
        )


def _copy_reconciliation_controls(
    connection,
    source_batch_id: str,
    recovery_batch_id: str,
) -> None:
    rows = connection.execute(
        """
        SELECT source_asset_id, reconciliation_name, source_value,
               warehouse_value, absolute_difference, tolerance, status,
               source_count, staging_count, core_count, mart_count, variance
        FROM control.reconciliation_result
        WHERE etl_batch_id = ?
        """,
        [source_batch_id],
    ).fetchall()
    for row in rows:
        reconciliation_id = hashlib.sha256(
            f"{recovery_batch_id}|INHERITED|{row[1]}".encode("utf-8")
        ).hexdigest()[:32]
        connection.execute(
            """
            INSERT OR IGNORE INTO control.reconciliation_result (
                reconciliation_id, etl_batch_id, source_asset_id,
                reconciliation_name, source_value, warehouse_value,
                absolute_difference, tolerance, status, reconciled_at,
                job_id, source_count, staging_count, core_count, mart_count,
                variance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, ?)
            """,
            [
                reconciliation_id,
                recovery_batch_id,
                *row[:7],
                datetime.now(timezone.utc),
                *row[7:],
            ],
        )


def inherit_completed_controls(
    connection,
    source_batch_id: str,
    recovery_batch_id: str,
    completed_job_names: set[str],
) -> None:
    if "VALIDATE_QUALITY" in completed_job_names:
        _copy_quality_controls(connection, source_batch_id, recovery_batch_id)
    if "RECONCILE_COUNTS" in completed_job_names:
        _copy_reconciliation_controls(
            connection,
            source_batch_id,
            recovery_batch_id,
        )


def record_recovery_event(
    connection,
    *,
    source_batch_id: str,
    recovery_batch_id: str,
    recovery_type: str,
    requested_job_name: str | None,
    status: str,
    details: dict,
) -> str:
    event_id = uuid4().hex
    connection.execute(
        """
        INSERT INTO control.etl_recovery_event (
            recovery_event_id, source_batch_id, recovery_batch_id,
            recovery_type, requested_job_name, status, details, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            event_id,
            source_batch_id,
            recovery_batch_id,
            recovery_type,
            requested_job_name,
            status,
            json.dumps(details, default=str),
            datetime.now(timezone.utc),
        ],
    )
    return event_id


def resume_failed_batch(
    batch_id: str,
    database_path: Path | str = WAREHOUSE_DB,
) -> dict:
    from src.enterprise_data.etl.scheduler import run_phase4b_etl

    return run_phase4b_etl(
        database_path=database_path,
        recovery_from_batch_id=batch_id,
    )


def rerun_failed_step(
    batch_id: str,
    job_name: str,
    database_path: Path | str = WAREHOUSE_DB,
) -> dict:
    from src.enterprise_data.connection import connect_warehouse
    from src.enterprise_data.etl.scheduler import run_phase4b_etl

    connection = connect_warehouse(database_path, read_only=True)
    try:
        row = connection.execute(
            """
            SELECT status
            FROM control.etl_job_run
            WHERE etl_batch_id = ? AND job_name = ?
            """,
            [batch_id, job_name],
        ).fetchone()
    finally:
        connection.close()
    if row is None or row[0] not in {"FAILED", "BLOCKED"}:
        raise ValueError(
            f"Job {job_name} is not a failed or blocked step in batch {batch_id}."
        )
    return run_phase4b_etl(
        database_path=database_path,
        recovery_from_batch_id=batch_id,
        requested_recovery_job=job_name,
    )

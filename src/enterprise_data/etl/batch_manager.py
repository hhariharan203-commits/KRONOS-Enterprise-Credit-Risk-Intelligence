from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.enterprise_data.schema_manager import (
    ensure_reconciliation_result_schema,
    refresh_control_views,
)


BATCH_STATUSES = {
    "PENDING",
    "RUNNING",
    "SUCCESS",
    "FAILED",
    "PARTIAL_SUCCESS",
    "ABANDONED",
}

PHASE4B_VERSION = "4B.1"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def initialize_etl_control_schema(connection) -> None:
    alter_statements = (
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS start_time TIMESTAMP",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS end_time TIMESTAMP",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS duration_seconds DOUBLE",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS records_processed BIGINT DEFAULT 0",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS records_loaded BIGINT DEFAULT 0",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS records_rejected BIGINT DEFAULT 0",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS artifact_count BIGINT DEFAULT 0",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS warehouse_status VARCHAR",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS batch_type VARCHAR",
        "ALTER TABLE control.etl_batch ADD COLUMN IF NOT EXISTS resume_of_batch_id VARCHAR",
        "ALTER TABLE control.rejected_record ADD COLUMN IF NOT EXISTS job_id VARCHAR",
        "ALTER TABLE control.rejected_record ADD COLUMN IF NOT EXISTS source_name VARCHAR",
        "ALTER TABLE control.rejected_record ADD COLUMN IF NOT EXISTS record_identifier VARCHAR",
        "ALTER TABLE control.rejected_record ADD COLUMN IF NOT EXISTS column_name VARCHAR",
        "ALTER TABLE control.rejected_record ADD COLUMN IF NOT EXISTS invalid_value VARCHAR",
        "ALTER TABLE control.rejected_record ADD COLUMN IF NOT EXISTS rejected_timestamp TIMESTAMP",
        "ALTER TABLE control.publish_status ADD COLUMN IF NOT EXISTS job_id VARCHAR",
        "ALTER TABLE control.publish_status ADD COLUMN IF NOT EXISTS previous_status VARCHAR",
        "ALTER TABLE control.publish_status ADD COLUMN IF NOT EXISTS requested_at TIMESTAMP",
        "ALTER TABLE control.publish_status ADD COLUMN IF NOT EXISTS validated_at TIMESTAMP",
        "ALTER TABLE control.publish_status ADD COLUMN IF NOT EXISTS transition_at TIMESTAMP",
    )
    for statement in alter_statements:
        connection.execute(statement)

    ensure_reconciliation_result_schema(connection)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS control.etl_job_run (
            job_id VARCHAR PRIMARY KEY,
            etl_batch_id VARCHAR NOT NULL,
            job_name VARCHAR NOT NULL,
            job_type VARCHAR NOT NULL,
            upstream_jobs VARCHAR NOT NULL,
            downstream_jobs VARCHAR NOT NULL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            status VARCHAR NOT NULL,
            duration_seconds DOUBLE,
            records_processed BIGINT DEFAULT 0,
            records_loaded BIGINT DEFAULT 0,
            records_rejected BIGINT DEFAULT 0,
            error_message VARCHAR,
            details_json VARCHAR,
            UNIQUE(etl_batch_id, job_name)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS control.etl_job_dependency (
            dependency_id VARCHAR PRIMARY KEY,
            etl_batch_id VARCHAR NOT NULL,
            upstream_job_name VARCHAR NOT NULL,
            downstream_job_name VARCHAR NOT NULL,
            validation_status VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS control.etl_quality_summary (
            quality_summary_id VARCHAR PRIMARY KEY,
            etl_batch_id VARCHAR NOT NULL,
            job_id VARCHAR,
            quality_score DOUBLE NOT NULL,
            quality_status VARCHAR NOT NULL,
            rule_count BIGINT NOT NULL,
            passed_rule_count BIGINT NOT NULL,
            warning_rule_count BIGINT NOT NULL,
            failed_rule_count BIGINT NOT NULL,
            quality_details VARCHAR NOT NULL,
            evaluated_at TIMESTAMP NOT NULL,
            UNIQUE(etl_batch_id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS control.operational_metric (
            operational_metric_id VARCHAR PRIMARY KEY,
            etl_batch_id VARCHAR,
            metric_name VARCHAR NOT NULL,
            metric_value DOUBLE,
            metric_text VARCHAR,
            metric_unit VARCHAR,
            details VARCHAR,
            captured_at TIMESTAMP NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS control.etl_recovery_event (
            recovery_event_id VARCHAR PRIMARY KEY,
            source_batch_id VARCHAR NOT NULL,
            recovery_batch_id VARCHAR NOT NULL,
            recovery_type VARCHAR NOT NULL,
            requested_job_name VARCHAR,
            status VARCHAR NOT NULL,
            details VARCHAR,
            created_at TIMESTAMP NOT NULL
        )
        """
    )
    refresh_control_views(connection)


def start_batch(
    connection,
    *,
    source_count: int = 0,
    artifact_count: int = 0,
    recovery_from_batch_id: str | None = None,
) -> str:
    initialize_etl_control_schema(connection)
    now = utc_now()
    connection.execute(
        """
        UPDATE control.etl_batch
        SET completed_at = ?, end_time = ?, status = 'ABANDONED',
            duration_seconds = date_diff('millisecond', COALESCE(start_time, started_at), ?) / 1000.0,
            error_message = COALESCE(
                error_message,
                'Previous ETL control process ended before batch completion.'
            )
        WHERE status = 'RUNNING'
        """,
        [now, now, now],
    )
    batch_id = uuid4().hex
    connection.execute(
        """
        INSERT INTO control.etl_batch (
            etl_batch_id, started_at, start_time, status, warehouse_version,
            source_count, artifact_count, warehouse_status, batch_type,
            resume_of_batch_id
        ) VALUES (?, ?, ?, 'RUNNING', ?, ?, ?, 'AVAILABLE', 'PHASE4B_CONTROL', ?)
        """,
        [
            batch_id,
            now,
            now,
            PHASE4B_VERSION,
            int(source_count),
            int(artifact_count),
            recovery_from_batch_id,
        ],
    )
    return batch_id


def finish_batch(
    connection,
    batch_id: str,
    *,
    status: str,
    source_count: int,
    artifact_count: int,
    warehouse_status: str = "AVAILABLE",
    error_message: str | None = None,
) -> dict:
    if status not in BATCH_STATUSES:
        raise ValueError(f"Unsupported batch status: {status}")
    now = utc_now()
    aggregates = connection.execute(
        """
        SELECT
            COALESCE(SUM(records_processed), 0),
            COALESCE(SUM(records_loaded), 0),
            COALESCE(SUM(records_rejected), 0)
        FROM control.etl_job_run
        WHERE etl_batch_id = ?
        """,
        [batch_id],
    ).fetchone()
    connection.execute(
        """
        UPDATE control.etl_batch
        SET completed_at = ?, end_time = ?,
            duration_seconds = date_diff('millisecond', COALESCE(start_time, started_at), ?) / 1000.0,
            status = ?, records_processed = ?, records_loaded = ?,
            records_rejected = ?, source_count = ?, artifact_count = ?,
            warehouse_status = ?, error_message = ?
        WHERE etl_batch_id = ?
        """,
        [
            now,
            now,
            now,
            status,
            int(aggregates[0]),
            int(aggregates[1]),
            int(aggregates[2]),
            int(source_count),
            int(artifact_count),
            warehouse_status,
            error_message,
            batch_id,
        ],
    )
    row = connection.execute(
        """
        SELECT duration_seconds, records_processed, records_loaded,
               records_rejected
        FROM control.etl_batch
        WHERE etl_batch_id = ?
        """,
        [batch_id],
    ).fetchone()
    return {
        "duration_seconds": float(row[0] or 0),
        "records_processed": int(row[1] or 0),
        "records_loaded": int(row[2] or 0),
        "records_rejected": int(row[3] or 0),
    }

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4


PUBLISH_STATUSES = {
    "DRAFT",
    "VALIDATED",
    "PUBLISHED",
    "FAILED",
    "ROLLED_BACK",
}


def _now():
    return datetime.now(timezone.utc)


def _latest_status(connection, batch_id: str, target_name: str) -> str | None:
    row = connection.execute(
        """
        SELECT status
        FROM control.publish_status
        WHERE etl_batch_id = ? AND target_name = ?
        ORDER BY COALESCE(transition_at, published_at) DESC
        LIMIT 1
        """,
        [batch_id, target_name],
    ).fetchone()
    return None if row is None else str(row[0])


def _record_transition(
    connection,
    *,
    batch_id: str,
    job_id: str | None,
    target_name: str,
    status: str,
    previous_status: str | None,
    row_count: int,
    details: dict,
) -> str:
    if status not in PUBLISH_STATUSES:
        raise ValueError(f"Unsupported publish status: {status}")
    now = _now()
    publish_id = uuid4().hex
    connection.execute(
        """
        INSERT INTO control.publish_status (
            publish_id, etl_batch_id, target_name, status, row_count,
            published_at, details, job_id, previous_status, requested_at,
            validated_at, transition_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            publish_id,
            batch_id,
            target_name,
            status,
            row_count,
            now,
            json.dumps(details, default=str),
            job_id,
            previous_status,
            now if status == "DRAFT" else None,
            now if status in {"VALIDATED", "PUBLISHED"} else None,
            now,
        ],
    )
    return publish_id


def create_draft(
    connection,
    batch_id: str,
    job_id: str | None,
    *,
    target_name: str = "KRONOS_RISK_WAREHOUSE",
) -> str:
    previous = _latest_status(connection, batch_id, target_name)
    if previous is not None:
        raise RuntimeError(
            f"Publish lifecycle already exists for batch {batch_id}: {previous}."
        )
    row_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.mart_credit_risk_current"
        ).fetchone()[0]
    )
    return _record_transition(
        connection,
        batch_id=batch_id,
        job_id=job_id,
        target_name=target_name,
        status="DRAFT",
        previous_status=None,
        row_count=row_count,
        details={"physical_publish": False, "mode": "CONTROL_METADATA_ONLY"},
    )


def validate_publish(
    connection,
    batch_id: str,
    job_id: str | None,
    *,
    target_name: str = "KRONOS_RISK_WAREHOUSE",
) -> str:
    previous = _latest_status(connection, batch_id, target_name)
    if previous != "DRAFT":
        raise RuntimeError("Only a DRAFT batch may enter VALIDATED status.")
    quality = connection.execute(
        """
        SELECT quality_status, quality_score
        FROM control.etl_quality_summary
        WHERE etl_batch_id = ?
        """,
        [batch_id],
    ).fetchone()
    reconciliation_failures = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM control.reconciliation_result
            WHERE etl_batch_id = ? AND status <> 'PASS'
            """,
            [batch_id],
        ).fetchone()[0]
    )
    if quality is None or quality[0] == "FAIL" or reconciliation_failures:
        _record_transition(
            connection,
            batch_id=batch_id,
            job_id=job_id,
            target_name=target_name,
            status="FAILED",
            previous_status=previous,
            row_count=0,
            details={
                "quality": quality,
                "reconciliation_failures": reconciliation_failures,
            },
        )
        raise RuntimeError("Batch failed publish validation controls.")
    row_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.mart_credit_risk_current"
        ).fetchone()[0]
    )
    return _record_transition(
        connection,
        batch_id=batch_id,
        job_id=job_id,
        target_name=target_name,
        status="VALIDATED",
        previous_status=previous,
        row_count=row_count,
        details={
            "quality_status": quality[0],
            "quality_score": quality[1],
            "reconciliation_failures": 0,
        },
    )


def publish_validated_batch(
    connection,
    batch_id: str,
    job_id: str | None,
    *,
    target_name: str = "KRONOS_RISK_WAREHOUSE",
) -> str:
    previous = _latest_status(connection, batch_id, target_name)
    if previous != "VALIDATED":
        raise RuntimeError("Only a VALIDATED batch may be published.")
    row_count = int(
        connection.execute(
            "SELECT COUNT(*) FROM mart.mart_credit_risk_current"
        ).fetchone()[0]
    )
    return _record_transition(
        connection,
        batch_id=batch_id,
        job_id=job_id,
        target_name=target_name,
        status="PUBLISHED",
        previous_status=previous,
        row_count=row_count,
        details={
            "physical_publish": False,
            "warehouse_mode": "READ_ONLY_MIRROR",
        },
    )


def rollback_publish(
    connection,
    batch_id: str,
    job_id: str | None = None,
    *,
    target_name: str = "KRONOS_RISK_WAREHOUSE",
    reason: str = "Operator-requested metadata rollback.",
) -> str:
    previous = _latest_status(connection, batch_id, target_name)
    if previous != "PUBLISHED":
        raise RuntimeError("Only a PUBLISHED batch may be rolled back.")
    return _record_transition(
        connection,
        batch_id=batch_id,
        job_id=job_id,
        target_name=target_name,
        status="ROLLED_BACK",
        previous_status=previous,
        row_count=0,
        details={"reason": reason, "physical_data_changed": False},
    )

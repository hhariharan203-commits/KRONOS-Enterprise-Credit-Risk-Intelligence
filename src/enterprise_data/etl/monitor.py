from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def _record_metric(
    connection,
    batch_id: str,
    name: str,
    *,
    value: float | None = None,
    text: str | None = None,
    unit: str | None = None,
    details: dict | None = None,
) -> None:
    captured_at = datetime.now(timezone.utc)
    metric_id = hashlib.sha256(
        f"{batch_id}|{name}".encode("utf-8")
    ).hexdigest()[:32]
    connection.execute(
        """
        INSERT OR REPLACE INTO control.operational_metric (
            operational_metric_id, etl_batch_id, metric_name, metric_value,
            metric_text, metric_unit, details, captured_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            metric_id,
            batch_id,
            name,
            value,
            text,
            unit,
            json.dumps(details or {}, default=str),
            captured_at,
        ],
    )


def capture_operational_metrics(connection, batch_id: str) -> dict:
    job_success = connection.execute(
        """
        SELECT
            SUM(CASE WHEN status IN ('SUCCESS', 'SKIPPED') THEN 1 ELSE 0 END),
            COUNT(*)
        FROM control.etl_job_run
        """
    ).fetchone()
    batch_success = connection.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END),
            COUNT(*)
        FROM control.etl_batch
        WHERE batch_type = 'PHASE4B_CONTROL'
          AND status IN ('SUCCESS', 'FAILED', 'PARTIAL_SUCCESS', 'ABANDONED')
        """
    ).fetchone()
    averages = connection.execute(
        """
        SELECT
            AVG(duration_seconds),
            AVG(records_processed),
            AVG(records_rejected)
        FROM control.etl_batch
        WHERE batch_type = 'PHASE4B_CONTROL'
          AND status IN ('SUCCESS', 'FAILED', 'PARTIAL_SUCCESS', 'ABANDONED')
        """
    ).fetchone()
    quality = connection.execute(
        """
        SELECT quality_score, quality_status
        FROM control.etl_quality_summary
        ORDER BY evaluated_at DESC
        LIMIT 1
        """
    ).fetchone()
    publish = connection.execute(
        """
        SELECT status
        FROM control.publish_status
        ORDER BY COALESCE(transition_at, published_at) DESC
        LIMIT 1
        """
    ).fetchone()
    freshness = connection.execute(
        """
        SELECT date_diff(
            'second',
            MAX(last_seen_at),
            CURRENT_TIMESTAMP
        ) / 3600.0
        FROM control.source_asset
        """
    ).fetchone()[0]

    metrics = {
        "job_success_rate": (
            100.0 * float(job_success[0] or 0) / float(job_success[1] or 1)
        ),
        "batch_success_rate": (
            100.0 * float(batch_success[0] or 0) / float(batch_success[1] or 1)
        ),
        "average_batch_duration_seconds": float(averages[0] or 0),
        "average_records_processed": float(averages[1] or 0),
        "average_records_rejected": float(averages[2] or 0),
        "latest_dq_score": float(quality[0]) if quality else None,
        "latest_dq_status": str(quality[1]) if quality else "NOT_AVAILABLE",
        "latest_publish_status": str(publish[0]) if publish else "NOT_AVAILABLE",
        "warehouse_freshness_hours": float(freshness or 0),
    }
    for name, value in metrics.items():
        if isinstance(value, (int, float)) or value is None:
            unit = (
                "PERCENT"
                if name.endswith("_rate") or name == "latest_dq_score"
                else "HOURS"
                if name == "warehouse_freshness_hours"
                else "SECONDS"
                if name == "average_batch_duration_seconds"
                else "RECORDS"
            )
            _record_metric(
                connection,
                batch_id,
                name,
                value=None if value is None else float(value),
                unit=unit,
            )
        else:
            _record_metric(connection, batch_id, name, text=str(value))
    return metrics

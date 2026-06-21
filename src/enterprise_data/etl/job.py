from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from uuid import uuid4

from src.enterprise_data.etl.execution_context import ExecutionContext


SUPPORTED_JOB_TYPES = {
    "SOURCE_LOAD",
    "VALIDATION",
    "STAGING_LOAD",
    "CORE_LOAD",
    "MART_BUILD",
    "RECONCILIATION",
    "PUBLISH",
    "LINEAGE",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class JobResult:
    status: str
    records_processed: int = 0
    records_loaded: int = 0
    records_rejected: int = 0
    details: dict = field(default_factory=dict)
    error_message: str | None = None


@dataclass
class ETLJob:
    job_name: str
    job_type: str
    action: Callable[[ExecutionContext], dict | JobResult | None]
    upstream_jobs: tuple[str, ...] = ()
    downstream_jobs: tuple[str, ...] = ()
    job_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if self.job_type not in SUPPORTED_JOB_TYPES:
            raise ValueError(f"Unsupported ETL job type: {self.job_type}")

    def register(self, context: ExecutionContext) -> None:
        context.connection.execute(
            """
            INSERT INTO control.etl_job_run (
                job_id, etl_batch_id, job_name, job_type, upstream_jobs,
                downstream_jobs, status
            ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
            """,
            [
                self.job_id,
                context.batch_id,
                self.job_name,
                self.job_type,
                json.dumps(list(self.upstream_jobs)),
                json.dumps(list(self.downstream_jobs)),
            ],
        )
        context.state.setdefault("job_ids", {})[self.job_name] = self.job_id

    def _finish(
        self,
        context: ExecutionContext,
        result: JobResult,
        started_at: datetime | None,
    ) -> JobResult:
        ended_at = utc_now()
        duration = (
            max((ended_at - started_at).total_seconds(), 0)
            if started_at is not None
            else 0
        )
        context.connection.execute(
            """
            UPDATE control.etl_job_run
            SET end_time = ?, status = ?, duration_seconds = ?,
                records_processed = ?, records_loaded = ?,
                records_rejected = ?, error_message = ?, details_json = ?
            WHERE job_id = ?
            """,
            [
                ended_at,
                result.status,
                duration,
                int(result.records_processed),
                int(result.records_loaded),
                int(result.records_rejected),
                result.error_message,
                json.dumps(result.details, default=str),
                self.job_id,
            ],
        )
        return result

    def execute(self, context: ExecutionContext) -> JobResult:
        started_at = utc_now()
        context.connection.execute(
            """
            UPDATE control.etl_job_run
            SET start_time = ?, status = 'RUNNING'
            WHERE job_id = ?
            """,
            [started_at, self.job_id],
        )
        context.state["current_job_id"] = self.job_id
        context.state["current_job_name"] = self.job_name
        try:
            raw = self.action(context)
            if isinstance(raw, JobResult):
                result = raw
            else:
                payload = raw or {}
                result = JobResult(
                    status=str(payload.get("status", "SUCCESS")),
                    records_processed=int(payload.get("records_processed", 0)),
                    records_loaded=int(payload.get("records_loaded", 0)),
                    records_rejected=int(payload.get("records_rejected", 0)),
                    details=dict(payload.get("details", {})),
                    error_message=payload.get("error_message"),
                )
            if result.status not in {"SUCCESS", "FAILED", "PARTIAL_SUCCESS"}:
                raise ValueError(
                    f"Job {self.job_name} returned unsupported status {result.status}."
                )
        except Exception as exc:
            result = JobResult(
                status="FAILED",
                error_message=f"{type(exc).__name__}: {exc}",
            )
        return self._finish(context, result, started_at)

    def mark_not_executed(
        self,
        context: ExecutionContext,
        *,
        status: str,
        reason: str,
    ) -> JobResult:
        result = JobResult(status=status, details={"reason": reason})
        return self._finish(context, result, None)

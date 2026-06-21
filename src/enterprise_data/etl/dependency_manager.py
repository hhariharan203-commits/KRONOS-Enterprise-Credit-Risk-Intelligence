from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from src.enterprise_data.etl.execution_context import ExecutionContext
from src.enterprise_data.etl.job import ETLJob, JobResult


class DependencyValidationError(ValueError):
    """Raised when an ETL dependency graph is invalid."""


class DependencyManager:
    def __init__(self, jobs: list[ETLJob]):
        self.jobs = jobs
        self.by_name = {job.job_name: job for job in jobs}
        if len(self.by_name) != len(jobs):
            raise DependencyValidationError("ETL job names must be unique.")
        downstream = {name: [] for name in self.by_name}
        for job in jobs:
            for upstream in job.upstream_jobs:
                if upstream not in self.by_name:
                    raise DependencyValidationError(
                        f"Job {job.job_name} references missing upstream job {upstream}."
                    )
                downstream[upstream].append(job.job_name)
        for job in jobs:
            job.downstream_jobs = tuple(downstream[job.job_name])
        self._execution_order = self._topological_order()

    def _topological_order(self) -> list[str]:
        remaining = {
            job.job_name: set(job.upstream_jobs)
            for job in self.jobs
        }
        order = []
        while remaining:
            ready = sorted(
                name for name, upstream in remaining.items()
                if not upstream
            )
            if not ready:
                raise DependencyValidationError(
                    "ETL dependency graph contains a cycle."
                )
            for name in ready:
                order.append(name)
                remaining.pop(name)
                for dependencies in remaining.values():
                    dependencies.discard(name)
        return order

    @property
    def execution_order(self) -> tuple[str, ...]:
        return tuple(self._execution_order)

    def persist_dependencies(self, context: ExecutionContext) -> None:
        now = datetime.now(timezone.utc)
        for job in self.jobs:
            for upstream in job.upstream_jobs:
                dependency_id = hashlib.sha256(
                    f"{context.batch_id}|{upstream}|{job.job_name}".encode("utf-8")
                ).hexdigest()[:32]
                context.connection.execute(
                    """
                    INSERT OR IGNORE INTO control.etl_job_dependency (
                        dependency_id, etl_batch_id, upstream_job_name,
                        downstream_job_name, validation_status, created_at
                    ) VALUES (?, ?, ?, ?, 'VALID', ?)
                    """,
                    [
                        dependency_id,
                        context.batch_id,
                        upstream,
                        job.job_name,
                        now,
                    ],
                )

    def execute(
        self,
        context: ExecutionContext,
        *,
        previously_completed: set[str] | None = None,
    ) -> dict[str, JobResult]:
        completed = previously_completed or set()
        results: dict[str, JobResult] = {}
        for job in self.jobs:
            job.register(context)
        self.persist_dependencies(context)

        for job_name in self._execution_order:
            job = self.by_name[job_name]
            if job_name in completed:
                results[job_name] = job.mark_not_executed(
                    context,
                    status="SKIPPED",
                    reason="Completed successfully in the source recovery batch.",
                )
                continue
            blocked_by = [
                upstream
                for upstream in job.upstream_jobs
                if results[upstream].status not in {"SUCCESS", "SKIPPED"}
            ]
            if blocked_by:
                results[job_name] = job.mark_not_executed(
                    context,
                    status="BLOCKED",
                    reason=(
                        "Upstream dependency did not succeed: "
                        + ", ".join(blocked_by)
                    ),
                )
                continue
            results[job_name] = job.execute(context)
            context.state.setdefault("job_results", {})[job_name] = results[job_name]
        return results

from __future__ import annotations

import json
from pathlib import Path

from src.enterprise_data.artifact_registry import current_artifact_hashes
from src.enterprise_data.config import CSV_SOURCES, WAREHOUSE_DB
from src.enterprise_data.connection import (
    connect_warehouse,
    discard_working_database,
    prepare_working_database,
    publish_working_database,
)
from src.enterprise_data.etl.batch_manager import (
    finish_batch,
    initialize_etl_control_schema,
    start_batch,
)
from src.enterprise_data.etl.dependency_manager import DependencyManager
from src.enterprise_data.etl.execution_context import ExecutionContext
from src.enterprise_data.etl.job import ETLJob
from src.enterprise_data.etl.monitor import capture_operational_metrics
from src.enterprise_data.etl.publisher import (
    create_draft,
    publish_validated_batch,
    validate_publish,
)
from src.enterprise_data.etl.quality_engine import run_enterprise_quality
from src.enterprise_data.etl.recovery import (
    completed_jobs,
    inherit_completed_controls,
    record_recovery_event,
    validate_recovery_source,
)
from src.enterprise_data.lineage import build_etl_job_lineage, build_lineage
from src.enterprise_data.reconciliation import (
    run_phase4b_reconciliation,
    run_reconciliation,
)
from src.enterprise_data.schema_manager import table_exists
from src.enterprise_data.source_registry import file_sha256, source_asset_id


PHASE4A_REQUIRED_TABLES = (
    ("control", "etl_batch"),
    ("control", "source_asset"),
    ("control", "artifact_registry"),
    ("staging", "stg_scored_portfolio"),
    ("core", "fact_credit_risk_snapshot"),
    ("mart", "mart_credit_risk_current"),
    ("mart", "mart_executive_current"),
)


def _validate_phase4a_contract(connection) -> None:
    missing = [
        f"{schema}.{table}"
        for schema, table in PHASE4A_REQUIRED_TABLES
        if not table_exists(connection, schema, table)
    ]
    if missing:
        raise RuntimeError(
            "Phase 4A warehouse contract is incomplete: " + ", ".join(missing)
        )


def _current_source_asset(source) -> tuple[str, str]:
    sha256 = file_sha256(source.path)
    return source_asset_id(source.path, sha256), sha256


def _verify_sources(context: ExecutionContext) -> dict:
    connection = context.connection
    failures = []
    total_records = 0
    for source in CSV_SOURCES:
        asset_id, sha256 = _current_source_asset(source)
        row = connection.execute(
            """
            SELECT row_count
            FROM control.source_asset
            WHERE source_asset_id = ? AND relative_path = ? AND sha256 = ?
            """,
            [asset_id, source.relative_path, sha256],
        ).fetchone()
        if row is None:
            failures.append(source.relative_path)
        else:
            total_records += int(row[0] or 0)

    current_artifacts = current_artifact_hashes()
    registered_artifacts = {
        (str(path), str(sha256))
        for path, sha256 in connection.execute(
            "SELECT relative_path, sha256 FROM control.artifact_registry"
        ).fetchall()
    }
    artifact_mismatches = [
        path
        for path, sha256 in current_artifacts.items()
        if (path, sha256) not in registered_artifacts
    ]
    if failures or artifact_mismatches:
        raise RuntimeError(
            "Warehouse mirror is stale. Run Phase 4A before Phase 4B. "
            f"source_mismatches={failures}; "
            f"artifact_mismatches={artifact_mismatches}"
        )
    context.set_state("source_count", len(CSV_SOURCES))
    context.set_state("artifact_count", len(current_artifacts))
    return {
        "status": "SUCCESS",
        "records_processed": total_records,
        "records_loaded": 0,
        "details": {
            "source_count": len(CSV_SOURCES),
            "artifact_count": len(current_artifacts),
            "mirror_mode": "READ_ONLY",
        },
    }


def _verify_staging(context: ExecutionContext) -> dict:
    connection = context.connection
    total = 0
    failures = []
    for source in CSV_SOURCES:
        asset_id, _ = _current_source_asset(source)
        source_row = connection.execute(
            "SELECT row_count FROM control.source_asset WHERE source_asset_id = ?",
            [asset_id],
        ).fetchone()
        staging_rows = int(
            connection.execute(
                f"""
                SELECT COUNT(*)
                FROM staging.{source.staging_table}
                WHERE source_asset_id = ?
                """,
                [asset_id],
            ).fetchone()[0]
        )
        expected = int(source_row[0]) if source_row else -1
        total += max(expected, 0)
        if staging_rows != expected:
            failures.append(
                {
                    "source": source.relative_path,
                    "source_count": expected,
                    "staging_count": staging_rows,
                }
            )
    if failures:
        raise RuntimeError(f"Source-to-staging parity failed: {failures}")
    return {
        "status": "SUCCESS",
        "records_processed": total,
        "records_loaded": 0,
        "details": {"verified_sources": len(CSV_SOURCES)},
    }


def _verify_core(context: ExecutionContext) -> dict:
    source = next(
        item for item in CSV_SOURCES
        if item.source_name == "scored_portfolio"
    )
    asset_id, _ = _current_source_asset(source)
    staging_count = int(
        context.connection.execute(
            """
            SELECT COUNT(*)
            FROM staging.stg_scored_portfolio
            WHERE source_asset_id = ?
            """,
            [asset_id],
        ).fetchone()[0]
    )
    core_count = int(
        context.connection.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_credit_risk_snapshot
            WHERE source_asset_id = ?
            """,
            [asset_id],
        ).fetchone()[0]
    )
    borrower_count = int(
        context.connection.execute(
            "SELECT COUNT(*) FROM core.dim_borrower"
        ).fetchone()[0]
    )
    facility_count = int(
        context.connection.execute(
            "SELECT COUNT(*) FROM core.dim_credit_facility"
        ).fetchone()[0]
    )
    if not (
        staging_count == core_count
        and borrower_count >= core_count
        and facility_count >= core_count
    ):
        raise RuntimeError(
            "Core parity failed: "
            f"staging={staging_count}, core={core_count}, "
            f"borrowers={borrower_count}, facilities={facility_count}"
        )
    return {
        "status": "SUCCESS",
        "records_processed": core_count,
        "records_loaded": 0,
        "details": {
            "staging_count": staging_count,
            "core_count": core_count,
            "borrower_count": borrower_count,
            "facility_count": facility_count,
        },
    }


def _verify_marts(context: ExecutionContext) -> dict:
    tables = (
        "mart_credit_risk_current",
        "mart_ifrs9_stage_current",
        "mart_ews_current",
        "mart_model_risk",
        "mart_executive_current",
        "mart_data_quality",
    )
    counts = {}
    for table in tables:
        if not table_exists(context.connection, "mart", table):
            raise RuntimeError(f"Required Phase 4A mart is missing: mart.{table}")
        counts[table] = int(
            context.connection.execute(
                f"SELECT COUNT(*) FROM mart.{table}"
            ).fetchone()[0]
        )
    source = next(
        item for item in CSV_SOURCES
        if item.source_name == "scored_portfolio"
    )
    asset_id, _ = _current_source_asset(source)
    current_core = int(
        context.connection.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_credit_risk_snapshot
            WHERE source_asset_id = ?
            """,
            [asset_id],
        ).fetchone()[0]
    )
    if counts["mart_credit_risk_current"] != current_core:
        raise RuntimeError(
            "Current credit mart does not match the current scored portfolio."
        )
    return {
        "status": "SUCCESS",
        "records_processed": sum(counts.values()),
        "records_loaded": 0,
        "details": counts,
    }


def _run_reconciliation(context: ExecutionContext) -> dict:
    source = next(
        item for item in CSV_SOURCES
        if item.source_name == "scored_portfolio"
    )
    asset_id, sha256 = _current_source_asset(source)
    phase4a_results = run_reconciliation(
        context.connection,
        context.batch_id,
        {
            "source_asset_id": asset_id,
            "relative_path": source.relative_path,
            "sha256": sha256,
        },
    )
    result = run_phase4b_reconciliation(
        context.connection,
        context.batch_id,
        context.get_state("current_job_id"),
    )
    result["phase4a_reconciliation_count"] = len(phase4a_results)
    result["phase4a_reconciliation_failures"] = sum(
        item["status"] != "PASS"
        for item in phase4a_results
    )
    context.set_state("reconciliation", result)
    return {
        "status": (
            "SUCCESS"
            if result["status"] == "PASS"
            and result["phase4a_reconciliation_failures"] == 0
            else "FAILED"
        ),
        "records_processed": result["source_count"],
        "records_loaded": 0,
        "details": result,
    }


def _run_publish(context: ExecutionContext) -> dict:
    job_id = context.get_state("current_job_id")
    draft_id = create_draft(context.connection, context.batch_id, job_id)
    validated_id = validate_publish(context.connection, context.batch_id, job_id)
    published_id = publish_validated_batch(
        context.connection,
        context.batch_id,
        job_id,
    )
    row_count = int(
        context.connection.execute(
            "SELECT COUNT(*) FROM mart.mart_credit_risk_current"
        ).fetchone()[0]
    )
    details = {
        "draft_publish_id": draft_id,
        "validated_publish_id": validated_id,
        "published_publish_id": published_id,
        "publish_status": "PUBLISHED",
        "physical_data_changed": False,
    }
    context.set_state("publish", details)
    return {
        "status": "SUCCESS",
        "records_processed": row_count,
        "records_loaded": 0,
        "details": details,
    }


def _run_lineage(context: ExecutionContext) -> dict:
    source_results = []
    for source in CSV_SOURCES:
        asset_id, sha256 = _current_source_asset(source)
        row = context.connection.execute(
            """
            SELECT row_count, schema_json
            FROM control.source_asset
            WHERE source_asset_id = ?
            """,
            [asset_id],
        ).fetchone()
        source_results.append(
            {
                "source_asset_id": asset_id,
                "sha256": sha256,
                "row_count": int(row[0] or 0),
                "schema": json.loads(row[1]) if row and row[1] else [],
                "relative_path": source.relative_path,
                "staging_table": f"staging.{source.staging_table}",
                "status": "VERIFIED",
            }
        )
    phase4a_lineage = build_lineage(
        context.connection,
        context.batch_id,
        source_results,
    )
    result = build_etl_job_lineage(context.connection, context.batch_id)
    result["phase4a_column_lineage"] = phase4a_lineage
    result["complete"] = (
        result["complete"] and phase4a_lineage["complete"]
    )
    context.set_state("lineage", result)
    return {
        "status": "SUCCESS" if result["complete"] else "FAILED",
        "records_processed": result["edges_processed"],
        "records_loaded": 0,
        "details": result,
    }


def _with_optional_failure(job_name: str, action, fail_job_name: str | None):
    if job_name != fail_job_name:
        return action

    def fail(_context):
        raise RuntimeError(f"Controlled failure requested for {job_name}.")

    return fail


def build_default_jobs(fail_job_name: str | None = None) -> list[ETLJob]:
    definitions = (
        ("REGISTER_SOURCES", "SOURCE_LOAD", _verify_sources, ()),
        (
            "VALIDATE_QUALITY",
            "VALIDATION",
            run_enterprise_quality,
            ("REGISTER_SOURCES",),
        ),
        (
            "VERIFY_STAGING",
            "STAGING_LOAD",
            _verify_staging,
            ("VALIDATE_QUALITY",),
        ),
        (
            "VERIFY_CORE",
            "CORE_LOAD",
            _verify_core,
            ("VERIFY_STAGING",),
        ),
        (
            "VERIFY_MARTS",
            "MART_BUILD",
            _verify_marts,
            ("VERIFY_CORE",),
        ),
        (
            "RECONCILE_COUNTS",
            "RECONCILIATION",
            _run_reconciliation,
            ("VERIFY_MARTS",),
        ),
        (
            "PUBLISH_WAREHOUSE",
            "PUBLISH",
            _run_publish,
            ("RECONCILE_COUNTS",),
        ),
        (
            "CAPTURE_LINEAGE",
            "LINEAGE",
            _run_lineage,
            ("PUBLISH_WAREHOUSE",),
        ),
    )
    return [
        ETLJob(
            job_name=name,
            job_type=job_type,
            action=_with_optional_failure(name, action, fail_job_name),
            upstream_jobs=upstream,
        )
        for name, job_type, action, upstream in definitions
    ]


def _batch_status(job_results: dict) -> str:
    statuses = [result.status for result in job_results.values()]
    if statuses and all(status in {"SUCCESS", "SKIPPED"} for status in statuses):
        return "SUCCESS"
    successful = any(status in {"SUCCESS", "SKIPPED"} for status in statuses)
    return "PARTIAL_SUCCESS" if successful else "FAILED"


def run_phase4b_etl(
    database_path: Path | str = WAREHOUSE_DB,
    *,
    recovery_from_batch_id: str | None = None,
    requested_recovery_job: str | None = None,
    fail_job_name: str | None = None,
) -> dict:
    working_database = prepare_working_database(database_path)
    connection = None
    batch_id = None
    should_publish = False
    result = None
    try:
        connection = connect_warehouse(working_database.working_path)
        _validate_phase4a_contract(connection)
        initialize_etl_control_schema(connection)
        source_count = len(CSV_SOURCES)
        artifact_count = len(current_artifact_hashes())
        previous_completed: set[str] = set()
        if recovery_from_batch_id:
            validate_recovery_source(connection, recovery_from_batch_id)
            previous_completed = completed_jobs(
                connection,
                recovery_from_batch_id,
            )

        batch_id = start_batch(
            connection,
            source_count=source_count,
            artifact_count=artifact_count,
            recovery_from_batch_id=recovery_from_batch_id,
        )
        should_publish = True
        context = ExecutionContext(
            connection=connection,
            batch_id=batch_id,
            database_path=Path(database_path),
            recovery_from_batch_id=recovery_from_batch_id,
        )
        if recovery_from_batch_id:
            inherit_completed_controls(
                connection,
                recovery_from_batch_id,
                batch_id,
                previous_completed,
            )
            inherited_quality = connection.execute(
                """
                SELECT quality_score, quality_status, rule_count,
                       passed_rule_count, warning_rule_count,
                       failed_rule_count
                FROM control.etl_quality_summary
                WHERE etl_batch_id = ?
                """,
                [batch_id],
            ).fetchone()
            if inherited_quality is not None:
                context.set_state(
                    "quality",
                    {
                        "quality_score": float(inherited_quality[0]),
                        "quality_status": str(inherited_quality[1]),
                        "rule_count": int(inherited_quality[2]),
                        "passed": int(inherited_quality[3]),
                        "warnings": int(inherited_quality[4]),
                        "failed": int(inherited_quality[5]),
                        "records_rejected": 0,
                        "inherited_from_batch": recovery_from_batch_id,
                    },
                )

        manager = DependencyManager(build_default_jobs(fail_job_name))
        job_results = manager.execute(
            context,
            previously_completed=previous_completed,
        )
        status = _batch_status(job_results)
        errors = {
            name: job_result.error_message
            for name, job_result in job_results.items()
            if job_result.error_message
        }
        batch_metrics = finish_batch(
            connection,
            batch_id,
            status=status,
            source_count=context.get_state("source_count", source_count),
            artifact_count=context.get_state("artifact_count", artifact_count),
            warehouse_status="AVAILABLE",
            error_message=json.dumps(errors) if errors else None,
        )
        monitoring = capture_operational_metrics(connection, batch_id)
        if recovery_from_batch_id:
            record_recovery_event(
                connection,
                source_batch_id=recovery_from_batch_id,
                recovery_batch_id=batch_id,
                recovery_type=(
                    "RERUN_FAILED_STEP"
                    if requested_recovery_job
                    else "RESUME_FAILED_BATCH"
                ),
                requested_job_name=requested_recovery_job,
                status=status,
                details={
                    "skipped_completed_jobs": sorted(previous_completed),
                    "job_statuses": {
                        name: job_result.status
                        for name, job_result in job_results.items()
                    },
                },
            )

        publish_status = connection.execute(
            """
            SELECT status
            FROM control.publish_status
            WHERE etl_batch_id = ?
            ORDER BY COALESCE(transition_at, published_at) DESC
            LIMIT 1
            """,
            [batch_id],
        ).fetchone()
        result = {
            "status": status,
            "database_path": str(working_database.target_path),
            "etl_batch_id": batch_id,
            "recovery_from_batch_id": recovery_from_batch_id,
            "execution_order": list(manager.execution_order),
            "job_statuses": {
                name: job_result.status
                for name, job_result in job_results.items()
            },
            "batch_metrics": batch_metrics,
            "quality": context.get_state("quality"),
            "reconciliation": context.get_state("reconciliation"),
            "publish_status": publish_status[0] if publish_status else None,
            "lineage": context.get_state("lineage"),
            "monitoring": monitoring,
            "warehouse_mode": "READ_ONLY_MIRROR",
            "source_of_truth": "data/processed/scored_portfolio.csv",
        }
    except Exception as exc:
        if connection is not None and batch_id is not None:
            finish_batch(
                connection,
                batch_id,
                status="FAILED",
                source_count=len(CSV_SOURCES),
                artifact_count=0,
                warehouse_status="UNAVAILABLE",
                error_message=f"{type(exc).__name__}: {exc}",
            )
            should_publish = True
        raise
    finally:
        if connection is not None:
            connection.close()
        if should_publish:
            publish_working_database(working_database)
        discard_working_database(working_database)
    return result


def run_phase4b_etl_safe(
    database_path: Path | str = WAREHOUSE_DB,
    **kwargs,
) -> dict:
    try:
        return run_phase4b_etl(database_path=database_path, **kwargs)
    except Exception as exc:
        return {
            "status": "ETL_UNAVAILABLE",
            "database_path": str(Path(database_path)),
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": (
                "NONE; KRONOS dashboards and CSV workflows remain authoritative."
            ),
        }


if __name__ == "__main__":
    print(json.dumps(run_phase4b_etl(), indent=2, default=str))

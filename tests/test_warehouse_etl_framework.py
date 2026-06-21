from __future__ import annotations

import shutil

import pytest

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.connection import connect_warehouse
from src.enterprise_data.etl.recovery import resume_failed_batch
from src.enterprise_data.etl.reject_handler import log_reject
from src.enterprise_data.etl.scheduler import run_phase4b_etl


@pytest.fixture(scope="module")
def successful_etl(tmp_path_factory):
    database = tmp_path_factory.mktemp("phase4b") / "successful.duckdb"
    shutil.copy2(WAREHOUSE_DB, database)
    result = run_phase4b_etl(database)
    assert result["status"] == "SUCCESS"
    return database, result


def test_batch_creation_and_job_execution(successful_etl) -> None:
    database, result = successful_etl
    connection = connect_warehouse(database, read_only=True)
    try:
        batch = connection.execute(
            """
            SELECT start_time, end_time, duration_seconds, status,
                   records_processed, records_loaded, records_rejected,
                   source_count, artifact_count, warehouse_status
            FROM control.etl_batch
            WHERE etl_batch_id = ?
            """,
            [result["etl_batch_id"]],
        ).fetchone()
        assert batch[0] is not None
        assert batch[1] is not None
        assert batch[2] >= 0
        assert batch[3] == "SUCCESS"
        assert batch[4] > 0
        assert batch[5] == 0
        assert batch[6] == 0
        assert batch[7] == 18
        assert batch[8] >= 53
        assert batch[9] == "AVAILABLE"

        jobs = connection.execute(
            """
            SELECT job_name, job_type, status, duration_seconds
            FROM control.etl_job_run
            WHERE etl_batch_id = ?
            ORDER BY start_time
            """,
            [result["etl_batch_id"]],
        ).fetchall()
        assert len(jobs) == 8
        assert all(row[2] == "SUCCESS" for row in jobs)
        assert all(row[3] >= 0 for row in jobs)
    finally:
        connection.close()


def test_quality_rules_and_reject_handling(successful_etl) -> None:
    database, result = successful_etl
    connection = connect_warehouse(database)
    try:
        quality = connection.execute(
            """
            SELECT quality_score, quality_status, rule_count,
                   failed_rule_count
            FROM control.etl_quality_summary
            WHERE etl_batch_id = ?
            """,
            [result["etl_batch_id"]],
        ).fetchone()
        assert quality == (100.0, "PASS", 11, 0)

        job_id = connection.execute(
            """
            SELECT job_id
            FROM control.etl_job_run
            WHERE etl_batch_id = ? AND job_name = 'VALIDATE_QUALITY'
            """,
            [result["etl_batch_id"]],
        ).fetchone()[0]
        reject_id = log_reject(
            connection,
            batch_id=result["etl_batch_id"],
            job_id=job_id,
            source_asset_id=None,
            source_name="unit_test_source",
            record_identifier="TEST-1",
            column_name="pd_score",
            invalid_value="1.25",
            rejection_reason="Test-only reject metadata verification.",
        )
        reject = connection.execute(
            """
            SELECT etl_batch_id, job_id, source_name, record_identifier,
                   column_name, invalid_value, rejection_reason,
                   rejected_timestamp
            FROM control.rejected_record
            WHERE rejected_record_id = ?
            """,
            [reject_id],
        ).fetchone()
        assert reject[:7] == (
            result["etl_batch_id"],
            job_id,
            "unit_test_source",
            "TEST-1",
            "pd_score",
            "1.25",
            "Test-only reject metadata verification.",
        )
        assert reject[7] is not None
    finally:
        connection.close()


def test_publish_lifecycle_and_reconciliation(successful_etl) -> None:
    database, result = successful_etl
    connection = connect_warehouse(database, read_only=True)
    try:
        lifecycle = [
            row[0]
            for row in connection.execute(
                """
                SELECT status
                FROM control.publish_status
                WHERE etl_batch_id = ?
                ORDER BY transition_at
                """,
                [result["etl_batch_id"]],
            ).fetchall()
        ]
        assert lifecycle == ["DRAFT", "VALIDATED", "PUBLISHED"]

        reconciliation = connection.execute(
            """
            SELECT source_count, staging_count, core_count, mart_count,
                   variance, status
            FROM control.reconciliation_result
            WHERE etl_batch_id = ?
              AND reconciliation_name = 'phase4b:end_to_end_row_parity'
            """,
            [result["etl_batch_id"]],
        ).fetchone()
        assert reconciliation == (50_000, 50_000, 50_000, 50_000, 0.0, "PASS")
    finally:
        connection.close()


def test_monitoring_metrics_and_lineage_enhancement(successful_etl) -> None:
    database, result = successful_etl
    connection = connect_warehouse(database, read_only=True)
    try:
        metric_names = {
            row[0]
            for row in connection.execute(
                """
                SELECT metric_name
                FROM control.operational_metric
                WHERE etl_batch_id = ?
                """,
                [result["etl_batch_id"]],
            ).fetchall()
        }
        assert {
            "job_success_rate",
            "batch_success_rate",
            "average_batch_duration_seconds",
            "average_records_processed",
            "average_records_rejected",
            "latest_dq_score",
            "latest_dq_status",
            "latest_publish_status",
            "warehouse_freshness_hours",
        }.issubset(metric_names)

        batch_edges = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.lineage_edge
            WHERE etl_batch_id = ?
              AND transformation_name = 'BATCH_EXECUTES_JOB'
            """,
            [result["etl_batch_id"]],
        ).fetchone()[0]
        object_edges = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.lineage_edge
            WHERE etl_batch_id = ?
              AND transformation_name LIKE 'JOB_%_OBJECT'
            """,
            [result["etl_batch_id"]],
        ).fetchone()[0]
        assert batch_edges == 8
        assert object_edges > 0
    finally:
        connection.close()


def test_idempotency_preserved(successful_etl) -> None:
    database, _ = successful_etl
    connection = connect_warehouse(database, read_only=True)
    try:
        before = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM core.fact_credit_risk_snapshot),
                (SELECT COUNT(*) FROM core.fact_market_observation),
                (SELECT COUNT(*) FROM mart.mart_credit_risk_current)
            """
        ).fetchone()
    finally:
        connection.close()

    repeat = run_phase4b_etl(database)
    assert repeat["status"] == "SUCCESS"
    assert repeat["batch_metrics"]["records_loaded"] == 0

    connection = connect_warehouse(database, read_only=True)
    try:
        after = connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM core.fact_credit_risk_snapshot),
                (SELECT COUNT(*) FROM core.fact_market_observation),
                (SELECT COUNT(*) FROM mart.mart_credit_risk_current)
            """
        ).fetchone()
        assert after == before
    finally:
        connection.close()


def test_recovery_skips_completed_steps_and_resumes(tmp_path) -> None:
    database = tmp_path / "recovery.duckdb"
    shutil.copy2(WAREHOUSE_DB, database)
    before = connect_warehouse(database, read_only=True)
    try:
        fact_count = before.execute(
            "SELECT COUNT(*) FROM core.fact_credit_risk_snapshot"
        ).fetchone()[0]
    finally:
        before.close()

    failed = run_phase4b_etl(database, fail_job_name="VERIFY_CORE")
    assert failed["status"] == "PARTIAL_SUCCESS"
    assert failed["job_statuses"]["VERIFY_CORE"] == "FAILED"
    assert failed["job_statuses"]["VERIFY_MARTS"] == "BLOCKED"

    recovered = resume_failed_batch(failed["etl_batch_id"], database)
    assert recovered["status"] == "SUCCESS"
    assert recovered["job_statuses"]["REGISTER_SOURCES"] == "SKIPPED"
    assert recovered["job_statuses"]["VALIDATE_QUALITY"] == "SKIPPED"
    assert recovered["job_statuses"]["VERIFY_STAGING"] == "SKIPPED"
    assert recovered["job_statuses"]["VERIFY_CORE"] == "SUCCESS"
    assert recovered["quality"]["quality_status"] == "PASS"

    connection = connect_warehouse(database, read_only=True)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM core.fact_credit_risk_snapshot"
        ).fetchone()[0] == fact_count
        event = connection.execute(
            """
            SELECT recovery_type, status
            FROM control.etl_recovery_event
            WHERE recovery_batch_id = ?
            """,
            [recovered["etl_batch_id"]],
        ).fetchone()
        assert event == ("RESUME_FAILED_BATCH", "SUCCESS")
    finally:
        connection.close()

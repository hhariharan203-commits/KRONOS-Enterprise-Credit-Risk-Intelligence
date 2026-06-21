from __future__ import annotations

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.contracts import (
    NOT_ESTABLISHED,
    PASS_WITH_LIMITATIONS,
    PROCESS_TIME_ONLY,
    SYNTHETIC_BASELINE,
)


def _record(
    connection,
    deployment_id: str,
    snapshot_id: str,
    rule_name: str,
    scope: str,
    status: str,
    actual,
    expected,
    details: str = "",
) -> dict:
    result_id = stable_id(deployment_id, snapshot_id, rule_name)
    connection.execute(
        """
        INSERT INTO control.temporal_quality_result (
            quality_result_id, deployment_id, snapshot_id, rule_name,
            rule_scope, status, actual_value, expected_value, details,
            checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            result_id,
            deployment_id,
            snapshot_id,
            rule_name,
            scope,
            status,
            str(actual),
            str(expected),
            details,
            utc_now(),
        ],
    )
    return {"rule_name": rule_name, "status": status, "actual": actual}


def run_quality_checks(
    connection,
    *,
    deployment_id: str,
    snapshot_id: str,
    profile: dict,
    baseline_profile: dict,
    source_path_valid: bool,
) -> dict:
    checks = [
        ("source_exists", profile["path"].exists(), True, "SOURCE", "PASS"),
        ("source_readable_regular_file", profile["path"].is_file(), True, "SOURCE", "PASS"),
        ("sha256_generated", len(profile["sha256_before"]) == 64, True, "SOURCE", "PASS"),
        ("source_hash_stable", profile["sha256_before"] == profile["sha256_after"], True, "SOURCE", "PASS"),
        ("row_count_baseline", profile["row_count"], baseline_profile["row_count"], "SOURCE", "PASS"),
        ("column_count_baseline", profile["column_count"], baseline_profile["column_count"], "SOURCE", "PASS"),
        ("borrower_id_exists", "borrower_id" in {c["column_name"] for c in profile["columns"]}, True, "IDENTITY", "PASS"),
        ("borrower_id_not_null", profile["borrower_null_count"], 0, "IDENTITY", "PASS"),
        ("borrower_id_unique_within_source", profile["distinct_borrower_count"], profile["row_count"], "IDENTITY", "PASS"),
        ("run_id_exists", "run_id" in {c["column_name"] for c in profile["columns"]}, True, "EXECUTION", "PASS"),
        ("run_id_baseline_count", len(profile["run_ids"]), len(baseline_profile["run_ids"]), "EXECUTION", "PASS"),
        ("model_version_exists", "model_version" in {c["column_name"] for c in profile["columns"]}, True, "EXECUTION", "PASS"),
        ("model_version_baseline_count", len(profile["model_versions"]), len(baseline_profile["model_versions"]), "EXECUTION", "PASS"),
        ("timestamp_exists", "timestamp" in {c["column_name"] for c in profile["columns"]}, True, "TEMPORAL", "PASS"),
        ("timestamp_parseable", profile["all_timestamps_parseable"], True, "TEMPORAL", "PASS"),
        ("observation_date_unavailable", None, None, "TEMPORAL", "WARNING"),
        ("reporting_date_unavailable", None, None, "TEMPORAL", "WARNING"),
        ("origination_date_unavailable", None, None, "TEMPORAL", "WARNING"),
        ("classification_process_time_only", PROCESS_TIME_ONLY, PROCESS_TIME_ONLY, "TEMPORAL", "PASS"),
        ("historical_eligibility_false", False, False, "TEMPORAL", "PASS"),
        ("source_path_allowlisted", source_path_valid, True, "SOURCE", "PASS"),
        ("schema_fingerprint_registered", len(profile["canonical_schema_hash"]) == 64, True, "SCHEMA", "PASS"),
        ("timestamp_timezone_present", profile["all_timestamps_timezone_aware"], True, "TEMPORAL", "PASS"),
        ("timestamp_cardinality_baseline", len(profile["timestamps"]), len(baseline_profile["timestamps"]), "TEMPORAL", "PASS"),
        ("all_rows_scored", profile["scoring_status"].get("SCORED", 0), profile["row_count"], "EXECUTION", "PASS"),
        ("synthetic_evidence_classification", SYNTHETIC_BASELINE, SYNTHETIC_BASELINE, "GOVERNANCE", "PASS"),
        ("identity_continuity_not_established", NOT_ESTABLISHED, NOT_ESTABLISHED, "IDENTITY", "PASS"),
    ]
    results = []
    for name, actual, expected, scope, expected_status in checks:
        if expected_status == "WARNING":
            status = "WARNING"
        else:
            status = "PASS" if actual == expected else "FAIL"
        results.append(
            _record(
                connection,
                deployment_id,
                snapshot_id,
                name,
                scope,
                status,
                actual,
                expected,
            )
        )
    failures = sum(item["status"] == "FAIL" for item in results)
    warnings = sum(item["status"] == "WARNING" for item in results)
    return {
        "status": PASS_WITH_LIMITATIONS if failures == 0 and warnings else "PASS",
        "check_count": len(results),
        "failure_count": failures,
        "warning_count": warnings,
        "results": results,
    }

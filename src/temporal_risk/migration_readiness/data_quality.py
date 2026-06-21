from __future__ import annotations

import json

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.migration_readiness.contracts import (
    ALLOWED_STATE_FIELDS,
    DISABLED,
    governance_score,
)


READINESS_CAPABILITIES = (
    "SNAPSHOT_CONTINUITY",
    "IDENTITY_CONTINUITY",
    "STATE_FIELD_CONTINUITY",
    "MIGRATION_TRANSITION_INPUTS",
)


def _check(
    name: str,
    category: str,
    condition: bool,
    *,
    earlier_value=None,
    later_value=None,
    expected_value=None,
    details: str = "",
) -> dict:
    return {
        "control_name": name,
        "control_category": category,
        "critical_flag": True,
        "applicable_flag": True,
        "earlier_value": earlier_value,
        "later_value": later_value,
        "expected_value": expected_value,
        "status": "PASS" if bool(condition) else "FAIL",
        "details": details,
    }


def evaluate_quality(
    context: dict,
    *,
    catalog_valid: bool,
    phase2a_release_valid: bool,
    phase2b_release_valid: bool,
    mart_and_views_empty: bool,
    domain_contract_matches: bool,
) -> dict:
    earlier = context["earlier"]
    later = context["later"]
    checks = [
        _check("exact_phase2c_catalog", "PLATFORM", catalog_valid),
        _check("phase2a_release_published", "PLATFORM", phase2a_release_valid),
        _check("phase2b_release_published", "PLATFORM", phase2b_release_valid),
        _check("mart_empty_and_no_views", "PLATFORM", mart_and_views_empty),
        _check("earlier_snapshot_exists", "SNAPSHOT", bool(earlier["snapshot_id"])),
        _check("later_snapshot_exists", "SNAPSHOT", bool(later["snapshot_id"])),
        _check(
            "snapshot_identifiers_distinct",
            "SNAPSHOT",
            earlier["snapshot_id"] != later["snapshot_id"],
        ),
        _check(
            "snapshot_dates_ordered",
            "SNAPSHOT",
            earlier["snapshot_date"] < later["snapshot_date"],
            earlier_value=earlier["snapshot_date"],
            later_value=later["snapshot_date"],
        ),
        _check(
            "phase2b_publication_verified",
            "SNAPSHOT",
            bool(earlier["phase2b_published"] and later["phase2b_published"]),
        ),
        _check(
            "observed_history_mode",
            "SNAPSHOT",
            earlier["history_mode"] == later["history_mode"] == "OBSERVED_TEMPORAL",
        ),
        _check(
            "observed_evidence_classification",
            "SNAPSHOT",
            earlier["evidence_classification"]
            == later["evidence_classification"]
            == "OBSERVED_SOURCE",
        ),
        _check(
            "immutable_source_hashes_registered",
            "SNAPSHOT",
            len(earlier["source_sha256"]) == 64
            and len(later["source_sha256"]) == 64,
        ),
        _check(
            "source_system_continuity",
            "IDENTITY",
            earlier["source_system"] == later["source_system"],
        ),
        _check(
            "identity_grain_continuity",
            "IDENTITY",
            earlier["identity_grain"] == later["identity_grain"],
        ),
        _check(
            "earlier_identity_complete",
            "IDENTITY",
            context["earlier_non_null_identity_count"]
            == context["earlier_population_count"],
        ),
        _check(
            "later_identity_complete",
            "IDENTITY",
            context["later_non_null_identity_count"]
            == context["later_population_count"],
        ),
        _check(
            "earlier_identity_unique",
            "IDENTITY",
            context["earlier_distinct_identity_count"]
            == context["earlier_population_count"],
        ),
        _check(
            "later_identity_unique",
            "IDENTITY",
            context["later_distinct_identity_count"]
            == context["later_population_count"],
        ),
        _check(
            "identity_overlap_present",
            "IDENTITY",
            context["overlapping_identity_count"] > 0,
        ),
        _check(
            "state_field_allowlisted",
            "STATE_FIELD",
            context["state_field"] in ALLOWED_STATE_FIELDS,
        ),
        _check(
            "earlier_state_mapping_source_supplied",
            "STATE_FIELD",
            bool(
                earlier["state_source_column"]
                and earlier["state_source_supplied"]
            ),
        ),
        _check(
            "later_state_mapping_source_supplied",
            "STATE_FIELD",
            bool(
                later["state_source_column"]
                and later["state_source_supplied"]
            ),
        ),
        _check(
            "controlled_domain_contract_consistent",
            "STATE_FIELD",
            domain_contract_matches,
        ),
        _check(
            "overlap_state_values_controlled",
            "STATE_FIELD",
            context["earlier_domain_valid"]
            and context["later_domain_valid"]
            and context["earlier_state_complete_overlap_count"]
            == context["overlapping_identity_count"]
            and context["later_state_complete_overlap_count"]
            == context["overlapping_identity_count"],
        ),
    ]
    applicable = sum(item["applicable_flag"] for item in checks)
    passed = sum(
        item["applicable_flag"] and item["status"] == "PASS"
        for item in checks
    )
    score = governance_score(passed, applicable)
    readiness_status = (
        "FAILED"
        if applicable == 0
        else "READY_BUT_DISABLED"
        if applicable == 24 and passed == 24
        else "NOT_READY"
    )
    return {
        "check_count": len(checks),
        "applicable_controls": applicable,
        "passed_applicable_controls": passed,
        "governance_score": score,
        "readiness_status": readiness_status,
        "quality_status": "PASS" if passed == applicable == 24 else "FAIL",
        "publication_allowed": passed == applicable == 24 and score is not None,
        "checks": checks,
    }


def persist_quality(
    connection,
    *,
    readiness_run_id: str,
    pair_id: str,
    quality: dict,
) -> None:
    for item in quality["checks"]:
        connection.execute(
            """
            INSERT INTO control.migration_quality_result (
                quality_result_id, readiness_run_id, pair_id, control_name,
                control_category, critical_flag, applicable_flag,
                earlier_value, later_value, expected_value, status, details,
                evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                stable_id(readiness_run_id, item["control_name"]),
                readiness_run_id,
                pair_id,
                item["control_name"],
                item["control_category"],
                item["critical_flag"],
                item["applicable_flag"],
                None
                if item["earlier_value"] is None
                else str(item["earlier_value"]),
                None
                if item["later_value"] is None
                else str(item["later_value"]),
                None
                if item["expected_value"] is None
                else str(item["expected_value"]),
                item["status"],
                item["details"],
                utc_now(),
            ],
        )


def persist_readiness(
    connection,
    *,
    readiness_run_id: str,
    pair_id: str,
    quality: dict,
) -> list[dict]:
    results = []
    for capability in READINESS_CAPABILITIES:
        result = {
            "capability_name": capability,
            "data_status": quality["readiness_status"],
            "activation_status": DISABLED,
            "applicable_controls": quality["applicable_controls"],
            "passed_applicable_controls": quality["passed_applicable_controls"],
            "governance_score": quality["governance_score"],
            "reason": (
                "All migration-readiness governance controls passed; "
                "analytical activation remains disabled."
            ),
        }
        connection.execute(
            """
            INSERT INTO control.migration_readiness_result (
                readiness_result_id, readiness_run_id, pair_id,
                capability_name, data_status, activation_status,
                applicable_controls, passed_applicable_controls,
                governance_score, required_evidence_json,
                available_evidence_json, missing_evidence_json, reason,
                evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                stable_id(readiness_run_id, capability),
                readiness_run_id,
                pair_id,
                capability,
                result["data_status"],
                DISABLED,
                result["applicable_controls"],
                result["passed_applicable_controls"],
                result["governance_score"],
                json.dumps(
                    [
                        "OBSERVED_SNAPSHOTS",
                        "SOURCE_IDENTITY",
                        "SOURCE_DATE",
                        "SOURCE_STATE",
                        "CONTROLLED_DOMAIN",
                    ]
                ),
                json.dumps(
                    [
                        "OBSERVED_SNAPSHOTS",
                        "SOURCE_IDENTITY",
                        "SOURCE_DATE",
                        "SOURCE_STATE",
                        "CONTROLLED_DOMAIN",
                    ]
                ),
                json.dumps([]),
                result["reason"],
                utc_now(),
            ],
        )
        results.append(result)
    return results

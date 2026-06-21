from __future__ import annotations

from src.temporal_risk.audit import stable_id, utc_now


def _result(
    name: str,
    earlier_value,
    later_value,
    expected_value,
    condition: bool,
    details: str,
) -> dict:
    return {
        "reconciliation_name": name,
        "earlier_value": earlier_value,
        "later_value": later_value,
        "expected_value": expected_value,
        "difference": 0.0 if condition else 1.0,
        "tolerance": 0.0,
        "status": "PASS" if condition else "FAIL",
        "details": details,
    }


def evaluate_reconciliations(context: dict) -> dict:
    overlap = context["overlapping_identity_count"]
    results = [
        _result(
            "earlier_snapshot_registry_count",
            context["earlier_registry_count"],
            None,
            1,
            context["earlier_registry_count"] == 1,
            "Earlier governed snapshot registry parity.",
        ),
        _result(
            "later_snapshot_registry_count",
            None,
            context["later_registry_count"],
            1,
            context["later_registry_count"] == 1,
            "Later governed snapshot registry parity.",
        ),
        _result(
            "earlier_accepted_population",
            context["earlier_records_accepted"],
            context["earlier_population_count"],
            context["earlier_population_count"],
            context["earlier_records_accepted"]
            == context["earlier_population_count"],
            "Earlier Phase 2B accepted population parity.",
        ),
        _result(
            "later_accepted_population",
            context["later_records_accepted"],
            context["later_population_count"],
            context["later_population_count"],
            context["later_records_accepted"]
            == context["later_population_count"],
            "Later Phase 2B accepted population parity.",
        ),
        _result(
            "earlier_distinct_identity_population",
            context["earlier_distinct_identity_count"],
            context["earlier_population_count"],
            context["earlier_population_count"],
            context["earlier_distinct_identity_count"]
            == context["earlier_population_count"],
            "Earlier identity-grain uniqueness parity.",
        ),
        _result(
            "later_distinct_identity_population",
            context["later_distinct_identity_count"],
            context["later_population_count"],
            context["later_population_count"],
            context["later_distinct_identity_count"]
            == context["later_population_count"],
            "Later identity-grain uniqueness parity.",
        ),
        _result(
            "overlap_within_earlier_population",
            overlap,
            context["earlier_population_count"],
            context["earlier_population_count"],
            overlap <= context["earlier_population_count"],
            "Overlap cannot exceed earlier population.",
        ),
        _result(
            "overlap_within_later_population",
            overlap,
            context["later_population_count"],
            context["later_population_count"],
            overlap <= context["later_population_count"],
            "Overlap cannot exceed later population.",
        ),
        _result(
            "earlier_overlap_state_completeness",
            context["earlier_state_complete_overlap_count"],
            context["earlier_state_missing_overlap_count"],
            overlap,
            context["earlier_state_complete_overlap_count"]
            + context["earlier_state_missing_overlap_count"]
            == overlap,
            "Earlier overlap completeness parity.",
        ),
        _result(
            "later_overlap_state_completeness",
            context["later_state_complete_overlap_count"],
            context["later_state_missing_overlap_count"],
            overlap,
            context["later_state_complete_overlap_count"]
            + context["later_state_missing_overlap_count"]
            == overlap,
            "Later overlap completeness parity.",
        ),
    ]
    return {
        "reconciliation_count": len(results),
        "failure_count": sum(item["status"] == "FAIL" for item in results),
        "status": (
            "PASS"
            if all(item["status"] == "PASS" for item in results)
            else "FAIL"
        ),
        "results": results,
    }


def persist_reconciliations(
    connection,
    *,
    readiness_run_id: str,
    pair_id: str,
    reconciliation: dict,
) -> None:
    for item in reconciliation["results"]:
        connection.execute(
            """
            INSERT INTO control.migration_reconciliation_result (
                reconciliation_result_id, readiness_run_id, pair_id,
                reconciliation_name, earlier_value, later_value,
                expected_value, difference, tolerance, status, details,
                reconciled_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                stable_id(readiness_run_id, item["reconciliation_name"]),
                readiness_run_id,
                pair_id,
                item["reconciliation_name"],
                None
                if item["earlier_value"] is None
                else str(item["earlier_value"]),
                None
                if item["later_value"] is None
                else str(item["later_value"]),
                None
                if item["expected_value"] is None
                else str(item["expected_value"]),
                item["difference"],
                item["tolerance"],
                item["status"],
                item["details"],
                utc_now(),
            ],
        )

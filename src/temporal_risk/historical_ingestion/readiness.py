from __future__ import annotations

import json

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.historical_ingestion.contracts import (
    DISABLED,
    OBSERVED_TEMPORAL,
    SIMULATED_TEMPORAL,
)


CAPABILITIES = (
    "HISTORICAL_STORAGE",
    "MIGRATION_INPUTS",
    "ROLL_RATE_INPUTS",
    "VINTAGE_INPUTS",
    "TRUE_OOT_INPUTS",
    "IFRS9_TEMPORAL_INPUTS",
)


def _available(mapped: set[str], fields: tuple[str, ...]) -> tuple[list[str], list[str]]:
    present = sorted(set(fields).intersection(mapped))
    missing = sorted(set(fields).difference(mapped))
    return present, missing


def evaluate_readiness(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    manifest: dict,
    mapped_fields: set[str],
    storage_ready: bool,
) -> list[dict]:
    observed = manifest["history_mode"] == OBSERVED_TEMPORAL
    simulated = manifest["history_mode"] == SIMULATED_TEMPORAL
    prior_snapshots = int(
        connection.execute(
            """
            SELECT COUNT(*) FROM core.dim_historical_snapshot
            WHERE history_mode = 'OBSERVED_TEMPORAL' AND snapshot_id <> ?
            """
            ,
            [snapshot_id],
        ).fetchone()[0]
    )
    entity_overlap = int(
        connection.execute(
            """
            SELECT COUNT(DISTINCT current_fact.entity_key)
            FROM core.fact_historical_credit_observation current_fact
            JOIN core.fact_historical_credit_observation prior_fact
              ON current_fact.entity_key = prior_fact.entity_key
             AND prior_fact.snapshot_id <> current_fact.snapshot_id
            JOIN core.dim_historical_snapshot prior_snapshot
              ON prior_snapshot.snapshot_id = prior_fact.snapshot_id
             AND prior_snapshot.history_mode = 'OBSERVED_TEMPORAL'
            WHERE current_fact.snapshot_id = ?
            """,
            [snapshot_id],
        ).fetchone()[0]
    )
    facility_overlap = int(
        connection.execute(
            """
            SELECT COUNT(DISTINCT current_fact.facility_key)
            FROM core.fact_historical_credit_observation current_fact
            JOIN core.fact_historical_credit_observation prior_fact
              ON current_fact.facility_key = prior_fact.facility_key
             AND prior_fact.snapshot_id <> current_fact.snapshot_id
            JOIN core.dim_historical_snapshot prior_snapshot
              ON prior_snapshot.snapshot_id = prior_fact.snapshot_id
             AND prior_snapshot.history_mode = 'OBSERVED_TEMPORAL'
            WHERE current_fact.snapshot_id = ?
              AND current_fact.facility_key IS NOT NULL
            """,
            [snapshot_id],
        ).fetchone()[0]
    )
    dates = connection.execute(
        """
        SELECT
            (SELECT snapshot_date FROM core.dim_historical_snapshot
             WHERE snapshot_id = ?),
            (SELECT MAX(snapshot_date) FROM core.dim_historical_snapshot
             WHERE history_mode = 'OBSERVED_TEMPORAL' AND snapshot_id <> ?)
        """,
        [snapshot_id, snapshot_id],
    ).fetchone()
    consecutive_dates = bool(
        dates[0]
        and dates[1]
        and 0 < (dates[0] - dates[1]).days <= 62
    )
    definitions = {
        "HISTORICAL_STORAGE": (
            ("source_entity_id", "observation_date"),
            "READY_BUT_DISABLED" if storage_ready else "NOT_READY",
            "Valid source-supplied identity and temporal storage contract."
            if storage_ready
            else "Historical storage controls did not pass.",
        ),
        "MIGRATION_INPUTS": (
            ("source_entity_id", "risk_grade"),
            "READY_BUT_DISABLED"
            if observed
            and prior_snapshots >= 1
            and entity_overlap > 0
            and "risk_grade" in mapped_fields
            else "NOT_ELIGIBLE"
            if simulated
            else "NOT_READY",
            "Readiness evidence only; no transition matrix is generated.",
        ),
        "ROLL_RATE_INPUTS": (
            ("source_facility_id", "delinquency_state"),
            "READY_BUT_DISABLED"
            if observed
            and prior_snapshots >= 1
            and facility_overlap > 0
            and consecutive_dates
            and {"source_facility_id", "delinquency_state"}.issubset(mapped_fields)
            else "NOT_ELIGIBLE"
            if simulated
            else "NOT_READY",
            "Readiness evidence only; no roll rate is generated.",
        ),
        "VINTAGE_INPUTS": (
            ("origination_date", "observation_date"),
            "READY_BUT_DISABLED"
            if observed
            and prior_snapshots >= 2
            and entity_overlap > 0
            and {"origination_date", "observation_date"}.issubset(mapped_fields)
            else "NOT_ELIGIBLE"
            if simulated
            else "NOT_READY",
            "Readiness evidence only; no vintage cohort is generated.",
        ),
        "TRUE_OOT_INPUTS": (
            ("observation_date", "default_outcome", "source_model_version"),
            "READY_BUT_DISABLED"
            if observed
            and prior_snapshots >= 1
            and entity_overlap > 0
            and {
                "observation_date",
                "default_outcome",
                "source_model_version",
            }.issubset(mapped_fields)
            and bool(manifest.get("model_freeze_metadata"))
            and bool(manifest.get("point_in_time_feature_metadata"))
            and bool(manifest.get("outcome_maturity_metadata"))
            else "NOT_ELIGIBLE"
            if simulated
            else "NOT_READY",
            "Readiness evidence only; no model validation is executed.",
        ),
        "IFRS9_TEMPORAL_INPUTS": (
            (
                "reporting_date",
                "origination_date",
                "maturity_date",
                "default_date",
                "cure_date",
                "recovery_date",
            ),
            "NOT_ELIGIBLE" if simulated else "NOT_READY",
            (
                "Phase 2B does not contain contractual cash-flow, discounting, "
                "scenario, staging, or ECL architecture."
            ),
        ),
    }
    results = []
    for capability in CAPABILITIES:
        required, status, reason = definitions[capability]
        available, missing = _available(mapped_fields, required)
        result = {
            "capability_name": capability,
            "data_status": status,
            "activation_status": DISABLED,
            "required_fields": list(required),
            "available_fields": available,
            "missing_fields": missing,
            "reason": reason,
        }
        result_id = stable_id(ingestion_batch_id, snapshot_id, capability)
        connection.execute(
            """
            INSERT INTO control.data_readiness_result (
                readiness_result_id, ingestion_batch_id, snapshot_id,
                capability_name, data_status, activation_status,
                required_fields_json, available_fields_json,
                missing_fields_json, history_mode, evidence_classification,
                reason, evaluated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                result_id,
                ingestion_batch_id,
                snapshot_id,
                capability,
                status,
                DISABLED,
                json.dumps(list(required)),
                json.dumps(available),
                json.dumps(missing),
                manifest["history_mode"],
                manifest["evidence_classification"],
                reason,
                utc_now(),
            ],
        )
        results.append(result)
    return results

from __future__ import annotations

import hashlib
import json

import pandas as pd

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.contracts import (
    NOT_ESTABLISHED,
    PROCESS_TIMESTAMP_ONLY,
    PROCESS_TIME_ONLY,
    SYNTHETIC_BASELINE,
    TEMPORAL_CONTRACTS,
)


LIMITATIONS = (
    "The source contains one synthetic current-state scoring run. It does not "
    "contain observed borrower history, observation dates, reporting dates, "
    "origination dates, or established longitudinal identity and cannot "
    "support migration, vintage, roll-rate, true OOT, temporal IFRS9, or "
    "observed historical-trend claims."
)


def inventory_identity_value(values: list[str]) -> str | None:
    normalized = sorted(str(value) for value in values)
    if not normalized:
        return None
    if len(normalized) == 1:
        return normalized[0]
    return json.dumps(normalized, separators=(",", ":"))


def register_reference_data(connection) -> None:
    classifications = (
        (
            "OBSERVED_TEMPORAL",
            "Source-supplied observed historical time.",
            True,
            False,
        ),
        (
            "SIMULATED_TEMPORAL",
            "Explicitly simulated historical time.",
            False,
            False,
        ),
        (
            "PROCESS_TIME_ONLY",
            "Execution time that is not an observation date.",
            False,
            False,
        ),
        ("UNKNOWN", "Temporal provenance is unknown.", False, False),
    )
    for code, description, historical, regulatory in classifications:
        connection.execute(
            """
            INSERT OR IGNORE INTO reference.dim_temporal_classification
            VALUES (?, ?, ?, ?, TRUE)
            """,
            [code, description, historical, regulatory],
        )
    statuses = (
        ("DISCOVERED", False),
        ("REGISTERED", False),
        ("VALIDATED", False),
        ("REJECTED", True),
        ("PUBLISHED", True),
        ("FAILED", True),
        ("ROLLED_BACK", True),
    )
    for code, terminal in statuses:
        connection.execute(
            """
            INSERT OR IGNORE INTO reference.dim_snapshot_status
            VALUES (?, ?, ?, TRUE)
            """,
            [code, code.replace("_", " ").title(), terminal],
        )


def register_contracts(connection) -> dict[str, dict]:
    registered = {}
    now = utc_now()
    for definition in TEMPORAL_CONTRACTS:
        canonical = {
            "contract_name": definition.contract_name,
            "contract_version": definition.contract_version,
            "description": definition.description,
            "required_fields": definition.required_fields,
            "prohibited_claims": definition.prohibited_claims,
            "eligibility_rule": definition.eligibility_rule,
        }
        contract_hash = hashlib.sha256(
            json.dumps(canonical, sort_keys=True).encode("utf-8")
        ).hexdigest().upper()
        contract_id = stable_id(
            definition.contract_name,
            definition.contract_version,
            contract_hash,
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO control.temporal_contract (
                temporal_contract_id, contract_name, contract_version,
                description, required_fields_json, prohibited_claims_json,
                eligibility_rule, contract_hash, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
            """,
            [
                contract_id,
                definition.contract_name,
                definition.contract_version,
                definition.description,
                json.dumps(definition.required_fields),
                json.dumps(definition.prohibited_claims),
                definition.eligibility_rule,
                contract_hash,
                now,
            ],
        )
        registered[definition.contract_name] = {
            "contract_id": contract_id,
            "contract_version": definition.contract_version,
            "contract_hash": contract_hash,
        }
    return registered


def register_snapshot(
    connection,
    *,
    deployment_id: str,
    source_asset_id: str,
    profile: dict,
    contract: dict,
) -> str:
    run_id = profile["run_ids"][0] if len(profile["run_ids"]) == 1 else None
    model_version = (
        profile["model_versions"][0]
        if len(profile["model_versions"]) == 1
        else None
    )
    run_inventory_identity = inventory_identity_value(profile["run_ids"])
    model_inventory_identity = inventory_identity_value(profile["model_versions"])
    process_timestamp_text = (
        profile["timestamps"][0] if len(profile["timestamps"]) == 1 else None
    )
    process_timestamp = (
        pd.Timestamp(process_timestamp_text).to_pydatetime()
        if process_timestamp_text
        else None
    )
    snapshot_id = stable_id(
        source_asset_id,
        contract["contract_id"],
        contract["contract_version"],
        run_inventory_identity,
        model_inventory_identity,
        process_timestamp_text,
        None,
        None,
        PROCESS_TIME_ONLY,
    )
    now = utc_now()
    connection.execute(
        """
        INSERT OR IGNORE INTO control.snapshot_registry (
            snapshot_id, source_asset_id, temporal_contract_id,
            temporal_contract_version, source_run_id, source_model_version,
            process_timestamp, observation_date, reporting_date,
            origination_date, source_date_provenance, history_mode,
            evidence_classification, identity_grain,
            identity_continuity_status, temporal_quality,
            historical_analytics_eligible, snapshot_status,
            population_count, distinct_entity_count, timezone, limitations,
            registered_at, validated_at, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?,
                  'BORROWER', ?, 'PROCESS_TIMESTAMP_NOT_OBSERVATION_TIME',
                  FALSE, 'PUBLISHED', ?, ?, 'UTC', ?, ?, ?, ?)
        """,
        [
            snapshot_id,
            source_asset_id,
            contract["contract_id"],
            contract["contract_version"],
            run_id,
            model_version,
            process_timestamp,
            PROCESS_TIMESTAMP_ONLY,
            PROCESS_TIME_ONLY,
            SYNTHETIC_BASELINE,
            NOT_ESTABLISHED,
            profile["row_count"],
            profile["distinct_borrower_count"],
            LIMITATIONS,
            now,
            now,
            now,
        ],
    )
    link_id = stable_id(snapshot_id, source_asset_id, "AUTHORITATIVE_BASELINE_SOURCE")
    connection.execute(
        """
        INSERT OR IGNORE INTO control.snapshot_source_link (
            snapshot_source_link_id, snapshot_id, source_asset_id,
            relationship_type, source_sha256, created_at
        ) VALUES (?, ?, ?, 'AUTHORITATIVE_BASELINE_SOURCE', ?, ?)
        """,
        [link_id, snapshot_id, source_asset_id, profile["sha256_before"], now],
    )
    manifest_id = stable_id(snapshot_id, source_asset_id, "SNAPSHOT_MANIFEST")
    connection.execute(
        """
        INSERT OR IGNORE INTO staging.stg_snapshot_manifest (
            manifest_row_id, deployment_id, source_asset_id, snapshot_id,
            logical_source_name, relative_path, source_sha256,
            canonical_schema_hash, row_count, column_count, source_run_id,
            source_model_version, process_timestamp, observation_date,
            reporting_date, origination_date, source_date_provenance,
            history_mode, evidence_classification, identity_continuity_status,
            temporal_quality, historical_analytics_eligible,
            discovery_timestamp
        ) VALUES (?, ?, ?, ?, 'scored_portfolio', ?, ?, ?, ?, ?, ?, ?, ?,
                  NULL, NULL, NULL, ?, ?, ?, ?,
                  'PROCESS_TIMESTAMP_NOT_OBSERVATION_TIME', FALSE, ?)
        """,
        [
            manifest_id,
            deployment_id,
            source_asset_id,
            snapshot_id,
            profile["relative_path"],
            profile["sha256_before"],
            profile["canonical_schema_hash"],
            profile["row_count"],
            profile["column_count"],
            run_id,
            model_version,
            process_timestamp,
            PROCESS_TIMESTAMP_ONLY,
            PROCESS_TIME_ONLY,
            SYNTHETIC_BASELINE,
            NOT_ESTABLISHED,
            now,
        ],
    )
    return snapshot_id

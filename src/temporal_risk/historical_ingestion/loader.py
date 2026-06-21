from __future__ import annotations

import hashlib
import json
from datetime import date, datetime

import pandas as pd

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.historical_ingestion.contracts import (
    CONTRACTS,
    OBSERVED_TEMPORAL,
)


EVENT_COLUMNS = {
    "origination_date": "ORIGINATION",
    "default_date": "DEFAULT",
    "cure_date": "CURE",
    "recovery_date": "RECOVERY",
    "maturity_date": "MATURITY",
}


def _value(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()
    if isinstance(value, (date, datetime)):
        return value
    return value.item() if hasattr(value, "item") else value


def register_reference_rows(connection) -> None:
    rows = (
        ("BORROWER", "Stable source-supplied borrower identity.", False),
        ("FACILITY", "Stable source-supplied facility identity.", True),
    )
    for code, description, requires_facility in rows:
        connection.execute(
            """
            INSERT OR IGNORE INTO reference.dim_identity_grain
            VALUES (?, ?, ?, TRUE)
            """,
            [code, description, requires_facility],
        )
    statuses = (
        ("NOT_ASSESSED", "Readiness has not been evaluated."),
        ("READY_BUT_DISABLED", "Inputs appear available; activation remains disabled."),
        ("NOT_READY", "Required source inputs are incomplete."),
        ("NOT_ELIGIBLE", "Evidence classification is not eligible."),
        ("FAILED", "Readiness evaluation failed."),
    )
    for code, description in statuses:
        connection.execute(
            """
            INSERT OR IGNORE INTO reference.dim_readiness_status
            VALUES (?, ?, FALSE, TRUE)
            """,
            [code, description],
        )


def register_contract(connection, manifest: dict) -> dict:
    definition = CONTRACTS[manifest["contract_name"]]
    canonical = {
        "contract_name": definition.contract_name,
        "contract_version": definition.contract_version,
        "history_mode": definition.history_mode,
        "evidence_classification": definition.evidence_classification,
        "description": definition.description,
        "required_fields": (
            "source_entity_id",
            "observation_or_reporting_date",
            "source_date_provenance",
            "source_hash",
        ),
        "prohibited_claims": (
            "migration",
            "roll_rate",
            "vintage",
            "true_oot",
            "ifrs9",
        ),
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
            json.dumps(canonical["required_fields"]),
            json.dumps(canonical["prohibited_claims"]),
            (
                "Source-supplied temporal identity may be stored; all "
                "analytical activation remains disabled."
            ),
            contract_hash,
            utc_now(),
        ],
    )
    return {
        "contract_id": contract_id,
        "contract_version": definition.contract_version,
        "contract_hash": contract_hash,
    }


def register_source_assets(
    connection,
    *,
    manifest: dict,
    source_frame: pd.DataFrame,
    schema_hash: str,
) -> tuple[str, str]:
    now = utc_now()
    source_asset_id = stable_id(
        manifest["source_relative_path"],
        manifest["source_file_sha256"].upper(),
    )
    manifest_asset_id = stable_id(
        manifest["manifest_relative_path"],
        manifest["manifest_sha256"],
    )
    assets = (
        (
            source_asset_id,
            "historical_snapshot_source",
            manifest["source_relative_path"],
            manifest["source_format"].upper(),
            manifest["source_file_sha256"].upper(),
            manifest["source_path"].stat().st_size,
            len(source_frame),
            len(source_frame.columns),
            schema_hash,
        ),
        (
            manifest_asset_id,
            "historical_snapshot_manifest",
            manifest["manifest_relative_path"],
            "JSON",
            manifest["manifest_sha256"],
            manifest["manifest_path"].stat().st_size,
            1,
            len(manifest),
            hashlib.sha256(
                json.dumps(sorted(manifest.keys())).encode("utf-8")
            ).hexdigest().upper(),
        ),
    )
    for asset in assets:
        connection.execute(
            """
            INSERT OR IGNORE INTO control.source_asset (
                source_asset_id, logical_source_name, relative_path,
                source_type, source_system, evidence_classification,
                authoritative_baseline, sha256, size_bytes, modified_at,
                row_count, column_count, canonical_schema_hash,
                first_seen_at, last_seen_at
            ) VALUES (?, ?, ?, ?, ?, ?, FALSE, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                asset[0],
                asset[1],
                asset[2],
                asset[3],
                manifest["source_system"],
                manifest["evidence_classification"],
                asset[4],
                asset[5],
                datetime.fromtimestamp(
                    (
                        manifest["source_path"]
                        if asset[0] == source_asset_id
                        else manifest["manifest_path"]
                    ).stat().st_mtime
                ),
                asset[6],
                asset[7],
                asset[8],
                now,
                now,
            ],
        )
        connection.execute(
            "UPDATE control.source_asset SET last_seen_at = ? WHERE source_asset_id = ?",
            [now, asset[0]],
        )
    for position, column in enumerate(source_frame.columns, start=1):
        column_id = stable_id(source_asset_id, column)
        connection.execute(
            """
            INSERT OR IGNORE INTO control.source_column (
                source_column_id, source_asset_id, column_name,
                ordinal_position, source_dtype, observed_nullable,
                semantic_role, temporal_role, provenance_classification
            ) VALUES (?, ?, ?, ?, ?, ?, 'HISTORICAL_SOURCE_ATTRIBUTE',
                      ?, 'SOURCE_SUPPLIED')
            """,
            [
                column_id,
                source_asset_id,
                str(column),
                position,
                str(source_frame[column].dtype),
                bool(source_frame[column].isna().any()),
                (
                    "SOURCE_TEMPORAL_FIELD"
                    if str(column)
                    in {
                        manifest.get("observation_date_column"),
                        manifest.get("reporting_date_column"),
                    }
                    else "NON_TEMPORAL"
                ),
            ],
        )
    return source_asset_id, manifest_asset_id


def governed_snapshot_id(
    manifest: dict,
    contract: dict,
) -> str:
    return stable_id(
        manifest["source_system"],
        manifest["identity_grain"],
        manifest["declared_snapshot_date"],
        manifest["history_mode"],
        contract["contract_id"],
        contract["contract_version"],
    )


def snapshot_state(
    connection,
    *,
    snapshot_id: str,
    source_hash: str,
    manifest_hash: str,
    contract_version: str,
) -> tuple[bool, bool]:
    rows = connection.execute(
        """
        SELECT snapshot.source_sha256,
               ingestion_file.manifest_sha256,
               snapshot.temporal_contract_version
        FROM core.dim_historical_snapshot AS snapshot
        LEFT JOIN control.historical_ingestion_file AS ingestion_file
          ON ingestion_file.ingestion_batch_id = snapshot.ingestion_batch_id
        WHERE snapshot.snapshot_id = ?
        """,
        [snapshot_id],
    ).fetchall()
    if not rows:
        return False, False
    exact_match = (
        len(rows) == 1
        and rows[0][0] == source_hash
        and rows[0][1] == manifest_hash
        and rows[0][2] == contract_version
    )
    return exact_match, not exact_match


def start_batch(
    connection,
    *,
    ingestion_batch_id: str,
    release_id: str,
    manifest: dict,
    contract: dict,
) -> None:
    connection.execute(
        """
        INSERT INTO control.historical_ingestion_batch (
            ingestion_batch_id, release_id, temporal_contract_id,
            temporal_contract_version, history_mode, started_at, status,
            source_sha256, manifest_sha256
        ) VALUES (?, ?, ?, ?, ?, ?, 'RUNNING', ?, ?)
        """,
        [
            ingestion_batch_id,
            release_id,
            contract["contract_id"],
            contract["contract_version"],
            manifest["history_mode"],
            utc_now(),
            manifest["source_file_sha256"].upper(),
            manifest["manifest_sha256"],
        ],
    )


def register_ingestion_file(
    connection,
    *,
    ingestion_batch_id: str,
    source_asset_id: str,
    manifest_asset_id: str,
    manifest: dict,
    schema_hash: str,
    source_frame: pd.DataFrame,
) -> str:
    ingestion_file_id = stable_id(
        ingestion_batch_id,
        source_asset_id,
        manifest_asset_id,
    )
    connection.execute(
        """
        INSERT INTO control.historical_ingestion_file (
            ingestion_file_id, ingestion_batch_id, source_asset_id,
            manifest_asset_id, source_relative_path, manifest_relative_path,
            source_format, source_sha256, manifest_sha256,
            canonical_schema_hash, row_count, column_count,
            declared_snapshot_date, observed_snapshot_date, status,
            registered_at, validated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'VALIDATED', ?, ?)
        """,
        [
            ingestion_file_id,
            ingestion_batch_id,
            source_asset_id,
            manifest_asset_id,
            manifest["source_relative_path"],
            manifest["manifest_relative_path"],
            manifest["source_format"].upper(),
            manifest["source_file_sha256"].upper(),
            manifest["manifest_sha256"],
            schema_hash,
            len(source_frame),
            len(source_frame.columns),
            manifest["declared_snapshot_date"],
            manifest["declared_snapshot_date"],
            utc_now(),
            utc_now(),
        ],
    )
    return ingestion_file_id


def register_mappings(
    connection,
    *,
    ingestion_batch_id: str,
    mappings: list[dict],
) -> None:
    for mapping in mappings:
        mapping_id = stable_id(
            ingestion_batch_id,
            mapping["source_column"],
            mapping["canonical_column"],
        )
        connection.execute(
            """
            INSERT INTO control.historical_field_mapping (
                field_mapping_id, ingestion_batch_id, source_column,
                canonical_column, mapping_type, required_flag,
                source_supplied_flag, allowed_cast,
                transformation_description, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                mapping_id,
                ingestion_batch_id,
                mapping["source_column"],
                mapping["canonical_column"],
                mapping["mapping_type"],
                mapping["required"],
                mapping["source_supplied"],
                mapping["allowed_cast"],
                mapping["transformation_description"],
                utc_now(),
            ],
        )


def stage_rows(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    source_asset_id: str,
    manifest: dict,
    normalized: pd.DataFrame,
    rejected_source_rows: set[int],
) -> None:
    for _, row in normalized.iterrows():
        source_row_number = int(row["source_row_number"])
        staging_id = stable_id(ingestion_batch_id, source_row_number)
        connection.execute(
            """
            INSERT INTO staging.stg_historical_snapshot_row (
                staging_row_id, ingestion_batch_id, snapshot_id,
                source_asset_id, source_row_number, history_mode,
                evidence_classification, source_entity_id,
                source_facility_id, observation_date, reporting_date,
                origination_date, default_date, cure_date, recovery_date,
                maturity_date, source_run_id, source_model_version, pd, lgd,
                ead, credit_score, risk_band, risk_grade, ifrs9_stage,
                watchlist_indicator, delinquency_state, utilization,
                underwriting_decision, default_outcome, dq_status,
                source_payload_json, loaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                staging_id,
                ingestion_batch_id,
                snapshot_id,
                source_asset_id,
                source_row_number,
                manifest["history_mode"],
                manifest["evidence_classification"],
                *[
                    _value(row[column])
                    for column in (
                        "source_entity_id",
                        "source_facility_id",
                        "observation_date",
                        "reporting_date",
                        "origination_date",
                        "default_date",
                        "cure_date",
                        "recovery_date",
                        "maturity_date",
                        "source_run_id",
                        "source_model_version",
                        "pd",
                        "lgd",
                        "ead",
                        "credit_score",
                        "risk_band",
                        "risk_grade",
                        "ifrs9_stage",
                        "watchlist_indicator",
                        "delinquency_state",
                        "utilization",
                        "underwriting_decision",
                        "default_outcome",
                    )
                ],
                "REJECTED" if source_row_number in rejected_source_rows else "ACCEPTED",
                row["source_payload_json"],
                utc_now(),
            ],
        )


def load_rejects(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    source_asset_id: str,
    rejected: list[dict],
) -> None:
    for item in rejected:
        reject_id = stable_id(
            ingestion_batch_id,
            item["source_row_number"],
            item["column_name"],
            item["rejection_reason"],
        )
        connection.execute(
            """
            INSERT INTO control.historical_reject_record (
                reject_record_id, ingestion_batch_id, snapshot_id,
                source_asset_id, source_row_number, raw_entity_identifier,
                raw_facility_identifier, column_name, invalid_value, severity,
                rejection_reason, source_payload_json, rejected_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                reject_id,
                ingestion_batch_id,
                snapshot_id,
                source_asset_id,
                item["source_row_number"],
                _value(item["raw_entity_identifier"]),
                _value(item["raw_facility_identifier"]),
                item["column_name"],
                item["invalid_value"],
                item["severity"],
                item["rejection_reason"],
                item["source_payload_json"],
                utc_now(),
            ],
        )


def load_events(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    source_asset_id: str,
    accepted: pd.DataFrame,
) -> int:
    count = 0
    for _, row in accepted.iterrows():
        for source_column, event_type in EVENT_COLUMNS.items():
            event_date = _value(row[source_column])
            if event_date is None:
                continue
            staging_event_id = stable_id(
                ingestion_batch_id,
                row["source_row_number"],
                event_type,
                event_date,
            )
            connection.execute(
                """
                INSERT INTO staging.stg_historical_event_row (
                    staging_event_id, ingestion_batch_id, snapshot_id,
                    source_asset_id, source_row_number, source_entity_id,
                    source_facility_id, event_type, event_date, source_column,
                    source_event_value, dq_status, loaded_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACCEPTED', ?)
                """,
                [
                    staging_event_id,
                    ingestion_batch_id,
                    snapshot_id,
                    source_asset_id,
                    int(row["source_row_number"]),
                    str(row["source_entity_id"]),
                    _value(row["source_facility_id"]),
                    event_type,
                    event_date,
                    source_column,
                    str(event_date),
                    utc_now(),
                ],
            )
            count += 1
    return count


def load_core(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    source_asset_id: str,
    manifest: dict,
    contract: dict,
    schema_hash: str,
    accepted: pd.DataFrame,
    run_inventory: list[str],
    model_inventory: list[str],
) -> dict:
    now = utc_now()
    snapshot_date = date.fromisoformat(str(manifest["declared_snapshot_date"]))
    snapshot_key = stable_id("HISTORICAL_SNAPSHOT", snapshot_id)
    entity_keys = {}
    facility_keys = {}
    for _, row in accepted.iterrows():
        source_entity_id = str(row["source_entity_id"])
        entity_key = stable_id(
            manifest["source_system"],
            manifest["identity_grain"],
            source_entity_id,
        )
        entity_keys[source_entity_id] = entity_key
        connection.execute(
            """
            INSERT OR IGNORE INTO core.dim_historical_entity (
                entity_key, source_system, identity_grain, source_entity_id,
                first_observed_date, last_observed_date,
                evidence_classification, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                entity_key,
                manifest["source_system"],
                manifest["identity_grain"],
                source_entity_id,
                snapshot_date,
                snapshot_date,
                manifest["evidence_classification"],
                now,
                now,
            ],
        )
        connection.execute(
            """
            UPDATE core.dim_historical_entity
            SET first_observed_date = LEAST(first_observed_date, ?),
                last_observed_date = GREATEST(last_observed_date, ?),
                updated_at = ?
            WHERE entity_key = ?
            """,
            [snapshot_date, snapshot_date, now, entity_key],
        )
        facility_value = _value(row["source_facility_id"])
        if facility_value is not None:
            source_facility_id = str(facility_value)
            facility_key = stable_id(manifest["source_system"], source_facility_id)
            facility_keys[(source_entity_id, source_facility_id)] = facility_key
            connection.execute(
                """
                INSERT OR IGNORE INTO core.dim_historical_facility (
                    facility_key, entity_key, source_system,
                    source_facility_id, first_observed_date,
                    last_observed_date, evidence_classification,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    facility_key,
                    entity_key,
                    manifest["source_system"],
                    source_facility_id,
                    snapshot_date,
                    snapshot_date,
                    manifest["evidence_classification"],
                    now,
                    now,
                ],
            )
            connection.execute(
                """
                UPDATE core.dim_historical_facility
                SET first_observed_date = LEAST(first_observed_date, ?),
                    last_observed_date = GREATEST(last_observed_date, ?),
                    updated_at = ?
                WHERE facility_key = ?
                """,
                [snapshot_date, snapshot_date, now, facility_key],
            )
    connection.execute(
        """
        INSERT INTO core.dim_historical_snapshot (
            historical_snapshot_key, snapshot_id, source_asset_id,
            temporal_contract_id, temporal_contract_version,
            ingestion_batch_id, snapshot_date, snapshot_date_type,
            history_mode, evidence_classification, identity_grain,
            identity_continuity_status, source_run_inventory_json,
            source_model_inventory_json, source_sha256,
            canonical_schema_hash, temporal_quality,
            storage_readiness_status, loaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            snapshot_key,
            snapshot_id,
            source_asset_id,
            contract["contract_id"],
            contract["contract_version"],
            ingestion_batch_id,
            snapshot_date,
            "OBSERVATION_DATE"
            if manifest.get("observation_date_column")
            else "REPORTING_DATE",
            manifest["history_mode"],
            manifest["evidence_classification"],
            manifest["identity_grain"],
            "SOURCE_SUPPLIED_UNVERIFIED",
            json.dumps(run_inventory),
            json.dumps(model_inventory),
            manifest["source_file_sha256"].upper(),
            schema_hash,
            "SOURCE_DATE_VALIDATED",
            "READY_BUT_DISABLED",
            now,
        ],
    )
    observation_count = 0
    for _, row in accepted.iterrows():
        source_entity_id = str(row["source_entity_id"])
        entity_key = entity_keys[source_entity_id]
        facility_value = _value(row["source_facility_id"])
        facility_key = (
            facility_keys[(source_entity_id, str(facility_value))]
            if facility_value is not None
            else None
        )
        observation_id = stable_id(snapshot_id, entity_key, facility_key)
        connection.execute(
            """
            INSERT INTO core.fact_historical_credit_observation (
                observation_id, snapshot_id, historical_snapshot_key,
                entity_key, facility_key, source_asset_id, source_row_number,
                observation_date, reporting_date, origination_date,
                maturity_date, source_run_id, source_model_version, pd, lgd,
                ead, credit_score, risk_band, risk_grade, ifrs9_stage,
                watchlist_indicator, delinquency_state, utilization,
                underwriting_decision, default_outcome,
                evidence_classification, loaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                      ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                observation_id,
                snapshot_id,
                snapshot_key,
                entity_key,
                facility_key,
                source_asset_id,
                int(row["source_row_number"]),
                *[
                    _value(row[column])
                    for column in (
                        "observation_date",
                        "reporting_date",
                        "origination_date",
                        "maturity_date",
                        "source_run_id",
                        "source_model_version",
                        "pd",
                        "lgd",
                        "ead",
                        "credit_score",
                        "risk_band",
                        "risk_grade",
                        "ifrs9_stage",
                        "watchlist_indicator",
                        "delinquency_state",
                        "utilization",
                        "underwriting_decision",
                        "default_outcome",
                    )
                ],
                manifest["evidence_classification"],
                now,
            ],
        )
        observation_count += 1
    staged_events = connection.execute(
        """
        SELECT source_row_number, source_entity_id, source_facility_id,
               event_type, event_date, source_column, source_event_value
        FROM staging.stg_historical_event_row
        WHERE ingestion_batch_id = ?
        """,
        [ingestion_batch_id],
    ).fetchall()
    for event in staged_events:
        source_entity_id = str(event[1])
        entity_key = entity_keys[source_entity_id]
        facility_key = (
            facility_keys.get((source_entity_id, str(event[2])))
            if event[2] is not None
            else None
        )
        event_id = stable_id(
            snapshot_id,
            entity_key,
            facility_key,
            event[3],
            event[4],
            event[0],
        )
        connection.execute(
            """
            INSERT INTO core.fact_historical_credit_event (
                event_id, snapshot_id, entity_key, facility_key,
                source_asset_id, source_row_number, event_type, event_date,
                source_column, source_event_value,
                provenance_classification, loaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SOURCE_SUPPLIED', ?)
            """,
            [
                event_id,
                snapshot_id,
                entity_key,
                facility_key,
                source_asset_id,
                event[0],
                event[3],
                event[4],
                event[5],
                event[6],
                now,
            ],
        )
    return {
        "snapshot_key": snapshot_key,
        "observation_count": observation_count,
        "entity_count": len(set(entity_keys.values())),
        "facility_count": len(set(facility_keys.values())),
        "event_count": len(staged_events),
    }


def register_shared_snapshot(
    connection,
    *,
    ingestion_batch_id: str,
    snapshot_id: str,
    source_asset_id: str,
    manifest: dict,
    contract: dict,
    schema_hash: str,
    accepted: pd.DataFrame,
    run_inventory: list[str],
    model_inventory: list[str],
    source_row_count: int,
    source_column_count: int,
) -> None:
    now = utc_now()
    observation_date = (
        manifest["declared_snapshot_date"]
        if manifest.get("observation_date_column")
        else None
    )
    reporting_date = (
        manifest["declared_snapshot_date"]
        if manifest.get("reporting_date_column")
        else None
    )
    run_id = run_inventory[0] if len(run_inventory) == 1 else None
    model_version = model_inventory[0] if len(model_inventory) == 1 else None
    connection.execute(
        """
        INSERT INTO control.snapshot_registry (
            snapshot_id, source_asset_id, temporal_contract_id,
            temporal_contract_version, source_run_id, source_model_version,
            process_timestamp, observation_date, reporting_date,
            origination_date, source_date_provenance, history_mode,
            evidence_classification, identity_grain,
            identity_continuity_status, temporal_quality,
            historical_analytics_eligible, snapshot_status,
            population_count, distinct_entity_count, timezone, limitations,
            registered_at, validated_at, published_at
        ) VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?, NULL, ?, ?, ?, ?,
                  'SOURCE_SUPPLIED_UNVERIFIED', 'SOURCE_DATE_VALIDATED',
                  ?, 'PUBLISHED', ?, ?, 'UTC', ?, ?, ?, ?)
        """,
        [
            snapshot_id,
            source_asset_id,
            contract["contract_id"],
            contract["contract_version"],
            run_id,
            model_version,
            observation_date,
            reporting_date,
            manifest["source_date_provenance"],
            manifest["history_mode"],
            manifest["evidence_classification"],
            manifest["identity_grain"],
            manifest["history_mode"] == OBSERVED_TEMPORAL,
            len(accepted),
            accepted["source_entity_id"].nunique(),
            (
                "Phase 2B stores governed source observations only. All "
                "migration, roll-rate, vintage, OOT, and IFRS9 processing is disabled."
            ),
            now,
            now,
            now,
        ],
    )
    link_id = stable_id(snapshot_id, source_asset_id, "HISTORICAL_SOURCE")
    connection.execute(
        """
        INSERT INTO control.snapshot_source_link (
            snapshot_source_link_id, snapshot_id, source_asset_id,
            relationship_type, source_sha256, created_at
        ) VALUES (?, ?, ?, 'HISTORICAL_SOURCE', ?, ?)
        """,
        [
            link_id,
            snapshot_id,
            source_asset_id,
            manifest["source_file_sha256"].upper(),
            now,
        ],
    )
    manifest_id = stable_id(snapshot_id, source_asset_id, "HISTORICAL_MANIFEST")
    connection.execute(
        """
        INSERT INTO staging.stg_snapshot_manifest (
            manifest_row_id, deployment_id, source_asset_id, snapshot_id,
            logical_source_name, relative_path, source_sha256,
            canonical_schema_hash, row_count, column_count, source_run_id,
            source_model_version, process_timestamp, observation_date,
            reporting_date, origination_date, source_date_provenance,
            history_mode, evidence_classification, identity_continuity_status,
            temporal_quality, historical_analytics_eligible,
            discovery_timestamp
        ) VALUES (?, ?, ?, ?, 'historical_snapshot_source', ?, ?, ?, ?, ?, ?,
                  ?, NULL, ?, ?, NULL, ?, ?, ?, 'SOURCE_SUPPLIED_UNVERIFIED',
                  'SOURCE_DATE_VALIDATED', ?, ?)
        """,
        [
            manifest_id,
            ingestion_batch_id,
            source_asset_id,
            snapshot_id,
            manifest["source_relative_path"],
            manifest["source_file_sha256"].upper(),
            schema_hash,
            source_row_count,
            source_column_count,
            run_id,
            model_version,
            observation_date,
            reporting_date,
            manifest["source_date_provenance"],
            manifest["history_mode"],
            manifest["evidence_classification"],
            manifest["history_mode"] == OBSERVED_TEMPORAL,
            now,
        ],
    )


def record_historical_publish(
    connection,
    ingestion_batch_id: str,
    previous_status: str | None,
    new_status: str,
    details: str,
) -> None:
    publish_id = stable_id(ingestion_batch_id, previous_status, new_status)
    connection.execute(
        """
        INSERT INTO control.historical_publish_status (
            historical_publish_id, ingestion_batch_id, target_name,
            previous_status, new_status, transition_at, details
        ) VALUES (?, ?, 'kronos_temporal_risk.duckdb', ?, ?, ?, ?)
        """,
        [
            publish_id,
            ingestion_batch_id,
            previous_status,
            new_status,
            utc_now(),
            details,
        ],
    )

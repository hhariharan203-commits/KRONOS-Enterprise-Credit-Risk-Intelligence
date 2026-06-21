from __future__ import annotations

import json

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.migration_readiness.config import PHASE2C_RELEASE_VERSION
from src.temporal_risk.migration_readiness.contracts import (
    CONTROLLED_CONTRACTS,
    PHASE2C_PAIR_CONFLICT,
    Phase2CPairConflictError,
)


def phase2c_release_id() -> str:
    return stable_id("PHASE2C", PHASE2C_RELEASE_VERSION)


def _contract_id(contract) -> str:
    return stable_id(
        contract.contract_name,
        contract.contract_version,
        contract.hash(),
    )


def register_controlled_contracts(connection) -> dict:
    registered = {}
    for contract in CONTROLLED_CONTRACTS:
        definition = contract.definition()
        contract_hash = contract.hash()
        existing = connection.execute(
            """
            SELECT contract_id, contract_hash
            FROM control.migration_transition_contract
            WHERE contract_name = ? AND contract_version = ?
            """,
            [contract.contract_name, contract.contract_version],
        ).fetchall()
        if existing and existing[0][1] != contract_hash:
            raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
        contract_id = _contract_id(contract)
        connection.execute(
            """
            INSERT OR IGNORE INTO control.migration_transition_contract (
                contract_id, contract_type, contract_name, contract_version,
                supported_history_mode, supported_evidence_classification,
                permitted_identity_grains_json, state_field,
                ordered_allowed_values_json, required_source_provenance_json,
                prohibited_capabilities_json, contract_definition_json,
                contract_hash, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
            """,
            [
                contract_id,
                contract.contract_type,
                contract.contract_name,
                contract.contract_version,
                definition["supported_history_mode"],
                definition["supported_evidence_classification"],
                json.dumps(definition["permitted_identity_grains"]),
                contract.state_field,
                json.dumps(list(contract.ordered_allowed_values))
                if contract.state_field
                else None,
                json.dumps(definition["required_source_provenance"]),
                json.dumps(definition["prohibited_capabilities"]),
                json.dumps(definition, sort_keys=True),
                contract_hash,
                utc_now(),
            ],
        )
        registered[contract.contract_name] = {
            "contract_id": contract_id,
            "contract_name": contract.contract_name,
            "contract_version": contract.contract_version,
            "contract_hash": contract_hash,
            "state_field": contract.state_field,
        }
    return registered


def validate_controlled_contracts(connection) -> dict:
    registered = {}
    for contract in CONTROLLED_CONTRACTS:
        row = connection.execute(
            """
            SELECT contract_id, contract_hash, status
            FROM control.migration_transition_contract
            WHERE contract_name = ? AND contract_version = ?
            """,
            [contract.contract_name, contract.contract_version],
        ).fetchone()
        if row is None or row[1] != contract.hash() or row[2] != "ACTIVE":
            raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
        registered[contract.contract_name] = {
            "contract_id": row[0],
            "contract_name": contract.contract_name,
            "contract_version": contract.contract_version,
            "contract_hash": row[1],
            "state_field": contract.state_field,
        }
    return registered


def register_phase2c_release(
    connection,
    *,
    database_path: str,
    specification_inventory: dict,
    catalog: dict,
) -> str:
    release_id = phase2c_release_id()
    earlier_releases = connection.execute(
        """
        SELECT phase_name, status
        FROM control.platform_release
        WHERE phase_name IN ('PHASE2A', 'PHASE2B')
        ORDER BY phase_name
        """
    ).fetchall()
    if earlier_releases != [("PHASE2A", "PUBLISHED"), ("PHASE2B", "PUBLISHED")]:
        raise RuntimeError("Published Phase 2A and Phase 2B releases are required.")
    connection.execute(
        """
        INSERT OR IGNORE INTO control.platform_release (
            release_id, phase_name, release_version, database_path,
            specification_hashes_json, schema_count, table_count,
            view_count, status, created_at
        ) VALUES (?, 'PHASE2C', ?, ?, ?, ?, ?, ?, 'DRAFT', ?)
        """,
        [
            release_id,
            PHASE2C_RELEASE_VERSION,
            database_path,
            json.dumps(specification_inventory, sort_keys=True),
            catalog["schema_count"],
            catalog["table_count"],
            catalog["view_count"],
            utc_now(),
        ],
    )
    connection.execute(
        """
        UPDATE control.platform_release
        SET database_path = ?, specification_hashes_json = ?,
            schema_count = ?, table_count = ?, view_count = ?, status = 'DRAFT'
        WHERE release_id = ? AND phase_name = 'PHASE2C'
        """,
        [
            database_path,
            json.dumps(specification_inventory, sort_keys=True),
            catalog["schema_count"],
            catalog["table_count"],
            catalog["view_count"],
            release_id,
        ],
    )
    return release_id


def publish_phase2c_release(connection, release_id: str) -> None:
    connection.execute(
        """
        UPDATE control.platform_release
        SET status = 'PUBLISHED'
        WHERE release_id = ? AND phase_name = 'PHASE2C'
        """,
        [release_id],
    )

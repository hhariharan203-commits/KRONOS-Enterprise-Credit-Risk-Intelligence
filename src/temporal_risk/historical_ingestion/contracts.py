from __future__ import annotations

from dataclasses import dataclass


PHASE2B_SCHEMA_READY = "PHASE2B_SCHEMA_READY"
PHASE2B_UPGRADE_PRESENT = "PHASE2B_UPGRADE_PRESENT"
PHASE2B_INGESTION_SUCCESS = "PHASE2B_INGESTION_SUCCESS"
PHASE2B_SCOPE_VIOLATION = "PHASE2B_SCOPE_VIOLATION"
PHASE2B_UNAVAILABLE = "PHASE2B_UNAVAILABLE"
PHASE2B_BASELINE_MISMATCH = "PHASE2B_BASELINE_MISMATCH"
HISTORICAL_SOURCE_NOT_READY = "HISTORICAL_SOURCE_NOT_READY"
HISTORICAL_CONTRACT_VIOLATION = "HISTORICAL_CONTRACT_VIOLATION"
SNAPSHOT_VERSION_CONFLICT = "SNAPSHOT_VERSION_CONFLICT"
SKIPPED_ALREADY_PUBLISHED = "SKIPPED_ALREADY_PUBLISHED"

OBSERVED_CONTRACT = "OBSERVED_HISTORICAL_SNAPSHOT_V1"
SIMULATED_CONTRACT = "SIMULATED_HISTORICAL_SNAPSHOT_V1"
OBSERVED_TEMPORAL = "OBSERVED_TEMPORAL"
SIMULATED_TEMPORAL = "SIMULATED_TEMPORAL"
OBSERVED_SOURCE = "OBSERVED_SOURCE"
SIMULATED_SOURCE = "SIMULATED_SOURCE"
DISABLED = "DISABLED_PENDING_FUTURE_PHASE"

PROHIBITED_CAPABILITIES = (
    "migration matrices",
    "migration analytics",
    "roll rates",
    "vintage analytics",
    "true oot",
    "ifrs9 calculations",
    "ifrs9 staging",
    "ecl",
    "dashboard integration",
    "application integration",
    "current warehouse integration",
    "phase 4 integration",
    "sas analytics integration",
)

REQUIRED_MANIFEST_FIELDS = (
    "manifest_version",
    "contract_name",
    "contract_version",
    "history_mode",
    "evidence_classification",
    "source_system",
    "source_file",
    "source_file_sha256",
    "source_format",
    "identity_grain",
    "entity_id_column",
    "facility_id_column",
    "observation_date_column",
    "reporting_date_column",
    "declared_snapshot_date",
    "source_date_provenance",
    "field_mapping",
    "source_run_id_column",
    "model_version_column",
    "created_at",
)

CANONICAL_FIELDS = (
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


class Phase2BError(RuntimeError):
    """Base exception for governed Phase 2B failures."""


class Phase2BScopeError(Phase2BError):
    """Raised when Phase 2B attempts analytical or integration scope."""


class Phase2BValidationError(Phase2BError):
    """Raised when a Phase 2B validation gate fails."""


class Phase2BBaselineError(Phase2BError):
    """Raised when a protected baseline changes."""


class HistoricalContractError(Phase2BError):
    """Raised when a historical source contract is invalid."""


class SnapshotConflictError(Phase2BError):
    """Raised for a governed snapshot identity with a different source hash."""


@dataclass(frozen=True)
class HistoricalContract:
    contract_name: str
    contract_version: str
    history_mode: str
    evidence_classification: str
    description: str


CONTRACTS = {
    OBSERVED_CONTRACT: HistoricalContract(
        OBSERVED_CONTRACT,
        "1",
        OBSERVED_TEMPORAL,
        OBSERVED_SOURCE,
        "Source-supplied observed historical snapshots.",
    ),
    SIMULATED_CONTRACT: HistoricalContract(
        SIMULATED_CONTRACT,
        "1",
        SIMULATED_TEMPORAL,
        SIMULATED_SOURCE,
        "Externally produced and explicitly labelled simulated snapshots.",
    ),
}


def enforce_scope(requested_capabilities: tuple[str, ...] = ()) -> None:
    normalized = {value.strip().lower() for value in requested_capabilities}
    prohibited = sorted(
        item
        for item in normalized
        if any(token in item for token in PROHIBITED_CAPABILITIES)
    )
    if prohibited:
        raise Phase2BScopeError(
            f"{PHASE2B_SCOPE_VIOLATION}: {', '.join(prohibited)}"
        )

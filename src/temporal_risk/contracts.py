from __future__ import annotations

from dataclasses import dataclass


PHASE2A_SUCCESS = "PHASE2A_SUCCESS"
TEMPORAL_PLATFORM_UNAVAILABLE = "TEMPORAL_PLATFORM_UNAVAILABLE"
BASELINE_MISMATCH = "BASELINE_MISMATCH"
PHASE2A_VALIDATION_FAILED = "PHASE2A_VALIDATION_FAILED"
PHASE2A_SCOPE_VIOLATION = "PHASE2A_SCOPE_VIOLATION"
BASELINE_SPECIFICATION_MISSING = "BASELINE_SPECIFICATION_MISSING"

PROCESS_TIME_ONLY = "PROCESS_TIME_ONLY"
SYNTHETIC_BASELINE = "SYNTHETIC_BASELINE"
NOT_ESTABLISHED = "NOT_ESTABLISHED"
PROCESS_TIMESTAMP_ONLY = "PROCESS_TIMESTAMP_ONLY"
PASS_WITH_LIMITATIONS = "PASS_WITH_LIMITATIONS"

PROHIBITED_CAPABILITIES = (
    "historical borrower records",
    "historical scoring",
    "historical model execution",
    "migration matrices",
    "roll rates",
    "vintage curves",
    "true oot validation",
    "ifrs9 temporal ecl",
    "dashboard integration",
    "app integration",
    "warehouse integration",
    "enterprise visibility integration",
    "sas analytics integration",
    "phase 4 integration",
)

ALLOWED_CAPABILITIES = (
    "create isolated temporal platform",
    "register baseline metadata",
    "register temporal contracts",
    "register snapshot metadata",
    "execute dq controls",
    "execute reconciliations",
    "persist lineage",
    "publish isolated temporal database",
)


class Phase2AError(RuntimeError):
    """Base exception for governed Phase 2A failures."""


class BaselineMismatchError(Phase2AError):
    """Raised when a protected baseline changes during deployment."""


class Phase2AScopeError(Phase2AError):
    """Raised when implementation exceeds the Phase 2A control boundary."""


class Phase2AValidationError(Phase2AError):
    """Raised when a Phase 2A validation gate fails."""


class BaselineSpecificationError(Phase2AError):
    """Raised when controlled Phase 2A specifications are unavailable."""


@dataclass(frozen=True)
class TemporalContractDefinition:
    contract_name: str
    contract_version: str
    description: str
    required_fields: tuple[str, ...]
    prohibited_claims: tuple[str, ...]
    eligibility_rule: str


TEMPORAL_CONTRACTS = (
    TemporalContractDefinition(
        contract_name="CURRENT_STATE_BASELINE",
        contract_version="1",
        description=(
            "Registers the current synthetic scored portfolio as process-time "
            "metadata only."
        ),
        required_fields=("borrower_id", "run_id", "model_version", "timestamp"),
        prohibited_claims=PROHIBITED_CAPABILITIES[:8],
        eligibility_rule="historical_analytics_eligible = false",
    ),
    TemporalContractDefinition(
        contract_name="HISTORICAL_SNAPSHOT",
        contract_version="1",
        description=(
            "Defines future source requirements without accepting historical "
            "borrower records in Phase 2A."
        ),
        required_fields=(
            "stable_source_entity_id",
            "observation_or_reporting_date",
            "source_date_provenance",
            "source_hash",
            "history_mode",
        ),
        prohibited_claims=PROHIBITED_CAPABILITIES,
        eligibility_rule=(
            "Future eligibility requires source-supplied observed dates and "
            "established longitudinal identity."
        ),
    ),
)


def enforce_scope(requested_capabilities: tuple[str, ...] = ALLOWED_CAPABILITIES) -> None:
    normalized = {value.strip().lower() for value in requested_capabilities}
    prohibited = sorted(normalized.intersection(PROHIBITED_CAPABILITIES))
    unknown = sorted(normalized.difference(ALLOWED_CAPABILITIES))
    if prohibited or unknown:
        details = ", ".join(prohibited + unknown)
        raise Phase2AScopeError(f"{PHASE2A_SCOPE_VIOLATION}: {details}")

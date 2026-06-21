from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


PHASE2C_SCHEMA_READY = "PHASE2C_SCHEMA_READY"
PHASE2C_READINESS_PUBLISHED = "PHASE2C_READINESS_PUBLISHED"
PHASE2C_SCOPE_VIOLATION = "PHASE2C_SCOPE_VIOLATION"
PHASE2C_UNAVAILABLE = "PHASE2C_UNAVAILABLE"
PHASE2C_BASELINE_MISMATCH = "PHASE2C_BASELINE_MISMATCH"
PHASE2C_SOURCE_NOT_READY = "PHASE2C_SOURCE_NOT_READY"
PHASE2C_SOURCE_NOT_ELIGIBLE = "PHASE2C_SOURCE_NOT_ELIGIBLE"
PHASE2C_PAIR_CONFLICT = "PHASE2C_PAIR_CONFLICT"
SKIPPED_ALREADY_PUBLISHED = "SKIPPED_ALREADY_PUBLISHED"
DISABLED = "DISABLED_PENDING_FUTURE_PHASE"

READINESS_CONTRACT_NAME = "MIGRATION_TRANSITION_READINESS_V1"
RISK_GRADE_CONTRACT_NAME = "RISK_GRADE_DOMAIN_V1"
RISK_BAND_CONTRACT_NAME = "RISK_BAND_DOMAIN_V1"
CONTRACT_VERSION = "1"

RISK_GRADE_VALUES = ("AAA", "AA", "A", "BBB", "BB", "B", "CCC")
RISK_BAND_VALUES = (
    "PRIME",
    "NEAR PRIME",
    "MODERATE RISK",
    "HIGH RISK",
    "DEFAULT RISK",
)

ALLOWED_STATE_FIELDS = ("risk_grade", "risk_band")

PROHIBITED_CAPABILITIES = (
    "migration matrices",
    "transition analytics",
    "roll rates",
    "vintage analytics",
    "true oot validation",
    "model execution",
    "ifrs9 calculations",
    "dashboard integration",
    "application integration",
    "current warehouse integration",
    "phase 4 integration",
    "sas integration",
    "views",
    "marts",
    "facts",
    "dimensions",
)


class Phase2CError(RuntimeError):
    """Base exception for governed Phase 2C failures."""


class Phase2CScopeError(Phase2CError):
    """Raised when a request exceeds the readiness-only boundary."""


class Phase2CValidationError(Phase2CError):
    """Raised when a Phase 2C validation gate fails."""


class Phase2CBaselineError(Phase2CError):
    """Raised when protected evidence changes."""


class Phase2CPairConflictError(Phase2CError):
    """Raised when pair or contract evidence conflicts."""


class Phase2CSourceNotReadyError(Phase2CError):
    """Raised when observed source evidence is insufficient."""


class Phase2CSourceNotEligibleError(Phase2CError):
    """Raised when source evidence cannot support observed readiness."""


@dataclass(frozen=True)
class ControlledContract:
    contract_type: str
    contract_name: str
    contract_version: str
    state_field: str | None
    ordered_allowed_values: tuple[str, ...]

    def definition(self) -> dict:
        return {
            "contract_type": self.contract_type,
            "contract_name": self.contract_name,
            "contract_version": self.contract_version,
            "supported_history_mode": "OBSERVED_TEMPORAL",
            "supported_evidence_classification": "OBSERVED_SOURCE",
            "permitted_identity_grains": ["BORROWER", "FACILITY"],
            "state_field": self.state_field,
            "ordered_allowed_values": list(self.ordered_allowed_values),
            "case_sensitive": True,
            "aliases_permitted": False,
            "normalization_permitted": False,
            "immutable_after_publication": True,
            "required_source_provenance": [
                "SOURCE_SUPPLIED_IDENTITY",
                "SOURCE_SUPPLIED_DATE",
                "SOURCE_SUPPLIED_STATE",
                "IMMUTABLE_SOURCE_HASH",
            ],
            "prohibited_capabilities": list(PROHIBITED_CAPABILITIES),
        }

    def hash(self) -> str:
        return hashlib.sha256(
            json.dumps(
                self.definition(),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest().upper()


READINESS_CONTRACT = ControlledContract(
    "MIGRATION_READINESS",
    READINESS_CONTRACT_NAME,
    CONTRACT_VERSION,
    None,
    (),
)
RISK_GRADE_CONTRACT = ControlledContract(
    "RISK_GRADE_DOMAIN",
    RISK_GRADE_CONTRACT_NAME,
    CONTRACT_VERSION,
    "risk_grade",
    RISK_GRADE_VALUES,
)
RISK_BAND_CONTRACT = ControlledContract(
    "RISK_BAND_DOMAIN",
    RISK_BAND_CONTRACT_NAME,
    CONTRACT_VERSION,
    "risk_band",
    RISK_BAND_VALUES,
)
CONTROLLED_CONTRACTS = (
    READINESS_CONTRACT,
    RISK_GRADE_CONTRACT,
    RISK_BAND_CONTRACT,
)
STATE_CONTRACTS = {
    "risk_grade": RISK_GRADE_CONTRACT,
    "risk_band": RISK_BAND_CONTRACT,
}


def prohibited_field_names() -> set[str]:
    return {
        "_".join(parts)
        for parts in (
            ("from", "state"),
            ("to", "state"),
            ("state", "pair"),
            ("transition", "pair"),
            ("transition", "count"),
            ("transition", "probability"),
            ("migration", "matrix", "cell"),
        )
    }


def is_prohibited_field_name(value: object) -> bool:
    return str(value) in prohibited_field_names()


def enforce_scope(requested_capabilities: tuple[str, ...] = ()) -> None:
    normalized = {str(value).strip().lower() for value in requested_capabilities}
    violations = sorted(
        value
        for value in normalized
        if any(token in value for token in PROHIBITED_CAPABILITIES)
    )
    if violations:
        raise Phase2CScopeError(
            f"{PHASE2C_SCOPE_VIOLATION}: {', '.join(violations)}"
        )


def governance_score(
    passed_applicable_controls: int,
    applicable_controls: int,
) -> Decimal | None:
    if applicable_controls == 0:
        return None
    value = (
        Decimal("100.0")
        * Decimal(passed_applicable_controls)
        / Decimal(applicable_controls)
    )
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

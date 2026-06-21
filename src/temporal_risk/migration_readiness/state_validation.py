from __future__ import annotations

from src.temporal_risk.migration_readiness.contracts import ControlledContract


def validate_values(values: list[object], contract: ControlledContract) -> dict:
    allowed = set(contract.ordered_allowed_values)
    non_null = [value for value in values if value is not None]
    invalid_count = sum(
        not isinstance(value, str) or value not in allowed
        for value in non_null
    )
    return {
        "value_count": len(values),
        "non_null_count": len(non_null),
        "missing_count": len(values) - len(non_null),
        "invalid_count": invalid_count,
        "valid": len(non_null) == len(values) and invalid_count == 0,
    }

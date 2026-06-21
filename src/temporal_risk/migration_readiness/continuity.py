from __future__ import annotations

from src.temporal_risk.migration_readiness.contracts import ControlledContract
from src.temporal_risk.migration_readiness.state_validation import validate_values


def _identity_column(identity_grain: str) -> str:
    return "facility_key" if identity_grain == "FACILITY" else "entity_key"


def _snapshot_rows(
    connection,
    *,
    snapshot_id: str,
    identity_grain: str,
    state_field: str,
) -> list[tuple]:
    if state_field not in {"risk_grade", "risk_band"}:
        raise ValueError("Unsupported state field.")
    identity_column = _identity_column(identity_grain)
    return connection.execute(
        f"""
        SELECT {identity_column}, {state_field}
        FROM core.fact_historical_credit_observation
        WHERE snapshot_id = ?
        ORDER BY {identity_column}
        """,
        [snapshot_id],
    ).fetchall()


def build_continuity_context(
    connection,
    *,
    earlier: dict,
    later: dict,
    state_field: str,
    domain_contract: ControlledContract,
) -> dict:
    earlier_rows = _snapshot_rows(
        connection,
        snapshot_id=earlier["snapshot_id"],
        identity_grain=earlier["identity_grain"],
        state_field=state_field,
    )
    later_rows = _snapshot_rows(
        connection,
        snapshot_id=later["snapshot_id"],
        identity_grain=later["identity_grain"],
        state_field=state_field,
    )
    earlier_map = {identity: value for identity, value in earlier_rows}
    later_map = {identity: value for identity, value in later_rows}
    overlap = sorted(
        set(earlier_map).intersection(later_map),
        key=lambda value: str(value),
    )
    earlier_overlap_values = [earlier_map[identity] for identity in overlap]
    later_overlap_values = [later_map[identity] for identity in overlap]
    earlier_validation = validate_values(
        earlier_overlap_values,
        domain_contract,
    )
    later_validation = validate_values(
        later_overlap_values,
        domain_contract,
    )
    earlier_batch = connection.execute(
        """
        SELECT records_accepted
        FROM control.historical_ingestion_batch
        WHERE ingestion_batch_id = ?
        """,
        [earlier["ingestion_batch_id"]],
    ).fetchone()
    later_batch = connection.execute(
        """
        SELECT records_accepted
        FROM control.historical_ingestion_batch
        WHERE ingestion_batch_id = ?
        """,
        [later["ingestion_batch_id"]],
    ).fetchone()
    earlier_registry = connection.execute(
        "SELECT COUNT(*) FROM control.snapshot_registry WHERE snapshot_id = ?",
        [earlier["snapshot_id"]],
    ).fetchone()[0]
    later_registry = connection.execute(
        "SELECT COUNT(*) FROM control.snapshot_registry WHERE snapshot_id = ?",
        [later["snapshot_id"]],
    ).fetchone()[0]
    return {
        "earlier": earlier,
        "later": later,
        "state_field": state_field,
        "earlier_population_count": len(earlier_rows),
        "later_population_count": len(later_rows),
        "earlier_distinct_identity_count": len(earlier_map),
        "later_distinct_identity_count": len(later_map),
        "earlier_non_null_identity_count": sum(
            identity is not None for identity, _ in earlier_rows
        ),
        "later_non_null_identity_count": sum(
            identity is not None for identity, _ in later_rows
        ),
        "overlapping_identity_count": len(overlap),
        "earlier_state_complete_overlap_count": earlier_validation["non_null_count"],
        "later_state_complete_overlap_count": later_validation["non_null_count"],
        "earlier_state_missing_overlap_count": earlier_validation["missing_count"],
        "later_state_missing_overlap_count": later_validation["missing_count"],
        "earlier_invalid_state_count": earlier_validation["invalid_count"],
        "later_invalid_state_count": later_validation["invalid_count"],
        "earlier_domain_valid": earlier_validation["valid"],
        "later_domain_valid": later_validation["valid"],
        "earlier_records_accepted": int(earlier_batch[0]) if earlier_batch else -1,
        "later_records_accepted": int(later_batch[0]) if later_batch else -1,
        "earlier_registry_count": int(earlier_registry),
        "later_registry_count": int(later_registry),
    }

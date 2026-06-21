from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2c_contracts import deployed_phase2c


def test_phase2c_release_and_contracts_are_distinct_and_published() -> None:
    _, database = deployed_phase2c()
    connection = connect_temporal(database)
    try:
        releases = connection.execute(
            """
            SELECT phase_name, status, schema_count, table_count, view_count
            FROM control.platform_release
            ORDER BY phase_name
            """
        ).fetchall()
        assert releases == [
            ("PHASE2A", "PUBLISHED", 5, 17, 0),
            ("PHASE2B", "PUBLISHED", 5, 36, 0),
            ("PHASE2C", "PUBLISHED", 5, 46, 0),
        ]
        contracts = connection.execute(
            """
            SELECT contract_name, contract_version, status
            FROM control.migration_transition_contract
            ORDER BY contract_name
            """
        ).fetchall()
        assert contracts == [
            ("MIGRATION_TRANSITION_READINESS_V1", "1", "ACTIVE"),
            ("RISK_BAND_DOMAIN_V1", "1", "ACTIVE"),
            ("RISK_GRADE_DOMAIN_V1", "1", "ACTIVE"),
        ]
    finally:
        connection.close()

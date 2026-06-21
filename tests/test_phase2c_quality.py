from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2c_contracts import shared_published_readiness


def test_exactly_24_critical_quality_controls_pass() -> None:
    _, database, _, result = shared_published_readiness()
    assert result["quality"]["check_count"] == 24
    assert result["quality"]["applicable_controls"] == 24
    assert result["quality"]["passed_applicable_controls"] == 24
    assert str(result["quality"]["governance_score"]) == "100.00"
    connection = connect_temporal(database)
    try:
        rows = connection.execute(
            """
            SELECT COUNT(*), SUM(CASE WHEN critical_flag THEN 1 ELSE 0 END),
                   SUM(CASE WHEN applicable_flag THEN 1 ELSE 0 END),
                   SUM(CASE WHEN status = 'PASS' THEN 1 ELSE 0 END)
            FROM control.migration_quality_result
            WHERE readiness_run_id = ?
            """,
            [result["readiness_run_id"]],
        ).fetchone()
        assert tuple(rows) == (24, 24, 24, 24)
    finally:
        connection.close()

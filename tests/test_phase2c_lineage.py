from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from test_phase2c_contracts import shared_published_readiness


def test_independent_lineage_inventory_is_complete() -> None:
    _, database, _, result = shared_published_readiness()
    assert result["lineage"] == {
        "node_count": 10,
        "edge_count": 12,
        "column_lineage_count": 6,
        "complete": True,
    }
    connection = connect_temporal(database)
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM control.historical_lineage_node"
        ).fetchone()[0] > 0
        assert connection.execute(
            """
            SELECT COUNT(*) FROM control.migration_lineage_node
            WHERE readiness_run_id = ?
            """,
            [result["readiness_run_id"]],
        ).fetchone()[0] == 10
    finally:
        connection.close()

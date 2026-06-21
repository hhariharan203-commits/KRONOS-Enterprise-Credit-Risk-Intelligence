from __future__ import annotations

from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.migration_readiness.source_catalog import (
    validate_exact_catalog,
)
from test_phase2c_contracts import deployed_phase2c


def test_exact_phase2c_catalog() -> None:
    _, database = deployed_phase2c()
    connection = connect_temporal(database)
    try:
        catalog = validate_exact_catalog(connection, "PHASE2C")
        assert (
            catalog["schema_count"],
            catalog["table_count"],
            catalog["view_count"],
            catalog["mart_object_count"],
        ) == (5, 46, 0, 0)
    finally:
        connection.close()

from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.reconciliation import reconcile_phase4d
from src.enterprise_data.risk_marts.source_catalog import open_read_only
from src.enterprise_data.risk_marts.validator import validate_phase4d


def test_phase4d_validation_and_reconciliation_pass() -> None:
    connection = open_read_only(WAREHOUSE_DB)
    try:
        validation = validate_phase4d(connection)
        reconciliation = reconcile_phase4d(connection)
        assert validation["status"] == "PASS"
        assert validation["failure_count"] == 0
        assert reconciliation["status"] == "PASS"
        assert reconciliation["failure_count"] == 0
        assert reconciliation["reconciliation_count"] == 19
    finally:
        connection.close()

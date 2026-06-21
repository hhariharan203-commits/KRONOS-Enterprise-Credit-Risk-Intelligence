from __future__ import annotations

from test_phase2b_contracts import shared_observed_ingestion


def test_phase2b_reconciliation_inventory_passes() -> None:
    _, _, result = shared_observed_ingestion()
    assert result["reconciliation"]["reconciliation_count"] == 12
    assert result["reconciliation"]["failure_count"] == 0

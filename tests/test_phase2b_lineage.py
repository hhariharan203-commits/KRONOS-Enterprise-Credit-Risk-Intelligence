from __future__ import annotations

from test_phase2b_contracts import shared_observed_ingestion


def test_phase2b_lineage_is_independent_and_complete() -> None:
    _, _, result = shared_observed_ingestion()
    assert result["lineage"]["complete"] is True
    assert result["lineage"]["column_lineage_count"] == 8

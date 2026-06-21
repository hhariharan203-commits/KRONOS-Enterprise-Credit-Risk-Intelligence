from __future__ import annotations

from test_phase2b_contracts import shared_observed_ingestion


def test_phase2b_executes_fixed_36_control_inventory() -> None:
    _, _, result = shared_observed_ingestion()
    assert result["quality"]["check_count"] == 36
    assert len({item["rule_name"] for item in result["quality"]["checks"]}) == 36

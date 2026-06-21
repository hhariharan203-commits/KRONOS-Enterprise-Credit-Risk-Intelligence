from __future__ import annotations

from src.temporal_risk.migration_readiness.config import (
    CURRENT_WAREHOUSE,
    SCORED_PORTFOLIO,
    VOLATILE_GENERATED_FILES,
)
from src.temporal_risk.migration_readiness.source_catalog import (
    protected_hash_inventory,
)


def test_protected_inventory_retains_authoritative_assets() -> None:
    inventory = protected_hash_inventory()
    assert CURRENT_WAREHOUSE.resolve().as_posix().endswith(
        "data/warehouse/kronos_risk.duckdb"
    )
    assert "data/warehouse/kronos_risk.duckdb" in inventory
    assert "data/processed/scored_portfolio.csv" in inventory
    assert VOLATILE_GENERATED_FILES.isdisjoint(inventory)
    assert all(".git/" not in path for path in inventory)


def test_volatile_exclusions_are_exact_files_only() -> None:
    assert VOLATILE_GENERATED_FILES == {
        "data/live/live_intelligence_cache.json",
        "outputs/artifact_lineage.json",
        "reports/test_kronos_enterprise_report.pdf",
    }

from __future__ import annotations

from src.temporal_risk.historical_ingestion.config import (
    CURRENT_WAREHOUSE,
    SCORED_PORTFOLIO,
    VOLATILE_GENERATED_FILES,
)
from src.temporal_risk.historical_ingestion.pipeline import protected_hash_inventory
from src.temporal_risk.historical_ingestion.source_discovery import repository_relative


def test_protected_hash_inventory_uses_allowlist_without_git() -> None:
    inventory = protected_hash_inventory()
    assert inventory
    assert all(".git/" not in path for path in inventory)
    assert "src/temporal_risk/pipeline.py" not in inventory
    assert not any(path.startswith("src/temporal_risk/historical_ingestion/") for path in inventory)
    assert VOLATILE_GENERATED_FILES.isdisjoint(inventory)


def test_authoritative_warehouse_and_portfolio_remain_protected() -> None:
    inventory = protected_hash_inventory()
    assert repository_relative(CURRENT_WAREHOUSE) in inventory
    assert repository_relative(SCORED_PORTFOLIO) in inventory

from __future__ import annotations

import pytest

from src.temporal_risk.contracts import (
    ALLOWED_CAPABILITIES,
    PHASE2A_SCOPE_VIOLATION,
    PROCESS_TIME_ONLY,
    SYNTHETIC_BASELINE,
    Phase2AScopeError,
    enforce_scope,
)
from src.temporal_risk.pipeline import specification_inventory


def test_phase2a_control_contract() -> None:
    enforce_scope()
    assert PROCESS_TIME_ONLY == "PROCESS_TIME_ONLY"
    assert SYNTHETIC_BASELINE == "SYNTHETIC_BASELINE"
    assert len(ALLOWED_CAPABILITIES) == 8


def test_phase2a_rejects_analytical_scope() -> None:
    with pytest.raises(Phase2AScopeError, match=PHASE2A_SCOPE_VIOLATION):
        enforce_scope(("migration matrices",))


def test_controlled_specifications_are_persisted_and_hashed() -> None:
    inventory = specification_inventory()
    assert len(inventory) == 6
    for record in inventory.values():
        assert record["status"] == "FILE_CONTROLLED"
        assert record["relative_path"].startswith("docs/")
        assert len(record["sha256"]) == 64

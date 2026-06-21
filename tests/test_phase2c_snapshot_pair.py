from __future__ import annotations

import pytest

import src.temporal_risk.migration_readiness.pair_selector as selector
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.migration_readiness.contracts import (
    PHASE2C_PAIR_CONFLICT,
    Phase2CPairConflictError,
)
from test_phase2c_contracts import two_snapshot_environment


def test_explicit_snapshot_pair_is_chronological() -> None:
    _, database, snapshot_ids = two_snapshot_environment()
    connection = connect_temporal(database)
    try:
        earlier, later = selector.select_pair(
            connection,
            state_field="risk_grade",
            earlier_snapshot_id=snapshot_ids[0],
            later_snapshot_id=snapshot_ids[1],
        )
        assert earlier["snapshot_date"] < later["snapshot_date"]
    finally:
        connection.close()


def test_automatic_pair_ambiguity_is_rejected(monkeypatch) -> None:
    records = [
        {
            "snapshot_id": "A",
            "snapshot_date": 1,
            "source_system": "S",
            "identity_grain": "BORROWER",
        },
        {
            "snapshot_id": "B",
            "snapshot_date": 1,
            "source_system": "S",
            "identity_grain": "BORROWER",
        },
        {
            "snapshot_id": "C",
            "snapshot_date": 2,
            "source_system": "S",
            "identity_grain": "BORROWER",
        },
    ]
    monkeypatch.setattr(selector, "candidates", lambda *args, **kwargs: records)
    with pytest.raises(Phase2CPairConflictError, match=PHASE2C_PAIR_CONFLICT):
        selector.select_pair(
            object(),
            state_field="risk_grade",
            source_system="S",
            identity_grain="BORROWER",
        )

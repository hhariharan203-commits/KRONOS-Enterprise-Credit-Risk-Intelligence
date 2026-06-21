from __future__ import annotations

import pytest

from src.temporal_risk.config import CURRENT_WAREHOUSE
from src.temporal_risk.connection import connect_temporal
from src.temporal_risk.contracts import Phase2AValidationError


def test_phase2b_cannot_write_current_warehouse() -> None:
    with pytest.raises(Phase2AValidationError):
        connect_temporal(
            CURRENT_WAREHOUSE,
            read_only=False,
            deployment_authorized=True,
        )

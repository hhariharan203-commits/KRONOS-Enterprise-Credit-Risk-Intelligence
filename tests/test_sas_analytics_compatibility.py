from __future__ import annotations

import hashlib
from pathlib import Path

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.sas_analytics.analytics_runner import (
    run_sas_style_analytics,
)
from src.enterprise_data.sas_analytics.contracts import (
    TEMPORAL_HISTORY_NOT_AVAILABLE,
    temporal_restriction_response,
)
from src.enterprise_data.sas_analytics.source_catalog import (
    ALLOWLISTED_STAGING_SOURCES,
    open_read_only,
    warehouse_row_counts,
    warehouse_signature,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_read_only_runner_preserves_warehouse_contract(tmp_path) -> None:
    database = Path(WAREHOUSE_DB)
    before_hash = _sha256(database)
    connection = open_read_only(database)
    try:
        before_signature = warehouse_signature(connection)
        before_rows = warehouse_row_counts(connection)
    finally:
        connection.close()

    result = run_sas_style_analytics(
        database_path=database,
        output_root=tmp_path,
    )
    assert result["status"] == "SUCCESS"

    connection = open_read_only(database)
    try:
        after_signature = warehouse_signature(connection)
        after_rows = warehouse_row_counts(connection)
    finally:
        connection.close()
    assert _sha256(database) == before_hash
    assert after_signature == before_signature
    assert after_rows == before_rows


def test_staging_allowlist_and_temporal_guard() -> None:
    assert set(ALLOWLISTED_STAGING_SOURCES) == {
        "calibration_deciles",
        "challenger_comparison",
        "challenger_performance",
        "oot_summary",
        "oot_risk_band_shift",
        "oot_score_shift",
    }
    response = temporal_restriction_response("migration analysis")
    assert response["status"] == TEMPORAL_HISTORY_NOT_AVAILABLE

from __future__ import annotations

from src.enterprise_data.config import WAREHOUSE_DB
from src.enterprise_data.risk_marts.source_catalog import open_read_only


def test_typed_model_governance_preserves_artifact_uncertainty() -> None:
    connection = open_read_only(WAREHOUSE_DB)
    try:
        rows = connection.execute(
            """
            SELECT
                model_family,
                artifact_count,
                artifact_match_status,
                approval_status,
                calibration_status,
                governance_status,
                psi,
                roc_auc,
                mae,
                r2_score
            FROM mart.vw_model_governance_current
            ORDER BY model_family
            """
        ).fetchall()
        assert {row[0] for row in rows} == {"PD", "LGD", "EAD"}
        assert all(row[1] == 4 for row in rows)
        assert all(
            row[2] == "UNRESOLVED_CURRENT_ARTIFACTS_DIFFER"
            for row in rows
        )
        assert all(row[5] == "PASSED" for row in rows)

        pd_row = next(row for row in rows if row[0] == "PD")
        assert pd_row[3] == "AMBER"
        assert pd_row[4] == "PASS"
        assert pd_row[6] == 0.001287
        assert pd_row[7] == 0.9068

        lgd_row = next(row for row in rows if row[0] == "LGD")
        ead_row = next(row for row in rows if row[0] == "EAD")
        assert lgd_row[8] == 0.0347
        assert lgd_row[9] == 0.9662
        assert ead_row[8] == 1576.4102
        assert ead_row[9] == 0.9838
    finally:
        connection.close()

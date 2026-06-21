from __future__ import annotations

from src.enterprise_data.sas_analytics.proc_transpose import (
    run_proc_transpose,
)
from src.enterprise_data.sas_analytics.source_catalog import open_read_only


def test_transposed_reporting_pivots_reconcile() -> None:
    connection = open_read_only()
    try:
        pivots = run_proc_transpose(connection)
    finally:
        connection.close()

    assert set(pivots) == {
        "risk_band",
        "ifrs9_stage",
        "industry",
        "region",
        "underwriting_decision",
    }
    for pivot in pivots.values():
        count_row = pivot[pivot["measure"] == "count"].iloc[0]
        ead_row = pivot[pivot["measure"] == "total_ead"].iloc[0]
        assert count_row["TOTAL"] == 50_000
        assert round(ead_row["TOTAL"], 2) == 837_946_260.46

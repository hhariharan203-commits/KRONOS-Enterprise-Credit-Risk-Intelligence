from __future__ import annotations

from src.enterprise_data.sas_analytics.proc_tabulate import run_proc_tabulate
from src.enterprise_data.sas_analytics.source_catalog import open_read_only


def test_dense_cross_tabs_include_totals_and_zero_cells() -> None:
    connection = open_read_only()
    try:
        frame = run_proc_tabulate(connection)
    finally:
        connection.close()

    expected_detail_rows = {
        "industry_by_risk_band": 50,
        "industry_by_ifrs9_stage": 30,
        "region_by_risk_band": 25,
        "risk_grade_by_decision": 28,
    }
    for table_name, row_count in expected_detail_rows.items():
        table = frame[frame["table_name"] == table_name]
        detail = table[table["cell_type"] == "DETAIL"]
        grand = table[table["cell_type"] == "GRAND_TOTAL"].iloc[0]
        assert len(detail) == row_count
        assert detail["count"].sum() == 50_000
        assert round(detail["total_ead"].sum(), 2) == 837_946_260.46
        assert grand["count"] == 50_000
        assert round(grand["total_ead"], 2) == 837_946_260.46

    decision = frame[
        (frame["table_name"] == "risk_grade_by_decision")
        & (frame["cell_type"] == "DETAIL")
    ]
    assert (decision["count"] == 0).any()

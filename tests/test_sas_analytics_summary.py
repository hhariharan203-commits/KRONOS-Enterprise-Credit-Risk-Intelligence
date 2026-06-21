from __future__ import annotations

from src.enterprise_data.sas_analytics.proc_summary import run_proc_summary
from src.enterprise_data.sas_analytics.source_catalog import open_read_only


def test_grouped_summaries_reconcile_to_portfolio() -> None:
    connection = open_read_only()
    try:
        frame = run_proc_summary(connection)
    finally:
        connection.close()

    for dimension in (
        "industry",
        "region",
        "risk_band",
        "risk_grade",
        "ifrs9_stage",
    ):
        subset = frame[frame["dimension"] == dimension]
        detail = subset[subset["category"] != "TOTAL"]
        total = subset[subset["category"] == "TOTAL"].iloc[0]
        assert detail["count"].sum() == 50_000
        assert total["count"] == 50_000
        assert round(detail["total_ead"].sum(), 2) == 837_946_260.46
        assert round(total["total_ead"], 2) == 837_946_260.46
        assert round(
            detail["current_credit_loss_proxy"].sum(),
            2,
        ) == round(total["current_credit_loss_proxy"], 2)

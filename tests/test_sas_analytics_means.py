from __future__ import annotations

from src.enterprise_data.sas_analytics.proc_means import run_proc_means
from src.enterprise_data.sas_analytics.source_catalog import open_read_only


def test_proc_equivalent_means_are_complete_and_reconciled() -> None:
    connection = open_read_only()
    try:
        frame = run_proc_means(connection)
    finally:
        connection.close()

    assert set(frame["metric"]) == {
        "pd",
        "lgd",
        "ead",
        "credit_score",
        "current_credit_loss_proxy",
    }
    assert (frame["n"] == 50_000).all()
    assert (frame["missing"] == 0).all()

    ead = frame[frame["metric"] == "ead"].iloc[0]
    assert round(ead["sum"], 2) == 837_946_260.46

    loss_proxy = frame[
        frame["metric"] == "current_credit_loss_proxy"
    ].iloc[0]
    assert loss_proxy["sum"] > 0
    assert "ecl" not in " ".join(frame["metric"]).lower()

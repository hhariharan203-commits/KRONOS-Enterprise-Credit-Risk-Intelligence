from __future__ import annotations

from src.enterprise_data.sas_analytics.proc_freq import run_proc_freq
from src.enterprise_data.sas_analytics.source_catalog import open_read_only


def test_proc_equivalent_frequencies_reconcile() -> None:
    connection = open_read_only()
    try:
        frame = run_proc_freq(connection)
    finally:
        connection.close()

    expected_categories = {
        "risk_band": 5,
        "risk_grade": 7,
        "industry": 10,
        "region": 5,
        "ifrs9_stage": 3,
    }
    for variable, category_count in expected_categories.items():
        subset = frame[frame["variable"] == variable]
        assert len(subset) == category_count
        assert subset["count"].sum() == 50_000
        assert round(subset["percentage"].sum(), 10) == 100.0
        assert round(subset["cumulative_percentage"].iloc[-1], 10) == 100.0

    watchlist = frame[frame["variable"] == "watchlist_status"]
    assert watchlist.loc[
        watchlist["category"] == "WATCHLIST",
        "count",
    ].iloc[0] == 16_378

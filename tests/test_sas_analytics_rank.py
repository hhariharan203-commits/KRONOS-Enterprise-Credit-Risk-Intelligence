from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.proc_rank import run_proc_rank
from src.enterprise_data.sas_analytics.source_catalog import open_read_only


def test_decile_ranking_is_balanced_and_deterministic() -> None:
    connection = open_read_only()
    try:
        first = run_proc_rank(connection)
        second = run_proc_rank(connection)
    finally:
        connection.close()

    pd.testing.assert_frame_equal(first, second)
    for metric in ("pd", "lgd", "ead", "credit_score"):
        subset = first[first["metric"] == metric]
        assert list(subset["decile"]) == list(range(1, 11))
        assert (subset["count"] == 5_000).all()
        assert subset["count"].sum() == 50_000

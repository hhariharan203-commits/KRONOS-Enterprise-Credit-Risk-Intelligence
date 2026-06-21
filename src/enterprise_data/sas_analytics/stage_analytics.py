from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.contracts import (
    temporal_restriction_response,
)
from src.enterprise_data.sas_analytics.proc_summary import grouped_summary
from src.enterprise_data.sas_analytics.proc_tabulate import dense_table


def stage_distribution(connection) -> pd.DataFrame:
    frame = grouped_summary(connection, "ifrs9_stage")
    total_count = int(frame.loc[frame["category"] == "TOTAL", "count"].iloc[0])
    total_ead = float(
        frame.loc[frame["category"] == "TOTAL", "total_ead"].iloc[0]
    )
    frame["portfolio_share"] = frame["count"] / total_count
    frame["exposure_share"] = frame["total_ead"] / total_ead
    return frame


def stage_risk_composition(connection) -> pd.DataFrame:
    return dense_table(connection, "ifrs9_stage", "risk_band")


def stage_concentration(connection) -> pd.DataFrame:
    stage = stage_distribution(connection)
    detail = stage[stage["category"] != "TOTAL"].copy()
    return pd.DataFrame(
        [
            {
                "stage_count": int(len(detail)),
                "exposure_hhi": float((detail["exposure_share"] ** 2).sum()),
                "largest_stage_exposure_share": float(
                    detail["exposure_share"].max()
                ),
                "stage_2_and_3_exposure_share": float(
                    detail.loc[
                        detail["category"].isin(["STAGE 2", "STAGE 3"]),
                        "exposure_share",
                    ].sum()
                ),
            }
        ]
    )


def request_temporal_stage_analysis(analysis_name: str) -> dict:
    return temporal_restriction_response(analysis_name)


def run_stage_analytics(connection) -> dict[str, pd.DataFrame]:
    return {
        "ifrs9_stage_distribution": stage_distribution(connection),
        "ifrs9_stage_risk_composition": stage_risk_composition(connection),
        "ifrs9_stage_concentration": stage_concentration(connection),
    }

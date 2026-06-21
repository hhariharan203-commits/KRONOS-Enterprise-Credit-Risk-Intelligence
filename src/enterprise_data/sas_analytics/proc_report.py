from __future__ import annotations

import pandas as pd

from src.enterprise_data.sas_analytics.concentration_analytics import (
    concentration_summary,
)
from src.enterprise_data.sas_analytics.model_risk_analytics import (
    governance_summary,
    validation_summary,
)
from src.enterprise_data.sas_analytics.portfolio_analytics import (
    portfolio_summary,
    watchlist_analytics,
)
from src.enterprise_data.sas_analytics.stage_analytics import stage_distribution


def institutional_reports(connection) -> dict[str, pd.DataFrame]:
    concentration = pd.concat(
        [
            concentration_summary(connection, "industry"),
            concentration_summary(connection, "region"),
        ],
        ignore_index=True,
    )
    model_report = governance_summary(connection)
    model_report["validation_records"] = len(validation_summary(connection))
    return {
        "portfolio_summary_report": portfolio_summary(connection),
        "risk_concentration_report": concentration,
        "ifrs9_stage_report": stage_distribution(connection),
        "watchlist_report": watchlist_analytics(connection),
        "model_risk_report": model_report,
    }


def _markdown_value(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")


def _frame_to_markdown(frame: pd.DataFrame) -> str:
    headers = [str(column) for column in frame.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in frame.itertuples(index=False, name=None):
        lines.append(
            "| " + " | ".join(_markdown_value(value) for value in row) + " |"
        )
    return "\n".join(lines)


def reports_to_markdown(reports: dict[str, pd.DataFrame]) -> str:
    sections = [
        "# KRONOS SAS-Style Analytics Institutional Report Pack",
        "",
        (
            "This pack contains PROC-Equivalent Analytics generated from the "
            "read-only KRONOS warehouse. It does not represent SAS runtime "
            "execution."
        ),
        "",
        (
            "The current credit loss proxy is a cross-sectional analytical "
            "measure only. It is not IFRS 9 ECL, a provision, or an accounting "
            "reserve."
        ),
        "",
    ]
    for name, frame in reports.items():
        title = name.replace("_", " ").title()
        sections.extend([f"## {title}", "", _frame_to_markdown(frame), ""])
    return "\n".join(sections)

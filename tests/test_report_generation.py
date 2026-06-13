from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.reporting.report_generator import generate_institutional_report
from src.shared.governance import artifact_lineage, create_governance_context, write_artifact_lineage


def test_institutional_report_generates_real_pdf() -> None:
    portfolio = pd.DataFrame(
        [
            {
                "enterprise_risk_score": 25,
                "systemic_risk_score": 20,
                "capital_ratio": 12.5,
                "stress_score": 22,
                "live_risk_pulse_score": 25,
            },
            {
                "enterprise_risk_score": 72,
                "systemic_risk_score": 68,
                "capital_ratio": 9.2,
                "stress_score": 74,
                "live_risk_pulse_score": 70,
            },
        ]
    )
    result = generate_institutional_report(portfolio, "test_kronos_enterprise_report.pdf")
    pdf_path = Path(result["pdf_report_path"])
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert result["executive_summary"]["portfolio_size"] == 2


def test_governance_artifact_lineage_contract() -> None:
    context = create_governance_context("Tests")
    lineage = artifact_lineage()
    assert context.dashboard_name == "Tests"
    assert {"pd_model", "lgd_model", "ead_model", "scored_portfolio"}.issubset(lineage)
    assert lineage["scored_portfolio"]["exists"] is True
    manifest = write_artifact_lineage()
    assert manifest.exists()

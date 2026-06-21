from __future__ import annotations

import hashlib
from pathlib import Path

from streamlit.testing.v1 import AppTest


WAREHOUSE_DB = Path("data/warehouse/kronos_risk.duckdb")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _assert_section(app: AppTest, text: str) -> None:
    values = [
        str(element.value)
        for element in app.markdown
    ]
    assert any(text in value for value in values)


def test_executive_dashboard_renders_phase4e_without_warehouse_write() -> None:
    before_hash = _sha256(WAREHOUSE_DB)
    app = AppTest.from_string(
        """
import pandas as pd
import app.executive_dashboard as dashboard

dashboard.get_live_intelligence = lambda **kwargs: {
    "macro_intelligence": {},
    "news_intelligence": {},
    "market_intelligence": {},
    "vix_intelligence": {},
    "summary": {},
    "source_freshness": {},
}
dashboard.render_live_status_card = lambda context: None
portfolio = pd.read_csv("data/processed/scored_portfolio.csv").head(100)
dashboard.render({"portfolio": portfolio})
"""
    )
    app.run(timeout=60)
    assert len(app.exception) == 0
    _assert_section(app, "ENTERPRISE DATA & RISK CONTROL")
    _assert_section(app, "MODEL GOVERNANCE STATUS")
    assert _sha256(WAREHOUSE_DB) == before_hash


def test_explainability_dashboard_renders_phase4e_without_warehouse_write() -> None:
    before_hash = _sha256(WAREHOUSE_DB)
    app = AppTest.from_string(
        """
import pandas as pd
import app.explainability_dashboard as dashboard

dashboard.cached_explain_borrower = lambda borrower: {
    "probability_of_default": 0.25,
    "explainability_confidence": 90,
    "risk_narrative": "Test narrative",
}
dashboard.cached_run_shap_pipeline = lambda borrower: {
    "top_drivers": [("pd_score", 0.2), ("ead", -0.1)],
    "executive_summary": "Test SHAP summary",
    "importance_df": pd.DataFrame(
        {"feature": ["pd_score", "ead"], "importance": [0.2, 0.1]}
    ),
}
dashboard.cached_run_feature_analysis = lambda: {
    "feature_importance": pd.DataFrame(
        {
            "feature": ["pd_score", "ead"],
            "importance_pct": [60.0, 40.0],
        }
    ),
    "category_importance": pd.DataFrame(
        {
            "category": ["Credit", "Exposure"],
            "importance_pct": [60.0, 40.0],
        }
    ),
    "summary": "Test feature summary",
}
dashboard.get_dashboard_live_context = lambda **kwargs: {}
dashboard.live_summary = lambda context: {}
dashboard.macro_intelligence = lambda context: {}
dashboard.market_intelligence = lambda context: {}
dashboard.render_live_status_card = lambda context: None
portfolio = pd.read_csv("data/processed/scored_portfolio.csv").head(1)
dashboard.render({"portfolio": portfolio})
"""
    )
    app.run(timeout=60)
    assert len(app.exception) == 0
    _assert_section(app, "ENTERPRISE MODEL GOVERNANCE MART")
    _assert_section(app, "MODEL VALIDATION & GOVERNANCE")
    assert _sha256(WAREHOUSE_DB) == before_hash


def test_reports_dashboard_renders_phase4e_without_warehouse_write() -> None:
    before_hash = _sha256(WAREHOUSE_DB)
    app = AppTest.from_string(
        """
import pandas as pd
import app.reports_dashboard as dashboard

dashboard.get_live_intelligence = lambda **kwargs: {
    "summary": {},
    "macro_intelligence": {},
    "news_intelligence": {},
    "market_intelligence": {},
}
dashboard.render_live_status_card = lambda context: None
portfolio = pd.read_csv("data/processed/scored_portfolio.csv").head(100)
dashboard.render({"portfolio": portfolio})
"""
    )
    app.run(timeout=60)
    assert len(app.exception) == 0
    _assert_section(app, "SAS-STYLE ANALYTICS PACK")
    _assert_section(app, "WAREHOUSE EVIDENCE PACK")
    _assert_section(app, "RISK MART EVIDENCE PACK")
    _assert_section(app, "INSTITUTIONAL VALIDATION PACK")
    assert _sha256(WAREHOUSE_DB) == before_hash

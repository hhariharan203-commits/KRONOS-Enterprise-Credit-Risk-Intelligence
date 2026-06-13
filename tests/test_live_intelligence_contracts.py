from __future__ import annotations

import pandas as pd

from src.live_monitoring.live_alerts import run_live_alert_engine
from src.live_monitoring.live_intelligence import get_live_intelligence
from src.live_monitoring.regime_detector import run_regime_detector
from src.live_monitoring.risk_pulse import run_risk_pulse_engine


def _portfolio() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "borrower_id": "L001",
                "pd_score": 0.08,
                "systemic_risk_score": 12,
                "stress_score": 20,
                "reserve_pressure_score": 18,
                "previous_pulse_score": 15,
            },
            {
                "borrower_id": "L002",
                "pd_score": 0.45,
                "systemic_risk_score": 55,
                "stress_score": 60,
                "reserve_pressure_score": 45,
                "previous_pulse_score": 40,
            },
        ]
    )


def test_live_intelligence_cache_contract() -> None:
    context = get_live_intelligence(allow_api_refresh=False)
    assert {
        "macro_intelligence",
        "market_intelligence",
        "news_intelligence",
        "vix_intelligence",
        "summary",
        "source_freshness",
    }.issubset(context)
    assert "enterprise_live_risk_score" in context["summary"]


def test_live_monitoring_engines_accept_live_context() -> None:
    context = get_live_intelligence(allow_api_refresh=False)

    pulse = run_risk_pulse_engine(_portfolio(), live_context=context)
    assert {
        "macro_stress_score",
        "market_stress_score",
        "sentiment_score",
        "executive_risk_regime",
    }.issubset(pulse["risk_pulse_results"].columns)

    macro = pd.DataFrame(
        [
            {
                "period": "LIVE",
                "gdp_stress": -1.5,
                "inflation_stress": 3.0,
                "unemployment_stress": 4.0,
                "market_volatility": 25,
                "previous_regime_score": 20,
            }
        ]
    )
    regime = run_regime_detector(macro, live_context=context)
    assert {
        "executive_cycle_regime",
        "market_conditions_score",
        "sentiment_conditions_score",
    }.issubset(regime["regime_results"].columns)

    alert_input = _portfolio().merge(
        pulse["risk_pulse_results"][
            [
                "borrower_id",
                "live_risk_pulse_score",
            ]
        ],
        on="borrower_id",
        how="left",
    )
    alert_input["previous_risk_score"] = alert_input["previous_pulse_score"]
    alerts = run_live_alert_engine(alert_input, live_context=context)
    assert {
        "macro_deterioration_alert",
        "market_stress_alert",
        "negative_news_sentiment_alert",
        "executive_alert_level",
    }.issubset(alerts["live_alert_results"].columns)


from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from src.live_monitoring.live_intelligence import get_live_intelligence


def get_dashboard_live_context(
    allow_api_refresh=True
):
    return get_live_intelligence(
        allow_api_refresh=allow_api_refresh
    )


def _format_timestamp(
    value
):
    if not value or value == "UNAVAILABLE":
        return "UNAVAILABLE"

    try:
        parsed = datetime.strptime(
            str(value),
            "%Y-%m-%d %H:%M:%S UTC"
        )
        return parsed.strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    except ValueError:
        return str(value)


def _format_live_value(
    value,
    suffix="",
    decimals=2
):
    if value in {
        None,
        "",
        "UNAVAILABLE",
    }:
        return "UNAVAILABLE"

    try:
        numeric_value = float(value)
    except (TypeError, ValueError):
        return str(value)

    return f"{numeric_value:.{decimals}f}{suffix}"


def _parse_source_timestamp(
    value
):
    if not value or value == "UNAVAILABLE":
        return None

    try:
        parsed = datetime.strptime(
            str(value),
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except ValueError:
        return None

    return parsed.replace(
        tzinfo=timezone.utc
    )


def _source_age_minutes(
    source
):
    timestamp = _parse_source_timestamp(
        source.get("last_updated")
    )

    if timestamp is None:
        return None

    return max(
        (
            datetime.now(timezone.utc) - timestamp
        ).total_seconds() / 60,
        0,
    )


def _source_currently_fresh(
    source
):
    age_minutes = _source_age_minutes(
        source
    )

    if age_minutes is None:
        return False

    try:
        refresh_minutes = float(
            source.get(
                "refresh_minutes",
                0,
            )
        )
    except (TypeError, ValueError):
        return False

    return refresh_minutes > 0 and age_minutes <= refresh_minutes


def _source_label(
    source_name,
    source
):
    status = str(
        source.get(
            "status",
            ""
        )
    )
    is_fresh = _source_currently_fresh(
        source
    )
    has_artifact = (
        source.get("last_updated")
        not in {
            None,
            "",
            "UNAVAILABLE",
        }
    )

    if (
        status == "LIVE_REFRESHED"
        and is_fresh
        and (
            _source_age_minutes(source) or 0
        ) <= 1
    ):
        return "Connected"

    if status == "LIVE_REFRESHED" and is_fresh:
        return "Cached"

    if status == "LIVE_REFRESHED" and has_artifact:
        return "Stale"

    if status in {
        "CACHE_FRESH",
        "CACHE_ONLY",
    } and is_fresh:
        return "Cached"

    if status in {
        "CACHE_FRESH",
        "CACHE_ONLY",
    } and has_artifact:
        return "Stale"

    if status.startswith("CACHE_FALLBACK") and has_artifact:
        return "Fallback"

    if status.startswith("CACHE_FALLBACK"):
        return "Disconnected"

    return "Disconnected"


def render_live_status_card(
    live_context
):
    sources = live_context.get(
        "source_freshness",
        {}
    )
    summary = live_context.get(
        "summary",
        {}
    )

    fred = sources.get("fred", {})
    news = sources.get("news", {})
    market = sources.get("market", {})
    vix = sources.get("vix", {})

    st.markdown("**Live Intelligence Status**")

    cols = st.columns(5)
    cols[0].metric(
        "FRED",
        _source_label("fred", fred)
    )
    cols[1].metric(
        "News",
        _source_label("news", news)
    )
    cols[2].metric(
        "Market",
        _source_label("market", market)
    )
    cols[3].metric(
        "VIX",
        _source_label("vix", vix)
    )
    cols[4].metric(
        "Live Risk",
        f"{summary.get('enterprise_live_risk_score', 0):.2f}"
    )

    st.caption(
        "Last Data Refresh | "
        f"FRED: {_format_timestamp(fred.get('last_updated'))} | "
        f"News: {_format_timestamp(news.get('last_updated'))} | "
        f"Market: {_format_timestamp(market.get('last_updated'))} | "
        f"VIX: {_format_timestamp(vix.get('last_updated'))}"
    )
    st.caption(
        "Current Regime: "
        f"{summary.get('executive_risk_regime', 'UNAVAILABLE')}"
    )

    render_live_market_snapshot(
        live_context
    )


def render_live_market_snapshot(
    live_context
):
    macro = live_context.get(
        "macro_intelligence",
        {}
    )
    market = live_context.get(
        "market_intelligence",
        {}
    )
    vix = live_context.get(
        "vix_intelligence",
        {}
    )
    news = live_context.get(
        "news_intelligence",
        {}
    )

    st.markdown("**Live Market Snapshot**")

    macro_cols = st.columns(4)
    macro_cols[0].metric(
        "Fed Funds",
        _format_live_value(
            macro.get("fed_funds_rate"),
            "%"
        )
    )
    macro_cols[1].metric(
        "10Y Treasury",
        _format_live_value(
            macro.get("treasury_10y"),
            "%"
        )
    )
    macro_cols[2].metric(
        "Unemployment",
        _format_live_value(
            macro.get("unemployment_rate"),
            "%"
        )
    )
    macro_cols[3].metric(
        "CPI Inflation",
        _format_live_value(
            macro.get("inflation_rate"),
            "%"
        )
    )

    market_cols = st.columns(4)
    market_cols[0].metric(
        "SPY",
        _format_live_value(
            market.get("sp500_latest")
        )
    )
    market_cols[1].metric(
        "XLF",
        _format_live_value(
            market.get("financial_sector_latest")
        )
    )
    market_cols[2].metric(
        "Treasury ETF",
        _format_live_value(
            market.get("treasury_etf_latest")
        )
    )
    market_cols[3].metric(
        "Dollar Index",
        _format_live_value(
            market.get("dollar_index_latest")
        )
    )

    signal_cols = st.columns(3)
    signal_cols[0].metric(
        "VIX",
        _format_live_value(
            vix.get("latest_vix")
        )
    )
    signal_cols[1].metric(
        "Market Sentiment",
        _format_live_value(
            news.get("market_sentiment_score")
        )
    )
    signal_cols[2].metric(
        "Sentiment Regime",
        news.get(
            "risk_sentiment_regime",
            "UNAVAILABLE"
        )
    )


def live_summary(
    live_context
):
    return live_context.get(
        "summary",
        {}
    )


def macro_intelligence(
    live_context
):
    return live_context.get(
        "macro_intelligence",
        {}
    )


def market_intelligence(
    live_context
):
    return live_context.get(
        "market_intelligence",
        {}
    )


def news_intelligence(
    live_context
):
    return live_context.get(
        "news_intelligence",
        {}
    )


def vix_intelligence(
    live_context
):
    return live_context.get(
        "vix_intelligence",
        {}
    )

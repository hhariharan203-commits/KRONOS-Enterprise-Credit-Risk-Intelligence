from __future__ import annotations

from datetime import datetime

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
    is_fresh = bool(
        source.get(
            "is_fresh",
            False
        )
    )
    has_artifact = (
        source.get("last_updated")
        not in {
            None,
            "",
            "UNAVAILABLE",
        }
    )

    if status == "LIVE_REFRESHED":
        return "Connected"

    if status in {
        "CACHE_FRESH",
        "CACHE_ONLY",
    } and is_fresh:
        return "Cached"

    if status == "CACHE_ONLY" and has_artifact:
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

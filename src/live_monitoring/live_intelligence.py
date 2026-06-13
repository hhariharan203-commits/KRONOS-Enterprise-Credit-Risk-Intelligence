# =============================================================================
# KRONOS — ENTERPRISE LIVE INTELLIGENCE ORCHESTRATOR
# File: src/live_monitoring/live_intelligence.py
# =============================================================================

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.shared.config import (
    ALPHA_VANTAGE_API_KEY,
    FRED_API_KEY,
    FRED_MARKET_DATA,
    LIVE_DATA_DIR,
    NEWS_API_KEY,
    SENTIMENT_DATA,
    SENTIMENT_SUMMARY_DATA,
    VIX_DATA,
)
from src.shared.logger import get_logger


log = get_logger("kronos.live_intelligence")

LIVE_INTELLIGENCE_CACHE = LIVE_DATA_DIR / "live_intelligence_cache.json"
ALPHA_VANTAGE_MARKET_DATA = LIVE_DATA_DIR / "alpha_vantage_market_data.csv"

REFRESH_MINUTES = {
    "fred": 60,
    "news": 30,
    "sentiment": 30,
    "market": 15,
    "vix": 15,
}


def _utc_now():
    return datetime.now(timezone.utc)


def _timestamp():
    return _utc_now().strftime("%Y-%m-%d %H:%M:%S UTC")


def _safe_read_csv(
    path
):
    try:
        if Path(path).exists():
            return pd.read_csv(path)
    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        log.warning("Could not read live artifact %s: %s", path, exc)

    return pd.DataFrame()


def _artifact_timestamp(
    path
):
    try:
        if Path(path).exists():
            return datetime.fromtimestamp(
                Path(path).stat().st_mtime,
                timezone.utc
            )
    except OSError:
        return None

    return None


def _artifact_fresh(
    path,
    source_name
):
    timestamp = _artifact_timestamp(path)

    if timestamp is None:
        return False

    age_minutes = (
        _utc_now() - timestamp
    ).total_seconds() / 60

    return age_minutes <= REFRESH_MINUTES[source_name]


def _source_status(
    path,
    source_name,
    status
):
    timestamp = _artifact_timestamp(path)

    return {
        "status": status,
        "artifact": str(path),
        "last_updated": (
            timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            if timestamp
            else "UNAVAILABLE"
        ),
        "refresh_minutes": REFRESH_MINUTES[source_name],
        "is_fresh": _artifact_fresh(path, source_name),
    }


def _latest_series_value(
    fred_df,
    series_name
):
    if fred_df.empty or "series_name" not in fred_df.columns:
        return None

    series = fred_df[
        fred_df["series_name"] == series_name
    ].copy()

    if series.empty:
        return None

    series["date"] = pd.to_datetime(
        series["date"],
        errors="coerce"
    )

    series = series.sort_values("date")

    return float(
        series["value"].iloc[-1]
    )


def _series_change_12_periods(
    fred_df,
    series_name
):
    if fred_df.empty or "series_name" not in fred_df.columns:
        return 0

    series = fred_df[
        fred_df["series_name"] == series_name
    ].copy()

    if len(series) < 13:
        return 0

    series["date"] = pd.to_datetime(
        series["date"],
        errors="coerce"
    )
    series = series.sort_values("date")

    current = float(series["value"].iloc[-1])
    prior = float(series["value"].iloc[-13])

    if prior == 0:
        return 0

    return round(
        ((current - prior) / prior) * 100,
        2
    )


def _score_band(
    score
):
    if score < 25:
        return "LOW"
    if score < 50:
        return "MODERATE"
    if score < 75:
        return "HIGH"
    return "CRITICAL"


def _regime_from_score(
    score
):
    if score < 15:
        return "EXPANSION"
    if score < 35:
        return "NORMAL"
    if score < 55:
        return "SLOWDOWN"
    if score < 75:
        return "RISK-OFF"
    if score < 90:
        return "STRESS"
    return "CRISIS"


def _sentiment_regime(
    score
):
    if score >= 65:
        return "BULLISH"
    if score >= 45:
        return "NEUTRAL"
    if score >= 30:
        return "BEARISH"
    if score >= 15:
        return "STRESS"
    return "CRISIS"


def _headline_score(
    sentiment_df,
    keywords,
    fallback
):
    if sentiment_df.empty or "headline" not in sentiment_df.columns:
        return fallback

    mask = sentiment_df["headline"].astype(str).str.contains(
        "|".join(keywords),
        case=False,
        regex=True,
        na=False
    )

    subset = sentiment_df[mask]

    if subset.empty or "polarity" not in subset.columns:
        return fallback

    polarity = pd.to_numeric(
        subset["polarity"],
        errors="coerce"
    ).dropna()

    if polarity.empty:
        return fallback

    return round(
        float((polarity.mean() + 1) * 50),
        2
    )


def _refresh_fred(
    force_refresh
):
    if not force_refresh and _artifact_fresh(FRED_MARKET_DATA, "fred"):
        return "CACHE_FRESH"

    if not FRED_API_KEY:
        return "CACHE_FALLBACK_API_KEY_MISSING"

    try:
        from src.data_pipeline.fetch_fred import fetch_all_fred_data

        frame = fetch_all_fred_data()

        if frame.empty:
            return "CACHE_FALLBACK_API_EMPTY"

        frame.to_csv(
            FRED_MARKET_DATA,
            index=False
        )
        return "LIVE_REFRESHED"

    except Exception as exc:
        log.warning("FRED refresh failed: %s", exc)
        return "CACHE_FALLBACK_API_FAILED"


def _refresh_news(
    force_refresh
):
    if (
        not force_refresh
        and _artifact_fresh(SENTIMENT_SUMMARY_DATA, "sentiment")
    ):
        return "CACHE_FRESH"

    if not NEWS_API_KEY:
        return "CACHE_FALLBACK_API_KEY_MISSING"

    try:
        from src.data_pipeline.fetch_sentiment import (
            analyze_all_headlines,
            fetch_live_headlines,
            generate_sentiment_summary,
            save_sentiment_data,
        )

        headlines = fetch_live_headlines()

        if len(headlines) == 0:
            return "CACHE_FALLBACK_API_EMPTY"

        sentiment_df = analyze_all_headlines(
            headlines
        )

        if sentiment_df.empty:
            return "CACHE_FALLBACK_SENTIMENT_EMPTY"

        save_sentiment_data(
            sentiment_df
        )
        generate_sentiment_summary(
            sentiment_df
        )

        return "LIVE_REFRESHED"

    except Exception as exc:
        log.warning("News refresh failed: %s", exc)
        return "CACHE_FALLBACK_API_FAILED"


def _refresh_market(
    force_refresh
):
    if (
        not force_refresh
        and _artifact_fresh(ALPHA_VANTAGE_MARKET_DATA, "market")
    ):
        return "CACHE_FRESH"

    if not ALPHA_VANTAGE_API_KEY:
        return "CACHE_FALLBACK_API_KEY_MISSING"

    try:
        from src.data_pipeline.fetch_alpha_vantage import (
            fetch_alpha_vantage_market_data,
            save_alpha_vantage_market_data,
        )

        market_df = fetch_alpha_vantage_market_data()

        if market_df.empty:
            return "CACHE_FALLBACK_API_EMPTY"

        save_alpha_vantage_market_data(
            market_df
        )

        return "LIVE_REFRESHED"

    except Exception as exc:
        log.warning("Alpha Vantage refresh failed: %s", exc)
        return "CACHE_FALLBACK_API_FAILED"


def _refresh_vix(
    force_refresh
):
    if not force_refresh and _artifact_fresh(VIX_DATA, "vix"):
        return "CACHE_FRESH"

    try:
        from src.data_pipeline.fetch_vix import (
            calculate_rolling_volatility,
            fetch_vix_data,
            save_vix_data,
        )

        vix_df = fetch_vix_data()

        if vix_df.empty:
            return "CACHE_FALLBACK_API_EMPTY"

        vix_df = calculate_rolling_volatility(
            vix_df
        )
        save_vix_data(
            vix_df
        )

        return "LIVE_REFRESHED"

    except Exception as exc:
        log.warning("VIX refresh failed: %s", exc)
        return "CACHE_FALLBACK_API_FAILED"


def build_fred_intelligence(
    fred_df
):
    fed_funds = _latest_series_value(
        fred_df,
        "fed_funds_rate"
    )
    unemployment = _latest_series_value(
        fred_df,
        "unemployment_rate"
    )
    treasury_10y = _latest_series_value(
        fred_df,
        "10y_treasury"
    )
    treasury_2y = _latest_series_value(
        fred_df,
        "2y_treasury"
    )
    aaa = _latest_series_value(
        fred_df,
        "aaa_corporate_yield"
    )
    bbb = _latest_series_value(
        fred_df,
        "bbb_corporate_yield"
    )
    recession = _latest_series_value(
        fred_df,
        "recession_indicator"
    )
    consumer_sentiment = _latest_series_value(
        fred_df,
        "consumer_sentiment"
    )
    inflation = _series_change_12_periods(
        fred_df,
        "cpi"
    )

    yield_curve = (
        round(treasury_10y - treasury_2y, 2)
        if treasury_10y is not None and treasury_2y is not None
        else None
    )
    credit_spread = (
        round(bbb - aaa, 2)
        if bbb is not None and aaa is not None
        else None
    )

    score = 0
    if fed_funds is not None and fed_funds > 5:
        score += 15
    if unemployment is not None and unemployment > 5:
        score += 20
    if inflation is not None and inflation > 4:
        score += 20
    if yield_curve is not None and yield_curve < 0:
        score += 25
    if credit_spread is not None and credit_spread > 2:
        score += 10
    if recession is not None and recession >= 1:
        score += 30

    score = min(score, 100)

    return {
        "fed_funds_rate": fed_funds,
        "inflation_rate": inflation,
        "unemployment_rate": unemployment,
        "treasury_10y": treasury_10y,
        "treasury_2y": treasury_2y,
        "yield_curve_spread": yield_curve,
        "credit_spread": credit_spread,
        "consumer_sentiment": consumer_sentiment,
        "recession_indicator": recession,
        "macro_stress_score": score,
        "economic_stress": _score_band(score),
        "recession_risk": _score_band(score + (15 if recession else 0)),
        "credit_conditions": (
            "TIGHTENING"
            if score >= 50
            else "NORMAL"
        ),
        "macro_regime": _regime_from_score(score),
    }


def build_sentiment_intelligence(
    summary_df,
    sentiment_df
):
    if summary_df.empty:
        market_score = 50
        stress_score = 50
        source_regime = "NEUTRAL"
        bullish = bearish = neutral = 0
    else:
        row = summary_df.iloc[0]
        market_score = float(row.get("market_sentiment_score", 50))
        stress_score = float(row.get("stress_score", 100 - market_score))
        source_regime = str(row.get("sentiment_regime", "NEUTRAL"))
        bullish = int(row.get("bullish_headlines", 0))
        bearish = int(row.get("bearish_headlines", 0))
        neutral = int(row.get("neutral_headlines", 0))

    credit_score = _headline_score(
        sentiment_df,
        ["credit", "default", "loan", "bank", "delinquency"],
        market_score
    )
    economic_score = _headline_score(
        sentiment_df,
        ["economy", "inflation", "recession", "rates", "unemployment"],
        market_score
    )
    financial_stress = round(
        100 - min(market_score, credit_score, economic_score),
        2
    )

    return {
        "market_sentiment_score": round(market_score, 2),
        "credit_sentiment_score": round(credit_score, 2),
        "economic_sentiment_score": round(economic_score, 2),
        "financial_stress_score": financial_stress,
        "sentiment_stress_score": round(stress_score, 2),
        "risk_sentiment_regime": _sentiment_regime(market_score),
        "source_sentiment_regime": source_regime,
        "bullish_headlines": bullish,
        "bearish_headlines": bearish,
        "neutral_headlines": neutral,
    }


def build_vix_intelligence(
    vix_df
):
    if vix_df.empty or "close_^vix" not in vix_df.columns:
        latest_vix = 0
    else:
        vix_values = pd.to_numeric(
            vix_df["close_^vix"],
            errors="coerce"
        ).dropna()

        latest_vix = (
            float(vix_values.iloc[-1])
            if not vix_values.empty
            else 0
        )

    volatility_score = min(
        round(latest_vix * 2.5, 2),
        100
    )

    return {
        "latest_vix": round(latest_vix, 2),
        "volatility_score": volatility_score,
        "vix_regime": _score_band(volatility_score),
    }


def _instrument_return(
    market_df,
    instrument,
    periods
):
    if market_df.empty or "instrument" not in market_df.columns:
        return 0

    frame = market_df[
        market_df["instrument"] == instrument
    ].copy()

    if frame.empty or len(frame) <= periods:
        return 0

    frame["date"] = pd.to_datetime(
        frame["date"],
        errors="coerce"
    )
    frame = frame.sort_values("date")
    close = pd.to_numeric(
        frame["close"],
        errors="coerce"
    ).dropna()

    if len(close) <= periods or close.iloc[-periods - 1] == 0:
        return 0

    return round(
        (
            close.iloc[-1] / close.iloc[-periods - 1]
            - 1
        ) * 100,
        2
    )


def build_market_intelligence(
    market_df,
    vix_intelligence
):
    sp500_5d = _instrument_return(
        market_df,
        "sp500",
        5
    )
    financial_5d = _instrument_return(
        market_df,
        "financial_sector",
        5
    )
    bank_5d = _instrument_return(
        market_df,
        "bank_etf",
        5
    )
    treasury_5d = _instrument_return(
        market_df,
        "treasury_etf",
        5
    )
    dollar_5d = _instrument_return(
        market_df,
        "dollar_index",
        5
    )

    drawdown_stress = max(0, -sp500_5d * 5)
    financial_stress = max(0, -financial_5d * 6)
    bank_stress = max(0, -bank_5d * 6)
    liquidity_stress = max(0, dollar_5d * 4) + max(0, -treasury_5d * 2)

    volatility_score = vix_intelligence["volatility_score"]
    market_risk_score = min(
        round(
            drawdown_stress * 0.25
            + financial_stress * 0.25
            + bank_stress * 0.25
            + liquidity_stress * 0.10
            + volatility_score * 0.15,
            2
        ),
        100
    )

    return {
        "sp500_5d_return": sp500_5d,
        "financial_sector_5d_return": financial_5d,
        "bank_etf_5d_return": bank_5d,
        "treasury_etf_5d_return": treasury_5d,
        "dollar_index_5d_return": dollar_5d,
        "market_risk_score": market_risk_score,
        "volatility_score": volatility_score,
        "liquidity_stress_score": min(round(liquidity_stress, 2), 100),
        "market_regime": _regime_from_score(market_risk_score),
    }


def _write_cache(
    context
):
    try:
        LIVE_INTELLIGENCE_CACHE.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        LIVE_INTELLIGENCE_CACHE.write_text(
            json.dumps(context, indent=2, default=str),
            encoding="utf-8"
        )
    except OSError as exc:
        log.warning("Could not write live intelligence cache: %s", exc)


def get_live_intelligence(
    force_refresh=False,
    allow_api_refresh=False
):
    """
    Return cached enterprise live intelligence with graceful API fallback.
    """

    if allow_api_refresh:
        fred_status = _refresh_fred(
            force_refresh
        )
        news_status = _refresh_news(
            force_refresh
        )
        market_status = _refresh_market(
            force_refresh
        )
        vix_status = _refresh_vix(
            force_refresh
        )
    else:
        fred_status = "CACHE_ONLY"
        news_status = "CACHE_ONLY"
        market_status = "CACHE_ONLY"
        vix_status = "CACHE_ONLY"

    fred_df = _safe_read_csv(
        FRED_MARKET_DATA
    )
    sentiment_summary_df = _safe_read_csv(
        SENTIMENT_SUMMARY_DATA
    )
    sentiment_df = _safe_read_csv(
        SENTIMENT_DATA
    )
    vix_df = _safe_read_csv(
        VIX_DATA
    )
    alpha_df = _safe_read_csv(
        ALPHA_VANTAGE_MARKET_DATA
    )

    macro = build_fred_intelligence(
        fred_df
    )
    news = build_sentiment_intelligence(
        sentiment_summary_df,
        sentiment_df
    )
    vix = build_vix_intelligence(
        vix_df
    )
    market = build_market_intelligence(
        alpha_df,
        vix
    )

    enterprise_live_risk_score = min(
        round(
            macro["macro_stress_score"] * 0.30
            + market["market_risk_score"] * 0.30
            + news["financial_stress_score"] * 0.25
            + vix["volatility_score"] * 0.15,
            2
        ),
        100
    )

    summary = {
        "enterprise_live_risk_score": enterprise_live_risk_score,
        "executive_risk_regime": _regime_from_score(
            enterprise_live_risk_score
        ),
        "macro_stress_score": macro["macro_stress_score"],
        "market_stress_score": market["market_risk_score"],
        "sentiment_score": news["market_sentiment_score"],
        "sentiment_stress_score": news["financial_stress_score"],
        "volatility_score": vix["volatility_score"],
        "liquidity_stress_score": market["liquidity_stress_score"],
        "portfolio_risk_context": (
            "Live external conditions are supportive"
            if enterprise_live_risk_score < 35
            else "Live external conditions require enhanced monitoring"
            if enterprise_live_risk_score < 65
            else "Live external conditions require executive risk review"
        ),
        "generated_at": _timestamp(),
    }

    context = {
        "macro_intelligence": macro,
        "news_intelligence": news,
        "market_intelligence": market,
        "vix_intelligence": vix,
        "summary": summary,
        "source_freshness": {
            "fred": _source_status(
                FRED_MARKET_DATA,
                "fred",
                fred_status
            ),
            "news": _source_status(
                SENTIMENT_DATA,
                "news",
                news_status
            ),
            "sentiment": _source_status(
                SENTIMENT_SUMMARY_DATA,
                "sentiment",
                news_status
            ),
            "market": _source_status(
                ALPHA_VANTAGE_MARKET_DATA,
                "market",
                market_status
            ),
            "vix": _source_status(
                VIX_DATA,
                "vix",
                vix_status
            ),
        },
    }

    _write_cache(
        context
    )

    return context

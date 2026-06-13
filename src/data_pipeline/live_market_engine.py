# =============================================================================
# KRONOS — LIVE MARKET INTELLIGENCE ENGINE
# File: src/data_pipeline/live_market_engine.py
# =============================================================================

import pandas as pd
from datetime import datetime

from src.data_pipeline.fetch_fred import (
    fetch_all_fred_data,
    detect_macro_regime,
)

from src.data_pipeline.fetch_vix import (
    fetch_vix_data,
    volatility_summary,
    detect_stress_signal,
)

from src.data_pipeline.fetch_sentiment import (
    fetch_live_headlines,
    analyze_all_headlines,
    generate_sentiment_summary,
)

# =============================================================================
# BUILD LIVE MACRO SNAPSHOT
# =============================================================================

def build_macro_snapshot(fred_df):
    """
    Extract latest macro indicators.
    """

    latest = (
        fred_df
        .sort_values("date")
        .groupby("series_name")
        .tail(1)
    )

    snapshot = {}

    for _, row in latest.iterrows():

        snapshot[row["series_name"]] = row["value"]

    return snapshot

# =============================================================================
# BUILD VIX SNAPSHOT
# =============================================================================

def build_vix_snapshot(vix_df):
    """
    Extract latest VIX intelligence.
    """

    vix_summary = volatility_summary(vix_df)

    latest_vix = vix_summary["latest_vix"]

    stress_signal = detect_stress_signal(latest_vix)

    snapshot = {
        "latest_vix": latest_vix,
        "volatility_regime": vix_summary["regime"],
        "fear_score": vix_summary["fear_score"],
        "stress_signal": stress_signal,
    }

    return snapshot

# =============================================================================
# BUILD SENTIMENT SNAPSHOT
# =============================================================================

def build_sentiment_snapshot():
    """
    Build live sentiment intelligence.
    """

    headlines = fetch_live_headlines()

    if len(headlines) == 0:

        print(
            "[KRONOS WARNING] No live headlines available"
        )

        return {

            "market_sentiment_score": 50,

            "stress_score": 50,

            "sentiment_regime": "NEUTRAL",

            "bullish_headlines": 0,

            "bearish_headlines": 0,

            "neutral_headlines": 0,
        }

    sentiment_df = analyze_all_headlines(
        headlines
    )

    summary = generate_sentiment_summary(
        sentiment_df
    )

    return summary

# =============================================================================
# MARKET REGIME ENGINE
# =============================================================================

def unified_market_regime(
    macro_regime,
    volatility_regime,
    sentiment_regime
):
    """
    Generate unified market regime.
    """

    # Severe risk conditions
    if (
        volatility_regime == "CRISIS VOLATILITY"
        or sentiment_regime == "SEVERE RISK-OFF"
    ):

        return "GLOBAL RISK-OFF"

    # Tightening / inflationary stress
    elif macro_regime == "TIGHTENING":

        return "MONETARY TIGHTENING"

    # Positive market environment
    elif (
        sentiment_regime in [
            "STRONG RISK-ON",
            "MODERATE RISK-ON"
        ]
        and volatility_regime == "LOW VOLATILITY"
    ):

        return "RISK-ON EXPANSION"

    # Recession conditions
    elif macro_regime == "RECESSION RISK":

        return "RECESSION WATCH"

    else:

        return "NEUTRAL MARKET REGIME"

# =============================================================================
# CREDIT CYCLE SIGNAL
# =============================================================================

def credit_cycle_signal(
    macro_regime,
    stress_signal,
    sentiment_regime
):

    if (
        macro_regime == "RECESSION RISK"
        or stress_signal == "SEVERE MARKET STRESS"
    ):

        return "CREDIT DETERIORATION"

    elif sentiment_regime in [
        "STRONG RISK-ON",
        "MODERATE RISK-ON"
    ]:

        return "CREDIT EXPANSION"

    return "STABLE CREDIT CONDITIONS"

# =============================================================================
# EXECUTIVE MARKET SUMMARY
# =============================================================================

def executive_market_summary(
    macro_snapshot,
    vix_snapshot,
    sentiment_snapshot,
    final_regime
):
    """
    Generate executive-level intelligence summary.
    """

    summary = {

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "market_regime":
            final_regime,

        "fed_funds_rate":
            round(
                macro_snapshot.get(
                    "fed_funds_rate",
                    0
                ),
                2
            ),

        "unemployment_rate":
            round(
                macro_snapshot.get(
                    "unemployment_rate",
                    0
                ),
                2
            ),

        "latest_vix":
            round(
                vix_snapshot.get(
                    "latest_vix",
                    0
                ),
                2
            ),

        "fear_score":
            round(
                vix_snapshot.get(
                    "fear_score",
                    0
                ),
                2
            ),

        "market_sentiment_score":
            round(
                sentiment_snapshot.get(
                    "market_sentiment_score",
                    0
                ),
                2
            ),

        "stress_score":
            round(
                sentiment_snapshot.get(
                    "stress_score",
                    0
                ),
                2
            ),

        "bullish_headlines":
            sentiment_snapshot.get(
                "bullish_headlines",
                0
            ),

        "bearish_headlines":
            sentiment_snapshot.get(
                "bearish_headlines",
                0
            ),

        "neutral_headlines":
            sentiment_snapshot.get(
                "neutral_headlines",
                0
            ),

        "stress_signal":
            vix_snapshot.get(
                "stress_signal",
                "UNKNOWN"
            ),
    }

    return summary

# =============================================================================
# MASTER LIVE MARKET ENGINE
# =============================================================================

def run_live_market_engine():
    """
    Run complete KRONOS live intelligence pipeline.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING LIVE MARKET INTELLIGENCE ENGINE")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # FETCH LIVE MACRO DATA
    # -------------------------------------------------------------------------

    fred_df = fetch_all_fred_data()

    macro_snapshot = build_macro_snapshot(fred_df)

    macro_regime = detect_macro_regime(fred_df)

    # -------------------------------------------------------------------------
    # FETCH LIVE VIX DATA
    # -------------------------------------------------------------------------

    vix_df = fetch_vix_data()

    vix_snapshot = build_vix_snapshot(vix_df)

    # -------------------------------------------------------------------------
    # FETCH SENTIMENT DATA
    # -------------------------------------------------------------------------

    sentiment_snapshot = build_sentiment_snapshot()

    # -------------------------------------------------------------------------
    # UNIFIED MARKET REGIME
    # -------------------------------------------------------------------------

    final_regime = unified_market_regime(
        macro_regime=macro_regime,
        volatility_regime=vix_snapshot["volatility_regime"],
        sentiment_regime=sentiment_snapshot["sentiment_regime"],
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------

    executive_summary = executive_market_summary(
        macro_snapshot=macro_snapshot,
        vix_snapshot=vix_snapshot,
        sentiment_snapshot=sentiment_snapshot,
        final_regime=final_regime,
    )

    executive_summary[
        "credit_cycle_signal"
    ] = credit_cycle_signal(
        macro_regime,
        vix_snapshot["stress_signal"],
        sentiment_snapshot["sentiment_regime"]
    )

    print("\n" + "=" * 80)
    print("[KRONOS] EXECUTIVE MARKET SUMMARY")
    print("=" * 80)

    for key, value in executive_summary.items():

        print(f"{key}: {value}")

    print("=" * 80)

    return {

        "macro_data":
            macro_snapshot,

        "vix_data":
            vix_snapshot,

        "sentiment_data":
            sentiment_snapshot,

        "market_regime":
            final_regime,

        "credit_cycle_signal":
            executive_summary[
                "credit_cycle_signal"
            ],

        "executive_summary":
            executive_summary,
    }

# =============================================================================
# SAVE EXECUTIVE SUMMARY
# =============================================================================

def save_market_summary(summary):

    output_file = (
        "data/live/live_market_summary.csv"
    )

    pd.DataFrame(
        [summary]
    ).to_csv(
        output_file,
        index=False
    )

    print(
        "\n[KRONOS] Market summary saved:"
    )

    print(output_file)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    results = run_live_market_engine()

    print("\n[KRONOS] LIVE MARKET ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
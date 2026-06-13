# =============================================================================
# KRONOS — LIVE VIX VOLATILITY ENGINE
# File: src/data_pipeline/fetch_vix.py
# =============================================================================

import pandas as pd
import yfinance as yf
from fredapi import Fred
from datetime import datetime

from src.shared.config import (
    FRED_API_KEY,
    VIX_DATA
)
from src.shared.logger import get_logger


log = get_logger("kronos.fetch_vix")

# =============================================================================
# FETCH VIX DATA
# =============================================================================

def fetch_vix_data(period="5y"):
    """
    Fetch historical + latest VIX data.
    """

    try:

        print("\n" + "=" * 70)
        print("[KRONOS] FETCHING VIX DATA")
        print("=" * 70)

        vix = yf.download(
            "^VIX",
            period=period,
            auto_adjust=False
        )

        if vix.empty:

            print("[KRONOS WARNING] No VIX data retrieved from yfinance")

            return fetch_vix_from_fred()

        vix.reset_index(inplace=True)

        clean_columns = []

        for col in vix.columns:

            if isinstance(col, tuple):

                col_name = "_".join(
                    str(x)
                    for x in col
                    if str(x) != ""
                )

            else:

                col_name = str(col)

            clean_columns.append(
                col_name
                .lower()
                .replace(" ", "_")
                .replace("-", "_")
            )

        vix.columns = clean_columns

        print(
            f"[KRONOS] VIX records fetched: {len(vix):,}"
        )

        print(
            f"[KRONOS] Columns: {list(vix.columns)}"
        )

        return vix

    except Exception as exc:

        print(
            "[KRONOS WARNING] yfinance VIX refresh failed; trying FRED fallback"
        )

        log.warning(
            "yfinance VIX refresh failed: %s",
            exc.__class__.__name__
        )

        return fetch_vix_from_fred()


def fetch_vix_from_fred(start_date="2015-01-01"):
    """
    Fetch VIX from FRED VIXCLS and map it to the existing VIX artifact schema.
    """

    if not FRED_API_KEY:

        log.warning("FRED VIX fallback unavailable: API key missing")

        return pd.DataFrame()

    try:

        fred = Fred(api_key=FRED_API_KEY)
        series = fred.get_series(
            "VIXCLS",
            observation_start=start_date
        )

        vix = pd.DataFrame(series)
        vix.columns = ["close_^vix"]
        vix.index.name = "date"
        vix.reset_index(inplace=True)
        vix = vix.dropna(
            subset=["close_^vix"]
        )

        if vix.empty:

            log.warning("FRED VIX fallback returned no records")

            return pd.DataFrame()

        for col in [
            "adj_close_^vix",
            "high_^vix",
            "low_^vix",
            "open_^vix",
        ]:

            vix[col] = vix["close_^vix"]

        vix["volume_^vix"] = 0
        vix = vix[
            [
                "date",
                "adj_close_^vix",
                "close_^vix",
                "high_^vix",
                "low_^vix",
                "open_^vix",
                "volume_^vix",
            ]
        ]

        print(
            f"[KRONOS] VIX records fetched from FRED: {len(vix):,}"
        )

        return vix

    except Exception as exc:

        log.warning(
            "FRED VIX fallback failed: %s",
            exc.__class__.__name__
        )

        return pd.DataFrame()

# =============================================================================
# VOLATILITY REGIME CLASSIFICATION
# =============================================================================

def classify_vix_regime(vix_value):
    """
    Classify market volatility regime.
    """

    if vix_value < 15:

        return "LOW VOLATILITY"

    elif vix_value < 25:

        return "NORMAL VOLATILITY"

    elif vix_value < 35:

        return "HIGH VOLATILITY"

    else:

        return "CRISIS VOLATILITY"

# =============================================================================
# MARKET FEAR LEVEL
# =============================================================================

def market_fear_score(vix_value):
    """
    Convert VIX into fear score.
    """

    score = min(max(vix_value * 2.5, 0), 100)

    return round(score, 2)

# =============================================================================
# VOLATILITY SUMMARY
# =============================================================================

def volatility_summary(vix_df):
    """
    Generate VIX intelligence summary.
    """

    latest = vix_df.iloc[-1]

    latest_vix = float(
    latest["close_^vix"]
)
    regime = classify_vix_regime(latest_vix)

    fear_score = market_fear_score(latest_vix)

    summary = {
        "latest_vix": round(latest_vix, 2),
        "regime": regime,
        "fear_score": fear_score,
    }

    print("\n[KRONOS] VOLATILITY SUMMARY")

    print(summary)

    return summary

# =============================================================================
# SAVE VIX DATA
# =============================================================================

def save_vix_data(df):
    """
    Save VIX dataset.
    """

    df.to_csv(VIX_DATA, index=False)

    print(f"\n[KRONOS] VIX data saved:")
    print(VIX_DATA)

# =============================================================================
# ROLLING VOLATILITY
# =============================================================================

def calculate_rolling_volatility(df, window=30):
    """
    Calculate rolling volatility metrics.
    """

    close_col = "close_^vix"

    df["returns"] = (
        df[close_col]
        .pct_change()
    )

    df["rolling_volatility"] = (
        df["returns"]
        .rolling(window=window)
        .std()
        * (252 ** 0.5)
    )

    print(
        "[KRONOS] Rolling volatility calculated"
    )

    return df

# =============================================================================
# STRESS SIGNAL DETECTION
# =============================================================================

def detect_stress_signal(vix_value):
    """
    Detect market stress condition.
    """

    if vix_value >= 40:

        return "SEVERE MARKET STRESS"

    elif vix_value >= 30:

        return "ELEVATED MARKET STRESS"

    elif vix_value >= 20:

        return "MODERATE RISK"

    else:

        return "NORMAL MARKET CONDITIONS"

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    vix_df = fetch_vix_data()

    if not vix_df.empty:

        vix_df = calculate_rolling_volatility(vix_df)

        save_vix_data(vix_df)

        summary = volatility_summary(vix_df)

        stress_signal = detect_stress_signal(
            summary["latest_vix"]
        )

        print(f"\n[KRONOS] Stress Signal: {stress_signal}")

        print("\n[KRONOS] VIX ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================

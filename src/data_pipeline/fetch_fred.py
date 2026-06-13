# =============================================================================
# KRONOS — LIVE FRED MACRO DATA ENGINE
# File: src/data_pipeline/fetch_fred.py
# =============================================================================

import pandas as pd
from fredapi import Fred
from datetime import datetime

from src.shared.config import (
    FRED_API_KEY,
    FRED_MARKET_DATA
)

# =============================================================================
# INITIALIZE FRED CLIENT
# =============================================================================

def initialize_fred():
    """
    Initialize FRED API client.
    """

    try:

        fred = Fred(api_key=FRED_API_KEY)

        print("[KRONOS] FRED API initialized")

        return fred

    except Exception as e:

        print("[KRONOS ERROR] Failed to initialize FRED API")
        print(e)

        return None

# =============================================================================
# FRED SERIES MAP
# =============================================================================

FRED_SERIES = {

    "fed_funds_rate": "FEDFUNDS",

    "cpi": "CPIAUCSL",

    "core_cpi": "CPILFESL",

    "unemployment_rate": "UNRATE",

    "real_gdp": "GDPC1",

    "industrial_production": "INDPRO",

    "10y_treasury": "GS10",

    "2y_treasury": "GS2",

    "aaa_corporate_yield": "AAA",

    "bbb_corporate_yield": "BAA",

    "initial_jobless_claims": "ICSA",

    "consumer_sentiment": "UMCSENT",

    "recession_indicator": "USREC"
}

# =============================================================================
# FETCH SINGLE SERIES
# =============================================================================

def fetch_series(fred, series_id, start_date="2015-01-01"):
    """
    Fetch a single FRED time series.
    """

    try:

        data = fred.get_series(
            series_id,
            observation_start=start_date
        )

        df = pd.DataFrame(data)

        df.columns = ["value"]

        df.index.name = "date"

        df.reset_index(inplace=True)

        return df

    except Exception as e:

        print(f"[KRONOS ERROR] Failed fetching series: {series_id}")
        print(e)

        return pd.DataFrame()

# =============================================================================
# FETCH ALL FRED DATA
# =============================================================================

def fetch_all_fred_data():
    """
    Fetch all configured FRED macro series.
    """

    fred = initialize_fred()

    if fred is None:

        return pd.DataFrame()

    all_data = []

    print("\n" + "=" * 70)
    print("[KRONOS] FETCHING LIVE FRED DATA")
    print("=" * 70)

    for name, series_id in FRED_SERIES.items():

        print(f"[KRONOS] Fetching: {name}")

        df = fetch_series(fred, series_id)

        if df.empty:

            continue

        df["series_name"] = name

        df["series_id"] = series_id

        all_data.append(df)

    if not all_data:

        print("[KRONOS ERROR] No FRED data retrieved")

        return pd.DataFrame()

    final_df = pd.concat(
        all_data,
        ignore_index=True
    )

    print(f"\n[KRONOS] Total records fetched: {len(final_df)}")

    return final_df

# =============================================================================
# TREASURY SPREAD CALCULATION
# =============================================================================

def calculate_treasury_spread(df):
    """
    Calculate 10Y - 2Y treasury spread.
    """

    try:

        treasury_10y = df[
            df["series_name"] == "10y_treasury"
        ][["date", "value"]]

        treasury_2y = df[
            df["series_name"] == "2y_treasury"
        ][["date", "value"]]

        treasury_10y.rename(
            columns={"value": "treasury_10y"},
            inplace=True
        )

        treasury_2y.rename(
            columns={"value": "treasury_2y"},
            inplace=True
        )

        spread_df = treasury_10y.merge(
            treasury_2y,
            on="date",
            how="inner"
        )

        spread_df["yield_curve_spread"] = (
            spread_df["treasury_10y"]
            - spread_df["treasury_2y"]
        )

        print("[KRONOS] Treasury spread calculated")

        return spread_df

    except Exception as e:

        print("[KRONOS ERROR] Treasury spread calculation failed")
        print(e)

        return pd.DataFrame()

def calculate_credit_spread(df):

    try:

        aaa = df[
            df["series_name"] == "aaa_corporate_yield"
        ][["date", "value"]]

        baa = df[
            df["series_name"] == "bbb_corporate_yield"
        ][["date", "value"]]

        aaa = aaa.rename(
            columns={"value": "aaa_yield"}
        )

        baa = baa.rename(
            columns={"value": "bbb_yield"}
        )

        spread = aaa.merge(
            baa,
            on="date",
            how="inner"
        )

        spread["credit_spread"] = (
            spread["bbb_yield"]
            - spread["aaa_yield"]
        )

        print(
            "[KRONOS] Credit spread calculated"
        )

        return spread

    except Exception as e:

        print(
            "[KRONOS ERROR] Credit spread calculation failed"
        )

        print(e)

        return pd.DataFrame()

def calculate_macro_stress_score(df):

    latest = (
        df.sort_values("date")
        .groupby("series_name")
        .tail(1)
    )

    score = 0

    try:

        unemployment = latest[
            latest["series_name"]
            == "unemployment_rate"
        ]["value"].values[0]

        fed_rate = latest[
            latest["series_name"]
            == "fed_funds_rate"
        ]["value"].values[0]

        if unemployment > 5:

            score += 25

        if fed_rate > 5:

            score += 20

    except (IndexError, KeyError, TypeError, ValueError):

        pass

    return min(score, 100)

# =============================================================================
# SAVE FRED DATA
# =============================================================================

def save_fred_data(df):
    """
    Save live FRED market data.
    """

    df.to_csv(FRED_MARKET_DATA, index=False)

    print(f"\n[KRONOS] FRED data saved:")
    print(FRED_MARKET_DATA)

# =============================================================================
# MARKET REGIME DETECTION
# =============================================================================

def detect_macro_regime(df):

    stress_score = (
        calculate_macro_stress_score(df)
    )

    if stress_score >= 75:

        regime = "CRISIS"

    elif stress_score >= 50:

        regime = "HIGH_STRESS"

    elif stress_score >= 25:

        regime = "ELEVATED_RISK"

    else:

        regime = "STABLE"

    print(
        f"\n[KRONOS] Macro Stress Score: {stress_score}"
    )

    print(
        f"[KRONOS] Current Macro Regime: {regime}"
    )

    return regime

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    fred_df = fetch_all_fred_data()

    if not fred_df.empty:

        save_fred_data(fred_df)

        yield_curve_df = calculate_treasury_spread(
            fred_df
        )

        if not yield_curve_df.empty:

            print(
                f"[KRONOS] Yield Curve Records: {len(yield_curve_df)}"
            )

        credit_spread_df = calculate_credit_spread(
            fred_df
        )

        if not credit_spread_df.empty:

            print(
                f"[KRONOS] Credit Spread Records: {len(credit_spread_df)}"
            )

        detect_macro_regime(
            fred_df
        )

        print(
            "\n[KRONOS] LIVE FRED ENGINE COMPLETED"
        )

# =============================================================================
# END OF FILE
# =============================================================================

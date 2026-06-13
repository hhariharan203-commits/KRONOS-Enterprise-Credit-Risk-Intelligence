# =============================================================================
# KRONOS — ALPHA VANTAGE MARKET DATA ENGINE
# File: src/data_pipeline/fetch_alpha_vantage.py
# =============================================================================

from __future__ import annotations

from datetime import datetime

import pandas as pd
import requests

from src.shared.config import ALPHA_VANTAGE_API_KEY, LIVE_DATA_DIR


ALPHA_VANTAGE_MARKET_DATA = LIVE_DATA_DIR / "alpha_vantage_market_data.csv"

ALPHA_MARKET_SYMBOLS = {
    "sp500": "SPY",
    "financial_sector": "XLF",
    "bank_etf": "KBE",
    "treasury_etf": "TLT",
    "dollar_index": "UUP",
}


def fetch_alpha_vantage_symbol(
    symbol,
    instrument_name
):
    """
    Fetch daily Alpha Vantage market data for one instrument.
    """

    if not ALPHA_VANTAGE_API_KEY:
        return pd.DataFrame()

    try:
        response = requests.get(
            "https://www.alphavantage.co/query",
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": ALPHA_VANTAGE_API_KEY,
                "outputsize": "compact",
            },
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        series = payload.get("Time Series (Daily)", {})

        if not series:
            return pd.DataFrame()

        rows = []
        for date_value, values in series.items():
            rows.append({
                "date": date_value,
                "instrument": instrument_name,
                "symbol": symbol,
                "open": float(values.get("1. open", 0)),
                "high": float(values.get("2. high", 0)),
                "low": float(values.get("3. low", 0)),
                "close": float(values.get("4. close", 0)),
                "volume": float(values.get("5. volume", 0)),
                "retrieved_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            })

        return pd.DataFrame(rows)

    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        print(
            f"[KRONOS ERROR] Alpha Vantage fetch failed for {symbol}: {exc}"
        )
        return pd.DataFrame()


def fetch_alpha_vantage_market_data():
    """
    Fetch KRONOS enterprise market instruments from Alpha Vantage.
    """

    frames = []

    for instrument_name, symbol in ALPHA_MARKET_SYMBOLS.items():
        frame = fetch_alpha_vantage_symbol(
            symbol,
            instrument_name
        )
        if not frame.empty:
            frames.append(frame)

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True
    )


def save_alpha_vantage_market_data(
    df
):
    """
    Save Alpha Vantage market data.
    """

    df.to_csv(
        ALPHA_VANTAGE_MARKET_DATA,
        index=False
    )

    print("\n[KRONOS] Alpha Vantage market data saved:")
    print(ALPHA_VANTAGE_MARKET_DATA)


if __name__ == "__main__":
    market_df = fetch_alpha_vantage_market_data()

    if not market_df.empty:
        save_alpha_vantage_market_data(
            market_df
        )
        print("\n[KRONOS] ALPHA VANTAGE MARKET ENGINE COMPLETED")
    else:
        print("\n[KRONOS WARNING] No Alpha Vantage market data retrieved")


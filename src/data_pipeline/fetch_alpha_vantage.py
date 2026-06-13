# =============================================================================
# KRONOS — ALPHA VANTAGE MARKET DATA ENGINE
# File: src/data_pipeline/fetch_alpha_vantage.py
# =============================================================================

from __future__ import annotations

from datetime import datetime
from time import sleep

import pandas as pd
import requests

from src.shared.config import ALPHA_VANTAGE_API_KEY, LIVE_DATA_DIR
from src.shared.logger import get_logger


ALPHA_VANTAGE_MARKET_DATA = LIVE_DATA_DIR / "alpha_vantage_market_data.csv"
log = get_logger("kronos.fetch_alpha_vantage")

ALPHA_MARKET_SYMBOLS = {
    "sp500": "SPY",
    "financial_sector": "XLF",
    "bank_etf": "KBE",
    "treasury_etf": "TLT",
    "dollar_index": "UUP",
}

ALPHA_VANTAGE_TIMEOUT_SECONDS = 20
ALPHA_VANTAGE_RETRY_ATTEMPTS = 3
ALPHA_VANTAGE_RETRY_BACKOFF_SECONDS = 2


def fetch_alpha_vantage_symbol(
    symbol,
    instrument_name
):
    """
    Fetch daily Alpha Vantage market data for one instrument.
    """

    if not ALPHA_VANTAGE_API_KEY:
        return pd.DataFrame()

    for attempt in range(1, ALPHA_VANTAGE_RETRY_ATTEMPTS + 1):
        try:
            response = requests.get(
                "https://www.alphavantage.co/query",
                params={
                    "function": "TIME_SERIES_DAILY",
                    "symbol": symbol,
                    "apikey": ALPHA_VANTAGE_API_KEY,
                    "outputsize": "compact",
                },
                timeout=ALPHA_VANTAGE_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            payload = response.json()
            series = payload.get("Time Series (Daily)", {})

            if not series:
                log.warning(
                    "Alpha Vantage returned no daily series for %s on attempt %s",
                    symbol,
                    attempt
                )
                if attempt < ALPHA_VANTAGE_RETRY_ATTEMPTS:
                    sleep(ALPHA_VANTAGE_RETRY_BACKOFF_SECONDS * attempt)
                    continue
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
            log.warning(
                "Alpha Vantage fetch failed for %s on attempt %s/%s: %s",
                symbol,
                attempt,
                ALPHA_VANTAGE_RETRY_ATTEMPTS,
                exc.__class__.__name__
            )
            if attempt < ALPHA_VANTAGE_RETRY_ATTEMPTS:
                sleep(ALPHA_VANTAGE_RETRY_BACKOFF_SECONDS * attempt)

    return pd.DataFrame()


def _cached_instrument_frame(
    instrument_name
):
    try:
        if not ALPHA_VANTAGE_MARKET_DATA.exists():
            return pd.DataFrame()

        cached = pd.read_csv(
            ALPHA_VANTAGE_MARKET_DATA
        )

        if (
            cached.empty
            or "instrument" not in cached.columns
        ):
            return pd.DataFrame()

        return cached[
            cached["instrument"] == instrument_name
        ].copy()

    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        log.warning(
            "Alpha Vantage cached fallback failed for %s: %s",
            instrument_name,
            exc.__class__.__name__
        )
        return pd.DataFrame()


def fetch_alpha_vantage_market_data():
    """
    Fetch KRONOS enterprise market instruments from Alpha Vantage.
    """

    frames = []

    missing_instruments = []

    for instrument_name, symbol in ALPHA_MARKET_SYMBOLS.items():
        frame = fetch_alpha_vantage_symbol(
            symbol,
            instrument_name
        )
        if not frame.empty:
            frames.append(frame)
        else:
            missing_instruments.append(instrument_name)

    for instrument_name in missing_instruments:
        cached_frame = _cached_instrument_frame(
            instrument_name
        )
        if not cached_frame.empty:
            log.warning(
                "Using cached Alpha Vantage fallback for %s",
                instrument_name
            )
            frames.append(cached_frame)

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

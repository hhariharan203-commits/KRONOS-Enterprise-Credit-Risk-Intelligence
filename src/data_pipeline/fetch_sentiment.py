# =============================================================================
# KRONOS — NEWS SENTIMENT INTELLIGENCE ENGINE
# File: src/data_pipeline/fetch_sentiment.py
# =============================================================================

import pandas as pd
import requests

from textblob import TextBlob
from datetime import datetime

from newsapi import NewsApiClient

from src.shared.config import (
    SENTIMENT_DATA,
    NEWS_API_KEY
)

# =============================================================================
# LIVE NEWS QUERY
# =============================================================================

NEWS_QUERY = (
    "banking OR credit OR default "
    "OR recession OR inflation "
    "OR economy OR interest rates"
)

# =============================================================================
# FETCH LIVE HEADLINES
# =============================================================================

def fetch_live_headlines():

    try:

        newsapi = NewsApiClient(
            api_key=NEWS_API_KEY
        )

        articles = newsapi.get_everything(
            q=NEWS_QUERY,
            language="en",
            sort_by="publishedAt",
            page_size=100
        )

        headlines = []

        for article in articles["articles"]:

            title = article.get("title")

            if title:

                headlines.append(title)

        print(
            f"[KRONOS] Live headlines fetched: {len(headlines)}"
        )

        return headlines

    except Exception as e:

        print(
            "[KRONOS ERROR] Failed fetching live headlines"
        )

        print(e)

        return []

# =============================================================================
# SENTIMENT CLASSIFICATION
# =============================================================================

def classify_sentiment(score):
    """
    Convert polarity score into sentiment label.
    """

    if score > 0.15:

        return "BULLISH"

    elif score < -0.15:

        return "BEARISH"

    else:

        return "NEUTRAL"

# =============================================================================
# ANALYZE SINGLE HEADLINE
# =============================================================================

def analyze_headline_sentiment(headline):
    """
    Analyze sentiment of a single financial headline.
    """

    blob = TextBlob(headline)

    polarity = blob.sentiment.polarity

    sentiment = classify_sentiment(polarity)

    return {
        "headline": headline,
        "polarity": round(polarity, 4),
        "sentiment": sentiment,
    }

# =============================================================================
# ANALYZE ALL HEADLINES
# =============================================================================

def analyze_all_headlines(headlines):
    """
    Run sentiment analysis on all headlines.
    """

    print("\n" + "=" * 70)
    print("[KRONOS] ANALYZING NEWS SENTIMENT")
    print("=" * 70)

    results = []

    for headline in headlines:

        sentiment_result = analyze_headline_sentiment(headline)

        results.append(sentiment_result)

    sentiment_df = pd.DataFrame(results)

    print(f"[KRONOS] Headlines analyzed: {len(sentiment_df)}")

    return sentiment_df

# =============================================================================
# MARKET SENTIMENT SCORE
# =============================================================================

def calculate_market_sentiment(sentiment_df):
    """
    Calculate aggregate market sentiment score.
    """

    avg_polarity = sentiment_df[
        "polarity"
    ].mean()

    sentiment_score = float(
        round(
            (avg_polarity + 1) * 50,
            2
        )
    )

    return sentiment_score

# =============================================================================
# SENTIMENT REGIME DETECTION
# =============================================================================

def detect_sentiment_regime(score):
    """
    Detect macro sentiment regime.
    """

    if score >= 70:

        return "STRONG RISK-ON"

    elif score >= 55:

        return "MODERATE RISK-ON"

    elif score >= 45:

        return "NEUTRAL"

    elif score >= 30:

        return "RISK-OFF"

    else:

        return "SEVERE RISK-OFF"

# =============================================================================
# SENTIMENT STRESS SCORE
# =============================================================================

def sentiment_stress_score(score):

    return round(
        100 - score,
        2
    )

# =============================================================================
# BULLISH / BEARISH COUNTS
# =============================================================================

def sentiment_breakdown(sentiment_df):
    """
    Generate sentiment distribution.
    """

    breakdown = sentiment_df["sentiment"].value_counts().to_dict()

    return breakdown


def filtered_sentiment_score(
    sentiment_df,
    keywords,
    fallback
):
    """
    Calculate a keyword-specific sentiment score.
    """

    if sentiment_df.empty or "headline" not in sentiment_df.columns:
        return fallback

    mask = sentiment_df["headline"].astype(str).str.contains(
        "|".join(keywords),
        case=False,
        regex=True,
        na=False
    )

    filtered = sentiment_df[mask]

    if filtered.empty or "polarity" not in filtered.columns:
        return fallback

    polarity = filtered["polarity"].mean()

    return float(
        round(
            (polarity + 1) * 50,
            2
        )
    )


def risk_sentiment_regime(
    score
):
    """
    Classify executive risk sentiment.
    """

    if score >= 65:

        return "BULLISH"

    elif score >= 45:

        return "NEUTRAL"

    elif score >= 30:

        return "BEARISH"

    elif score >= 15:

        return "STRESS"

    return "CRISIS"

# =============================================================================
# GENERATE SENTIMENT SUMMARY
# =============================================================================

def generate_sentiment_summary(sentiment_df):
    """
    Generate executive sentiment intelligence.
    """

    sentiment_score = calculate_market_sentiment(
        sentiment_df
    )

    regime = detect_sentiment_regime(
        sentiment_score
    )

    breakdown = sentiment_breakdown(
        sentiment_df
    )

    credit_sentiment_score = filtered_sentiment_score(
        sentiment_df,
        [
            "credit",
            "default",
            "loan",
            "bank",
            "delinquency",
        ],
        sentiment_score
    )

    economic_sentiment_score = filtered_sentiment_score(
        sentiment_df,
        [
            "economy",
            "inflation",
            "recession",
            "interest",
            "rates",
            "unemployment",
        ],
        sentiment_score
    )

    financial_stress_score = float(
        round(
            100 - min(
                sentiment_score,
                credit_sentiment_score,
                economic_sentiment_score
            ),
            2
        )
    )

    summary = {

        "market_sentiment_score":
            sentiment_score,

        "stress_score":
            sentiment_stress_score(
                sentiment_score
            ),

        "sentiment_regime":
            regime,

        "bullish_headlines":
            breakdown.get(
                "BULLISH",
                0
            ),

        "bearish_headlines":
            breakdown.get(
                "BEARISH",
                0
            ),

        "neutral_headlines":
            breakdown.get(
                "NEUTRAL",
                0
            ),

        "credit_sentiment_score":
            credit_sentiment_score,

        "economic_sentiment_score":
            economic_sentiment_score,

        "financial_stress_score":
            financial_stress_score,

        "risk_sentiment_regime":
            risk_sentiment_regime(
                sentiment_score
            ),

        "analysis_timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
    }

    summary_df = pd.DataFrame(
        [summary]
    )

    summary_df.to_csv(
        SENTIMENT_DATA.parent
        / "sentiment_summary.csv",
        index=False
    )

    print("\n[KRONOS] SENTIMENT SUMMARY")

    print(summary)

    return summary

# =============================================================================
# SAVE SENTIMENT DATA
# =============================================================================

def save_sentiment_data(df):
    """
    Save sentiment analysis dataset.
    """

    df.to_csv(
        SENTIMENT_DATA,
        index=False
    )

    print(
        f"\n[KRONOS] Sentiment data saved:"
    )

    print(SENTIMENT_DATA)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    headlines = fetch_live_headlines()

    if len(headlines) == 0:

        print(
            "\n[KRONOS ERROR] No headlines retrieved"
        )

    else:

        sentiment_df = analyze_all_headlines(
            headlines
        )

        if not sentiment_df.empty:

            save_sentiment_data(
                sentiment_df
            )

            generate_sentiment_summary(
                sentiment_df
            )

            print(
                "\n[KRONOS] SENTIMENT ENGINE COMPLETED"
            )

# =============================================================================
# END OF FILE
# =============================================================================

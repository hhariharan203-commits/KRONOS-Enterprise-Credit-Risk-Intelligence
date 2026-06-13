# =============================================================================
# KRONOS — ENTERPRISE CREDIT SCORECARD ENGINE
# File: src/credit_risk/scorecard.py
# =============================================================================

import pandas as pd

# =============================================================================
# CREDIT RATING SCALE
# =============================================================================

RATING_SCALE = [
    {
        "grade": "AAA",
        "min_score": 800,
        "max_score": 850,
        "risk_level": "EXCEPTIONAL",
        "default_risk": "EXTREMELY LOW",
    },
    {
        "grade": "AA",
        "min_score": 740,
        "max_score": 799,
        "risk_level": "VERY STRONG",
        "default_risk": "VERY LOW",
    },
    {
        "grade": "A",
        "min_score": 680,
        "max_score": 739,
        "risk_level": "STRONG",
        "default_risk": "LOW",
    },
    {
        "grade": "BBB",
        "min_score": 620,
        "max_score": 679,
        "risk_level": "MODERATE",
        "default_risk": "MODERATE",
    },
    {
        "grade": "BB",
        "min_score": 560,
        "max_score": 619,
        "risk_level": "ELEVATED",
        "default_risk": "HIGHER THAN AVERAGE",
    },
    {
        "grade": "B",
        "min_score": 500,
        "max_score": 559,
        "risk_level": "HIGH RISK",
        "default_risk": "HIGH",
    },
    {
        "grade": "CCC",
        "min_score": 300,
        "max_score": 499,
        "risk_level": "DISTRESSED",
        "default_risk": "SEVERE",
    },
]

# =============================================================================
# MAP CREDIT SCORE TO RATING
# =============================================================================

def map_credit_rating(credit_score):
    """
    Convert numerical credit score into institutional rating.
    """

    for rating in RATING_SCALE:

        if (
            rating["min_score"]
            <= credit_score
            <= rating["max_score"]
        ):

            return rating

    return {
        "grade": "UNKNOWN",
        "risk_level": "UNKNOWN",
        "default_risk": "UNKNOWN",
    }

# =============================================================================
# BORROWER CATEGORY
# =============================================================================

def borrower_category(grade):
    """
    Categorize borrower quality.
    """

    if grade in ["AAA", "AA"]:

        return "PREMIUM BORROWER"

    elif grade in ["A", "BBB"]:

        return "STANDARD BORROWER"

    elif grade in ["BB", "B"]:

        return "WATCHLIST BORROWER"

    else:

        return "DISTRESSED BORROWER"

# =============================================================================
# LENDING SUITABILITY
# =============================================================================

def lending_suitability(grade):
    """
    Determine institutional lending suitability.
    """

    if grade in ["AAA", "AA"]:

        return "FULL APPROVAL"

    elif grade in ["A", "BBB"]:

        return "APPROVAL WITH STANDARD MONITORING"

    elif grade in ["BB", "B"]:

        return "LIMITED APPROVAL WITH ENHANCED MONITORING"

    else:

        return "REJECT OR SPECIAL SITUATIONS REVIEW"

# =============================================================================
# EXPECTED MONITORING LEVEL
# =============================================================================

def monitoring_level(grade):
    """
    Determine borrower monitoring intensity.
    """

    if grade in ["AAA", "AA"]:

        return "LOW MONITORING"

    elif grade in ["A", "BBB"]:

        return "MODERATE MONITORING"

    elif grade in ["BB", "B"]:

        return "HIGH MONITORING"

    else:

        return "CRITICAL WATCHLIST"

# =============================================================================
# GENERATE FULL SCORECARD
# =============================================================================

def generate_scorecard(
    credit_score,
    pd_probability,
    lgd,
    ead
):
    """
    Generate enterprise borrower scorecard.
    """

    rating = map_credit_rating(
        credit_score
    )

    grade = rating["grade"]

    expected_loss = round(
        pd_probability
        * lgd
        * ead,
        2
    )

    if expected_loss < 1000:

        loss_band = "LOW LOSS"

    elif expected_loss < 5000:

        loss_band = "MODERATE LOSS"

    elif expected_loss < 10000:

        loss_band = "HIGH LOSS"

    else:

        loss_band = "SEVERE LOSS"

    scorecard = {

        "credit_score":
            credit_score,

        "credit_grade":
            grade,

        "risk_level":
            rating["risk_level"],

        "default_risk":
            rating["default_risk"],

        "probability_of_default":
            round(
                pd_probability * 100,
                2
            ),

        "loss_given_default":
            round(
                lgd * 100,
                2
            ),

        "exposure_at_default":
            round(
                ead,
                2
            ),

        "expected_loss":
            expected_loss,

        "expected_loss_band":
            loss_band,

        "borrower_category":
            borrower_category(
                grade
            ),

        "lending_suitability":
            lending_suitability(
                grade
            ),

        "monitoring_level":
            monitoring_level(
                grade
            ),
    }

    return scorecard

# =============================================================================
# SCORECARD SUMMARY
# =============================================================================

def print_scorecard(scorecard):
    """
    Print formatted institutional scorecard.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] ENTERPRISE CREDIT SCORECARD")
    print("=" * 80)

    for key, value in scorecard.items():

        formatted_key = (
            key.replace("_", " ")
            .title()
        )

        print(f"{formatted_key}: {value}")

    print("=" * 80)

# =============================================================================
# PORTFOLIO RATING DISTRIBUTION
# =============================================================================

def portfolio_rating_distribution(scores):
    """
    Analyze portfolio credit quality distribution.
    """

    grades = []

    for score in scores:

        rating = map_credit_rating(score)

        grades.append(rating["grade"])

    distribution = (
        pd.Series(grades)
        .value_counts()
        .reset_index()
    )

    distribution.columns = [
        "credit_grade",
        "borrower_count"
    ]

    return distribution

# =============================================================================
# SAMPLE EXECUTION
# =============================================================================

if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # SAMPLE BORROWER
    # -------------------------------------------------------------------------

    sample_score = 712

    sample_pd = 0.2702

    sample_lgd = 0.2244

    sample_ead = 28521.61

    scorecard = generate_scorecard(
        credit_score=sample_score,
        pd_probability=sample_pd,
        lgd=sample_lgd,
        ead=sample_ead
    )

    print_scorecard(
        scorecard
    )

    # -------------------------------------------------------------------------
    # SAMPLE PORTFOLIO
    # -------------------------------------------------------------------------

    portfolio_scores = [
        820,
        760,
        710,
        650,
        590,
        530,
        420,
    ]

    distribution = portfolio_rating_distribution(
        portfolio_scores
    )

    print(
        "\n[KRONOS] PORTFOLIO RATING DISTRIBUTION"
    )

    print(
        distribution
    )

    print(
        "\n[KRONOS] SCORECARD ENGINE COMPLETED"
    )

# =============================================================================
# END OF FILE
# =============================================================================
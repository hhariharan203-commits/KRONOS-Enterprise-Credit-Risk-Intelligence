# =============================================================================
# KRONOS — ENTERPRISE ANOMALY DETECTION ENGINE
# File: src/ews/anomaly_detection.py
# =============================================================================

import pandas as pd
import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# =============================================================================
# PREPARE PORTFOLIO DATA
# =============================================================================

def prepare_portfolio_data(
    portfolio_df
):
    """
    Prepare borrower portfolio dataset.
    """

    feature_cols = [
        "current_pd",
        "credit_utilization",
        "payment_burden_ratio",
        "total_delinquency",
        "loan_to_income_ratio",
    ]

    available_cols = [
        col for col in feature_cols
        if col in portfolio_df.columns
    ]

    df = portfolio_df[
        available_cols
    ].copy()

    df = df.fillna(0)

    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(df)

    return (
        scaled_data,
        available_cols,
        scaler
    )

# =============================================================================
# BUILD ISOLATION FOREST
# =============================================================================

def build_anomaly_model():
    """
    Build enterprise anomaly detection model.
    """

    model = IsolationForest(
        n_estimators=200,
        contamination=0.08,
        random_state=42,
    )

    return model

# =============================================================================
# RUN ANOMALY DETECTION
# =============================================================================

def detect_anomalies(
    portfolio_df
):
    """
    Detect abnormal borrower behavior.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING ANOMALY DETECTION")
    print("=" * 80)

    (
        scaled_data,
        feature_cols,
        scaler
    ) = prepare_portfolio_data(
        portfolio_df
    )

    model = build_anomaly_model()

    model.fit(
        scaled_data
    )

    # -------------------------------------------------------------------------
    # PREDICTIONS
    # -------------------------------------------------------------------------

    anomaly_labels = model.predict(
        scaled_data
    )

    anomaly_scores = model.decision_function(
        scaled_data
    )

    portfolio_df = portfolio_df.copy()

    portfolio_df["anomaly_flag"] = anomaly_labels

    portfolio_df["anomaly_score"] = anomaly_scores

    # Convert to readable labels
    portfolio_df["anomaly_status"] = (
        portfolio_df["anomaly_flag"]
        .apply(
            lambda x:
            "ANOMALOUS"
            if x == -1
            else "NORMAL"
        )
    )

    return portfolio_df

# =============================================================================
# ANOMALY SEVERITY
# =============================================================================

def anomaly_severity(
    anomaly_score
):
    """
    Classify anomaly severity.
    """

    if anomaly_score > 0.05:

        return "LOW ANOMALY"

    elif anomaly_score > -0.02:

        return "MODERATE ANOMALY"

    elif anomaly_score > -0.08:

        return "HIGH ANOMALY"

    else:

        return "SEVERE ANOMALY"

# =============================================================================
# ANOMALY RISK GRADE
# =============================================================================

def anomaly_risk_grade(
    anomaly_score
):
    """
    Portfolio anomaly grade.
    """

    if anomaly_score > 0.05:

        return "A"

    elif anomaly_score > -0.02:

        return "B"

    elif anomaly_score > -0.08:

        return "C"

    else:

        return "D"

# =============================================================================
# RISK ESCALATION LEVEL
# =============================================================================

def escalation_level(
    severity
):
    """
    Determine escalation workflow.
    """

    if severity == "LOW ANOMALY":

        return "MONITOR"

    elif severity == "MODERATE ANOMALY":

        return "ENHANCED REVIEW"

    elif severity == "HIGH ANOMALY":

        return "WATCHLIST"

    else:

        return "IMMEDIATE INVESTIGATION"

# =============================================================================
# HIDDEN DISTRESS SIGNALS
# =============================================================================

def hidden_distress_signals(
    borrower_row
):
    """
    Identify hidden borrower distress signals.
    """

    signals = []

    # -------------------------------------------------------------------------
    # UTILIZATION SPIKE
    # -------------------------------------------------------------------------

    if borrower_row.get(
        "credit_utilization",
        0
    ) > 0.85:

        signals.append(
            "Extreme credit utilization detected"
        )

    # -------------------------------------------------------------------------
    # PAYMENT STRESS
    # -------------------------------------------------------------------------

    if borrower_row.get(
        "payment_burden_ratio",
        0
    ) > 0.45:

        signals.append(
            "Elevated payment burden pressure"
        )

    # -------------------------------------------------------------------------
    # DELINQUENCY STRESS
    # -------------------------------------------------------------------------

    if borrower_row.get(
        "total_delinquency",
        0
    ) >= 3:

        signals.append(
            "High delinquency concentration"
        )

    # -------------------------------------------------------------------------
    # RAPID PD DETERIORATION
    # -------------------------------------------------------------------------

    current_pd = borrower_row.get(
        "current_pd",
        0
    )

    previous_pd = borrower_row.get(
        "previous_pd",
        0
    )

    if (current_pd - previous_pd) > 0.12:

        signals.append(
            "Rapid borrower deterioration trend"
        )

    if len(signals) == 0:

        signals.append(
            "No major hidden distress signals detected"
        )

    return signals

# =============================================================================
# PORTFOLIO ANOMALY SUMMARY
# =============================================================================

def portfolio_anomaly_summary(
    portfolio_df
):
    """
    Generate enterprise anomaly overview.
    """

    total_accounts = len(
        portfolio_df
    )

    anomaly_accounts = len(
        portfolio_df[
            portfolio_df["anomaly_status"]
            == "ANOMALOUS"
        ]
    )

    anomaly_pct = (
        anomaly_accounts / total_accounts
    ) * 100

    summary = {
        "total_accounts":
            total_accounts,

        "anomalous_accounts":
            anomaly_accounts,

        "anomaly_percentage":
            round(anomaly_pct, 2),
    }

    return summary

# =============================================================================
# PORTFOLIO RISK CONCENTRATION
# =============================================================================

def portfolio_risk_concentration(
    portfolio_df
):
    """
    Measure anomaly concentration.
    """

    anomalous = portfolio_df[
        portfolio_df["anomaly_status"]
        == "ANOMALOUS"
    ]

    concentration = (
        len(anomalous)
        / len(portfolio_df)
    ) * 100

    return round(
        concentration,
        2
    )

# =============================================================================
# GENERATE BORROWER ALERTS
# =============================================================================

def generate_borrower_alerts(
    portfolio_df
):
    """
    Generate borrower anomaly alerts.
    """

    alerts = []

    anomalous_df = portfolio_df[
        portfolio_df["anomaly_status"]
        == "ANOMALOUS"
    ]

    for _, row in anomalous_df.iterrows():

        severity = anomaly_severity(
            row["anomaly_score"]
        )

        risk_grade = anomaly_risk_grade(
            row["anomaly_score"]
        )

        escalation = escalation_level(
            severity
        )

        distress_signals = hidden_distress_signals(
            row
        )

        alert = {

            "borrower_id":
                row.get(
                    "borrower_id",
                    "UNKNOWN"
                ),

            "risk_grade":
                risk_grade,

            "severity":
                severity,

            "escalation":
                escalation,

            "anomaly_score":
                round(
                    float(
                        row["anomaly_score"]
                    ),
                    4
                ),

            "distress_signals":
                distress_signals,
        }

        alerts.append(
            alert
        )

    return alerts

# =============================================================================
# FULL ANOMALY PIPELINE
# =============================================================================

def run_anomaly_pipeline(
    portfolio_df
):
    """
    Run full enterprise anomaly workflow.
    """

    portfolio_df = detect_anomalies(
        portfolio_df
    )

    summary = portfolio_anomaly_summary(
        portfolio_df
    )

    concentration = portfolio_risk_concentration(
        portfolio_df
    )

    alerts = generate_borrower_alerts(
        portfolio_df
    )

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n" + "=" * 80)
    print("[KRONOS] ANOMALY DETECTION SUMMARY")
    print("=" * 80)

    for key, value in summary.items():

        print(f"{key}: {value}")

    print(
        f"\nPortfolio Risk Concentration: "
        f"{concentration}%"
    )

    print("\nANOMALY ALERTS\n")

    for alert in alerts:

        print(alert)

    print("=" * 80)

    return {

        "portfolio_results":
            portfolio_df,

        "summary":
            summary,

        "risk_concentration":
            concentration,

        "alerts":
            alerts,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "current_pd": 0.08,
        "previous_pd": 0.06,
        "credit_utilization": 0.32,
        "payment_burden_ratio": 0.18,
        "loan_to_income_ratio": 0.22,
        "total_delinquency": 0,
    },

    {
        "borrower_id": "B1002",
        "current_pd": 0.35,
        "previous_pd": 0.12,
        "credit_utilization": 0.92,
        "payment_burden_ratio": 0.51,
        "loan_to_income_ratio": 0.67,
        "total_delinquency": 4,
    },

    {
        "borrower_id": "B1003",
        "current_pd": 0.14,
        "previous_pd": 0.11,
        "credit_utilization": 0.48,
        "payment_burden_ratio": 0.24,
        "loan_to_income_ratio": 0.34,
        "total_delinquency": 1,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_anomaly_pipeline(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] ANOMALY DETECTION COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
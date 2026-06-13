# =============================================================================
# KRONOS — CONTAGION ENGINE
# File: src/contagion/contagion_engine.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# CONTAGION THRESHOLDS
# =============================================================================

CONTAGION_THRESHOLDS = {

    "LOW": 0.10,
    "MODERATE": 0.25,
    "HIGH": 0.45,
    "SYSTEMIC": 0.70,
}

# =============================================================================
# BORROWER CONNECTION STRENGTH
# =============================================================================

def connection_strength(
    exposure_a,
    exposure_b
):
    """
    Estimate interconnected exposure strength.
    """

    if exposure_a + exposure_b == 0:

        return 0

    strength = (
        min(exposure_a, exposure_b)
        / max(exposure_a, exposure_b)
    )

    return round(
        float(strength),
        4
    )

# =============================================================================
# CONTAGION TRANSMISSION
# =============================================================================

def contagion_transmission(
    default_probability,
    connection_weight
):
    """
    Calculate contagion transmission risk.
    """

    contagion_risk = (
        default_probability
        * connection_weight
    )

    return round(
        float(contagion_risk),
        4
    )

# =============================================================================
# SYSTEMIC IMPACT SCORE
# =============================================================================

def systemic_impact_score(
    contagion_risk,
    borrower_exposure
):
    """
    Estimate systemic impact intensity.
    """

    impact_score = (
        contagion_risk
        * borrower_exposure
    ) / 1000

    return min(
        round(impact_score, 2),
        100
    )

# =============================================================================
# NETWORK STABILITY
# =============================================================================

def network_stability(
    average_contagion
):
    """
    Determine portfolio network stability.
    """

    if average_contagion < 0.10:

        return "STABLE NETWORK"

    elif average_contagion < 0.25:

        return "ELEVATED NETWORK RISK"

    elif average_contagion < 0.45:

        return "HIGH NETWORK INSTABILITY"

    return "SYSTEMIC CONTAGION RISK"

# =============================================================================
# CONTAGION SEVERITY
# =============================================================================

def contagion_severity(
    contagion_risk
):
    """
    Classify contagion severity.
    """

    if contagion_risk < CONTAGION_THRESHOLDS["LOW"]:

        return "LOW CONTAGION"

    elif contagion_risk < CONTAGION_THRESHOLDS["MODERATE"]:

        return "MODERATE CONTAGION"

    elif contagion_risk < CONTAGION_THRESHOLDS["HIGH"]:

        return "HIGH CONTAGION"

    return "SYSTEMIC CONTAGION"

# =============================================================================
# CASCADE FAILURE RISK
# =============================================================================

def cascade_failure_risk(
    systemic_score
):
    """
    Estimate probability of cascade failure.
    """

    if systemic_score < 10:

        return "LIMITED CASCADE RISK"

    elif systemic_score < 25:

        return "MODERATE CASCADE RISK"

    elif systemic_score < 50:

        return "HIGH CASCADE RISK"

    return "SYSTEMIC FAILURE RISK"

# =============================================================================
# CONCENTRATION RISK
# =============================================================================

def concentration_risk(
    total_exposure,
    portfolio_exposure
):
    """
    Measure exposure concentration risk.
    """

    if portfolio_exposure <= 0:

        return 0

    concentration = (
        total_exposure
        / portfolio_exposure
    ) * 100

    return round(
        concentration,
        2
    )

# =============================================================================
# EXECUTIVE CONTAGION NARRATIVE
# =============================================================================

def generate_contagion_narrative(
    borrower_id,
    severity,
    cascade_risk
):
    """
    Generate executive contagion commentary.
    """

    narrative = (
        f"Borrower {borrower_id} exhibits "
        f"{severity.lower()} with "
        f"{cascade_risk.lower()} across "
        "the interconnected portfolio network."
    )

    return narrative

# =============================================================================
# RUN CONTAGION ANALYSIS
# =============================================================================

def run_contagion_analysis(
    portfolio_df
):
    """
    Run enterprise contagion simulation.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING CONTAGION ENGINE")
    print("=" * 80)

    portfolio_df = (
        portfolio_df.copy()
    )

    print(
        f"Portfolio Rows Before Filter: "
        f"{len(portfolio_df):,}"
    )

    portfolio_df = (
        portfolio_df
        .nlargest(
            500,
            "ead"
        )
        .reset_index(
            drop=True
        )
    )

    print(
        f"Portfolio Rows After Filter: "
        f"{len(portfolio_df):,}"
    )

    total_portfolio_exposure = (
        portfolio_df["ead"]
        .sum()
    )

    contagion_results = []

    # -------------------------------------------------------------------------
    # INTERCONNECTED RISK ANALYSIS
    # -------------------------------------------------------------------------

    for idx, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        borrower_pd = borrower["pd_score"]

        borrower_exposure = borrower["ead"]

        # ---------------------------------------------------------------------
        # NETWORK CONNECTIONS
        # ---------------------------------------------------------------------

        connected_risk = []

        for jdx, peer in portfolio_df.iterrows():

            if idx == jdx:

                continue

            connection = connection_strength(
                borrower_exposure,
                peer["ead"]
            )

            contagion_risk = contagion_transmission(
                borrower_pd,
                connection
            )

            connected_risk.append(
                contagion_risk
            )

        # ---------------------------------------------------------------------
        # AGGREGATE CONTAGION
        # ---------------------------------------------------------------------

        avg_contagion = np.mean(
            connected_risk
        )

        systemic_score = systemic_impact_score(
            avg_contagion,
            borrower_exposure
        )

        severity = contagion_severity(
            avg_contagion
        )

        cascade_risk = cascade_failure_risk(
            systemic_score
        )

        concentration = concentration_risk(
            borrower_exposure,
            total_portfolio_exposure
        )

        narrative = generate_contagion_narrative(
            borrower_id,
            severity,
            cascade_risk
        )

        contagion_results.append({

            "borrower_id":
                borrower_id,

            "average_contagion_risk":
                round(
                    float(avg_contagion),
                    4
                ),

            "systemic_impact_score":
                systemic_score,

            "contagion_severity":
                severity,

            "cascade_failure_risk":
                cascade_risk,

            "exposure_concentration_pct":
                concentration,

            "executive_narrative":
                narrative,
        })

    contagion_df = pd.DataFrame(
        contagion_results
    )

    # -------------------------------------------------------------------------
    # NETWORK STABILITY
    # -------------------------------------------------------------------------

    portfolio_avg_contagion = round(
        float(
            contagion_df[
                "average_contagion_risk"
            ].mean()
        ),
        4
    )

    network_status = network_stability(
        portfolio_avg_contagion
    )

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "portfolio_average_contagion":
            portfolio_avg_contagion,

        "network_stability":
            network_status,

        "total_portfolio_exposure":
            round(
                float(
                    total_portfolio_exposure
                ),
                2
            ),

        "highest_contagion_risk":
            round(
                float(
                    contagion_df[
                        "average_contagion_risk"
                    ].max()
                ),
                4
            ),

        "highest_systemic_score":
            round(
                float(
                    contagion_df[
                        "systemic_impact_score"
                    ].max()
                ),
                2
            ),

        "average_concentration":
            round(
                float(
                    contagion_df[
                        "exposure_concentration_pct"
                    ].mean()
                ),
                2
            ),

        "high_risk_borrowers":
            int(
                (
                    contagion_df[
                        "contagion_severity"
                    ]
                    == "HIGH CONTAGION"
                ).sum()
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] CONTAGION SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nCONTAGION ANALYSIS\n")

    print(
        contagion_df[
            [
                "borrower_id",
                "average_contagion_risk",
                "systemic_impact_score",
                "contagion_severity",
                "cascade_failure_risk",
                "exposure_concentration_pct",
            ]
        ].head(25)
    )

    print("=" * 80)

    return {

        "contagion_results":
            contagion_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.04,
        "ead": 18000,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.28,
        "ead": 64000,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.71,
        "ead": 120000,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.17,
        "ead": 42000,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_contagion_analysis(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] CONTAGION ENGINE COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
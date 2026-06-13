# =============================================================================
# KRONOS — CASCADE SIMULATOR
# File: src/contagion/cascade_simulator.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# CASCADE THRESHOLDS
# =============================================================================

CASCADE_THRESHOLDS = {

    "LOW": 0.10,
    "MODERATE": 0.25,
    "HIGH": 0.45,
    "SYSTEMIC": 0.70,
}

# =============================================================================
# INITIAL DEFAULT IMPACT
# =============================================================================

def initial_default_impact(
    pd_score,
    exposure
):
    """
    Estimate borrower default shock intensity.
    """

    impact = (
        pd_score
        * exposure
    ) / 1000

    return round(
        float(impact),
        2
    )

# =============================================================================
# CONTAGION PROPAGATION
# =============================================================================

def contagion_propagation(
    source_impact,
    connection_strength
):
    """
    Propagate stress through network connections.
    """

    propagation = (
        source_impact
        * connection_strength
    )

    return round(
        float(propagation),
        2
    )

# =============================================================================
# CASCADE AMPLIFICATION
# =============================================================================

def cascade_amplification(
    propagation_value,
    contagion_round
):
    """
    Model amplification through sequential contagion.
    """

    amplification_factor = (
        1 + (contagion_round * 0.15)
    )

    amplified_loss = (
        propagation_value
        * amplification_factor
    )

    return round(
        float(amplified_loss),
        2
    )

# =============================================================================
# SYSTEMIC FAILURE SEVERITY
# =============================================================================

def systemic_failure_severity(
    cascade_loss
):
    """
    Classify systemic collapse severity.
    """

    if cascade_loss < 10:

        return "LIMITED SYSTEMIC STRESS"

    elif cascade_loss < 30:

        return "MODERATE CASCADE STRESS"

    elif cascade_loss < 60:

        return "HIGH SYSTEMIC STRESS"

    return "SYSTEMIC FAILURE RISK"

# =============================================================================
# FAILURE WAVE CLASSIFICATION
# =============================================================================

def failure_wave_classification(
    cascade_round
):
    """
    Determine deterioration wave intensity.
    """

    if cascade_round == 1:

        return "PRIMARY FAILURE WAVE"

    elif cascade_round == 2:

        return "SECONDARY FAILURE WAVE"

    elif cascade_round == 3:

        return "TERTIARY FAILURE WAVE"

    return "SYSTEMIC COLLAPSE WAVE"

# =============================================================================
# NETWORK COLLAPSE RISK
# =============================================================================

def network_collapse_risk(
    average_cascade_loss
):
    """
    Determine network collapse severity.
    """

    if average_cascade_loss < 10:

        return "STABLE NETWORK CONDITIONS"

    elif average_cascade_loss < 25:

        return "ELEVATED COLLAPSE RISK"

    elif average_cascade_loss < 50:

        return "HIGH NETWORK INSTABILITY"

    return "SYSTEMIC NETWORK FAILURE"

# =============================================================================
# CONTAGION ACCELERATION
# =============================================================================

def contagion_acceleration(
    round_losses
):
    """
    Measure contagion acceleration intensity.
    """

    if len(round_losses) < 2:

        return 0

    acceleration = (
        round_losses[-1]
        - round_losses[0]
    )

    return round(
        float(acceleration),
        2
    )

# =============================================================================
# EXECUTIVE CASCADE NARRATIVE
# =============================================================================

def generate_cascade_narrative(
    borrower_id,
    severity,
    wave
):
    """
    Generate executive systemic-collapse commentary.
    """

    narrative = (
        f"Borrower {borrower_id} triggered "
        f"{severity.lower()} during "
        f"{wave.lower()} across the "
        "interconnected portfolio network."
    )

    return narrative

# =============================================================================
# RUN CASCADE SIMULATION
# =============================================================================

def run_cascade_simulation(
    portfolio_df,
    rounds=3
):
    """
    Run enterprise cascade-failure simulation.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING CASCADE SIMULATOR")
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

    cascade_results = []

    # -------------------------------------------------------------------------
    # SIMULATE BORROWER FAILURES
    # -------------------------------------------------------------------------

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower[
            "borrower_id"
        ]

        pd_score = borrower[
            "pd_score"
        ]

        exposure = borrower[
            "ead"
        ]

        connection_strength = borrower.get(
            "connection_strength",
            0.40
        )

        # ---------------------------------------------------------------------
        # INITIAL SHOCK
        # ---------------------------------------------------------------------

        base_impact = initial_default_impact(
            pd_score,
            exposure
        )

        round_losses = []

        current_impact = base_impact

        # ---------------------------------------------------------------------
        # CASCADE ROUNDS
        # ---------------------------------------------------------------------

        for round_num in range(1, rounds + 1):

            propagation = contagion_propagation(
                current_impact,
                connection_strength
            )

            amplified_loss = cascade_amplification(
                propagation,
                round_num
            )

            round_losses.append(
                amplified_loss
            )

            current_impact = amplified_loss

        # ---------------------------------------------------------------------
        # FINAL CASCADE ANALYTICS
        # ---------------------------------------------------------------------

        total_cascade_loss = round(
            float(sum(round_losses)),
            2
        )

        average_loss = round(
            float(np.mean(round_losses)),
            2
        )

        severity = systemic_failure_severity(
            total_cascade_loss
        )

        wave = failure_wave_classification(
            rounds
        )

        acceleration = contagion_acceleration(
            round_losses
        )

        narrative = generate_cascade_narrative(
            borrower_id,
            severity,
            wave
        )

        cascade_results.append({

            "borrower_id":
                borrower_id,

            "initial_default_impact":
                base_impact,

            "total_cascade_loss":
                total_cascade_loss,

            "average_round_loss":
                average_loss,

            "cascade_acceleration":
                acceleration,

            "failure_wave":
                wave,

            "systemic_failure_severity":
                severity,

            "executive_narrative":
                narrative,
        })

    cascade_df = pd.DataFrame(
        cascade_results
    )

    # -------------------------------------------------------------------------
    # NETWORK COLLAPSE ANALYTICS
    # -------------------------------------------------------------------------

    average_cascade_loss = round(
        float(
            cascade_df[
                "total_cascade_loss"
            ].mean()
        ),
        2
    )

    network_status = network_collapse_risk(
        average_cascade_loss
    )

    # -------------------------------------------------------------------------
    # PORTFOLIO SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "average_cascade_loss":
            average_cascade_loss,

        "maximum_cascade_loss":
            round(
                float(
                    cascade_df[
                        "total_cascade_loss"
                    ].max()
                ),
                2
            ),

        "total_cascade_loss":
            round(
                float(
                    cascade_df[
                        "total_cascade_loss"
                    ].sum()
                ),
                2
            ),

        "average_acceleration":
            round(
                float(
                    cascade_df[
                        "cascade_acceleration"
                    ].mean()
                ),
                2
            ),

        "maximum_acceleration":
            round(
                float(
                    cascade_df[
                        "cascade_acceleration"
                    ].max()
                ),
                2
            ),

        "network_collapse_risk":
            network_status,

        "high_systemic_accounts":
            int(
                (
                    cascade_df[
                        "systemic_failure_severity"
                    ].isin(
                        [
                            "HIGH SYSTEMIC STRESS",
                            "SYSTEMIC FAILURE RISK"
                        ]
                    )
                ).sum()
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] CASCADE SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nCASCADE FAILURE ANALYSIS\n")

    print(
        cascade_df[
            [
                "borrower_id",
                "initial_default_impact",
                "total_cascade_loss",
                "cascade_acceleration",
                "failure_wave",
                "systemic_failure_severity",
            ]
        ].head(25)
    )

    print("=" * 80)

    return {

        "cascade_results":
            cascade_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "pd_score": 0.05,
        "ead": 24000,
        "connection_strength": 0.35,
    },

    {
        "borrower_id": "B1002",
        "pd_score": 0.31,
        "ead": 72000,
        "connection_strength": 0.52,
    },

    {
        "borrower_id": "B1003",
        "pd_score": 0.74,
        "ead": 140000,
        "connection_strength": 0.78,
    },

    {
        "borrower_id": "B1004",
        "pd_score": 0.18,
        "ead": 48000,
        "connection_strength": 0.41,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_cascade_simulation(
        SAMPLE_PORTFOLIO,
        rounds=3
    )

    print("\n[KRONOS] CASCADE SIMULATOR COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
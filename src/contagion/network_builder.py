# =============================================================================
# KRONOS — NETWORK BUILDER
# File: src/contagion/network_builder.py
# =============================================================================

import pandas as pd
import numpy as np

# =============================================================================
# NETWORK THRESHOLDS
# =============================================================================

SYSTEMIC_NODE_THRESHOLD = 0.60

CLUSTER_THRESHOLD = 0.40

# =============================================================================
# CONNECTION WEIGHT
# =============================================================================

def connection_weight(
    exposure_a,
    exposure_b
):
    """
    Calculate borrower network connection strength.
    """

    if max(exposure_a, exposure_b) == 0:

        return 0

    weight = (
        min(exposure_a, exposure_b)
        / max(exposure_a, exposure_b)
    )

    return round(
        float(weight),
        4
    )

# =============================================================================
# BUILD NETWORK EDGES
# =============================================================================

def build_network_edges(
    portfolio_df
):
    """
    Build interconnected borrower relationships.
    """

    edges = []

    for idx, borrower_a in portfolio_df.iterrows():

        for jdx, borrower_b in portfolio_df.iterrows():

            if idx >= jdx:

                continue

            borrower_a_id = borrower_a["borrower_id"]
            borrower_b_id = borrower_b["borrower_id"]

            exposure_a = borrower_a["ead"]
            exposure_b = borrower_b["ead"]

            weight = connection_weight(
                exposure_a,
                exposure_b
            )

            edges.append({

                "source":
                    borrower_a_id,

                "target":
                    borrower_b_id,

                "connection_weight":
                    weight,
            })

    return pd.DataFrame(edges)

# =============================================================================
# NODE CENTRALITY
# =============================================================================

def node_centrality(
    borrower_id,
    edge_df
):
    """
    Calculate borrower network centrality.
    """

    connected_edges = edge_df[
        (
            edge_df["source"]
            == borrower_id
        )
        |
        (
            edge_df["target"]
            == borrower_id
        )
    ]

    if len(connected_edges) == 0:

        return 0

    centrality = (
        connected_edges[
            "connection_weight"
        ].mean()
    )

    return round(
        float(centrality),
        4
    )

# =============================================================================
# SYSTEMIC IMPORTANCE
# =============================================================================

def systemic_importance(
    centrality,
    exposure_concentration
):
    """
    Estimate systemic borrower importance.
    """

    importance = (

        centrality * 0.50
        + exposure_concentration * 0.50

    )

    return min(
        round(importance, 2),
        100
    )

# =============================================================================
# EXPOSURE CONCENTRATION
# =============================================================================

def exposure_concentration(
    borrower_exposure,
    portfolio_exposure
):
    """
    Calculate borrower concentration percentage.
    """

    if portfolio_exposure <= 0:

        return 0

    concentration = (
        borrower_exposure
        / portfolio_exposure
    ) * 100

    return round(
        concentration,
        2
    )

# =============================================================================
# SYSTEMIC NODE CLASSIFICATION
# =============================================================================

def systemic_node_classification(
    centrality
):
    """
    Identify critical systemic borrowers.
    """

    if centrality >= 0.75:

        return "CRITICAL SYSTEMIC NODE"

    elif centrality >= 0.50:

        return "HIGH SYSTEMIC NODE"

    elif centrality >= 0.25:

        return "MODERATE SYSTEMIC NODE"

    return "LIMITED SYSTEMIC NODE"

# =============================================================================
# CLUSTER DETECTION
# =============================================================================

def cluster_classification(
    connection_weight_value
):
    """
    Detect concentration cluster intensity.
    """

    if connection_weight_value >= 0.75:

        return "CRITICAL CONCENTRATION CLUSTER"

    elif connection_weight_value >= 0.50:

        return "HIGH CONCENTRATION CLUSTER"

    elif connection_weight_value >= 0.25:

        return "MODERATE CONCENTRATION CLUSTER"

    return "LIMITED CONCENTRATION CLUSTER"

# =============================================================================
# NETWORK STABILITY
# =============================================================================

def network_stability(
    average_centrality
):
    """
    Determine systemic network stability.
    """

    if average_centrality < 0.20:

        return "STABLE NETWORK"

    elif average_centrality < 0.40:

        return "ELEVATED NETWORK RISK"

    elif average_centrality < 0.60:

        return "HIGH NETWORK INTERDEPENDENCE"

    return "SYSTEMIC NETWORK INSTABILITY"

# =============================================================================
# EXECUTIVE NETWORK NARRATIVE
# =============================================================================

def generate_network_narrative(
    borrower_id,
    node_classification,
    systemic_score
):
    """
    Generate executive systemic-risk commentary.
    """

    narrative = (
        f"Borrower {borrower_id} is classified as "
        f"{node_classification.lower()} with "
        f"systemic importance score of "
        f"{systemic_score}."
    )

    return narrative

# =============================================================================
# BUILD NETWORK ANALYSIS
# =============================================================================

def run_network_analysis(
    portfolio_df
):
    """
    Run enterprise financial network analysis.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING NETWORK BUILDER")
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

    # -------------------------------------------------------------------------
    # BUILD EDGE NETWORK
    # -------------------------------------------------------------------------

    edge_df = build_network_edges(
        portfolio_df
    )

    # -------------------------------------------------------------------------
    # NODE ANALYSIS
    # -------------------------------------------------------------------------

    network_results = []

    for _, borrower in portfolio_df.iterrows():

        borrower_id = borrower["borrower_id"]

        borrower_exposure = borrower["ead"]

        centrality = node_centrality(
            borrower_id,
            edge_df
        )

        concentration = exposure_concentration(
            borrower_exposure,
            total_portfolio_exposure
        )

        systemic_score = systemic_importance(
            centrality,
            concentration
        )

        node_classification = (
            systemic_node_classification(
                centrality
            )
        )

        narrative = generate_network_narrative(
            borrower_id,
            node_classification,
            systemic_score
        )

        network_results.append({

            "borrower_id":
                borrower_id,

            "network_centrality":
                centrality,

            "exposure_concentration_pct":
                concentration,

            "systemic_importance_score":
                systemic_score,

            "systemic_node_classification":
                node_classification,

            "executive_narrative":
                narrative,
        })

    network_df = pd.DataFrame(
        network_results
    )

    # -------------------------------------------------------------------------
    # CLUSTER ANALYSIS
    # -------------------------------------------------------------------------

    edge_df["cluster_classification"] = (
        edge_df["connection_weight"]
        .apply(cluster_classification)
    )

    # -------------------------------------------------------------------------
    # NETWORK STABILITY
    # -------------------------------------------------------------------------

    average_centrality = round(
        float(
            network_df[
                "network_centrality"
            ].mean()
        ),
        4
    )

    stability = network_stability(
        average_centrality
    )

    # -------------------------------------------------------------------------
    # SUMMARY
    # -------------------------------------------------------------------------

    summary = {

        "average_network_centrality":
            average_centrality,

        "network_stability":
            stability,

        "total_network_exposure":
            round(
                float(
                    total_portfolio_exposure
                ),
                2
            ),

        "total_connections":
            len(edge_df),

        "average_connection_weight":
            round(
                float(
                    edge_df[
                        "connection_weight"
                    ].mean()
                ),
                4
            ),

        "highest_systemic_score":
            round(
                float(
                    network_df[
                        "systemic_importance_score"
                    ].max()
                ),
                2
            ),

        "critical_nodes":
            int(
                (
                    network_df[
                        "systemic_node_classification"
                    ]
                    == "CRITICAL SYSTEMIC NODE"
                ).sum()
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] NETWORK SUMMARY\n")

    for key, value in summary.items():

        print(f"{key}: {value}")

    print("\n" + "-" * 80)

    print("\nSYSTEMIC NODE ANALYSIS\n")

    print(
        network_df[
            [
                "borrower_id",
                "network_centrality",
                "exposure_concentration_pct",
                "systemic_importance_score",
                "systemic_node_classification",
            ]
        ]
    )

    print("\n" + "-" * 80)

    print("\nNETWORK CONNECTIONS\n")

    print(
        edge_df[
            [
                "source",
                "target",
                "connection_weight",
                "cluster_classification",
            ]
        ].head(25)
    )

    print("=" * 80)

    return {

        "network_results":
            network_df,

        "network_edges":
            edge_df,

        "summary":
            summary,
    }

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "borrower_id": "B1001",
        "ead": 24000,
    },

    {
        "borrower_id": "B1002",
        "ead": 72000,
    },

    {
        "borrower_id": "B1003",
        "ead": 130000,
    },

    {
        "borrower_id": "B1004",
        "ead": 46000,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    run_network_analysis(
        SAMPLE_PORTFOLIO
    )

    print("\n[KRONOS] NETWORK BUILDER COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================
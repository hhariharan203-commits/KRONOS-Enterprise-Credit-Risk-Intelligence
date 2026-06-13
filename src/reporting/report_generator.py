# =============================================================================
# KRONOS — REPORT GENERATOR
# File: src/reporting/report_generator.py
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime
from contextlib import redirect_stdout
from io import StringIO

# =============================================================================
# IMPORT KRONOS REPORTING MODULES
# =============================================================================

from src.reporting.narrative_engine import (
    run_narrative_engine
)

from src.reporting.pdf_builder import (
    build_pdf_report
)
from src.contagion.contagion_engine import run_contagion_analysis
from src.decisioning.decision_terminal import run_decision_engine
from src.ews.ews_engine import run_ews_engine
from src.provisioning.ecl_calculator import run_ecl_pipeline
from src.stress_testing.stress_engine import run_stress_pipeline
from src.shared.utils import normalize_ifrs_stage, normalize_ifrs_stage_series

# =============================================================================
# ENGINE-DERIVED REPORTING CONTEXT
# =============================================================================

def _has_columns(
    frame,
    columns
):
    return all(
        column in frame.columns
        for column in columns
    )


def _run_engine(
    context,
    name,
    func,
    *args,
    **kwargs
):
    try:
        with redirect_stdout(StringIO()):
            result = func(*args, **kwargs)

        context["engine_status"][name] = "COMPLETED"
        return result

    except Exception as exc:
        context["engine_status"][name] = "FAILED"
        context["engine_errors"][name] = (
            f"{type(exc).__name__}: {exc}"
        )
        return None


def _prepare_reporting_stages(
    portfolio_df
):
    if "ifrs_stage" in portfolio_df.columns:
        portfolio_df["ifrs_stage"] = normalize_ifrs_stage_series(
            portfolio_df["ifrs_stage"]
        )

    if "current_stage" in portfolio_df.columns:
        portfolio_df["current_stage"] = normalize_ifrs_stage_series(
            portfolio_df["current_stage"]
        )

    elif "ifrs_stage" in portfolio_df.columns:
        portfolio_df["current_stage"] = portfolio_df["ifrs_stage"]

    else:
        portfolio_df["current_stage"] = "STAGE 1"

    return portfolio_df


def _derive_ews_scores(
    portfolio_df,
    context
):
    if "early_warning_score" in portfolio_df.columns:
        portfolio_df["ews_score"] = portfolio_df[
            "early_warning_score"
        ]
        return portfolio_df

    if "pd_score" not in portfolio_df.columns:
        context["engine_status"]["ews"] = "SKIPPED"
        return portfolio_df

    scores = []

    for _, row in portfolio_df.iterrows():
        result = _run_engine(
            context,
            "ews",
            run_ews_engine,
            {
                "current_pd": row.get("pd_score", 0),
                "previous_pd": row.get("previous_pd", row.get("pd_score", 0) * 0.8),
                "credit_utilization": row.get("credit_utilization", 0),
                "payment_burden_ratio": row.get("payment_burden_ratio", 0),
                "loan_to_income_ratio": row.get("loan_to_income_ratio", 0),
                "total_delinquency": row.get("total_delinquency", 0),
            },
        )

        scores.append(
            result.get("ews_score", 0)
            if result
            else 0
        )

    portfolio_df["ews_score"] = scores
    portfolio_df["early_warning_score"] = scores
    return portfolio_df


def prepare_engine_derived_reporting_data(
    portfolio_df
):
    """
    Enrich report inputs from core engines when dashboard proxies are absent.
    """

    portfolio_df = _prepare_reporting_stages(
        portfolio_df.copy()
    )

    context = {
        "engine_status": {},
        "engine_errors": {},
        "engine_summaries": {},
    }

    portfolio_df = _derive_ews_scores(
        portfolio_df,
        context
    )

    if _has_columns(
        portfolio_df,
        ["borrower_id", "pd_score", "lgd", "ead", "current_stage"]
    ):
        ecl_result = _run_engine(
            context,
            "provisioning",
            run_ecl_pipeline,
            portfolio_df,
        )

        if ecl_result:
            context["engine_summaries"]["provisioning"] = ecl_result[
                "summary"
            ]
            reserve_results = ecl_result["portfolio_results"][
                [
                    "borrower_id",
                    "reserve_concentration",
                    "reserve_coverage_ratio",
                ]
            ]
            portfolio_df = portfolio_df.merge(
                reserve_results,
                on="borrower_id",
                how="left",
            )
            portfolio_df["reserve_pressure_score"] = (
                portfolio_df["reserve_concentration"]
                .fillna(0)
                .clip(lower=0)
                * 100
            )

    if _has_columns(
        portfolio_df,
        ["borrower_id", "pd_score", "lgd", "ead"]
    ):
        stress_result = _run_engine(
            context,
            "stress_testing",
            run_stress_pipeline,
            portfolio_df,
            "SEVERE RECESSION",
        )

        if stress_result:
            context["engine_summaries"]["stress_testing"] = stress_result[
                "summary"
            ]
            stress_results = stress_result["portfolio_results"][
                [
                    "borrower_id",
                    "loss_impact_pct",
                    "capital_pressure",
                ]
            ]
            portfolio_df = portfolio_df.merge(
                stress_results,
                on="borrower_id",
                how="left",
            )
            portfolio_df["stress_score"] = (
                portfolio_df["loss_impact_pct"]
                .fillna(0)
                .clip(lower=0, upper=100)
            )

        contagion_result = _run_engine(
            context,
            "contagion",
            run_contagion_analysis,
            portfolio_df,
        )

        if contagion_result:
            context["engine_summaries"]["contagion"] = contagion_result[
                "summary"
            ]
            contagion_results = contagion_result["contagion_results"][
                [
                    "borrower_id",
                    "systemic_impact_score",
                    "average_contagion_risk",
                ]
            ]
            portfolio_df = portfolio_df.merge(
                contagion_results,
                on="borrower_id",
                how="left",
            )
            portfolio_df["systemic_risk_score"] = (
                portfolio_df["systemic_impact_score"]
                .fillna(0)
                .clip(lower=0, upper=100)
            )

    if "reserve_pressure_score" not in portfolio_df.columns:
        portfolio_df["reserve_pressure_score"] = 20

    if "systemic_risk_score" not in portfolio_df.columns:
        portfolio_df["systemic_risk_score"] = portfolio_df.get(
            "early_warning_score",
            pd.Series([0] * len(portfolio_df))
        )

    if _has_columns(
        portfolio_df,
        ["borrower_id", "pd_score"]
    ):
        decision_result = _run_engine(
            context,
            "decision",
            run_decision_engine,
            portfolio_df,
        )

        if decision_result:
            context["engine_summaries"]["decision"] = decision_result[
                "summary"
            ]
            decision_results = decision_result["decision_results"][
                [
                    "borrower_id",
                    "aggregated_risk_score",
                    "underwriting_decision",
                    "decision_confidence",
                ]
            ]
            portfolio_df = portfolio_df.merge(
                decision_results,
                on="borrower_id",
                how="left",
                suffixes=("", "_engine"),
            )
            portfolio_df["enterprise_risk_score"] = (
                portfolio_df["aggregated_risk_score"]
                .fillna(0)
                .clip(lower=0, upper=100)
            )

    if "enterprise_risk_score" not in portfolio_df.columns:
        portfolio_df["enterprise_risk_score"] = (
            portfolio_df.get(
                "pd_score",
                pd.Series([0] * len(portfolio_df))
            )
            * 100
        )

    if "stress_score" not in portfolio_df.columns:
        portfolio_df["stress_score"] = portfolio_df.get(
            "early_warning_score",
            pd.Series([0] * len(portfolio_df))
        )

    if "live_risk_pulse_score" not in portfolio_df.columns:
        portfolio_df["live_risk_pulse_score"] = (
            portfolio_df[
                [
                    "enterprise_risk_score",
                    "systemic_risk_score",
                    "stress_score",
                ]
            ]
            .mean(axis=1)
        )

    if "capital_ratio" not in portfolio_df.columns:
        portfolio_df["capital_ratio"] = (
            12
            - (
                portfolio_df["stress_score"].fillna(0).clip(0, 100)
                / 25
            )
        ).clip(lower=4, upper=14)

    return portfolio_df, context

# =============================================================================
# EXECUTIVE METRIC AGGREGATION
# =============================================================================

def aggregate_executive_metrics(
    portfolio_df
):
    """
    Aggregate institutional portfolio metrics.
    """

    metrics = {

        "average_enterprise_risk":
            round(
                float(
                    portfolio_df[
                        "enterprise_risk_score"
                    ].mean()
                ),
                2
            ),

        "average_systemic_risk":
            round(
                float(
                    portfolio_df[
                        "systemic_risk_score"
                    ].mean()
                ),
                2
            ),

        "average_capital_ratio":
            round(
                float(
                    portfolio_df[
                        "capital_ratio"
                    ].mean()
                ),
                2
            ),

        "average_stress_score":
            round(
                float(
                    portfolio_df[
                        "stress_score"
                    ].mean()
                ),
                2
            ),

        "average_risk_pulse":
            round(
                float(
                    portfolio_df[
                        "live_risk_pulse_score"
                    ].mean()
                ),
                2
            ),

        "critical_risk_entities":
            int(
                (
                    portfolio_df[
                        "enterprise_risk_score"
                    ] >= 85
                ).sum()
            ),

        "maximum_enterprise_risk":
            round(
                float(
                    portfolio_df[
                        "enterprise_risk_score"
                    ].max()
                ),
                2
            ),

        "maximum_systemic_risk":
            round(
                float(
                    portfolio_df[
                        "systemic_risk_score"
                    ].max()
                ),
                2
            ),

        "minimum_capital_ratio":
            round(
                float(
                    portfolio_df[
                        "capital_ratio"
                    ].min()
                ),
                2
            ),

        "portfolio_size":
            int(
                len(
                    portfolio_df
                )
            ),
    }

    return metrics

# =============================================================================
# GOVERNANCE SUMMARY
# =============================================================================

def governance_summary(
    metrics
):
    """
    Generate governance intelligence summary.
    """

    avg_risk = metrics[
        "average_enterprise_risk"
    ]

    if avg_risk < 25:

        governance_status = (
            "STANDARD GOVERNANCE CONDITIONS"
        )

        board_priority = (
            "LOW BOARD PRIORITY"
        )

        action = (
            "Continue standard enterprise monitoring."
        )

    elif avg_risk < 50:

        governance_status = (
            "ELEVATED GOVERNANCE MONITORING"
        )

        board_priority = (
            "MODERATE BOARD PRIORITY"
        )

        action = (
            "Increase enterprise monitoring intensity."
        )

    elif avg_risk < 75:

        governance_status = (
            "HIGH GOVERNANCE ESCALATION"
        )

        board_priority = (
            "HIGH BOARD PRIORITY"
        )

        action = (
            "Activate enterprise mitigation controls."
        )

    else:

        governance_status = (
            "CRITICAL GOVERNANCE ESCALATION"
        )

        board_priority = (
            "CRITICAL BOARD PRIORITY"
        )

        action = (
            "Activate executive crisis-management framework."
        )

    summary = {

        "governance_status":
            governance_status,

        "board_priority":
            board_priority,

        "recommended_action":
            action,
    }

    return summary

# =============================================================================
# REGIME CLASSIFICATION
# =============================================================================

def classify_regime(
    stress_score
):
    """
    Determine macroeconomic regime condition.
    """

    if stress_score < 25:

        return "STABLE ECONOMIC REGIME"

    elif stress_score < 50:

        return "ELEVATED RISK REGIME"

    elif stress_score < 75:

        return "STRESSED ECONOMIC REGIME"

    return "SYSTEMIC CRISIS REGIME"

# =============================================================================
# EXECUTIVE ESCALATION
# =============================================================================

def executive_escalation(
    risk_score,
    regime_classification=None,
    stress_score=None
):
    """
    Determine executive escalation pathway.
    """

    if (
        regime_classification == "SYSTEMIC CRISIS REGIME"
        or (
            stress_score is not None
            and stress_score >= 75
        )
    ):

        return "EXECUTIVE CRISIS MANAGEMENT"

    if risk_score < 25:

        return "STANDARD MONITORING"

    elif risk_score < 50:

        return "ENTERPRISE RISK ESCALATION"

    elif risk_score < 75:

        return "BOARD RISK COMMITTEE REVIEW"

    return "EXECUTIVE CRISIS MANAGEMENT"

# =============================================================================
# BUILD METRICS DATAFRAME
# =============================================================================

def build_metrics_dataframe(
    metrics
):
    """
    Convert enterprise metrics into reporting table.
    """

    rows = []

    for key, value in metrics.items():

        rows.append({

            "Metric":
                key.replace(
                    "_",
                    " "
                ).title(),

            "Value":
                value,
        })

    return pd.DataFrame(rows)

# =============================================================================
# ENTERPRISE REPORT SECTIONS
# =============================================================================

def _series_or_default(
    portfolio_df,
    column_name,
    default_value=0
):
    """
    Return a portfolio column or a default-valued series.
    """

    if column_name in portfolio_df.columns:

        return portfolio_df[column_name]

    return pd.Series(
        [default_value] * len(portfolio_df)
    )


def portfolio_risk_summary(
    portfolio_df,
    metrics
):
    """
    Summarize portfolio-level credit and enterprise risk.
    """

    pd_scores = _series_or_default(
        portfolio_df,
        "pd_score",
        0
    )

    enterprise_scores = _series_or_default(
        portfolio_df,
        "enterprise_risk_score",
        metrics["average_enterprise_risk"]
    )

    return {

        "portfolio_size":
            metrics["portfolio_size"],

        "average_pd_score":
            round(
                float(pd_scores.mean()),
                4
            ),

        "average_enterprise_risk":
            metrics["average_enterprise_risk"],

        "maximum_enterprise_risk":
            metrics["maximum_enterprise_risk"],

        "high_risk_accounts":
            int(
                (
                    enterprise_scores >= 75
                ).sum()
            ),
    }


def ifrs9_summary(
    portfolio_df
):
    """
    Summarize IFRS9 portfolio staging.
    """

    stage_column = (
        "ifrs_stage"
        if "ifrs_stage" in portfolio_df.columns
        else "current_stage"
    )

    if stage_column not in portfolio_df.columns:

        return {

            "stage_1_accounts":
                0,

            "stage_2_accounts":
                0,

            "stage_3_accounts":
                0,

            "stage_2_3_accounts":
                0,
        }

    stages = normalize_ifrs_stage_series(
        portfolio_df[stage_column]
    )

    stage_1 = int((stages == "STAGE 1").sum())
    stage_2 = int((stages == "STAGE 2").sum())
    stage_3 = int((stages == "STAGE 3").sum())

    return {

        "stage_1_accounts":
            stage_1,

        "stage_2_accounts":
            stage_2,

        "stage_3_accounts":
            stage_3,

        "stage_2_3_accounts":
            stage_2 + stage_3,
    }


def stress_testing_summary(
    portfolio_df
):
    """
    Summarize portfolio stress outcomes.
    """

    stress_scores = _series_or_default(
        portfolio_df,
        "stress_score",
        0
    )

    return {

        "average_stress_score":
            round(
                float(stress_scores.mean()),
                2
            ),

        "maximum_stress_score":
            round(
                float(stress_scores.max()),
                2
            ),

        "stressed_accounts":
            int(
                (
                    stress_scores >= 75
                ).sum()
            ),
    }


def concentration_risk_summary(
    portfolio_df
):
    """
    Summarize top exposure concentration.
    """

    if "ead" not in portfolio_df.columns:

        return {

            "total_exposure":
                0,

            "largest_exposure":
                0,

            "top_10_exposure_share":
                0,
        }

    exposures = portfolio_df["ead"].fillna(0)
    total_exposure = float(exposures.sum())
    top_10_exposure = float(
        exposures.sort_values(
            ascending=False
        ).head(10).sum()
    )

    concentration_share = (
        top_10_exposure / total_exposure
        if total_exposure > 0
        else 0
    )

    return {

        "total_exposure":
            round(total_exposure, 2),

        "largest_exposure":
            round(float(exposures.max()), 2),

        "top_10_exposure_share":
            round(concentration_share, 4),
    }


def watchlist_summary(
    portfolio_df
):
    """
    Summarize watchlist and escalated accounts.
    """

    decision_column = (
        "underwriting_decision_engine"
        if "underwriting_decision_engine" in portfolio_df.columns
        else "underwriting_decision"
    )

    decisions = _series_or_default(
        portfolio_df,
        decision_column,
        ""
    ).astype(str).str.upper()

    watchlist_accounts = int(
        decisions.str.contains(
            "WATCH|WATCHLIST",
            na=False,
            regex=True
        ).sum()
    )

    escalated_accounts = int(
        decisions.str.contains(
            "REJECT|REJECTED|ENHANCED|REVIEW|WATCH|WATCHLIST",
            na=False,
            regex=True
        ).sum()
    )

    return {

        "watchlist_accounts":
            watchlist_accounts,

        "escalated_accounts":
            escalated_accounts,
    }


def top_exposure_summary(
    portfolio_df,
    top_n=5
):
    """
    Return the largest portfolio exposures.
    """

    if "ead" not in portfolio_df.columns:

        return []

    display_columns = [
        column
        for column in [
            "borrower_id",
            "ead",
            "pd_score",
            "lgd",
            "ifrs_stage",
            "underwriting_decision",
        ]
        if column in portfolio_df.columns
    ]

    return (
        portfolio_df
        .sort_values(
            by="ead",
            ascending=False
        )
        .head(top_n)[display_columns]
        .to_dict("records")
    )


def executive_narrative_section(
    enterprise_sections
):
    """
    Create a concise executive narrative from enterprise sections.
    """

    portfolio = enterprise_sections["portfolio_risk_summary"]
    ifrs9 = enterprise_sections["ifrs9_summary"]
    stress = enterprise_sections["stress_testing_summary"]
    watchlist = enterprise_sections["watchlist_summary"]

    return {

        "executive_narrative":
            (
                f"Portfolio contains {portfolio['portfolio_size']} accounts "
                f"with average enterprise risk of "
                f"{portfolio['average_enterprise_risk']}. "
                f"IFRS9 Stage 2/3 accounts total "
                f"{ifrs9['stage_2_3_accounts']}. "
                f"Stress monitoring identified "
                f"{stress['stressed_accounts']} stressed accounts and "
                f"{watchlist['escalated_accounts']} escalated decisions."
            )
    }


def build_enterprise_sections(
    portfolio_df,
    metrics
):
    """
    Build institutional reporting sections.
    """

    sections = {

        "portfolio_risk_summary":
            portfolio_risk_summary(
                portfolio_df,
                metrics
            ),

        "ifrs9_summary":
            ifrs9_summary(
                portfolio_df
            ),

        "stress_testing_summary":
            stress_testing_summary(
                portfolio_df
            ),

        "concentration_risk_summary":
            concentration_risk_summary(
                portfolio_df
            ),

        "watchlist_summary":
            watchlist_summary(
                portfolio_df
            ),

        "top_exposure_summary":
            top_exposure_summary(
                portfolio_df
            ),
    }

    sections["executive_narrative_section"] = (
        executive_narrative_section(
            sections
        )
    )

    return sections

# =============================================================================
# GENERATE INSTITUTIONAL REPORT
# =============================================================================

def generate_institutional_report(
    portfolio_df,
    output_filename="kronos_enterprise_report.pdf"
):
    """
    Master executive reporting orchestration workflow.
    """

    print("\n" + "=" * 80)
    print("[KRONOS] RUNNING REPORT GENERATOR")
    print("=" * 80)

    portfolio_df, engine_context = prepare_engine_derived_reporting_data(
        portfolio_df
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE METRICS
    # -------------------------------------------------------------------------

    metrics = aggregate_executive_metrics(
        portfolio_df
    )

    # -------------------------------------------------------------------------
    # GOVERNANCE SUMMARY
    # -------------------------------------------------------------------------

    governance = governance_summary(
        metrics
    )

    # -------------------------------------------------------------------------
    # REGIME + ESCALATION
    # -------------------------------------------------------------------------

    regime = classify_regime(
        metrics[
            "average_stress_score"
        ]
    )

    escalation = executive_escalation(
        metrics[
            "average_enterprise_risk"
        ],
        regime_classification=regime,
        stress_score=metrics[
            "average_stress_score"
        ]
    )

    # -------------------------------------------------------------------------
    # NARRATIVE ENGINE
    # -------------------------------------------------------------------------

    narrative_results = (
        run_narrative_engine(

            enterprise_risk_score=
                metrics[
                    "average_enterprise_risk"
                ],

            systemic_risk_score=
                metrics[
                    "average_systemic_risk"
                ],

            capital_ratio=
                metrics[
                    "average_capital_ratio"
                ],

            regime_classification=
                regime,

            escalation_level=
                escalation,

            stress_score=
                metrics[
                    "average_stress_score"
                ],
        )
    )

    # -------------------------------------------------------------------------
    # EXECUTIVE SUMMARY
    # -------------------------------------------------------------------------

    executive_summary = {

        "enterprise_risk_score":
            metrics[
                "average_enterprise_risk"
            ],

        "systemic_risk_score":
            metrics[
                "average_systemic_risk"
            ],

        "capital_ratio":
            metrics[
                "average_capital_ratio"
            ],

        "risk_pulse":
            metrics[
                "average_risk_pulse"
            ],

        "critical_entities":
            metrics[
                "critical_risk_entities"
            ],

        "maximum_enterprise_risk":
            metrics[
                "maximum_enterprise_risk"
            ],

        "maximum_systemic_risk":
            metrics[
                "maximum_systemic_risk"
            ],

        "minimum_capital_ratio":
            metrics[
                "minimum_capital_ratio"
            ],

        "portfolio_size":
            metrics[
                "portfolio_size"
            ],

        "regime_classification":
            regime,

        "executive_escalation":
            escalation,

        "report_generation_time":
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
    }

    # -------------------------------------------------------------------------
    # METRICS TABLE
    # -------------------------------------------------------------------------

    metrics_df = build_metrics_dataframe(
        metrics
    )

    # -------------------------------------------------------------------------
    # ENTERPRISE REPORT SECTIONS
    # -------------------------------------------------------------------------

    enterprise_sections = build_enterprise_sections(
        portfolio_df,
        metrics
    )

    # -------------------------------------------------------------------------
    # BUILD PDF REPORT
    # -------------------------------------------------------------------------

    pdf_path = build_pdf_report(

        executive_summary=
            executive_summary,

        narrative_results=
            narrative_results,

        metrics_df=
            metrics_df,

        governance_summary=
            governance,

        enterprise_sections=
            enterprise_sections,

        output_filename=
            output_filename,
    )

    # -------------------------------------------------------------------------
    # FINAL REPORT PACKAGE
    # -------------------------------------------------------------------------

    report_package = {

        "executive_summary":
            executive_summary,

        "governance_summary":
            governance,

        "narrative_results":
            narrative_results,

        "metrics":
            metrics,

        "enterprise_sections":
            enterprise_sections,

        "engine_reporting_context":
            engine_context,

        "pdf_report_path":
            pdf_path,

        "generated_timestamp":
            datetime.utcnow().strftime(
                "%Y-%m-%d %H:%M:%S UTC"
            ),
    }

    # -------------------------------------------------------------------------
    # REPORTING
    # -------------------------------------------------------------------------

    print("\n[KRONOS] REPORT GENERATION COMPLETE\n")

    for key, value in report_package.items():

        print(f"\n{key}:\n{value}")

    print("\n" + "=" * 80)

    return report_package

# =============================================================================
# SAMPLE PORTFOLIO
# =============================================================================

SAMPLE_PORTFOLIO = pd.DataFrame([

    {
        "enterprise_risk_score": 24,
        "systemic_risk_score": 18,
        "capital_ratio": 13.1,
        "stress_score": 22,
        "live_risk_pulse_score": 25,
    },

    {
        "enterprise_risk_score": 58,
        "systemic_risk_score": 52,
        "capital_ratio": 10.2,
        "stress_score": 48,
        "live_risk_pulse_score": 54,
    },

    {
        "enterprise_risk_score": 92,
        "systemic_risk_score": 90,
        "capital_ratio": 6.5,
        "stress_score": 88,
        "live_risk_pulse_score": 95,
    },

    {
        "enterprise_risk_score": 38,
        "systemic_risk_score": 32,
        "capital_ratio": 11.6,
        "stress_score": 30,
        "live_risk_pulse_score": 36,
    },

])

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":

    generate_institutional_report(

        portfolio_df=SAMPLE_PORTFOLIO,

        output_filename=
            "kronos_master_enterprise_report.pdf"
    )

    print("\n[KRONOS] REPORT GENERATOR COMPLETED")

# =============================================================================
# END OF FILE
# =============================================================================

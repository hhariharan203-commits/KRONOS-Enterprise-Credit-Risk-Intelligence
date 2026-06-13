import pandas as pd
import numpy as np

import plotly.express as px
import plotly.graph_objects as go

import streamlit as st

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:

    sys.path.append(
        str(ROOT_DIR)
    )

# =============================================================================
# PROVISIONING ENGINE
# =============================================================================

from src.provisioning.provisioning_engine import (
    classify_ifrs9_stage,
    calculate_ecl
)

# =============================================================================
# STAGE MIGRATION
# =============================================================================

from src.provisioning.stage_migration import (
    run_stage_migration_analysis
)

# =============================================================================
# ECL CALCULATOR
# =============================================================================

from src.provisioning.ecl_calculator import (
    run_ecl_pipeline
)

# =============================================================================
# RESERVE SIMULATOR
# =============================================================================

from src.provisioning.reserve_simulator import (
    run_reserve_simulation,
    run_all_scenarios
)

from src.shared.cache_manager import timed_cache

from app.live_intelligence_components import (
    get_dashboard_live_context,
    macro_intelligence,
    market_intelligence,
    render_live_status_card,
    live_summary,
)

cached_run_stage_migration_analysis = timed_cache()(run_stage_migration_analysis)
cached_run_ecl_pipeline = timed_cache()(run_ecl_pipeline)
cached_run_reserve_simulation = timed_cache()(run_reserve_simulation)
cached_run_all_scenarios = timed_cache()(run_all_scenarios)

# =============================================================================
# KRONOS GLOBAL DESIGN SYSTEM
# =============================================================================

KRONOS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

/* ── ROOT TOKENS ─────────────────────────────────────────────── */
:root {
    --navy-950:   #030712;
    --navy-900:   #060f23;
    --navy-800:   #0a1628;
    --navy-700:   #0f1f38;
    --navy-600:   #152848;
    --navy-500:   #1e3a5f;
    --slate-600:  #334155;
    --slate-500:  #475569;
    --slate-400:  #64748b;
    --slate-300:  #94a3b8;
    --slate-200:  #cbd5e1;
    --slate-100:  #e2e8f0;
    --emerald:    #10b981;
    --emerald-dk: #059669;
    --amber:      #f59e0b;
    --amber-dk:   #d97706;
    --crimson:    #ef4444;
    --crimson-dk: #dc2626;
    --sapphire:   #3b82f6;
    --sapphire-dk:#2563eb;
    --teal:       #14b8a6;
    --teal-dk:    #0d9488;
    --gold:       #fbbf24;
    --text-prime: #e2e8f0;
    --text-muted: #94a3b8;
    --text-dim:   #64748b;
    --border:     rgba(148,163,184,0.12);
    --border-hi:  rgba(148,163,184,0.25);
    --glow-teal:  rgba(20,184,166,0.14);
    --glow-blue:  rgba(59,130,246,0.12);
}

/* ── GLOBAL RESET ────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', 'SF Pro Display', system-ui, sans-serif !important;
    background-color: var(--navy-950) !important;
    color: var(--text-prime) !important;
}

.main .block-container {
    padding: 1.5rem 2.5rem 4rem !important;
    max-width: 1600px !important;
    background: var(--navy-950) !important;
}

/* ── HIDE STREAMLIT CHROME ───────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── EXECUTIVE BANNER ────────────────────────────────────────── */
.kronos-banner {
    background: linear-gradient(135deg, var(--navy-800) 0%, var(--navy-700) 40%, var(--navy-600) 100%);
    border: 1px solid var(--border-hi);
    border-top: 3px solid var(--teal);
    border-radius: 4px;
    padding: 2rem 2.5rem 1.75rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.kronos-banner::before {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 420px; height: 100%;
    background: radial-gradient(ellipse at top right, var(--glow-teal), transparent 70%);
    pointer-events: none;
}
.kronos-banner-title {
    font-size: 1.85rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-prime);
    margin: 0 0 0.25rem;
    line-height: 1.2;
}
.kronos-banner-title span {
    color: var(--teal);
}
.kronos-banner-sub {
    font-size: 0.78rem;
    font-weight: 400;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace !important;
    margin-top: 0.5rem;
}
.kronos-banner-tags {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.kronos-tag {
    background: rgba(20,184,166,0.1);
    border: 1px solid rgba(20,184,166,0.3);
    color: var(--teal);
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.2rem 0.65rem;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace !important;
}
.kronos-tag.green {
    background: rgba(16,185,129,0.1);
    border-color: rgba(16,185,129,0.3);
    color: var(--emerald);
}
.kronos-tag.amber {
    background: rgba(245,158,11,0.1);
    border-color: rgba(245,158,11,0.3);
    color: var(--amber);
}
.kronos-tag.red {
    background: rgba(239,68,68,0.1);
    border-color: rgba(239,68,68,0.3);
    color: var(--crimson);
}
.kronos-tag.blue {
    background: rgba(59,130,246,0.12);
    border-color: rgba(59,130,246,0.3);
    color: var(--sapphire);
}

/* ── SECTION HEADERS ─────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin: 2.25rem 0 1.25rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border);
}
.section-header-icon {
    width: 32px; height: 32px;
    background: var(--navy-700);
    border: 1px solid var(--border-hi);
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem;
}
.section-header-text {
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--slate-200);
    font-family: 'IBM Plex Mono', monospace !important;
}
.section-header-badge {
    margin-left: auto;
    background: var(--navy-700);
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.18rem 0.55rem;
    border-radius: 2px;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── KPI CARDS ───────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--navy-800) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    padding: 1rem 1.25rem !important;
    position: relative !important;
    overflow: hidden !important;
    transition: border-color 0.2s !important;
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-hi) !important;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--teal), transparent);
}
[data-testid="stMetricLabel"] {
    font-size: 0.62rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.4rem !important;
    font-weight: 600 !important;
    color: var(--text-prime) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    letter-spacing: -0.02em !important;
    line-height: 1.3 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.7rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── DATAFRAMES ──────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    background: var(--navy-900) !important;
}
[data-testid="stDataFrame"] thead tr th {
    background: var(--navy-700) !important;
    color: var(--text-muted) !important;
    font-size: 0.62rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-family: 'IBM Plex Mono', monospace !important;
    border-bottom: 1px solid var(--border-hi) !important;
    padding: 0.6rem 0.75rem !important;
}
[data-testid="stDataFrame"] tbody tr td {
    background: var(--navy-900) !important;
    color: var(--text-prime) !important;
    font-size: 0.78rem !important;
    font-family: 'IBM Plex Mono', monospace !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 0.5rem 0.75rem !important;
}
[data-testid="stDataFrame"] tbody tr:hover td {
    background: var(--navy-800) !important;
}

/* ── ALERT BOXES ─────────────────────────────────────────────── */
.stAlert {
    border-radius: 4px !important;
    border-left-width: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.7 !important;
}

/* ── DIVIDER ─────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── NARRATIVE BLOCK ─────────────────────────────────────────── */
.kronos-narrative {
    background: var(--navy-800);
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
    color: var(--slate-300);
}
.kronos-narrative-warn {
    border-left-color: var(--amber);
    background: rgba(245,158,11,0.05);
}
.kronos-narrative-critical {
    border-left-color: var(--crimson);
    background: rgba(239,68,68,0.05);
}
.kronos-narrative-success {
    border-left-color: var(--emerald);
    background: rgba(16,185,129,0.05);
}
.kronos-narrative-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--teal);
    margin-bottom: 0.75rem;
    display: block;
}
.kronos-narrative-warn .kronos-narrative-label     { color: var(--amber); }
.kronos-narrative-critical .kronos-narrative-label { color: var(--crimson); }
.kronos-narrative-success .kronos-narrative-label  { color: var(--emerald); }

/* ── FOOTER ──────────────────────────────────────────────────── */
.kronos-footer {
    background: var(--navy-900);
    border: 1px solid var(--border);
    border-top: 2px solid var(--border-hi);
    border-radius: 4px;
    padding: 0.85rem 1.5rem;
    margin-top: 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
}
.kronos-footer-text {
    font-size: 0.62rem;
    color: var(--text-dim);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
}
.kronos-footer-tags {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
}
</style>
"""

# =============================================================================
# PLOTLY THEME
# =============================================================================

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(6,15,35,0)",
    plot_bgcolor="rgba(10,22,40,0.5)",
    font=dict(
        family="IBM Plex Mono, monospace",
        color="#94a3b8",
        size=11
    ),
    title=dict(
        font=dict(
            family="IBM Plex Sans, sans-serif",
            color="#e2e8f0",
            size=13
        ),
        x=0,
        xanchor="left",
        pad=dict(l=4, b=12)
    ),
    xaxis=dict(
        gridcolor="rgba(148,163,184,0.08)",
        linecolor="rgba(148,163,184,0.15)",
        tickcolor="rgba(148,163,184,0.15)",
        zeroline=False,
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.08)",
        linecolor="rgba(148,163,184,0.15)",
        tickcolor="rgba(148,163,184,0.15)",
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(10,22,40,0.6)",
        bordercolor="rgba(148,163,184,0.15)",
        borderwidth=1,
        font=dict(size=10)
    ),
    margin=dict(l=8, r=8, t=48, b=8),
    hoverlabel=dict(
        bgcolor="#0a1628",
        bordercolor="#334155",
        font=dict(family="IBM Plex Mono", size=11)
    )
)

PLOTLY_COLORS = [
    "#14b8a6", "#3b82f6", "#10b981",
    "#f59e0b", "#ef4444", "#8b5cf6",
    "#f97316", "#06b6d4", "#84cc16"
]

STAGE_COLORMAP = {
    "STAGE 1": "#10b981",
    "STAGE 2": "#f59e0b",
    "STAGE 3": "#ef4444",
}


def _apply_layout(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def _section(icon, title, badge=None):
    badge_html = (
        f'<span class="section-header-badge">{badge}</span>'
        if badge else ""
    )
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-header-icon">{icon}</div>
            <span class="section-header-text">{title}</span>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def _narrative(content, variant="default", label="Executive Intelligence"):
    css_class = {
        "warn":     "kronos-narrative-warn",
        "critical": "kronos-narrative-critical",
        "success":  "kronos-narrative-success",
    }.get(variant, "")
    st.markdown(
        f"""
        <div class="kronos-narrative {css_class}">
            <span class="kronos-narrative-label">{label}</span>
            {content}
        </div>
        """,
        unsafe_allow_html=True
    )


def render(shared_data=None):

    shared_data = shared_data or {}

    # ── inject global CSS ────────────────────────────────────────
    st.markdown(KRONOS_CSS, unsafe_allow_html=True)

    # ==========================================================
    # EXECUTIVE BANNER
    # ==========================================================

    st.markdown(
        """
        <div class="kronos-banner">
            <div class="kronos-banner-title">
                <span>KRONOS</span> Provisioning Dashboard
            </div>
            <div class="kronos-banner-sub">
                Enterprise Credit Risk Intelligence Platform · IFRS 9 Provisioning & ECL Analytics Division
            </div>
            <div class="kronos-banner-tags">
                <span class="kronos-tag">IFRS 9</span>
                <span class="kronos-tag blue">ECL Analytics</span>
                <span class="kronos-tag green">Stage Migration</span>
                <span class="kronos-tag amber">Reserve Stress</span>
                <span class="kronos-tag red">Capital Impact</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    portfolio = (
        shared_data.get("portfolio", pd.DataFrame())
        .copy()
    )

    if portfolio.empty:
        st.warning(
            "Portfolio data unavailable."
        )
        return

    required_columns = {
        "borrower_id",
        "ead",
        "early_warning_score",
        "lgd",
        "pd_score",
    }
    missing_columns = sorted(required_columns - set(portfolio.columns))
    if missing_columns:
        st.warning(
            "Portfolio data missing required columns: "
            + ", ".join(missing_columns)
        )
        return

    # =============================================================================
    # IFRS9 DATA PREPARATION
    # =============================================================================

    portfolio = portfolio.copy()

    portfolio["current_stage"] = portfolio.apply(
        lambda row:
        classify_ifrs9_stage(
            row["pd_score"],
            row["early_warning_score"],
            row.get("total_delinquency", 0),
            row.get("current_rating", "A")
        ),
        axis=1
    )

    portfolio["expected_credit_loss"] = portfolio.apply(
        lambda row:
        calculate_ecl(
            row["pd_score"],
            row["lgd"],
            row["ead"],
            row["current_stage"]
        ),
        axis=1
    )

    portfolio["current_ecl"] = (
        portfolio["expected_credit_loss"]
    )

    portfolio["previous_stage"] = np.where(
        portfolio["pd_score"] < 0.10,
        "STAGE 1",
        np.where(
            portfolio["pd_score"] < 0.30,
            "STAGE 2",
            "STAGE 3"
        )
    )

    portfolio["previous_ecl"] = (
        portfolio["expected_credit_loss"]
        * 0.85
    )

    # =============================================================================
    # IFRS9 STAGE MIGRATION
    # =============================================================================

    migration_results = (
        cached_run_stage_migration_analysis(
            portfolio
        )
    )

    migration_df = (
        migration_results[
            "portfolio_results"
        ]
    )

    migration_summary = (
        migration_results[
            "summary"
        ]
    )

    transition_matrix = (
        migration_results[
            "transition_matrix"
        ]
    )
    transition_matrix = transition_matrix.copy()
    transition_matrix.index = [
        str(stage).replace("_", " ").upper()
        for stage in transition_matrix.index
    ]
    transition_matrix.columns = [
        str(stage).replace("_", " ").upper()
        for stage in transition_matrix.columns
    ]

    # =============================================================================
    # ECL ANALYTICS
    # =============================================================================

    ecl_results = (
        cached_run_ecl_pipeline(
            portfolio
        )
    )

    ecl_df = (
        ecl_results[
            "portfolio_results"
        ]
    )

    ecl_summary = (
        ecl_results[
            "summary"
        ]
    )

    top_ecl = (
        ecl_results[
            "top_reserve_exposures"
        ]
    )

    # =============================================================================
    # RESERVE STRESS TEST
    # =============================================================================

    stress_results = (
        cached_run_reserve_simulation(
            portfolio,
            scenario="SEVERE RECESSION"
        )
    )

    stress_df = (
        stress_results[
            "portfolio_results"
        ]
    )

    stress_summary = (
        stress_results[
            "summary"
        ]
    )

    stage_stress = (
        stress_results[
            "stage_stress_impact"
        ]
    )

    scenario_comparison = (
        cached_run_all_scenarios(
            portfolio
        )
    )

    live_context = get_dashboard_live_context(
        allow_api_refresh=True
    )
    live_data = live_summary(live_context)
    macro_data = macro_intelligence(live_context)
    market_data = market_intelligence(live_context)

    _section("🌐", "Live IFRS 9 Environment", "CONTEXT")
    render_live_status_card(live_context)

    live_cols = st.columns(3)
    live_cols[0].metric(
        "Macro Deterioration",
        f"{macro_data.get('macro_stress_score', 0):.2f}"
    )
    live_cols[1].metric(
        "Live Risk Regime",
        live_data.get("executive_risk_regime", "UNAVAILABLE")
    )
    live_cols[2].metric(
        "Market Stress",
        f"{market_data.get('market_risk_score', 0):.2f}"
    )

    # =============================================================================
    # EXECUTIVE PROVISIONING DASHBOARD
    # =============================================================================

    st.divider()

    _section("🏦", "Executive Provisioning Dashboard", "IFRS 9")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Portfolio ECL",
        f"${ecl_summary['total_portfolio_ecl']:,.0f}"
    )

    c2.metric(
        "Coverage Ratio",
        f"{ecl_summary['portfolio_coverage_ratio']}%"
    )

    c3.metric(
        "STAGE 3 ECL %",
        f"{ecl_summary['stage3_ecl_concentration']}%"
    )

    c4.metric(
        "Reserve Concentration",
        f"{ecl_summary['largest_reserve_concentration']}%"
    )

    c5.metric(
        "Reserve Risk",
        ecl_summary["concentration_risk"]
    )

    _narrative(
        f"""
        Portfolio ECL of <b>${ecl_summary['total_portfolio_ecl']:,.0f}</b> is the reserve view
        for IFRS 9 oversight. Reserve risk is <b>{ecl_summary['concentration_risk']}</b>
        because the largest borrower contributes <b>{ecl_summary['largest_reserve_concentration']}%</b>
        of total reserves; the key executive action is to monitor STAGE 3 concentration and
        reserve stress sensitivity.
        """,
        variant="default",
        label="◈ Reserve Adequacy Context"
    )

    # =============================================================================
    # IFRS9 STAGE MIGRATION DASHBOARD
    # =============================================================================

    st.divider()

    _section("🔄", "IFRS 9 Stage Migration Dashboard", "MIGRATION")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Accounts",
        migration_summary["total_accounts"]
    )

    c2.metric(
        "Deterioration",
        migration_summary["deterioration_accounts"]
    )

    c3.metric(
        "Recovery",
        migration_summary["recovery_accounts"]
    )

    c4.metric(
        "Stable",
        migration_summary["stable_accounts"]
    )

    c5.metric(
        "Stage Health",
        migration_results[
            "portfolio_stage_health"
        ]
    )

    # =============================================================================
    # IFRS9 TRANSITION MATRIX
    # =============================================================================

    st.divider()

    _section("📐", "IFRS 9 Transition Matrix", "STAGE FLOW")

    st.dataframe(
        transition_matrix,
        width="stretch"
    )

    # =============================================================================
    # ECL DISTRIBUTION ANALYTICS
    # =============================================================================

    st.divider()

    _section("📊", "Expected Credit Loss Analytics", "ECL MIX")

    stage_ecl = pd.DataFrame(

        list(
            ecl_summary[
                "stage_ecl_distribution"
            ].items()
        ),

        columns=[
            "Stage",
            "Contribution"
        ]
    )
    stage_ecl["Stage"] = (
        stage_ecl["Stage"]
        .astype(str)
        .str.replace("_", " ", regex=False)
        .str.upper()
    )

    fig = px.pie(
        stage_ecl,
        names="Stage",
        values="Contribution",
        title="Stage Contribution to Portfolio ECL",
        color="Stage",
        color_discrete_map=STAGE_COLORMAP,
        hole=0.42
    )

    _apply_layout(fig)
    fig.update_traces(
        textfont=dict(family="IBM Plex Mono", size=10),
        marker_line_color="#060f23",
        marker_line_width=2
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================
    # RESERVE STRESS DASHBOARD
    # =============================================================================

    st.divider()

    _section("🧪", "Reserve Stress Testing", "SEVERE RECESSION")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Reserve Growth %",
        stress_summary[
            "portfolio_reserve_growth_pct"
        ]
    )

    c2.metric(
        "Capital Grade",
        stress_summary[
            "capital_stress_grade"
        ]
    )

    c3.metric(
        "Capital Warning",
        stress_summary[
            "capital_warning"
        ]
    )

    c4.metric(
        "Concentration Risk",
        stress_summary[
            "concentration_risk"
        ]
    )

    # =============================================================================
    # SCENARIO COMPARISON
    # =============================================================================

    st.divider()

    _section("🔬", "Macro Scenario Comparison", "ALL SCENARIOS")

    st.dataframe(
        scenario_comparison,
        width="stretch"
    )

    fig = px.bar(
        scenario_comparison,
        x="scenario",
        y="stressed_portfolio_ecl",
        title="Portfolio ECL Under Stress Scenarios",
        color="scenario",
        color_discrete_sequence=PLOTLY_COLORS
    )

    _apply_layout(fig)
    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================
    # STAGE STRESS IMPACT
    # =============================================================================

    if stage_stress is not None:

        st.divider()

        _section("⚡", "Stage-Level Stress Impact", "IFRS 9 STAGE ΔECL")

        stage_stress = stage_stress.copy()
        stage_stress["stage"] = (
            stage_stress["stage"]
            .astype(str)
            .str.replace("_", " ", regex=False)
            .str.upper()
        )

        st.dataframe(
            stage_stress,
            width="stretch"
        )

        fig = px.bar(
            stage_stress,
            x="stage",
            y="stage_stressed_ecl",
            title="Stressed ECL by IFRS 9 Stage",
            color="stage",
            color_discrete_map=STAGE_COLORMAP
        )

        _apply_layout(fig)
        fig.update_traces(marker_line_width=0)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # =============================================================================
    # TOP RESERVE EXPOSURES
    # =============================================================================

    st.divider()

    _section("🔴", "Top Reserve Exposures", "HIGH EXPOSURE")

    st.dataframe(
        top_ecl,
        width="stretch"
    )

    # =============================================================================
    # TOP STRESSED BORROWERS
    # =============================================================================

    st.divider()

    _section("⚠️", "Top Stressed Borrowers", "STRESS RANKING")

    top_stressed = stress_df.nlargest(
        20,
        "stressed_ecl"
    )

    st.dataframe(
        top_stressed[
            [
                "borrower_id",
                "baseline_ecl",
                "stressed_ecl",
                "reserve_inflation_pct",
                "capital_impact",
                "stress_grade"
            ]
        ],
        width="stretch"
    )

    # =============================================================================
    # STAGE DISTRIBUTION
    # =============================================================================

    st.divider()

    _section("🥧", "IFRS 9 Stage Distribution", "STAGE MIX")

    stage_counts = (
        portfolio["current_stage"]
        .value_counts()
        .reset_index()
    )

    stage_counts.columns = [
        "Stage",
        "Count"
    ]
    stage_counts["Stage"] = (
        stage_counts["Stage"]
        .astype(str)
        .str.replace("_", " ", regex=False)
        .str.upper()
    )

    fig = px.pie(
        stage_counts,
        names="Stage",
        values="Count",
        title="Portfolio IFRS 9 Stage Mix",
        color="Stage",
        color_discrete_map=STAGE_COLORMAP,
        hole=0.42
    )

    _apply_layout(fig)
    fig.update_traces(
        textfont=dict(family="IBM Plex Mono", size=10),
        marker_line_color="#060f23",
        marker_line_width=2
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =============================================================================
    # EXECUTIVE NARRATIVE TERMINAL
    # =============================================================================

    st.divider()

    _section("📋", "Executive Provisioning Intelligence", "CRO BRIEF")

    _narrative(
        ecl_summary["executive_narrative"],
        variant="default",
        label="◈ ECL Portfolio Intelligence"
    )

    _narrative(
        stress_summary["executive_narrative"],
        variant="warn",
        label="⚠ Reserve Stress Intelligence"
    )

    # =============================================================================
    # PROVISIONING DATASET
    # =============================================================================

    st.divider()

    _section("🗄️", "Provisioning Analytics Dataset", "ECL RECORDS")

    st.dataframe(
        ecl_df.head(1000),
        width="stretch"
    )

    # ==========================================================
    # KRONOS FOOTER
    # ==========================================================

    st.divider()

    st.markdown(
        """
        <div class="kronos-footer">
            <span class="kronos-footer-text">KRONOS Enterprise Risk Platform · IFRS 9 Provisioning & ECL Analytics Division</span>
            <div class="kronos-footer-tags">
                <span class="kronos-tag">IFRS 9</span>
                <span class="kronos-tag blue">ECL Engine</span>
                <span class="kronos-tag green">Stage Migration</span>
                <span class="kronos-tag amber">Reserve Simulator</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # END OF DASHBOARD
    # ==========================================================

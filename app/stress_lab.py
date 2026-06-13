# =============================================================================
# KRONOS — STRESS TESTING LAB
# File: app/stress_lab.py
# =============================================================================

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
# STRESS ENGINE
# =============================================================================

from src.stress_testing.stress_engine import (
    run_stress_pipeline
)

# =============================================================================
# MACRO SHOCK ENGINE
# =============================================================================

from src.stress_testing.macro_shock import (
    run_macro_pipeline
)

# =============================================================================
# VAR ENGINE
# =============================================================================

from src.stress_testing.var_engine import (
    run_var_analysis
)

# =============================================================================
# CVAR ENGINE
# =============================================================================

from src.stress_testing.cvar_engine import (
    run_cvar_analysis
)

# =============================================================================
# CAPITAL IMPACT ENGINE
# =============================================================================

from src.stress_testing.capital_impact import (
    run_capital_impact_analysis
)

from src.shared.cache_manager import timed_cache

cached_run_stress_pipeline = timed_cache()(run_stress_pipeline)
cached_run_macro_pipeline = timed_cache()(run_macro_pipeline)
cached_run_var_analysis = timed_cache()(run_var_analysis)
cached_run_cvar_analysis = timed_cache()(run_cvar_analysis)
cached_run_capital_impact_analysis = timed_cache()(run_capital_impact_analysis)

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
    --gold:       #fbbf24;
    --text-prime: #e2e8f0;
    --text-muted: #94a3b8;
    --text-dim:   #64748b;
    --border:     rgba(148,163,184,0.12);
    --border-hi:  rgba(148,163,184,0.25);
    --glow-blue:  rgba(59,130,246,0.15);
    --glow-green: rgba(16,185,129,0.12);
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
    border-top: 3px solid var(--sapphire);
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
    width: 400px; height: 100%;
    background: radial-gradient(ellipse at top right, var(--glow-blue), transparent 70%);
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
    color: var(--sapphire);
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
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.3);
    color: var(--sapphire);
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
    background: linear-gradient(90deg, var(--sapphire), transparent);
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

/* ── SELECTBOX CONTROL ───────────────────────────────────────── */
.stSelectbox > div > div {
    background: var(--navy-800) !important;
    border: 1px solid var(--border-hi) !important;
    border-radius: 4px !important;
    color: var(--text-prime) !important;
}
.stSelectbox label {
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
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

/* ── ALERT / INFO / WARNING / SUCCESS BOXES ──────────────────── */
.stAlert {
    border-radius: 4px !important;
    border-left-width: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.7 !important;
}
div[data-testid="stAlert"][data-baseweb="notification"] {
    background: var(--navy-800) !important;
}

/* info → sapphire */
div[class*="stAlert"] > div[class*="alert-info"] {
    background: rgba(59,130,246,0.08) !important;
    border-left-color: var(--sapphire) !important;
    color: var(--slate-200) !important;
}
/* warning → amber */
div[class*="stAlert"] > div[class*="alert-warning"] {
    background: rgba(245,158,11,0.08) !important;
    border-left-color: var(--amber) !important;
    color: var(--slate-200) !important;
}
/* success → emerald */
div[class*="stAlert"] > div[class*="alert-success"] {
    background: rgba(16,185,129,0.08) !important;
    border-left-color: var(--emerald) !important;
    color: var(--slate-200) !important;
}

/* ── DIVIDER ─────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 2rem 0 !important;
}

/* ── PLOTLY CHARTS ───────────────────────────────────────────── */
.js-plotly-plot .plotly {
    border-radius: 4px !important;
}

/* ── NARRATIVE BLOCK ─────────────────────────────────────────── */
.kronos-narrative {
    background: var(--navy-800);
    border: 1px solid var(--border);
    border-left: 3px solid var(--sapphire);
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
    color: var(--sapphire);
    margin-bottom: 0.75rem;
    display: block;
}
.kronos-narrative-warn .kronos-narrative-label { color: var(--amber); }
.kronos-narrative-critical .kronos-narrative-label { color: var(--crimson); }
.kronos-narrative-success .kronos-narrative-label { color: var(--emerald); }

/* ── RECOMMENDATION BULLETS ──────────────────────────────────── */
.kronos-rec-item {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    padding: 0.6rem 0.85rem;
    background: var(--navy-800);
    border: 1px solid var(--border);
    border-left: 3px solid var(--amber);
    border-radius: 4px;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    color: var(--slate-200);
    font-family: 'IBM Plex Mono', monospace;
}
.kronos-rec-dot {
    width: 6px; height: 6px;
    background: var(--amber);
    border-radius: 50%;
    margin-top: 0.35rem;
    flex-shrink: 0;
}

/* ── STATUS PILL ─────────────────────────────────────────────── */
.kronos-pill {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 2px;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: 'IBM Plex Mono', monospace;
}
.pill-critical { background: rgba(239,68,68,0.15); color: var(--crimson); border: 1px solid rgba(239,68,68,0.3); }
.pill-high     { background: rgba(245,158,11,0.15); color: var(--amber);   border: 1px solid rgba(245,158,11,0.3); }
.pill-moderate { background: rgba(59,130,246,0.15);  color: var(--sapphire); border: 1px solid rgba(59,130,246,0.3); }
.pill-low      { background: rgba(16,185,129,0.15); color: var(--emerald); border: 1px solid rgba(16,185,129,0.3); }

/* ── COMMAND CENTER BANNER ───────────────────────────────────── */
.command-center {
    background: linear-gradient(135deg, var(--navy-800), var(--navy-700));
    border: 1px solid var(--border-hi);
    border-top: 3px solid var(--gold);
    border-radius: 4px;
    padding: 1.5rem 2rem;
    margin: 1rem 0 1.5rem;
}
.command-center-title {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--gold);
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 0.25rem;
}
.command-center-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-family: 'IBM Plex Mono', monospace;
}

/* ── SCENARIO CONTROL ────────────────────────────────────────── */
.scenario-control-wrapper {
    background: var(--navy-800);
    border: 1px solid var(--border-hi);
    border-radius: 4px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
}
.scenario-label {
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 0.35rem;
}

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
    "#3b82f6", "#10b981", "#f59e0b",
    "#ef4444", "#8b5cf6", "#06b6d4",
    "#f97316", "#84cc16", "#ec4899"
]

SEVERITY_COLORMAP = {
    "LOW":      "#10b981",
    "MODERATE": "#3b82f6",
    "HIGH":     "#f59e0b",
    "CRITICAL": "#ef4444",
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


# =============================================================================
# MAIN RENDER
# =============================================================================

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
                <span>KRONOS</span> Stress Testing Lab
            </div>
            <div class="kronos-banner-sub">
                Enterprise Credit Risk Intelligence Platform · Stress Analytics Division
            </div>
            <div class="kronos-banner-tags">
                <span class="kronos-tag">Basel III / IV</span>
                <span class="kronos-tag">IFRS 9</span>
                <span class="kronos-tag green">VaR / CVaR</span>
                <span class="kronos-tag green">Capital Adequacy</span>
                <span class="kronos-tag amber">Macro Shock</span>
                <span class="kronos-tag amber">Scenario Analysis</span>
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
        "loan_amount",
        "pd_score",
        "risk_migration_score",
    }
    missing_columns = sorted(required_columns - set(portfolio.columns))
    if missing_columns:
        st.warning(
            "Portfolio data missing required columns: "
            + ", ".join(missing_columns)
        )
        return

    # ==========================================================
    # NUMERIC CLEANUP
    # ==========================================================

    numeric_cols = [

        "pd_score",

        "lgd",

        "ead",

        "loan_amount",

        "early_warning_score",

        "risk_migration_score",
    ]

    for col in numeric_cols:

        if col in portfolio.columns:

            portfolio[col] = pd.to_numeric(
                portfolio[col],
                errors="coerce"
            )

    portfolio = portfolio.fillna(0)

    # ==========================================================
    # SCENARIO CONTROL CENTER
    # ==========================================================

    st.markdown(
        """
        <div class="scenario-control-wrapper">
            <div class="scenario-label">▸ Scenario Control Center — Select Stress Environment</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    _section("🎛️", "Scenario Control Center", "ACTIVE")

    scenario = st.selectbox(
        "Stress Scenario",
        [

            "BASELINE",

            "MILD RECESSION",

            "SEVERE RECESSION",

            "FINANCIAL CRISIS",
        ]
    )

    # ==========================================================
    # RUN STRESS ENGINE
    # ==========================================================

    stress_results = (
        cached_run_stress_pipeline(
            portfolio,
            scenario
        )
    )

    stressed_df = (
        stress_results[
            "portfolio_results"
        ]
    )

    stress_summary = (
        stress_results[
            "summary"
        ]
    )

    # ==========================================================
    # RUN MACRO ENGINE
    # ==========================================================

    macro_results = (
        cached_run_macro_pipeline(
            portfolio,
            scenario
        )
    )

    macro_df = (
        macro_results[
            "portfolio_results"
        ]
    )

    macro_summary = (
        macro_results[
            "summary"
        ]
    )

    # ==========================================================
    # RUN VAR ENGINE
    # ==========================================================

    var_results = (
        cached_run_var_analysis(
            portfolio
        )
    )

    # ==========================================================
    # RUN CVAR ENGINE
    # ==========================================================

    cvar_results = (
        cached_run_cvar_analysis(
            portfolio
        )
    )

    # ==========================================================
    # CAPITAL IMPACT ENGINE
    # ==========================================================

    stressed_losses = (
        stress_summary[
            "stressed_portfolio_loss"
        ]
    )

    capital_results = (
        cached_run_capital_impact_analysis(
            baseline_capital=750000000,
            risk_weighted_assets=5000000000,
            stressed_losses=stressed_losses,
        )
    )

    baseline_loss = stress_summary["baseline_portfolio_loss"]
    stressed_loss = stress_summary["stressed_portfolio_loss"]
    deterioration_pct = stress_summary["portfolio_loss_deterioration_pct"]
    avg_stressed_pd = stress_summary["average_stressed_pd"]
    stress_grade = stress_summary["stress_grade"]
    stress_concentration = stress_summary["stress_concentration"]
    resilience_score = capital_results["capital_resilience_score"]

    comparison_rows = []
    scenario_list = [
        "BASELINE",
        "MILD RECESSION",
        "SEVERE RECESSION",
        "FINANCIAL CRISIS",
    ]

    for stress_scenario in scenario_list:
        scenario_results = cached_run_stress_pipeline(
            portfolio,
            stress_scenario
        )
        scenario_summary = scenario_results["summary"]
        comparison_rows.append(
            {
                "Scenario": stress_scenario,
                "Stressed Loss": round(
                    scenario_summary["stressed_portfolio_loss"],
                    2
                ),
                "Average PD": round(
                    scenario_summary["average_stressed_pd"] * 100,
                    2
                ),
                "Deterioration %": round(
                    scenario_summary["portfolio_loss_deterioration_pct"],
                    2
                ),
                "Stress Grade": scenario_summary["stress_grade"],
                "Concentration %": round(
                    scenario_summary["stress_concentration"],
                    2
                ),
            }
        )

    comparison_df = pd.DataFrame(comparison_rows)
    worst_case = comparison_df.loc[
        comparison_df["Stressed Loss"].idxmax()
    ]

    enterprise_risk_score = round(
        (deterioration_pct * 0.35)
        + (stress_concentration * 0.20)
        + (macro_summary["systemic_stress_score"] * 0.25)
        + ((100 - resilience_score) * 0.20),
        2
    )
    enterprise_risk_score = min(enterprise_risk_score, 100)

    if enterprise_risk_score >= 80:
        enterprise_status = "CRITICAL RISK"
    elif enterprise_risk_score >= 60:
        enterprise_status = "HIGH RISK"
    elif enterprise_risk_score >= 40:
        enterprise_status = "MODERATE RISK"
    else:
        enterprise_status = "LOW RISK"

    executive_recommendations = []
    if deterioration_pct > 100:
        executive_recommendations.append("Increase credit provisioning reserves.")
    if stress_concentration > 25:
        executive_recommendations.append("Reduce portfolio concentration risk.")
    if capital_results["stressed_capital_ratio"] < 12:
        executive_recommendations.append("Review capital adequacy planning.")
    if enterprise_risk_score > 60:
        executive_recommendations.append("Escalate portfolio review to CRO.")
    if len(executive_recommendations) == 0:
        executive_recommendations.append("Portfolio remains resilient under current scenario.")

    # ==========================================================
    # EXECUTIVE STRESS CONCLUSION
    # ==========================================================

    st.divider()

    _section("📝", "Executive Scenario Narrative", "WORST CASE")

    _narrative(
        f"""
        <b>Worst Case Scenario:</b> {worst_case['Scenario']}<br>
        <b>Expected Portfolio Loss:</b> ${worst_case['Stressed Loss']:,.0f}<br>
        <b>Average Stressed PD:</b> {worst_case['Average PD']:.2f}%<br>
        <b>Portfolio Deterioration:</b> {worst_case['Deterioration %']:.2f}%<br>
        <b>Stress Grade:</b> {worst_case['Stress Grade']}<br>
        <b>Stress Concentration:</b> {worst_case['Concentration %']:.2f}%<br><br>
        Conclusion first: management should prioritize capital preservation, provisioning,
        and risk mitigation planning before reviewing detailed scenario analytics below.
        """,
        variant="warn",
        label="⚠ Worst Case Scenario Alert"
    )

    st.markdown(
        """
        <div class="command-center">
            <div class="command-center-title">▶ Executive Stress Command Center</div>
            <div class="command-center-sub">Board-Level Risk Intelligence · Enterprise Risk Score · CRO KPI Panel</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    _section("🏛️", "CRO KPI Panel", "LIVE")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Enterprise Risk", f"{enterprise_risk_score:.2f}")
    c2.metric("Risk Status", enterprise_status)
    c3.metric("Stress Grade", stress_grade)
    c4.metric("Macro Regime", macro_summary["macro_regime"])
    c5.metric("Capital Status", capital_results["capital_status"])

    _section("✅", "Executive Recommendations", "ACTION ITEMS")

    for rec in executive_recommendations:
        st.markdown(
            f'<div class="kronos-rec-item"><div class="kronos-rec-dot"></div>{rec}</div>',
            unsafe_allow_html=True
        )

    # ==========================================================
    # EXECUTIVE STRESS DASHBOARD
    # ==========================================================

    st.divider()

    _section("📊", "Executive Stress Dashboard", scenario)

    baseline_loss = (
        stress_summary[
            "baseline_portfolio_loss"
        ]
    )

    stressed_loss = (
        stress_summary[
            "stressed_portfolio_loss"
        ]
    )

    deterioration_pct = (
        stress_summary[
            "portfolio_loss_deterioration_pct"
        ]
    )

    avg_stressed_pd = (
        stress_summary[
            "average_stressed_pd"
        ]
    )

    stress_grade = (
        stress_summary[
            "stress_grade"
        ]
    )

    stress_concentration = (
        stress_summary[
            "stress_concentration"
        ]
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Baseline Loss",
        f"${baseline_loss:,.0f}"
    )

    c2.metric(
        "Stressed Loss",
        f"${stressed_loss:,.0f}"
    )

    c3.metric(
        "Deterioration %",
        f"{deterioration_pct:.2f}%"
    )

    c4.metric(
        "Avg Stressed PD",
        f"{avg_stressed_pd:.2%}"
    )

    c5.metric(
        "Stress Grade",
        stress_grade
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Stress Concentration",
        f"{stress_concentration:.2f}%"
    )

    c2.metric(
        "Largest Exposure",
        f"${stress_summary['largest_stressed_exposure']:,.0f}"
    )

    c3.metric(
        "Scenario",
        scenario
    )

    # ==========================================================
    # CAPITAL ADEQUACY DASHBOARD
    # ==========================================================

    st.divider()

    _section("🏦", "Capital Adequacy Dashboard", "REGULATORY")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Baseline Ratio",
        f"{capital_results['baseline_capital_ratio']:.2f}%"
    )

    c2.metric(
        "Stressed Ratio",
        f"{capital_results['stressed_capital_ratio']:.2f}%"
    )

    c3.metric(
        "Buffer Erosion",
        f"{capital_results['capital_buffer_erosion_pct']:.2f}%"
    )

    c4.metric(
        "Resilience Score",
        f"{capital_results['capital_resilience_score']:.2f}"
    )

    c5.metric(
        "Capital Remaining",
        f"{capital_results['capital_remaining_pct']:.2f}%"
    )

    # ==========================================================
    # MACRO SHOCK DASHBOARD
    # ==========================================================

    st.divider()

    _section("🌐", "Systemic Macro Shock Dashboard", "MACRO")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Stress Score",
        macro_summary[
            "systemic_stress_score"
        ]
    )

    c2.metric(
        "Macro Regime",
        macro_summary[
            "macro_regime"
        ]
    )

    c3.metric(
        "Sensitivity %",
        f"{macro_summary['portfolio_sensitivity_pct']:.2f}%"
    )

    c4.metric(
        "Largest Exposure",
        f"${macro_summary['largest_stressed_exposure']:,.0f}"
    )

    c5.metric(
        "Concentration %",
        f"{macro_summary['stress_concentration']:.2f}%"
    )

    # ==========================================================
    # VAR & CVAR ANALYTICS DASHBOARD
    # ==========================================================

    st.divider()

    _section("📉", "VaR & CVaR Analytics Dashboard", "TAIL RISK")

    var95 = (
        var_results["var_results"]["95%"]["var_percentage"]
    )

    var99 = (
        var_results["var_results"]["99%"]["var_percentage"]
    )

    cvar95 = (
        cvar_results["cvar_results"]["95%"]["cvar_percentage"]
    )

    cvar99 = (
        cvar_results["cvar_results"]["99%"]["cvar_percentage"]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "95% VaR",
        f"{var95:.2f}%"
    )

    c2.metric(
        "99% VaR",
        f"{var99:.2f}%"
    )

    c3.metric(
        "95% CVaR",
        f"{cvar95:.2f}%"
    )

    c4.metric(
        "99% CVaR",
        f"{cvar99:.2f}%"
    )

    # ==========================================================
    # TAIL RISK ASSESSMENT
    # ==========================================================

    tail_ratio = (
        cvar99 / var99
        if var99 > 0
        else 0
    )

    if tail_ratio >= 1.50:

        tail_risk = "CRITICAL"

    elif tail_ratio >= 1.30:

        tail_risk = "HIGH"

    elif tail_ratio >= 1.10:

        tail_risk = "MODERATE"

    else:

        tail_risk = "LOW"

    c1, c2 = st.columns(2)

    c1.metric(
        "Tail Severity Ratio",
        f"{tail_ratio:.2f}"
    )

    c2.metric(
        "Tail Risk Level",
        tail_risk
    )

    # ==========================================================
    # LOSS DISTRIBUTION
    # ==========================================================

    st.divider()

    _section("📈", "Loss Distribution Analysis", "ECL MODELLING")

    loss_series = (
        portfolio["ead"]
        * portfolio["pd_score"]
        * portfolio["lgd"]
    )

    fig = px.histogram(
        loss_series,
        nbins=50,
        title="Portfolio Loss Distribution",
        color_discrete_sequence=[PLOTLY_COLORS[0]]
    )
    _apply_layout(fig)
    fig.update_traces(marker_line_color="rgba(59,130,246,0.3)", marker_line_width=0.5)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # VAR / CVAR VISUALIZATION
    # ==========================================================

    st.divider()

    _section("⚠️", "Tail Risk Visualization", "VAR vs CVAR")

    var_cvar_df = pd.DataFrame({

        "Confidence": [
            "95%",
            "99%"
        ],

        "VaR": [
            var95,
            var99
        ],

        "CVaR": [
            cvar95,
            cvar99
        ]
    })

    fig = px.bar(
        var_cvar_df,
        x="Confidence",
        y=["VaR", "CVaR"],
        barmode="group",
        title="VaR vs CVaR Comparison",
        color_discrete_sequence=[PLOTLY_COLORS[0], PLOTLY_COLORS[2]]
    )
    _apply_layout(fig)
    fig.update_traces(marker_line_width=0)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE RISK NARRATIVE
    # ==========================================================

    st.divider()

    _section("📋", "Executive Risk Narrative", "CRO BRIEF")

    _narrative(
        f"""
        <b>95% VaR:</b> {var95:.2f}%<br>
        <b>99% VaR:</b> {var99:.2f}%<br>
        <b>95% CVaR:</b> {cvar95:.2f}%<br>
        <b>99% CVaR:</b> {cvar99:.2f}%<br><br>
        <b>Tail Risk Classification:</b> {tail_risk}<br>
        <b>Portfolio Deterioration:</b> {deterioration_pct:.2f}%<br>
        <b>Stressed Portfolio Loss:</b> ${stressed_loss:,.0f}
        """,
        variant="default",
        label="Tail Risk Intelligence"
    )

    # ==========================================================
    # SCENARIO COMPARISON & BENCHMARK DASHBOARD
    # ==========================================================

    st.divider()

    _section("🔬", "Scenario Comparison & Benchmark Dashboard", "ALL SCENARIOS")

    comparison_rows = []

    scenario_list = [

        "BASELINE",

        "MILD RECESSION",

        "SEVERE RECESSION",

        "FINANCIAL CRISIS",
    ]

    for stress_scenario in scenario_list:

        scenario_results = (
            cached_run_stress_pipeline(
                portfolio,
                stress_scenario
            )
        )

        scenario_summary = (
            scenario_results[
                "summary"
            ]
        )

        comparison_rows.append(

            {

                "Scenario":
                    stress_scenario,

                "Stressed Loss":
                    round(
                        scenario_summary[
                            "stressed_portfolio_loss"
                        ],
                        2
                    ),

                "Average PD":
                    round(
                        scenario_summary[
                            "average_stressed_pd"
                        ] * 100,
                        2
                    ),

                "Deterioration %":
                    round(
                        scenario_summary[
                            "portfolio_loss_deterioration_pct"
                        ],
                        2
                    ),

                "Stress Grade":
                    scenario_summary[
                        "stress_grade"
                    ],

                "Concentration %":
                    round(
                        scenario_summary[
                            "stress_concentration"
                        ],
                        2
                    ),
            }
        )

    comparison_df = pd.DataFrame(
        comparison_rows
    )

    # ==========================================================
    # SCENARIO TABLE
    # ==========================================================

    st.dataframe(
        comparison_df,
        width="stretch"
    )

    # ==========================================================
    # LOSS COMPARISON
    # ==========================================================

    st.divider()

    _section("💰", "Portfolio Loss Comparison", "CROSS-SCENARIO")

    fig = px.bar(

        comparison_df,

        x="Scenario",

        y="Stressed Loss",

        text="Stressed Loss",

        title="Portfolio Loss Across Stress Scenarios",

        color="Scenario",

        color_discrete_sequence=PLOTLY_COLORS
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )
    _apply_layout(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # AVERAGE PD COMPARISON
    # ==========================================================

    st.divider()

    _section("📐", "Average PD Comparison", "PROBABILITY")

    fig = px.line(

        comparison_df,

        x="Scenario",

        y="Average PD",

        markers=True,

        title="Average Stressed PD Across Scenarios",

        color_discrete_sequence=[PLOTLY_COLORS[2]]
    )

    fig.update_traces(
        line_width=2,
        marker_size=8,
        marker_color=PLOTLY_COLORS[2],
        marker_line_color=PLOTLY_COLORS[0],
        marker_line_width=1.5
    )
    _apply_layout(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # DETERIORATION COMPARISON
    # ==========================================================

    st.divider()

    _section("📉", "Portfolio Deterioration Comparison", "DELTA IMPACT")

    fig = px.bar(

        comparison_df,

        x="Scenario",

        y="Deterioration %",

        text="Deterioration %",

        title="Portfolio Deterioration Across Scenarios",

        color="Scenario",

        color_discrete_sequence=PLOTLY_COLORS
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )
    _apply_layout(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # STRESS CONCENTRATION
    # ==========================================================

    st.divider()

    _section("🎯", "Stress Concentration Comparison", "CONCENTRATION")

    fig = px.bar(

        comparison_df,

        x="Scenario",

        y="Concentration %",

        text="Concentration %",

        title="Stress Concentration Across Scenarios",

        color="Scenario",

        color_discrete_sequence=PLOTLY_COLORS
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )
    _apply_layout(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # STRESS GRADE BENCHMARK
    # ==========================================================

    st.divider()

    _section("🏅", "Stress Grade Benchmark", "GRADE TABLE")

    st.dataframe(

        comparison_df[
            [
                "Scenario",
                "Stress Grade"
            ]
        ],

        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE NARRATIVE
    # ==========================================================

    st.divider()

    _section("📝", "Executive Scenario Narrative", "WORST CASE")

    worst_case = comparison_df.loc[
        comparison_df[
            "Stressed Loss"
        ].idxmax()
    ]

    _narrative(
        f"""
        <b>Worst Case Scenario:</b> {worst_case['Scenario']}<br>
        <b>Expected Portfolio Loss:</b> ${worst_case['Stressed Loss']:,.0f}<br>
        <b>Average Stressed PD:</b> {worst_case['Average PD']:.2f}%<br>
        <b>Portfolio Deterioration:</b> {worst_case['Deterioration %']:.2f}%<br>
        <b>Stress Grade:</b> {worst_case['Stress Grade']}<br>
        <b>Stress Concentration:</b> {worst_case['Concentration %']:.2f}%<br><br>
        Management should prioritize capital preservation, provisioning, and risk mitigation planning under this scenario.
        """,
        variant="warn",
        label="⚠ Worst Case Scenario Alert"
    )

    # ==========================================================
    # CAPITAL STRESS VISUALIZATION DASHBOARD
    # ==========================================================

    st.divider()

    _section("🔋", "Capital Stress Visualization Dashboard", "CAPITAL")

    baseline_capital = (
        capital_results[
            "baseline_capital"
        ]
    )

    stressed_capital = (
        capital_results[
            "stressed_capital"
        ]
    )

    capital_erosion = (
        capital_results[
            "capital_buffer_erosion_pct"
        ]
    )

    resilience_score = (
        capital_results[
            "capital_resilience_score"
        ]
    )

    capital_remaining = (
        capital_results[
            "capital_remaining_pct"
        ]
    )

    # ==========================================================
    # CAPITAL POSITION METRICS
    # ==========================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Baseline Capital",
        f"${baseline_capital:,.0f}"
    )

    c2.metric(
        "Stressed Capital",
        f"${stressed_capital:,.0f}"
    )

    c3.metric(
        "Capital Erosion",
        f"{capital_erosion:.2f}%"
    )

    c4.metric(
        "Resilience Score",
        f"{resilience_score:.2f}"
    )

    # ==========================================================
    # CAPITAL COMPARISON CHART
    # ==========================================================

    capital_df = pd.DataFrame({

        "Category": [

            "Baseline Capital",

            "Stressed Capital",
        ],

        "Amount": [

            baseline_capital,

            stressed_capital,
        ]
    })

    fig = px.bar(

        capital_df,

        x="Category",

        y="Amount",

        text="Amount",

        title="Capital Position Comparison",

        color="Category",

        color_discrete_sequence=[PLOTLY_COLORS[0], PLOTLY_COLORS[3]]
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )
    _apply_layout(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # CAPITAL HEALTH GAUGE
    # ==========================================================

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=resilience_score,

            title={
                "text": "Capital Resilience Score",
                "font": {"family": "IBM Plex Sans", "color": "#e2e8f0", "size": 14}
            },

            number={"font": {"color": "#e2e8f0", "family": "IBM Plex Mono"}},

            gauge={
                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#475569",
                    "tickfont": {"color": "#64748b", "family": "IBM Plex Mono", "size": 10}
                },
                "bar": {"color": "#10b981", "thickness": 0.22},
                "bgcolor": "#0a1628",
                "bordercolor": "#1e3a5f",
                "borderwidth": 1,
                "steps": [
                    {"range": [0, 33],   "color": "rgba(239,68,68,0.15)"},
                    {"range": [33, 66],  "color": "rgba(245,158,11,0.12)"},
                    {"range": [66, 100], "color": "rgba(16,185,129,0.12)"},
                ],
                "threshold": {
                    "line": {"color": "#f59e0b", "width": 2},
                    "thickness": 0.75,
                    "value": 70
                }
            }
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(6,15,35,0)",
        plot_bgcolor="rgba(6,15,35,0)",
        font={"family": "IBM Plex Mono", "color": "#94a3b8"},
        margin=dict(l=24, r=24, t=48, b=24),
        height=300
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # CAPITAL ADEQUACY SUMMARY
    # ==========================================================

    st.divider()

    _section("📑", "Capital Adequacy Summary", "REGULATORY")

    summary_df = pd.DataFrame({

        "Metric": [

            "Capital Status",

            "Solvency Status",

            "Recovery Action",

            "Regulatory Status",

            "Capital Depletion Risk",
        ],

        "Value": [

            capital_results[
                "capital_status"
            ],

            capital_results[
                "solvency_status"
            ],

            capital_results[
                "recovery_action"
            ],

            capital_results[
                "regulatory_status"
            ],

            capital_results[
                "capital_depletion_risk"
            ],
        ]
    })

    st.dataframe(
        summary_df,
        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE CAPITAL NARRATIVE
    # ==========================================================

    st.divider()

    _section("✅", "Executive Capital Narrative", "CAPITAL BRIEF")

    _narrative(
        f"""
        <b>Capital Status:</b> {capital_results['capital_status']}<br>
        <b>Solvency Assessment:</b> {capital_results['solvency_status']}<br>
        <b>Regulatory Status:</b> {capital_results['regulatory_status']}<br>
        <b>Capital Remaining:</b> {capital_remaining:.2f}%<br>
        <b>Resilience Score:</b> {resilience_score:.2f}<br>
        <b>Recommended Action:</b> {capital_results['recovery_action']}
        """,
        variant="success",
        label="✓ Capital Position Assessment"
    )

    # ==========================================================
    # TOP STRESSED BORROWERS DASHBOARD
    # ==========================================================

    st.divider()

    _section("🔴", "Top Stressed Borrowers Dashboard", "HIGH EXPOSURE")

    top_stressed = (

        stressed_df

        .sort_values(
            by="stressed_ecl",
            ascending=False
        )

        .head(20)
    )

    display_cols = [

        "borrower_id",

        "stressed_pd",

        "stressed_lgd",

        "stressed_ead",

        "stressed_ecl",

        "loss_impact_pct",

        "stress_severity",
    ]

    available_cols = [

        col

        for col in display_cols

        if col in top_stressed.columns
    ]

    st.dataframe(

        top_stressed[
            available_cols
        ],

        width="stretch"
    )

    # ==========================================================
    # TOP STRESSED ECL
    # ==========================================================

    st.divider()

    _section("💥", "Top Stressed ECL Exposure", "TOP 10")

    fig = px.bar(

        top_stressed.head(10),

        x="borrower_id",

        y="stressed_ecl",

        color="stress_severity",

        title="Largest Stressed Credit Losses",

        color_discrete_map=SEVERITY_COLORMAP
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_width=0)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # STRESS SEVERITY BREAKDOWN
    # ==========================================================

    st.divider()

    _section("🟠", "Stress Severity Distribution", "SEVERITY MIX")

    severity_counts = (

        stressed_df[
            "stress_severity"
        ]

        .value_counts()

        .reset_index()
    )

    severity_counts.columns = [

        "Severity",

        "Count"
    ]

    fig = px.pie(

        severity_counts,

        names="Severity",

        values="Count",

        title="Portfolio Stress Severity Mix",

        color="Severity",

        color_discrete_map=SEVERITY_COLORMAP,

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

    # ==========================================================
    # STRESS WATCHLIST DISTRIBUTION
    # ==========================================================

    st.divider()

    _section("👁️", "Stress Watchlist Distribution", "DISTRESS CLASS")

    watchlist_counts = (

        stressed_df[
            "stress_watchlist"
        ]

        .value_counts()

        .reset_index()
    )

    watchlist_counts.columns = [

        "Watchlist",

        "Count"
    ]

    fig = px.bar(

        watchlist_counts,

        x="Watchlist",

        y="Count",

        text="Count",

        title="Borrower Distress Classification",

        color="Watchlist",

        color_discrete_sequence=PLOTLY_COLORS
    )

    fig.update_traces(
        textposition="outside",
        marker_line_width=0
    )
    _apply_layout(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # CONCENTRATION ANALYSIS
    # ==========================================================

    st.divider()

    _section("🎯", "Exposure Concentration Analysis", "CONCENTRATION")

    total_stressed_ecl = (
        stressed_df[
            "stressed_ecl"
        ].sum()
    )

    top10_ecl = (
        top_stressed
        .head(10)[
            "stressed_ecl"
        ]
        .sum()
    )

    if total_stressed_ecl > 0:

        concentration_ratio = round(
            (
                top10_ecl
                / total_stressed_ecl
            ) * 100,
            2
        )

    else:

        concentration_ratio = 0

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Total Stressed ECL",
        f"${total_stressed_ecl:,.0f}"
    )

    c2.metric(
        "Top 10 ECL",
        f"${top10_ecl:,.0f}"
    )

    c3.metric(
        "Concentration %",
        f"{concentration_ratio:.2f}%"
    )

    # ==========================================================
    # EXECUTIVE CONCENTRATION NARRATIVE
    # ==========================================================

    st.divider()

    _section("⚡", "Executive Concentration Narrative", "CONCENTRATION RISK")

    if concentration_ratio >= 40:

        concentration_risk = (
            "HIGH CONCENTRATION RISK"
        )

    elif concentration_ratio >= 25:

        concentration_risk = (
            "MODERATE CONCENTRATION RISK"
        )

    else:

        concentration_risk = (
            "LOW CONCENTRATION RISK"
        )

    _conc_variant = (
        "critical" if concentration_ratio >= 40
        else "warn" if concentration_ratio >= 25
        else "success"
    )

    _narrative(
        f"""
        Top 10 borrowers account for <b>{concentration_ratio:.2f}%</b> of stressed portfolio losses.<br><br>
        <b>Total Stressed Portfolio Loss:</b> ${total_stressed_ecl:,.0f}<br>
        <b>Largest Borrower Concentration:</b> ${top10_ecl:,.0f}<br>
        <b>Concentration Assessment:</b> {concentration_risk}<br><br>
        Management should monitor borrower clustering risk, sector concentration, and contagion vulnerability.
        """,
        variant=_conc_variant,
        label=f"◈ Concentration Intelligence — {concentration_risk}"
    )

    # ==========================================================
    # STRESS SCENARIO HEATMAPS
    # ==========================================================

    st.divider()

    _section("🗺️", "Stress Scenario Heatmaps", "ENTERPRISE")

    heatmap_df = comparison_df.copy()

    heatmap_df = heatmap_df.set_index(
        "Scenario"
    )

    heatmap_data = heatmap_df[
        [
            "Stressed Loss",
            "Average PD",
            "Deterioration %",
            "Concentration %"
        ]
    ]

    fig = px.imshow(

        heatmap_data,

        text_auto=".2f",

        aspect="auto",

        title="Enterprise Stress Heatmap",

        color_continuous_scale=[
            [0.0, "#0a1628"],
            [0.3, "#1e3a5f"],
            [0.6, "#d97706"],
            [1.0, "#dc2626"],
        ]
    )

    _apply_layout(fig)
    fig.update_traces(
        textfont=dict(family="IBM Plex Mono", size=10, color="#e2e8f0")
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # PORTFOLIO RISK MATRIX
    # ==========================================================

    st.divider()

    _section("🔷", "Portfolio Risk Matrix", "RISK SCATTER")

    risk_matrix = stressed_df.copy()

    risk_matrix["risk_size"] = (
        risk_matrix["stressed_ecl"]
    )

    fig = px.scatter(

        risk_matrix,

        x="stressed_pd",

        y="loss_impact_pct",

        size="risk_size",

        color="stress_severity",

        hover_data=[
            "borrower_id"
        ],

        title="Borrower Stress Risk Matrix",

        color_discrete_map=SEVERITY_COLORMAP
    )

    _apply_layout(fig)
    fig.update_traces(
        marker_line_width=0.5,
        marker_line_color="rgba(255,255,255,0.15)",
        marker_opacity=0.8
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # STRESSED PD VS ECL
    # ==========================================================

    st.divider()

    _section("🔵", "Stressed PD vs Stressed ECL", "PD-ECL")

    fig = px.scatter(

        stressed_df,

        x="stressed_pd",

        y="stressed_ecl",

        color="stress_severity",

        hover_data=[
            "borrower_id"
        ],

        title="PD-ECL Relationship",

        color_discrete_map=SEVERITY_COLORMAP
    )

    _apply_layout(fig)
    fig.update_traces(
        marker_size=5,
        marker_opacity=0.75,
        marker_line_width=0
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # LOSS IMPACT DISTRIBUTION
    # ==========================================================

    st.divider()

    _section("📊", "Loss Impact Distribution", "PORTFOLIO ΔL")

    fig = px.histogram(

        stressed_df,

        x="loss_impact_pct",

        nbins=40,

        title="Portfolio Deterioration Distribution",

        color_discrete_sequence=[PLOTLY_COLORS[2]]
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_width=0.5, marker_line_color="rgba(245,158,11,0.3)")

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # RISK QUADRANT ANALYSIS
    # ==========================================================

    st.divider()

    _section("🔳", "Risk Quadrant Analysis", "QUADRANT")

    avg_pd = (
        stressed_df["stressed_pd"]
        .mean()
    )

    avg_loss = (
        stressed_df["loss_impact_pct"]
        .mean()
    )

    fig = go.Figure()

    fig.add_trace(

        go.Scatter(

            x=stressed_df[
                "stressed_pd"
            ],

            y=stressed_df[
                "loss_impact_pct"
            ],

            mode="markers",

            text=stressed_df[
                "borrower_id"
            ],

            marker=dict(
                size=8,
                color="#3b82f6",
                opacity=0.72,
                line=dict(color="rgba(255,255,255,0.1)", width=0.5)
            )
        )
    )

    fig.add_vline(
        x=avg_pd,
        line_color="#f59e0b",
        line_dash="dot",
        line_width=1.2
    )

    fig.add_hline(
        y=avg_loss,
        line_color="#f59e0b",
        line_dash="dot",
        line_width=1.2
    )

    fig.update_layout(

        title={
            "text": "Portfolio Risk Quadrants",
            "font": {"family": "IBM Plex Sans", "color": "#e2e8f0", "size": 13},
            "x": 0, "xanchor": "left"
        },

        xaxis_title="Stressed PD",

        yaxis_title="Loss Impact %",

        **{k: v for k, v in PLOTLY_LAYOUT.items()
           if k not in ("title",)}
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE HEATMAP NARRATIVE
    # ==========================================================

    st.divider()

    _section("📋", "Executive Risk Matrix Narrative", "RISK BRIEF")

    high_risk_accounts = len(

        stressed_df[

            (
                stressed_df[
                    "stressed_pd"
                ] > avg_pd
            )

            &

            (
                stressed_df[
                    "loss_impact_pct"
                ] > avg_loss
            )
        ]
    )

    _narrative(
        f"""
        <b>Average Stressed PD:</b> {avg_pd:.4f}<br>
        <b>Average Loss Impact:</b> {avg_loss:.2f}%<br>
        <b>High-Risk Quadrant Accounts:</b> {high_risk_accounts:,}<br><br>
        These borrowers exhibit above-average probability of default and above-average portfolio deterioration impact.
        Management should prioritize monitoring, remediation, and exposure reduction for this segment.
        """,
        variant="default",
        label="◈ Risk Matrix Intelligence"
    )

    # ==========================================================
    # EXECUTIVE STRESS COMMAND CENTER
    # ==========================================================

    st.divider()

    st.markdown(
        """
        <div class="command-center">
            <div class="command-center-title">▶ Executive Stress Command Center</div>
            <div class="command-center-sub">Board-Level Risk Intelligence · Enterprise Risk Score · CRO KPI Panel</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # ENTERPRISE RISK SCORE
    # ==========================================================

    enterprise_risk_score = round(

        (
            deterioration_pct * 0.35
        )

        +

        (
            stress_concentration * 0.20
        )

        +

        (
            macro_summary[
                "systemic_stress_score"
            ] * 0.25
        )

        +

        (
            (100 - resilience_score)
            * 0.20
        ),

        2
    )

    enterprise_risk_score = min(
        enterprise_risk_score,
        100
    )

    # ==========================================================
    # ENTERPRISE RISK CLASSIFICATION
    # ==========================================================

    if enterprise_risk_score >= 80:

        enterprise_status = (
            "CRITICAL RISK"
        )

    elif enterprise_risk_score >= 60:

        enterprise_status = (
            "HIGH RISK"
        )

    elif enterprise_risk_score >= 40:

        enterprise_status = (
            "MODERATE RISK"
        )

    else:

        enterprise_status = (
            "LOW RISK"
        )

    # ==========================================================
    # CRO KPI PANEL
    # ==========================================================

    _section("🏛️", "CRO KPI Panel", "LIVE")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Enterprise Risk",
        f"{enterprise_risk_score:.2f}"
    )

    c2.metric(
        "Risk Status",
        enterprise_status
    )

    c3.metric(
        "Stress Grade",
        stress_grade
    )

    c4.metric(
        "Macro Regime",
        macro_summary[
            "macro_regime"
        ]
    )

    c5.metric(
        "Capital Status",
        capital_results[
            "capital_status"
        ]
    )

    # ==========================================================
    # ENTERPRISE RISK GAUGE
    # ==========================================================

    _gauge_color = (
        "#ef4444" if enterprise_risk_score >= 80
        else "#f59e0b" if enterprise_risk_score >= 60
        else "#3b82f6" if enterprise_risk_score >= 40
        else "#10b981"
    )

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=enterprise_risk_score,

            title={
                "text": "Enterprise Risk Score",
                "font": {"family": "IBM Plex Sans", "color": "#e2e8f0", "size": 14}
            },

            number={"font": {"color": "#e2e8f0", "family": "IBM Plex Mono", "size": 36}},

            gauge={

                "axis": {
                    "range": [0, 100],
                    "tickcolor": "#475569",
                    "tickfont": {"color": "#64748b", "family": "IBM Plex Mono", "size": 10}
                },

                "bar": {"color": _gauge_color, "thickness": 0.22},

                "bgcolor": "#0a1628",

                "bordercolor": "#1e3a5f",

                "borderwidth": 1,

                "steps": [
                    {"range": [0, 40],   "color": "rgba(16,185,129,0.1)"},
                    {"range": [40, 60],  "color": "rgba(59,130,246,0.1)"},
                    {"range": [60, 80],  "color": "rgba(245,158,11,0.12)"},
                    {"range": [80, 100], "color": "rgba(239,68,68,0.15)"},
                ],

                "threshold": {
                    "line": {"color": "#94a3b8", "width": 1.5},
                    "thickness": 0.75,
                    "value": enterprise_risk_score
                }
            }
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(6,15,35,0)",
        plot_bgcolor="rgba(6,15,35,0)",
        font={"family": "IBM Plex Mono", "color": "#94a3b8"},
        margin=dict(l=24, r=24, t=48, b=24),
        height=320
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # BOARD REPORT TABLE
    # ==========================================================

    st.divider()

    _section("📋", "Board-Level Risk Summary", "BOARD REPORT")

    board_report = pd.DataFrame({

        "Metric": [

            "Scenario",

            "Baseline Loss",

            "Stressed Loss",

            "Loss Deterioration",

            "Stress Grade",

            "Stress Concentration",

            "Systemic Stress Score",

            "Macro Regime",

            "Capital Ratio",

            "Capital Status",

            "Resilience Score",

            "Enterprise Risk Score",
        ],

        "Value": [

            scenario,

            round(
                baseline_loss,
                2
            ),

            round(
                stressed_loss,
                2
            ),

            f"{deterioration_pct:.2f}%",

            stress_grade,

            f"{stress_concentration:.2f}%",

            macro_summary[
                "systemic_stress_score"
            ],

            macro_summary[
                "macro_regime"
            ],

            f"{capital_results['stressed_capital_ratio']:.2f}%",

            capital_results[
                "capital_status"
            ],

            f"{resilience_score:.2f}",

            f"{enterprise_risk_score:.2f}",
        ]
    })

    st.dataframe(
        board_report,
        width="stretch"
    )

    # ==========================================================
    # ENTERPRISE RECOMMENDATIONS
    # ==========================================================

    st.divider()

    _section("✅", "Executive Recommendations", "ACTION ITEMS")

    recommendations = []

    if deterioration_pct > 100:

        recommendations.append(
            "Increase credit provisioning reserves."
        )

    if stress_concentration > 25:

        recommendations.append(
            "Reduce portfolio concentration risk."
        )

    if capital_results[
        "stressed_capital_ratio"
    ] < 12:

        recommendations.append(
            "Review capital adequacy planning."
        )

    if enterprise_risk_score > 60:

        recommendations.append(
            "Escalate portfolio review to CRO."
        )

    if len(recommendations) == 0:

        recommendations.append(
            "Portfolio remains resilient under current scenario."
        )

    for rec in recommendations:

        st.markdown(
            f'<div class="kronos-rec-item"><div class="kronos-rec-dot"></div>{rec}</div>',
            unsafe_allow_html=True
        )

    # ==========================================================
    # EXECUTIVE SUMMARY
    # ==========================================================

    st.divider()

    _section("🏆", "Executive Board Narrative", "FINAL SUMMARY")

    _narrative(
        f"""
        <b>Scenario Evaluated:</b> {scenario}<br>
        <b>Enterprise Risk Score:</b> {enterprise_risk_score:.2f}<br>
        <b>Risk Classification:</b> {enterprise_status}<br>
        <b>Portfolio Deterioration:</b> {deterioration_pct:.2f}%<br>
        <b>Stress Grade:</b> {stress_grade}<br>
        <b>Capital Position:</b> {capital_results['capital_status']}<br>
        <b>Macroeconomic Regime:</b> {macro_summary['macro_regime']}<br>
        <b>Stress Concentration:</b> {stress_concentration:.2f}%<br><br>
        The portfolio is currently classified as <b>{enterprise_status.lower()}</b> under the selected stress scenario.
        Management should use this analysis for capital planning, provisioning, risk appetite review,
        portfolio optimization, and regulatory stress-testing exercises.
        """,
        variant="success",
        label="✓ Executive Board Summary"
    )

    # ==========================================================
    # KRONOS FOOTER
    # ==========================================================

    st.divider()

    st.markdown(
        """
        <div class="kronos-footer">
            <span class="kronos-footer-text">KRONOS Enterprise Risk Platform · Stress Testing Division</span>
            <div class="kronos-footer-tags">
                <span class="kronos-tag">Basel III / IV</span>
                <span class="kronos-tag">IFRS 9</span>
                <span class="kronos-tag green">ECL Engine</span>
                <span class="kronos-tag amber">Portfolio Risk Intelligence</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # END OF DASHBOARD
    # ==========================================================

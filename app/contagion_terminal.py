# =============================================================================
# KRONOS — CONTAGION TERMINAL
# File: app/contagion_terminal.py
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
# CONTAGION ENGINE
# =============================================================================

from src.contagion.contagion_engine import (
    run_contagion_analysis
)

# =============================================================================
# NETWORK BUILDER
# =============================================================================

from src.contagion.network_builder import (
    run_network_analysis
)

# =============================================================================
# CASCADE SIMULATOR
# =============================================================================

from src.contagion.cascade_simulator import (
    run_cascade_simulation
)

# =============================================================================
# SYSTEMIC RISK ENGINE
# =============================================================================

from src.contagion.systemic_risk import (
    run_systemic_risk_analysis
)

from src.shared.cache_manager import timed_cache

from app.live_intelligence_components import (
    get_dashboard_live_context,
    macro_intelligence,
    market_intelligence,
    render_live_status_card,
    live_summary,
)

cached_run_contagion_analysis = timed_cache()(run_contagion_analysis)
cached_run_network_analysis = timed_cache()(run_network_analysis)
cached_run_cascade_simulation = timed_cache()(run_cascade_simulation)
cached_run_systemic_risk_analysis = timed_cache()(run_systemic_risk_analysis)

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
    --violet:     #8b5cf6;
    --text-prime: #e2e8f0;
    --text-muted: #94a3b8;
    --text-dim:   #64748b;
    --border:     rgba(148,163,184,0.12);
    --border-hi:  rgba(148,163,184,0.25);
    --glow-blue:  rgba(59,130,246,0.15);
    --glow-violet:rgba(139,92,246,0.12);
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
    border-top: 3px solid var(--violet);
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
    background: radial-gradient(ellipse at top right, var(--glow-violet), transparent 70%);
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
    color: var(--violet);
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
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.3);
    color: var(--violet);
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
    background: linear-gradient(90deg, var(--violet), transparent);
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

/* ── ALERT / INFO / WARNING / SUCCESS BOXES ──────────────────── */
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
    border-left: 3px solid var(--violet);
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
    color: var(--violet);
    margin-bottom: 0.75rem;
    display: block;
}
.kronos-narrative-warn .kronos-narrative-label     { color: var(--amber); }
.kronos-narrative-critical .kronos-narrative-label { color: var(--crimson); }
.kronos-narrative-success .kronos-narrative-label  { color: var(--emerald); }

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
    "#8b5cf6", "#3b82f6", "#10b981",
    "#f59e0b", "#ef4444", "#06b6d4",
    "#f97316", "#84cc16", "#ec4899"
]

SYSTEMIC_COLORMAP = {
    "LOW":      "#10b981",
    "MODERATE": "#3b82f6",
    "HIGH":     "#f59e0b",
    "CRITICAL": "#ef4444",
    "SYSTEMIC": "#8b5cf6",
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
                <span>KRONOS</span> Contagion Terminal
            </div>
            <div class="kronos-banner-sub">
                Enterprise Credit Risk Intelligence Platform · Contagion & Network Analytics Division
            </div>
            <div class="kronos-banner-tags">
                <span class="kronos-tag">Contagion Intelligence</span>
                <span class="kronos-tag blue">Network Analytics</span>
                <span class="kronos-tag amber">Cascade Simulation</span>
                <span class="kronos-tag red">Systemic Risk</span>
                <span class="kronos-tag green">Fragility Scoring</span>
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
        "behavioral_risk_score",
        "borrower_id",
        "ead",
        "early_warning_score",
        "industry",
        "pd_score",
        "region",
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

        "ead",

        "early_warning_score",

        "risk_migration_score",

        "behavioral_risk_score",
    ]

    for col in numeric_cols:

        if col in portfolio.columns:

            portfolio[col] = pd.to_numeric(
                portfolio[col],
                errors="coerce"
            )

    portfolio = portfolio.fillna(0)

    # ==========================================================
    # RUN CONTAGION ENGINE
    # ==========================================================

    contagion_results = (
        cached_run_contagion_analysis(
            portfolio
        )
    )

    contagion_df = (
        contagion_results[
            "contagion_results"
        ]
    )

    contagion_summary = (
        contagion_results[
            "summary"
        ]
    )

    # ==========================================================
    # RUN NETWORK ENGINE
    # ==========================================================

    network_results = (
        cached_run_network_analysis(
            portfolio
        )
    )

    network_df = (
        network_results[
            "network_results"
        ]
    )

    edge_df = (
        network_results[
            "network_edges"
        ]
    )

    network_summary = (
        network_results[
            "summary"
        ]
    )

    # ==========================================================
    # RUN CASCADE SIMULATOR
    # ==========================================================

    cascade_results = (
        cached_run_cascade_simulation(
            portfolio
        )
    )

    cascade_df = (
        cascade_results[
            "cascade_results"
        ]
    )

    cascade_summary = (
        cascade_results[
            "summary"
        ]
    )

    # ==========================================================
    # RUN SYSTEMIC RISK ENGINE
    # ==========================================================

    systemic_results = (
        cached_run_systemic_risk_analysis(
            portfolio
        )
    )

    systemic_df = (
        systemic_results[
            "systemic_results"
        ]
    )

    systemic_summary = (
        systemic_results[
            "summary"
        ]
    )

    live_context = get_dashboard_live_context(
        allow_api_refresh=True
    )
    live_data = live_summary(live_context)
    macro_data = macro_intelligence(live_context)
    market_data = market_intelligence(live_context)

    _section("🌐", "Live Contagion Environment", "CONTEXT")
    render_live_status_card(live_context)

    live_cols = st.columns(4)
    live_cols[0].metric(
        "Market Contagion",
        f"{market_data.get('market_risk_score', 0):.2f}"
    )
    live_cols[1].metric(
        "Macro Stress",
        f"{macro_data.get('macro_stress_score', 0):.2f}"
    )
    live_cols[2].metric(
        "Sentiment Stress",
        f"{live_data.get('sentiment_stress_score', 0):.2f}"
    )
    live_cols[3].metric(
        "Liquidity Stress",
        f"{market_data.get('liquidity_stress_score', 0):.2f}"
    )

    # ==========================================================
    # EXECUTIVE SYSTEMIC RISK DASHBOARD
    # ==========================================================

    st.divider()

    _section("🌐", "Executive Systemic Risk Dashboard", "SYSTEMIC")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Avg Fragility",
        systemic_summary[
            "average_systemic_fragility"
        ]
    )

    c2.metric(
        "Avg Resilience",
        systemic_summary[
            "average_enterprise_resilience"
        ]
    )

    c3.metric(
        "Avg Collapse Prob",
        f"{systemic_summary['average_collapse_probability']:.2%}"
    )

    c4.metric(
        "Critical Entities",
        systemic_summary[
            "critical_systemic_entities"
        ]
    )

    c5.metric(
        "Network Status",
        systemic_summary[
            "portfolio_network_instability"
        ]
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Max Systemic Importance",
        systemic_summary[
            "maximum_systemic_importance"
        ]
    )

    c2.metric(
        "Avg Systemic Importance",
        systemic_summary[
            "average_systemic_importance"
        ]
    )

    c3.metric(
        "Max Collapse Prob",
        f"{systemic_summary['maximum_collapse_probability']:.2%}"
    )

    _narrative(
        """
        <b>Terminology:</b> Entity and borrower both refer to a portfolio borrower record.
        A <b>node</b> is that borrower represented inside the network graph.
        <b>Critical nodes</b> are high-connectivity network positions; <b>critical entities</b>
        are borrowers breaching systemic-risk thresholds. Network instability reflects the
        overall interconnectedness risk across those nodes.
        """,
        variant="default",
        label="◈ Executive Network Definitions"
    )

    # ==========================================================
    # CONTAGION INTELLIGENCE DASHBOARD
    # ==========================================================

    st.divider()

    _section("🦠", "Contagion Intelligence Dashboard", "CONTAGION")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Portfolio Contagion",
        contagion_summary[
            "portfolio_average_contagion"
        ]
    )

    c2.metric(
        "Network Stability",
        contagion_summary[
            "network_stability"
        ]
    )

    c3.metric(
        "Highest Contagion",
        contagion_summary[
            "highest_contagion_risk"
        ]
    )

    c4.metric(
        "High Risk Borrowers",
        contagion_summary[
            "high_risk_borrowers"
        ]
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Highest Systemic Score",
        contagion_summary[
            "highest_systemic_score"
        ]
    )

    c2.metric(
        "Average Concentration %",
        contagion_summary[
            "average_concentration"
        ]
    )

    # ==========================================================
    # NETWORK ANALYTICS DASHBOARD
    # ==========================================================

    st.divider()

    _section("🔗", "Network Analytics Dashboard", "TOPOLOGY")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Avg Centrality",
        network_summary[
            "average_network_centrality"
        ]
    )

    c2.metric(
        "Total Connections",
        network_summary[
            "total_connections"
        ]
    )

    c3.metric(
        "Avg Connection Weight",
        network_summary[
            "average_connection_weight"
        ]
    )

    c4.metric(
        "Critical Nodes",
        network_summary[
            "critical_nodes"
        ]
    )

    st.metric(
        "Network Stability",
        network_summary[
            "network_stability"
        ]
    )

    # ==========================================================
    # CASCADE FAILURE DASHBOARD
    # ==========================================================

    st.divider()

    _section("⚡", "Cascade Failure Dashboard", "SIMULATION")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Cascade Loss",
        cascade_summary[
            "average_cascade_loss"
        ]
    )

    c2.metric(
        "Maximum Cascade Loss",
        cascade_summary[
            "maximum_cascade_loss"
        ]
    )

    c3.metric(
        "Average Acceleration",
        cascade_summary[
            "average_acceleration"
        ]
    )

    c4.metric(
        "High Systemic Accounts",
        cascade_summary[
            "high_systemic_accounts"
        ]
    )

    st.metric(
        "Network Collapse Risk",
        cascade_summary[
            "network_collapse_risk"
        ]
    )

    # ==========================================================
    # SYSTEMIC FRAGILITY VISUALIZATION
    # ==========================================================

    st.divider()

    _section("📊", "Systemic Fragility Distribution", "FRAGILITY SCORES")

    fig = px.histogram(

        systemic_df,

        x="systemic_fragility_score",

        nbins=30,

        title="Distribution of Systemic Fragility Scores",

        color_discrete_sequence=[PLOTLY_COLORS[0]]
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_color="rgba(139,92,246,0.3)", marker_line_width=0.5)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # TOP SYSTEMIC ENTITIES
    # ==========================================================

    st.divider()

    _section("🔴", "Top Systemic Entities", "HIGH IMPORTANCE")

    top_systemic = (
        systemic_df
        .sort_values(
            "systemic_importance_index",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_systemic[
            [
                "borrower_id",
                "systemic_fragility_score",
                "collapse_probability",
                "enterprise_resilience_score",
                "systemic_importance_index",
                "systemic_risk_classification",
            ]
        ],
        width="stretch"
    )

    # ==========================================================
    # TOP CONTAGION BORROWERS
    # ==========================================================

    st.divider()

    _section("🦠", "Top Contagion Borrowers", "EXPOSURE RANKING")

    top_contagion = (
        contagion_df
        .sort_values(
            "average_contagion_risk",
            ascending=False
        )
        .head(20)
    )

    fig = px.bar(

        top_contagion,

        x="borrower_id",

        y="average_contagion_risk",

        color="systemic_impact_score",

        title="Highest Contagion Risk Borrowers",

        color_continuous_scale=[
            [0.0, "#1e3a5f"],
            [0.4, "#8b5cf6"],
            [0.7, "#f59e0b"],
            [1.0, "#ef4444"],
        ]
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_width=0)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # NETWORK CONNECTION STRENGTH
    # ==========================================================

    st.divider()

    _section("🔗", "Network Connection Distribution", "TOPOLOGY")

    fig = px.histogram(

        edge_df,

        x="connection_weight",

        nbins=40,

        title="Network Connection Strength Distribution",

        color_discrete_sequence=[PLOTLY_COLORS[1]]
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_color="rgba(59,130,246,0.3)", marker_line_width=0.5)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # CASCADE LOSS ANALYSIS
    # ==========================================================

    st.divider()

    _section("💥", "Cascade Loss Distribution", "FAILURE CASCADE")

    fig = px.histogram(

        cascade_df,

        x="total_cascade_loss",

        nbins=40,

        title="Cascade Failure Loss Distribution",

        color_discrete_sequence=[PLOTLY_COLORS[3]]
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_color="rgba(245,158,11,0.3)", marker_line_width=0.5)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # SYSTEMIC IMPORTANCE RANKING
    # ==========================================================

    st.divider()

    _section("🏆", "Systemic Importance Ranking", "TOP 25")

    ranking_df = (
        systemic_df
        .sort_values(
            "systemic_importance_index",
            ascending=False
        )
        .head(25)
    )

    fig = px.bar(

        ranking_df,

        x="borrower_id",

        y="systemic_importance_index",

        color="systemic_fragility_score",

        title="Most Systemically Important Borrowers",

        color_continuous_scale=[
            [0.0, "#0a1628"],
            [0.35, "#8b5cf6"],
            [0.7, "#f59e0b"],
            [1.0, "#ef4444"],
        ]
    )

    _apply_layout(fig)
    fig.update_traces(marker_line_width=0)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE CONTAGION NARRATIVE
    # ==========================================================

    st.divider()

    _section("📋", "Executive Contagion Narrative", "CRO BRIEF")

    top_entity = (
        systemic_df
        .sort_values(
            "systemic_importance_index",
            ascending=False
        )
        .iloc[0]
    )

    _narrative(
        f"""
        <b>Highest Systemic Entity:</b> {top_entity['borrower_id']}<br>
        <b>Systemic Importance:</b> {top_entity['systemic_importance_index']:.2f}<br>
        <b>Fragility Score:</b> {top_entity['systemic_fragility_score']:.2f}<br>
        <b>Collapse Probability:</b> {top_entity['collapse_probability']:.2%}<br>
        <b>Risk Classification:</b> {top_entity['systemic_risk_classification']}<br><br>
        Current portfolio conditions indicate <b>{systemic_summary['portfolio_network_instability']}</b>.<br><br>
        Management should prioritize concentration monitoring, contagion mitigation,
        capital preservation, and stress-testing preparedness.
        """,
        variant="warn",
        label="⚠ Systemic Contagion Alert"
    )

    # ==========================================================
    # KRONOS FOOTER
    # ==========================================================

    st.divider()

    st.markdown(
        """
        <div class="kronos-footer">
            <span class="kronos-footer-text">KRONOS Enterprise Risk Platform · Contagion & Network Analytics Division</span>
            <div class="kronos-footer-tags">
                <span class="kronos-tag">Systemic Risk</span>
                <span class="kronos-tag blue">Network Topology</span>
                <span class="kronos-tag green">Cascade Simulation</span>
                <span class="kronos-tag amber">Contagion Intelligence</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ==========================================================
    # END OF DASHBOARD
    # ==========================================================

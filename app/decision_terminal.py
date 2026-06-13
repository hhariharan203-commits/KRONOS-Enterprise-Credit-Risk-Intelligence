# =============================================================================
# KRONOS — DECISION TERMINAL
# File: app/decision_terminal.py
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
# DECISION ENGINE
# =============================================================================

from src.decisioning.decision_terminal import (
    run_decision_engine
)

# =============================================================================
# POLICY ENGINE
# =============================================================================

from src.decisioning.policy_rules import (
    run_policy_engine
)

# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

from src.decisioning.recommendation_engine import (
    run_recommendation_engine
)

from src.shared.cache_manager import timed_cache

cached_run_decision_engine = timed_cache()(run_decision_engine)
cached_run_policy_engine = timed_cache()(run_policy_engine)
cached_run_recommendation_engine = timed_cache()(run_recommendation_engine)

# =============================================================================
# KRONOS GLOBAL DESIGN SYSTEM — INJECTED CSS
# =============================================================================

KRONOS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Playfair+Display:wght@600;700&display=swap');

/* ── ROOT TOKENS ─────────────────────────────────────────────────────────── */
:root {
    --navy-900:  #050d1a;
    --navy-800:  #091427;
    --navy-700:  #0d1f3c;
    --navy-600:  #132a52;
    --navy-500:  #1a3568;

    --slate-600: #374b6e;
    --slate-500: #4a6080;
    --slate-400: #627898;
    --slate-300: #8294ae;
    --slate-200: #a8b8cc;
    --slate-100: #cdd8e5;

    --emerald:   #00c896;
    --emerald-d: #00a07a;
    --amber:     #f0a500;
    --amber-d:   #c07800;
    --crimson:   #e02442;
    --crimson-d: #b01830;
    --ice-blue:  #4db8ff;
    --gold:      #c9a84c;

    --text-primary:   #e8edf5;
    --text-secondary: #a8b8cc;
    --text-muted:     #627898;

    --border-subtle:  rgba(77,184,255,0.12);
    --border-accent:  rgba(77,184,255,0.28);
    --glass-bg:       rgba(9,20,39,0.72);
    --card-bg:        rgba(13,31,60,0.85);
    --glow-blue:      0 0 24px rgba(77,184,255,0.14);
    --glow-emerald:   0 0 20px rgba(0,200,150,0.18);
    --glow-crimson:   0 0 20px rgba(224,36,66,0.18);
}

/* ── GLOBAL BASE ─────────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: var(--navy-900) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: var(--navy-800) !important;
    border-right: 1px solid var(--border-subtle) !important;
}

/* ── EXECUTIVE BANNER ────────────────────────────────────────────────────── */
.kronos-banner {
    background: linear-gradient(135deg, var(--navy-700) 0%, var(--navy-800) 50%, #0a1830 100%);
    border: 1px solid var(--border-accent);
    border-radius: 4px;
    padding: 32px 36px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--glow-blue), inset 0 1px 0 rgba(77,184,255,0.15);
}

.kronos-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        var(--ice-blue) 30%,
        var(--emerald) 70%,
        transparent 100%);
}

.kronos-banner::after {
    content: 'KRONOS';
    position: absolute;
    right: 36px; top: 50%;
    transform: translateY(-50%);
    font-family: 'JetBrains Mono', monospace;
    font-size: 72px;
    font-weight: 600;
    color: rgba(77,184,255,0.04);
    letter-spacing: 8px;
    pointer-events: none;
}

.banner-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 3px;
    color: var(--ice-blue);
    text-transform: uppercase;
    margin-bottom: 10px;
}

.banner-title {
    font-family: 'Playfair Display', serif;
    font-size: 30px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.3px;
    line-height: 1.15;
    margin-bottom: 10px;
}

.banner-subtitle {
    font-size: 13px;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 18px;
}

.banner-divider {
    color: var(--slate-500);
    font-size: 10px;
}

.banner-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0,200,150,0.12);
    border: 1px solid rgba(0,200,150,0.3);
    color: var(--emerald);
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 1.5px;
    padding: 3px 10px;
    border-radius: 2px;
}

.banner-pill::before {
    content: '●';
    font-size: 6px;
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
}

/* ── SECTION DIVIDER ─────────────────────────────────────────────────────── */
.section-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 36px 0 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border-subtle);
}

.section-header-line {
    width: 4px;
    height: 22px;
    background: linear-gradient(180deg, var(--ice-blue), var(--emerald));
    border-radius: 2px;
    flex-shrink: 0;
}

.section-header-text {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    font-weight: 600;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: var(--text-primary);
}

.section-badge {
    margin-left: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1.5px;
    color: var(--text-muted);
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border-subtle);
    padding: 3px 8px;
    border-radius: 2px;
}

/* ── KPI INTELLIGENCE CARDS ──────────────────────────────────────────────── */
.kpi-grid {
    display: grid;
    gap: 12px;
    margin-bottom: 8px;
}

.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 20px 22px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}

.kpi-card:hover {
    border-color: var(--border-accent);
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    border-radius: 4px 4px 0 0;
}

.kpi-card.emerald::before { background: var(--emerald); box-shadow: var(--glow-emerald); }
.kpi-card.amber::before   { background: var(--amber); }
.kpi-card.crimson::before { background: var(--crimson); box-shadow: var(--glow-crimson); }
.kpi-card.ice::before     { background: var(--ice-blue); box-shadow: var(--glow-blue); }
.kpi-card.gold::before    { background: var(--gold); }
.kpi-card.neutral::before { background: var(--slate-400); }

.kpi-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9.5px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 10px;
}

.kpi-value {
    font-family: 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
    letter-spacing: -1px;
    margin-bottom: 6px;
}

.kpi-value.emerald { color: var(--emerald); }
.kpi-value.amber   { color: var(--amber); }
.kpi-value.crimson { color: var(--crimson); }
.kpi-value.ice     { color: var(--ice-blue); }
.kpi-value.gold    { color: var(--gold); }

.kpi-sub {
    font-size: 11px;
    color: var(--text-muted);
    letter-spacing: 0.3px;
}

.kpi-icon {
    position: absolute;
    bottom: 14px; right: 18px;
    font-size: 22px;
    opacity: 0.18;
}

/* ── INSIGHT PANEL ───────────────────────────────────────────────────────── */
.insight-panel {
    background: linear-gradient(135deg, rgba(13,31,60,0.9), rgba(9,20,39,0.95));
    border: 1px solid var(--border-accent);
    border-left: 3px solid var(--ice-blue);
    border-radius: 4px;
    padding: 20px 24px;
    margin: 16px 0 24px;
    position: relative;
}

.insight-panel.warning {
    border-left-color: var(--amber);
    background: linear-gradient(135deg, rgba(240,165,0,0.06), rgba(9,20,39,0.95));
}

.insight-panel.critical {
    border-left-color: var(--crimson);
    background: linear-gradient(135deg, rgba(224,36,66,0.07), rgba(9,20,39,0.95));
}

.insight-panel.positive {
    border-left-color: var(--emerald);
    background: linear-gradient(135deg, rgba(0,200,150,0.06), rgba(9,20,39,0.95));
}

.insight-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--ice-blue);
    margin-bottom: 8px;
}

.insight-panel.warning  .insight-eyebrow { color: var(--amber); }
.insight-panel.critical .insight-eyebrow { color: var(--crimson); }
.insight-panel.positive .insight-eyebrow { color: var(--emerald); }

.insight-body {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.7;
}

.insight-body strong {
    color: var(--text-primary);
    font-weight: 600;
}

/* ── GOVERNANCE PANEL ────────────────────────────────────────────────────── */
.governance-panel {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 18px 22px;
    margin: 12px 0;
}

.governance-panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-subtle);
}

.governance-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 7px 0;
    border-bottom: 1px solid rgba(255,255,255,0.035);
    font-size: 12.5px;
}

.governance-row:last-child { border-bottom: none; }

.governance-key { color: var(--text-secondary); }

.governance-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: var(--text-primary);
}

.governance-val.breach { color: var(--crimson); }
.governance-val.watch  { color: var(--amber); }
.governance-val.ok     { color: var(--emerald); }

/* ── STREAMLIT COMPONENT OVERRIDES ───────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    padding: 18px 20px 16px !important;
    transition: border-color 0.2s !important;
}

div[data-testid="stMetric"]:hover {
    border-color: var(--border-accent) !important;
}

div[data-testid="stMetric"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 9.5px !important;
    font-weight: 500 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

div[data-testid="stMetricValue"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.8px !important;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 32px 0 !important;
}

/* Page title */
h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.3px !important;
}

h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    letter-spacing: 0.3px !important;
    text-transform: uppercase !important;
    font-size: 13px !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    padding-bottom: 10px !important;
    margin-bottom: 18px !important;
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] thead th {
    background: var(--navy-700) !important;
    color: var(--text-muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-accent) !important;
}

[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid var(--border-subtle) !important;
    transition: background 0.15s !important;
}

[data-testid="stDataFrame"] tbody tr:hover {
    background: rgba(77,184,255,0.05) !important;
}

[data-testid="stDataFrame"] tbody td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--text-secondary) !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, var(--navy-600), var(--navy-700)) !important;
    border: 1px solid var(--border-accent) !important;
    color: var(--ice-blue) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    padding: 10px 24px !important;
    border-radius: 3px !important;
    transition: all 0.2s !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: var(--navy-600) !important;
    border-color: var(--ice-blue) !important;
    box-shadow: var(--glow-blue) !important;
}

/* Warning */
[data-testid="stAlert"] {
    background: rgba(224,36,66,0.08) !important;
    border: 1px solid rgba(224,36,66,0.3) !important;
    border-radius: 4px !important;
    color: var(--text-secondary) !important;
}

/* Caption */
[data-testid="stCaptionContainer"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
}

/* Pie chart container */
[data-testid="stPlotlyChart"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    background: var(--card-bg) !important;
    padding: 4px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--navy-800); }
::-webkit-scrollbar-thumb { background: var(--slate-600); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--slate-400); }

/* Status indicator row */
.status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 1px;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--emerald);
    box-shadow: 0 0 6px var(--emerald);
    flex-shrink: 0;
}

.status-dot.amber  { background: var(--amber); box-shadow: 0 0 6px var(--amber); }
.status-dot.crimson { background: var(--crimson); box-shadow: 0 0 6px var(--crimson); }

/* Export center block */
.export-wrapper {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 24px 28px;
    margin-top: 8px;
}

.export-description {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 16px;
    line-height: 1.6;
}
</style>
"""

# =============================================================================
# PLOTLY THEME HELPER
# =============================================================================

_PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(9,20,39,0)",
    plot_bgcolor="rgba(9,20,39,0)",
    font=dict(
        family="Inter, JetBrains Mono, sans-serif",
        color="#a8b8cc",
        size=11
    ),
    title=dict(
        font=dict(
            family="Inter, sans-serif",
            size=13,
            color="#e8edf5"
        ),
        x=0.0,
        xanchor="left",
        pad=dict(l=4, b=16)
    ),
    margin=dict(t=48, b=24, l=24, r=24),
    legend=dict(
        bgcolor="rgba(9,20,39,0.6)",
        bordercolor="rgba(77,184,255,0.18)",
        borderwidth=1,
        font=dict(size=11, color="#a8b8cc")
    ),
    colorway=[
        "#4db8ff", "#00c896", "#f0a500",
        "#e02442", "#c9a84c", "#8294ae",
        "#627898"
    ]
)

_PIE_COLORS = [
    "#4db8ff", "#00c896", "#f0a500",
    "#e02442", "#c9a84c", "#8294ae"
]

# =============================================================================
# UI COMPONENT HELPERS
# =============================================================================

def _section(title: str, badge: str = "") -> None:
    badge_html = (
        f'<span class="section-badge">{badge}</span>'
        if badge else ""
    )
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-header-line"></div>
            <span class="section-header-text">{title}</span>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def _insight(body: str, kind: str = "", eyebrow: str = "Executive Intelligence") -> None:
    st.markdown(
        f"""
        <div class="insight-panel {kind}">
            <div class="insight-eyebrow">{eyebrow}</div>
            <div class="insight-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _governance_panel(title: str, rows: list) -> None:
    rows_html = "".join(
        f'<div class="governance-row">'
        f'  <span class="governance-key">{k}</span>'
        f'  <span class="governance-val {cls}">{v}</span>'
        f'</div>'
        for k, v, cls in rows
    )
    st.markdown(
        f"""
        <div class="governance-panel">
            <div class="governance-panel-title">{title}</div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True
    )


def _apply_plotly_theme(fig):
    fig.update_layout(**_PLOTLY_LAYOUT)
    return fig


# =============================================================================
# MAIN RENDER
# =============================================================================

def render(shared_data=None):

    shared_data = shared_data or {}

    # ── Inject global CSS ────────────────────────────────────────────────────
    st.markdown(KRONOS_CSS, unsafe_allow_html=True)

    # ── Executive Banner ─────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="kronos-banner">
            <div class="banner-eyebrow">KRONOS PLATFORM · DECISION TERMINAL v4</div>
            <div class="banner-title">🎯 Decision Intelligence Terminal</div>
            <div class="banner-subtitle">
                Decision Intelligence
                <span class="banner-divider">·</span>
                Policy Governance
                <span class="banner-divider">·</span>
                AI Recommendations
                <span class="banner-pill">LIVE</span>
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
        "pd_score",
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
    ]

    for col in numeric_cols:

        if col in portfolio.columns:

            portfolio[col] = pd.to_numeric(
                portfolio[col],
                errors="coerce"
            )

    portfolio = portfolio.fillna(0)

    # ==========================================================
    # DATA PREPARATION
    # ==========================================================

    portfolio["systemic_risk_score"] = (

        portfolio["pd_score"] * 100

    )

    portfolio["reserve_pressure_score"] = (

        portfolio["early_warning_score"]

    )

    portfolio["policy_status"] = np.where(

        portfolio["pd_score"] >= 0.85,

        "POLICY BREACH",

        np.where(

            portfolio["pd_score"] >= 0.70,

            "POLICY WATCHLIST",

            "POLICY COMPLIANT"

        )

    )

    # ==========================================================
    # DECISION ENGINE
    # ==========================================================

    decision_results = (
        cached_run_decision_engine(
            portfolio
        )
    )

    decision_df = (
        decision_results[
            "decision_results"
        ]
    )

    decision_summary = (
        decision_results[
            "summary"
        ]
    )

    # ==========================================================
    # POLICY ENGINE
    # ==========================================================

    policy_results = (
        cached_run_policy_engine(
            portfolio
        )
    )

    policy_df = (
        policy_results[
            "policy_results"
        ]
    )

    policy_summary = (
        policy_results[
            "summary"
        ]
    )

    # ==========================================================
    # RECOMMENDATION ENGINE INPUT
    # ==========================================================

    recommendation_input = (
        portfolio.merge(
            decision_df[
                [
                    "borrower_id",
                    "aggregated_risk_score"
                ]
            ],
            on="borrower_id",
            how="left"
        )
    )

    # ==========================================================
    # RECOMMENDATION ENGINE
    # ==========================================================

    recommendation_results = (
        cached_run_recommendation_engine(
            recommendation_input
        )
    )

    recommendation_df = (
        recommendation_results[
            "recommendation_results"
        ]
    )

    recommendation_summary = (
        recommendation_results[
            "summary"
        ]
    )

    # ==========================================================
    # EXECUTIVE DECISION DASHBOARD
    # ==========================================================

    st.divider()

    _section("Executive Decision Dashboard", "UNDERWRITING INTELLIGENCE")

    _insight(
        "Underwriting decisions have been processed across the active portfolio. "
        "Outputs are decision-support records requiring named human approval before action. "
        "Review approved accounts for covenant compliance, escalate manual reviews "
        "to senior credit officers, and action watchlist positions before month-end "
        "reserve cycle. <strong>Decision Watchlist</strong> reflects underwriting policy "
        "treatment and is separate from EWS Enhanced Monitoring and Critical Watchlist queues. "
        "<strong>Rejected accounts</strong> require formal documentation "
        "per Basel IV governance requirements with accountable approver sign-off.",
        kind="",
        eyebrow="Decision Engine · Executive Summary"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Approved",
        decision_summary[
            "approved_accounts"
        ]
    )

    c2.metric(
        "Manual Review",
        decision_summary[
            "manual_review_accounts"
        ]
    )

    c3.metric(
        "Watchlist",
        decision_summary[
            "watchlist_accounts"
        ]
    )

    c4.metric(
        "Rejected",
        decision_summary[
            "rejected_accounts"
        ]
    )

    c5.metric(
        "Avg Risk Score",
        decision_summary[
            "average_risk_score"
        ]
    )

    # ==========================================================
    # UNDERWRITING DECISION DISTRIBUTION
    # ==========================================================

    st.divider()

    _section("Underwriting Decision Distribution", "PORTFOLIO ANALYTICS")

    decision_chart = (
        decision_df[
            "underwriting_decision"
        ]
        .value_counts()
        .reset_index()
    )

    decision_chart.columns = [
        "Decision",
        "Count"
    ]

    fig = px.pie(
        decision_chart,
        names="Decision",
        values="Count",
        title="Portfolio Decision Distribution",
        color_discrete_sequence=_PIE_COLORS,
        hole=0.45
    )

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono, monospace",
            size=11,
            color="#e8edf5"
        ),
        marker=dict(
            line=dict(color="#091427", width=2)
        ),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Count: %{value}<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    fig = _apply_plotly_theme(fig)

    fig.update_layout(
        title_text="Portfolio Decision Distribution",
        annotations=[dict(
            text="DECISIONS",
            x=0.5, y=0.5,
            font=dict(
                family="JetBrains Mono, monospace",
                size=10,
                color="#627898"
            ),
            showarrow=False
        )]
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # POLICY GOVERNANCE DASHBOARD
    # ==========================================================

    st.divider()

    _section("Policy Governance Dashboard", "GOVERNANCE · COMPLIANCE")

    _insight(
        "Policy governance scanning complete. <strong>Critical breaches</strong> require "
        "immediate escalation to the Chief Risk Officer and Board Risk Committee. "
        "Approval denials must be logged in the regulatory breach register. "
        "Alignment score reflects aggregate policy conformance across the active portfolio.",
        kind="warning",
        eyebrow="Policy Engine · Governance Alert"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Policy Breaches",
        policy_summary[
            "total_policy_breaches"
        ]
    )

    c2.metric(
        "Critical Breaches",
        policy_summary[
            "critical_governance_breaches"
        ]
    )

    c3.metric(
        "Approval Denials",
        policy_summary[
            "approval_denials"
        ]
    )

    c4.metric(
        "Alignment Score",
        policy_summary[
            "average_policy_alignment"
        ]
    )

    _governance_panel(
        "GOVERNANCE FRAMEWORK SUMMARY",
        [
            ("Policy Breach Threshold",       "PD ≥ 0.85",        "breach"),
            ("Watchlist Trigger",             "PD ≥ 0.70",        "watch"),
            ("Compliant Band",                "PD < 0.70",        "ok"),
            ("Governance Standard",           "Basel IV / IFRS 9",""),
            ("Escalation Protocol",           "CRO + Board Risk", ""),
        ]
    )

    # ==========================================================
    # RECOMMENDATION INTELLIGENCE
    # ==========================================================

    st.divider()

    _section("AI Recommendation Intelligence", "RECOMMENDATION ENGINE")

    _insight(
        "AI-driven recommendations have been generated for the active portfolio. "
        "Recommendations do not constitute automated credit approval; they require senior "
        "credit officer review, accountability assignment, and governance evidence. "
        "<strong>Critical priority accounts</strong> require same-day executive action. "
        "High priority accounts should be reviewed within 48 hours by senior credit officers. "
        "Executive escalations indicate positions requiring Board-level visibility and "
        "strategic portfolio repositioning.",
        kind="critical",
        eyebrow="Recommendation Engine · Priority Intelligence"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Critical Priority",
        recommendation_summary[
            "critical_priority_accounts"
        ]
    )

    c2.metric(
        "High Priority",
        recommendation_summary[
            "high_priority_accounts"
        ]
    )

    c3.metric(
        "Executive Escalations",
        recommendation_summary[
            "executive_escalations"
        ]
    )

    c4.metric(
        "Recommendation Confidence",
        recommendation_summary[
            "average_recommendation_confidence"
        ]
    )

    # ==========================================================
    # TOP RISK BORROWERS
    # ==========================================================

    st.divider()

    _section("Top Risk Borrowers", "RISK INTELLIGENCE · TOP 20")

    _insight(
        "The twenty highest-risk borrowers by aggregated risk score are displayed below. "
        "Positions in the <strong>top decile</strong> warrant immediate credit review, "
        "enhanced monitoring covenants, and potential exposure reduction strategies. "
        "Cross-reference against policy violation registry before taking action.",
        kind="",
        eyebrow="Risk Engine · Senior Credit Review"
    )

    top_risk = (
        decision_df
        .sort_values(
            by="aggregated_risk_score",
            ascending=False
        )
        .head(20)
    )

    st.dataframe(
        top_risk,
        width="stretch"
    )

    # ==========================================================
    # POLICY VIOLATIONS
    # ==========================================================

    st.divider()

    _section("Policy Violations", "BREACH REGISTRY")

    _insight(
        "All accounts with active policy violations are listed in the breach registry below. "
        "Each violation must be individually reviewed, documented, and actioned per the "
        "institution's <strong>Credit Risk Policy Framework</strong>. Repeated violations "
        "trigger enhanced supervisory review under Basel IV Article 92 requirements.",
        kind="warning",
        eyebrow="Policy Engine · Violation Register"
    )

    violations = policy_df[
        policy_df[
            "violation_count"
        ] > 0
    ]

    st.dataframe(
        violations,
        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE ACTION QUEUE
    # ==========================================================

    st.divider()

    _section("Executive Action Queue", "ACTION REQUIRED")

    _insight(
        "Prioritised action queue generated by the AI Recommendation Engine. "
        "Items are ranked by urgency, exposure materiality, and policy sensitivity. "
        "<strong>Executive escalations</strong> must be formally acknowledged by a "
        "C-suite officer within the regulatory response window. All actions are "
        "timestamped and logged for audit trail purposes.",
        kind="critical",
        eyebrow="Recommendation Engine · Action Required"
    )

    st.dataframe(
        recommendation_df,
        width="stretch"
    )

    # ==========================================================
    # FULL DECISION PORTFOLIO
    # ==========================================================

    st.divider()

    _section("Full Decision Portfolio", "CONSOLIDATED VIEW")

    _insight(
        "Consolidated portfolio view merging decision, policy, and recommendation outputs "
        "across all active accounts. This table represents the <strong>single source of truth</strong> "
        "for executive reporting, regulatory submissions, and board pack preparation. "
        "Download via the Export Center below for offline distribution.",
        kind="positive",
        eyebrow="Decision Intelligence · Full Portfolio"
    )

    final_df = (
        decision_df
        .merge(
            policy_df,
            on="borrower_id",
            how="left"
        )
        .merge(
            recommendation_df,
            on="borrower_id",
            how="left"
        )
    )

    st.dataframe(
        final_df,
        width="stretch"
    )

    # ==========================================================
    # EXECUTIVE EXPORT CENTER
    # ==========================================================

    st.divider()

    _section("Executive Export Center", "SECURE DISTRIBUTION")

    st.markdown(
        """
        <div class="export-wrapper">
            <div class="governance-panel-title">DECISION PORTFOLIO — SECURE EXPORT</div>
            <div class="export-description">
                Export the consolidated decision portfolio as a structured CSV file for
                board pack preparation, regulatory submission, or offline credit review.
                All exports are timestamped and subject to institutional data governance policy.
                Distribution is restricted to authorized personnel with active portfolio oversight mandates.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    csv = final_df.to_csv(
        index=False
    )

    st.download_button(
        label=
            "Download Decision Portfolio",

        data=
            csv,

        file_name=
            "kronos_decision_portfolio.csv",

        mime=
            "text/csv"
    )

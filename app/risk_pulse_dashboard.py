# =============================================================================
# KRONOS — RISK PULSE DASHBOARD
# File: app/risk_pulse_dashboard.py
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
# RISK PULSE ENGINE
# =============================================================================

from src.live_monitoring.risk_pulse import (
    run_risk_pulse_engine
)

# =============================================================================
# REGIME DETECTOR
# =============================================================================

from src.live_monitoring.regime_detector import (
    run_regime_detector
)

# =============================================================================
# LIVE ALERT ENGINE
# =============================================================================

from src.live_monitoring.live_alerts import (
    run_live_alert_engine
)

from src.shared.cache_manager import timed_cache

cached_run_risk_pulse_engine = timed_cache()(run_risk_pulse_engine)
cached_run_regime_detector = timed_cache()(run_regime_detector)
cached_run_live_alert_engine = timed_cache()(run_live_alert_engine)

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
    --signal:    #ff6b35;

    --text-primary:   #e8edf5;
    --text-secondary: #a8b8cc;
    --text-muted:     #627898;

    --border-subtle:  rgba(77,184,255,0.12);
    --border-accent:  rgba(77,184,255,0.28);
    --glass-bg:       rgba(9,20,39,0.72);
    --card-bg:        rgba(13,31,60,0.85);
    --glow-blue:      0 0 24px rgba(77,184,255,0.14);
    --glow-emerald:   0 0 20px rgba(0,200,150,0.18);
    --glow-crimson:   0 0 20px rgba(224,36,66,0.22);
    --glow-signal:    0 0 20px rgba(255,107,53,0.22);
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
    box-shadow: var(--glow-crimson), inset 0 1px 0 rgba(224,36,66,0.12);
}

.kronos-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        var(--crimson) 25%,
        var(--signal) 55%,
        var(--amber) 100%);
}

.kronos-banner::after {
    content: 'PULSE';
    position: absolute;
    right: 36px; top: 50%;
    transform: translateY(-50%);
    font-family: 'JetBrains Mono', monospace;
    font-size: 72px;
    font-weight: 600;
    color: rgba(224,36,66,0.04);
    letter-spacing: 8px;
    pointer-events: none;
}

.banner-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 3px;
    color: var(--crimson);
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
    background: rgba(224,36,66,0.12);
    border: 1px solid rgba(224,36,66,0.38);
    color: var(--crimson);
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
    animation: pulse-dot 1.4s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.2; }
}

/* ── SECTION HEADER ──────────────────────────────────────────────────────── */
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
    background: linear-gradient(180deg, var(--crimson), var(--amber));
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

.section-badge.live {
    color: var(--crimson);
    background: rgba(224,36,66,0.08);
    border-color: rgba(224,36,66,0.28);
    animation: badge-pulse 2s infinite;
}

@keyframes badge-pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.6; }
}

/* ── INSIGHT PANEL ───────────────────────────────────────────────────────── */
.insight-panel {
    background: linear-gradient(135deg, rgba(13,31,60,0.9), rgba(9,20,39,0.95));
    border: 1px solid var(--border-accent);
    border-left: 3px solid var(--ice-blue);
    border-radius: 4px;
    padding: 20px 24px;
    margin: 16px 0 24px;
}

.insight-panel.warning {
    border-left-color: var(--amber);
    background: linear-gradient(135deg, rgba(240,165,0,0.06), rgba(9,20,39,0.95));
}

.insight-panel.critical {
    border-left-color: var(--crimson);
    background: linear-gradient(135deg, rgba(224,36,66,0.08), rgba(9,20,39,0.95));
}

.insight-panel.positive {
    border-left-color: var(--emerald);
    background: linear-gradient(135deg, rgba(0,200,150,0.06), rgba(9,20,39,0.95));
}

.insight-panel.signal {
    border-left-color: var(--signal);
    background: linear-gradient(135deg, rgba(255,107,53,0.07), rgba(9,20,39,0.95));
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
.insight-panel.signal   .insight-eyebrow { color: var(--signal); }

.insight-body {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.7;
}

.insight-body strong { color: var(--text-primary); font-weight: 600; }

/* ── ALERT TICKER ────────────────────────────────────────────────────────── */
.alert-ticker {
    background: rgba(224,36,66,0.06);
    border: 1px solid rgba(224,36,66,0.22);
    border-radius: 4px;
    padding: 11px 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--crimson);
    letter-spacing: 1px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.ticker-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--crimson);
    box-shadow: 0 0 8px var(--crimson);
    flex-shrink: 0;
    animation: pulse-dot 1.4s infinite;
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

/* ── STREAMLIT OVERRIDES ─────────────────────────────────────────────────── */
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

hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 32px 0 !important;
}

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
    background: rgba(224,36,66,0.04) !important;
}

[data-testid="stDataFrame"] tbody td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--text-secondary) !important;
}

[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, var(--navy-600), var(--navy-700)) !important;
    border: 1px solid rgba(224,36,66,0.35) !important;
    color: var(--crimson) !important;
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
    border-color: var(--crimson) !important;
    box-shadow: var(--glow-crimson) !important;
}

[data-testid="stAlert"] {
    background: rgba(0,200,150,0.06) !important;
    border: 1px solid rgba(0,200,150,0.22) !important;
    border-radius: 4px !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
}

[data-testid="stPlotlyChart"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    background: var(--card-bg) !important;
    padding: 4px !important;
}

[data-testid="stCaptionContainer"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
}

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

::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--navy-800); }
::-webkit-scrollbar-thumb { background: var(--slate-600); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: var(--slate-400); }
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
        font=dict(family="Inter, sans-serif", size=13, color="#e8edf5"),
        x=0.0,
        xanchor="left",
        pad=dict(l=4, b=16)
    ),
    margin=dict(t=48, b=24, l=24, r=24),
    legend=dict(
        bgcolor="rgba(9,20,39,0.6)",
        bordercolor="rgba(224,36,66,0.18)",
        borderwidth=1,
        font=dict(size=11, color="#a8b8cc")
    ),
    colorway=[
        "#e02442", "#f0a500", "#4db8ff",
        "#00c896", "#ff6b35", "#c9a84c", "#627898"
    ]
)

_AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="rgba(77,184,255,0.07)",
    gridwidth=1,
    zeroline=False,
    tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#8294ae")
)

_PIE_COLORS = ["#e02442", "#f0a500", "#4db8ff", "#00c896", "#ff6b35", "#c9a84c"]


def _apply_plotly_theme(fig):
    fig.update_layout(**_PLOTLY_LAYOUT)
    return fig


# =============================================================================
# UI HELPERS
# =============================================================================

def _section(title: str, badge: str = "", live: bool = False) -> None:
    live_class = " live" if live else ""
    badge_html = (
        f'<span class="section-badge{live_class}">{badge}</span>'
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
        f'<span class="governance-key">{k}</span>'
        f'<span class="governance-val {cls}">{v}</span>'
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


def _alert_ticker(message: str) -> None:
    st.markdown(
        f"""
        <div class="alert-ticker">
            <div class="ticker-dot"></div>
            {message}
        </div>
        """,
        unsafe_allow_html=True
    )


# =============================================================================
# MAIN RENDER
# =============================================================================

def render(shared_data=None):

    shared_data = shared_data or {}

    # ── Inject CSS ───────────────────────────────────────────────────────────
    st.markdown(KRONOS_CSS, unsafe_allow_html=True)

    # ── Executive Banner ─────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="kronos-banner">
            <div class="banner-eyebrow">KRONOS PLATFORM · RISK PULSE MODULE v4</div>
            <div class="banner-title">📡 Risk Pulse Dashboard</div>
            <div class="banner-subtitle">
                Real-Time Risk Monitoring
                <span class="banner-divider">·</span>
                Macro Regime Intelligence
                <span class="banner-divider">·</span>
                Enterprise Alert Center
                <span class="banner-pill">LIVE FEED</span>
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
        "risk_migration_score",
    }
    missing_columns = sorted(required_columns - set(portfolio.columns))
    if missing_columns:
        st.warning(
            "Portfolio data missing required columns: "
            + ", ".join(missing_columns)
        )
        return

    # =========================================================================
    # NUMERIC CLEANUP
    # =========================================================================

    numeric_cols = [

        "pd_score",

        "ead",

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

    # =========================================================================
    # LIVE MONITORING FEATURES
    # =========================================================================

    portfolio["systemic_risk_score"] = (

        portfolio["pd_score"] * 100

    )

    portfolio["reserve_pressure_score"] = (

        portfolio["early_warning_score"]

    )

    portfolio["stress_score"] = (

        portfolio["early_warning_score"]

    )

    portfolio["previous_pulse_score"] = (

        portfolio["risk_migration_score"]

    )

    # =========================================================================
    # RISK PULSE ENGINE
    # =========================================================================

    pulse_results = (
        cached_run_risk_pulse_engine(
            portfolio
        )
    )

    pulse_df = (
        pulse_results[
            "risk_pulse_results"
        ]
    )

    pulse_summary = (
        pulse_results[
            "summary"
        ]
    )

    # =========================================================================
    # MACRO REGIME DATA
    # =========================================================================

    macro_df = pd.DataFrame([

        {
            "period": "2025-Q1",

            "gdp_stress": -1.2,

            "inflation_stress": 2.5,

            "unemployment_stress": 3.0,

            "market_volatility": 18,

            "previous_regime_score": 20,
        },

        {
            "period": "2025-Q2",

            "gdp_stress": -2.0,

            "inflation_stress": 3.5,

            "unemployment_stress": 4.0,

            "market_volatility": 25,

            "previous_regime_score": 25,
        },

        {
            "period": "2025-Q3",

            "gdp_stress": -3.5,

            "inflation_stress": 5.2,

            "unemployment_stress": 5.8,

            "market_volatility": 45,

            "previous_regime_score": 40,
        },

        {
            "period": "2025-Q4",

            "gdp_stress": -4.5,

            "inflation_stress": 6.8,

            "unemployment_stress": 7.2,

            "market_volatility": 60,

            "previous_regime_score": 55,
        },

        {
            "period": "2026-Q1",

            "gdp_stress": -2.0,

            "inflation_stress": 4.0,

            "unemployment_stress": 5.0,

            "market_volatility": 35,

            "previous_regime_score": 40,
        }

    ])

    # =========================================================================
    # REGIME DETECTOR
    # =========================================================================

    regime_results = (
        cached_run_regime_detector(
            macro_df
        )
    )

    regime_df = (
        regime_results[
            "regime_results"
        ]
    )

    regime_summary = (
        regime_results[
            "summary"
        ]
    )

    # =========================================================================
    # LIVE ALERT INPUT
    # =========================================================================

    alert_input = (
        portfolio.merge(
            pulse_df[
                [
                    "borrower_id",
                    "live_risk_pulse_score"
                ]
            ],
            on="borrower_id",
            how="left"
        )
    )

    alert_input["previous_risk_score"] = (

        alert_input[
            "previous_pulse_score"
        ]

    )

    # =========================================================================
    # LIVE ALERT ENGINE
    # =========================================================================

    alert_results = (
        cached_run_live_alert_engine(
            alert_input
        )
    )

    alert_df = (
        alert_results[
            "live_alert_results"
        ]
    )

    alert_summary = (
        alert_results[
            "summary"
        ]
    )

    # =========================================================================
    # LIVE RISK PULSE EXECUTIVE DASHBOARD
    # =========================================================================

    st.divider()

    _section(
        "Live Risk Pulse Executive Dashboard",
        badge="● LIVE",
        live=True
    )

    _alert_ticker(
        "LIVE MONITORING ACTIVE — Risk pulse data is streaming in real-time. "
        "Critical escalations require immediate senior credit officer review."
    )

    _insight(
        "Real-time risk pulse scores have been computed across the active portfolio. "
        "The <strong>Average Risk Pulse</strong> reflects aggregate portfolio stress at the current monitoring interval. "
        "Critical escalations identify accounts breaching enterprise risk thresholds and require same-session action. "
        "<strong>Enterprise Resilience</strong> score measures portfolio-wide capacity to absorb credit deterioration.",
        kind="critical",
        eyebrow="Risk Pulse Engine · Live Executive Feed"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Risk Pulse",
        pulse_summary[
            "average_live_risk_pulse"
        ]
    )

    c2.metric(
        "Highest Risk Pulse",
        pulse_summary[
            "highest_live_risk"
        ]
    )

    c3.metric(
        "Critical Escalations",
        pulse_summary[
            "critical_escalations"
        ]
    )

    c4.metric(
        "Enterprise Resilience",
        pulse_summary[
            "average_enterprise_resilience"
        ]
    )

    _insight(
        "Refresh visibility: this dashboard was rendered at "
        f"<strong>{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>. "
        "Alert priority order is <strong>Critical Escalations</strong>, then "
        "<strong>Governance Breaches</strong>, then <strong>High Priority Alerts</strong>. "
        "Leadership should assign owners to critical escalations before reviewing distribution charts.",
        kind="critical",
        eyebrow="Risk Pulse Engine · Executive Action Priority"
    )

    # =========================================================================
    # LIVE RISK PULSE DISTRIBUTION
    # =========================================================================

    st.divider()

    _section("Live Risk Pulse Distribution", "PORTFOLIO ANALYTICS")

    _insight(
        "The distribution of live risk pulse scores reveals the concentration of credit stress "
        "across the portfolio. A right-skewed distribution indicates <strong>tail risk concentration</strong> "
        "requiring portfolio-level hedging consideration. Flat distributions suggest broad systemic "
        "deterioration requiring macro-level policy response.",
        kind="warning",
        eyebrow="Risk Pulse Engine · Score Distribution"
    )

    fig = px.histogram(
        pulse_df,
        x="live_risk_pulse_score",
        nbins=20,
        title="Portfolio Risk Pulse Distribution",
        color_discrete_sequence=["#e02442"]
    )

    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(9,20,39,0.7)", width=0.8),
            opacity=0.82
        ),
        hovertemplate="Risk Pulse: %{x:.2f}<br>Count: %{y}<extra></extra>"
    )

    fig.update_xaxes(**_AXIS_STYLE, title_text="Live Risk Pulse Score",
                     title_font=dict(size=10, color="#627898"))
    fig.update_yaxes(**_AXIS_STYLE, title_text="Account Count",
                     title_font=dict(size=10, color="#627898"))

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # MACRO REGIME INTELLIGENCE
    # =========================================================================

    st.divider()

    _section("Macro Regime Intelligence", "REGIME DETECTOR")

    _insight(
        "Macro regime classification integrates GDP stress, inflation, unemployment, and market volatility "
        "into a composite regime score. <strong>Crisis regime periods</strong> represent quarters where "
        "portfolio-level default probabilities are materially elevated above long-run averages. "
        "Recession probability drives strategic reserve provisioning and capital allocation decisions.",
        kind="signal",
        eyebrow="Regime Detector · Macro Intelligence"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Regime Score",
        regime_summary[
            "average_regime_score"
        ]
    )

    c2.metric(
        "Crisis Regimes",
        regime_summary[
            "crisis_regime_periods"
        ]
    )

    c3.metric(
        "Recession Probability",
        regime_summary[
            "average_recession_probability"
        ]
    )

    c4.metric(
        "Regime Confidence",
        regime_summary[
            "average_regime_confidence"
        ]
    )

    # =========================================================================
    # REGIME TREND ANALYSIS
    # =========================================================================

    st.divider()

    _section("Regime Trend Analysis", "MACRO · QUARTERLY TREND")

    _insight(
        "Quarterly macro regime score trend reveals the trajectory of systemic credit risk "
        "across the stress horizon. An <strong>ascending trend</strong> signals deteriorating macro conditions "
        "and warrants proactive credit tightening. Monitor 2026-Q1 recovery dynamics closely "
        "for evidence of regime normalisation before adjusting portfolio risk appetite.",
        kind="warning",
        eyebrow="Regime Detector · Trend Surveillance"
    )

    fig = px.line(
        regime_df,
        x="period",
        y="macro_regime_score",
        markers=True,
        title="Macro Regime Score — Quarterly Trend"
    )

    fig.update_traces(
        line=dict(color="#ff6b35", width=2.5),
        marker=dict(
            color="#ff6b35",
            size=8,
            line=dict(color="#091427", width=2),
            symbol="circle"
        ),
        hovertemplate="Period: %{x}<br>Regime Score: %{y:.2f}<extra></extra>"
    )

    fig.update_xaxes(
        **_AXIS_STYLE,
        title_text="Quarter",
        title_font=dict(size=10, color="#627898")
    )

    fig.update_yaxes(
        **_AXIS_STYLE,
        title_text="Macro Regime Score",
        title_font=dict(size=10, color="#627898")
    )

    fig.add_hrect(
        y0=50, y1=100,
        fillcolor="rgba(224,36,66,0.06)",
        line_width=0,
        annotation_text="CRISIS THRESHOLD",
        annotation_font=dict(
            family="JetBrains Mono, monospace",
            size=9,
            color="#e02442"
        ),
        annotation_position="top left"
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # REGIME DETAILS
    # =========================================================================

    st.divider()

    _section("Current Regime Assessment", "REGIME · PERIOD DETAIL")

    _insight(
        "Detailed regime assessment table provides full period-by-period macro stress decomposition. "
        "Use this data for <strong>ICAAP stress scenario construction</strong>, IFRS 9 forward-looking "
        "macro-economic variable calibration, and regulatory capital planning submissions.",
        kind="",
        eyebrow="Regime Detector · Period Assessment"
    )

    st.dataframe(
        regime_df,
        width="stretch"
    )

    # =========================================================================
    # LIVE ALERT CENTER
    # =========================================================================

    st.divider()

    _section("Live Alert Center", badge="● ALERTS", live=True)

    _alert_ticker(
        "ALERT CENTER ACTIVE — "
        + str(alert_summary["critical_priority_alerts"])
        + " critical alerts detected. Immediate executive review required."
    )

    _insight(
        "The enterprise alert center monitors portfolio positions in real-time against "
        "breach thresholds, governance triggers, and systemic risk indicators. "
        "<strong>Critical alerts</strong> must be actioned within the current trading session. "
        "Governance breaches trigger mandatory regulatory notification under BCBS 239 requirements.",
        kind="critical",
        eyebrow="Live Alert Engine · Enterprise Alert Center"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Critical Alerts",
        alert_summary[
            "critical_priority_alerts"
        ]
    )

    c2.metric(
        "High Priority Alerts",
        alert_summary[
            "high_priority_alerts"
        ]
    )

    c3.metric(
        "Governance Breaches",
        alert_summary[
            "governance_breaches"
        ]
    )

    c4.metric(
        "Systemic Alerts",
        alert_summary[
            "systemic_alert_accounts"
        ]
    )

    _governance_panel(
        "ALERT GOVERNANCE FRAMEWORK",
        [
            ("Critical Alert Response",  "Same Session",   "breach"),
            ("High Priority Window",     "48 Hours",       "watch"),
            ("Governance Breach Filing", "Regulatory Log", "breach"),
            ("Systemic Alert Protocol",  "CRO + Board",    "breach"),
            ("Standard Monitoring",      "Daily Cycle",    "ok"),
        ]
    )

    # =========================================================================
    # ALERT PRIORITY DISTRIBUTION
    # =========================================================================

    st.divider()

    _section("Alert Priority Distribution", "PORTFOLIO ANALYTICS")

    _insight(
        "Alert priority distribution reveals the severity profile of current portfolio stress signals. "
        "A concentration of <strong>critical and high priority alerts</strong> indicates systemic deterioration "
        "requiring portfolio-level risk appetite review. Standard monitoring positions should be "
        "re-evaluated if macro regime conditions continue to deteriorate.",
        kind="warning",
        eyebrow="Alert Engine · Priority Distribution"
    )

    alert_chart = (
        alert_df[
            "alert_priority"
        ]
        .value_counts()
        .reset_index()
    )

    alert_chart.columns = [
        "Priority",
        "Count"
    ]

    fig = px.pie(
        alert_chart,
        names="Priority",
        values="Count",
        title="Enterprise Alert Priority Distribution",
        color_discrete_sequence=_PIE_COLORS,
        hole=0.44
    )

    fig.update_traces(
        textfont=dict(
            family="JetBrains Mono, monospace",
            size=11,
            color="#e8edf5"
        ),
        marker=dict(line=dict(color="#091427", width=2)),
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Count: %{value}<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    fig = _apply_plotly_theme(fig)

    fig.update_layout(
        annotations=[dict(
            text="ALERTS",
            x=0.5, y=0.5,
            font=dict(
                family="JetBrains Mono, monospace",
                size=9,
                color="#627898"
            ),
            showarrow=False
        )]
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # LIVE ALERT DETAILS
    # =========================================================================

    st.divider()

    _section("Live Alert Details", "OPERATIONAL INTELLIGENCE")

    _insight(
        "Full live alert register for the current monitoring cycle. Each record includes "
        "borrower identity, alert priority classification, governance breach status, and "
        "systemic risk flag. <strong>Export this table</strong> as part of the daily risk "
        "reporting pack for distribution to senior credit officers and the CRO office.",
        kind="",
        eyebrow="Alert Engine · Live Register"
    )

    st.dataframe(
        alert_df,
        width="stretch"
    )

    # =========================================================================
    # EXECUTIVE ESCALATION MONITOR
    # =========================================================================

    st.divider()

    _section("Executive Escalation Monitor", "ESCALATION ANALYTICS")

    _insight(
        "Executive escalation distribution quantifies the volume of positions requiring "
        "board-level or C-suite attention versus standard monitoring. "
        "<strong>High escalation concentration</strong> should trigger emergency Risk Committee "
        "convening and portfolio-level defensive positioning review.",
        kind="critical",
        eyebrow="Alert Engine · Escalation Monitor"
    )

    escalation_chart = (
        alert_df[
            "executive_escalation"
        ]
        .value_counts()
        .reset_index()
    )

    escalation_chart.columns = [
        "Escalation",
        "Count"
    ]

    fig = px.bar(
        escalation_chart,
        x="Escalation",
        y="Count",
        title="Executive Escalation Distribution",
        color_discrete_sequence=["#e02442"]
    )

    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(9,20,39,0.7)", width=0.8),
            opacity=0.85
        ),
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
    )

    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#a8b8cc"),
        title_text=""
    )

    fig.update_yaxes(
        **_AXIS_STYLE,
        title_text="Account Count",
        title_font=dict(size=10, color="#627898")
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # EXECUTIVE ESCALATION QUEUE
    # =========================================================================

    st.divider()

    _section("Executive Escalation Queue", "ACTION REQUIRED")

    _insight(
        "Filtered escalation queue showing all accounts above standard monitoring threshold. "
        "Each position in this queue requires a <strong>named senior credit officer assignment</strong> "
        "and formal action plan documentation before next reporting cycle close.",
        kind="critical",
        eyebrow="Alert Engine · Executive Queue"
    )

    escalation_queue = alert_df[
        alert_df[
            "executive_escalation"
        ]
        != "STANDARD MONITORING"
    ]

    st.dataframe(
        escalation_queue,
        width="stretch"
    )

    # =========================================================================
    # RISK SEVERITY MATRIX
    # =========================================================================

    st.divider()

    _section("Risk Severity Matrix", "CONCENTRATION ANALYSIS")

    _insight(
        "The enterprise risk concentration matrix cross-references escalation severity against "
        "portfolio health classification. <strong>High-density cells</strong> in the upper-right "
        "(critical escalation × deteriorating health) represent the most urgent portfolio clusters "
        "requiring immediate capital provisioning and covenant enforcement review.",
        kind="signal",
        eyebrow="Risk Pulse Engine · Severity Matrix"
    )

    heatmap_df = (

        pulse_df

        .groupby(
            [
                "executive_escalation",
                "portfolio_health"
            ]
        )

        .size()

        .reset_index(
            name="count"
        )

    )

    fig = px.density_heatmap(

        heatmap_df,

        x="executive_escalation",

        y="portfolio_health",

        z="count",

        title="Enterprise Risk Concentration Matrix",

        color_continuous_scale=[
            [0.0,  "rgba(9,20,39,0.9)"],
            [0.3,  "#132a52"],
            [0.6,  "#f0a500"],
            [0.85, "#e02442"],
            [1.0,  "#7a0018"]
        ]
    )

    fig.update_xaxes(
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#a8b8cc"),
        title_text="Executive Escalation",
        title_font=dict(size=10, color="#627898")
    )

    fig.update_yaxes(
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#a8b8cc"),
        title_text="Portfolio Health",
        title_font=dict(size=10, color="#627898")
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # CAPITAL PRESSURE & RESILIENCE DASHBOARD
    # =========================================================================

    st.divider()

    _section("Capital Pressure & Enterprise Resilience", "CAPITAL ANALYTICS")

    _insight(
        "Capital pressure and resilience metrics provide a real-time view of the portfolio's "
        "capacity to absorb further credit deterioration without breaching regulatory capital minima. "
        "<strong>Minimum resilience</strong> identifies the most vulnerable position in the portfolio "
        "and establishes the binding constraint for portfolio-level risk appetite setting.",
        kind="",
        eyebrow="Risk Pulse Engine · Capital Intelligence"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Resilience",
        pulse_summary[
            "average_enterprise_resilience"
        ]
    )

    c2.metric(
        "Maximum Resilience",
        pulse_summary[
            "maximum_resilience"
        ]
    )

    c3.metric(
        "Minimum Resilience",
        pulse_summary[
            "minimum_resilience"
        ]
    )

    c4.metric(
        "High Risk Accounts",
        pulse_summary[
            "high_risk_accounts"
        ]
    )

    # =========================================================================
    # RISK VS SYSTEMIC RISK ANALYSIS
    # =========================================================================

    st.divider()

    _section("Risk Pulse vs Systemic Risk", "BIVARIATE RISK ANALYSIS")

    _insight(
        "The scatter plot below maps live risk pulse scores against systemic risk exposure "
        "for each borrower, coloured by escalation classification. "
        "<strong>Upper-right quadrant</strong> positions represent accounts with both high pulse "
        "and high systemic risk — these require immediate dual-trigger action across credit "
        "and macro stress frameworks simultaneously.",
        kind="warning",
        eyebrow="Risk Pulse Engine · Bivariate Analysis"
    )

    fig = px.scatter(

        pulse_df,

        x="live_risk_pulse_score",

        y="systemic_risk_score",

        color="executive_escalation",

        hover_data=[
            "borrower_id"
        ],

        title="Risk Pulse vs Systemic Risk — Escalation Map",

        color_discrete_sequence=_PIE_COLORS
    )

    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.78,
            line=dict(color="rgba(9,20,39,0.5)", width=0.8)
        )
    )

    fig.update_xaxes(
        **_AXIS_STYLE,
        title_text="Live Risk Pulse Score",
        title_font=dict(size=10, color="#627898")
    )

    fig.update_yaxes(
        **_AXIS_STYLE,
        title_text="Systemic Risk Score",
        title_font=dict(size=10, color="#627898")
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # CAPITAL PRESSURE MONITOR
    # =========================================================================

    st.divider()

    _section("Capital Pressure Monitor", "CAPITAL DISTRIBUTION")

    _insight(
        "Capital pressure distribution classifies portfolio positions by their capital consumption "
        "and stress buffer consumption rate. <strong>Elevated capital pressure</strong> signals "
        "accounts approaching internal capital threshold triggers, warranting early engagement "
        "with credit restructuring teams and collateral enforcement review.",
        kind="signal",
        eyebrow="Risk Pulse Engine · Capital Pressure"
    )

    capital_chart = (
        pulse_df[
            "capital_pressure"
        ]
        .value_counts()
        .reset_index()
    )

    capital_chart.columns = [
        "Capital Pressure",
        "Count"
    ]

    fig = px.bar(
        capital_chart,
        x="Capital Pressure",
        y="Count",
        title="Capital Pressure Distribution",
        color_discrete_sequence=["#f0a500"]
    )

    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(9,20,39,0.7)", width=0.8),
            opacity=0.85
        ),
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
    )

    fig.update_xaxes(
        showgrid=False,
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#a8b8cc"),
        title_text=""
    )

    fig.update_yaxes(
        **_AXIS_STYLE,
        title_text="Account Count",
        title_font=dict(size=10, color="#627898")
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =========================================================================
    # CRITICAL ALERT QUEUE
    # =========================================================================

    st.divider()

    _section("Critical Alert Queue", badge="● CRITICAL", live=True)

    _insight(
        "Filtered critical alert queue displaying only <strong>CRITICAL PRIORITY</strong> accounts. "
        "Each position in this queue requires immediate escalation to the Chief Risk Officer. "
        "All actions must be logged in the incident management system within 2 hours of detection.",
        kind="critical",
        eyebrow="Alert Engine · Critical Priority Queue"
    )

    critical_alerts = alert_df[

        alert_df[
            "alert_priority"
        ]
        == "CRITICAL PRIORITY ALERT"

    ]

    if critical_alerts.empty:

        st.success(
            "No critical alerts detected."
        )

    else:

        st.dataframe(
            critical_alerts,
            width="stretch"
        )

    # =========================================================================
    # GOVERNANCE BREACH MONITOR
    # =========================================================================

    st.divider()

    _section("Governance Breach Monitor", "GOVERNANCE · BREACH REGISTER")

    _insight(
        "Active governance breach monitor. All accounts flagged with governance breaches must be "
        "individually documented in the <strong>Regulatory Breach Register</strong> and reported "
        "to the Compliance Officer within the regulatory notification window. "
        "Repeated breaches trigger supervisory escalation under SREP framework.",
        kind="warning",
        eyebrow="Alert Engine · Governance Breach Monitor"
    )

    governance_breaches = alert_df[

        alert_df[
            "governance_breach"
        ]
        != "NO GOVERNANCE BREACH"

    ]

    if governance_breaches.empty:

        st.success(
            "No governance breaches detected."
        )

    else:

        st.dataframe(
            governance_breaches,
            width="stretch"
        )

    # =========================================================================
    # SYSTEMIC ALERT WATCHLIST
    # =========================================================================

    st.divider()

    _section("Systemic Alert Watchlist", "SYSTEMIC RISK · WATCHLIST")

    _insight(
        "Systemic alert watchlist identifies accounts triggering <strong>CRITICAL SYSTEMIC ALERT</strong> "
        "classification. These positions represent potential contagion vectors within the portfolio "
        "and require assessment under the institution's Systemic Risk Framework and "
        "interconnectedness stress testing protocols.",
        kind="critical",
        eyebrow="Alert Engine · Systemic Watchlist"
    )

    systemic_watchlist = alert_df[

        alert_df[
            "systemic_alert"
        ]
        == "CRITICAL SYSTEMIC ALERT"

    ]

    if systemic_watchlist.empty:

        st.success(
            "No critical systemic alerts."
        )

    else:

        st.dataframe(
            systemic_watchlist,
            width="stretch"
        )

    # =========================================================================
    # FULL RISK MONITORING FEED
    # =========================================================================

    st.divider()

    _section("Full Risk Monitoring Feed", "CONSOLIDATED FEED")

    _insight(
        "Complete consolidated risk monitoring feed merging pulse scores and live alert data "
        "for all active accounts. This table serves as the <strong>single monitoring record</strong> "
        "for the current cycle and feeds into the daily executive risk pack and regulatory reporting suite.",
        kind="positive",
        eyebrow="Risk Intelligence · Full Monitoring Feed"
    )

    final_df = (

        pulse_df

        .merge(
            alert_df,
            on="borrower_id",
            how="left"
        )

    )

    st.dataframe(
        final_df,
        width="stretch"
    )

    # =========================================================================
    # TOP RISK ACCOUNTS
    # =========================================================================

    st.divider()

    _section("Top Risk Accounts", "RISK INTELLIGENCE · TOP 20")

    _insight(
        "Top 20 accounts by live risk pulse score. These positions form the <strong>priority surveillance "
        "list</strong> for the current monitoring cycle. Senior credit officers should review each "
        "account's covenant package and EAD exposure before the next executive reporting deadline.",
        kind="warning",
        eyebrow="Risk Pulse Engine · Priority Surveillance List"
    )

    top_risk_accounts = (

        pulse_df

        .sort_values(
            by="live_risk_pulse_score",
            ascending=False
        )

        .head(20)

    )

    st.dataframe(
        top_risk_accounts,
        width="stretch"
    )

    # =========================================================================
    # REAL-TIME EXECUTIVE NARRATIVES
    # =========================================================================

    st.divider()

    _section("Executive Risk Narratives", "AI NARRATIVE INTELLIGENCE")

    _insight(
        "AI-generated executive narratives provide borrower-level risk commentary for each "
        "account in the alert feed. Use these narratives for <strong>credit committee briefings</strong>, "
        "board pack preparation, and senior credit officer escalation memos. "
        "Narratives are generated at each monitoring cycle and timestamped for audit purposes.",
        kind="",
        eyebrow="Alert Engine · AI Narrative Feed"
    )

    narrative_df = alert_df[
        [
            "borrower_id",
            "executive_narrative"
        ]
    ]

    st.dataframe(
        narrative_df,
        width="stretch"
    )

    # =========================================================================
    # EXECUTIVE EXPORT CENTER
    # =========================================================================

    st.divider()

    _section("Executive Export Center", "SECURE DISTRIBUTION")

    st.markdown(
        """
        <div class="export-wrapper">
            <div class="governance-panel-title">RISK PULSE REPORT — SECURE EXPORT</div>
            <div class="export-description">
                Export the consolidated risk pulse monitoring feed as a structured CSV file for
                inclusion in the daily executive risk pack, regulatory reporting submissions,
                and senior credit officer distribution. All exports are cycle-stamped and subject
                to institutional data governance policy. Distribution restricted to authorised
                risk monitoring and credit surveillance personnel.
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
            "Download Risk Pulse Report",

        data=
            csv,

        file_name=
            "kronos_risk_pulse_report.csv",

        mime=
            "text/csv"
    )

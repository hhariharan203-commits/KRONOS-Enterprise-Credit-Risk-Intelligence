# =============================================================================
# KRONOS — REPORTS DASHBOARD
# File: app/reports_dashboard.py
# =============================================================================

import os
import contextlib
import io

import pandas as pd
import numpy as np

import plotly.express as px

import streamlit as st

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:

    sys.path.append(
        str(ROOT_DIR)
    )

# =============================================================================
# REPORT GENERATOR
# =============================================================================

from src.reporting.report_generator import (
    generate_institutional_report,
)
from src.live_monitoring.live_intelligence import get_live_intelligence
from src.shared.cache_manager import timed_cache
from app.live_intelligence_components import render_live_status_card


def _generate_report_quiet(
    portfolio,
    live_context,
    build_pdf
):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        return generate_institutional_report(
            portfolio,
            live_context=live_context,
            build_pdf=build_pdf
        )


cached_generate_report = timed_cache()(
    _generate_report_quiet
)

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
    --amber:     #f0a500;
    --crimson:   #e02442;
    --ice-blue:  #4db8ff;
    --gold:      #c9a84c;

    --text-primary:   #e8edf5;
    --text-secondary: #a8b8cc;
    --text-muted:     #627898;

    --border-subtle:  rgba(77,184,255,0.12);
    --border-accent:  rgba(77,184,255,0.28);
    --card-bg:        rgba(13,31,60,0.85);
    --glow-blue:      0 0 24px rgba(77,184,255,0.14);
    --glow-emerald:   0 0 20px rgba(0,200,150,0.18);
    --glow-gold:      0 0 20px rgba(201,168,76,0.20);
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
    border: 1px solid rgba(201,168,76,0.28);
    border-radius: 4px;
    padding: 32px 36px 28px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--glow-gold), inset 0 1px 0 rgba(201,168,76,0.12);
}

.kronos-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        var(--gold) 30%,
        var(--ice-blue) 65%,
        transparent 100%);
}

.kronos-banner::after {
    content: 'REPORT';
    position: absolute;
    right: 36px; top: 50%;
    transform: translateY(-50%);
    font-family: 'JetBrains Mono', monospace;
    font-size: 72px;
    font-weight: 600;
    color: rgba(201,168,76,0.04);
    letter-spacing: 8px;
    pointer-events: none;
}

.banner-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 3px;
    color: var(--gold);
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
    background: rgba(201,168,76,0.12);
    border: 1px solid rgba(201,168,76,0.38);
    color: var(--gold);
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
    animation: pulse-dot 2.5s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
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
    background: linear-gradient(180deg, var(--gold), var(--ice-blue));
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

.insight-panel.gold {
    border-left-color: var(--gold);
    background: linear-gradient(135deg, rgba(201,168,76,0.07), rgba(9,20,39,0.95));
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
.insight-panel.gold     .insight-eyebrow { color: var(--gold); }

.insight-body {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.7;
}

.insight-body strong { color: var(--text-primary); font-weight: 600; }

/* ── NARRATIVE EXPANDER OVERRIDES ────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: var(--card-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    margin-bottom: 8px !important;
}

[data-testid="stExpander"] summary {
    font-family: 'Inter', sans-serif !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.6px !important;
    text-transform: uppercase !important;
    color: var(--text-secondary) !important;
    padding: 14px 18px !important;
}

[data-testid="stExpander"] summary:hover {
    color: var(--text-primary) !important;
    background: rgba(77,184,255,0.04) !important;
}

[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
    padding: 4px 18px 18px !important;
    font-size: 13px !important;
    color: var(--text-secondary) !important;
    line-height: 1.75 !important;
    border-top: 1px solid var(--border-subtle) !important;
}

/* ── PDF PATH CODE BLOCK ──────────────────────────────────────────────────── */
[data-testid="stCode"] {
    background: var(--navy-800) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--gold) !important;
}

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
    background: rgba(201,168,76,0.05) !important;
}

[data-testid="stDataFrame"] tbody td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--text-secondary) !important;
}

[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, var(--navy-600), var(--navy-700)) !important;
    border: 1px solid rgba(201,168,76,0.38) !important;
    color: var(--gold) !important;
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
    border-color: var(--gold) !important;
    box-shadow: var(--glow-gold) !important;
}

[data-testid="stAlert"] {
    background: rgba(77,184,255,0.05) !important;
    border: 1px solid rgba(77,184,255,0.2) !important;
    border-radius: 4px !important;
    color: var(--text-secondary) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    line-height: 1.7 !important;
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
    margin-bottom: 16px;
}

.export-description {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 0;
    line-height: 1.6;
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
        bordercolor="rgba(201,168,76,0.18)",
        borderwidth=1,
        font=dict(size=11, color="#a8b8cc")
    ),
    colorway=[
        "#c9a84c", "#4db8ff", "#00c896",
        "#f0a500", "#e02442", "#627898"
    ]
)

_AXIS_STYLE = dict(
    showgrid=True,
    gridcolor="rgba(77,184,255,0.07)",
    gridwidth=1,
    zeroline=False,
    tickfont=dict(family="JetBrains Mono, monospace", size=10, color="#8294ae")
)


def _apply_plotly_theme(fig):
    fig.update_layout(**_PLOTLY_LAYOUT)
    return fig


# =============================================================================
# UI HELPERS
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
            <div class="banner-eyebrow">KRONOS PLATFORM · EXECUTIVE REPORTING CENTER v4</div>
            <div class="banner-title">📑 Executive Reporting Center</div>
            <div class="banner-subtitle">
                Board Reporting
                <span class="banner-divider">·</span>
                Governance Intelligence
                <span class="banner-divider">·</span>
                Enterprise PDF Reporting
                <span class="banner-pill">BOARD READY</span>
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

        "early_warning_score",

        "ead",
    ]

    for col in numeric_cols:

        if col in portfolio.columns:

            portfolio[col] = pd.to_numeric(
                portfolio[col],
                errors="coerce"
            )

    portfolio = portfolio.fillna(0)

    # ==========================================================
    # REPORTING DATA PREPARATION
    # ==========================================================

    # The report generator enriches missing reporting metrics
    # directly from KRONOS engines.

    live_context = get_live_intelligence(
        allow_api_refresh=True
    )
    live_summary = live_context.get("summary", {})
    macro_intelligence = live_context.get("macro_intelligence", {})
    news_intelligence = live_context.get("news_intelligence", {})
    market_intelligence = live_context.get("market_intelligence", {})
    pdf_report_path = str(
        Path("reports") / "kronos_enterprise_report.pdf"
    )
    report_cache_key = "kronos_enterprise_report_package"

    generate_report = st.button(
        "Generate / Refresh Enterprise Report"
    )

    if generate_report:
        st.session_state[report_cache_key] = cached_generate_report(
            portfolio,
            live_context,
            False
        )

    if report_cache_key not in st.session_state:
        render_live_status_card(live_context)
        st.info(
            "Generate the current enterprise report to display the board-ready "
            "reporting sections. The latest cached PDF remains available when present."
        )

        if os.path.exists(
            pdf_report_path
        ):

            with open(
                pdf_report_path,
                "rb"
            ) as pdf_file:

                st.download_button(
                    label=
                        "Download Latest Enterprise PDF Report",
                    data=
                        pdf_file,
                    file_name=
                        "KRONOS_Enterprise_Report.pdf",
                    mime=
                        "application/pdf"
                )

        return

    # ==========================================================
    # REPORT GENERATION
    # ==========================================================

    report_package = st.session_state[
        report_cache_key
    ]

    portfolio = (
        report_package
        .get(
            "engine_reporting_context",
            {}
        )
        .get(
            "prepared_portfolio",
            portfolio
        )
    )

    executive_summary = (
        report_package[
            "executive_summary"
        ]
    )

    governance_summary = (
        report_package[
            "governance_summary"
        ]
    )

    narrative_results = (
        report_package[
            "narrative_results"
        ]
    )

    metrics = (
        report_package[
            "metrics"
        ]
    )

    pdf_report_path = (
        report_package.get(
            "pdf_report_path"
        )
        or pdf_report_path
    )

    regime_classification = executive_summary[
        "regime_classification"
    ]
    executive_escalation = executive_summary[
        "executive_escalation"
    ]
    strategic_recommendation = narrative_results[
        "strategic_recommendation"
    ]
    crisis_reporting = (
        "CRISIS" in str(regime_classification).upper()
        or "CRISIS" in str(executive_escalation).upper()
    )

    # ==========================================================
    # EXECUTIVE REPORTING DASHBOARD
    # ==========================================================

    st.divider()

    _section("Executive Risk Overview", "BOARD INTELLIGENCE")

    _insight(
        "Executive risk overview synthesises the four primary board-level risk indicators. "
        "<strong>Enterprise Risk</strong> reflects the portfolio-wide credit quality score. "
        "<strong>Systemic Risk</strong> captures contagion and interconnectedness exposure. "
        "<strong>Capital Ratio</strong> confirms regulatory adequacy. "
        "<strong>Risk Pulse</strong> provides the real-time monitoring signal for board situational awareness.",
        kind="gold",
        eyebrow="Report Generator · Executive Board View"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Enterprise Risk",
        executive_summary[
            "enterprise_risk_score"
        ]
    )

    c2.metric(
        "Systemic Risk",
        executive_summary[
            "systemic_risk_score"
        ]
    )

    c3.metric(
        "Capital Ratio",
        executive_summary[
            "capital_ratio"
        ]
    )

    c4.metric(
        "Risk Pulse",
        executive_summary[
            "risk_pulse"
        ]
    )

    # ==========================================================
    # LIVE INTELLIGENCE REPORTING
    # ==========================================================

    st.divider()

    _section("Live Intelligence Reporting", "MACRO · MARKET · NEWS")

    _insight(
        "Live intelligence context is embedded into the report package and board dashboard. "
        "Macroeconomic, market, and news signals provide the external-risk lens for the "
        "current reporting cycle while preserving the historical portfolio analytics base.",
        kind="gold",
        eyebrow="Report Generator · Live Intelligence"
    )

    render_live_status_card(live_context)

    li1, li2, li3, li4 = st.columns(4)

    li1.metric(
        "Enterprise Live Risk",
        f"{live_summary.get('enterprise_live_risk_score', 0):.2f}"
    )

    li2.metric(
        "Macro Regime",
        macro_intelligence.get(
            "macro_regime",
            "UNAVAILABLE"
        )
    )

    li3.metric(
        "Market Regime",
        market_intelligence.get(
            "market_regime",
            "UNAVAILABLE"
        )
    )

    li4.metric(
        "News Regime",
        news_intelligence.get(
            "risk_sentiment_regime",
            "UNAVAILABLE"
        )
    )

    # ==========================================================
    # PORTFOLIO INTELLIGENCE
    # ==========================================================

    st.divider()

    _section("Portfolio Intelligence", "PORTFOLIO ANALYTICS")

    _insight(
        "Portfolio intelligence metrics provide the structural context behind top-line risk scores. "
        "<strong>Critical entities</strong> are accounts breaching enterprise risk thresholds and requiring "
        "board-level visibility. Maximum risk and systemic readings establish the tail scenario "
        "for stress capital calculations and ICAAP submissions.",
        kind="",
        eyebrow="Report Generator · Portfolio Intelligence"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Critical Entities",
        executive_summary[
            "critical_entities"
        ]
    )

    c2.metric(
        "Portfolio Size",
        executive_summary[
            "portfolio_size"
        ]
    )

    c3.metric(
        "Maximum Risk",
        executive_summary[
            "maximum_enterprise_risk"
        ]
    )

    c4.metric(
        "Maximum Systemic",
        executive_summary[
            "maximum_systemic_risk"
        ]
    )

    # ==========================================================
    # ENTERPRISE RISK DISTRIBUTION
    # ==========================================================

    st.divider()

    _section("Enterprise Risk Distribution", "RISK ANALYTICS")

    _insight(
        "Enterprise risk score distribution across the full portfolio. "
        "A <strong>bimodal distribution</strong> indicates a polarised portfolio with concentrated pockets of "
        "high-risk and low-risk accounts, requiring targeted credit management rather than "
        "blunt portfolio-level policy adjustments. Use for IFRS 9 staging boundary calibration.",
        kind="warning",
        eyebrow="Report Generator · Enterprise Distribution"
    )

    fig = px.histogram(

        portfolio,

        x="enterprise_risk_score",

        nbins=30,

        title="Enterprise Risk Score Distribution",

        color_discrete_sequence=["#c9a84c"]
    )

    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(9,20,39,0.7)", width=0.8),
            opacity=0.82
        ),
        hovertemplate="Risk Score: %{x:.2f}<br>Count: %{y}<extra></extra>"
    )

    fig.update_xaxes(
        **_AXIS_STYLE,
        title_text="Enterprise Risk Score",
        title_font=dict(size=10, color="#627898")
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

    # ==========================================================
    # RISK VS SYSTEMIC ANALYSIS
    # ==========================================================

    st.divider()

    _section("Enterprise vs Systemic Risk", "BIVARIATE RISK ANALYSIS")

    _insight(
        "Bivariate scatter mapping enterprise risk scores against systemic risk exposure. "
        "Accounts in the <strong>upper-right quadrant</strong> (high enterprise + high systemic) represent "
        "dual-trigger risks requiring coordinated credit and macro stress intervention. "
        "These are primary candidates for name-level stress testing and capital surcharges.",
        kind="critical",
        eyebrow="Report Generator · Risk Quadrant Analysis"
    )

    fig = px.scatter(

        portfolio,

        x="enterprise_risk_score",

        y="systemic_risk_score",

        hover_data=[
            "borrower_id"
        ],

        title="Enterprise Risk vs Systemic Risk — Quadrant Map",

        color_discrete_sequence=["#4db8ff"]
    )

    fig.update_traces(
        marker=dict(
            size=7,
            opacity=0.72,
            line=dict(color="rgba(9,20,39,0.5)", width=0.8)
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Enterprise Risk: %{x:.2f}<br>"
            "Systemic Risk: %{y:.2f}<extra></extra>"
        )
    )

    fig.update_xaxes(
        **_AXIS_STYLE,
        title_text="Enterprise Risk Score",
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

    # ==========================================================
    # GOVERNANCE INTELLIGENCE CENTER
    # ==========================================================

    st.divider()

    _section("Governance Intelligence", "GOVERNANCE · COMPLIANCE")

    _insight(
        "Governance intelligence reflects the current portfolio's compliance status against "
        "institutional policy thresholds. <strong>Board priority classification</strong> drives "
        "the agenda position for risk items at the next Board Risk Committee meeting. "
        "Recommended actions are generated by the institutional report engine and require formal acknowledgement.",
        kind="warning",
        eyebrow="Report Generator · Governance Status"
    )

    governance_status = (
        governance_summary[
            "governance_status"
        ]
    )

    board_priority = (
        governance_summary[
            "board_priority"
        ]
    )

    recommended_action = (
        governance_summary[
            "recommended_action"
        ]
    )

    if crisis_reporting:
        governance_status = "CRISIS GOVERNANCE CONDITIONS"
        board_priority = "CRITICAL BOARD PRIORITY"
        recommended_action = strategic_recommendation

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Governance Status",
            governance_status
        )

    with c2:

        st.metric(
            "Board Priority",
            board_priority
        )

    if (
        "CRITICAL"
        in governance_status
    ):

        st.error(
            recommended_action
        )

    elif (
        "HIGH"
        in governance_status
    ):

        st.warning(
            recommended_action
        )

    else:

        st.success(
            recommended_action
        )

    # ==========================================================
    # REGIME & ESCALATION CENTER
    # ==========================================================

    st.divider()

    _section("Regime Intelligence Center", "MACRO · ESCALATION")

    _insight(
        "Macro regime classification and executive escalation status are the two primary "
        "board-level risk positioning signals. <strong>Regime classification</strong> anchors "
        "the strategic risk narrative for the reporting period. "
        "Executive escalation level determines the minimum seniority of executive sponsor "
        "required to formally acknowledge the risk position.",
        kind="gold",
        eyebrow="Report Generator · Regime & Escalation"
    )

    c1, c2 = st.columns(2)

    c1.metric(
        "Regime Classification",
        regime_classification
    )

    c2.metric(
        "Executive Escalation",
        executive_escalation
    )

    # ==========================================================
    # GOVERNANCE SUMMARY TABLE
    # ==========================================================

    st.divider()

    _section("Governance Summary", "GOVERNANCE REGISTER")

    _insight(
        "Formal governance summary table for inclusion in Board Risk Committee packs. "
        "The three governance dimensions — status, priority, and recommended action — "
        "constitute the <strong>minimum disclosure set</strong> required under internal model "
        "governance policy and external regulatory reporting frameworks.",
        kind="",
        eyebrow="Report Generator · Governance Register"
    )

    governance_df = pd.DataFrame({

        "Metric": [

            "Governance Status",

            "Board Priority",

            "Recommended Action"
        ],

        "Value": [

            governance_status,

            board_priority,

            recommended_action
        ]
    })

    st.dataframe(
        governance_df,
        width="stretch"
    )

    # ==========================================================
    # ENTERPRISE METRICS TABLE
    # ==========================================================

    st.divider()

    _section("Enterprise Metrics", "FULL METRICS REGISTER")

    _insight(
        "Complete enterprise metrics register generated by the institutional report engine. "
        "These metrics form the <strong>quantitative backbone</strong> of the board report "
        "and feed directly into the PDF report generation pipeline. "
        "All values are computed at report generation time and are point-in-time measurements.",
        kind="positive",
        eyebrow="Report Generator · Enterprise Metrics"
    )

    metrics_df = pd.DataFrame(

        metrics.items(),

        columns=[
            "Metric",
            "Value"
        ]
    )

    st.dataframe(
        metrics_df,
        width="stretch"
    )

    # ==========================================================
    # AI NARRATIVE INTELLIGENCE
    # ==========================================================

    st.divider()

    _section("AI Narrative Intelligence", "BOARD NARRATIVES")

    _insight(
        "AI-generated executive narratives provide board-ready risk commentary across five "
        "critical dimensions: enterprise risk, systemic risk, capital adequacy, macro regime, "
        "and executive escalation. These narratives are produced by the KRONOS Report Generator "
        "and are designed for direct inclusion in <strong>board pack risk sections</strong>. "
        "Expand each section to review the narrative before PDF export.",
        kind="gold",
        eyebrow="Report Generator · AI Narrative Suite"
    )

    with st.expander(
        "Enterprise Risk Narrative",
        expanded=True
    ):

        st.write(

            narrative_results[
                "enterprise_risk_narrative"
            ]

        )

    with st.expander(
        "Systemic Risk Narrative"
    ):

        st.write(

            narrative_results[
                "systemic_risk_narrative"
            ]

        )

    with st.expander(
        "Capital Adequacy Narrative"
    ):

        st.write(

            narrative_results[
                "capital_adequacy_narrative"
            ]

        )

    with st.expander(
        "Macro Regime Narrative"
    ):

        st.write(

            narrative_results[
                "macro_regime_narrative"
            ]

        )

    with st.expander(
        "Executive Escalation Narrative"
    ):

        st.write(

            narrative_results[
                "executive_escalation_narrative"
            ]

        )

    # ==========================================================
    # STRATEGIC RECOMMENDATION CENTER
    # ==========================================================

    st.divider()

    _section("Strategic Recommendation", "BOARD STRATEGY")

    _insight(
        "The strategic recommendation below synthesises all portfolio intelligence, governance "
        "findings, and macro regime signals into a <strong>single board-level action directive</strong>. "
        "This recommendation should be formally reviewed by the Chief Risk Officer and presented "
        "to the Board Risk Committee as the primary agenda item at the next scheduled meeting.",
        kind="positive",
        eyebrow="Report Generator · Strategic Directive"
    )

    if crisis_reporting:
        st.error(strategic_recommendation)
    elif "HIGH" in str(governance_status).upper():
        st.warning(strategic_recommendation)
    else:
        st.success(strategic_recommendation)

    # ==========================================================
    # AI EXPLAINABILITY COMMENTARY
    # ==========================================================

    st.divider()

    _section("AI Explainability Commentary", "MODEL TRANSPARENCY")

    _insight(
        "AI explainability commentary provides model transparency disclosure for board-level "
        "audiences. This section satisfies the <strong>SR 11-7 model transparency requirement</strong> "
        "for board packs and supports the institution's responsible AI governance framework. "
        "Include verbatim in the Model Risk section of the board report.",
        kind="",
        eyebrow="Report Generator · Explainability Disclosure"
    )

    st.info(

        narrative_results[
            "ai_explainability_narrative"
        ]

    )

    # ==========================================================
    # BOARD EXECUTIVE SUMMARY
    # ==========================================================

    st.divider()

    _section("Board Executive Summary", "BOARD PACK · COVER SUMMARY")

    _insight(
        "Board-level executive summary for the cover page of the risk report. "
        "This summary is calibrated for a <strong>non-technical board audience</strong> and presents "
        "the key risk findings in plain language with clear action directives. "
        "Review with the Company Secretary before including in the final board pack.",
        kind="warning",
        eyebrow="Report Generator · Board Cover Summary"
    )

    board_summary = narrative_results[
        "board_level_summary"
    ]
    if crisis_reporting:
        board_summary = (
            f"{regime_classification} is active with {executive_escalation}. "
            f"{strategic_recommendation} Enterprise Risk is "
            f"{executive_summary['enterprise_risk_score']} and Systemic Risk is "
            f"{executive_summary['systemic_risk_score']}; board attention should remain "
            "focused on crisis governance, exposure reduction, and formal executive accountability."
        )

    st.warning(board_summary)

    # ==========================================================
    # REPORT METADATA
    # ==========================================================

    st.divider()

    _section("Report Metadata", "AUDIT TRAIL")

    _insight(
        "Report metadata provides the audit trail for this reporting cycle. "
        "Generation timestamp, narrative timestamp, regime classification, and escalation level "
        "are all captured at report generation time and must be preserved in the "
        "<strong>document management system</strong> for regulatory examination purposes.",
        kind="",
        eyebrow="Report Generator · Metadata Registry"
    )

    metadata_df = pd.DataFrame({

        "Field": [

            "Report Generated",

            "Narrative Timestamp",

            "Regime Classification",

            "Executive Escalation"
        ],

        "Value": [

            executive_summary[
                "report_generation_time"
            ],

            narrative_results[
                "report_timestamp"
            ],

            executive_summary[
                "regime_classification"
            ],

            executive_escalation
        ]
    })

    st.dataframe(
        metadata_df,
        width="stretch"
    )

    # ==========================================================
    # PDF REPORT CENTER
    # ==========================================================

    st.divider()

    _section("Enterprise PDF Report", "SECURE PDF DISTRIBUTION")

    _insight(
        "The institutional PDF report has been generated by the KRONOS Report Generator "
        "and is available for secure download below. This PDF constitutes the "
        "<strong>formal board reporting artefact</strong> for the current reporting cycle. "
        "Distribution is restricted to Board members, the CRO, CFO, and designated risk officers. "
        "Server-side storage remains internal; the executive view exposes only the secure download control.",
        kind="gold",
        eyebrow="Report Generator · PDF Report Center"
    )

    # ==========================================================
    # PDF DOWNLOAD
    # ==========================================================

    st.markdown(
        """
        <div class="export-wrapper">
            <div class="governance-panel-title">ENTERPRISE PDF REPORT — SECURE DOWNLOAD</div>
            <div class="export-description">
                Download the institutional-grade PDF report for board pack inclusion and
                regulatory submission. This document is generated by the KRONOS Report Generator
                and contains the complete executive summary, governance findings, AI narratives,
                and strategic recommendation for the current reporting cycle.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Generate / Refresh Enterprise PDF Report"
    ):

        pdf_report_package = cached_generate_report(
            portfolio,
            live_context,
            True
        )
        pdf_report_path = (
            pdf_report_package.get(
                "pdf_report_path"
            )
            or pdf_report_path
        )

    if os.path.exists(
        pdf_report_path
    ):

        with open(
            pdf_report_path,
            "rb"
        ) as pdf_file:

            st.download_button(

                label=
                    "Download Enterprise PDF Report",

                data=
                    pdf_file,

                file_name=
                    "KRONOS_Enterprise_Report.pdf",

                mime=
                    "application/pdf"
            )

    else:

        st.error(
            "PDF report file not found."
        )

# =============================================================================
# END OF FILE
# =============================================================================

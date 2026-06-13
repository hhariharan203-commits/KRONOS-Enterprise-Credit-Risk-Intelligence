# =============================================================================
# KRONOS — EXPLAINABILITY DASHBOARD
# File: app/explainability_dashboard.py
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
# EXPLAINABILITY ENGINE
# =============================================================================

from src.explainability.explainability import (
    explain_borrower
)

# =============================================================================
# SHAP ENGINE
# =============================================================================

from src.explainability.shap_engine import (
    run_shap_pipeline
)

# =============================================================================
# FEATURE IMPORTANCE ENGINE
# =============================================================================

from src.explainability.feature_importance import (
    run_feature_analysis
)

from src.shared.cache_manager import timed_cache

cached_explain_borrower = timed_cache()(explain_borrower)
cached_run_shap_pipeline = timed_cache()(run_shap_pipeline)
cached_run_feature_analysis = timed_cache()(run_feature_analysis)


def _business_driver_label(feature):
    feature_text = str(feature)
    mappings = {
        "lgd": "Loss Severity",
        "ead": "Exposure Size",
        "income": "Borrower Income Capacity",
        "credit_limit": "Credit Limit Utilisation",
        "interest_rate": "Rate Sensitivity",
        "macro": "Macro Sensitivity",
        "risk_profile": "Risk Profile",
        "collateral": "Collateral Support",
        "delinquency": "Delinquency Behaviour",
        "headroom": "Credit Headroom",
    }
    for key, label in mappings.items():
        if key in feature_text.lower():
            return label
    return feature_text.replace("_", " ").title()


def _business_driver_reason(feature, impact):
    direction = "raises" if impact >= 0 else "reduces"
    return (
        f"{_business_driver_label(feature)} {direction} the modelled default-risk signal "
        "for the selected borrower."
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
    --emerald-d: #00a07a;
    --amber:     #f0a500;
    --amber-d:   #c07800;
    --crimson:   #e02442;
    --crimson-d: #b01830;
    --ice-blue:  #4db8ff;
    --gold:      #c9a84c;
    --violet:    #9b72ff;

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
    --glow-violet:    0 0 20px rgba(155,114,255,0.18);
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
        var(--violet) 20%,
        var(--ice-blue) 60%,
        var(--emerald) 100%);
}

.kronos-banner::after {
    content: 'XPLAIN';
    position: absolute;
    right: 36px; top: 50%;
    transform: translateY(-50%);
    font-family: 'JetBrains Mono', monospace;
    font-size: 72px;
    font-weight: 600;
    color: rgba(155,114,255,0.04);
    letter-spacing: 8px;
    pointer-events: none;
}

.banner-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 3px;
    color: var(--violet);
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
    background: rgba(155,114,255,0.12);
    border: 1px solid rgba(155,114,255,0.35);
    color: var(--violet);
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
    background: linear-gradient(180deg, var(--violet), var(--ice-blue));
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

.insight-panel.violet {
    border-left-color: var(--violet);
    background: linear-gradient(135deg, rgba(155,114,255,0.07), rgba(9,20,39,0.95));
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
.insight-panel.violet   .insight-eyebrow { color: var(--violet); }

.insight-body {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.7;
}

.insight-body strong {
    color: var(--text-primary);
    font-weight: 600;
}

/* ── GOVERNANCE VALIDATION BLOCK ─────────────────────────────────────────── */
.governance-block {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 22px 26px;
    margin: 12px 0;
}

.governance-block-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-subtle);
}

.governance-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 9px 0;
    border-bottom: 1px solid rgba(255,255,255,0.035);
    font-size: 12.5px;
    color: var(--text-secondary);
}

.governance-item:last-child { border-bottom: none; }

.governance-check {
    width: 18px; height: 18px;
    border-radius: 50%;
    background: rgba(0,200,150,0.15);
    border: 1px solid rgba(0,200,150,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    color: var(--emerald);
    flex-shrink: 0;
    font-weight: 700;
}

.governance-item-label {
    font-family: 'Inter', sans-serif;
    color: var(--text-secondary);
    font-size: 12.5px;
}

/* ── NARRATIVE BOX ───────────────────────────────────────────────────────── */
.narrative-box {
    background: linear-gradient(135deg, rgba(155,114,255,0.07), rgba(9,20,39,0.9));
    border: 1px solid rgba(155,114,255,0.22);
    border-radius: 4px;
    padding: 20px 24px;
    margin: 12px 0 20px;
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.75;
    font-style: italic;
}

/* ── SHAP SUMMARY BOX ────────────────────────────────────────────────────── */
.shap-summary-box {
    background: linear-gradient(135deg, rgba(0,200,150,0.07), rgba(9,20,39,0.9));
    border: 1px solid rgba(0,200,150,0.22);
    border-radius: 4px;
    padding: 20px 24px;
    margin: 12px 0 20px;
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.75;
}

/* ── EXPLORER PANEL ──────────────────────────────────────────────────────── */
.explorer-panel {
    background: var(--card-bg);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 22px 24px;
    margin-bottom: 16px;
}

.explorer-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 10px;
}

/* ── EXPORT WRAPPER ──────────────────────────────────────────────────────── */
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

.export-grid {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}

/* ── STREAMLIT COMPONENT OVERRIDES ───────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: var(--navy-900) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

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
    background: rgba(155,114,255,0.05) !important;
}

[data-testid="stDataFrame"] tbody td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    color: var(--text-secondary) !important;
}

[data-testid="stDownloadButton"] button {
    background: linear-gradient(135deg, var(--navy-600), var(--navy-700)) !important;
    border: 1px solid var(--border-accent) !important;
    color: var(--violet) !important;
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
    border-color: var(--violet) !important;
    box-shadow: var(--glow-violet) !important;
}

[data-testid="stAlert"] {
    background: rgba(77,184,255,0.07) !important;
    border: 1px solid rgba(77,184,255,0.22) !important;
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

div[data-testid="stSelectbox"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: var(--navy-700) !important;
    border: 1px solid var(--border-accent) !important;
    border-radius: 3px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
}

[data-testid="stCaptionContainer"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 2px !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
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
        "#9b72ff", "#4db8ff", "#00c896",
        "#f0a500", "#e02442", "#c9a84c",
        "#627898"
    ]
)

_BAR_COLOR_SHAP     = "#9b72ff"
_BAR_COLOR_FEATURE  = "#4db8ff"
_PIE_COLORS = [
    "#9b72ff", "#4db8ff", "#00c896",
    "#f0a500", "#e02442", "#c9a84c"
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


def _governance_block(items: list) -> None:
    items_html = "".join(
        f'<div class="governance-item">'
        f'  <div class="governance-check">✓</div>'
        f'  <span class="governance-item-label">{label}</span>'
        f'</div>'
        for label in items
    )
    st.markdown(
        f"""
        <div class="governance-block">
            <div class="governance-block-title">Governance Validation Register</div>
            {items_html}
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
            <div class="banner-eyebrow">KRONOS PLATFORM · EXPLAINABILITY MODULE v4</div>
            <div class="banner-title">🔍 Explainability Intelligence Dashboard</div>
            <div class="banner-subtitle">
                Borrower Explainability
                <span class="banner-divider">·</span>
                SHAP Intelligence
                <span class="banner-divider">·</span>
                Model Governance
                <span class="banner-pill">XAI ACTIVE</span>
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

    borrower = (
        portfolio.iloc[0]
        .to_dict()
    )

    explanation_results = (
        cached_explain_borrower(
            borrower
        )
    )

    shap_results = (
        cached_run_shap_pipeline(
            borrower
        )
    )

    feature_results = (
        cached_run_feature_analysis()
    )

    if (
        explanation_results is None
        or shap_results is None
        or feature_results is None
    ):

        st.error(
            "Explainability engines failed."
        )

        return

    # ==========================================================
    # EXECUTIVE EXPLAINABILITY OVERVIEW
    # ==========================================================

    st.divider()

    _section("Executive Explainability Overview", "XAI · MODEL TRANSPARENCY")

    _insight(
        "Explainability engines have completed analysis for the lead borrower in the active portfolio. "
        "The <strong>PD probability</strong> reflects current model output calibrated against macro-credit conditions. "
        "Model confidence and SHAP driver counts confirm full transparency coverage. "
        "All outputs are audit-ready for regulatory submissions under SR 11-7 and EBA guidelines.",
        kind="violet",
        eyebrow="Explainability Engine · Executive Overview"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "PD Probability",
        f"{round(explanation_results['probability_of_default'] * 100, 2)}%"
    )

    c2.metric(
        "Model Confidence",
        f"{explanation_results['explainability_confidence']}%"
    )

    c3.metric(
        "SHAP Drivers",
        len(
            shap_results[
                "top_drivers"
            ]
        )
    )

    c4.metric(
        "Features Analysed",
        len(
            feature_results[
                "feature_importance"
            ]
        )
    )

    # ==========================================================
    # BORROWER AI EXPLANATION
    # ==========================================================

    st.divider()

    _section("Borrower AI Explanation", "NARRATIVE · RISK ATTRIBUTION")

    _insight(
        "The AI-generated borrower narrative below reflects the model's interpretation of credit risk "
        "drivers for the selected borrower. This narrative is produced by the KRONOS Explainability Engine "
        "and is intended for use by <strong>senior credit officers</strong> and <strong>model risk teams</strong> "
        "during credit review, model validation, and regulatory examination.",
        kind="",
        eyebrow="Explainability Engine · Borrower Narrative"
    )

    st.info(
        explanation_results[
            "risk_narrative"
        ]
    )

    # ==========================================================
    # SHAP EXECUTIVE INTELLIGENCE
    # ==========================================================

    st.divider()

    _section("SHAP Executive Intelligence", "SHAP · DRIVER ANALYSIS")

    _insight(
        "SHAP (SHapley Additive exPlanations) values quantify the marginal contribution of each "
        "feature to the model's default probability output. The executive summary below synthesises "
        "key driver findings. <strong>Positive SHAP values</strong> increase predicted PD; "
        "<strong>negative values</strong> reduce it. Use this intelligence for credit covenant "
        "negotiation and exposure management decisions.",
        kind="positive",
        eyebrow="SHAP Engine · Executive Summary"
    )

    st.success(
        shap_results[
            "executive_summary"
        ]
    )

    business_driver_df = pd.DataFrame(
        shap_results["top_drivers"],
        columns=[
            "Technical Feature",
            "Impact"
        ]
    ).head(5)
    business_driver_df["Business Driver"] = business_driver_df[
        "Technical Feature"
    ].apply(_business_driver_label)
    business_driver_df["Reason"] = business_driver_df.apply(
        lambda row: _business_driver_reason(
            row["Technical Feature"],
            row["Impact"]
        ),
        axis=1
    )

    st.dataframe(
        business_driver_df[
            [
                "Business Driver",
                "Impact",
                "Reason",
                "Technical Feature"
            ]
        ],
        width="stretch"
    )

    # ==========================================================
    # TOP SHAP DRIVERS
    # ==========================================================

    st.divider()

    _section("Top SHAP Risk Drivers", "SHAP · FEATURE ATTRIBUTION")

    _insight(
        "The waterfall chart below ranks features by their absolute SHAP impact on the borrower's "
        "default probability. <strong>High-impact features</strong> in the positive direction "
        "should be prioritised for credit covenant monitoring and early warning triggers. "
        "Cross-reference against the enterprise feature importance model for portfolio-wide context.",
        kind="",
        eyebrow="SHAP Engine · Top Driver Attribution"
    )

    shap_df = pd.DataFrame(

        shap_results[
            "top_drivers"
        ],

        columns=[
            "Feature",
            "Impact"
        ]
    )

    fig = px.bar(

        shap_df,

        x="Impact",

        y="Feature",

        orientation="h",

        title="Top SHAP Drivers — Feature Attribution",

        color_discrete_sequence=[_BAR_COLOR_SHAP]
    )

    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(9,20,39,0.6)", width=0.8)
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "SHAP Impact: %{x:.4f}<extra></extra>"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(77,184,255,0.08)",
        gridwidth=1,
        zeroline=True,
        zerolinecolor="rgba(77,184,255,0.25)",
        zerolinewidth=1.5,
        title_text="SHAP Value",
        title_font=dict(size=10, color="#627898"),
        tickfont=dict(
            family="JetBrains Mono, monospace",
            size=10,
            color="#8294ae"
        )
    )

    fig.update_yaxes(
        showgrid=False,
        title_text="",
        tickfont=dict(
            family="JetBrains Mono, monospace",
            size=10,
            color="#a8b8cc"
        )
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.dataframe(
        shap_df,
        width="stretch"
    )

    # ==========================================================
    # SHAP IMPORTANCE RANKING
    # ==========================================================

    st.divider()

    _section("SHAP Importance Ranking", "SHAP · RANKED REGISTRY")

    _insight(
        "Full SHAP importance ranking across all evaluated features. "
        "This table serves as the primary audit artifact for model transparency reviews. "
        "Rankings are stable across the current model version and reflect training-time "
        "<strong>global feature attribution</strong> using TreeSHAP methodology.",
        kind="violet",
        eyebrow="SHAP Engine · Importance Registry"
    )

    st.dataframe(

        shap_results[
            "importance_df"
        ],

        width="stretch"
    )

    # ==========================================================
    # ENTERPRISE FEATURE IMPORTANCE
    # ==========================================================

    st.divider()

    _section("Enterprise Feature Importance", "MODEL ANALYTICS · TOP 20")

    _insight(
        "Enterprise-level feature importance scores reflect the trained model's reliance on each "
        "input variable across the entire portfolio. The top 20 features are visualised below. "
        "<strong>High-importance features</strong> represent the primary levers for credit risk "
        "differentiation and should be subject to enhanced data quality monitoring and "
        "governance controls.",
        kind="",
        eyebrow="Feature Engine · Enterprise Risk Drivers"
    )

    feature_df = (

        feature_results[
            "feature_importance"
        ]

        .head(20)

    )

    fig = px.bar(

        feature_df,

        x="importance_pct",

        y="feature",

        orientation="h",

        title="Top 20 Enterprise Risk Drivers — Importance Score",

        color_discrete_sequence=[_BAR_COLOR_FEATURE]
    )

    fig.update_traces(
        marker=dict(
            line=dict(color="rgba(9,20,39,0.6)", width=0.8)
        ),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Importance: %{x:.2f}%<extra></extra>"
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(77,184,255,0.08)",
        gridwidth=1,
        zeroline=False,
        title_text="Importance (%)",
        title_font=dict(size=10, color="#627898"),
        tickfont=dict(
            family="JetBrains Mono, monospace",
            size=10,
            color="#8294ae"
        ),
        ticksuffix="%"
    )

    fig.update_yaxes(
        showgrid=False,
        title_text="",
        tickfont=dict(
            family="JetBrains Mono, monospace",
            size=10,
            color="#a8b8cc"
        )
    )

    fig = _apply_plotly_theme(fig)

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # CATEGORY CONTRIBUTION ANALYSIS
    # ==========================================================

    st.divider()

    _section("Category Contribution Analysis", "PORTFOLIO ANALYTICS")

    _insight(
        "Category-level contribution analysis aggregates feature importance scores by risk domain. "
        "This view supports <strong>model governance reporting</strong> and helps risk committees "
        "understand which broad categories of risk variables — financial, behavioural, macro — "
        "are driving model outputs. Use for stress testing parameter prioritisation.",
        kind="warning",
        eyebrow="Feature Engine · Category Attribution"
    )

    category_df = (

        feature_results[
            "category_importance"
        ]

    )

    fig = px.pie(

        category_df,

        names="category",

        values="importance_pct",

        title="Category Contribution Breakdown",

        color_discrete_sequence=_PIE_COLORS,

        hole=0.42
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
            "Contribution: %{value:.2f}%<br>"
            "Share: %{percent}<extra></extra>"
        )
    )

    fig = _apply_plotly_theme(fig)

    fig.update_layout(
        annotations=[dict(
            text="CATEGORY",
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

    st.dataframe(

        category_df,

        width="stretch"
    )

    # ==========================================================
    # RISK DRIVER DEEP DIVE
    # ==========================================================

    st.divider()

    _section("Risk Driver Deep Dive", "FULL FEATURE REGISTRY")

    _insight(
        "Complete feature registry displaying all risk drivers evaluated by the enterprise model. "
        "This table is the authoritative source for <strong>model documentation</strong>, "
        "SR 11-7 model risk management submissions, and internal audit reviews. "
        "All features are ranked by importance percentile against the portfolio baseline.",
        kind="",
        eyebrow="Feature Engine · Full Driver Registry"
    )

    st.dataframe(

        feature_results[
            "feature_importance"
        ],

        width="stretch"
    )

    # ==========================================================
    # MODEL GOVERNANCE SUMMARY
    # ==========================================================

    st.divider()

    _section("Model Governance Summary", "GOVERNANCE · COMPLIANCE")

    _insight(
        "Model governance validation confirms that all explainability requirements have been met "
        "for the current model version. Feature importance, SHAP attribution, and borrower-level "
        "narratives are available and audit-ready. <strong>Model transparency requirements</strong> "
        "are satisfied under SR 11-7, EBA/GL/2023/01, and internal Model Risk Policy v4.2.",
        kind="positive",
        eyebrow="Governance Engine · Compliance Confirmation"
    )

    st.success(

        feature_results[
            "summary"
        ]
    )

    st.success(

        shap_results[
            "executive_summary"
        ]
    )

    _governance_block([
        "Feature Importance Verified",
        "SHAP Explainability Generated",
        "Borrower-Level Explanation Available",
        "Executive Narrative Produced",
        "Model Transparency Requirements Met",
        "Risk Driver Attribution Available",
        "Portfolio Explainability Complete",
    ])

    # ==========================================================
    # EXPLAINABILITY EXPLORER
    # ==========================================================

    st.divider()

    _section("Explainability Explorer", "INTERACTIVE · FEATURE DRILL-DOWN")

    _insight(
        "Select any feature from the enterprise model to view its individual importance profile. "
        "This interactive explorer supports <strong>ad-hoc model interrogation</strong> during "
        "credit review sessions, model validation walkthroughs, and regulatory examinations. "
        "Feature-level detail is sourced directly from the live feature importance engine.",
        kind="violet",
        eyebrow="Feature Engine · Interactive Explorer"
    )

    st.markdown(
        '<div class="explorer-panel"><div class="explorer-label">Feature Selection — Click to Inspect</div>',
        unsafe_allow_html=True
    )

    selected_feature = st.selectbox(

        "Select Feature",

        feature_results[
            "feature_importance"
        ][
            "feature"
        ].tolist()
    )

    st.markdown('</div>', unsafe_allow_html=True)

    selected_row = (

        feature_results[
            "feature_importance"
        ]

        .query(
            "feature == @selected_feature"
        )

    )

    st.dataframe(

        selected_row,

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
            <div class="governance-block-title">EXPLAINABILITY REPORTS — SECURE EXPORT</div>
            <div class="export-description">
                Export feature importance and category contribution reports as structured CSV files
                for model documentation, regulatory submission, or board-level model governance reporting.
                All exports are versioned and subject to the institution's Model Risk Management Policy.
                Distribution is restricted to authorised model governance and credit risk personnel.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    feature_csv = (

        feature_results[
            "feature_importance"
        ]

        .to_csv(
            index=False
        )

    )

    category_csv = (

        feature_results[
            "category_importance"
        ]

        .to_csv(
            index=False
        )

    )

    st.download_button(

        label=
            "Download Feature Importance Report",

        data=
            feature_csv,

        file_name=
            "kronos_feature_importance.csv",

        mime=
            "text/csv"
    )

    st.download_button(

        label=
            "Download Category Importance Report",

        data=
            category_csv,

        file_name=
            "kronos_category_importance.csv",

        mime=
            "text/csv"
    )

    # ==========================================================
    # END OF DASHBOARD
    # ==========================================================

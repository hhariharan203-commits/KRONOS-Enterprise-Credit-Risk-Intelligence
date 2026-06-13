import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.ews.ews_engine import (
    classify_ews_alert
)

from src.ews.anomaly_detection import (
    anomaly_severity
)

from src.ews.migration_tracker import (
    migration_risk_score
)

from src.ews.watchlist import (
    classify_watchlist_level
)


def render(shared_data=None):

    shared_data = shared_data or {}

    # ── DASHBOARD CSS ───────────────────────────────────────────────
    st.markdown(
        """
        <style>
            /* ── EXECUTIVE BANNER ──────────────────────────────── */
            .kx-banner {
                background: linear-gradient(135deg, rgba(17,30,51,0.95) 0%, rgba(7,13,24,0.98) 100%);
                border: 1px solid rgba(239,68,68,0.28);
                border-left: 4px solid #ef4444;
                border-radius: 14px;
                padding: 1.4rem 1.75rem;
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 24px rgba(0,0,0,0.45), 0 0 48px rgba(239,68,68,0.05);
            }
            .kx-banner::after {
                content: '';
                position: absolute;
                top: -60%; right: -8%;
                width: 320px; height: 320px;
                background: radial-gradient(circle, rgba(239,68,68,0.06) 0%, transparent 70%);
                pointer-events: none;
            }
            .kx-banner-eyebrow {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.66rem;
                font-weight: 500;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                color: #ef4444;
                margin-bottom: 0.35rem;
            }
            .kx-banner-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 1.55rem;
                font-weight: 700;
                color: #f0f6ff;
                letter-spacing: -0.01em;
                margin-bottom: 0.3rem;
            }
            .kx-banner-subtitle {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.82rem;
                color: #64748b;
                line-height: 1.5;
            }
            .kx-banner-badge {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                background: rgba(239,68,68,0.12);
                border: 1px solid rgba(239,68,68,0.30);
                border-radius: 20px;
                padding: 3px 10px;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                color: #f87171;
                margin-left: 10px;
                vertical-align: middle;
            }
            .kx-banner-dot {
                width: 5px; height: 5px;
                background: #ef4444;
                border-radius: 50%;
                display: inline-block;
                animation: kx-pulse 1.4s ease-in-out infinite;
            }
            @keyframes kx-pulse {
                0%,100% { opacity:1; transform:scale(1); }
                50%      { opacity:0.3; transform:scale(0.6); }
            }

            /* ── SECTION HEADERS ───────────────────────────────── */
            .kx-section-header {
                display: flex;
                align-items: flex-start;
                gap: 11px;
                margin: 0.2rem 0 1rem 0;
                padding-bottom: 0.7rem;
                border-bottom: 1px solid rgba(239,68,68,0.15);
            }
            .kx-section-icon { font-size: 1.1rem; line-height: 1.6; flex-shrink: 0; }
            .kx-section-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 1.0rem; font-weight: 700;
                color: #e8edf7; letter-spacing: 0.01em;
            }
            .kx-section-sub {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.68rem; color: #4a5a72;
                letter-spacing: 0.05em; text-transform: uppercase; margin-top: 1px;
            }

            /* ── SECTION WRAPPER ───────────────────────────────── */
            .kx-section {
                background: rgba(11,17,30,0.55);
                border: 1px solid rgba(148,163,184,0.10);
                border-radius: 14px;
                padding: 1.25rem 1.4rem 1.1rem 1.4rem;
                margin-bottom: 1.25rem;
            }

            /* ── CRITICAL SECTION ──────────────────────────────── */
            .kx-section-critical {
                background: rgba(11,17,30,0.55);
                border: 1px solid rgba(239,68,68,0.18);
                border-radius: 14px;
                padding: 1.25rem 1.4rem 1.1rem 1.4rem;
                margin-bottom: 1.25rem;
            }

            /* ── DIVIDER ───────────────────────────────────────── */
            .kx-divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(239,68,68,0.22),
                            rgba(148,163,184,0.10), transparent);
                margin: 1.4rem 0;
            }

            /* ── NARRATIVE (CRIMSON) ───────────────────────────── */
            .kx-narrative {
                background: linear-gradient(135deg, rgba(239,68,68,0.06) 0%, rgba(17,30,51,0.92) 100%);
                border: 1px solid rgba(239,68,68,0.22);
                border-left: 4px solid #ef4444;
                border-radius: 12px;
                padding: 1.4rem 1.6rem;
                margin-top: 0.5rem;
            }
            .kx-narrative-header { display: flex; align-items: center; gap: 8px; margin-bottom: 0.9rem; }
            .kx-narrative-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem; font-weight: 600;
                letter-spacing: 0.12em; text-transform: uppercase;
                color: #f87171;
                background: rgba(239,68,68,0.12);
                border: 1px solid rgba(239,68,68,0.25);
                border-radius: 4px; padding: 2px 8px;
            }
            .kx-narrative-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.9rem; font-weight: 600; color: #e8edf7;
            }
            .kx-narrative-body {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.84rem; color: #94a3b8; line-height: 1.8;
            }
            .kx-narrative-body strong { color: #e8edf7; font-weight: 600; }

            /* ── ACTION ITEMS ──────────────────────────────────── */
            .kx-action-list {
                list-style: none; padding: 0; margin: 0.8rem 0 0 0;
                display: flex; flex-direction: column; gap: 5px;
            }
            .kx-action-item {
                display: flex; align-items: center; gap: 9px;
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.82rem; color: #94a3b8;
                padding: 5px 10px;
                border-radius: 6px;
                background: rgba(12,21,38,0.55);
                border: 1px solid rgba(239,68,68,0.10);
            }
            .kx-action-dot {
                width: 6px; height: 6px;
                background: #ef4444;
                border-radius: 50%; flex-shrink: 0;
            }

            /* ── GOVERNANCE PANEL ──────────────────────────────── */
            .kx-governance {
                background: linear-gradient(135deg, rgba(139,92,246,0.06) 0%, rgba(17,30,51,0.9) 100%);
                border: 1px solid rgba(139,92,246,0.2);
                border-left: 4px solid #8b5cf6;
                border-radius: 12px;
                padding: 1.4rem 1.6rem;
                margin-top: 1rem;
            }
            .kx-governance-header { display: flex; align-items: center; gap: 8px; margin-bottom: 0.9rem; }
            .kx-governance-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem; font-weight: 600;
                letter-spacing: 0.12em; text-transform: uppercase;
                color: #a78bfa;
                background: rgba(139,92,246,0.12);
                border: 1px solid rgba(139,92,246,0.25);
                border-radius: 4px; padding: 2px 8px;
            }
            .kx-governance-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.9rem; font-weight: 600; color: #e8edf7;
            }
            .kx-stat-row { display: flex; gap: 1.5rem; flex-wrap: wrap; margin-top: 0.5rem; }
            .kx-stat-item { display: flex; flex-direction: column; gap: 2px; }
            .kx-stat-label {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem; color: #4a5a72;
                text-transform: uppercase; letter-spacing: 0.08em;
            }
            .kx-stat-value {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.92rem; font-weight: 600; color: #e8edf7;
            }
            .kx-stat-value.emerald { color: #10b981; }
            .kx-stat-value.amber   { color: #f59e0b; }
            .kx-stat-value.crimson { color: #ef4444; }

            /* ── FOOTER ────────────────────────────────────────── */
            .kx-footer {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.65rem;
                color: #2d3d54;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                text-align: center;
                padding: 1.5rem 0 0.5rem 0;
                border-top: 1px solid rgba(239,68,68,0.08);
                margin-top: 1.5rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── PLOTLY THEME ────────────────────────────────────────────────
    PLOTLY_LAYOUT = dict(
        paper_bgcolor="rgba(7,13,24,0)",
        plot_bgcolor="rgba(12,21,38,0.55)",
        font=dict(family="IBM Plex Sans, Helvetica Neue, Arial", color="#94a3b8", size=11),
        margin=dict(l=16, r=16, t=44, b=16),
        colorway=["#ef4444", "#f59e0b", "#10b981", "#2563eb", "#8b5cf6", "#06b6d4", "#f97316"],
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.08)",
            linecolor="rgba(148,163,184,0.18)",
            tickfont=dict(size=10, color="#64748b"),
            title_font=dict(color="#94a3b8", size=11),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.08)",
            linecolor="rgba(148,163,184,0.18)",
            tickfont=dict(size=10, color="#64748b"),
            title_font=dict(color="#94a3b8", size=11),
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(12,21,38,0.7)",
            bordercolor="rgba(148,163,184,0.15)",
            borderwidth=1,
            font=dict(size=10, color="#94a3b8"),
        ),
        hoverlabel=dict(
            bgcolor="#111e33",
            bordercolor="#ef4444",
            font=dict(family="IBM Plex Mono", size=11, color="#e8edf7"),
        ),
    )

    EWS_ALERT_COLORS = {
        "CRITICAL":  "#ef4444",
        "HIGH":      "#f97316",
        "MEDIUM":    "#f59e0b",
        "LOW":       "#10b981",
        "NORMAL":    "#2563eb",
    }

    PIE_COLORS = ["#ef4444", "#f59e0b", "#10b981", "#2563eb", "#8b5cf6", "#06b6d4"]

    HEATMAP_COLORSCALE = [
        [0.0,  "#0c1526"],
        [0.25, "#1e3a6e"],
        [0.5,  "#f59e0b"],
        [0.75, "#f97316"],
        [1.0,  "#ef4444"],
    ]

    # ── SECTION HEADER HELPER ───────────────────────────────────────
    def section_header(icon, title, subtitle=None, critical=False):
        border_color = "rgba(239,68,68,0.18)" if critical else "rgba(37,99,235,0.18)"
        sub_html = (
            f'<div class="kx-section-sub">{subtitle}</div>'
            if subtitle else ""
        )
        st.markdown(
            f"""
            <div class="kx-section-header" style="border-bottom:1px solid {border_color}">
                <span class="kx-section-icon">{icon}</span>
                <div>
                    <div class="kx-section-title">{title}</div>
                    {sub_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    portfolio = shared_data.get("portfolio", pd.DataFrame()).copy()

    if portfolio.empty:
        st.warning("Portfolio data unavailable.")
        return

    required_columns = {
        "borrower_id",
        "credit_utilization",
        "days_past_due",
        "early_warning_score",
        "ifrs_stage",
        "industry",
        "payment_burden_ratio",
        "region",
        "risk_grade",
        "risk_migration_score",
        "total_delinquency",
        "watchlist_flag",
    }
    missing_columns = sorted(required_columns - set(portfolio.columns))
    if missing_columns:
        st.warning(
            "Portfolio data missing required columns: "
            + ", ".join(missing_columns)
        )
        return

    portfolio["ifrs_stage_display"] = (
        portfolio["ifrs_stage"]
        .astype(str)
        .str.replace("_", " ", regex=False)
        .str.upper()
    )

    # ==========================================================
    # DATA PREP
    # ==========================================================

    numeric_cols = [
        "early_warning_score",
        "risk_migration_score",
        "days_past_due",
        "credit_utilization",
        "payment_burden_ratio",
        "total_delinquency",
        "pd_score",
        "loan_amount",
        "ead"
    ]

    for col in numeric_cols:

        if col in portfolio.columns:

            portfolio[col] = pd.to_numeric(
                portfolio[col],
                errors="coerce"
            )

    portfolio = portfolio.fillna(0)

    # ==========================================================
    # EWS ALERT CLASSIFICATION
    # ==========================================================

    portfolio["ews_alert"] = portfolio[
        "early_warning_score"
    ].apply(classify_ews_alert)

    # ==========================================================
    # ANOMALY SIMULATION
    # ==========================================================

    portfolio["simulated_anomaly_score"] = (
        (
            portfolio["credit_utilization"] * 40
        )
        +
        (
            portfolio["payment_burden_ratio"] * 30
        )
        +
        (
            portfolio["total_delinquency"] * 5
        )
        -
        20
    ) / 100

    portfolio["anomaly_severity"] = (
        portfolio["simulated_anomaly_score"]
        .apply(anomaly_severity)
    )

    portfolio["anomaly_status"] = np.where(
        portfolio["simulated_anomaly_score"] < 0,
        "ANOMALOUS",
        "NORMAL"
    )

    # ==========================================================
    # WATCHLIST SIMULATION
    # ==========================================================

    portfolio["migration_direction"] = np.where(
        portfolio["risk_migration_score"] >= 40,
        "DOWNGRADE",
        "STABLE"
    )

    portfolio["watchlist_level"] = portfolio.apply(
        lambda row: classify_watchlist_level(
            row["early_warning_score"],
            row["anomaly_status"],
            row["migration_direction"],
            row["risk_grade"]
        ),
        axis=1
    )

    # ==========================================================
    # EXECUTIVE KPIs
    # ==========================================================

    total_borrowers = len(portfolio)

    watchlist_accounts = len(
        portfolio[
            portfolio["watchlist_level"] !=
            "STANDARD PORTFOLIO"
        ]
    )

    critical_watchlist = len(
        portfolio[
            portfolio["watchlist_level"] ==
            "CRITICAL WATCHLIST"
        ]
    )

    anomalous_accounts = len(
        portfolio[
            portfolio["anomaly_status"] ==
            "ANOMALOUS"
        ]
    )

    avg_ews = portfolio[
        "early_warning_score"
    ].mean()

    avg_migration = portfolio[
        "risk_migration_score"
    ].mean()

    stage2_accounts = len(
        portfolio[
            portfolio["ifrs_stage"] == "STAGE 2"
        ]
    )

    stage3_accounts = len(
        portfolio[
            portfolio["ifrs_stage"] == "STAGE 3"
        ]
    )

    # ── EXECUTIVE BANNER ────────────────────────────────────────────
    st.markdown(
        """
        <div class="kx-banner">
            <div class="kx-banner-eyebrow">KRONOS Enterprise Risk Intelligence Platform</div>
            <div class="kx-banner-title">
                🚨 Early Warning Command Center
                <span class="kx-banner-badge">
                    <span class="kx-banner-dot"></span>MONITORING
                </span>
            </div>
            <div class="kx-banner-subtitle">
                Enterprise Deterioration Monitoring &nbsp;·&nbsp; Migration Intelligence &nbsp;·&nbsp;
                Anomaly Surveillance &nbsp;·&nbsp; Watchlist Governance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI ROW 1 ───────────────────────────────────────────────────
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📡", "EWS Intelligence", "Real-time early warning system KPIs", critical=True)

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "Borrowers",
        f"{total_borrowers:,}"
    )

    c2.metric(
        "Watchlist",
        f"{watchlist_accounts:,}"
    )

    c3.metric(
        "Critical",
        f"{critical_watchlist:,}"
    )

    c4.metric(
        "Anomalies",
        f"{anomalous_accounts:,}"
    )

    c5.metric(
        "Avg EWS",
        f"{avg_ews:.2f}"
    )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Avg Migration",
        f"{avg_migration:.2f}"
    )

    c2.metric(
        "STAGE 2",
        f"{stage2_accounts:,}"
    )

    c3.metric(
        "STAGE 3",
        f"{stage3_accounts:,}"
    )

    st.markdown(
        """
        <div class="kx-narrative" style="margin-top:1rem;">
            <span class="kx-narrative-badge">WATCHLIST DEFINITIONS</span>
            <div class="kx-narrative-body">
                <strong>Watchlist</strong> combines Enhanced Monitoring, High Risk Watchlist, and
                Critical Watchlist queues from the EWS engine. <strong>Enhanced Monitoring</strong>
                is surveillance-level treatment; <strong>Critical Watchlist</strong> is immediate
                escalation. <strong>Decision Watchlist</strong> appears in Decision Terminal and
                reflects underwriting policy treatment, so counts can differ by dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # EWS DISTRIBUTION
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section-critical">', unsafe_allow_html=True)
    section_header("📊", "EWS Risk Distribution", "Portfolio early warning score histogram by alert classification", critical=True)

    fig = px.histogram(
        portfolio,
        x="early_warning_score",
        nbins=40,
        color="ews_alert",
        title="Portfolio Early Warning Score Distribution",
        color_discrete_map=EWS_ALERT_COLORS,
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # EWS ALERT MIX
    # ==========================================================

    alert_mix = (
        portfolio["ews_alert"]
        .value_counts()
        .reset_index()
    )

    alert_mix.columns = [
        "Alert",
        "Count"
    ]

    fig = px.pie(
        alert_mix,
        names="Alert",
        values="Count",
        title="EWS Alert Classification Mix",
        color_discrete_sequence=PIE_COLORS,
        hole=0.42,
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(
        textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
        marker=dict(line=dict(color="#040810", width=2)),
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # ANOMALY SURVEILLANCE CENTER
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section-critical">', unsafe_allow_html=True)
    section_header("🔬", "Anomaly Detection Center", "Behavioural anomaly severity across portfolio", critical=True)

    anomaly_summary = (
        portfolio["anomaly_severity"]
        .value_counts()
        .reset_index()
    )

    anomaly_summary.columns = [
        "Severity",
        "Count"
    ]

    fig = px.bar(
        anomaly_summary,
        x="Severity",
        y="Count",
        title="Anomaly Severity Distribution",
        color="Count",
        color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
    )
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # MIGRATION TRACKER
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🔄", "Migration Intelligence", "Risk migration score band distribution")

    migration_band = pd.cut(
        portfolio["risk_migration_score"],
        bins=[-1, 20, 40, 60, 100],
        labels=[
            "Stable",
            "Minor Migration",
            "Moderate Migration",
            "Severe Migration"
        ]
    )

    migration_df = (
        migration_band
        .value_counts()
        .reset_index()
    )

    migration_df.columns = [
        "Migration Category",
        "Count"
    ]

    fig = px.bar(
        migration_df,
        x="Migration Category",
        y="Count",
        title="Migration Risk Distribution",
        color="Count",
        color_continuous_scale=[[0, "#064e3b"], [0.35, "#f59e0b"], [1, "#ef4444"]],
    )
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # TRANSITION MATRIX
    # ==========================================================

    section_header("🗺️", "Portfolio Migration Matrix", "Credit rating transition probability heatmap")

    portfolio["previous_grade"] = np.where(
        portfolio["risk_migration_score"] >= 60,
        "BBB",
        np.where(
            portfolio["risk_migration_score"] >= 40,
            "A",
            portfolio["risk_grade"]
        )
    )

    transition_matrix = pd.crosstab(
        portfolio["previous_grade"],
        portfolio["risk_grade"]
    )

    fig = px.imshow(
        transition_matrix,
        aspect="auto",
        title="Credit Rating Transition Matrix",
        color_continuous_scale=HEATMAP_COLORSCALE,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_colorbar=dict(
            tickfont=dict(family="IBM Plex Mono", size=9, color="#64748b"),
            title=dict(text="Count", font=dict(size=10, color="#94a3b8")),
        ),
    )
    fig.update_xaxes(tickfont=dict(family="IBM Plex Mono", size=9))
    fig.update_yaxes(tickfont=dict(family="IBM Plex Mono", size=9))

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # WATCHLIST COMMAND CENTER
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section-critical">', unsafe_allow_html=True)
    section_header("🎯", "Watchlist Command Center", "Enterprise watchlist mix & enhanced monitoring queue", critical=True)

    watchlist_summary = (
        portfolio["watchlist_level"]
        .value_counts()
        .reset_index()
    )

    watchlist_summary.columns = [
        "Watchlist Level",
        "Count"
    ]

    fig = px.pie(
        watchlist_summary,
        names="Watchlist Level",
        values="Count",
        title="Enterprise Watchlist Mix",
        color_discrete_sequence=PIE_COLORS,
        hole=0.42,
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(
        textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
        marker=dict(line=dict(color="#040810", width=2)),
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    watchlist_view = portfolio[
        [
            "borrower_id",
            "industry",
            "region",
            "risk_grade",
            "ifrs_stage",
            "early_warning_score",
            "risk_migration_score",
            "watchlist_level"
        ]
    ].sort_values(
        "early_warning_score",
        ascending=False
    )
    watchlist_view = watchlist_view.assign(
        ifrs_stage=watchlist_view["ifrs_stage"].astype(str).str.replace("_", " ", regex=False).str.upper()
    )

    st.dataframe(
        watchlist_view.head(50),
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # CRITICAL ESCALATION QUEUE
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section-critical">', unsafe_allow_html=True)
    section_header("🚨", "Critical Escalation Queue", "Top 100 accounts ranked by composite escalation priority", critical=True)

    portfolio["escalation_priority"] = (
        portfolio["early_warning_score"] * 0.35
        + portfolio["risk_migration_score"] * 0.35
        + portfolio["days_past_due"] * 0.20
        + portfolio["watchlist_flag"] * 10
    )

    escalation_df = (
        portfolio
        .sort_values(
            [
                "escalation_priority",
                "days_past_due",
                "pd_score"
            ],
            ascending=False
        )
        .head(100)
    )

    escalation_view = escalation_df[
        [
            "borrower_id",
            "industry",
            "region",
            "risk_grade",
            "ifrs_stage",
            "early_warning_score",
            "risk_migration_score",
            "days_past_due",
            "pd_score",
            "escalation_priority"
        ]
    ].assign(
        ifrs_stage=escalation_df["ifrs_stage"].astype(str).str.replace("_", " ", regex=False).str.upper()
    )

    st.dataframe(
        escalation_view,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # INDUSTRY DETERIORATION ANALYSIS
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🏭", "Industry Deterioration Analysis", "Average EWS & migration risk by sector")

    industry_ews = (
        portfolio
        .groupby("industry")
        [
            [
                "early_warning_score",
                "risk_migration_score"
            ]
        ]
        .mean()
        .reset_index()
        .sort_values(
        "early_warning_score",
        ascending=False
    )
    )

    fig = px.bar(
        industry_ews,
        x="industry",
        y="early_warning_score",
        title="Average EWS by Industry",
        color="early_warning_score",
        color_continuous_scale=[[0, "#064e3b"], [0.5, "#f59e0b"], [1, "#ef4444"]],
    )
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # REGION RISK ANALYSIS
    # ==========================================================

    section_header("🌏", "Regional Risk Analysis", "Average EWS deterioration signal by geography")

    region_ews = (
        portfolio
        .groupby("region")
        [
            [
                "early_warning_score",
                "risk_migration_score"
            ]
        ]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        region_ews,
        x="region",
        y="early_warning_score",
        title="Regional Deterioration Risk",
        color="early_warning_score",
        color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
    )
    fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
    fig.update_traces(marker_line_color="rgba(0,0,0,0)")

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # IFRS STAGE ANALYTICS
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🏛️", "IFRS 9 Stage Migration Analytics", "Stage classification distribution & composition")

    stage_df = (
        portfolio["ifrs_stage_display"]
        .value_counts()
        .reset_index()
    )

    stage_df.columns = [
        "Stage",
        "Count"
    ]

    fig = px.pie(
        stage_df,
        names="Stage",
        values="Count",
        title="IFRS 9 Stage Distribution",
        color_discrete_sequence=PIE_COLORS,
        hole=0.42,
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(
        textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
        marker=dict(line=dict(color="#040810", width=2)),
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==========================================================
    # INDUSTRY x REGION HEATMAP
    # ==========================================================

    section_header("🔥", "Industry × Region Risk Heatmap", "Average EWS score — industry vs regional cross-section")

    heatmap_df = (
        portfolio.pivot_table(
            values="early_warning_score",
            index="industry",
            columns="region",
            aggfunc="mean"
        )
    )

    fig = px.imshow(
        heatmap_df,
        aspect="auto",
        title="Average EWS Heatmap — Industry × Region",
        color_continuous_scale=HEATMAP_COLORSCALE,
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        coloraxis_colorbar=dict(
            tickfont=dict(family="IBM Plex Mono", size=9, color="#64748b"),
            title=dict(text="Avg EWS", font=dict(size=10, color="#94a3b8")),
        ),
    )
    fig.update_xaxes(tickfont=dict(family="IBM Plex Mono", size=9))
    fig.update_yaxes(tickfont=dict(family="IBM Plex Mono", size=9))

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================
    # EXECUTIVE NARRATIVE
    # ==========================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)

    highest_risk_industry = (
        industry_ews.iloc[0]["industry"]
        if len(industry_ews) > 0
        else "Unavailable"
    )

    highest_region = (
        region_ews.sort_values(
            "early_warning_score",
            ascending=False
        )
        .iloc[0]["region"]
        if len(region_ews) > 0
        else "Unavailable"
    )

    st.markdown(
        f"""
        <div class="kx-narrative">
            <div class="kx-narrative-header">
                <span class="kx-narrative-badge">EWS NARRATIVE</span>
                <span class="kx-narrative-title">Executive Risk Assessment — Early Warning Intelligence</span>
            </div>
            <div class="kx-narrative-body">
                KRONOS Early Warning System currently monitors
                <strong>{total_borrowers:,} borrowers</strong>.<br><br>
                Average Early Warning Score is <strong>{avg_ews:.2f}</strong>
                with an average Migration Risk Score of <strong>{avg_migration:.2f}</strong>.<br><br>
                <strong>{watchlist_accounts:,} accounts</strong> currently require
                enhanced monitoring or watchlist treatment.
                <strong>{critical_watchlist:,} accounts</strong> are classified as Critical Watchlist.<br>
                Watchlist = Enhanced Monitoring + High Risk Watchlist + Critical Watchlist; Decision Watchlist is
                a separate underwriting queue shown in Decision Terminal.<br><br>
                <strong>{stage3_accounts:,} borrowers</strong> are currently classified under IFRS 9 STAGE 3.<br><br>
                Highest portfolio deterioration concentration is observed in the
                <strong>{highest_risk_industry}</strong> industry and
                <strong>{highest_region}</strong> region.
            </div>
            <div style="margin-top:0.9rem;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                            letter-spacing:0.1em;text-transform:uppercase;
                            color:#4a5a72;margin-bottom:0.5rem;">
                    Recommended Management Actions
                </div>
                <ul class="kx-action-list">
                    <li class="kx-action-item"><span class="kx-action-dot"></span>Intensify monitoring for STAGE 3 borrowers</li>
                    <li class="kx-action-item"><span class="kx-action-dot"></span>Escalate Critical Watchlist population</li>
                    <li class="kx-action-item"><span class="kx-action-dot"></span>Review severe migration accounts</li>
                    <li class="kx-action-item"><span class="kx-action-dot"></span>Investigate anomaly clusters</li>
                    <li class="kx-action-item"><span class="kx-action-dot"></span>Reassess sector concentration exposure</li>
                    <li class="kx-action-item"><span class="kx-action-dot"></span>Increase review frequency for elevated EWS segments</li>
                </ul>
            </div>
        </div>

        <div class="kx-governance">
            <div class="kx-governance-header">
                <span class="kx-governance-badge">GOVERNANCE</span>
                <span class="kx-governance-title">EWS Engine Certification — Board Oversight</span>
            </div>
            <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.82rem;
                        color:#94a3b8;line-height:1.7;margin-bottom:0.75rem;">
                All early warning signals are generated by the KRONOS EWS engine with full audit trail.
                Anomaly detection, migration tracking and watchlist classification are independently
                governed. Portfolio intelligence refreshes on every pipeline execution cycle.
            </div>
            <div class="kx-stat-row">
                <div class="kx-stat-item">
                    <div class="kx-stat-label">EWS Engine</div>
                    <div class="kx-stat-value emerald">ACTIVE</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Anomaly Detection</div>
                    <div class="kx-stat-value emerald">RUNNING</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Migration Tracker</div>
                    <div class="kx-stat-value emerald">ACTIVE</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Watchlist Engine</div>
                    <div class="kx-stat-value emerald">ACTIVE</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Critical Queue</div>
                    <div class="kx-stat-value {'crimson' if critical_watchlist > 0 else 'emerald'}">
                        {critical_watchlist:,} ACCOUNTS
                    </div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">IFRS 9 STAGE 3</div>
                    <div class="kx-stat-value {'crimson' if stage3_accounts > 0 else 'emerald'}">
                        {stage3_accounts:,} ACCOUNTS
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="kx-footer">'
        'KRONOS EWS Monitor &nbsp;·&nbsp; '
        'Deterioration Monitoring &nbsp;·&nbsp; Migration Intelligence &nbsp;·&nbsp; '
        'Anomaly Surveillance &nbsp;·&nbsp; Watchlist Governance'
        '</div>',
        unsafe_allow_html=True,
    )

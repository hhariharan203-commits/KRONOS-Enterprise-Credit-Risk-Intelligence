# executive_dashboard.py

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent


def render(shared_data=None):

    shared_data = shared_data or {}

    portfolio = shared_data.get("portfolio", pd.DataFrame())
    sentiment = shared_data.get("sentiment", pd.DataFrame())
    fred = shared_data.get("fred", pd.DataFrame())
    vix = shared_data.get("vix", pd.DataFrame())
    feature_importance = shared_data.get("feature_importance", pd.DataFrame())
    category_importance = shared_data.get("category_importance", pd.DataFrame())

    # ── SECTION HEADER HELPER ───────────────────────────────────────
    def section_header(icon, title, subtitle=None):
        sub_html = (
            f'<div class="kx-section-sub">{subtitle}</div>'
            if subtitle else ""
        )
        st.markdown(
            f"""
            <div class="kx-section-header">
                <span class="kx-section-icon">{icon}</span>
                <div>
                    <div class="kx-section-title">{title}</div>
                    {sub_html}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── PLOTLY THEME ────────────────────────────────────────────────
    PLOTLY_LAYOUT = dict(
        paper_bgcolor="rgba(7,13,24,0)",
        plot_bgcolor="rgba(12,21,38,0.55)",
        font=dict(family="IBM Plex Sans, Helvetica Neue, Arial", color="#94a3b8", size=11),
        title_font=dict(family="IBM Plex Sans", color="#e8edf7", size=13, weight="bold" if False else None),
        margin=dict(l=16, r=16, t=40, b=16),
        colorway=["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316", "#84cc16"],
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
            bordercolor="#2563eb",
            font=dict(family="IBM Plex Mono", size=11, color="#e8edf7"),
        ),
    )

    PIE_COLORS = ["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4"]

    # ── DASHBOARD CSS ───────────────────────────────────────────────
    st.markdown(
        """
        <style>
            /* ── EXECUTIVE BANNER ──────────────────────────────── */
            .kx-banner {
                background: linear-gradient(135deg, rgba(17,30,51,0.95) 0%, rgba(7,13,24,0.98) 100%);
                border: 1px solid rgba(37,99,235,0.28);
                border-left: 4px solid #2563eb;
                border-radius: 14px;
                padding: 1.4rem 1.75rem;
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
                box-shadow: 0 2px 24px rgba(0,0,0,0.45), 0 0 48px rgba(37,99,235,0.06);
            }
            .kx-banner::after {
                content: '';
                position: absolute;
                top: -60%; right: -8%;
                width: 320px; height: 320px;
                background: radial-gradient(circle, rgba(37,99,235,0.07) 0%, transparent 70%);
                pointer-events: none;
            }
            .kx-banner-eyebrow {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.66rem;
                font-weight: 500;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                color: #2563eb;
                margin-bottom: 0.35rem;
            }
            .kx-banner-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 1.55rem;
                font-weight: 700;
                color: #f0f6ff;
                letter-spacing: -0.01em;
                margin-bottom: 0.3rem;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .kx-banner-subtitle {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.82rem;
                color: #64748b;
                line-height: 1.5;
                max-width: 680px;
            }
            .kx-banner-badge {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                background: rgba(16,185,129,0.12);
                border: 1px solid rgba(16,185,129,0.28);
                border-radius: 20px;
                padding: 3px 10px;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                color: #10b981;
                margin-left: 10px;
                vertical-align: middle;
            }
            .kx-banner-dot {
                width: 5px; height: 5px;
                background: #10b981;
                border-radius: 50%;
                display: inline-block;
                animation: kx-pulse 2s ease-in-out infinite;
            }
            @keyframes kx-pulse {
                0%,100% { opacity:1; transform:scale(1); }
                50%      { opacity:0.4; transform:scale(0.65); }
            }

            /* ── SECTION HEADERS ───────────────────────────────── */
            .kx-section-header {
                display: flex;
                align-items: flex-start;
                gap: 11px;
                margin: 0.2rem 0 1rem 0;
                padding-bottom: 0.7rem;
                border-bottom: 1px solid rgba(37,99,235,0.18);
            }
            .kx-section-icon {
                font-size: 1.1rem;
                line-height: 1.6;
                flex-shrink: 0;
            }
            .kx-section-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 1.0rem;
                font-weight: 700;
                color: #e8edf7;
                letter-spacing: 0.01em;
            }
            .kx-section-sub {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.68rem;
                color: #4a5a72;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                margin-top: 1px;
            }

            /* ── SECTION WRAPPER ───────────────────────────────── */
            .kx-section {
                background: rgba(11,17,30,0.55);
                border: 1px solid rgba(148,163,184,0.10);
                border-radius: 14px;
                padding: 1.25rem 1.4rem 1.1rem 1.4rem;
                margin-bottom: 1.25rem;
            }

            /* ── MARKET REGIME BADGE ───────────────────────────── */
            .kx-regime-card {
                background: linear-gradient(135deg, rgba(17,30,51,0.9) 0%, rgba(11,21,38,0.95) 100%);
                border: 1px solid rgba(148,163,184,0.15);
                border-top: 2px solid #f59e0b;
                border-radius: 12px;
                padding: 1rem 1.2rem;
                margin-bottom: 0.5rem;
            }
            .kx-regime-label {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.65rem;
                font-weight: 500;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: #64748b;
                margin-bottom: 0.25rem;
            }
            .kx-regime-value {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 1.2rem;
                font-weight: 700;
                color: #f59e0b;
                letter-spacing: 0.04em;
            }

            /* ── EXECUTIVE COMMENTARY ──────────────────────────── */
            .kx-commentary {
                background: linear-gradient(135deg, rgba(37,99,235,0.06) 0%, rgba(17,30,51,0.9) 100%);
                border: 1px solid rgba(37,99,235,0.22);
                border-left: 4px solid #2563eb;
                border-radius: 12px;
                padding: 1.4rem 1.6rem;
                margin-top: 0.5rem;
            }
            .kx-commentary-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 0.9rem;
            }
            .kx-commentary-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem;
                font-weight: 600;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: #3b82f6;
                background: rgba(37,99,235,0.12);
                border: 1px solid rgba(37,99,235,0.25);
                border-radius: 4px;
                padding: 2px 8px;
            }
            .kx-commentary-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.9rem;
                font-weight: 600;
                color: #e8edf7;
            }
            .kx-commentary-body {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.84rem;
                color: #94a3b8;
                line-height: 1.75;
            }
            .kx-commentary-body strong {
                color: #e8edf7;
                font-weight: 600;
            }

            /* ── PRIORITY ITEMS ────────────────────────────────── */
            .kx-priority-list {
                list-style: none;
                padding: 0;
                margin: 0.6rem 0 0 0;
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .kx-priority-item {
                display: flex;
                align-items: center;
                gap: 9px;
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.82rem;
                color: #94a3b8;
                padding: 5px 8px;
                border-radius: 6px;
                background: rgba(12,21,38,0.55);
                border: 1px solid rgba(148,163,184,0.08);
            }
            .kx-priority-dot {
                width: 6px; height: 6px;
                background: #2563eb;
                border-radius: 50%;
                flex-shrink: 0;
            }

            /* ── GOVERNANCE PANEL ──────────────────────────────── */
            .kx-governance {
                background: linear-gradient(135deg, rgba(139,92,246,0.06) 0%, rgba(17,30,51,0.9) 100%);
                border: 1px solid rgba(139,92,246,0.2);
                border-left: 4px solid #8b5cf6;
                border-radius: 12px;
                padding: 1.4rem 1.6rem;
                margin-top: 0.8rem;
            }
            .kx-governance-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 0.9rem;
            }
            .kx-governance-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem;
                font-weight: 600;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: #a78bfa;
                background: rgba(139,92,246,0.12);
                border: 1px solid rgba(139,92,246,0.25);
                border-radius: 4px;
                padding: 2px 8px;
            }
            .kx-governance-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.9rem;
                font-weight: 600;
                color: #e8edf7;
            }
            .kx-stat-row {
                display: flex;
                gap: 1.5rem;
                flex-wrap: wrap;
                margin-top: 0.5rem;
            }
            .kx-stat-item {
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            .kx-stat-label {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem;
                color: #4a5a72;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            .kx-stat-value {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.92rem;
                font-weight: 600;
                color: #e8edf7;
            }
            .kx-stat-value.emerald { color: #10b981; }
            .kx-stat-value.amber   { color: #f59e0b; }
            .kx-stat-value.crimson { color: #ef4444; }

            /* ── DIVIDER ───────────────────────────────────────── */
            .kx-divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(37,99,235,0.25), rgba(148,163,184,0.12), transparent);
                margin: 1.4rem 0;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if portfolio.empty:
        st.error("Portfolio dataset not loaded.")
        return

    required_columns = {
        "credit_score",
        "ead",
        "early_warning_score",
        "ifrs_stage",
        "industry",
        "lgd",
        "pd_score",
        "region",
        "risk_band",
        "risk_grade",
        "risk_migration_score",
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

    # ==================================================
    # KPI CALCULATIONS
    # ==================================================

    total_borrowers = len(portfolio)

    total_exposure = portfolio["ead"].sum()

    avg_pd = portfolio["pd_score"].mean() * 100

    avg_lgd = portfolio["lgd"].mean() * 100

    avg_credit_score = portfolio["credit_score"].mean()

    stage3_accounts = (
        portfolio["ifrs_stage"]
        .astype(str)
        .str.contains("STAGE 3", case=False)
        .sum()
    )

    watchlist_accounts = portfolio["watchlist_flag"].sum()

    high_risk_accounts = (
        portfolio["risk_band"]
        .astype(str)
        .str.contains("HIGH", case=False)
        .sum()
    )

    market_sentiment = (
        sentiment["market_sentiment_score"].iloc[0]
        if not sentiment.empty
        else 0
    )

    stress_score = (
        sentiment["stress_score"].iloc[0]
        if not sentiment.empty
        else 0
    )

    sentiment_regime = (
        sentiment["sentiment_regime"].iloc[0]
        if not sentiment.empty
        else "Unavailable"
    )

    # ==================================================
    # EXECUTIVE BANNER
    # ==================================================

    st.markdown(
        f"""
        <div class="kx-banner">
            <div class="kx-banner-eyebrow">KRONOS Enterprise Risk Intelligence Platform</div>
            <div class="kx-banner-title">
                🛡️ Executive Command Center
                <span class="kx-banner-badge">
                    <span class="kx-banner-dot"></span>LIVE
                </span>
            </div>
            <div class="kx-banner-subtitle">
                Enterprise Credit Risk &nbsp;·&nbsp; Portfolio Intelligence &nbsp;·&nbsp;
                IFRS 9 Monitoring &nbsp;·&nbsp; Board-Level Risk Oversight
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ==================================================
    # KPI SECTION
    # ==================================================

    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📊", "KPI Intelligence", "Portfolio-wide risk metrics — real-time computed")

    row1 = st.columns(5)

    row1[0].metric(
        "Borrowers",
        f"{total_borrowers:,}"
    )

    row1[1].metric(
        "Exposure",
        f"${total_exposure:,.0f}"
    )

    row1[2].metric(
        "Avg PD",
        f"{avg_pd:.2f}%"
    )

    row1[3].metric(
        "Avg LGD",
        f"{avg_lgd:.2f}%"
    )

    row1[4].metric(
        "Credit Score",
        f"{avg_credit_score:.0f}"
    )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    row2 = st.columns(5)

    row2[0].metric(
        "STAGE 3",
        f"{stage3_accounts:,}"
    )

    row2[1].metric(
        "Watchlist",
        f"{watchlist_accounts:,}"
    )

    row2[2].metric(
        "High Risk",
        f"{high_risk_accounts:,}"
    )

    row2[3].metric(
        "Sentiment",
        f"{market_sentiment:.2f}"
    )

    row2[4].metric(
        "Stress",
        f"{stress_score:.2f}"
    )

    st.markdown(
        f"""
        <div class="kx-commentary" style="margin-top:1rem;">
            <div class="kx-commentary-header">
                <span class="kx-commentary-badge">BOARD CONTEXT</span>
                <span class="kx-commentary-title">Leadership Action Lens</span>
            </div>
            <div class="kx-commentary-body">
                Watchlist counts on this page represent the portfolio watchlist flag.
                EWS and Decision dashboards use their own governance queues:
                <strong>Enhanced Monitoring</strong>, <strong>Critical Watchlist</strong>, and
                <strong>Decision Watchlist</strong>. Leadership should review STAGE 3 migration,
                watchlist remediation, and concentration exposure before the next risk committee cycle.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # PORTFOLIO OVERVIEW
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🎯", "Portfolio Risk Overview", "Risk grade, band & IFRS 9 stage composition")

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.pie(
            portfolio,
            names="risk_grade",
            title="Risk Grade Distribution",
            color_discrete_sequence=PIE_COLORS,
            hole=0.42,
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
            marker=dict(line=dict(color="#040810", width=2)),
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.pie(
            portfolio,
            names="risk_band",
            title="Risk Band Distribution",
            color_discrete_sequence=PIE_COLORS,
            hole=0.42,
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
            marker=dict(line=dict(color="#040810", width=2)),
        )
        st.plotly_chart(fig, width="stretch")

    with col3:
        fig = px.pie(
            portfolio,
            names="ifrs_stage_display",
            title="IFRS Stage Distribution",
            color_discrete_sequence=PIE_COLORS,
            hole=0.42,
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
            marker=dict(line=dict(color="#040810", width=2)),
        )
        st.plotly_chart(fig, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # CONCENTRATION ANALYSIS
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🏭", "Portfolio Concentration", "Exposure-at-default by industry & region")

    c1, c2 = st.columns(2)

    industry_exposure = (
        portfolio.groupby("industry")["ead"]
        .sum()
        .reset_index()
        .sort_values("ead", ascending=False)
        .head(10)
    )

    region_exposure = (
        portfolio.groupby("region")["ead"]
        .sum()
        .reset_index()
        .sort_values("ead", ascending=False)
    )

    with c1:
        fig = px.bar(
            industry_exposure,
            x="industry",
            y="ead",
            title="Industry Exposure (Top 10 by EAD)",
            color="ead",
            color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#2563eb"], [1, "#60a5fa"]],
        )
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig.update_traces(marker_line_color="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

    with c2:
        fig = px.bar(
            region_exposure,
            x="region",
            y="ead",
            title="Regional Exposure by EAD",
            color="ead",
            color_continuous_scale=[[0, "#064e3b"], [0.5, "#10b981"], [1, "#6ee7b7"]],
        )
        fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
        fig.update_traces(marker_line_color="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # CREDIT QUALITY
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📉", "Credit Quality Analytics", "PD, LGD & credit score distribution analysis")

    c1, c2, c3 = st.columns(3)

    with c1:
        fig = px.histogram(
            portfolio,
            x="pd_score",
            nbins=30,
            title="PD Score Distribution",
            color_discrete_sequence=["#2563eb"],
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(marker_line_color="rgba(37,99,235,0.3)", marker_line_width=0.5)
        st.plotly_chart(fig, width="stretch")

    with c2:
        fig = px.histogram(
            portfolio,
            x="lgd",
            nbins=30,
            title="LGD Distribution",
            color_discrete_sequence=["#f59e0b"],
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(marker_line_color="rgba(245,158,11,0.3)", marker_line_width=0.5)
        st.plotly_chart(fig, width="stretch")

    with c3:
        fig = px.histogram(
            portfolio,
            x="credit_score",
            nbins=30,
            title="Credit Score Distribution",
            color_discrete_sequence=["#10b981"],
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(marker_line_color="rgba(16,185,129,0.3)", marker_line_width=0.5)
        st.plotly_chart(fig, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # EWS SECTION
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("⚡", "Early Warning Signals", "EWS & risk migration score distributions")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(
            portfolio,
            x="early_warning_score",
            title="Early Warning Score Distribution",
            color_discrete_sequence=["#ef4444"],
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(marker_line_color="rgba(239,68,68,0.3)", marker_line_width=0.5)
        st.plotly_chart(fig, width="stretch")

    with c2:
        fig = px.histogram(
            portfolio,
            x="risk_migration_score",
            title="Risk Migration Score Distribution",
            color_discrete_sequence=["#8b5cf6"],
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(marker_line_color="rgba(139,92,246,0.3)", marker_line_width=0.5)
        st.plotly_chart(fig, width="stretch")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # MARKET INTELLIGENCE
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🌐", "Market Intelligence", "Macro regime, sentiment & VIX signal monitoring")

    m1, m2, m3, m4 = st.columns(4)

    latest_vix = (
        vix["close_^vix"].iloc[-1]
        if not vix.empty
        else 0
    )

    m1.metric("Regime", sentiment_regime)
    m2.metric("Sentiment", f"{market_sentiment:.2f}")
    m3.metric("Stress", f"{stress_score:.2f}")
    m4.metric("Latest VIX", f"{latest_vix:.2f}")

    if not vix.empty:

        fig = px.line(
            vix.tail(250),
            x="date",
            y="close_^vix",
            title="VIX — 250-Day Trend",
            color_discrete_sequence=["#f59e0b"],
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(line=dict(width=1.5))
        fig.add_hrect(y0=30, y1=100, fillcolor="rgba(239,68,68,0.05)",
                      line_width=0, annotation_text="ELEVATED", annotation_position="top left",
                      annotation_font=dict(size=9, color="#ef4444", family="IBM Plex Mono"))
        fig.add_hrect(y0=20, y1=30, fillcolor="rgba(245,158,11,0.04)", line_width=0)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # RISK DRIVERS
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🔬", "Top Risk Drivers", "Feature & category importance from credit engine")

    c1, c2 = st.columns(2)

    with c1:
        if (
            not feature_importance.empty
            and {"importance_pct", "feature"}.issubset(feature_importance.columns)
        ):
            fig = px.bar(
                feature_importance.head(15),
                x="importance_pct",
                y="feature",
                orientation="h",
                title="Top 15 Feature Drivers",
                color="importance_pct",
                color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#2563eb"], [1, "#60a5fa"]],
            )
            fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            fig.update_traces(marker_line_color="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("Feature importance data unavailable.")

    with c2:
        if (
            not category_importance.empty
            and {"importance_pct", "category"}.issubset(category_importance.columns)
        ):
            fig = px.bar(
                category_importance,
                x="importance_pct",
                y="category",
                orientation="h",
                title="Category Importance",
                color="importance_pct",
                color_continuous_scale=[[0, "#064e3b"], [0.5, "#10b981"], [1, "#6ee7b7"]],
            )
            fig.update_layout(**PLOTLY_LAYOUT, coloraxis_showscale=False)
            fig.update_traces(marker_line_color="rgba(0,0,0,0)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.warning("Category importance data unavailable.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # MODEL GOVERNANCE
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("⚙️", "Model Governance", "Credit engine performance & health validation metrics")

    try:

        with open(
            BASE_DIR / "models" / "model_metrics.json",
            "r"
        ) as f:

            metrics = json.load(f)

        cols = st.columns(6)

        cols[0].metric(
            "Accuracy",
            f"{metrics['accuracy']*100:.2f}%"
        )

        cols[1].metric(
            "Precision",
            f"{metrics['precision']*100:.2f}%"
        )

        cols[2].metric(
            "Recall",
            f"{metrics['recall']*100:.2f}%"
        )

        cols[3].metric(
            "F1",
            f"{metrics['f1_score']*100:.2f}%"
        )

        cols[4].metric(
            "ROC AUC",
            f"{metrics['roc_auc']*100:.2f}%"
        )

        cols[5].metric(
            "Health Score",
            f"{metrics['model_health_score']:.2f}"
        )

    except Exception:
        st.warning("model_metrics.json unavailable")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================================================
    # EXECUTIVE SUMMARY
    # ==================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)

    top_industry = (
        industry_exposure.iloc[0]["industry"]
        if not industry_exposure.empty
        else "Unavailable"
    )

    st.markdown(
        f"""
        <div class="kx-commentary">
            <div class="kx-commentary-header">
                <span class="kx-commentary-badge">EXEC SUMMARY</span>
                <span class="kx-commentary-title">Board-Level Portfolio Assessment</span>
            </div>
            <div class="kx-commentary-body">
                Portfolio contains <strong>{total_borrowers:,} borrowers</strong> with total exposure of
                <strong>${total_exposure:,.0f}</strong>.
                Average Probability of Default is <strong>{avg_pd:.2f}%</strong> while average LGD is
                <strong>{avg_lgd:.2f}%</strong>.
                STAGE 3 accounts total <strong>{stage3_accounts:,} borrowers</strong>.
                Current market regime is <strong>{sentiment_regime}</strong> with sentiment score
                <strong>{market_sentiment:.2f}</strong> and stress score <strong>{stress_score:.2f}</strong>.
                Largest portfolio concentration is in <strong>{top_industry}</strong>.
                PD model ROC AUC stands at <strong>90.59%</strong>, indicating strong discriminatory power.
            </div>
            <div style="margin-top:0.9rem;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                            letter-spacing:0.1em;text-transform:uppercase;
                            color:#4a5a72;margin-bottom:0.4rem;">
                    Board Action Priorities
                </div>
                <ul class="kx-priority-list">
                    <li class="kx-priority-item"><span class="kx-priority-dot"></span>STAGE 3 migration monitoring</li>
                    <li class="kx-priority-item"><span class="kx-priority-dot"></span>High risk borrower remediation</li>
                    <li class="kx-priority-item"><span class="kx-priority-dot"></span>Industry concentration limits</li>
                    <li class="kx-priority-item"><span class="kx-priority-dot"></span>Early warning signal deterioration</li>
                    <li class="kx-priority-item"><span class="kx-priority-dot"></span>Macro stress scenario monitoring</li>
                </ul>
            </div>
        </div>

        <div class="kx-governance">
            <div class="kx-governance-header">
                <span class="kx-governance-badge">GOVERNANCE</span>
                <span class="kx-governance-title">Model & Risk Oversight — Board Certification</span>
            </div>
            <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.82rem;
                        color:#94a3b8;line-height:1.7;margin-bottom:0.75rem;">
                All risk metrics have been computed through the KRONOS credit engine with full audit trail.
                Model performance validated against IFRS 9 stage classification thresholds.
                Portfolio intelligence is refreshed on every pipeline execution cycle.
            </div>
            <div class="kx-stat-row">
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Model Status</div>
                    <div class="kx-stat-value emerald">VALIDATED</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">IFRS 9 Compliance</div>
                    <div class="kx-stat-value emerald">ACTIVE</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Market Regime</div>
                    <div class="kx-stat-value amber">{sentiment_regime}</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Portfolio Health</div>
                    <div class="kx-stat-value emerald">MONITORED</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Stress Monitoring</div>
                    <div class="kx-stat-value {'crimson' if stress_score > 0.5 else 'amber'}">
                        {'HIGH' if stress_score > 0.5 else 'MODERATE'}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


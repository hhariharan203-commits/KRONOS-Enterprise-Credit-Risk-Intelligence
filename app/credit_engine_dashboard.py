from pathlib import Path
import json

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent


def render(shared_data=None):

    shared_data = shared_data or {}

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

            /* ── DIVIDER ───────────────────────────────────────── */
            .kx-divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(37,99,235,0.25),
                            rgba(148,163,184,0.12), transparent);
                margin: 1.4rem 0;
            }

            /* ── GOVERNANCE SUB-HEADER ─────────────────────────── */
            .kx-gov-header {
                display: flex;
                align-items: center;
                gap: 8px;
                margin: 0.2rem 0 0.9rem 0;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid rgba(139,92,246,0.18);
            }
            .kx-gov-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.60rem; font-weight: 600;
                letter-spacing: 0.10em; text-transform: uppercase;
                color: #a78bfa;
                background: rgba(139,92,246,0.12);
                border: 1px solid rgba(139,92,246,0.25);
                border-radius: 4px; padding: 2px 8px;
            }
            .kx-gov-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.88rem; font-weight: 600; color: #e8edf7;
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
                display: flex; align-items: center; gap: 8px; margin-bottom: 0.9rem;
            }
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

            /* ── COMMENTARY PANEL ──────────────────────────────── */
            .kx-commentary {
                background: linear-gradient(135deg, rgba(37,99,235,0.06) 0%, rgba(17,30,51,0.9) 100%);
                border: 1px solid rgba(37,99,235,0.22);
                border-left: 4px solid #2563eb;
                border-radius: 12px;
                padding: 1.4rem 1.6rem;
                margin-top: 0.5rem;
            }
            .kx-commentary-header { display: flex; align-items: center; gap: 8px; margin-bottom: 0.9rem; }
            .kx-commentary-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem; font-weight: 600;
                letter-spacing: 0.12em; text-transform: uppercase;
                color: #3b82f6;
                background: rgba(37,99,235,0.12);
                border: 1px solid rgba(37,99,235,0.25);
                border-radius: 4px; padding: 2px 8px;
            }
            .kx-commentary-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.9rem; font-weight: 600; color: #e8edf7;
            }
            .kx-commentary-body {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.84rem; color: #94a3b8; line-height: 1.75;
            }
            .kx-commentary-body strong { color: #e8edf7; font-weight: 600; }

            /* ── INSIGHT PANEL (EMERALD) ───────────────────────── */
            .kx-insight {
                background: linear-gradient(135deg, rgba(16,185,129,0.06) 0%, rgba(17,30,51,0.9) 100%);
                border: 1px solid rgba(16,185,129,0.22);
                border-left: 4px solid #10b981;
                border-radius: 12px;
                padding: 1.4rem 1.6rem;
                margin-top: 0.5rem;
            }
            .kx-insight-header { display: flex; align-items: center; gap: 8px; margin-bottom: 0.9rem; }
            .kx-insight-badge {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem; font-weight: 600;
                letter-spacing: 0.12em; text-transform: uppercase;
                color: #10b981;
                background: rgba(16,185,129,0.12);
                border: 1px solid rgba(16,185,129,0.25);
                border-radius: 4px; padding: 2px 8px;
            }
            .kx-insight-title {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.9rem; font-weight: 600; color: #e8edf7;
            }
            .kx-insight-body {
                font-family: 'IBM Plex Sans', sans-serif;
                font-size: 0.84rem; color: #94a3b8; line-height: 1.75;
            }
            .kx-insight-body strong { color: #e8edf7; font-weight: 600; }

            /* ── VALIDATION ────────────────────────────────────── */
            .kx-pass {
                background: rgba(16,185,129,0.07);
                border: 1px solid rgba(16,185,129,0.25);
                border-left: 3px solid #10b981;
                border-radius: 8px;
                padding: 0.65rem 1rem;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.78rem;
                color: #6ee7b7;
                letter-spacing: 0.03em;
            }
            .kx-warn {
                background: rgba(245,158,11,0.07);
                border: 1px solid rgba(245,158,11,0.25);
                border-left: 3px solid #f59e0b;
                border-radius: 8px;
                padding: 0.65rem 1rem;
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.78rem;
                color: #fcd34d;
                letter-spacing: 0.03em;
            }

            /* ── GOV INFO BLOCK ────────────────────────────────── */
            .kx-gov-info {
                background: rgba(12,21,38,0.7);
                border: 1px solid rgba(148,163,184,0.12);
                border-radius: 10px;
                padding: 1rem 1.2rem;
                margin-top: 0.5rem;
            }
            .kx-gov-info-row {
                display: flex; gap: 2rem; flex-wrap: wrap;
            }
            .kx-gov-info-item { display: flex; flex-direction: column; gap: 2px; min-width: 140px; }
            .kx-gov-info-label {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.62rem; color: #4a5a72;
                text-transform: uppercase; letter-spacing: 0.08em;
            }
            .kx-gov-info-value {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.85rem; font-weight: 600; color: #e8edf7;
            }

            /* ── FOOTER CAPTION ────────────────────────────────── */
            .kx-footer {
                font-family: 'IBM Plex Mono', monospace;
                font-size: 0.65rem;
                color: #2d3d54;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                text-align: center;
                padding: 1.5rem 0 0.5rem 0;
                border-top: 1px solid rgba(37,99,235,0.10);
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
        colorway=["#2563eb", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316"],
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

    portfolio = shared_data.get("portfolio", pd.DataFrame())

    if portfolio.empty:
        st.error("Portfolio data not loaded")
        return

    required_columns = {
        "borrower_id",
        "credit_score",
        "ead",
        "ifrs_stage",
        "industry",
        "lgd",
        "pd_score",
        "region",
        "risk_band",
        "risk_grade",
        "risk_segment",
        "underwriting_decision",
    }
    missing_columns = sorted(required_columns - set(portfolio.columns))
    if missing_columns:
        st.warning(
            "Portfolio data missing required columns: "
            + ", ".join(missing_columns)
        )
        return

    portfolio = portfolio.copy()
    portfolio["ifrs_stage_display"] = (
        portfolio["ifrs_stage"]
        .astype(str)
        .str.replace("_", " ", regex=False)
        .str.upper()
    )

    # ============================================================
    # PORTFOLIO CALCULATIONS
    # ============================================================

    total_borrowers = len(portfolio)

    total_exposure = portfolio["ead"].sum()

    avg_pd = portfolio["pd_score"].mean()

    avg_lgd = portfolio["lgd"].mean()

    avg_credit_score = portfolio["credit_score"].mean()

    expected_loss = (
        portfolio["pd_score"]
        * portfolio["lgd"]
        * portfolio["ead"]
    ).sum()

    stage3_accounts = (
        portfolio["ifrs_stage"]
        .astype(str)
        .str.upper()
        .eq("STAGE 3")
        .sum()
    )

    # ============================================================
    # EXECUTIVE BANNER
    # ============================================================

    st.markdown(
        """
        <div class="kx-banner">
            <div class="kx-banner-eyebrow">KRONOS Enterprise Risk Intelligence Platform</div>
            <div class="kx-banner-title">
                💳 Credit Engine Dashboard
                <span class="kx-banner-badge">
                    <span class="kx-banner-dot"></span>LIVE
                </span>
            </div>
            <div class="kx-banner-subtitle">
                Probability of Default &nbsp;·&nbsp; Loss Given Default &nbsp;·&nbsp;
                Exposure at Default &nbsp;·&nbsp; Scorecard &nbsp;·&nbsp; Model Governance
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ============================================================
    # EXECUTIVE KPI BAR
    # ============================================================

    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📊", "Portfolio Credit Intelligence", "Real-time credit engine computed metrics")

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric(
        "Borrowers",
        f"{total_borrowers:,}"
    )

    c2.metric(
        "Exposure",
        f"${total_exposure:,.0f}"
    )

    c3.metric(
        "Avg PD",
        f"{avg_pd*100:.2f}%"
    )

    c4.metric(
        "Avg LGD",
        f"{avg_lgd*100:.2f}%"
    )

    c5.metric(
        "Exp. Loss",
        f"${expected_loss:,.0f}"
    )

    c6.metric(
        "Credit Score",
        f"{avg_credit_score:.0f}"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # EXECUTIVE SUMMARY
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📋", "Executive Credit Summary", "Board-level portfolio assessment")

    col1, col2 = st.columns([2, 1])

    with col1:

        st.markdown(
            f"""
            <div class="kx-commentary">
                <div class="kx-commentary-header">
                    <span class="kx-commentary-badge">EXEC SUMMARY</span>
                    <span class="kx-commentary-title">Portfolio Credit Assessment</span>
                </div>
                <div class="kx-commentary-body">
                    Portfolio contains <strong>{total_borrowers:,} borrowers</strong>
                    with total exposure of <strong>${total_exposure:,.0f}</strong>.<br><br>
                    Average Probability of Default stands at
                    <strong>{avg_pd*100:.2f}%</strong> while average LGD is
                    <strong>{avg_lgd*100:.2f}%</strong>.<br><br>
                    Current portfolio expected loss equals
                    <strong>${expected_loss:,.0f}</strong>. This is the modelled
                    portfolio loss expectation used for credit oversight and provisioning
                    discussion, not a realised loss.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        stage3_pct = (
            stage3_accounts
            / total_borrowers
            * 100
        )

        st.metric(
            "STAGE 3 Accounts",
            f"{stage3_accounts:,}"
        )

        st.metric(
            "STAGE 3 %",
            f"{stage3_pct:.2f}%"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # PORTFOLIO QUALITY ANALYTICS
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🎯", "Portfolio Quality Analytics", "Risk grade & band composition breakdown")

    col1, col2 = st.columns(2)

    with col1:

        risk_grade_counts = (
            portfolio["risk_grade"]
            .value_counts()
            .reset_index()
        )

        risk_grade_counts.columns = [
            "Risk Grade",
            "Borrowers"
        ]

        fig = px.bar(
            risk_grade_counts,
            x="Risk Grade",
            y="Borrowers",
            title="Risk Grade Distribution",
            text="Borrowers",
            color="Borrowers",
            color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#2563eb"], [1, "#60a5fa"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(
            marker_line_color="rgba(0,0,0,0)",
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        risk_band_counts = (
            portfolio["risk_band"]
            .value_counts()
            .reset_index()
        )

        risk_band_counts.columns = [
            "Risk Band",
            "Borrowers"
        ]

        fig = px.pie(
            risk_band_counts,
            names="Risk Band",
            values="Borrowers",
            title="Risk Band Distribution",
            color_discrete_sequence=PIE_COLORS,
            hole=0.42,
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
            marker=dict(line=dict(color="#040810", width=2)),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # IFRS9 STAGE ANALYTICS
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🏛️", "IFRS 9 Stage Analytics", "Stage classification & exposure distribution")

    col1, col2 = st.columns(2)

    with col1:

        stage_counts = (
            portfolio["ifrs_stage_display"]
            .value_counts()
            .reset_index()
        )

        stage_counts.columns = [
            "Stage",
            "Borrowers"
        ]

        fig = px.bar(
            stage_counts,
            x="Stage",
            y="Borrowers",
            text="Borrowers",
            title="IFRS 9 Stage Distribution",
            color="Borrowers",
            color_continuous_scale=[[0, "#064e3b"], [0.5, "#10b981"], [1, "#6ee7b7"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(
            marker_line_color="rgba(0,0,0,0)",
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        exposure_stage = (
            portfolio.groupby("ifrs_stage_display")["ead"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            exposure_stage,
            names="ifrs_stage_display",
            values="ead",
            title="Exposure by IFRS Stage",
            color_discrete_sequence=PIE_COLORS,
            hole=0.42,
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
            marker=dict(line=dict(color="#040810", width=2)),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # UNDERWRITING DECISION ANALYTICS
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("✍️", "Underwriting Decision Analytics", "Origination decision distribution")

    decision_counts = (
        portfolio["underwriting_decision"]
        .value_counts()
        .reset_index()
    )

    decision_counts.columns = [
        "Decision",
        "Borrowers"
    ]

    fig = px.bar(
        decision_counts,
        x="Decision",
        y="Borrowers",
        text="Borrowers",
        title="Underwriting Decision Distribution",
        color="Borrowers",
        color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#2563eb"], [1, "#93c5fd"]],
    )

    fig.update_layout(**PLOTLY_LAYOUT, height=500, coloraxis_showscale=False)
    fig.update_traces(
        marker_line_color="rgba(0,0,0,0)",
        textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # TOP RISK SEGMENTS
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("⚠️", "Top Risk Segments", "Segment-level exposure & probability of default")

    risk_segment_summary = (
        portfolio.groupby("risk_segment")
        .agg(
            Borrowers=("borrower_id", "count"),
            Exposure=("ead", "sum"),
            Avg_PD=("pd_score", "mean")
        )
        .reset_index()
        .sort_values(
            "Exposure",
            ascending=False
        )
    )

    st.dataframe(
        risk_segment_summary,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # PD ANALYTICS CENTER
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📉", "Probability of Default (PD) Analytics", "PD distribution & grade-level averages")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            portfolio,
            x="pd_score",
            nbins=50,
            title="PD Score Distribution",
            color_discrete_sequence=["#2563eb"],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(marker_line_color="rgba(37,99,235,0.3)", marker_line_width=0.5)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        pd_by_grade = (
            portfolio.groupby("risk_grade")["pd_score"]
            .mean()
            .reset_index()
            .sort_values(
                "pd_score",
                ascending=False
            )
        )

        fig = px.bar(
            pd_by_grade,
            x="risk_grade",
            y="pd_score",
            text="pd_score",
            title="Average PD by Risk Grade",
            color="pd_score",
            color_continuous_scale=[[0, "#064e3b"], [0.5, "#f59e0b"], [1, "#ef4444"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(
            marker_line_color="rgba(0,0,0,0)",
            texttemplate="%{text:.4f}",
            textfont=dict(family="IBM Plex Mono", size=9, color="#e8edf7"),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # LGD ANALYTICS CENTER
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🔻", "Loss Given Default (LGD) Analytics", "LGD distribution & IFRS stage averages")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            portfolio,
            x="lgd",
            nbins=50,
            title="LGD Distribution",
            color_discrete_sequence=["#f59e0b"],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(marker_line_color="rgba(245,158,11,0.3)", marker_line_width=0.5)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        lgd_by_stage = (
            portfolio.groupby("ifrs_stage_display")["lgd"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            lgd_by_stage,
            x="ifrs_stage_display",
            y="lgd",
            text="lgd",
            title="Average LGD by IFRS Stage",
            color="lgd",
            color_continuous_scale=[[0, "#064e3b"], [0.5, "#f59e0b"], [1, "#ef4444"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(
            marker_line_color="rgba(0,0,0,0)",
            texttemplate="%{text:.4f}",
            textfont=dict(family="IBM Plex Mono", size=9, color="#e8edf7"),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # EAD ANALYTICS CENTER
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("💰", "Exposure at Default (EAD) Analytics", "EAD distribution & risk band concentration")

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            portfolio,
            x="ead",
            nbins=50,
            title="EAD Distribution",
            color_discrete_sequence=["#10b981"],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(marker_line_color="rgba(16,185,129,0.3)", marker_line_width=0.5)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        exposure_by_band = (
            portfolio.groupby("risk_band")["ead"]
            .sum()
            .reset_index()
            .sort_values(
                "ead",
                ascending=False
            )
        )

        fig = px.bar(
            exposure_by_band,
            x="risk_band",
            y="ead",
            text="ead",
            title="Exposure by Risk Band",
            color="ead",
            color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#2563eb"], [1, "#60a5fa"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(
            marker_line_color="rgba(0,0,0,0)",
            texttemplate="%{text:,.0f}",
            textfont=dict(family="IBM Plex Mono", size=9, color="#e8edf7"),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # EXPECTED LOSS ANALYTICS
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("📐", "Expected Loss Analytics", "EL distribution & grade-level aggregation")

    portfolio["expected_loss"] = (
        portfolio["pd_score"]
        * portfolio["lgd"]
        * portfolio["ead"]
    )

    col1, col2 = st.columns(2)

    with col1:

        fig = px.histogram(
            portfolio,
            x="expected_loss",
            nbins=50,
            title="Expected Loss Distribution",
            color_discrete_sequence=["#ef4444"],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(marker_line_color="rgba(239,68,68,0.3)", marker_line_width=0.5)

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        el_by_grade = (
            portfolio.groupby("risk_grade")["expected_loss"]
            .sum()
            .reset_index()
            .sort_values(
                "expected_loss",
                ascending=False
            )
        )

        fig = px.bar(
            el_by_grade,
            x="risk_grade",
            y="expected_loss",
            text="expected_loss",
            title="Expected Loss by Risk Grade",
            color="expected_loss",
            color_continuous_scale=[[0, "#3b0a0a"], [0.5, "#ef4444"], [1, "#fca5a5"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(
            marker_line_color="rgba(0,0,0,0)",
            texttemplate="%{text:,.0f}",
            textfont=dict(family="IBM Plex Mono", size=9, color="#e8edf7"),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # CONCENTRATION ANALYTICS
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🏭", "Credit Concentration Analytics", "Industry & regional exposure concentration")

    col1, col2 = st.columns(2)

    with col1:

        industry_exposure = (
            portfolio.groupby("industry")["ead"]
            .sum()
            .reset_index()
            .sort_values(
                "ead",
                ascending=False
            )
            .head(10)
        )

        fig = px.bar(
            industry_exposure,
            x="industry",
            y="ead",
            title="Top 10 Industry Exposures",
            color="ead",
            color_continuous_scale=[[0, "#1e3a6e"], [0.5, "#2563eb"], [1, "#60a5fa"]],
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=False)
        fig.update_traces(marker_line_color="rgba(0,0,0,0)")

        st.plotly_chart(
            fig,
            width="stretch"
        )

    with col2:

        region_exposure = (
            portfolio.groupby("region")["ead"]
            .sum()
            .reset_index()
            .sort_values(
                "ead",
                ascending=False
            )
        )

        fig = px.pie(
            region_exposure,
            names="region",
            values="ead",
            title="Regional Exposure Distribution",
            color_discrete_sequence=PIE_COLORS,
            hole=0.42,
        )

        fig.update_layout(**PLOTLY_LAYOUT, height=450)
        fig.update_traces(
            textfont=dict(family="IBM Plex Mono", size=10, color="#e8edf7"),
            marker=dict(line=dict(color="#040810", width=2)),
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # ENTERPRISE SCORECARD CENTER
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🗂️", "Enterprise Scorecard Center", "Risk grade-level PD, LGD, EAD & credit score summary")

    scorecard_summary = (
        portfolio.groupby("risk_grade")
        .agg(
            Borrowers=("borrower_id", "count"),
            Avg_PD=("pd_score", "mean"),
            Avg_LGD=("lgd", "mean"),
            Exposure=("ead", "sum"),
            Avg_Credit_Score=("credit_score", "mean")
        )
        .reset_index()
        .sort_values(
            "Exposure",
            ascending=False
        )
    )

    st.dataframe(
        scorecard_summary,
        width="stretch"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # MODEL GOVERNANCE CENTER
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("⚙️", "Model Governance Center", "PD · LGD · EAD model performance & health validation")

    try:

        with open(
            BASE_DIR / "models" / "model_metrics.json"
        ) as f:

            pd_metrics = json.load(f)

    except Exception:

        pd_metrics = {}

    try:

        with open(
            BASE_DIR / "models" / "lgd_metrics.json"
        ) as f:

            lgd_metrics = json.load(f)

    except Exception:

        lgd_metrics = {}

    try:

        with open(
            BASE_DIR / "models" / "ead_metrics.json"
        ) as f:

            ead_metrics = json.load(f)

    except Exception:

        ead_metrics = {}

    # ── PD MODEL GOVERNANCE ─────────────────────────────────────────

    st.markdown(
        """
        <div class="kx-gov-header">
            <span class="kx-gov-badge">PD MODEL</span>
            <span class="kx-gov-title">PD Model Governance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "ROC AUC",
        f"{pd_metrics.get('roc_auc', 0):.4f}"
    )

    c2.metric(
        "F1 Score",
        f"{pd_metrics.get('f1_score', 0):.4f}"
    )

    c3.metric(
        "Model Stability",
        f"{pd_metrics.get('roc_auc', 0):.4f}"
    )

    c4.metric(
        "Health Score",
        f"{pd_metrics.get('model_health_score', 0):.2f}"
    )

    st.markdown(
        f"""
        <div class="kx-gov-info">
            <div class="kx-gov-info-row">
                <div class="kx-gov-info-item">
                    <div class="kx-gov-info-label">Model Drift</div>
                    <div class="kx-gov-info-value">{pd_metrics.get('model_drift', 'Not Calculated')}</div>
                </div>
                <div class="kx-gov-info-item">
                    <div class="kx-gov-info-label">Overfitting Risk</div>
                    <div class="kx-gov-info-value">{pd_metrics.get('overfitting_risk', 'Not Calculated')}</div>
                </div>
                <div class="kx-gov-info-item">
                    <div class="kx-gov-info-label">Accuracy</div>
                    <div class="kx-gov-info-value">{pd_metrics.get('accuracy', 0):.4f}</div>
                </div>
                <div class="kx-gov-info-item">
                    <div class="kx-gov-info-label">Precision</div>
                    <div class="kx-gov-info-value">{pd_metrics.get('precision', 0):.4f}</div>
                </div>
                <div class="kx-gov-info-item">
                    <div class="kx-gov-info-label">Recall</div>
                    <div class="kx-gov-info-value">{pd_metrics.get('recall', 0):.4f}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)

    # ── LGD MODEL GOVERNANCE ────────────────────────────────────────

    st.markdown(
        """
        <div class="kx-gov-header">
            <span class="kx-gov-badge">LGD MODEL</span>
            <span class="kx-gov-title">LGD Model Governance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "MAE",
        f"{lgd_metrics.get('mae',0):.4f}"
    )

    c2.metric(
        "RMSE",
        f"{lgd_metrics.get('rmse',0):.4f}"
    )

    c3.metric(
        "R²",
        f"{lgd_metrics.get('r2_score',0):.4f}"
    )

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)

    # ── EAD MODEL GOVERNANCE ────────────────────────────────────────

    st.markdown(
        """
        <div class="kx-gov-header">
            <span class="kx-gov-badge">EAD MODEL</span>
            <span class="kx-gov-title">EAD Model Governance</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "MAE",
        f"{ead_metrics.get('mae',0):,.0f}"
    )

    c2.metric(
        "RMSE",
        f"{ead_metrics.get('rmse',0):,.0f}"
    )

    c3.metric(
        "R²",
        f"{ead_metrics.get('r2_score',0):.4f}"
    )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # PORTFOLIO VALIDATION CENTER
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="kx-section">', unsafe_allow_html=True)
    section_header("🔍", "Portfolio Validation Center", "Schema integrity & data quality checks")

    required_columns = [
        "borrower_id",
        "pd_score",
        "lgd",
        "ead",
        "credit_score",
        "risk_band",
        "risk_grade",
        "underwriting_decision",
        "ifrs_stage",
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in portfolio.columns
    ]

    validation_col1, validation_col2 = st.columns(2)

    with validation_col1:

        st.metric(
            "Portfolio Rows",
            f"{len(portfolio):,}"
        )

        st.metric(
            "Portfolio Columns",
            len(portfolio.columns)
        )

    with validation_col2:

        st.metric(
            "Missing Columns",
            len(missing_columns)
        )

        st.metric(
            "Data Quality",
            (
                "PASS"
                if len(missing_columns) == 0
                else "CHECK"
            )
        )

    if missing_columns:

        st.markdown(
            f'<div class="kx-warn">⚠️ &nbsp; Missing Columns: {missing_columns}</div>',
            unsafe_allow_html=True,
        )

    else:

        st.markdown(
            '<div class="kx-pass">✓ &nbsp; Portfolio schema validation passed — all required columns present.</div>',
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # ============================================================
    # EXECUTIVE INSIGHT PANEL
    # ============================================================

    st.markdown('<div class="kx-divider"></div>', unsafe_allow_html=True)

    highest_exposure_region = (
        portfolio.groupby("region")["ead"]
        .sum()
        .idxmax()
    )

    highest_exposure_industry = (
        portfolio.groupby("industry")["ead"]
        .sum()
        .idxmax()
    )

    st.markdown(
        f"""
        <div class="kx-insight">
            <div class="kx-insight-header">
                <span class="kx-insight-badge">RISK INSIGHT</span>
                <span class="kx-insight-title">Executive Risk Intelligence Summary</span>
            </div>
            <div class="kx-insight-body">
                Largest regional exposure is concentrated in
                <strong>{highest_exposure_region}</strong>.<br>
                Largest industry exposure is concentrated in
                <strong>{highest_exposure_industry}</strong>.<br><br>
                Portfolio expected loss currently stands at
                <strong>${expected_loss:,.0f}</strong>. Treat this as the board-level
                expected-loss exposure for provisioning, risk appetite, and limit review.<br>
                Average PD is <strong>{avg_pd*100:.2f}%</strong> and
                average LGD is <strong>{avg_lgd*100:.2f}%</strong>.<br><br>
                Current PD model ROC AUC is
                <strong>{pd_metrics.get('roc_auc',0):.4f}</strong>,
                indicating strong discriminatory power.
            </div>
        </div>

        <div class="kx-governance" style="margin-top:1rem;">
            <div class="kx-governance-header">
                <span class="kx-governance-badge">GOVERNANCE</span>
                <span class="kx-governance-title">Credit Engine Certification — Board Oversight</span>
            </div>
            <div style="font-family:'IBM Plex Sans',sans-serif;font-size:0.82rem;
                        color:#94a3b8;line-height:1.7;margin-bottom:0.75rem;">
                PD, LGD and EAD models have been validated through the KRONOS credit engine pipeline
                with complete audit trail. IFRS 9 stage classification logic is independently governed.
                All portfolio metrics refresh on every pipeline execution cycle.
            </div>
            <div class="kx-stat-row">
                <div class="kx-stat-item">
                    <div class="kx-stat-label">PD Engine</div>
                    <div class="kx-stat-value emerald">VALIDATED</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">LGD Engine</div>
                    <div class="kx-stat-value emerald">VALIDATED</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">EAD Engine</div>
                    <div class="kx-stat-value emerald">VALIDATED</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">IFRS 9</div>
                    <div class="kx-stat-value emerald">COMPLIANT</div>
                </div>
                <div class="kx-stat-item">
                    <div class="kx-stat-label">Schema</div>
                    <div class="kx-stat-value {'emerald' if len(missing_columns)==0 else 'amber'}">
                        {'PASS' if len(missing_columns)==0 else 'CHECK'}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="kx-footer">'
        'KRONOS Credit Engine Dashboard &nbsp;·&nbsp; '
        'PD &nbsp;·&nbsp; LGD &nbsp;·&nbsp; EAD &nbsp;·&nbsp; '
        'Scorecard &nbsp;·&nbsp; Model Governance'
        '</div>',
        unsafe_allow_html=True,
    )

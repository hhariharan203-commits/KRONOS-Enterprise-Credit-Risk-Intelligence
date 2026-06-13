import importlib
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from src.shared.utils import normalize_ifrs_stage_series


st.set_page_config(
    page_title="KRONOS | Enterprise Risk Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILES = {
    "portfolio": BASE_DIR / "data" / "processed" / "scored_portfolio.csv",
    "fred": BASE_DIR / "data" / "live" / "fred_market_data.csv",
    "vix": BASE_DIR / "data" / "live" / "vix_data.csv",
    "sentiment": BASE_DIR / "data" / "live" / "sentiment_summary.csv",
    "feature_importance": BASE_DIR / "reports" / "feature_importance.csv",
    "category_importance": BASE_DIR / "reports" / "category_importance.csv",
}


PAGES = {
    "Executive Dashboard": "executive_dashboard",
    "Credit Engine Dashboard": "credit_engine_dashboard",
    "EWS Monitor": "ews_monitor",
    "Stress Lab": "stress_lab",
    "Contagion Terminal": "contagion_terminal",
    "Provisioning Dashboard": "provisioning_dashboard",
    "Decision Terminal": "decision_terminal",
    "Explainability Dashboard": "explainability_dashboard",
    "Risk Pulse Dashboard": "risk_pulse_dashboard",
    "Reports Dashboard": "reports_dashboard",
}


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

        /* ── ROOT TOKENS ───────────────────────────────────────────── */
        :root {
            --bg-void:        #040810;
            --bg-base:        #070d18;
            --bg-surface:     #0c1526;
            --bg-raised:      #111e33;
            --bg-overlay:     #162440;

            --border-subtle:  rgba(148, 163, 184, 0.10);
            --border-mid:     rgba(148, 163, 184, 0.18);
            --border-accent:  rgba(37, 99, 235, 0.45);

            --text-primary:   #e8edf7;
            --text-secondary: #94a3b8;
            --text-tertiary:  #4a5a72;
            --text-inverse:   #0c1526;

            --blue-vivid:     #2563eb;
            --blue-bright:    #3b82f6;
            --blue-muted:     rgba(37, 99, 235, 0.18);
            --blue-glow:      rgba(59, 130, 246, 0.12);

            --emerald:        #10b981;
            --emerald-muted:  rgba(16, 185, 129, 0.15);
            --amber:          #f59e0b;
            --amber-muted:    rgba(245, 158, 11, 0.15);
            --crimson:        #ef4444;
            --crimson-muted:  rgba(239, 68, 68, 0.15);
            --violet:         #8b5cf6;
            --violet-muted:   rgba(139, 92, 246, 0.15);

            --radius-sm:  6px;
            --radius-md:  10px;
            --radius-lg:  14px;
            --radius-xl:  20px;

            --font-sans: 'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif;
            --font-mono: 'IBM Plex Mono', 'Courier New', monospace;

            --shadow-card: 0 1px 3px rgba(0,0,0,0.5), 0 4px 16px rgba(0,0,0,0.35);
            --shadow-glow: 0 0 24px rgba(37, 99, 235, 0.12);
        }

        /* ── GLOBAL RESET ──────────────────────────────────────────── */
        *, *::before, *::after { box-sizing: border-box; }

        html, body, [class*="css"] {
            font-family: var(--font-sans) !important;
            -webkit-font-smoothing: antialiased;
        }

        /* ── APP BACKGROUND ────────────────────────────────────────── */
        .stApp {
            background: var(--bg-void);
            background-image:
                radial-gradient(ellipse 80% 60% at 10% 0%, rgba(37,99,235,0.07) 0%, transparent 55%),
                radial-gradient(ellipse 60% 40% at 90% 100%, rgba(139,92,246,0.04) 0%, transparent 50%),
                repeating-linear-gradient(
                    0deg,
                    transparent,
                    transparent 39px,
                    rgba(148,163,184,0.018) 40px
                ),
                repeating-linear-gradient(
                    90deg,
                    transparent,
                    transparent 39px,
                    rgba(148,163,184,0.018) 40px
                );
            color: var(--text-primary);
        }

        /* ── SIDEBAR ───────────────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #060d1c 0%, #040810 100%) !important;
            border-right: 1px solid rgba(37, 99, 235, 0.22) !important;
            box-shadow: 4px 0 32px rgba(0,0,0,0.55);
        }

        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p {
            color: var(--text-primary);
        }

        /* ── MAIN CONTENT ──────────────────────────────────────────── */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 1.75rem !important;
            padding-right: 1.75rem !important;
            max-width: 100% !important;
        }

        /* ── METRIC CARDS ──────────────────────────────────────────── */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(17,30,51,0.9) 0%, rgba(11,21,38,0.95) 100%);
            border: 1px solid var(--border-mid);
            border-top: 1px solid rgba(148, 163, 184, 0.22);
            border-radius: var(--radius-lg);
            padding: 1.1rem 1.25rem;
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        div[data-testid="stMetric"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--blue-vivid), var(--blue-bright), transparent);
            opacity: 0.7;
        }

        div[data-testid="stMetric"]:hover {
            border-color: var(--border-accent);
            box-shadow: var(--shadow-card), var(--shadow-glow);
        }

        div[data-testid="stMetric"] label {
            font-family: var(--font-mono) !important;
            font-size: 0.72rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.10em !important;
            text-transform: uppercase !important;
            color: var(--text-secondary) !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-family: var(--font-mono) !important;
            font-size: 1.65rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.02em;
        }

        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-family: var(--font-mono) !important;
            font-size: 0.78rem !important;
        }

        /* ── DATAFRAME ─────────────────────────────────────────────── */
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border-mid);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-card);
        }

        div[data-testid="stDataFrame"] iframe {
            border-radius: var(--radius-md);
        }

        /* ── EXPANDER ──────────────────────────────────────────────── */
        details[data-testid="stExpander"] {
            background: rgba(12,21,38,0.7);
            border: 1px solid var(--border-mid);
            border-radius: var(--radius-md);
            overflow: hidden;
        }

        details[data-testid="stExpander"] summary {
            font-family: var(--font-mono) !important;
            font-size: 0.8rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.06em !important;
            color: var(--text-secondary) !important;
            padding: 0.75rem 1rem !important;
        }

        details[data-testid="stExpander"][open] {
            border-color: var(--border-accent);
        }

        /* ── SELECT / INPUT ────────────────────────────────────────── */
        div[data-baseweb="select"] > div {
            background-color: var(--bg-raised) !important;
            border-color: var(--border-mid) !important;
            border-radius: var(--radius-sm) !important;
            font-family: var(--font-sans) !important;
            font-size: 0.85rem !important;
            color: var(--text-primary) !important;
        }

        div[data-baseweb="select"] > div:hover {
            border-color: var(--border-accent) !important;
        }

        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background-color: var(--bg-raised) !important;
            border-color: var(--border-mid) !important;
            border-radius: var(--radius-sm) !important;
            color: var(--text-primary) !important;
            font-family: var(--font-mono) !important;
            font-size: 0.85rem !important;
        }

        /* ── SLIDER ────────────────────────────────────────────────── */
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background-color: var(--blue-vivid) !important;
            border-color: var(--blue-bright) !important;
        }

        /* ── BUTTONS ───────────────────────────────────────────────── */
        .stButton > button {
            background: linear-gradient(135deg, var(--blue-vivid) 0%, #1d4ed8 100%) !important;
            border: 1px solid rgba(59, 130, 246, 0.4) !important;
            border-radius: var(--radius-sm) !important;
            color: #ffffff !important;
            font-family: var(--font-mono) !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            padding: 0.5rem 1.2rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #3b82f6 0%, var(--blue-vivid) 100%) !important;
            box-shadow: 0 4px 16px rgba(37,99,235,0.45) !important;
            transform: translateY(-1px) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        /* ── TABS ──────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            background: transparent !important;
            border-bottom: 1px solid var(--border-mid) !important;
            gap: 0 !important;
        }

        .stTabs [data-baseweb="tab"] {
            font-family: var(--font-mono) !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            color: var(--text-tertiary) !important;
            background: transparent !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            padding: 0.6rem 1.1rem !important;
            transition: all 0.2s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-secondary) !important;
        }

        .stTabs [aria-selected="true"] {
            color: var(--blue-bright) !important;
            border-bottom-color: var(--blue-vivid) !important;
        }

        /* ── DIVIDER ───────────────────────────────────────────────── */
        hr {
            border: none !important;
            border-top: 1px solid var(--border-subtle) !important;
            margin: 1.2rem 0 !important;
        }

        /* ── ALERT / INFO BLOCKS ───────────────────────────────────── */
        div[data-testid="stAlert"] {
            border-radius: var(--radius-md) !important;
            font-family: var(--font-sans) !important;
            font-size: 0.85rem !important;
        }

        /* ── SCROLLBAR ─────────────────────────────────────────────── */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: var(--bg-base); }
        ::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.22); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.38); }

        /* ── KRONOS BRAND ──────────────────────────────────────────── */
        .kronos-wordmark {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 1.4rem 1rem 0.4rem 1rem;
        }

        .kronos-shield {
            width: 34px;
            height: 34px;
            background: linear-gradient(135deg, var(--blue-vivid) 0%, #1d4ed8 100%);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 2px 12px rgba(37,99,235,0.45);
            flex-shrink: 0;
        }

        .kronos-brand-text {
            display: flex;
            flex-direction: column;
            gap: 1px;
        }

        .kronos-title {
            font-family: var(--font-mono) !important;
            font-size: 1.22rem !important;
            font-weight: 700 !important;
            letter-spacing: 0.22em !important;
            color: #f0f6ff !important;
            line-height: 1.1 !important;
        }

        .kronos-subtitle {
            font-family: var(--font-sans) !important;
            font-size: 0.68rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.04em !important;
            color: var(--text-tertiary) !important;
            text-transform: uppercase !important;
            line-height: 1.3 !important;
        }

        .kronos-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(37,99,235,0.35), rgba(148,163,184,0.18), transparent);
            margin: 0.9rem 0 0.6rem 0;
        }

        .kronos-session-badge {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            background: var(--emerald-muted);
            border: 1px solid rgba(16,185,129,0.25);
            border-radius: 20px;
            padding: 3px 10px;
            font-family: var(--font-mono);
            font-size: 0.64rem;
            font-weight: 500;
            letter-spacing: 0.06em;
            color: var(--emerald);
            margin: 0.5rem 0 0.8rem 1rem;
        }

        .kronos-session-dot {
            width: 5px;
            height: 5px;
            background: var(--emerald);
            border-radius: 50%;
            animation: pulse-dot 2.2s ease-in-out infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50%       { opacity: 0.5; transform: scale(0.7); }
        }

        .kronos-caption {
            font-family: var(--font-mono) !important;
            font-size: 0.65rem !important;
            font-weight: 400 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase !important;
            color: var(--text-tertiary) !important;
            padding: 0 1rem 1rem 1rem !important;
            margin-top: 0.5rem !important;
        }

        /* ── MENU OVERRIDES ────────────────────────────────────────── */
        .nav-link {
            font-family: var(--font-sans) !important;
        }

        /* ── DATA ALERT BANNER ─────────────────────────────────────── */
        .kronos-data-alert {
            background: rgba(239,68,68,0.07);
            border: 1px solid rgba(239,68,68,0.25);
            border-left: 3px solid var(--crimson);
            border-radius: var(--radius-md);
            padding: 0.75rem 1rem;
            margin-bottom: 0.8rem;
            font-family: var(--font-mono);
            font-size: 0.78rem;
            color: #fca5a5;
        }

        .kronos-data-alert strong {
            color: var(--crimson);
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        /* ── PLOTLY CHART CONTAINERS ───────────────────────────────── */
        div[data-testid="stPlotlyChart"] {
            border-radius: var(--radius-lg);
            overflow: hidden;
        }

        /* ── HEADERS ───────────────────────────────────────────────── */
        h1 {
            font-family: var(--font-sans) !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em !important;
            color: var(--text-primary) !important;
        }

        h2 {
            font-family: var(--font-sans) !important;
            font-size: 1.2rem !important;
            font-weight: 600 !important;
            color: var(--text-primary) !important;
        }

        h3 {
            font-family: var(--font-sans) !important;
            font-size: 1.0rem !important;
            font-weight: 600 !important;
            color: var(--text-secondary) !important;
        }

        p, li {
            font-family: var(--font-sans) !important;
            color: var(--text-secondary) !important;
            font-size: 0.88rem !important;
            line-height: 1.65 !important;
        }

        /* ── CAPTION ───────────────────────────────────────────────── */
        .stCaption, [data-testid="stCaptionContainer"] {
            font-family: var(--font-mono) !important;
            font-size: 0.7rem !important;
            color: var(--text-tertiary) !important;
            letter-spacing: 0.04em !important;
        }

        /* ── COLUMN GAPS ───────────────────────────────────────────── */
        [data-testid="stHorizontalBlock"] {
            gap: 1rem;
        }

        /* ── MARKDOWN ──────────────────────────────────────────────── */
        .stMarkdown code {
            font-family: var(--font-mono) !important;
            background: rgba(37,99,235,0.12) !important;
            border: 1px solid rgba(37,99,235,0.2) !important;
            border-radius: 4px !important;
            padding: 1px 6px !important;
            font-size: 0.82rem !important;
            color: #93c5fd !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Loading KRONOS enterprise data assets...")
def load_shared_data() -> tuple[dict, list[str]]:
    shared_data = {}
    missing_files = []

    for key, path in DATA_FILES.items():
        if not path.exists():
            shared_data[key] = pd.DataFrame()
            missing_files.append(str(path.relative_to(BASE_DIR)))
            continue

        try:
            shared_data[key] = pd.read_csv(path)
            if (
                key == "portfolio"
                and "ifrs_stage" in shared_data[key].columns
            ):
                shared_data[key]["ifrs_stage"] = normalize_ifrs_stage_series(
                    shared_data[key]["ifrs_stage"]
                )
        except Exception as exc:
            shared_data[key] = pd.DataFrame()
            missing_files.append(f"{path.relative_to(BASE_DIR)} | {exc}")

    return shared_data, missing_files


def render_dashboard(module_name: str, shared_data: dict) -> None:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:
        st.error(f"Dashboard import failed: {module_name}")
        st.exception(exc)
        return

    try:
        if not hasattr(module, "render"):
            st.error(f"Dashboard module '{module_name}' does not expose render(shared_data).")
            return

        module.render(shared_data)
    except Exception as exc:
        st.error(f"Dashboard execution failed: {module_name}")
        st.exception(exc)


shared_data, missing_files = load_shared_data()

with st.sidebar:
    st.markdown(
        """
        <div class="kronos-wordmark">
            <div class="kronos-shield">🛡️</div>
            <div class="kronos-brand-text">
                <div class="kronos-title">KRONOS</div>
                <div class="kronos-subtitle">Risk Intelligence Platform</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="kronos-session-badge">'
        '<span class="kronos-session-dot"></span>'
        'LIVE SESSION ACTIVE'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="kronos-divider"></div>', unsafe_allow_html=True)

    selected_page = option_menu(
        menu_title=None,
        options=list(PAGES.keys()),
        icons=[
            "speedometer2",
            "cpu",
            "activity",
            "graph-down-arrow",
            "diagram-3",
            "cash-stack",
            "terminal",
            "search",
            "broadcast",
            "file-earmark-bar-graph",
        ],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {
                "padding": "0 4px",
                "background-color": "transparent",
            },
            "icon": {
                "color": "#4a5a72",
                "font-size": "14px",
            },
            "nav-link": {
                "font-size": "13px",
                "font-weight": "500",
                "text-align": "left",
                "margin": "2px 0",
                "padding": "9px 14px",
                "color": "#7a8fa8",
                "border-radius": "8px",
                "--hover-color": "rgba(17, 30, 51, 0.9)",
                "font-family": "'IBM Plex Sans', sans-serif",
                "letter-spacing": "0.01em",
                "transition": "all 0.18s ease",
            },
            "nav-link-selected": {
                "background-color": "rgba(37, 99, 235, 0.88)",
                "color": "#ffffff",
                "font-weight": "600",
                "box-shadow": "0 2px 12px rgba(37,99,235,0.35)",
            },
        },
    )

    st.markdown('<div class="kronos-divider"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="kronos-caption">Institutional Credit Risk Command Layer</div>',
        unsafe_allow_html=True,
    )


if missing_files:
    with st.expander("⚠️  Data Loading Alerts", expanded=True):
        for missing_file in missing_files:
            st.markdown(
                f'<div class="kronos-data-alert">'
                f'<strong>MISSING</strong> &nbsp;{missing_file}'
                f'</div>',
                unsafe_allow_html=True,
            )

render_dashboard(PAGES[selected_page], shared_data)

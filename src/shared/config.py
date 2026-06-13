# =============================================================================
# KRONOS — ENTERPRISE FINANCIAL INTELLIGENCE PLATFORM
# File: src/shared/config.py
# Classification: INTERNAL — RESTRICTED
# =============================================================================
#
# Central configuration registry.  All path constants, API keys, model
# hyper-parameters, and operational thresholds are defined here and imported
# by every other module.  Never hard-code paths or settings elsewhere.
#
# =============================================================================

from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# PROJECT ROOT
# ---------------------------------------------------------------------------

ROOT_DIR: Path = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# CORE DIRECTORIES
# ---------------------------------------------------------------------------

APP_DIR:     Path = ROOT_DIR / "app"
SRC_DIR:     Path = ROOT_DIR / "src"
DATA_DIR:    Path = ROOT_DIR / "data"
MODELS_DIR:  Path = ROOT_DIR / "models"
REPORTS_DIR: Path = ROOT_DIR / "reports"
OUTPUTS_DIR: Path = ROOT_DIR / "outputs"
DOCS_DIR:    Path = ROOT_DIR / "docs"
TESTS_DIR:   Path = ROOT_DIR / "tests"
LOGS_DIR:    Path = ROOT_DIR / "logs"

# ---------------------------------------------------------------------------
# DATA DIRECTORIES
# ---------------------------------------------------------------------------

RAW_DATA_DIR:       Path = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
LIVE_DATA_DIR:      Path = DATA_DIR / "live"

# ---------------------------------------------------------------------------
# RAW DATA SOURCES
# ---------------------------------------------------------------------------

LENDING_CLUB_DIR:        Path = RAW_DATA_DIR / "lending_club"
HOME_CREDIT_DIR:         Path = RAW_DATA_DIR / "home_credit"
GERMAN_CREDIT_DIR:       Path = RAW_DATA_DIR / "german_credit"
GIVE_ME_SOME_CREDIT_DIR: Path = RAW_DATA_DIR / "give_me_some_credit"

# ---------------------------------------------------------------------------
# MASTER CREDIT DATASET
# ---------------------------------------------------------------------------

MASTER_CREDIT_DATA: Path = RAW_DATA_DIR / "master_credit_dataset.csv"

# ---------------------------------------------------------------------------
# PROCESSED DATA FILES
# ---------------------------------------------------------------------------

CLEANED_CREDIT_DATA:      Path = PROCESSED_DATA_DIR / "cleaned_credit_data.csv"
ENGINEERED_FEATURES_DATA: Path = PROCESSED_DATA_DIR / "engineered_features.csv"
MERGED_CREDIT_DATA:       Path = PROCESSED_DATA_DIR / "merged_credit_dataset.csv"
SCORED_PORTFOLIO_DATA:    Path = PROCESSED_DATA_DIR / "scored_portfolio.csv"

# ---------------------------------------------------------------------------
# LIVE DATA FILES
# ---------------------------------------------------------------------------

FRED_MARKET_DATA:    Path = LIVE_DATA_DIR / "fred_market_data.csv"
VIX_DATA:            Path = LIVE_DATA_DIR / "vix_data.csv"
SENTIMENT_DATA:      Path = LIVE_DATA_DIR / "sentiment_data.csv"
SENTIMENT_SUMMARY_DATA: Path = LIVE_DATA_DIR / "sentiment_summary.csv"

# ---------------------------------------------------------------------------
# MODEL FILES
# ---------------------------------------------------------------------------

PD_MODEL_FILE:      Path = MODELS_DIR / "pd_model.pkl"
LGD_MODEL_FILE:     Path = MODELS_DIR / "lgd_model.pkl"
EAD_MODEL_FILE:     Path = MODELS_DIR / "ead_model.pkl"
EWS_MODEL_FILE:     Path = MODELS_DIR / "ews_model.pkl"
SCALER_FILE:        Path = MODELS_DIR / "scaler.pkl"
FEATURE_COLUMNS_FILE: Path = MODELS_DIR / "feature_cols.json"
MODEL_METRICS_FILE: Path = MODELS_DIR / "model_metrics.json"

# ── LGD Artifacts ────────────────────────────────────────────────────────────
LGD_FEATURE_COLUMNS_FILE: Path = MODELS_DIR / "lgd_feature_cols.json"
LGD_SCALER_FILE:          Path = MODELS_DIR / "lgd_scaler.pkl"
LGD_METRICS_FILE:         Path = MODELS_DIR / "lgd_metrics.json"

# ── EAD Artifacts ────────────────────────────────────────────────────────────
EAD_FEATURE_COLUMNS_FILE: Path = MODELS_DIR / "ead_feature_cols.json"
EAD_SCALER_FILE:          Path = MODELS_DIR / "ead_scaler.pkl"
EAD_METRICS_FILE:         Path = MODELS_DIR / "ead_metrics.json"

# ---------------------------------------------------------------------------
# REPORT FILES
# ---------------------------------------------------------------------------

MASTER_ENTERPRISE_REPORT:   Path = REPORTS_DIR / "kronos_master_enterprise_report.pdf"
FEATURE_IMPORTANCE_REPORT:  Path = REPORTS_DIR / "feature_importance.csv"
CATEGORY_IMPORTANCE_REPORT: Path = REPORTS_DIR / "category_importance.csv"
FEATURE_SUMMARY_REPORT:     Path = REPORTS_DIR / "feature_summary.txt"

# ---------------------------------------------------------------------------
# OUTPUT DIRECTORIES
# ---------------------------------------------------------------------------

CHARTS_OUTPUT_DIR:      Path = OUTPUTS_DIR / "charts"
SHAP_OUTPUT_DIR:        Path = OUTPUTS_DIR / "shap_outputs"
STRESS_RESULTS_DIR:     Path = OUTPUTS_DIR / "stress_results"
CONTAGION_MAPS_DIR:     Path = OUTPUTS_DIR / "contagion_maps"
PORTFOLIO_ANALYSIS_DIR: Path = OUTPUTS_DIR / "portfolio_analysis"

# ---------------------------------------------------------------------------
# API CONFIGURATION
# ---------------------------------------------------------------------------

FRED_API_KEY:          str = os.getenv("FRED_API_KEY", "")
NEWS_API_KEY:          str = os.getenv("NEWS_API_KEY", "")
ALPHA_VANTAGE_API_KEY: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")

# ---------------------------------------------------------------------------
# APPLICATION SETTINGS
# ---------------------------------------------------------------------------

APP_NAME:    str  = "KRONOS"
APP_VERSION: str  = "1.0.0"
DEBUG_MODE:  bool = False

ENABLE_CACHE:            bool = True
AUTO_REFRESH_SECONDS:    int  = 300
EXECUTIVE_REFRESH_SECONDS: int = 300
DEFAULT_CHART_HEIGHT:    int  = 450
DEFAULT_TABLE_HEIGHT:    int  = 400
MAX_DASHBOARD_ROWS:      int  = 1000

# ---------------------------------------------------------------------------
# STREAMLIT SETTINGS
# ---------------------------------------------------------------------------

STREAMLIT_PAGE_TITLE:   str = "KRONOS | Enterprise Risk Intelligence"
STREAMLIT_LAYOUT:       str = "wide"
STREAMLIT_SIDEBAR_STATE: str = "expanded"

# ---------------------------------------------------------------------------
# MODEL SETTINGS
# ---------------------------------------------------------------------------

RANDOM_STATE:           int   = 42
TEST_SIZE:              float = 0.20
VALIDATION_SIZE:        float = 0.10
DEFAULT_N_ESTIMATORS:   int   = 300
DEFAULT_MAX_DEPTH:      int   = 6
DEFAULT_LEARNING_RATE:  float = 0.05

# ---------------------------------------------------------------------------
# RISK SETTINGS
# ---------------------------------------------------------------------------

PD_WARNING_THRESHOLD:  float = 0.25
PD_HIGH_RISK_THRESHOLD: float = 0.50
VIX_WARNING_LEVEL:     int   = 25
VIX_CRISIS_LEVEL:      int   = 40

# ---------------------------------------------------------------------------
# DECISION THRESHOLDS
# ---------------------------------------------------------------------------

DECISION_APPROVE_THRESHOLD:              int = 25
DECISION_REVIEW_THRESHOLD:               int = 50
DECISION_WATCHLIST_THRESHOLD:            int = 70
DECISION_ENHANCED_MONITORING_THRESHOLD:  int = 85

# ---------------------------------------------------------------------------
# RISK PULSE THRESHOLDS
# ---------------------------------------------------------------------------

RISK_PULSE_LOW:      int = 25
RISK_PULSE_MODERATE: int = 50
RISK_PULSE_HIGH:     int = 75
RISK_PULSE_CRITICAL: int = 90

# ---------------------------------------------------------------------------
# REGIME THRESHOLDS
# ---------------------------------------------------------------------------

REGIME_STABLE:   int = 25
REGIME_ELEVATED: int = 50
REGIME_STRESSED: int = 75
REGIME_CRISIS:   int = 90

# ---------------------------------------------------------------------------
# ALERT THRESHOLDS
# ---------------------------------------------------------------------------

ALERT_RISK_PULSE_CRITICAL: int = 85
ALERT_STRESS_CRITICAL:     int = 80
ALERT_SYSTEMIC_CRITICAL:   int = 75
ALERT_RESERVE_CRITICAL:    int = 70

# ---------------------------------------------------------------------------
# CACHE SETTINGS
# ---------------------------------------------------------------------------

CACHE_TTL_SECONDS: int  = 3600
ENABLE_DISK_CACHE: bool = True

# ---------------------------------------------------------------------------
# LOGGING SETTINGS
# ---------------------------------------------------------------------------

LOG_LEVEL:            str  = "INFO"
ENABLE_MODEL_LOGGING: bool = True
ENABLE_API_LOGGING:   bool = True

# ---------------------------------------------------------------------------
# STRESS SCENARIOS
# ---------------------------------------------------------------------------

RESERVE_STRESS_SCENARIOS: dict[str, dict[str, float]] = {
    "BASELINE": {
        "pd_multiplier": 1.00,
        "lgd_multiplier": 1.00,
        "ead_multiplier": 1.00,
    },
    "MILD RECESSION": {
        "pd_multiplier": 1.25,
        "lgd_multiplier": 1.10,
        "ead_multiplier": 1.05,
    },
    "SEVERE RECESSION": {
        "pd_multiplier": 1.70,
        "lgd_multiplier": 1.35,
        "ead_multiplier": 1.20,
    },
    "FINANCIAL CRISIS": {
        "pd_multiplier": 2.40,
        "lgd_multiplier": 1.60,
        "ead_multiplier": 1.40,
    },
}

CREDIT_STRESS_SCENARIOS: dict[str, dict[str, float]] = {
    "BASELINE": {
        "pd_multiplier": 1.00,
        "lgd_multiplier": 1.00,
        "ead_multiplier": 1.00,
        "unemployment_shock": 0,
        "interest_rate_shock": 0,
        "inflation_shock": 0,
    },
    "MILD RECESSION": {
        "pd_multiplier": 1.25,
        "lgd_multiplier": 1.10,
        "ead_multiplier": 1.05,
        "unemployment_shock": 1.5,
        "interest_rate_shock": 0.75,
        "inflation_shock": 1.2,
    },
    "SEVERE RECESSION": {
        "pd_multiplier": 1.80,
        "lgd_multiplier": 1.35,
        "ead_multiplier": 1.20,
        "unemployment_shock": 4.0,
        "interest_rate_shock": 2.25,
        "inflation_shock": 3.5,
    },
    "FINANCIAL CRISIS": {
        "pd_multiplier": 2.60,
        "lgd_multiplier": 1.60,
        "ead_multiplier": 1.45,
        "unemployment_shock": 7.0,
        "interest_rate_shock": 4.0,
        "inflation_shock": 6.0,
    },
}

MACRO_STRESS_SCENARIOS: dict[str, dict[str, float]] = {
    "BASELINE": {
        "gdp_shock": 0.0,
        "unemployment_shock": 0.0,
        "inflation_shock": 0.0,
        "interest_rate_shock": 0.0,
        "market_volatility_shock": 0.0,
    },
    "MILD RECESSION": {
        "gdp_shock": -1.5,
        "unemployment_shock": 1.5,
        "inflation_shock": 1.0,
        "interest_rate_shock": 0.75,
        "market_volatility_shock": 12,
    },
    "SEVERE RECESSION": {
        "gdp_shock": -4.5,
        "unemployment_shock": 4.0,
        "inflation_shock": 3.5,
        "interest_rate_shock": 2.25,
        "market_volatility_shock": 28,
    },
    "FINANCIAL CRISIS": {
        "gdp_shock": -8.0,
        "unemployment_shock": 7.5,
        "inflation_shock": 6.0,
        "interest_rate_shock": 4.5,
        "market_volatility_shock": 45,
    },
}

# ---------------------------------------------------------------------------
# DIRECTORY BOOTSTRAP  —  create all required directories on import
# ---------------------------------------------------------------------------

_DIRECTORIES_TO_CREATE: list[Path] = [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    LIVE_DATA_DIR,
    MODELS_DIR,
    REPORTS_DIR,
    OUTPUTS_DIR,
    LOGS_DIR,
    CHARTS_OUTPUT_DIR,
    SHAP_OUTPUT_DIR,
    STRESS_RESULTS_DIR,
    CONTAGION_MAPS_DIR,
    PORTFOLIO_ANALYSIS_DIR,
]

for _directory in _DIRECTORIES_TO_CREATE:
    _directory.mkdir(parents=True, exist_ok=True)

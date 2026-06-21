from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
WAREHOUSE_DIR = ROOT_DIR / "data" / "warehouse"
WAREHOUSE_DB = WAREHOUSE_DIR / "kronos_risk.duckdb"
SQL_DIR = ROOT_DIR / "sql"


@dataclass(frozen=True)
class CsvSource:
    source_name: str
    relative_path: str
    staging_table: str
    source_domain: str

    @property
    def path(self) -> Path:
        return ROOT_DIR / self.relative_path


CSV_SOURCES = (
    CsvSource("master_credit", "data/raw/master_credit_dataset.csv", "stg_master_credit", "CREDIT"),
    CsvSource("cleaned_credit", "data/processed/cleaned_credit_data.csv", "stg_cleaned_credit", "CREDIT"),
    CsvSource("engineered_features", "data/processed/engineered_features.csv", "stg_engineered_features", "CREDIT"),
    CsvSource("merged_credit", "data/processed/merged_credit_dataset.csv", "stg_merged_credit", "CREDIT"),
    CsvSource("scored_portfolio", "data/processed/scored_portfolio.csv", "stg_scored_portfolio", "CREDIT"),
    CsvSource("fred_observation", "data/live/fred_market_data.csv", "stg_fred_observation", "MARKET"),
    CsvSource("vix_observation", "data/live/vix_data.csv", "stg_vix_observation", "MARKET"),
    CsvSource("market_observation", "data/live/alpha_vantage_market_data.csv", "stg_market_observation", "MARKET"),
    CsvSource("sentiment_detail", "data/live/sentiment_data.csv", "stg_sentiment_detail", "MARKET"),
    CsvSource("sentiment_summary", "data/live/sentiment_summary.csv", "stg_sentiment_summary", "MARKET"),
    CsvSource("feature_importance", "reports/feature_importance.csv", "stg_feature_importance", "MODEL_RISK"),
    CsvSource("category_importance", "reports/category_importance.csv", "stg_category_importance", "MODEL_RISK"),
    CsvSource("calibration_decile", "outputs/calibration/decile_analysis.csv", "stg_calibration_decile", "MODEL_RISK"),
    CsvSource("challenger_comparison", "outputs/challenger_models/model_comparison.csv", "stg_challenger_comparison", "MODEL_RISK"),
    CsvSource("challenger_performance", "outputs/challenger_models/model_performance_table.csv", "stg_challenger_performance", "MODEL_RISK"),
    CsvSource("oot_summary", "outputs/oot_validation/oot_summary.csv", "stg_oot_summary", "MODEL_RISK"),
    CsvSource("oot_risk_band_shift", "outputs/oot_validation/risk_band_distribution_shift.csv", "stg_oot_risk_band_shift", "MODEL_RISK"),
    CsvSource("oot_score_shift", "outputs/oot_validation/score_distribution_shift.csv", "stg_oot_score_shift", "MODEL_RISK"),
)

ARTIFACT_ROOTS = (
    ROOT_DIR / "data",
    ROOT_DIR / "models",
    ROOT_DIR / "outputs",
    ROOT_DIR / "reports",
    SQL_DIR / "phase4d",
)

JSON_ROOTS = (
    ROOT_DIR / "data" / "live",
    ROOT_DIR / "models",
    ROOT_DIR / "outputs",
)

SCHEMA_SQL_FILES = (
    SQL_DIR / "ddl" / "001_schemas.sql",
    SQL_DIR / "ddl" / "002_control_tables.sql",
    SQL_DIR / "ddl" / "003_staging_tables.sql",
    SQL_DIR / "ddl" / "004_dimensions.sql",
    SQL_DIR / "ddl" / "005_fact_tables.sql",
    SQL_DIR / "ddl" / "006_marts.sql",
)

CONTROL_VIEW_SQL_FILES = (
    SQL_DIR / "views" / "reconciliation_views.sql",
)

MART_SQL_FILES = (
    SQL_DIR / "views" / "current_portfolio_views.sql",
    *CONTROL_VIEW_SQL_FILES,
    SQL_DIR / "marts" / "credit_risk_mart.sql",
    SQL_DIR / "marts" / "ifrs9_stage_mart.sql",
    SQL_DIR / "marts" / "ews_mart.sql",
    SQL_DIR / "marts" / "model_risk_mart.sql",
    SQL_DIR / "marts" / "executive_mart.sql",
)

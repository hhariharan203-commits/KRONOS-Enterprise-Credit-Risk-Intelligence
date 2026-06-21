from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
TEMPORAL_ROOT = ROOT_DIR / "temporal_platform"
TEMPORAL_DATABASE = TEMPORAL_ROOT / "warehouse" / "kronos_temporal_risk.duckdb"
PHASE2C_EVIDENCE_DIR = TEMPORAL_ROOT / "evidence" / "phase2c"
CURRENT_WAREHOUSE = ROOT_DIR / "data" / "warehouse" / "kronos_risk.duckdb"
SCORED_PORTFOLIO = ROOT_DIR / "data" / "processed" / "scored_portfolio.csv"

SQL_DIR = ROOT_DIR / "sql" / "phase2c" / "ddl"
DDL_FILES = (
    SQL_DIR / "001_migration_control_tables.sql",
    SQL_DIR / "002_migration_lineage_tables.sql",
)

SPECIFICATION_NAMES = ("PHASE2C_IMPLEMENTATION_SPEC_FINAL.md",)

BUSINESS_SCHEMAS = ("control", "staging", "reference", "core", "mart")
EXPECTED_SCHEMA_COUNT = 5
EXPECTED_TABLE_COUNT = 46
EXPECTED_VIEW_COUNT = 0
PHASE2C_RELEASE_VERSION = "2C.0"

PHASE2C_TABLES = {
    "control.migration_readiness_run",
    "control.migration_snapshot_pair",
    "control.migration_transition_contract",
    "control.migration_quality_result",
    "control.migration_readiness_result",
    "control.migration_reconciliation_result",
    "control.migration_lineage_node",
    "control.migration_lineage_edge",
    "control.migration_column_lineage",
    "control.migration_publish_status",
}

PROTECTED_ROOTS = (
    "app",
    "src",
    "tests",
    "docs",
    "sql",
    "models",
    "data",
    "outputs",
    "reports",
    "analytics",
)

AUTHORIZED_PREFIXES = (
    "src/temporal_risk/migration_readiness/",
    "sql/phase2c/",
    "tests/test_phase2c_",
    "docs/PHASE2C_",
    "docs/MIGRATION_READINESS_",
)

AUTHORIZED_FILES = {
    "src/temporal_risk/pipeline.py",
    "src/temporal_risk/historical_ingestion/config.py",
    "src/temporal_risk/historical_ingestion/contracts.py",
    "src/temporal_risk/historical_ingestion/pipeline.py",
}

VOLATILE_GENERATED_FILES = {
    "data/live/live_intelligence_cache.json",
    "outputs/artifact_lineage.json",
    "reports/test_kronos_enterprise_report.pdf",
}

EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    "venv",
    ".venv",
}

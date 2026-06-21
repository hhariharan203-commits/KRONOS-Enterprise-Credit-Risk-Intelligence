from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
TEMPORAL_ROOT = ROOT_DIR / "temporal_platform"
TEMPORAL_DATABASE = TEMPORAL_ROOT / "warehouse" / "kronos_temporal_risk.duckdb"
PHASE2B_BACKUP_DIR = TEMPORAL_ROOT / "backups"
PHASE2B_EVIDENCE_DIR = TEMPORAL_ROOT / "evidence" / "phase2b"
OBSERVED_INBOUND_DIR = TEMPORAL_ROOT / "inbound" / "observed"
SIMULATED_INBOUND_DIR = TEMPORAL_ROOT / "inbound" / "simulated"
CURRENT_WAREHOUSE = ROOT_DIR / "data" / "warehouse" / "kronos_risk.duckdb"
SCORED_PORTFOLIO = ROOT_DIR / "data" / "processed" / "scored_portfolio.csv"

SQL_DIR = ROOT_DIR / "sql" / "phase2b" / "ddl"
DDL_FILES = (
    SQL_DIR / "001_reference_extensions.sql",
    SQL_DIR / "002_control_tables.sql",
    SQL_DIR / "003_staging_tables.sql",
    SQL_DIR / "004_core_dimensions.sql",
    SQL_DIR / "005_core_facts.sql",
)

SPECIFICATION_NAMES = (
    "PHASE2B_IMPLEMENTATION_PLAN.md",
    "PHASE2B_PRE_IMPLEMENTATION_AUDIT.md",
    "PHASE2B_IMPLEMENTATION_SPEC_FINAL.md",
)

BUSINESS_SCHEMAS = ("control", "staging", "reference", "core", "mart")
PHASE2B_RELEASE_VERSION = "2B.0"
EXPECTED_SCHEMA_COUNT = 5
EXPECTED_TABLE_COUNT = 36
EXPECTED_VIEW_COUNT = 0
PHASE2C_EXPECTED_TABLE_COUNT = 46

PHASE2B_TABLES = {
    "reference.dim_identity_grain",
    "reference.dim_readiness_status",
    "control.historical_ingestion_batch",
    "control.historical_ingestion_file",
    "control.historical_field_mapping",
    "control.historical_reject_record",
    "control.data_readiness_result",
    "control.historical_reconciliation_result",
    "control.historical_lineage_node",
    "control.historical_lineage_edge",
    "control.historical_column_lineage",
    "control.historical_publish_status",
    "staging.stg_historical_snapshot_row",
    "staging.stg_historical_event_row",
    "core.dim_historical_entity",
    "core.dim_historical_facility",
    "core.dim_historical_snapshot",
    "core.fact_historical_credit_observation",
    "core.fact_historical_credit_event",
}
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
    "src/temporal_risk/historical_ingestion/",
    "sql/phase2b/",
    "tests/test_phase2b_",
    "docs/PHASE2B_",
    "docs/HISTORICAL_",
)
AUTHORIZED_FILES = {
    "src/temporal_risk/pipeline.py",
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

from __future__ import annotations

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
TEMPORAL_ROOT = ROOT_DIR / "temporal_platform"
TEMPORAL_WAREHOUSE_DIR = TEMPORAL_ROOT / "warehouse"
TEMPORAL_DATABASE = TEMPORAL_WAREHOUSE_DIR / "kronos_temporal_risk.duckdb"
TEMPORAL_BACKUP_DIR = TEMPORAL_ROOT / "backups"
TEMPORAL_EVIDENCE_DIR = TEMPORAL_ROOT / "evidence" / "phase2a"

CURRENT_WAREHOUSE = ROOT_DIR / "data" / "warehouse" / "kronos_risk.duckdb"
SCORED_PORTFOLIO = ROOT_DIR / "data" / "processed" / "scored_portfolio.csv"
PHASE4_ARTIFACT_ROOTS = (
    ROOT_DIR / "data",
    ROOT_DIR / "models",
    ROOT_DIR / "outputs",
    ROOT_DIR / "reports",
)

SQL_DIR = ROOT_DIR / "sql" / "phase2a" / "ddl"
DDL_FILES = (
    SQL_DIR / "001_schemas.sql",
    SQL_DIR / "002_reference_tables.sql",
    SQL_DIR / "003_control_tables.sql",
    SQL_DIR / "004_staging_tables.sql",
)

SPECIFICATION_NAMES = (
    "PHASE2_IMPACT_ANALYSIS.md",
    "PHASE2_IMPLEMENTATION_BLUEPRINT.md",
    "PHASE2A_IMPLEMENTATION_PLAN.md",
    "PHASE2A_PRE_IMPLEMENTATION_AUDIT.md",
    "PHASE2A_IMPLEMENTATION_PROMPT.md",
    "PHASE2A_SPEC_FINALIZATION.md",
)

BUSINESS_SCHEMAS = ("control", "staging", "reference", "core", "mart")
EXPECTED_TABLE_COUNT = 17
EXPECTED_VIEW_COUNT = 0
PHASE_NAME = "PHASE2A"
RELEASE_VERSION = "2A.1"

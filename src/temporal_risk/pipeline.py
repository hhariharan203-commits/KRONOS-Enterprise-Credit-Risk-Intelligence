from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.temporal_risk.audit import (
    finish_deployment,
    record_publish_transition,
    register_release,
    set_release_status,
    start_deployment,
)
from src.temporal_risk.config import (
    BUSINESS_SCHEMAS,
    CURRENT_WAREHOUSE,
    PHASE4_ARTIFACT_ROOTS,
    ROOT_DIR,
    SCORED_PORTFOLIO,
    SPECIFICATION_NAMES,
    TEMPORAL_DATABASE,
    TEMPORAL_EVIDENCE_DIR,
    TEMPORAL_ROOT,
)
from src.temporal_risk.connection import (
    assert_evidence_target,
    assert_temporal_target,
    connect_temporal,
    discard_working_database,
    file_sha256,
    prepare_working_database,
    publish_working_database,
)
from src.temporal_risk.contracts import (
    BASELINE_MISMATCH,
    BASELINE_SPECIFICATION_MISSING,
    PHASE2A_SCOPE_VIOLATION,
    PHASE2A_SUCCESS,
    PHASE2A_VALIDATION_FAILED,
    TEMPORAL_PLATFORM_UNAVAILABLE,
    BaselineMismatchError,
    BaselineSpecificationError,
    Phase2AScopeError,
    Phase2AValidationError,
    enforce_scope,
)
from src.temporal_risk.data_quality import run_quality_checks
from src.temporal_risk.lineage import build_lineage
from src.temporal_risk.reconciliation import run_reconciliations
from src.temporal_risk.schema_manager import initialize_schema, validate_catalog
from src.temporal_risk.snapshot_registry import (
    register_contracts,
    register_reference_data,
    register_snapshot,
)
from src.temporal_risk.source_registry import (
    profile_source,
    register_source,
    serializable_profile,
)


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
APPROVED_PREFIXES = (
    "src/temporal_risk/",
    "sql/phase2a/",
    "tests/test_phase2a_",
    "docs/PHASE2A_COMPLETION_REPORT.md",
    "docs/TEMPORAL_PLATFORM_ARCHITECTURE.md",
    "docs/TEMPORAL_CONTROL_DATA_DICTIONARY.md",
    "docs/TEMPORAL_GOVERNANCE_STANDARD.md",
    "docs/TEMPORAL_PLATFORM_OPERATIONS.md",
    "temporal_platform/",
)
APPROVED_FILES = {".gitignore"}
EXCLUDED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".git",
    "venv",
    ".venv",
}
FORBIDDEN_IMPORT_PREFIXES = (
    "app",
    "src.enterprise_data",
    "src.credit_risk",
    "src.model_validation",
    "src.provisioning",
    "src.ews",
    "src.stress_testing",
    "src.contagion",
    "src.decisioning",
    "src.reporting",
)
PHASE2A_UPGRADE_PRESENT = "PHASE2A_UPGRADE_PRESENT"
PHASE2A_TABLES = {
    "control.column_lineage",
    "control.deployment_run",
    "control.lineage_edge",
    "control.lineage_node",
    "control.platform_release",
    "control.publish_status",
    "control.reconciliation_result",
    "control.rollback_event",
    "control.snapshot_registry",
    "control.snapshot_source_link",
    "control.source_asset",
    "control.source_column",
    "control.temporal_contract",
    "control.temporal_quality_result",
    "reference.dim_snapshot_status",
    "reference.dim_temporal_classification",
    "staging.stg_snapshot_manifest",
}
PHASE2B_TABLES = {
    "control.data_readiness_result",
    "control.historical_column_lineage",
    "control.historical_field_mapping",
    "control.historical_ingestion_batch",
    "control.historical_ingestion_file",
    "control.historical_lineage_edge",
    "control.historical_lineage_node",
    "control.historical_publish_status",
    "control.historical_reconciliation_result",
    "control.historical_reject_record",
    "core.dim_historical_entity",
    "core.dim_historical_facility",
    "core.dim_historical_snapshot",
    "core.fact_historical_credit_event",
    "core.fact_historical_credit_observation",
    "reference.dim_identity_grain",
    "reference.dim_readiness_status",
    "staging.stg_historical_event_row",
    "staging.stg_historical_snapshot_row",
}
PHASE2C_TABLES = {
    "control.migration_column_lineage",
    "control.migration_lineage_edge",
    "control.migration_lineage_node",
    "control.migration_publish_status",
    "control.migration_quality_result",
    "control.migration_readiness_result",
    "control.migration_readiness_run",
    "control.migration_reconciliation_result",
    "control.migration_snapshot_pair",
    "control.migration_transition_contract",
}


def _json_ready(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_json_ready(payload), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def specification_inventory() -> dict:
    inventory = {}
    for name in SPECIFICATION_NAMES:
        matches = []
        direct = ROOT_DIR / name
        if direct.is_file():
            matches.append(direct)
        for search_root in (
            ROOT_DIR / "docs",
            ROOT_DIR / "src",
            ROOT_DIR / "tests",
            ROOT_DIR / "sql",
        ):
            if search_root.exists():
                matches.extend(
                    path for path in search_root.rglob(name) if path.is_file()
                )
        expected = ROOT_DIR / "docs" / name
        if len(matches) != 1 or matches[0].resolve() != expected.resolve():
            raise BaselineSpecificationError(
                f"{BASELINE_SPECIFICATION_MISSING}: {name}; "
                f"matches={[str(path) for path in matches]}"
            )
        path = matches[0]
        sha256 = file_sha256(path)
        if len(sha256) != 64:
            raise BaselineSpecificationError(
                f"{BASELINE_SPECIFICATION_MISSING}: invalid SHA-256 for {name}"
            )
        inventory[name] = {
            "status": "FILE_CONTROLLED",
            "relative_path": path.resolve().relative_to(ROOT_DIR.resolve()).as_posix(),
            "sha256": sha256,
        }
    return inventory


def current_warehouse_state(database_path: Path = CURRENT_WAREHOUSE) -> dict:
    import duckdb

    path = database_path.resolve()
    connection = duckdb.connect(str(path), read_only=True)
    try:
        placeholders = ",".join("?" for _ in BUSINESS_SCHEMAS)
        schemas = int(
            connection.execute(
                f"""
                SELECT COUNT(*) FROM information_schema.schemata
                WHERE schema_name IN ({placeholders})
                """,
                list(BUSINESS_SCHEMAS),
            ).fetchone()[0]
        )
        tables = int(
            connection.execute(
                f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema IN ({placeholders})
                  AND table_type = 'BASE TABLE'
                """,
                list(BUSINESS_SCHEMAS),
            ).fetchone()[0]
        )
        views = int(
            connection.execute(
                f"""
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema IN ({placeholders})
                  AND table_type = 'VIEW'
                """,
                list(BUSINESS_SCHEMAS),
            ).fetchone()[0]
        )
        artifact_count = int(
            connection.execute("SELECT COUNT(*) FROM control.artifact_registry").fetchone()[0]
        )
    finally:
        connection.close()
    return {
        "database_path": path.as_posix(),
        "sha256": file_sha256(path),
        "schema_count": schemas,
        "table_count": tables,
        "view_count": views,
        "artifact_registry_count": artifact_count,
    }


def _profile_comparison(profile: dict) -> dict:
    return {
        "sha256": profile["sha256_before"],
        "row_count": profile["row_count"],
        "column_count": profile["column_count"],
        "canonical_schema_hash": profile["canonical_schema_hash"],
        "distinct_borrower_count": profile["distinct_borrower_count"],
        "run_ids": profile["run_ids"],
        "model_versions": profile["model_versions"],
        "timestamps": profile["timestamps"],
        "scoring_status": profile["scoring_status"],
    }


def baseline_state(
    *,
    current_warehouse: Path = CURRENT_WAREHOUSE,
    scored_portfolio: Path = SCORED_PORTFOLIO,
) -> dict:
    profile = profile_source(scored_portfolio)
    return {
        "warehouse": current_warehouse_state(current_warehouse),
        "scored_portfolio": _profile_comparison(profile),
    }


def compare_baselines(before: dict, after: dict) -> dict:
    matches = before == after
    return {
        "status": "PASS" if matches else "FAIL",
        "matches": matches,
        "before": before,
        "after": after,
    }


def _approved_relative(relative: str) -> bool:
    return relative in APPROVED_FILES or any(
        relative.startswith(prefix) for prefix in APPROVED_PREFIXES
    )


def protected_hash_inventory() -> dict:
    inventory = {}
    candidates = []
    for root_name in PROTECTED_ROOTS:
        root = ROOT_DIR / root_name
        if root.exists():
            candidates.extend(path for path in root.rglob("*") if path.is_file())
    for root_file in ("README.md", "requirements.txt", "requirements-dev.txt"):
        path = ROOT_DIR / root_file
        if path.is_file():
            candidates.append(path)
    for path in sorted(set(candidates)):
        relative = path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if _approved_relative(relative):
            continue
        inventory[relative] = file_sha256(path)
    return inventory


def validate_source_path(source_path: Path) -> bool:
    resolved = source_path.resolve()
    return (
        resolved == SCORED_PORTFOLIO.resolve()
        and resolved.is_relative_to(ROOT_DIR.resolve())
    )


def validate_scope_boundary() -> dict:
    enforce_scope()
    package_root = ROOT_DIR / "src" / "temporal_risk"
    violations = []
    for path in package_root.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                if name.startswith(FORBIDDEN_IMPORT_PREFIXES):
                    violations.append(f"{path.name}:{name}")
    sql_root = ROOT_DIR / "sql" / "phase2a"
    for path in sql_root.rglob("*.sql"):
        text = path.read_text(encoding="utf-8").upper()
        for prohibited in ("CREATE VIEW", "CREATE TABLE CORE.", "CREATE TABLE MART."):
            if prohibited in text:
                violations.append(f"{path.name}:{prohibited}")
    if violations:
        raise Phase2AScopeError(
            f"{PHASE2A_SCOPE_VIOLATION}: " + ", ".join(violations)
        )
    return {"status": "PASS", "violations": [], "independently_removable": True}


def phase2b_upgrade_present(database_path: Path | str) -> bool:
    path = Path(database_path).resolve()
    if not path.is_file():
        return False
    connection = connect_temporal(path, read_only=True)
    try:
        rows = connection.execute(
            """
            SELECT table_schema, table_name, table_type
            FROM information_schema.tables
            WHERE table_schema IN ('control', 'staging', 'reference', 'core', 'mart')
            """
        ).fetchall()
        schemas = {
            row[0]
            for row in connection.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name IN ('control', 'staging', 'reference', 'core', 'mart')
                """
            ).fetchall()
        }
    finally:
        connection.close()
    tables = {f"{schema}.{table}" for schema, table, kind in rows if kind == "BASE TABLE"}
    views = {f"{schema}.{table}" for schema, table, kind in rows if kind == "VIEW"}
    recognized_tables = (
        PHASE2A_TABLES | PHASE2B_TABLES,
        PHASE2A_TABLES | PHASE2B_TABLES | PHASE2C_TABLES,
    )
    return (
        schemas == set(BUSINESS_SCHEMAS)
        and tables in recognized_tables
        and not views
        and not any(name.startswith("mart.") for name in tables)
    )


def _table_counts(connection) -> dict:
    names = [
        ("reference", "dim_temporal_classification"),
        ("reference", "dim_snapshot_status"),
        ("control", "platform_release"),
        ("control", "deployment_run"),
        ("control", "source_asset"),
        ("control", "source_column"),
        ("control", "temporal_contract"),
        ("control", "snapshot_registry"),
        ("control", "snapshot_source_link"),
        ("control", "temporal_quality_result"),
        ("control", "reconciliation_result"),
        ("control", "lineage_node"),
        ("control", "lineage_edge"),
        ("control", "column_lineage"),
        ("control", "publish_status"),
        ("control", "rollback_event"),
        ("staging", "stg_snapshot_manifest"),
    ]
    return {
        f"{schema}.{table}": int(
            connection.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
        )
        for schema, table in names
    }


def run_phase2a(
    database_path: Path | str = TEMPORAL_DATABASE,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
    evidence_dir: Path | str = TEMPORAL_EVIDENCE_DIR,
    current_warehouse: Path | str = CURRENT_WAREHOUSE,
    scored_portfolio: Path | str = SCORED_PORTFOLIO,
    capture_protected_hashes: bool = True,
) -> dict:
    database_path = Path(database_path)
    runtime_root = Path(runtime_root)
    evidence_dir = Path(evidence_dir)
    current_warehouse = Path(current_warehouse)
    scored_portfolio = Path(scored_portfolio)

    scope = validate_scope_boundary()
    assert_temporal_target(database_path, runtime_root=runtime_root)
    evidence_root = assert_evidence_target(
        evidence_dir,
        runtime_root=runtime_root,
    )
    if phase2b_upgrade_present(database_path):
        return {
            "status": PHASE2A_UPGRADE_PRESENT,
            "application_impact": "NONE",
            "database_path": str(database_path.resolve()),
        }
    specs = specification_inventory()
    deployment_id = uuid4().hex.upper()
    run_evidence_dir = evidence_root / deployment_id
    protected_before = (
        protected_hash_inventory() if capture_protected_hashes else {}
    )
    baseline_before = baseline_state(
        current_warehouse=current_warehouse,
        scored_portfolio=scored_portfolio,
    )
    source_profile = profile_source(scored_portfolio)

    run_evidence_dir.mkdir(parents=True, exist_ok=False)
    write_json(run_evidence_dir / "specification_hash_inventory.json", specs)
    write_json(run_evidence_dir / "protected_hashes_before.json", protected_before)
    write_json(run_evidence_dir / "baseline_verification.json", {"before": baseline_before})
    write_json(
        run_evidence_dir / "source_profile.json",
        serializable_profile(source_profile),
    )

    working = prepare_working_database(
        database_path,
        runtime_root=runtime_root,
    )
    connection = connect_temporal(
        working.working_path,
        read_only=False,
        deployment_authorized=True,
        runtime_root=working.working_path.parent,
    )
    result = None
    try:
        initialize_schema(connection)
        catalog = validate_catalog(connection)
        release_id = register_release(
            connection,
            database_path=database_path.resolve().as_posix(),
            specification_inventory=specs,
            catalog=catalog,
        )
        start_deployment(connection, deployment_id, release_id)
        record_publish_transition(
            connection,
            deployment_id,
            previous_status=None,
            new_status="DRAFT",
            details="Isolated Phase 2A control deployment started.",
        )

        register_reference_data(connection)
        contracts = register_contracts(connection)
        source_asset_id = register_source(connection, source_profile)
        snapshot_id = register_snapshot(
            connection,
            deployment_id=deployment_id,
            source_asset_id=source_asset_id,
            profile=source_profile,
            contract=contracts["CURRENT_STATE_BASELINE"],
        )
        quality = run_quality_checks(
            connection,
            deployment_id=deployment_id,
            snapshot_id=snapshot_id,
            profile=source_profile,
            baseline_profile=baseline_before["scored_portfolio"],
            source_path_valid=validate_source_path(scored_portfolio),
        )
        reconciliation = run_reconciliations(
            connection,
            deployment_id=deployment_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            profile=source_profile,
            baseline_profile=baseline_before["scored_portfolio"],
        )
        lineage = build_lineage(
            connection,
            deployment_id=deployment_id,
            source_asset_id=source_asset_id,
            source_hash=source_profile["sha256_before"],
            contract=contracts["CURRENT_STATE_BASELINE"],
            snapshot_id=snapshot_id,
            release_id=release_id,
        )
        if (
            quality["check_count"] != 27
            or quality["failure_count"] != 0
            or reconciliation["reconciliation_count"] != 9
            or reconciliation["failure_count"] != 0
            or not lineage["complete"]
        ):
            raise Phase2AValidationError(PHASE2A_VALIDATION_FAILED)

        baseline_pre_publish = baseline_state(
            current_warehouse=current_warehouse,
            scored_portfolio=scored_portfolio,
        )
        comparison = compare_baselines(baseline_before, baseline_pre_publish)
        if not comparison["matches"]:
            raise BaselineMismatchError(BASELINE_MISMATCH)

        record_publish_transition(
            connection,
            deployment_id,
            previous_status="DRAFT",
            new_status="VALIDATED",
            details="DQ, reconciliation, lineage, scope and baseline controls passed.",
        )
        record_publish_transition(
            connection,
            deployment_id,
            previous_status="VALIDATED",
            new_status="PUBLISHED",
            details="Authorized for isolated file publication.",
        )
        set_release_status(connection, release_id, "PUBLISHED")
        finish_deployment(
            connection,
            deployment_id,
            status=PHASE2A_SUCCESS,
            source_sha256=source_profile["sha256_before"],
        )
        table_counts = _table_counts(connection)
        connection.execute("CHECKPOINT")
        result = {
            "status": PHASE2A_SUCCESS,
            "deployment_id": deployment_id,
            "release_id": release_id,
            "source_asset_id": source_asset_id,
            "snapshot_id": snapshot_id,
            "catalog": catalog,
            "table_counts": table_counts,
            "quality": quality,
            "reconciliation": reconciliation,
            "lineage": lineage,
            "scope": scope,
            "baseline_pre_publish": comparison,
            "backup_path": str(working.backup_path) if working.backup_path else None,
            "evidence_directory": str(run_evidence_dir),
        }
    except Exception as exc:
        try:
            finish_deployment(
                connection,
                deployment_id,
                status=type(exc).__name__,
                source_sha256=source_profile["sha256_before"],
                error=exc,
            )
            connection.execute("CHECKPOINT")
        except Exception:
            pass
        raise
    finally:
        connection.close()

    try:
        publish_working_database(working)
    except Exception:
        discard_working_database(working)
        raise

    published_hash = file_sha256(database_path)
    baseline_after = baseline_state(
        current_warehouse=current_warehouse,
        scored_portfolio=scored_portfolio,
    )
    baseline_comparison = compare_baselines(baseline_before, baseline_after)
    protected_after = (
        protected_hash_inventory() if capture_protected_hashes else {}
    )
    protected_match = protected_before == protected_after
    if not baseline_comparison["matches"] or not protected_match:
        raise BaselineMismatchError(BASELINE_MISMATCH)

    read_only = connect_temporal(database_path, read_only=True)
    try:
        published_catalog = validate_catalog(read_only)
        published_counts = _table_counts(read_only)
    finally:
        read_only.close()

    baseline_payload = {
        "before": baseline_before,
        "after": baseline_after,
        "comparison": baseline_comparison["status"],
    }
    compatibility = {
        "status": "PASS",
        "baseline_unchanged": baseline_comparison["matches"],
        "protected_hashes_unchanged": protected_match,
        "current_warehouse_unchanged": (
            baseline_before["warehouse"] == baseline_after["warehouse"]
        ),
        "scored_portfolio_unchanged": (
            baseline_before["scored_portfolio"]
            == baseline_after["scored_portfolio"]
        ),
        "phase4_artifact_roots_exclude_temporal_platform": all(
            not TEMPORAL_ROOT.resolve().is_relative_to(root.resolve())
            for root in PHASE4_ARTIFACT_ROOTS
        ),
        "independently_removable": True,
    }
    deployment_manifest = {
        **result,
        "database_path": str(database_path.resolve()),
        "database_sha256": published_hash,
        "published_catalog": published_catalog,
        "published_table_counts": published_counts,
        "compatibility": compatibility,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    write_json(run_evidence_dir / "protected_hashes_after.json", protected_after)
    write_json(run_evidence_dir / "baseline_verification.json", baseline_payload)
    write_json(run_evidence_dir / "database_catalog.json", published_catalog)
    write_json(run_evidence_dir / "quality_summary.json", result["quality"])
    write_json(
        run_evidence_dir / "reconciliation_summary.json",
        result["reconciliation"],
    )
    write_json(run_evidence_dir / "lineage_manifest.json", result["lineage"])
    write_json(run_evidence_dir / "compatibility_summary.json", compatibility)
    write_json(run_evidence_dir / "deployment_manifest.json", deployment_manifest)
    return deployment_manifest


def run_phase2a_safe(*args, **kwargs) -> dict:
    try:
        return run_phase2a(*args, **kwargs)
    except Phase2AScopeError as exc:
        return {
            "status": PHASE2A_SCOPE_VIOLATION,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }
    except BaselineMismatchError as exc:
        return {
            "status": BASELINE_MISMATCH,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }
    except BaselineSpecificationError as exc:
        return {
            "status": BASELINE_SPECIFICATION_MISSING,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }
    except Exception as exc:
        return {
            "status": TEMPORAL_PLATFORM_UNAVAILABLE,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE; KRONOS remains independent.",
        }


if __name__ == "__main__":
    print(json.dumps(run_phase2a_safe(), indent=2, default=str))

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

from src.temporal_risk.audit import (
    finish_deployment,
    record_publish_transition,
    start_deployment,
    utc_now,
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
from src.temporal_risk.historical_ingestion.config import (
    AUTHORIZED_FILES,
    AUTHORIZED_PREFIXES,
    BUSINESS_SCHEMAS,
    CURRENT_WAREHOUSE,
    DDL_FILES,
    EXCLUDED_PARTS,
    EXPECTED_SCHEMA_COUNT,
    EXPECTED_TABLE_COUNT,
    EXPECTED_VIEW_COUNT,
    PHASE2B_EVIDENCE_DIR,
    PHASE2C_EXPECTED_TABLE_COUNT,
    PHASE2C_TABLES,
    PROTECTED_ROOTS,
    ROOT_DIR,
    SCORED_PORTFOLIO,
    SPECIFICATION_NAMES,
    TEMPORAL_DATABASE,
    TEMPORAL_ROOT,
    VOLATILE_GENERATED_FILES,
)
from src.temporal_risk.historical_ingestion.contracts import (
    HISTORICAL_CONTRACT_VIOLATION,
    HISTORICAL_SOURCE_NOT_READY,
    PHASE2B_BASELINE_MISMATCH,
    PHASE2B_INGESTION_SUCCESS,
    PHASE2B_SCHEMA_READY,
    PHASE2B_SCOPE_VIOLATION,
    PHASE2B_UNAVAILABLE,
    PHASE2B_UPGRADE_PRESENT,
    SKIPPED_ALREADY_PUBLISHED,
    SNAPSHOT_VERSION_CONFLICT,
    HistoricalContractError,
    Phase2BBaselineError,
    Phase2BScopeError,
    Phase2BValidationError,
    SnapshotConflictError,
    enforce_scope,
)
from src.temporal_risk.historical_ingestion.data_quality import evaluate_quality
from src.temporal_risk.historical_ingestion.extractor import extract_source
from src.temporal_risk.historical_ingestion.lineage import build_lineage
from src.temporal_risk.historical_ingestion.loader import (
    governed_snapshot_id,
    load_core,
    load_events,
    load_rejects,
    record_historical_publish,
    register_contract,
    register_ingestion_file,
    register_mappings,
    register_reference_rows,
    register_shared_snapshot,
    register_source_assets,
    snapshot_state,
    stage_rows,
    start_batch,
)
from src.temporal_risk.historical_ingestion.manifest import load_manifest
from src.temporal_risk.historical_ingestion.normalizer import (
    canonical_schema_hash,
    inventory_values,
    normalize_frame,
)
from src.temporal_risk.historical_ingestion.readiness import evaluate_readiness
from src.temporal_risk.historical_ingestion.reconciliation import (
    run_reconciliations,
)
from src.temporal_risk.historical_ingestion.release_registry import (
    phase2b_release_id,
    publish_phase2b_release,
    register_phase2b_release,
)
from src.temporal_risk.historical_ingestion.schema_mapping import (
    normalized_mappings,
)
from src.temporal_risk.historical_ingestion.source_discovery import source_profile
from src.temporal_risk.pipeline import (
    PHASE2A_TABLES,
    PHASE2B_TABLES,
    PHASE2C_TABLES as PHASE2C_RECOGNITION_TABLES,
)


def _json_ready(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (datetime, date)):
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
        expected = ROOT_DIR / "docs" / name
        matches = [
            path
            for root in (ROOT_DIR / "docs", ROOT_DIR / "src", ROOT_DIR / "tests", ROOT_DIR / "sql")
            if root.exists()
            for path in root.rglob(name)
            if path.is_file()
        ]
        if len(matches) != 1 or matches[0].resolve() != expected.resolve():
            raise Phase2BValidationError(
                f"Controlled Phase 2B specification is unavailable: {name}"
            )
        inventory[name] = {
            "status": "FILE_CONTROLLED",
            "relative_path": expected.relative_to(ROOT_DIR).as_posix(),
            "sha256": file_sha256(expected),
        }
    return inventory


def catalog_signature(connection) -> dict:
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
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name IN ('control', 'staging', 'reference', 'core', 'mart')
            """
        ).fetchall()
    }
    tables = sorted(
        f"{schema}.{table}" for schema, table, kind in rows if kind == "BASE TABLE"
    )
    views = sorted(
        f"{schema}.{table}" for schema, table, kind in rows if kind == "VIEW"
    )
    return {
        "schema_count": len(schemas),
        "table_count": len(tables),
        "view_count": len(views),
        "mart_object_count": sum(name.startswith("mart.") for name in tables + views),
        "schemas": sorted(schemas),
        "tables": tables,
        "views": views,
    }


def validate_phase2a_catalog(connection) -> dict:
    signature = catalog_signature(connection)
    expected_tables = sorted(PHASE2A_TABLES)
    if (
        signature["schema_count"] != 5
        or signature["tables"] != expected_tables
        or signature["view_count"] != 0
        or signature["mart_object_count"] != 0
    ):
        raise Phase2BValidationError(
            f"Phase 2A baseline catalog is not exact: {signature}"
        )
    return signature


def validate_phase2b_catalog(connection) -> dict:
    signature = catalog_signature(connection)
    expected_tables = sorted(PHASE2A_TABLES | PHASE2B_TABLES)
    if (
        signature["schema_count"] != EXPECTED_SCHEMA_COUNT
        or signature["table_count"] != EXPECTED_TABLE_COUNT
        or signature["view_count"] != EXPECTED_VIEW_COUNT
        or signature["mart_object_count"] != 0
        or signature["tables"] != expected_tables
    ):
        raise Phase2BValidationError(
            f"Phase 2B catalog is not exact: {signature}"
        )
    return signature


def validate_phase2b_ingestion_catalog(connection) -> dict:
    signature = catalog_signature(connection)
    phase2b_tables = sorted(PHASE2A_TABLES | PHASE2B_TABLES)
    phase2c_tables = sorted(
        PHASE2A_TABLES | PHASE2B_TABLES | PHASE2C_RECOGNITION_TABLES
    )
    if (
        signature["schema_count"] != EXPECTED_SCHEMA_COUNT
        or signature["view_count"] != EXPECTED_VIEW_COUNT
        or signature["mart_object_count"] != 0
        or signature["tables"] not in (phase2b_tables, phase2c_tables)
        or signature["table_count"]
        not in (EXPECTED_TABLE_COUNT, PHASE2C_EXPECTED_TABLE_COUNT)
    ):
        raise Phase2BValidationError(
            f"Phase 2B ingestion catalog is not recognized: {signature}"
        )
    return signature


def initialize_phase2b_schema(connection) -> None:
    for path in DDL_FILES:
        if not path.is_file():
            raise Phase2BValidationError(f"Phase 2B DDL is unavailable: {path}")
        connection.execute(path.read_text(encoding="utf-8"))


def _canonical_cell(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return value


def phase2a_row_inventory(connection) -> dict:
    inventory = {}
    for object_name in sorted(PHASE2A_TABLES):
        schema, table = object_name.split(".", 1)
        columns = connection.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = ? AND table_name = ?
            ORDER BY ordinal_position
            """,
            [schema, table],
        ).fetchall()
        names = [row[0] for row in columns]
        info = connection.execute(f"PRAGMA table_info('{schema}.{table}')").fetchall()
        primary = [row[1] for row in info if bool(row[5])]
        if not primary:
            raise Phase2BValidationError(f"Phase 2A table lacks a primary key: {object_name}")
        rows = connection.execute(
            f"SELECT * FROM {schema}.{table} ORDER BY {', '.join(primary)}"
        ).fetchall()
        records = {}
        for row in rows:
            payload = {
                name: _canonical_cell(value)
                for name, value in zip(names, row)
            }
            key = json.dumps(
                [_canonical_cell(payload[name]) for name in primary],
                sort_keys=True,
                default=str,
            )
            digest = hashlib.sha256(
                json.dumps(
                    payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                ).encode("utf-8")
            ).hexdigest().upper()
            records[key] = digest
        inventory[object_name] = {
            "primary_key": primary,
            "row_count": len(rows),
            "rows": records,
        }
    return inventory


def compare_original_rows(before: dict, after: dict) -> dict:
    changes = []
    for table, baseline in before.items():
        current = after.get(table, {"rows": {}})
        for key, digest in baseline["rows"].items():
            if current["rows"].get(key) != digest:
                changes.append({"table": table, "primary_key": key})
    return {
        "status": "PASS" if not changes else "FAIL",
        "matches": not changes,
        "changed_rows": changes,
    }


def _authorized(relative: str) -> bool:
    return relative in AUTHORIZED_FILES or relative in VOLATILE_GENERATED_FILES or any(
        relative.startswith(prefix) for prefix in AUTHORIZED_PREFIXES
    )


def protected_hash_inventory() -> dict:
    inventory = {}
    candidates = []
    for root_name in PROTECTED_ROOTS:
        root = ROOT_DIR / root_name
        if root.exists():
            candidates.extend(path for path in root.rglob("*") if path.is_file())
    for name in ("README.md", "requirements.txt", "requirements-dev.txt", ".gitignore"):
        path = ROOT_DIR / name
        if path.is_file():
            candidates.append(path)
    for path in sorted(set(candidates)):
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        relative = path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()
        if _authorized(relative):
            continue
        inventory[relative] = file_sha256(path)
    return inventory


def external_baseline() -> dict:
    return {
        "current_warehouse_sha256": file_sha256(CURRENT_WAREHOUSE),
        "scored_portfolio_sha256": file_sha256(SCORED_PORTFOLIO),
    }


def _assert_baselines(
    *,
    protected_before: dict,
    external_before: dict,
) -> dict:
    protected_after = protected_hash_inventory()
    external_after = external_baseline()
    result = {
        "protected_hashes_unchanged": protected_before == protected_after,
        "external_assets_unchanged": external_before == external_after,
        "protected_file_count": len(protected_before),
        "current_warehouse_sha256": external_after["current_warehouse_sha256"],
        "scored_portfolio_sha256": external_after["scored_portfolio_sha256"],
    }
    result["status"] = (
        "PASS"
        if result["protected_hashes_unchanged"]
        and result["external_assets_unchanged"]
        else "FAIL"
    )
    if result["status"] != "PASS":
        raise Phase2BBaselineError(PHASE2B_BASELINE_MISMATCH)
    return result


def _schema_deployment_evidence(
    *,
    evidence_root: Path,
    deployment_id: str,
    payload: dict,
) -> Path:
    target = evidence_root / deployment_id
    target.mkdir(parents=True, exist_ok=False)
    write_json(target / "deployment_manifest.json", payload)
    write_json(target / "protected_hash_verification.json", payload["protected"])
    write_json(target / "phase2a_row_preservation.json", payload["phase2a_rows"])
    write_json(target / "database_catalog.json", payload["catalog"])
    write_json(target / "specification_hash_inventory.json", payload["specifications"])
    return target


def deploy_phase2b_schema(
    database_path: Path | str = TEMPORAL_DATABASE,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
    evidence_dir: Path | str = PHASE2B_EVIDENCE_DIR,
    capture_protected_hashes: bool = True,
) -> dict:
    enforce_scope()
    database_path = assert_temporal_target(database_path, runtime_root=runtime_root)
    evidence_root = assert_evidence_target(evidence_dir, runtime_root=runtime_root)
    specs = specification_inventory()
    protected_before = protected_hash_inventory() if capture_protected_hashes else {}
    external_before = external_baseline()

    baseline_connection = connect_temporal(database_path, read_only=True)
    try:
        current_signature = catalog_signature(baseline_connection)
        if current_signature["tables"] == sorted(
            PHASE2A_TABLES | PHASE2B_TABLES | PHASE2C_TABLES
        ):
            return {
                "status": PHASE2B_UPGRADE_PRESENT,
                "catalog": validate_phase2b_ingestion_catalog(
                    baseline_connection
                ),
                "release_id": phase2b_release_id(),
                "idempotent": True,
                "database_sha256": file_sha256(database_path),
            }
        if current_signature["tables"] == sorted(PHASE2A_TABLES | PHASE2B_TABLES):
            return {
                "status": PHASE2B_SCHEMA_READY,
                "catalog": validate_phase2b_catalog(baseline_connection),
                "release_id": phase2b_release_id(),
                "idempotent": True,
                "database_sha256": file_sha256(database_path),
            }
        validate_phase2a_catalog(baseline_connection)
        original_rows = phase2a_row_inventory(baseline_connection)
    finally:
        baseline_connection.close()

    deployment_id = uuid4().hex.upper()
    pre_database_hash = file_sha256(database_path)
    working = prepare_working_database(database_path, runtime_root=runtime_root)
    connection = connect_temporal(
        working.working_path,
        read_only=False,
        deployment_authorized=True,
        runtime_root=working.working_path.parent,
    )
    try:
        initialize_phase2b_schema(connection)
        register_reference_rows(connection)
        catalog = validate_phase2b_catalog(connection)
        release_id = register_phase2b_release(
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
            details="Phase 2B additive schema deployment started.",
        )
        phase2a_after = phase2a_row_inventory(connection)
        row_preservation = compare_original_rows(original_rows, phase2a_after)
        if not row_preservation["matches"]:
            raise Phase2BBaselineError(PHASE2B_BASELINE_MISMATCH)
        record_publish_transition(
            connection,
            deployment_id,
            previous_status="DRAFT",
            new_status="VALIDATED",
            details="Exact 5/36/0 catalog and Phase 2A row preservation verified.",
        )
        record_publish_transition(
            connection,
            deployment_id,
            previous_status="VALIDATED",
            new_status="PUBLISHED",
            details="Phase 2B isolated schema authorized for file publication.",
        )
        publish_phase2b_release(connection, release_id)
        finish_deployment(
            connection,
            deployment_id,
            status=PHASE2B_SCHEMA_READY,
        )
        connection.execute("CHECKPOINT")
    except Exception:
        connection.close()
        discard_working_database(working)
        raise
    else:
        connection.close()

    publish_working_database(working)
    published_connection = connect_temporal(database_path, read_only=True)
    try:
        published_catalog = validate_phase2b_catalog(published_connection)
        published_rows = phase2a_row_inventory(published_connection)
        row_preservation = compare_original_rows(original_rows, published_rows)
        phase2a_release_rows = published_connection.execute(
            "SELECT COUNT(*) FROM control.platform_release WHERE phase_name = 'PHASE2A'"
        ).fetchone()[0]
        phase2b_release_rows = published_connection.execute(
            "SELECT COUNT(*) FROM control.platform_release WHERE phase_name = 'PHASE2B'"
        ).fetchone()[0]
    finally:
        published_connection.close()
    if not row_preservation["matches"] or phase2a_release_rows != 1 or phase2b_release_rows != 1:
        raise Phase2BBaselineError(PHASE2B_BASELINE_MISMATCH)
    protected = (
        _assert_baselines(
            protected_before=protected_before,
            external_before=external_before,
        )
        if capture_protected_hashes
        else {"status": "NOT_CAPTURED"}
    )
    payload = {
        "status": PHASE2B_SCHEMA_READY,
        "deployment_id": deployment_id,
        "release_id": release_id,
        "database_path": database_path,
        "database_sha256_before": pre_database_hash,
        "database_sha256_after": file_sha256(database_path),
        "backup_path": working.backup_path,
        "catalog": published_catalog,
        "phase2a_rows": row_preservation,
        "phase2a_release_rows": phase2a_release_rows,
        "phase2b_release_rows": phase2b_release_rows,
        "protected": protected,
        "specifications": specs,
        "generated_at": utc_now(),
    }
    evidence_path = _schema_deployment_evidence(
        evidence_root=evidence_root,
        deployment_id=deployment_id,
        payload=payload,
    )
    payload["evidence_directory"] = evidence_path
    return payload


def deploy_phase2b_schema_safe(*args, **kwargs) -> dict:
    try:
        return deploy_phase2b_schema(*args, **kwargs)
    except Phase2BScopeError as exc:
        return {"status": PHASE2B_SCOPE_VIOLATION, "error": str(exc)}
    except Phase2BBaselineError as exc:
        return {"status": PHASE2B_BASELINE_MISMATCH, "error": str(exc)}
    except Exception as exc:
        return {
            "status": PHASE2B_UNAVAILABLE,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }


def run_historical_ingestion(
    manifest_path: Path | str,
    *,
    database_path: Path | str = TEMPORAL_DATABASE,
    runtime_root: Path | str = TEMPORAL_ROOT,
    evidence_dir: Path | str = PHASE2B_EVIDENCE_DIR,
    capture_protected_hashes: bool = True,
) -> dict:
    enforce_scope()
    database_path = assert_temporal_target(database_path, runtime_root=runtime_root)
    evidence_root = assert_evidence_target(evidence_dir, runtime_root=runtime_root)
    specs = specification_inventory()
    manifest = load_manifest(manifest_path, runtime_root=runtime_root)
    source_hash_before = file_sha256(manifest["source_path"])
    source_frame = extract_source(manifest["source_path"], manifest["source_format"])
    mappings = normalized_mappings(manifest, list(source_frame.columns))
    normalized = normalize_frame(source_frame, mappings)
    schema_hash = canonical_schema_hash(source_frame)
    profile = source_profile(
        manifest["source_path"],
        manifest["source_format"],
        runtime_root=runtime_root,
    )
    protected_before = protected_hash_inventory() if capture_protected_hashes else {}
    external_before = external_baseline()

    read_only = connect_temporal(database_path, read_only=True)
    try:
        validate_phase2b_ingestion_catalog(read_only)
        original_rows = phase2a_row_inventory(read_only)
        contract_preview = register_contract_preview(manifest)
        snapshot_id = governed_snapshot_id(manifest, contract_preview)
        already_published, conflict = snapshot_state(
            read_only,
            snapshot_id=snapshot_id,
            source_hash=source_hash_before,
            manifest_hash=manifest["manifest_sha256"],
            contract_version=contract_preview["contract_version"],
        )
    finally:
        read_only.close()
    if already_published:
        return {
            "status": SKIPPED_ALREADY_PUBLISHED,
            "snapshot_id": snapshot_id,
            "database_sha256": file_sha256(database_path),
        }
    if conflict:
        raise SnapshotConflictError(SNAPSHOT_VERSION_CONFLICT)

    ingestion_batch_id = uuid4().hex.upper()
    working = prepare_working_database(database_path, runtime_root=runtime_root)
    connection = connect_temporal(
        working.working_path,
        read_only=False,
        deployment_authorized=True,
        runtime_root=working.working_path.parent,
    )
    try:
        validate_phase2b_ingestion_catalog(connection)
        contract = register_contract(connection, manifest)
        snapshot_id = governed_snapshot_id(manifest, contract)
        release_id = phase2b_release_id()
        start_batch(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            release_id=release_id,
            manifest=manifest,
            contract=contract,
        )
        record_historical_publish(
            connection,
            ingestion_batch_id,
            None,
            "DRAFT",
            "Historical ingestion started.",
        )
        source_asset_id, manifest_asset_id = register_source_assets(
            connection,
            manifest=manifest,
            source_frame=source_frame,
            schema_hash=schema_hash,
        )
        connection.execute(
            """
            UPDATE control.historical_ingestion_batch
            SET source_asset_id = ?, manifest_asset_id = ?
            WHERE ingestion_batch_id = ?
            """,
            [source_asset_id, manifest_asset_id, ingestion_batch_id],
        )
        register_ingestion_file(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            source_asset_id=source_asset_id,
            manifest_asset_id=manifest_asset_id,
            manifest=manifest,
            schema_hash=schema_hash,
            source_frame=source_frame,
        )
        register_mappings(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            mappings=mappings,
        )
        source_hash_after = file_sha256(manifest["source_path"])
        quality = evaluate_quality(
            source_frame=source_frame,
            normalized=normalized,
            manifest=manifest,
            mappings=mappings,
            source_hash_before=source_hash_before,
            source_hash_after=source_hash_after,
            schema_hash=schema_hash,
            snapshot_exists=False,
            snapshot_conflict=False,
        )
        if quality["check_count"] != 36 or quality["critical_failure_count"] or quality["accepted"].empty:
            raise HistoricalContractError(HISTORICAL_SOURCE_NOT_READY)
        rejected_source_rows = {
            item["source_row_number"] for item in quality["rejected"]
        }
        stage_rows(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            manifest=manifest,
            normalized=normalized,
            rejected_source_rows=rejected_source_rows,
        )
        load_rejects(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            rejected=quality["rejected"],
        )
        source_event_count = load_events(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            accepted=quality["accepted"],
        )
        run_inventory = inventory_values(quality["accepted"], "source_run_id")
        model_inventory = inventory_values(
            quality["accepted"], "source_model_version"
        )
        core = load_core(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            manifest=manifest,
            contract=contract,
            schema_hash=schema_hash,
            accepted=quality["accepted"],
            run_inventory=run_inventory,
            model_inventory=model_inventory,
        )
        register_shared_snapshot(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            source_asset_id=source_asset_id,
            manifest=manifest,
            contract=contract,
            schema_hash=schema_hash,
            accepted=quality["accepted"],
            run_inventory=run_inventory,
            model_inventory=model_inventory,
            source_row_count=len(source_frame),
            source_column_count=len(source_frame.columns),
        )
        mapped_fields = {item["canonical_column"] for item in mappings}
        readiness = evaluate_readiness(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            manifest=manifest,
            mapped_fields=mapped_fields,
            storage_ready=True,
        )
        ifrs9 = next(
            item for item in readiness if item["capability_name"] == "IFRS9_TEMPORAL_INPUTS"
        )
        if ifrs9["data_status"] not in {"NOT_READY", "NOT_ELIGIBLE"}:
            raise Phase2BValidationError("IFRS9 readiness ceiling was violated.")
        accepted = quality["accepted"]
        ead_sum = (
            float(accepted["ead"].dropna().sum())
            if accepted["ead"].notna().any()
            else None
        )
        default_count = (
            int(
                accepted["default_outcome"]
                .dropna()
                .astype(str)
                .str.lower()
                .isin({"1", "true", "default", "defaulted", "yes"})
                .sum()
            )
            if accepted["default_outcome"].notna().any()
            else None
        )
        reconciliation = run_reconciliations(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            snapshot_id=snapshot_id,
            source_rows=len(source_frame),
            accepted_rows=len(accepted),
            rejected_source_rows=len(rejected_source_rows),
            distinct_entities=core["entity_count"],
            distinct_facilities=core["facility_count"],
            source_hash=source_hash_before,
            schema_hash=schema_hash,
            snapshot_date=str(manifest["declared_snapshot_date"]),
            source_event_count=source_event_count,
            source_ead_sum=ead_sum,
            source_default_count=default_count,
        )
        if reconciliation["reconciliation_count"] != 12 or reconciliation["failure_count"]:
            raise Phase2BValidationError("Historical reconciliation failed.")
        lineage = build_lineage(
            connection,
            ingestion_batch_id=ingestion_batch_id,
            source_asset_id=source_asset_id,
            source_hash=source_hash_before,
            manifest=manifest,
            contract_id=contract["contract_id"],
            contract_hash=contract["contract_hash"],
            snapshot_id=snapshot_id,
            mappings=mappings,
        )
        if not lineage["complete"]:
            raise Phase2BValidationError("Historical lineage is incomplete.")
        record_historical_publish(
            connection,
            ingestion_batch_id,
            "DRAFT",
            "VALIDATED",
            "DQ, readiness, reconciliation, lineage, and preservation passed.",
        )
        record_historical_publish(
            connection,
            ingestion_batch_id,
            "VALIDATED",
            "PUBLISHED",
            "Historical snapshot authorized for isolated publication.",
        )
        connection.execute(
            """
            UPDATE control.historical_ingestion_batch
            SET completed_at = ?, status = ?, records_read = ?,
                records_staged = ?, records_accepted = ?,
                records_rejected = ?, records_inserted = ?,
                records_skipped = 0, snapshot_count = 1,
                quality_score = ?, quality_status = ?,
                quality_details_json = ?
            WHERE ingestion_batch_id = ?
            """,
            [
                utc_now(),
                PHASE2B_INGESTION_SUCCESS,
                len(source_frame),
                len(source_frame),
                len(accepted),
                len(rejected_source_rows),
                len(accepted),
                quality["quality_score"],
                quality["quality_status"],
                json.dumps(quality["checks"], sort_keys=True),
                ingestion_batch_id,
            ],
        )
        phase2a_after = phase2a_row_inventory(connection)
        row_preservation = compare_original_rows(original_rows, phase2a_after)
        if not row_preservation["matches"]:
            raise Phase2BBaselineError(PHASE2B_BASELINE_MISMATCH)
        connection.execute("CHECKPOINT")
    except Exception:
        connection.close()
        discard_working_database(working)
        raise
    else:
        connection.close()

    publish_working_database(working)
    published = connect_temporal(database_path, read_only=True)
    try:
        catalog = validate_phase2b_ingestion_catalog(published)
        phase2a_rows = compare_original_rows(
            original_rows,
            phase2a_row_inventory(published),
        )
    finally:
        published.close()
    if not phase2a_rows["matches"]:
        raise Phase2BBaselineError(PHASE2B_BASELINE_MISMATCH)
    protected = (
        _assert_baselines(
            protected_before=protected_before,
            external_before=external_before,
        )
        if capture_protected_hashes
        else {"status": "NOT_CAPTURED"}
    )
    result = {
        "status": PHASE2B_INGESTION_SUCCESS,
        "ingestion_batch_id": ingestion_batch_id,
        "snapshot_id": snapshot_id,
        "source_asset_id": source_asset_id,
        "manifest_asset_id": manifest_asset_id,
        "database_path": database_path,
        "database_sha256": file_sha256(database_path),
        "backup_path": working.backup_path,
        "catalog": catalog,
        "quality": {
            key: value
            for key, value in quality.items()
            if key not in {"accepted", "rejected"}
        },
        "rejected_source_rows": len(rejected_source_rows),
        "readiness": readiness,
        "reconciliation": reconciliation,
        "lineage": lineage,
        "phase2a_rows": phase2a_rows,
        "protected": protected,
        "specifications": specs,
        "generated_at": utc_now(),
    }
    evidence_path = evidence_root / ingestion_batch_id
    evidence_path.mkdir(parents=True, exist_ok=False)
    write_json(evidence_path / "ingestion_manifest.json", result)
    write_json(evidence_path / "quality_summary.json", result["quality"])
    write_json(evidence_path / "readiness_summary.json", {"results": readiness})
    write_json(evidence_path / "reconciliation_summary.json", reconciliation)
    write_json(evidence_path / "lineage_summary.json", lineage)
    write_json(evidence_path / "protected_hash_verification.json", protected)
    result["evidence_directory"] = evidence_path
    return result


def register_contract_preview(manifest: dict) -> dict:
    definition = {
        "contract_name": manifest["contract_name"],
        "contract_version": str(manifest["contract_version"]),
        "history_mode": manifest["history_mode"],
        "evidence_classification": manifest["evidence_classification"],
    }
    contract_hash = hashlib.sha256(
        json.dumps(
            {
                **definition,
                "description": (
                    "Source-supplied observed historical snapshots."
                    if manifest["history_mode"] == "OBSERVED_TEMPORAL"
                    else "Externally produced and explicitly labelled simulated snapshots."
                ),
                "required_fields": (
                    "source_entity_id",
                    "observation_or_reporting_date",
                    "source_date_provenance",
                    "source_hash",
                ),
                "prohibited_claims": (
                    "migration",
                    "roll_rate",
                    "vintage",
                    "true_oot",
                    "ifrs9",
                ),
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest().upper()
    from src.temporal_risk.audit import stable_id

    return {
        "contract_id": stable_id(
            definition["contract_name"],
            definition["contract_version"],
            contract_hash,
        ),
        "contract_version": definition["contract_version"],
        "contract_hash": contract_hash,
    }


def run_historical_ingestion_safe(*args, **kwargs) -> dict:
    try:
        return run_historical_ingestion(*args, **kwargs)
    except Phase2BScopeError as exc:
        return {"status": PHASE2B_SCOPE_VIOLATION, "error": str(exc)}
    except SnapshotConflictError as exc:
        return {"status": SNAPSHOT_VERSION_CONFLICT, "error": str(exc)}
    except HistoricalContractError as exc:
        return {"status": HISTORICAL_CONTRACT_VIOLATION, "error": str(exc)}
    except Phase2BBaselineError as exc:
        return {"status": PHASE2B_BASELINE_MISMATCH, "error": str(exc)}
    except Exception as exc:
        return {
            "status": PHASE2B_UNAVAILABLE,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }

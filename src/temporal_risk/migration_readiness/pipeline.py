from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.connection import (
    assert_evidence_target,
    assert_temporal_target,
    connect_temporal,
    discard_working_database,
    file_sha256,
    prepare_working_database,
    publish_working_database,
)
from src.temporal_risk.migration_readiness.config import (
    CURRENT_WAREHOUSE,
    DDL_FILES,
    PHASE2C_EVIDENCE_DIR,
    ROOT_DIR,
    SCORED_PORTFOLIO,
    SPECIFICATION_NAMES,
    TEMPORAL_DATABASE,
    TEMPORAL_ROOT,
)
from src.temporal_risk.migration_readiness.continuity import (
    build_continuity_context,
)
from src.temporal_risk.migration_readiness.contracts import (
    DISABLED,
    PHASE2C_BASELINE_MISMATCH,
    PHASE2C_PAIR_CONFLICT,
    PHASE2C_READINESS_PUBLISHED,
    PHASE2C_SCHEMA_READY,
    PHASE2C_SCOPE_VIOLATION,
    PHASE2C_SOURCE_NOT_ELIGIBLE,
    PHASE2C_SOURCE_NOT_READY,
    PHASE2C_UNAVAILABLE,
    READINESS_CONTRACT_NAME,
    STATE_CONTRACTS,
    SKIPPED_ALREADY_PUBLISHED,
    Phase2CBaselineError,
    Phase2CPairConflictError,
    Phase2CScopeError,
    Phase2CSourceNotEligibleError,
    Phase2CSourceNotReadyError,
    Phase2CValidationError,
    enforce_scope,
)
from src.temporal_risk.migration_readiness.data_quality import (
    evaluate_quality,
    persist_quality,
    persist_readiness,
)
from src.temporal_risk.migration_readiness.lineage import build_lineage
from src.temporal_risk.migration_readiness.pair_selector import (
    candidates,
    select_pair,
)
from src.temporal_risk.migration_readiness.reconciliation import (
    evaluate_reconciliations,
    persist_reconciliations,
)
from src.temporal_risk.migration_readiness.release_registry import (
    phase2c_release_id,
    publish_phase2c_release,
    register_controlled_contracts,
    register_phase2c_release,
    validate_controlled_contracts,
)
from src.temporal_risk.migration_readiness.source_catalog import (
    assert_external_and_protected,
    catalog_signature,
    compare_preserved_rows,
    exact_tables,
    external_baseline,
    protected_hash_inventory,
    row_inventory,
    validate_exact_catalog,
)


def _json_ready(value):
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if hasattr(value, "as_tuple"):
        return str(value)
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
        path = ROOT_DIR / "docs" / name
        if not path.is_file():
            raise Phase2CValidationError(
                f"Controlled Phase 2C specification is unavailable: {name}"
            )
        inventory[name] = {
            "status": "FILE_CONTROLLED",
            "relative_path": path.relative_to(ROOT_DIR).as_posix(),
            "sha256": file_sha256(path),
        }
    return inventory


def initialize_phase2c_schema(connection) -> None:
    for path in DDL_FILES:
        if not path.is_file():
            raise Phase2CValidationError(f"Phase 2C DDL is unavailable: {path}")
        connection.execute(path.read_text(encoding="utf-8"))


def _release_status(connection, phase_name: str) -> bool:
    rows = connection.execute(
        """
        SELECT COUNT(*) FROM control.platform_release
        WHERE phase_name = ? AND status = 'PUBLISHED'
        """,
        [phase_name],
    ).fetchone()[0]
    return int(rows) == 1


def _record_publish(
    connection,
    *,
    readiness_run_id: str,
    previous_status: str | None,
    new_status: str,
    details: str,
) -> None:
    connection.execute(
        """
        INSERT INTO control.migration_publish_status (
            publish_status_id, readiness_run_id, target_name,
            previous_status, new_status, transition_at, details
        ) VALUES (?, ?, 'kronos_temporal_risk.duckdb', ?, ?, ?, ?)
        """,
        [
            stable_id(readiness_run_id, previous_status, new_status),
            readiness_run_id,
            previous_status,
            new_status,
            utc_now(),
            details,
        ],
    )


def _start_run(
    connection,
    *,
    readiness_run_id: str,
    run_type: str,
    release_id: str,
    pre_operation_hash: str,
    earlier: dict | None = None,
    later: dict | None = None,
    state_field: str | None = None,
    readiness_contract: dict | None = None,
    domain_contract: dict | None = None,
) -> None:
    connection.execute(
        """
        INSERT INTO control.migration_readiness_run (
            readiness_run_id, release_id, run_type, started_at,
            lifecycle_status, earlier_snapshot_id, later_snapshot_id,
            state_field, readiness_contract_id,
            readiness_contract_version, readiness_contract_hash,
            state_domain_contract_id, state_domain_contract_version,
            state_domain_contract_hash, activation_status,
            pre_operation_database_sha256
        ) VALUES (?, ?, ?, ?, 'RUNNING', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            readiness_run_id,
            release_id,
            run_type,
            utc_now(),
            earlier["snapshot_id"] if earlier else None,
            later["snapshot_id"] if later else None,
            state_field,
            readiness_contract["contract_id"] if readiness_contract else None,
            readiness_contract["contract_version"] if readiness_contract else None,
            readiness_contract["contract_hash"] if readiness_contract else None,
            domain_contract["contract_id"] if domain_contract else None,
            domain_contract["contract_version"] if domain_contract else None,
            domain_contract["contract_hash"] if domain_contract else None,
            DISABLED,
            pre_operation_hash,
        ],
    )


def _finish_run(
    connection,
    *,
    readiness_run_id: str,
    lifecycle_status: str,
    quality: dict | None = None,
    error: Exception | None = None,
) -> None:
    connection.execute(
        """
        UPDATE control.migration_readiness_run
        SET completed_at = ?, lifecycle_status = ?,
            applicable_controls = ?, passed_applicable_controls = ?,
            governance_score = ?, quality_status = ?, readiness_status = ?,
            error_class = ?, error_message = ?
        WHERE readiness_run_id = ?
        """,
        [
            utc_now(),
            lifecycle_status,
            quality["applicable_controls"] if quality else None,
            quality["passed_applicable_controls"] if quality else None,
            quality["governance_score"] if quality else None,
            quality["quality_status"] if quality else None,
            quality["readiness_status"] if quality else None,
            type(error).__name__ if error else None,
            str(error) if error else None,
            readiness_run_id,
        ],
    )


def _assert_idempotency(
    connection,
    *,
    earlier: dict,
    later: dict,
    state_field: str,
    readiness_contract: dict,
    domain_contract: dict,
) -> str | None:
    rows = connection.execute(
        """
        SELECT
            run.lifecycle_status,
            pair.readiness_contract_version,
            pair.readiness_contract_hash,
            pair.state_domain_contract_version,
            pair.state_domain_contract_hash,
            pair.earlier_source_sha256,
            pair.later_source_sha256
        FROM control.migration_snapshot_pair pair
        JOIN control.migration_readiness_run run
          ON run.readiness_run_id = pair.readiness_run_id
        WHERE pair.earlier_snapshot_id = ?
          AND pair.later_snapshot_id = ?
          AND pair.state_field = ?
        """,
        [earlier["snapshot_id"], later["snapshot_id"], state_field],
    ).fetchall()
    if not rows:
        return None
    if len(rows) != 1:
        raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
    row = rows[0]
    if (
        row[1] == readiness_contract["contract_version"]
        and row[2] != readiness_contract["contract_hash"]
    ) or (
        row[3] == domain_contract["contract_version"]
        and row[4] != domain_contract["contract_hash"]
    ):
        raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)
    exact = (
        row[0] == "PUBLISHED"
        and row[1] == readiness_contract["contract_version"]
        and row[2] == readiness_contract["contract_hash"]
        and row[3] == domain_contract["contract_version"]
        and row[4] == domain_contract["contract_hash"]
        and row[5] == earlier["source_sha256"]
        and row[6] == later["source_sha256"]
    )
    if exact:
        return SKIPPED_ALREADY_PUBLISHED
    raise Phase2CPairConflictError(PHASE2C_PAIR_CONFLICT)


def _register_pair(
    connection,
    *,
    readiness_run_id: str,
    pair_id: str,
    context: dict,
    readiness_contract: dict,
    domain_contract: dict,
) -> None:
    earlier = context["earlier"]
    later = context["later"]
    connection.execute(
        """
        INSERT INTO control.migration_snapshot_pair (
            pair_id, readiness_run_id, earlier_snapshot_id,
            later_snapshot_id, earlier_snapshot_date, later_snapshot_date,
            source_system, identity_grain, history_mode,
            evidence_classification, state_field, readiness_contract_id,
            readiness_contract_version, readiness_contract_hash,
            state_domain_contract_id, state_domain_contract_version,
            state_domain_contract_hash, earlier_source_sha256,
            later_source_sha256, earlier_population_count,
            later_population_count, overlapping_identity_count,
            earlier_state_complete_overlap_count,
            later_state_complete_overlap_count,
            earlier_state_missing_overlap_count,
            later_state_missing_overlap_count, identity_continuity_status,
            state_continuity_status, eligibility_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                  ?, ?, ?, ?, ?, ?, ?, 'ESTABLISHED_BY_OVERLAP',
                  'CONTROLLED_DOMAIN_VALIDATED', 'READY_BUT_DISABLED')
        """,
        [
            pair_id,
            readiness_run_id,
            earlier["snapshot_id"],
            later["snapshot_id"],
            earlier["snapshot_date"],
            later["snapshot_date"],
            earlier["source_system"],
            earlier["identity_grain"],
            earlier["history_mode"],
            earlier["evidence_classification"],
            context["state_field"],
            readiness_contract["contract_id"],
            readiness_contract["contract_version"],
            readiness_contract["contract_hash"],
            domain_contract["contract_id"],
            domain_contract["contract_version"],
            domain_contract["contract_hash"],
            earlier["source_sha256"],
            later["source_sha256"],
            context["earlier_population_count"],
            context["later_population_count"],
            context["overlapping_identity_count"],
            context["earlier_state_complete_overlap_count"],
            context["later_state_complete_overlap_count"],
            context["earlier_state_missing_overlap_count"],
            context["later_state_missing_overlap_count"],
        ],
    )


def _write_deployment_evidence(evidence_root: Path, run_id: str, payload: dict) -> Path:
    target = evidence_root / run_id
    target.mkdir(parents=True, exist_ok=False)
    write_json(target / "deployment_summary.json", payload)
    write_json(target / "catalog_verification.json", payload["catalog"])
    write_json(target / "preservation_verification.json", payload["preservation"])
    write_json(target / "protected_hash_verification.json", payload["protected"])
    write_json(target / "specification_hash_inventory.json", payload["specifications"])
    return target


def deploy_phase2c_schema(
    database_path: Path | str = TEMPORAL_DATABASE,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
    evidence_dir: Path | str = PHASE2C_EVIDENCE_DIR,
    capture_protected_hashes: bool = True,
) -> dict:
    enforce_scope()
    database_path = assert_temporal_target(database_path, runtime_root=runtime_root)
    evidence_root = assert_evidence_target(evidence_dir, runtime_root=runtime_root)
    specifications = specification_inventory()
    protected_before = protected_hash_inventory() if capture_protected_hashes else {}
    external_before = external_baseline()

    baseline = connect_temporal(database_path, read_only=True)
    try:
        signature = catalog_signature(baseline)
        if signature["tables"] == sorted(exact_tables("PHASE2C")):
            catalog = validate_exact_catalog(baseline, "PHASE2C")
            validate_controlled_contracts(baseline)
            if not _release_status(baseline, "PHASE2C"):
                raise Phase2CValidationError("Published Phase 2C release is unavailable.")
            return {
                "status": PHASE2C_SCHEMA_READY,
                "catalog": catalog,
                "release_id": phase2c_release_id(),
                "database_sha256": file_sha256(database_path),
                "idempotent": True,
            }
        validate_exact_catalog(baseline, "PHASE2B")
        if not _release_status(baseline, "PHASE2A") or not _release_status(
            baseline, "PHASE2B"
        ):
            raise Phase2CValidationError("Accepted earlier releases are unavailable.")
        preserved_before = row_inventory(baseline, exact_tables("PHASE2B"))
    finally:
        baseline.close()

    pre_operation_hash = file_sha256(database_path)
    working = prepare_working_database(database_path, runtime_root=runtime_root)
    readiness_run_id = uuid4().hex.upper()
    connection = connect_temporal(
        working.working_path,
        read_only=False,
        deployment_authorized=True,
        runtime_root=working.working_path.parent,
    )
    try:
        initialize_phase2c_schema(connection)
        contracts = register_controlled_contracts(connection)
        catalog = validate_exact_catalog(connection, "PHASE2C")
        release_id = register_phase2c_release(
            connection,
            database_path=database_path.as_posix(),
            specification_inventory=specifications,
            catalog=catalog,
        )
        _start_run(
            connection,
            readiness_run_id=readiness_run_id,
            run_type="SCHEMA_DEPLOYMENT",
            release_id=release_id,
            pre_operation_hash=pre_operation_hash,
            readiness_contract=contracts[READINESS_CONTRACT_NAME],
        )
        _record_publish(
            connection,
            readiness_run_id=readiness_run_id,
            previous_status=None,
            new_status="DRAFT",
            details="Phase 2C additive control schema deployment started.",
        )
        preservation = compare_preserved_rows(
            preserved_before,
            row_inventory(connection, exact_tables("PHASE2B")),
        )
        _record_publish(
            connection,
            readiness_run_id=readiness_run_id,
            previous_status="DRAFT",
            new_status="VALIDATED",
            details="Exact catalog and earlier-phase row preservation verified.",
        )
        _record_publish(
            connection,
            readiness_run_id=readiness_run_id,
            previous_status="VALIDATED",
            new_status="PUBLISHED",
            details="Phase 2C control schema authorized for file publication.",
        )
        publish_phase2c_release(connection, release_id)
        _finish_run(
            connection,
            readiness_run_id=readiness_run_id,
            lifecycle_status="PUBLISHED",
        )
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
        published_catalog = validate_exact_catalog(published, "PHASE2C")
        published_preservation = compare_preserved_rows(
            preserved_before,
            row_inventory(published, exact_tables("PHASE2B")),
        )
        validate_controlled_contracts(published)
        if not _release_status(published, "PHASE2C"):
            raise Phase2CValidationError("Phase 2C release was not published.")
    finally:
        published.close()

    protected = (
        assert_external_and_protected(protected_before, external_before)
        if capture_protected_hashes
        else {"status": "NOT_CAPTURED"}
    )
    result = {
        "status": PHASE2C_SCHEMA_READY,
        "readiness_run_id": readiness_run_id,
        "release_id": release_id,
        "database_path": database_path,
        "database_sha256_before": pre_operation_hash,
        "database_sha256_after": file_sha256(database_path),
        "backup_path": working.backup_path,
        "catalog": published_catalog,
        "preservation": published_preservation,
        "protected": protected,
        "specifications": specifications,
        "generated_at": utc_now(),
    }
    evidence_path = _write_deployment_evidence(
        evidence_root,
        readiness_run_id,
        result,
    )
    result["evidence_directory"] = evidence_path
    return result


def deploy_phase2c_schema_safe(*args, **kwargs) -> dict:
    try:
        return deploy_phase2c_schema(*args, **kwargs)
    except Phase2CScopeError as exc:
        return {"status": PHASE2C_SCOPE_VIOLATION, "error": str(exc)}
    except Phase2CBaselineError as exc:
        return {"status": PHASE2C_BASELINE_MISMATCH, "error": str(exc)}
    except Phase2CPairConflictError as exc:
        return {"status": PHASE2C_PAIR_CONFLICT, "error": str(exc)}
    except Exception as exc:
        return {
            "status": PHASE2C_UNAVAILABLE,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }


def evaluate_migration_readiness(
    *,
    state_field: str,
    earlier_snapshot_id: str | None = None,
    later_snapshot_id: str | None = None,
    source_system: str | None = None,
    identity_grain: str | None = None,
    database_path: Path | str = TEMPORAL_DATABASE,
    runtime_root: Path | str = TEMPORAL_ROOT,
    evidence_dir: Path | str = PHASE2C_EVIDENCE_DIR,
    capture_protected_hashes: bool = True,
) -> dict:
    enforce_scope()
    if state_field not in STATE_CONTRACTS:
        raise Phase2CScopeError(PHASE2C_SCOPE_VIOLATION)
    database_path = assert_temporal_target(database_path, runtime_root=runtime_root)
    evidence_root = assert_evidence_target(evidence_dir, runtime_root=runtime_root)

    read_only = connect_temporal(database_path, read_only=True)
    try:
        catalog = validate_exact_catalog(read_only, "PHASE2C")
        controlled = validate_controlled_contracts(read_only)
        observed_candidates = candidates(read_only, state_field=state_field)
        if len(observed_candidates) < 2:
            return {
                "status": PHASE2C_SOURCE_NOT_READY,
                "application_impact": "NONE",
                "database_sha256": file_sha256(database_path),
            }
        earlier, later = select_pair(
            read_only,
            state_field=state_field,
            earlier_snapshot_id=earlier_snapshot_id,
            later_snapshot_id=later_snapshot_id,
            source_system=source_system,
            identity_grain=identity_grain,
        )
        readiness_contract = controlled[READINESS_CONTRACT_NAME]
        domain_definition = STATE_CONTRACTS[state_field]
        domain_contract = controlled[domain_definition.contract_name]
        existing = _assert_idempotency(
            read_only,
            earlier=earlier,
            later=later,
            state_field=state_field,
            readiness_contract=readiness_contract,
            domain_contract=domain_contract,
        )
        if existing:
            return {
                "status": existing,
                "database_sha256": file_sha256(database_path),
            }
        context = build_continuity_context(
            read_only,
            earlier=earlier,
            later=later,
            state_field=state_field,
            domain_contract=domain_definition,
        )
        phase2a_valid = _release_status(read_only, "PHASE2A")
        phase2b_valid = _release_status(read_only, "PHASE2B")
        quality = evaluate_quality(
            context,
            catalog_valid=catalog["table_count"] == 46,
            phase2a_release_valid=phase2a_valid,
            phase2b_release_valid=phase2b_valid,
            mart_and_views_empty=(
                catalog["view_count"] == 0
                and catalog["mart_object_count"] == 0
            ),
            domain_contract_matches=(
                domain_contract["contract_version"]
                == domain_definition.contract_version
                and domain_contract["contract_hash"] == domain_definition.hash()
            ),
        )
        reconciliation = evaluate_reconciliations(context)
        if (
            not quality["publication_allowed"]
            or quality["check_count"] != 24
            or reconciliation["reconciliation_count"] != 10
            or reconciliation["failure_count"] != 0
        ):
            return {
                "status": quality["readiness_status"],
                "quality": {
                    key: value
                    for key, value in quality.items()
                    if key != "checks"
                },
                "reconciliation_status": reconciliation["status"],
                "application_impact": "NONE",
            }
        preserved_before = row_inventory(read_only, exact_tables("PHASE2C"))
    finally:
        read_only.close()

    specifications = specification_inventory()
    protected_before = protected_hash_inventory() if capture_protected_hashes else {}
    external_before = external_baseline()
    pre_operation_hash = file_sha256(database_path)
    working = prepare_working_database(database_path, runtime_root=runtime_root)
    readiness_run_id = uuid4().hex.upper()
    pair_id = stable_id(
        earlier["snapshot_id"],
        later["snapshot_id"],
        state_field,
        readiness_contract["contract_version"],
        readiness_contract["contract_hash"],
        domain_contract["contract_version"],
        domain_contract["contract_hash"],
        earlier["source_sha256"],
        later["source_sha256"],
    )
    connection = connect_temporal(
        working.working_path,
        read_only=False,
        deployment_authorized=True,
        runtime_root=working.working_path.parent,
    )
    try:
        validate_exact_catalog(connection, "PHASE2C")
        validate_controlled_contracts(connection)
        _start_run(
            connection,
            readiness_run_id=readiness_run_id,
            run_type="READINESS_EVALUATION",
            release_id=phase2c_release_id(),
            pre_operation_hash=pre_operation_hash,
            earlier=earlier,
            later=later,
            state_field=state_field,
            readiness_contract=readiness_contract,
            domain_contract=domain_contract,
        )
        _record_publish(
            connection,
            readiness_run_id=readiness_run_id,
            previous_status=None,
            new_status="DRAFT",
            details="Migration-readiness governance evaluation started.",
        )
        _register_pair(
            connection,
            readiness_run_id=readiness_run_id,
            pair_id=pair_id,
            context=context,
            readiness_contract=readiness_contract,
            domain_contract=domain_contract,
        )
        persist_quality(
            connection,
            readiness_run_id=readiness_run_id,
            pair_id=pair_id,
            quality=quality,
        )
        readiness_results = persist_readiness(
            connection,
            readiness_run_id=readiness_run_id,
            pair_id=pair_id,
            quality=quality,
        )
        persist_reconciliations(
            connection,
            readiness_run_id=readiness_run_id,
            pair_id=pair_id,
            reconciliation=reconciliation,
        )
        lineage = build_lineage(
            connection,
            readiness_run_id=readiness_run_id,
            source_context=context,
            readiness_contract=readiness_contract,
            domain_contract=domain_contract,
        )
        if not lineage["complete"]:
            raise Phase2CValidationError("Phase 2C lineage is incomplete.")
        _record_publish(
            connection,
            readiness_run_id=readiness_run_id,
            previous_status="DRAFT",
            new_status="VALIDATED",
            details="Quality, readiness, reconciliation, and lineage controls passed.",
        )
        _record_publish(
            connection,
            readiness_run_id=readiness_run_id,
            previous_status="VALIDATED",
            new_status="PUBLISHED",
            details="Readiness evidence published with analytical activation disabled.",
        )
        _finish_run(
            connection,
            readiness_run_id=readiness_run_id,
            lifecycle_status="PUBLISHED",
            quality=quality,
        )
        preservation = compare_preserved_rows(
            preserved_before,
            row_inventory(connection, exact_tables("PHASE2C")),
        )
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
        published_catalog = validate_exact_catalog(published, "PHASE2C")
        published_preservation = compare_preserved_rows(
            preserved_before,
            row_inventory(published, exact_tables("PHASE2C")),
        )
    finally:
        published.close()
    protected = (
        assert_external_and_protected(protected_before, external_before)
        if capture_protected_hashes
        else {"status": "NOT_CAPTURED"}
    )
    result = {
        "status": PHASE2C_READINESS_PUBLISHED,
        "readiness_run_id": readiness_run_id,
        "pair_id": pair_id,
        "state_field": state_field,
        "database_path": database_path,
        "database_sha256_before": pre_operation_hash,
        "database_sha256_after": file_sha256(database_path),
        "backup_path": working.backup_path,
        "catalog": published_catalog,
        "quality": {
            key: value for key, value in quality.items() if key != "checks"
        },
        "readiness_results": readiness_results,
        "reconciliation": {
            key: value
            for key, value in reconciliation.items()
            if key != "results"
        },
        "lineage": lineage,
        "preservation": published_preservation,
        "protected": protected,
        "specifications": specifications,
        "generated_at": utc_now(),
    }
    evidence_path = evidence_root / readiness_run_id
    evidence_path.mkdir(parents=True, exist_ok=False)
    write_json(evidence_path / "readiness_summary.json", result)
    write_json(
        evidence_path / "quality_summary.json",
        {"controls": quality["checks"]},
    )
    write_json(
        evidence_path / "reconciliation_summary.json",
        {"controls": reconciliation["results"]},
    )
    write_json(evidence_path / "lineage_summary.json", lineage)
    write_json(evidence_path / "protected_hash_verification.json", protected)
    result["evidence_directory"] = evidence_path
    return result


def evaluate_migration_readiness_safe(*args, **kwargs) -> dict:
    try:
        return evaluate_migration_readiness(*args, **kwargs)
    except Phase2CScopeError as exc:
        return {"status": PHASE2C_SCOPE_VIOLATION, "error": str(exc)}
    except Phase2CSourceNotReadyError as exc:
        return {"status": PHASE2C_SOURCE_NOT_READY, "error": str(exc)}
    except Phase2CSourceNotEligibleError as exc:
        return {"status": PHASE2C_SOURCE_NOT_ELIGIBLE, "error": str(exc)}
    except Phase2CPairConflictError as exc:
        return {"status": PHASE2C_PAIR_CONFLICT, "error": str(exc)}
    except Phase2CBaselineError as exc:
        return {"status": PHASE2C_BASELINE_MISMATCH, "error": str(exc)}
    except Exception as exc:
        return {
            "status": PHASE2C_UNAVAILABLE,
            "error": f"{type(exc).__name__}: {exc}",
            "application_impact": "NONE",
        }

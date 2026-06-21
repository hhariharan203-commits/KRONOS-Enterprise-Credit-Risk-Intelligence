from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
WAREHOUSE = ROOT / "data" / "warehouse" / "kronos_risk.duckdb"
SOURCE_DIRS = ("app", "src", "tests")
REQUIRED_PATHS = (
    "app/main.py",
    "data/processed/scored_portfolio.csv",
    "models/pd_model.pkl",
    "models/lgd_model.pkl",
    "models/ead_model.pkl",
    "outputs/model_validation_pack/validation_summary.json",
    "reports/model_validation_pack.pdf",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_python() -> dict:
    files = [
        path
        for directory in SOURCE_DIRS
        for path in (ROOT / directory).rglob("*.py")
    ]
    errors = []
    for path in files:
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "file_count": len(files),
        "errors": errors,
    }


def validate_required_paths() -> dict:
    missing = [item for item in REQUIRED_PATHS if not (ROOT / item).is_file()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "missing": missing,
    }


def validate_registry_rows(
    connection: duckdb.DuckDBPyConnection,
    table: str,
) -> dict:
    rows = connection.execute(
        f"""
        SELECT relative_path, sha256
        FROM {table}
        WHERE is_current = TRUE
        ORDER BY relative_path
        """
    ).fetchall()
    missing = []
    mismatched = []
    for relative_path, expected_hash in rows:
        path = ROOT / Path(relative_path)
        if not path.is_file():
            missing.append(relative_path)
        elif sha256(path) != expected_hash:
            mismatched.append(relative_path)
    return {
        "status": "PASS" if not missing and not mismatched else "FAIL",
        "current_count": len(rows),
        "missing": missing,
        "hash_mismatches": mismatched,
    }


def validate_warehouse() -> dict:
    if not WAREHOUSE.is_file():
        return {"status": "FAIL", "error": "Warehouse is missing."}

    connection = duckdb.connect(str(WAREHOUSE), read_only=True)
    try:
        source_registry = validate_registry_rows(
            connection,
            "control.source_asset",
        )
        artifact_registry = validate_registry_rows(
            connection,
            "control.artifact_registry",
        )
        credit_rows = connection.execute(
            "SELECT COUNT(*) FROM core.fact_credit_risk_snapshot"
        ).fetchone()[0]
        reconciliation_failures = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.vw_latest_reconciliation
            WHERE status <> 'PASS'
            """
        ).fetchone()[0]
        quality_failures = connection.execute(
            """
            SELECT COUNT(*)
            FROM control.vw_latest_data_quality
            WHERE status <> 'PASS'
            """
        ).fetchone()[0]
        batch_status = connection.execute(
            """
            SELECT status
            FROM control.etl_batch
            ORDER BY started_at DESC
            LIMIT 1
            """
        ).fetchone()
        status = (
            "PASS"
            if source_registry["status"] == "PASS"
            and artifact_registry["status"] == "PASS"
            and credit_rows == 50000
            and reconciliation_failures == 0
            and quality_failures == 0
            and batch_status
            and batch_status[0] == "SUCCESS"
            else "FAIL"
        )
        return {
            "status": status,
            "credit_risk_rows": credit_rows,
            "latest_batch_status": batch_status[0] if batch_status else None,
            "reconciliation_failures": reconciliation_failures,
            "quality_failures": quality_failures,
            "source_registry": source_registry,
            "artifact_registry": artifact_registry,
        }
    finally:
        connection.close()


def validate_residuals() -> dict:
    residuals = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if "venv" in relative.parts or ".streamlit" in relative.parts:
            continue
        name = path.name
        if (
            name.endswith(".working.duckdb")
            or name.endswith(".working.duckdb.wal")
            or name.endswith(".json.tmp")
            or ".pyc." in name
        ):
            residuals.append(str(relative).replace("\\", "/"))
    return {
        "status": "PASS" if not residuals else "FAIL",
        "residuals": sorted(residuals),
    }


def main() -> int:
    checks = {
        "python_syntax": validate_python(),
        "required_paths": validate_required_paths(),
        "warehouse": validate_warehouse(),
        "residual_artifacts": validate_residuals(),
    }
    checks["status"] = (
        "PASS"
        if all(value["status"] == "PASS" for value in checks.values())
        else "FAIL"
    )
    print(json.dumps(checks, indent=2))
    return 0 if checks["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

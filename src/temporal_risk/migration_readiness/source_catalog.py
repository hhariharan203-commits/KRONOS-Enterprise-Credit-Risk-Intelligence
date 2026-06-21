from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path

from src.temporal_risk.connection import file_sha256
from src.temporal_risk.migration_readiness.config import (
    AUTHORIZED_FILES,
    AUTHORIZED_PREFIXES,
    BUSINESS_SCHEMAS,
    CURRENT_WAREHOUSE,
    EXCLUDED_PARTS,
    PHASE2C_TABLES,
    PROTECTED_ROOTS,
    ROOT_DIR,
    SCORED_PORTFOLIO,
    VOLATILE_GENERATED_FILES,
)
from src.temporal_risk.migration_readiness.contracts import (
    PHASE2C_BASELINE_MISMATCH,
    Phase2CBaselineError,
    Phase2CValidationError,
)
from src.temporal_risk.pipeline import PHASE2A_TABLES, PHASE2B_TABLES


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


def exact_tables(level: str) -> set[str]:
    if level == "PHASE2A":
        return set(PHASE2A_TABLES)
    if level == "PHASE2B":
        return set(PHASE2A_TABLES) | set(PHASE2B_TABLES)
    if level == "PHASE2C":
        return set(PHASE2A_TABLES) | set(PHASE2B_TABLES) | set(PHASE2C_TABLES)
    raise ValueError(f"Unknown catalog level: {level}")


def validate_exact_catalog(connection, level: str) -> dict:
    signature = catalog_signature(connection)
    expected = sorted(exact_tables(level))
    if (
        signature["schemas"] != sorted(BUSINESS_SCHEMAS)
        or signature["tables"] != expected
        or signature["views"]
        or signature["mart_object_count"] != 0
    ):
        raise Phase2CValidationError(
            f"Exact {level} catalog recognition failed: {signature}"
        )
    return signature


def _cell(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.hex()
    return value


def row_inventory(connection, object_names: set[str] | list[str]) -> dict:
    inventory = {}
    for object_name in sorted(object_names):
        schema, table = object_name.split(".", 1)
        columns = [
            row[0]
            for row in connection.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = ? AND table_name = ?
                ORDER BY ordinal_position
                """,
                [schema, table],
            ).fetchall()
        ]
        info = connection.execute(
            f"PRAGMA table_info('{schema}.{table}')"
        ).fetchall()
        primary = [row[1] for row in info if bool(row[5])]
        if not primary:
            raise Phase2CValidationError(
                f"Protected table lacks a primary key: {object_name}"
            )
        rows = connection.execute(
            f"SELECT * FROM {schema}.{table} ORDER BY {', '.join(primary)}"
        ).fetchall()
        records = {}
        for row in rows:
            payload = {
                name: _cell(value)
                for name, value in zip(columns, row)
            }
            key = json.dumps(
                [_cell(payload[name]) for name in primary],
                sort_keys=True,
                default=str,
            )
            records[key] = hashlib.sha256(
                json.dumps(
                    payload,
                    sort_keys=True,
                    separators=(",", ":"),
                    default=str,
                ).encode("utf-8")
            ).hexdigest().upper()
        inventory[object_name] = {
            "primary_key": primary,
            "row_count": len(rows),
            "rows": records,
        }
    return inventory


def compare_preserved_rows(before: dict, after: dict) -> dict:
    changes = []
    for table, baseline in before.items():
        current = after.get(table, {"rows": {}})
        for key, digest in baseline["rows"].items():
            if current["rows"].get(key) != digest:
                changes.append({"table": table, "primary_key": key})
    result = {
        "matches": not changes,
        "status": "PASS" if not changes else "FAIL",
        "changed_rows": changes,
    }
    if changes:
        raise Phase2CBaselineError(PHASE2C_BASELINE_MISMATCH)
    return result


def _authorized(relative: str) -> bool:
    return (
        relative in AUTHORIZED_FILES
        or relative in VOLATILE_GENERATED_FILES
        or any(relative.startswith(prefix) for prefix in AUTHORIZED_PREFIXES)
    )


def protected_hash_inventory() -> dict:
    candidates = []
    for root_name in PROTECTED_ROOTS:
        root = ROOT_DIR / root_name
        if root.exists():
            candidates.extend(path for path in root.rglob("*") if path.is_file())
    for name in ("README.md", "requirements.txt", "requirements-dev.txt", ".gitignore"):
        path = ROOT_DIR / name
        if path.is_file():
            candidates.append(path)
    inventory = {}
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


def assert_external_and_protected(
    protected_before: dict,
    external_before: dict,
) -> dict:
    protected_after = protected_hash_inventory()
    external_after = external_baseline()
    result = {
        "protected_hashes_unchanged": protected_before == protected_after,
        "external_assets_unchanged": external_before == external_after,
        "protected_file_count": len(protected_before),
        **external_after,
    }
    result["status"] = (
        "PASS"
        if result["protected_hashes_unchanged"]
        and result["external_assets_unchanged"]
        else "FAIL"
    )
    if result["status"] != "PASS":
        raise Phase2CBaselineError(PHASE2C_BASELINE_MISMATCH)
    return result

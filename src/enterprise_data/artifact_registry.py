from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from src.enterprise_data.config import ARTIFACT_ROOTS, ROOT_DIR, WAREHOUSE_DIR
from src.enterprise_data.source_registry import file_sha256, relative_path


STRUCTURED_SUFFIXES = {".csv", ".json"}
BINARY_SUFFIXES = {".pkl", ".pdf", ".png"}
DOCUMENT_SUFFIXES = {".md", ".txt"}
SQL_SUFFIXES = {".sql"}


def discover_artifacts() -> list[Path]:
    artifacts = []
    for root in ARTIFACT_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            try:
                path.resolve().relative_to(WAREHOUSE_DIR.resolve())
                continue
            except ValueError:
                pass
            artifacts.append(path)
    return sorted(set(artifacts))


def content_class(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in STRUCTURED_SUFFIXES:
        return "STRUCTURED"
    if suffix in BINARY_SUFFIXES:
        return "BINARY_METADATA_ONLY"
    if suffix in DOCUMENT_SUFFIXES:
        return "DOCUMENT_METADATA_ONLY"
    if suffix in SQL_SUFFIXES:
        return "SQL_METADATA_ONLY"
    return "OTHER_METADATA_ONLY"


def register_artifacts(connection) -> list[dict]:
    records = []
    now = datetime.now(timezone.utc)
    for path in discover_artifacts():
        sha256 = file_sha256(path)
        relpath = relative_path(path)
        artifact_id = hashlib.sha256(
            f"{relpath}|{sha256}".encode("utf-8")
        ).hexdigest()[:32]
        record = {
            "artifact_id": artifact_id,
            "relative_path": relpath,
            "artifact_type": path.suffix.lower().lstrip(".") or "unknown",
            "content_class": content_class(path),
            "sha256": sha256,
            "size_bytes": path.stat().st_size,
            "modified_at": datetime.fromtimestamp(
                path.stat().st_mtime,
                tz=timezone.utc,
            ),
        }
        connection.execute(
            """
            UPDATE control.artifact_registry
            SET is_current = FALSE
            WHERE relative_path = ?
            """,
            [record["relative_path"]],
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO control.artifact_registry (
                artifact_id, relative_path, artifact_type, content_class,
                sha256, size_bytes, modified_at, registered_at, binary_stored,
                is_current
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, FALSE, TRUE)
            """,
            [
                record["artifact_id"],
                record["relative_path"],
                record["artifact_type"],
                record["content_class"],
                record["sha256"],
                record["size_bytes"],
                record["modified_at"],
                now,
            ],
        )
        connection.execute(
            """
            UPDATE control.artifact_registry
            SET artifact_type = ?, content_class = ?, size_bytes = ?,
                modified_at = ?, registered_at = ?, is_current = TRUE
            WHERE artifact_id = ?
            """,
            [
                record["artifact_type"],
                record["content_class"],
                record["size_bytes"],
                record["modified_at"],
                now,
                record["artifact_id"],
            ],
        )
        records.append(record)
    return records


def current_artifact_hashes() -> dict[str, str]:
    return {
        relative_path(path): file_sha256(path)
        for path in discover_artifacts()
    }

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from src.temporal_risk.config import PHASE_NAME, RELEASE_VERSION


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stable_id(*values: object) -> str:
    payload = "|".join("" if value is None else str(value) for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()


def register_release(
    connection,
    *,
    database_path: str,
    specification_inventory: dict,
    catalog: dict,
) -> str:
    release_id = stable_id(PHASE_NAME, RELEASE_VERSION)
    connection.execute(
        """
        INSERT OR IGNORE INTO control.platform_release (
            release_id, phase_name, release_version, database_path,
            specification_hashes_json, schema_count, table_count,
            view_count, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'DRAFT', ?)
        """,
        [
            release_id,
            PHASE_NAME,
            RELEASE_VERSION,
            database_path,
            json.dumps(specification_inventory, sort_keys=True),
            catalog["schema_count"],
            catalog["table_count"],
            catalog["view_count"],
            utc_now(),
        ],
    )
    connection.execute(
        """
        UPDATE control.platform_release
        SET database_path = ?, specification_hashes_json = ?,
            schema_count = ?, table_count = ?, view_count = ?,
            status = 'DRAFT'
        WHERE release_id = ?
        """,
        [
            database_path,
            json.dumps(specification_inventory, sort_keys=True),
            catalog["schema_count"],
            catalog["table_count"],
            catalog["view_count"],
            release_id,
        ],
    )
    return release_id


def start_deployment(connection, deployment_id: str, release_id: str) -> None:
    connection.execute(
        """
        INSERT INTO control.deployment_run (
            deployment_id, release_id, started_at, status
        ) VALUES (?, ?, ?, 'RUNNING')
        """,
        [deployment_id, release_id, utc_now()],
    )


def finish_deployment(
    connection,
    deployment_id: str,
    *,
    status: str,
    source_sha256: str | None = None,
    working_database_sha256: str | None = None,
    published_database_sha256: str | None = None,
    error: Exception | None = None,
) -> None:
    connection.execute(
        """
        UPDATE control.deployment_run
        SET completed_at = ?, status = ?, source_sha256 = ?,
            working_database_sha256 = ?, published_database_sha256 = ?,
            error_class = ?, error_message = ?
        WHERE deployment_id = ?
        """,
        [
            utc_now(),
            status,
            source_sha256,
            working_database_sha256,
            published_database_sha256,
            type(error).__name__ if error else None,
            str(error) if error else None,
            deployment_id,
        ],
    )


def record_publish_transition(
    connection,
    deployment_id: str,
    *,
    previous_status: str | None,
    new_status: str,
    details: str,
) -> None:
    publish_id = stable_id(deployment_id, previous_status, new_status)
    connection.execute(
        """
        INSERT INTO control.publish_status (
            publish_id, deployment_id, target_name, previous_status,
            new_status, transition_at, details
        ) VALUES (?, ?, 'kronos_temporal_risk.duckdb', ?, ?, ?, ?)
        """,
        [
            publish_id,
            deployment_id,
            previous_status,
            new_status,
            utc_now(),
            details,
        ],
    )


def set_release_status(connection, release_id: str, status: str) -> None:
    connection.execute(
        "UPDATE control.platform_release SET status = ? WHERE release_id = ?",
        [status, release_id],
    )

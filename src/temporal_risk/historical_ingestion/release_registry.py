from __future__ import annotations

import json

from src.temporal_risk.audit import stable_id, utc_now
from src.temporal_risk.historical_ingestion.config import PHASE2B_RELEASE_VERSION


def phase2b_release_id() -> str:
    return stable_id("PHASE2B", PHASE2B_RELEASE_VERSION)


def register_phase2b_release(
    connection,
    *,
    database_path: str,
    specification_inventory: dict,
    catalog: dict,
) -> str:
    release_id = phase2b_release_id()
    existing_phase2a = connection.execute(
        "SELECT release_id FROM control.platform_release WHERE phase_name = 'PHASE2A'"
    ).fetchall()
    if not existing_phase2a:
        raise RuntimeError("A published Phase 2A release is required.")
    connection.execute(
        """
        INSERT OR IGNORE INTO control.platform_release (
            release_id, phase_name, release_version, database_path,
            specification_hashes_json, schema_count, table_count,
            view_count, status, created_at
        ) VALUES (?, 'PHASE2B', ?, ?, ?, ?, ?, ?, 'DRAFT', ?)
        """,
        [
            release_id,
            PHASE2B_RELEASE_VERSION,
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
            schema_count = ?, table_count = ?, view_count = ?, status = 'DRAFT'
        WHERE release_id = ? AND phase_name = 'PHASE2B'
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


def publish_phase2b_release(connection, release_id: str) -> None:
    connection.execute(
        """
        UPDATE control.platform_release
        SET status = 'PUBLISHED'
        WHERE release_id = ? AND phase_name = 'PHASE2B'
        """,
        [release_id],
    )

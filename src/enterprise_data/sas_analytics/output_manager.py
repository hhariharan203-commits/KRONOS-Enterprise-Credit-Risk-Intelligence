from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from src.enterprise_data.config import ROOT_DIR
from src.enterprise_data.sas_analytics.contracts import AnalyticsRunMetadata


DEFAULT_OUTPUT_ROOT = ROOT_DIR / "analytics" / "sas_style_runs"
SAFE_NAME = re.compile(r"^[a-z0-9_]+$")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_name(name: str) -> str:
    if not SAFE_NAME.fullmatch(name):
        raise ValueError(f"Unsafe analytics artifact name: {name}")
    return name


def create_run_directory(
    metadata: AnalyticsRunMetadata,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
) -> Path:
    root = Path(output_root)
    run_directory = root / metadata.analytics_run_id
    run_directory.mkdir(parents=True, exist_ok=False)
    return run_directory


def _json_default(value):
    if pd.isna(value):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    return str(value)


def persist_frame(
    run_directory: Path,
    *,
    name: str,
    frame: pd.DataFrame,
    analytics_module: str,
    warehouse_objects: list[str],
) -> list[dict]:
    name = _validate_name(name)
    csv_path = run_directory / f"{name}.csv"
    json_path = run_directory / f"{name}.json"
    frame.to_csv(csv_path, index=False)
    json_path.write_text(
        json.dumps(
            frame.to_dict("records"),
            indent=2,
            default=_json_default,
        ),
        encoding="utf-8",
    )
    return [
        {
            "relative_path": path.name,
            "sha256": file_sha256(path),
            "size_bytes": path.stat().st_size,
            "analytics_module": analytics_module,
            "warehouse_objects": warehouse_objects,
        }
        for path in (csv_path, json_path)
    ]


def persist_markdown(
    run_directory: Path,
    *,
    name: str,
    markdown: str,
    analytics_module: str,
    warehouse_objects: list[str],
) -> dict:
    name = _validate_name(name)
    path = run_directory / f"{name}.md"
    path.write_text(markdown, encoding="utf-8")
    return {
        "relative_path": path.name,
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
        "analytics_module": analytics_module,
        "warehouse_objects": warehouse_objects,
    }


def persist_json(
    run_directory: Path,
    name: str,
    payload: dict | list,
) -> dict:
    name = _validate_name(name)
    path = run_directory / f"{name}.json"
    path.write_text(
        json.dumps(payload, indent=2, default=_json_default),
        encoding="utf-8",
    )
    return {
        "relative_path": path.name,
        "sha256": file_sha256(path),
        "size_bytes": path.stat().st_size,
    }


def write_hash_inventory(
    run_directory: Path,
    artifacts: list[dict],
) -> dict:
    inventory = [
        {
            "relative_path": artifact["relative_path"],
            "sha256": artifact["sha256"],
            "size_bytes": artifact["size_bytes"],
        }
        for artifact in sorted(
            artifacts,
            key=lambda item: item["relative_path"],
        )
    ]
    return persist_json(run_directory, "hash_inventory", inventory)


def write_run_manifest(
    run_directory: Path,
    metadata: AnalyticsRunMetadata,
    *,
    artifacts: list[dict],
    hash_inventory: dict,
    warehouse_unchanged: bool,
) -> dict:
    payload = {
        "framework": "KRONOS SAS-Style Analytics",
        "terminology": "PROC-Equivalent Analytics",
        "run_metadata": asdict(metadata),
        "output_count": len(artifacts),
        "hash_inventory": hash_inventory,
        "warehouse_read_only": True,
        "warehouse_unchanged": warehouse_unchanged,
        "borrower_level_ranks_persisted": False,
        "current_credit_loss_proxy_disclaimer": (
            "Not IFRS 9 ECL, a provision, or an accounting reserve."
        ),
    }
    return persist_json(run_directory, "manifest", payload)

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from src.temporal_risk.connection import file_sha256
from src.temporal_risk.historical_ingestion.contracts import (
    CONTRACTS,
    HISTORICAL_CONTRACT_VIOLATION,
    OBSERVED_CONTRACT,
    REQUIRED_MANIFEST_FIELDS,
    SIMULATED_CONTRACT,
    HistoricalContractError,
)
from src.temporal_risk.historical_ingestion.config import TEMPORAL_ROOT
from src.temporal_risk.historical_ingestion.source_discovery import (
    repository_relative,
    validate_inbound_file,
)


def load_manifest(
    path: Path | str,
    *,
    runtime_root: Path | str = TEMPORAL_ROOT,
) -> dict:
    manifest_path = Path(path).expanduser().resolve()
    if not manifest_path.is_file():
        raise HistoricalContractError(f"Manifest is unavailable: {manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HistoricalContractError("Manifest JSON is invalid.") from exc
    if not isinstance(payload, dict):
        raise HistoricalContractError("Manifest must be a JSON object.")
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in payload]
    if missing:
        raise HistoricalContractError(
            f"{HISTORICAL_CONTRACT_VIOLATION}: missing {missing}"
        )
    contract = CONTRACTS.get(str(payload["contract_name"]))
    if contract is None or str(payload["contract_version"]) != contract.contract_version:
        raise HistoricalContractError("Historical contract name or version is unsupported.")
    if payload["history_mode"] != contract.history_mode:
        raise HistoricalContractError("History mode does not match the contract.")
    if payload["evidence_classification"] != contract.evidence_classification:
        raise HistoricalContractError(
            "Evidence classification does not match the contract."
        )
    if not payload["observation_date_column"] and not payload["reporting_date_column"]:
        raise HistoricalContractError(
            "A source-supplied observation or reporting date is required."
        )
    try:
        date.fromisoformat(str(payload["declared_snapshot_date"]))
    except ValueError as exc:
        raise HistoricalContractError("Declared snapshot date is invalid.") from exc
    if payload["contract_name"] == OBSERVED_CONTRACT:
        forbidden = {
            "simulation_method",
            "simulation_version",
            "simulation_producer",
            "simulation_seed",
        }
        if any(payload.get(field) not in (None, "") for field in forbidden):
            raise HistoricalContractError(
                "Observed sources must not contain simulation metadata."
            )
    if payload["contract_name"] == SIMULATED_CONTRACT:
        required = (
            "simulation_method",
            "simulation_version",
            "simulation_producer",
        )
        if any(not payload.get(field) for field in required):
            raise HistoricalContractError(
                "Simulated sources require explicit simulation metadata."
            )
    if Path(str(payload["source_file"])).is_absolute():
        raise HistoricalContractError("Manifest source_file must be repository-relative.")
    manifest_path = validate_inbound_file(
        manifest_path,
        payload["history_mode"],
        runtime_root=runtime_root,
    )
    source_path = validate_inbound_file(
        payload["source_file"],
        payload["history_mode"],
        runtime_root=runtime_root,
    )
    payload["manifest_path"] = manifest_path
    payload["manifest_relative_path"] = repository_relative(
        manifest_path,
        runtime_root=runtime_root,
    )
    payload["manifest_sha256"] = file_sha256(manifest_path)
    payload["source_path"] = source_path
    payload["source_relative_path"] = repository_relative(
        source_path,
        runtime_root=runtime_root,
    )
    if file_sha256(source_path) != str(payload["source_file_sha256"]).upper():
        raise HistoricalContractError("Manifest source hash does not match the file.")
    return payload

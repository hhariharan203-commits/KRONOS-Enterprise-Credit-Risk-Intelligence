from __future__ import annotations

import json

import pytest

from src.temporal_risk.historical_ingestion.contracts import HistoricalContractError
from src.temporal_risk.historical_ingestion.manifest import load_manifest
from test_phase2b_contracts import deployed_phase2b, write_manifest


def test_manifest_requires_matching_contract_metadata() -> None:
    root, _ = deployed_phase2b()
    manifest = write_manifest(root)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["evidence_classification"] = "SIMULATED_SOURCE"
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(HistoricalContractError):
        load_manifest(manifest, runtime_root=root)

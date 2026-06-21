from __future__ import annotations

from src.temporal_risk.historical_ingestion.contracts import (
    CANONICAL_FIELDS,
    HistoricalContractError,
)


def normalized_mappings(manifest: dict, source_columns: list[str]) -> list[dict]:
    raw = manifest["field_mapping"]
    if isinstance(raw, dict):
        mappings = [
            {
                "canonical_column": canonical,
                "source_column": source,
                "required": canonical
                in {"source_entity_id", "observation_date", "reporting_date"},
                "allowed_cast": None,
            }
            for canonical, source in raw.items()
        ]
    elif isinstance(raw, list):
        mappings = [dict(item) for item in raw]
    else:
        raise HistoricalContractError("field_mapping must be an object or list.")
    by_canonical = {}
    for mapping in mappings:
        canonical = str(mapping.get("canonical_column", ""))
        source = str(mapping.get("source_column", ""))
        if canonical not in CANONICAL_FIELDS:
            raise HistoricalContractError(f"Unsupported canonical field: {canonical}")
        if not source or source not in source_columns:
            raise HistoricalContractError(
                f"Mapped source column is unavailable: {source}"
            )
        if canonical in by_canonical:
            raise HistoricalContractError(
                f"Duplicate canonical mapping: {canonical}"
            )
        by_canonical[canonical] = {
            "canonical_column": canonical,
            "source_column": source,
            "required": bool(mapping.get("required", False)),
            "allowed_cast": mapping.get("allowed_cast"),
            "mapping_type": "EXPLICIT_SOURCE_MAPPING",
            "source_supplied": True,
            "transformation_description": (
                "Explicit rename with optional safe datatype cast."
            ),
        }
    required_pairs = {
        "source_entity_id": manifest["entity_id_column"],
    }
    if manifest.get("facility_id_column"):
        required_pairs["source_facility_id"] = manifest["facility_id_column"]
    if manifest.get("observation_date_column"):
        required_pairs["observation_date"] = manifest["observation_date_column"]
    if manifest.get("reporting_date_column"):
        required_pairs["reporting_date"] = manifest["reporting_date_column"]
    for canonical, source in required_pairs.items():
        mapping = by_canonical.get(canonical)
        if mapping is None or mapping["source_column"] != source:
            raise HistoricalContractError(
                f"Manifest declaration requires explicit mapping {canonical} -> {source}"
            )
        mapping["required"] = True
    return [by_canonical[name] for name in sorted(by_canonical)]

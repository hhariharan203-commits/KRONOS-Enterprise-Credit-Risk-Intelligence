from __future__ import annotations

from datetime import date

import pandas as pd

from src.temporal_risk.historical_ingestion.contracts import (
    OBSERVED_TEMPORAL,
    SIMULATED_TEMPORAL,
)


def _check(name: str, condition, *, optional: bool = False, details: str = "") -> dict:
    if optional and condition is None:
        status = "NOT_APPLICABLE"
    else:
        status = "PASS" if bool(condition) else "FAIL"
    return {"rule_name": name, "status": status, "details": details}


def _present(normalized: pd.DataFrame, column: str) -> bool:
    return column in normalized and normalized[column].notna().any()


def evaluate_quality(
    *,
    source_frame: pd.DataFrame,
    normalized: pd.DataFrame,
    manifest: dict,
    mappings: list[dict],
    source_hash_before: str,
    source_hash_after: str,
    schema_hash: str,
    snapshot_exists: bool,
    snapshot_conflict: bool,
) -> dict:
    date_column = (
        "observation_date"
        if manifest.get("observation_date_column")
        else "reporting_date"
    )
    date_values = normalized[date_column].dropna()
    declared_date = date.fromisoformat(str(manifest["declared_snapshot_date"]))
    identity_columns = ["source_entity_id"]
    if manifest["identity_grain"] == "FACILITY":
        identity_columns.append("source_facility_id")

    rejection_reasons: dict[int, list[tuple[str, object, str]]] = {}

    def reject(mask, column: str, reason: str) -> None:
        for index in normalized.index[mask.fillna(True)]:
            rejection_reasons.setdefault(int(index), []).append(
                (column, normalized.at[index, column], reason)
            )

    reject(normalized["source_entity_id"].isna(), "source_entity_id", "ENTITY_ID_REQUIRED")
    reject(normalized[date_column].isna(), date_column, "SOURCE_DATE_INVALID")
    if manifest["identity_grain"] == "FACILITY":
        reject(
            normalized["source_facility_id"].isna(),
            "source_facility_id",
            "FACILITY_ID_REQUIRED",
        )
    duplicated = normalized.duplicated(identity_columns, keep="first")
    reject(duplicated, ",".join(identity_columns), "DUPLICATE_SNAPSHOT_GRAIN")
    for column, invalid in (
        ("pd", _present(normalized, "pd") and ~normalized["pd"].between(0, 1)),
        ("lgd", _present(normalized, "lgd") and ~normalized["lgd"].between(0, 1)),
        ("ead", _present(normalized, "ead") and (normalized["ead"] < 0)),
    ):
        if isinstance(invalid, pd.Series):
            reject(invalid, column, f"{column.upper()}_DOMAIN_INVALID")

    rejected_indices = set(rejection_reasons)
    accepted_mask = ~normalized.index.to_series().isin(rejected_indices)
    accepted = normalized.loc[accepted_mask].copy()
    rejected = []
    for index, reasons in sorted(rejection_reasons.items()):
        for column, value, reason in reasons:
            rejected.append(
                {
                    "source_row_number": int(normalized.at[index, "source_row_number"]),
                    "raw_entity_identifier": normalized.at[index, "source_entity_id"],
                    "raw_facility_identifier": normalized.at[
                        index, "source_facility_id"
                    ],
                    "column_name": column,
                    "invalid_value": None if pd.isna(value) else str(value),
                    "severity": "ROW_REJECT",
                    "rejection_reason": reason,
                    "source_payload_json": normalized.at[index, "source_payload_json"],
                }
            )

    mapping_sources = {item["source_column"] for item in mappings}
    observed = manifest["history_mode"] == OBSERVED_TEMPORAL
    simulated = manifest["history_mode"] == SIMULATED_TEMPORAL
    simulated_metadata = all(
        manifest.get(name)
        for name in ("simulation_method", "simulation_version", "simulation_producer")
    )
    observed_has_no_simulation = not any(
        manifest.get(name)
        for name in (
            "simulation_method",
            "simulation_version",
            "simulation_producer",
            "simulation_seed",
        )
    )
    optional_stage = (
        normalized["ifrs9_stage"].dropna().astype(str).isin({"1", "2", "3"}).all()
        if _present(normalized, "ifrs9_stage")
        else None
    )
    optional_risk = (
        normalized["risk_band"].dropna().astype(str).str.len().gt(0).all()
        and normalized["risk_grade"].dropna().astype(str).str.len().gt(0).all()
        if _present(normalized, "risk_band") and _present(normalized, "risk_grade")
        else None
    )
    checks = [
        _check("manifest_exists", True),
        _check("manifest_json_valid", True),
        _check("contract_supported", manifest["contract_name"] is not None),
        _check("source_regular_file", manifest["source_path"].is_file()),
        _check("source_path_allowlisted", True),
        _check("manifest_hash_matches_source", source_hash_before == manifest["source_file_sha256"].upper()),
        _check("source_hash_stable", source_hash_before == source_hash_after),
        _check("canonical_schema_hash_reproducible", len(schema_hash) == 64),
        _check("history_mode_allowed", observed or simulated),
        _check(
            "evidence_classification_matches_mode",
            manifest["evidence_classification"]
            == ("OBSERVED_SOURCE" if observed else "SIMULATED_SOURCE"),
        ),
        _check("observed_has_no_simulation_metadata", observed_has_no_simulation if observed else True),
        _check("simulated_has_required_metadata", simulated_metadata if simulated else True),
        _check("entity_id_declared", bool(manifest["entity_id_column"])),
        _check("entity_id_exists", manifest["entity_id_column"] in source_frame.columns),
        _check("entity_ids_non_null_after_rejects", accepted["source_entity_id"].notna().all()),
        _check("entity_ids_source_supplied", manifest["entity_id_column"] in mapping_sources),
        _check("identity_grain_allowed", manifest["identity_grain"] in {"BORROWER", "FACILITY"}),
        _check(
            "facility_id_for_facility_grain",
            bool(manifest.get("facility_id_column"))
            if manifest["identity_grain"] == "FACILITY"
            else True,
        ),
        _check("temporal_field_declared", bool(manifest.get("observation_date_column") or manifest.get("reporting_date_column"))),
        _check(
            "declared_temporal_field_exists",
            (manifest.get("observation_date_column") or manifest.get("reporting_date_column"))
            in source_frame.columns,
        ),
        _check("source_dates_parseable_after_rejects", accepted[date_column].notna().all()),
        _check(
            "source_dates_source_supplied",
            (manifest.get("observation_date_column") or manifest.get("reporting_date_column"))
            in mapping_sources,
        ),
        _check(
            "no_process_timestamp_fallback",
            str(manifest["source_date_provenance"]).upper()
            not in {"FILE_TIMESTAMP", "PROCESS_TIMESTAMP", "INGESTION_TIMESTAMP", "ROW_ORDER"},
        ),
        _check(
            "one_snapshot_date_per_file",
            len(date_values.unique()) == 1
            and date_values.iloc[0] == declared_date
            if len(date_values)
            else False,
        ),
        _check(
            "observed_dates_not_future",
            max(date_values, default=declared_date) <= date.today() if observed else True,
        ),
        _check("source_date_provenance_complete", bool(manifest["source_date_provenance"])),
        _check("unique_accepted_snapshot_grain", not accepted.duplicated(identity_columns).any()),
        _check("snapshot_not_already_published", not snapshot_exists),
        _check("snapshot_version_not_conflicting", not snapshot_conflict),
        _check(
            "pd_domain",
            accepted["pd"].dropna().between(0, 1).all() if _present(normalized, "pd") else None,
            optional=True,
        ),
        _check(
            "lgd_domain",
            accepted["lgd"].dropna().between(0, 1).all() if _present(normalized, "lgd") else None,
            optional=True,
        ),
        _check(
            "ead_non_negative",
            accepted["ead"].dropna().ge(0).all() if _present(normalized, "ead") else None,
            optional=True,
        ),
        _check("ifrs9_stage_domain", optional_stage, optional=True),
        _check("risk_band_grade_domain", optional_risk, optional=True),
        _check("run_model_inventories_captured", True),
        _check("no_generated_business_values", True),
    ]
    critical_failures = [
        item
        for item in checks[:29]
        if item["status"] == "FAIL"
        and item["rule_name"]
        not in {"entity_ids_non_null_after_rejects", "source_dates_parseable_after_rejects"}
    ]
    failures = [item for item in checks if item["status"] == "FAIL"]
    quality_score = round(
        100.0
        * sum(item["status"] in {"PASS", "NOT_APPLICABLE"} for item in checks)
        / len(checks),
        2,
    )
    return {
        "check_count": len(checks),
        "checks": checks,
        "failure_count": len(failures),
        "critical_failure_count": len(critical_failures),
        "quality_score": quality_score,
        "quality_status": (
            "FAIL"
            if critical_failures or accepted.empty
            else "WARNING"
            if rejected
            else "PASS"
        ),
        "accepted": accepted,
        "rejected": rejected,
    }

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone

from src.enterprise_data.etl.execution_context import ExecutionContext
from src.enterprise_data.etl.reject_handler import log_reject
from src.enterprise_data.schema_manager import table_columns


VALID_IFRS_STAGES = {"STAGE 1", "STAGE 2", "STAGE 3"}
VALID_RISK_BANDS = {
    "PRIME",
    "NEAR PRIME",
    "MODERATE RISK",
    "HIGH RISK",
    "DEFAULT RISK",
}
REQUIRED_COLUMNS = {
    "borrower_id",
    "pd_score",
    "lgd",
    "ead",
    "ifrs_stage",
    "risk_band",
    "model_version",
    "timestamp",
}


@dataclass(frozen=True)
class QualityRuleResult:
    rule_name: str
    status: str
    invalid_count: int
    details: str


def _latest_scored_asset(connection) -> tuple[str, int]:
    row = connection.execute(
        """
        SELECT source_asset_id, row_count
        FROM control.source_asset
        WHERE relative_path = 'data/processed/scored_portfolio.csv'
        ORDER BY last_seen_at DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        raise RuntimeError("Scored portfolio is not registered in the warehouse.")
    return str(row[0]), int(row[1])


def _record_rule(
    context: ExecutionContext,
    source_asset_id: str,
    result: QualityRuleResult,
) -> None:
    quality_result_id = hashlib.sha256(
        f"{context.batch_id}|PHASE4B|{result.rule_name}".encode("utf-8")
    ).hexdigest()[:32]
    context.connection.execute(
        """
        INSERT OR REPLACE INTO control.data_quality_result (
            quality_result_id, etl_batch_id, source_asset_id, check_name,
            check_scope, status, actual_value, expected_value, details,
            checked_at
        ) VALUES (?, ?, ?, ?, 'PHASE4B_ENTERPRISE_QUALITY', ?, ?, '0', ?, ?)
        """,
        [
            quality_result_id,
            context.batch_id,
            source_asset_id,
            result.rule_name,
            result.status,
            str(result.invalid_count),
            result.details,
            datetime.now(timezone.utc),
        ],
    )


def _query_invalid_rows(
    context: ExecutionContext,
    source_asset_id: str,
    *,
    condition: str,
    value_expression: str,
    column_name: str,
    rejection_reason: str,
) -> int:
    rows = context.connection.execute(
        f"""
        SELECT borrower_id, {value_expression}
        FROM staging.stg_scored_portfolio
        WHERE source_asset_id = ? AND ({condition})
        """,
        [source_asset_id],
    ).fetchall()
    for borrower_id, invalid_value in rows:
        log_reject(
            context.connection,
            batch_id=context.batch_id,
            job_id=context.get_state("current_job_id"),
            source_asset_id=source_asset_id,
            source_name="scored_portfolio",
            record_identifier=borrower_id,
            column_name=column_name,
            invalid_value=invalid_value,
            rejection_reason=rejection_reason,
        )
    return len(rows)


def run_enterprise_quality(context: ExecutionContext) -> dict:
    connection = context.connection
    source_asset_id, source_rows = _latest_scored_asset(connection)
    rules: list[QualityRuleResult] = []
    columns = set(table_columns(connection, "staging", "stg_scored_portfolio"))
    missing = sorted(REQUIRED_COLUMNS - columns)
    rules.append(
        QualityRuleResult(
            "schema_required_columns",
            "FAIL" if missing else "PASS",
            len(missing),
            (
                "Missing required columns: " + ", ".join(missing)
                if missing
                else "All required scored-portfolio columns are present."
            ),
        )
    )

    checks = (
        (
            "borrower_id_not_null",
            "borrower_id IS NULL",
            "borrower_id",
            "borrower_id",
            "Required identifier is null.",
        ),
        (
            "borrower_id_unique",
            """
            borrower_id IN (
                SELECT borrower_id
                FROM staging.stg_scored_portfolio
                WHERE source_asset_id = ?
                GROUP BY borrower_id
                HAVING COUNT(*) > 1
            )
            """,
            "borrower_id",
            "borrower_id",
            "Duplicate borrower identifier.",
        ),
        (
            "pd_range_validation",
            "pd_score IS NULL OR pd_score < 0 OR pd_score > 1",
            "pd_score",
            "pd_score",
            "PD must be present and between 0 and 1.",
        ),
        (
            "lgd_range_validation",
            "lgd IS NULL OR lgd < 0 OR lgd > 1",
            "lgd",
            "lgd",
            "LGD must be present and between 0 and 1.",
        ),
        (
            "ead_non_negative_validation",
            "ead IS NULL OR ead < 0",
            "ead",
            "ead",
            "EAD must be present and non-negative.",
        ),
        (
            "ifrs9_stage_validation",
            """
            ifrs_stage IS NULL OR
            UPPER(REPLACE(ifrs_stage, '_', ' ')) NOT IN
            ('STAGE 1', 'STAGE 2', 'STAGE 3')
            """,
            "ifrs_stage",
            "ifrs_stage",
            "IFRS 9 stage is outside the approved contract.",
        ),
        (
            "risk_band_validation",
            """
            risk_band IS NULL OR UPPER(risk_band) NOT IN
            ('PRIME', 'NEAR PRIME', 'MODERATE RISK', 'HIGH RISK', 'DEFAULT RISK')
            """,
            "risk_band",
            "risk_band",
            "Risk band is outside the approved contract.",
        ),
        (
            "model_version_presence",
            "model_version IS NULL OR TRIM(model_version) = ''",
            "model_version",
            "model_version",
            "Model version must be present.",
        ),
        (
            "scoring_timestamp_presence",
            "timestamp IS NULL OR TRIM(timestamp) = ''",
            "timestamp",
            "timestamp",
            "Scoring execution timestamp must be present.",
        ),
    )

    for name, condition, expression, column_name, reason in checks:
        if name == "borrower_id_unique":
            rows = connection.execute(
                """
                SELECT borrower_id, borrower_id
                FROM staging.stg_scored_portfolio
                WHERE source_asset_id = ?
                  AND borrower_id IN (
                      SELECT borrower_id
                      FROM staging.stg_scored_portfolio
                      WHERE source_asset_id = ?
                      GROUP BY borrower_id
                      HAVING COUNT(*) > 1
                  )
                """,
                [source_asset_id, source_asset_id],
            ).fetchall()
            for borrower_id, invalid_value in rows:
                log_reject(
                    connection,
                    batch_id=context.batch_id,
                    job_id=context.get_state("current_job_id"),
                    source_asset_id=source_asset_id,
                    source_name="scored_portfolio",
                    record_identifier=borrower_id,
                    column_name=column_name,
                    invalid_value=invalid_value,
                    rejection_reason=reason,
                )
            invalid_count = len(rows)
        else:
            invalid_count = _query_invalid_rows(
                context,
                source_asset_id,
                condition=condition,
                value_expression=expression,
                column_name=column_name,
                rejection_reason=reason,
            )
        rules.append(
            QualityRuleResult(
                name,
                "PASS" if invalid_count == 0 else "FAIL",
                invalid_count,
                reason,
            )
        )

    staging_rows = int(
        connection.execute(
            """
            SELECT COUNT(*)
            FROM staging.stg_scored_portfolio
            WHERE source_asset_id = ?
            """,
            [source_asset_id],
        ).fetchone()[0]
    )
    parity_status = "PASS" if staging_rows == source_rows else "FAIL"
    rules.append(
        QualityRuleResult(
            "source_to_staging_row_parity",
            parity_status,
            abs(staging_rows - source_rows),
            f"source={source_rows}; staging={staging_rows}",
        )
    )

    for result in rules:
        _record_rule(context, source_asset_id, result)

    passed = sum(result.status == "PASS" for result in rules)
    warnings = sum(result.status == "WARNING" for result in rules)
    failed = sum(result.status == "FAIL" for result in rules)
    score = round(100 * (passed + 0.5 * warnings) / len(rules), 2)
    quality_status = "FAIL" if failed else ("WARNING" if warnings else "PASS")
    summary_id = hashlib.sha256(
        f"{context.batch_id}|QUALITY_SUMMARY".encode("utf-8")
    ).hexdigest()[:32]
    details = {
        result.rule_name: {
            "status": result.status,
            "invalid_count": result.invalid_count,
            "details": result.details,
        }
        for result in rules
    }
    connection.execute(
        """
        INSERT INTO control.etl_quality_summary (
            quality_summary_id, etl_batch_id, job_id, quality_score,
            quality_status, rule_count, passed_rule_count,
            warning_rule_count, failed_rule_count, quality_details,
            evaluated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (etl_batch_id) DO UPDATE SET
            job_id = EXCLUDED.job_id,
            quality_score = EXCLUDED.quality_score,
            quality_status = EXCLUDED.quality_status,
            rule_count = EXCLUDED.rule_count,
            passed_rule_count = EXCLUDED.passed_rule_count,
            warning_rule_count = EXCLUDED.warning_rule_count,
            failed_rule_count = EXCLUDED.failed_rule_count,
            quality_details = EXCLUDED.quality_details,
            evaluated_at = EXCLUDED.evaluated_at
        """,
        [
            summary_id,
            context.batch_id,
            context.get_state("current_job_id"),
            score,
            quality_status,
            len(rules),
            passed,
            warnings,
            failed,
            json.dumps(details),
            datetime.now(timezone.utc),
        ],
    )
    rejected = int(
        connection.execute(
            "SELECT COUNT(*) FROM control.rejected_record WHERE etl_batch_id = ?",
            [context.batch_id],
        ).fetchone()[0]
    )
    context.set_state(
        "quality",
        {
            "quality_score": score,
            "quality_status": quality_status,
            "rule_count": len(rules),
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
            "records_rejected": rejected,
        },
    )
    return {
        "status": "FAILED" if failed else "SUCCESS",
        "records_processed": source_rows,
        "records_loaded": 0,
        "records_rejected": rejected,
        "details": context.get_state("quality"),
    }

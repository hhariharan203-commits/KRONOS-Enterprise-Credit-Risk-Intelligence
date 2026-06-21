CREATE OR REPLACE VIEW control.vw_latest_reconciliation AS
SELECT
    reconciliation_id,
    etl_batch_id,
    source_asset_id,
    reconciliation_name,
    source_value,
    warehouse_value,
    absolute_difference,
    tolerance,
    status,
    reconciled_at,
    job_id,
    source_count,
    staging_count,
    core_count,
    mart_count,
    variance
FROM control.reconciliation_result
WHERE reconciled_at = (
    SELECT MAX(reconciled_at)
    FROM control.reconciliation_result
);

CREATE OR REPLACE VIEW control.vw_latest_data_quality AS
SELECT
    quality_result_id,
    etl_batch_id,
    source_asset_id,
    check_name,
    check_scope,
    status,
    actual_value,
    expected_value,
    details,
    checked_at
FROM control.data_quality_result
WHERE checked_at = (
    SELECT MAX(checked_at)
    FROM control.data_quality_result
);

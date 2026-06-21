CREATE OR REPLACE VIEW control.vw_latest_reconciliation AS
SELECT *
FROM control.reconciliation_result
WHERE reconciled_at = (
    SELECT MAX(reconciled_at)
    FROM control.reconciliation_result
);

CREATE OR REPLACE VIEW control.vw_latest_data_quality AS
SELECT *
FROM control.data_quality_result
WHERE checked_at = (
    SELECT MAX(checked_at)
    FROM control.data_quality_result
);

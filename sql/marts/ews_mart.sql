CREATE OR REPLACE TABLE mart.mart_ews_current AS
SELECT
    borrower_key,
    facility_key,
    early_warning_score,
    watchlist_flag,
    risk_band,
    risk_grade,
    ifrs_stage,
    ead,
    source_run_id,
    warehouse_loaded_at AS warehouse_snapshot_timestamp
FROM mart.vw_current_credit_portfolio;

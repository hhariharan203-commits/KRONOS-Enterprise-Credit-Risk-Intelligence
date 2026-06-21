CREATE OR REPLACE VIEW mart.vw_watchlist_intelligence_current AS
SELECT
    borrower_key,
    facility_key,
    pd_score,
    lgd,
    ead,
    early_warning_score AS ews_score,
    risk_band,
    risk_grade,
    watchlist_flag,
    ROW_NUMBER() OVER (
        ORDER BY
            early_warning_score DESC,
            pd_score DESC,
            ead DESC,
            borrower_key ASC
    ) AS priority_rank,
    source_run_id,
    source_model_version,
    warehouse_loaded_at AS warehouse_snapshot_timestamp
FROM mart.mart_credit_risk_current
WHERE watchlist_flag = 1;

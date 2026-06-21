CREATE OR REPLACE TABLE mart.mart_executive_current AS
SELECT
    COUNT(*) AS portfolio_count,
    SUM(ead) AS total_ead,
    AVG(pd_score) AS average_pd,
    AVG(lgd) AS average_lgd,
    SUM(CASE WHEN watchlist_flag = 1 THEN 1 ELSE 0 END) AS watchlist_accounts,
    SUM(CASE WHEN ifrs_stage = 'STAGE 2' THEN 1 ELSE 0 END) AS stage_2_accounts,
    SUM(CASE WHEN ifrs_stage = 'STAGE 3' THEN 1 ELSE 0 END) AS stage_3_accounts,
    SUM(CASE WHEN risk_band IN ('HIGH RISK', 'DEFAULT RISK') THEN 1 ELSE 0 END) AS high_risk_accounts,
    MIN(source_run_id) AS source_run_id,
    MIN(source_model_version) AS source_model_version,
    MIN(scoring_execution_timestamp) AS scoring_execution_timestamp,
    MIN(temporal_basis) AS temporal_basis,
    MAX(warehouse_loaded_at) AS warehouse_snapshot_timestamp
FROM mart.vw_current_credit_portfolio;

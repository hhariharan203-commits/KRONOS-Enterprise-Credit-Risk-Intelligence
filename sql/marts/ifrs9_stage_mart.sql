CREATE OR REPLACE TABLE mart.mart_ifrs9_stage_current AS
SELECT
    ifrs_stage,
    COUNT(*) AS account_count,
    SUM(ead) AS total_ead,
    AVG(pd_score) AS average_pd,
    AVG(lgd) AS average_lgd,
    MAX(warehouse_loaded_at) AS warehouse_snapshot_timestamp
FROM mart.vw_current_credit_portfolio
GROUP BY ifrs_stage;

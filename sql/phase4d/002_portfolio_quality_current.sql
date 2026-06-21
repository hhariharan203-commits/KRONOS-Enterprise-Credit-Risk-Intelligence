CREATE OR REPLACE VIEW mart.vw_portfolio_quality_current AS
SELECT
    COUNT(*) AS portfolio_count,
    SUM(ead) AS total_ead,
    AVG(pd_score) AS average_pd,
    AVG(lgd) AS average_lgd,
    SUM(pd_score * ead) / NULLIF(SUM(ead), 0) AS weighted_pd,
    SUM(lgd * ead) / NULLIF(SUM(ead), 0) AS weighted_lgd,
    SUM(CASE WHEN watchlist_flag = 1 THEN 1 ELSE 0 END)
        AS watchlist_count,
    SUM(CASE WHEN watchlist_flag = 1 THEN ead ELSE 0 END)
        AS watchlist_exposure,
    SUM(CASE WHEN ifrs_stage = 'STAGE 1' THEN 1 ELSE 0 END)
        AS stage_1_count,
    SUM(CASE WHEN ifrs_stage = 'STAGE 2' THEN 1 ELSE 0 END)
        AS stage_2_count,
    SUM(CASE WHEN ifrs_stage = 'STAGE 3' THEN 1 ELSE 0 END)
        AS stage_3_count,
    SUM(CASE WHEN ifrs_stage = 'STAGE 1' THEN ead ELSE 0 END)
        AS stage_1_exposure,
    SUM(CASE WHEN ifrs_stage = 'STAGE 2' THEN ead ELSE 0 END)
        AS stage_2_exposure,
    SUM(CASE WHEN ifrs_stage = 'STAGE 3' THEN ead ELSE 0 END)
        AS stage_3_exposure,
    SUM(CASE WHEN days_past_due > 0 THEN 1 ELSE 0 END)
        AS delinquent_count,
    SUM(CASE WHEN days_past_due > 0 THEN ead ELSE 0 END)
        AS delinquent_exposure,
    AVG(days_past_due) AS average_days_past_due,
    MAX(days_past_due) AS maximum_days_past_due,
    AVG(total_delinquency) AS average_total_delinquency,
    AVG(credit_utilization) AS average_credit_utilization,
    MAX(credit_utilization) AS maximum_credit_utilization,
    SUM(credit_utilization * ead) / NULLIF(SUM(ead), 0)
        AS exposure_weighted_utilization,
    SUM(pd_score * lgd * ead) AS current_credit_loss_proxy,
    MIN(source_run_id) AS source_run_id,
    MIN(source_model_version) AS source_model_version,
    MIN(scoring_execution_timestamp) AS scoring_execution_timestamp,
    MIN(temporal_basis) AS temporal_basis,
    MIN(temporal_quality) AS temporal_quality,
    MAX(warehouse_loaded_at) AS warehouse_snapshot_timestamp
FROM mart.mart_credit_risk_current;

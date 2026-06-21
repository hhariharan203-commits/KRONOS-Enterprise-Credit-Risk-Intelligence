CREATE OR REPLACE VIEW mart.vw_enterprise_risk_summary_current AS
WITH latest_batch AS (
    SELECT batch.etl_batch_id
    FROM control.etl_batch batch
    JOIN control.publish_status publish
      ON publish.etl_batch_id = batch.etl_batch_id
    WHERE batch.batch_type = 'PHASE4B_CONTROL'
      AND batch.status = 'SUCCESS'
      AND publish.status = 'PUBLISHED'
    ORDER BY COALESCE(publish.transition_at, publish.published_at) DESC
    LIMIT 1
),
quality AS (
    SELECT quality_score, quality_status
    FROM control.etl_quality_summary
    WHERE etl_batch_id = (SELECT etl_batch_id FROM latest_batch)
    ORDER BY evaluated_at DESC
    LIMIT 1
),
reconciliation AS (
    SELECT
        COUNT(*) AS reconciliation_count,
        SUM(CASE WHEN status <> 'PASS' THEN 1 ELSE 0 END)
            AS reconciliation_failures,
        CASE
            WHEN SUM(CASE WHEN status <> 'PASS' THEN 1 ELSE 0 END) = 0
                THEN 'PASS'
            ELSE 'FAIL'
        END AS reconciliation_status
    FROM control.reconciliation_result
    WHERE etl_batch_id = (SELECT etl_batch_id FROM latest_batch)
),
publication AS (
    SELECT status AS publish_status
    FROM control.publish_status
    WHERE etl_batch_id = (SELECT etl_batch_id FROM latest_batch)
    ORDER BY COALESCE(transition_at, published_at) DESC
    LIMIT 1
),
concentration AS (
    SELECT
        MAX(CASE WHEN dimension_type = 'INDUSTRY' THEN hhi END)
            AS industry_hhi,
        MAX(CASE WHEN dimension_type = 'REGION' THEN hhi END)
            AS region_hhi,
        MAX(CASE WHEN dimension_type = 'RISK_BAND' THEN hhi END)
            AS risk_band_hhi,
        MAX(CASE WHEN dimension_type = 'RISK_GRADE' THEN hhi END)
            AS risk_grade_hhi,
        MAX(CASE WHEN dimension_type = 'INDUSTRY'
                 THEN exposure_share END)
            AS largest_industry_exposure_share,
        MAX(CASE WHEN dimension_type = 'REGION'
                 THEN exposure_share END)
            AS largest_region_exposure_share
    FROM mart.vw_concentration_risk_current
),
pd_governance AS (
    SELECT
        approval_status,
        calibration_status,
        psi,
        challenger_status,
        validation_status,
        governance_status,
        artifact_match_status
    FROM mart.vw_model_governance_current
    WHERE model_family = 'PD'
)
SELECT
    portfolio.portfolio_count,
    portfolio.total_ead,
    portfolio.average_pd,
    portfolio.average_lgd,
    portfolio.weighted_pd,
    portfolio.weighted_lgd,
    portfolio.current_credit_loss_proxy,
    portfolio.watchlist_count,
    portfolio.watchlist_exposure,
    portfolio.watchlist_exposure / NULLIF(portfolio.total_ead, 0)
        AS watchlist_exposure_share,
    portfolio.stage_1_count,
    portfolio.stage_2_count,
    portfolio.stage_3_count,
    portfolio.stage_1_exposure,
    portfolio.stage_2_exposure,
    portfolio.stage_3_exposure,
    portfolio.delinquent_count,
    portfolio.delinquent_exposure,
    portfolio.average_credit_utilization,
    concentration.industry_hhi,
    concentration.region_hhi,
    concentration.risk_band_hhi,
    concentration.risk_grade_hhi,
    concentration.largest_industry_exposure_share,
    concentration.largest_region_exposure_share,
    pd_governance.approval_status,
    pd_governance.calibration_status,
    pd_governance.psi,
    pd_governance.challenger_status,
    pd_governance.validation_status,
    pd_governance.governance_status,
    pd_governance.artifact_match_status,
    quality.quality_score AS data_quality_score,
    quality.quality_status AS data_quality_status,
    reconciliation.reconciliation_count,
    reconciliation.reconciliation_failures,
    reconciliation.reconciliation_status,
    publication.publish_status,
    latest_batch.etl_batch_id AS published_batch_id,
    portfolio.source_run_id,
    portfolio.source_model_version,
    portfolio.scoring_execution_timestamp,
    portfolio.temporal_basis,
    portfolio.temporal_quality,
    portfolio.warehouse_snapshot_timestamp
FROM mart.vw_portfolio_quality_current portfolio
CROSS JOIN concentration
CROSS JOIN pd_governance
CROSS JOIN quality
CROSS JOIN reconciliation
CROSS JOIN publication
CROSS JOIN latest_batch;

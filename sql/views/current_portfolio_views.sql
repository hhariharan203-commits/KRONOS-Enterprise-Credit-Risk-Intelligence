CREATE OR REPLACE VIEW mart.vw_current_credit_portfolio AS
SELECT *
FROM core.fact_credit_risk_snapshot
QUALIFY DENSE_RANK() OVER (
    ORDER BY warehouse_loaded_at DESC, source_asset_id DESC
) = 1;

CREATE OR REPLACE VIEW mart.vw_risk_band_summary AS
SELECT
    risk_band,
    COUNT(*) AS account_count,
    SUM(ead) AS total_ead,
    AVG(pd_score) AS average_pd,
    AVG(lgd) AS average_lgd
FROM mart.vw_current_credit_portfolio
GROUP BY risk_band;

CREATE OR REPLACE VIEW mart.vw_risk_grade_summary AS
SELECT
    risk_grade,
    COUNT(*) AS account_count,
    SUM(ead) AS total_ead,
    AVG(pd_score) AS average_pd
FROM mart.vw_current_credit_portfolio
GROUP BY risk_grade;

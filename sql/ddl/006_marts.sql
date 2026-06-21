CREATE TABLE IF NOT EXISTS mart.mart_credit_risk_current AS
SELECT * FROM core.fact_credit_risk_snapshot WHERE FALSE;

CREATE TABLE IF NOT EXISTS mart.mart_ifrs9_stage_current (
    ifrs_stage VARCHAR,
    account_count BIGINT,
    total_ead DOUBLE,
    average_pd DOUBLE,
    average_lgd DOUBLE,
    warehouse_snapshot_timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mart.mart_ews_current (
    borrower_key VARCHAR,
    facility_key VARCHAR,
    early_warning_score DOUBLE,
    watchlist_flag BIGINT,
    risk_band VARCHAR,
    risk_grade VARCHAR,
    ifrs_stage VARCHAR,
    ead DOUBLE,
    source_run_id VARCHAR,
    warehouse_snapshot_timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mart.mart_model_risk (
    record_type VARCHAR,
    model_family VARCHAR,
    metric_name VARCHAR,
    metric_value VARCHAR,
    validation_type VARCHAR,
    validation_status VARCHAR,
    source_asset_id VARCHAR,
    warehouse_loaded_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mart.mart_executive_current (
    portfolio_count BIGINT,
    total_ead DOUBLE,
    average_pd DOUBLE,
    average_lgd DOUBLE,
    watchlist_accounts BIGINT,
    stage_2_accounts BIGINT,
    stage_3_accounts BIGINT,
    high_risk_accounts BIGINT,
    source_run_id VARCHAR,
    source_model_version VARCHAR,
    scoring_execution_timestamp TIMESTAMP,
    temporal_basis VARCHAR,
    warehouse_snapshot_timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mart.mart_data_quality AS
SELECT * FROM core.fact_data_quality WHERE FALSE;

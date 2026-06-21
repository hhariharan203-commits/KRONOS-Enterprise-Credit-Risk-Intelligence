CREATE TABLE IF NOT EXISTS core.fact_credit_risk_snapshot (
    snapshot_id VARCHAR PRIMARY KEY,
    borrower_key VARCHAR NOT NULL,
    facility_key VARCHAR NOT NULL,
    source_asset_id VARCHAR NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    source_run_id VARCHAR,
    source_model_version VARCHAR,
    scoring_execution_timestamp TIMESTAMP,
    temporal_basis VARCHAR NOT NULL,
    temporal_quality VARCHAR NOT NULL,
    pd_score DOUBLE,
    lgd DOUBLE,
    ead DOUBLE,
    credit_score DOUBLE,
    risk_band VARCHAR,
    risk_grade VARCHAR,
    underwriting_decision VARCHAR,
    ifrs_stage VARCHAR,
    scoring_status VARCHAR,
    industry VARCHAR,
    region VARCHAR,
    risk_profile VARCHAR,
    watchlist_flag BIGINT,
    target_default DOUBLE,
    days_past_due DOUBLE,
    total_delinquency DOUBLE,
    credit_utilization DOUBLE,
    payment_burden_ratio DOUBLE,
    loan_to_income_ratio DOUBLE,
    early_warning_score DOUBLE,
    dataset_source VARCHAR,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.fact_market_observation (
    observation_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    source_system VARCHAR NOT NULL,
    observation_date DATE,
    series_key VARCHAR,
    metric_name VARCHAR,
    metric_value DOUBLE,
    payload_json VARCHAR NOT NULL,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.fact_model_performance (
    performance_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    model_family VARCHAR NOT NULL,
    metric_name VARCHAR NOT NULL,
    metric_value VARCHAR,
    source_generated_at TIMESTAMP,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.fact_model_validation (
    validation_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    validation_type VARCHAR NOT NULL,
    validation_status VARCHAR,
    metrics_json VARCHAR NOT NULL,
    source_generated_at TIMESTAMP,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.fact_feature_importance (
    feature_importance_id VARCHAR PRIMARY KEY,
    source_asset_id VARCHAR NOT NULL,
    etl_batch_id VARCHAR NOT NULL,
    feature_name VARCHAR NOT NULL,
    importance DOUBLE,
    importance_pct DOUBLE,
    category VARCHAR,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.fact_data_quality (
    quality_result_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    source_asset_id VARCHAR,
    check_name VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    actual_value VARCHAR,
    expected_value VARCHAR,
    checked_at TIMESTAMP NOT NULL
);

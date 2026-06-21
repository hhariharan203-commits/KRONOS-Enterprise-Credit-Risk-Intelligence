CREATE TABLE IF NOT EXISTS reference.dim_industry (
    industry_key VARCHAR PRIMARY KEY,
    industry_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_region (
    region_key VARCHAR PRIMARY KEY,
    region_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_risk_band (
    risk_band_key VARCHAR PRIMARY KEY,
    risk_band_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_risk_grade (
    risk_grade_key VARCHAR PRIMARY KEY,
    risk_grade_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_ifrs_stage (
    ifrs_stage_key VARCHAR PRIMARY KEY,
    ifrs_stage_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS reference.dim_data_source (
    data_source_key VARCHAR PRIMARY KEY,
    data_source_name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS core.dim_borrower (
    borrower_key VARCHAR PRIMARY KEY,
    source_borrower_id VARCHAR NOT NULL,
    age DOUBLE,
    annual_income DOUBLE,
    employment_years DOUBLE,
    industry VARCHAR,
    region VARCHAR,
    risk_profile VARCHAR,
    source_asset_id VARCHAR NOT NULL,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.dim_credit_facility (
    facility_key VARCHAR PRIMARY KEY,
    borrower_key VARCHAR NOT NULL,
    source_account_id VARCHAR,
    account_proxy_flag BOOLEAN NOT NULL,
    loan_amount DOUBLE,
    interest_rate DOUBLE,
    loan_term DOUBLE,
    credit_limit DOUBLE,
    revolving_balance DOUBLE,
    monthly_payment DOUBLE,
    collateral_value DOUBLE,
    source_asset_id VARCHAR NOT NULL,
    warehouse_loaded_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.dim_model (
    model_version VARCHAR PRIMARY KEY,
    model_version_source VARCHAR NOT NULL,
    artifact_match_status VARCHAR NOT NULL,
    notes VARCHAR,
    first_seen_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS core.dim_model_artifact (
    artifact_id VARCHAR PRIMARY KEY,
    model_family VARCHAR,
    artifact_role VARCHAR NOT NULL,
    relative_path VARCHAR NOT NULL,
    sha256 VARCHAR NOT NULL,
    size_bytes BIGINT NOT NULL,
    modified_at TIMESTAMP
);

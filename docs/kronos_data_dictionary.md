# KRONOS Data Dictionary

Generated from repository inspection. No dashboard code or existing source files were modified.

## Scope

- CSV sources inspected: `data/raw/*.csv`, `data/processed/*.csv`, `data/live/*.csv`, `reports/*.csv`.
- Model artifacts inspected: `models/*.json`, including feature-column and metrics artifacts.
- Engine source inspected: `src/credit_risk`, `src/ews`, `src/provisioning`, `src/stress_testing`, `src/contagion`, `src/decisioning`, `src/live_monitoring`, and `src/reporting`.
- Current app files inspected: `app/main.py` and `app/executive_dashboard.py`.

## KRONOS v1.1 Contract Notes

- Dashboard modules use the standardized `render(shared_data=None)` interface registered by `app/main.py`.
- The scored portfolio contract uses standardized IFRS9 values: `STAGE 1`, `STAGE 2`, and `STAGE 3`.
- Decision outputs now include audit-friendly trace fields: `decision_trace_id`, `decision_rationale`, `recommendation_trace`, and `decision_audit_record`.
- Reporting outputs now include `enterprise_sections` covering portfolio risk, IFRS9, stress testing, concentration risk, watchlist, top exposure, and executive narrative summaries.
- Governance outputs now include model registry metadata, active model designation, performance tracking, and champion/challenger scaffolding.
- This dictionary is a generated snapshot; source data profiles may still show raw upstream values before pipeline standardization.

## CSV Inventory

| CSV File | Rows | Columns |
| --- | --- | --- |
| data/raw/master_credit_dataset.csv | 50000 | 32 |
| data/processed/cleaned_credit_data.csv | 50000 | 32 |
| data/processed/engineered_features.csv | 50000 | 50 |
| data/processed/merged_credit_dataset.csv | 50000 | 51 |
| data/processed/scored_portfolio.csv | 50000 | 63 |
| data/live/fred_market_data.csv | 2136 | 4 |
| data/live/sentiment_data.csv | 97 | 3 |
| data/live/sentiment_summary.csv | 1 | 7 |
| data/live/vix_data.csv | 1256 | 9 |
| reports/category_importance.csv | 16 | 2 |
| reports/feature_importance.csv | 61 | 4 |

## CSV Profile: `data/raw/master_credit_dataset.csv`

- Rows: `50000`
- Columns: `32`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| borrower_id | int64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| age | int64 | 0.0 | 49 | Not categorical or not low-cardinality |
| annual_income | float64 | 0.0 | 46857 | Not categorical or not low-cardinality |
| employment_years | int64 | 0.0 | 35 | Not categorical or not low-cardinality |
| industry | str | 0.0 | 10 | Government, Construction, Manufacturing, Transportation, Retail, Financial Services, Technology, Healthcare, Education, Energy |
| region | str | 0.0 | 5 | East, South, West, Central, North |
| risk_profile | str | 0.0 | 4 | PRIME, HIGH_RISK, SUBPRIME, NEAR_PRIME |
| loan_amount | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| interest_rate | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| loan_term | int64 | 0.0 | 5 | 36, 48, 60, 24, 12 |
| credit_limit | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| revolving_balance | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| monthly_payment | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| delinq_2yrs | int64 | 0.0 | 13 | 0, 8, 4, 6, 2, 1, 5, 3, 7, 9, 10, 11, 12 |
| days_past_due | int64 | 0.0 | 5 | 0, 60, 30, 90, 120 |
| collateral_value | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| dti_ratio | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| credit_utilization | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| payment_burden_ratio | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| loan_to_income_ratio | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| collateral_coverage_ratio | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| macro_sensitivity | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| interest_rate_sensitivity | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| unemployment_sensitivity | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| behavioral_risk_score | float64 | 0.0 | 45587 | Not categorical or not low-cardinality |
| risk_migration_score | float64 | 0.0 | 47380 | Not categorical or not low-cardinality |
| early_warning_score | float64 | 0.0 | 47752 | Not categorical or not low-cardinality |
| ifrs_stage | str | 0.0 | 3 | STAGE 1, STAGE 2, STAGE 3 |
| watchlist_flag | int64 | 0.0 | 2 | 0, 1 |
| target_default | int64 | 0.0 | 2 | 0, 1 |
| lgd_seed | float64 | 0.0 | 48297 | Not categorical or not low-cardinality |
| ead_seed | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |

## CSV Profile: `data/processed/cleaned_credit_data.csv`

- Rows: `50000`
- Columns: `32`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| borrower_id | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| age | float64 | 0.0 | 48 | Not categorical or not low-cardinality |
| annual_income | float64 | 0.0 | 46358 | Not categorical or not low-cardinality |
| employment_years | float64 | 0.0 | 35 | Not categorical or not low-cardinality |
| industry | str | 0.0 | 10 | Government, Construction, Manufacturing, Transportation, Retail, Financial Services, Technology, Healthcare, Education, Energy |
| region | str | 0.0 | 5 | East, South, West, Central, North |
| risk_profile | str | 0.0 | 4 | PRIME, HIGH_RISK, SUBPRIME, NEAR_PRIME |
| loan_amount | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| interest_rate | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| loan_term | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| credit_limit | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| revolving_balance | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| monthly_payment | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| delinq_2yrs | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| days_past_due | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| collateral_value | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| dti_ratio | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| credit_utilization | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| payment_burden_ratio | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| loan_to_income_ratio | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| collateral_coverage_ratio | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| macro_sensitivity | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| interest_rate_sensitivity | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| unemployment_sensitivity | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| behavioral_risk_score | float64 | 0.0 | 45088 | Not categorical or not low-cardinality |
| risk_migration_score | float64 | 0.0 | 46893 | Not categorical or not low-cardinality |
| early_warning_score | float64 | 0.0 | 47253 | Not categorical or not low-cardinality |
| ifrs_stage | str | 0.0 | 3 | STAGE 1, STAGE 2, STAGE 3 |
| watchlist_flag | int64 | 0.0 | 2 | 0, 1 |
| target_default | float64 | 0.0 | 2 | Not categorical or not low-cardinality |
| lgd_seed | float64 | 0.0 | 47798 | Not categorical or not low-cardinality |
| ead_seed | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |

## CSV Profile: `data/processed/engineered_features.csv`

- Rows: `50000`
- Columns: `50`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| borrower_id | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| age | float64 | 0.0 | 48 | Not categorical or not low-cardinality |
| annual_income | float64 | 0.0 | 46358 | Not categorical or not low-cardinality |
| employment_years | float64 | 0.0 | 35 | Not categorical or not low-cardinality |
| industry | str | 0.0 | 10 | Government, Construction, Manufacturing, Transportation, Retail, Financial Services, Technology, Healthcare, Education, Energy |
| region | str | 0.0 | 5 | East, South, West, Central, North |
| risk_profile | str | 0.0 | 4 | PRIME, HIGH_RISK, SUBPRIME, NEAR_PRIME |
| loan_amount | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| interest_rate | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| loan_term | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| credit_limit | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| revolving_balance | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| monthly_payment | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| delinq_2yrs | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| days_past_due | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| collateral_value | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| dti_ratio | float64 | 0.0 | 49699 | Not categorical or not low-cardinality |
| credit_utilization | float64 | 0.0 | 49596 | Not categorical or not low-cardinality |
| payment_burden_ratio | float64 | 0.0 | 49811 | Not categorical or not low-cardinality |
| loan_to_income_ratio | float64 | 0.0 | 49699 | Not categorical or not low-cardinality |
| collateral_coverage_ratio | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| macro_sensitivity | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| interest_rate_sensitivity | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| unemployment_sensitivity | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| behavioral_risk_score | float64 | 0.0 | 45088 | Not categorical or not low-cardinality |
| risk_migration_score | float64 | 0.0 | 46893 | Not categorical or not low-cardinality |
| early_warning_score | float64 | 0.0 | 47253 | Not categorical or not low-cardinality |
| ifrs_stage | str | 0.0 | 3 | STAGE 1, STAGE 2, STAGE 3 |
| watchlist_flag | int64 | 0.0 | 2 | 0, 1 |
| target_default | float64 | 0.0 | 2 | Not categorical or not low-cardinality |
| lgd_seed | float64 | 0.0 | 47798 | Not categorical or not low-cardinality |
| ead_seed | float64 | 0.0 | 49002 | Not categorical or not low-cardinality |
| total_delinquency | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| high_delinquency_flag | int64 | 0.0 | 2 | 0, 1 |
| young_borrower_flag | int64 | 0.0 | 2 | 0, 1 |
| senior_borrower_flag | int64 | 0.0 | 2 | 0, 1 |
| credit_headroom | float64 | 0.0 | 49596 | Not categorical or not low-cardinality |
| credit_buffer_ratio | float64 | 0.0 | 49596 | Not categorical or not low-cardinality |
| disposable_income | float64 | 0.0 | 49811 | Not categorical or not low-cardinality |
| employment_stability_score | float64 | 0.0 | 1048 | Not categorical or not low-cardinality |
| delinquency_severity | float64 | 0.0 | 20 | Not categorical or not low-cardinality |
| age_risk_score | int64 | 0.0 | 2 | 0, 1 |
| collateral_shortfall_ratio | float64 | 0.0 | 9320 | Not categorical or not low-cardinality |
| utilization_x_delinquency | float64 | 0.0 | 26787 | Not categorical or not low-cardinality |
| dti_x_behavioral_risk | float64 | 0.0 | 49999 | Not categorical or not low-cardinality |
| macro_x_behavioral | float64 | 0.0 | 49597 | Not categorical or not low-cardinality |
| risk_migration_x_ews | float64 | 0.0 | 47429 | Not categorical or not low-cardinality |
| ifrs_stage_2_flag | int64 | 0.0 | 1 | 0 |
| ifrs_stage_3_flag | int64 | 0.0 | 1 | 0 |
| risk_segment | str | 0.0 | 2 | LOW_RISK, HIGH_RISK |

## CSV Profile: `data/processed/merged_credit_dataset.csv`

- Rows: `50000`
- Columns: `51`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| borrower_id | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| age | float64 | 0.0 | 48 | Not categorical or not low-cardinality |
| annual_income | float64 | 0.0 | 46305 | Not categorical or not low-cardinality |
| employment_years | float64 | 0.0 | 35 | Not categorical or not low-cardinality |
| industry | str | 0.0 | 10 | Government, Construction, Manufacturing, Transportation, Retail, Financial Services, Technology, Healthcare, Education, Energy |
| region | str | 0.0 | 5 | East, South, West, Central, North |
| risk_profile | str | 0.0 | 4 | PRIME, HIGH_RISK, SUBPRIME, NEAR_PRIME |
| loan_amount | float64 | 0.0 | 48945 | Not categorical or not low-cardinality |
| interest_rate | float64 | 0.0 | 48926 | Not categorical or not low-cardinality |
| loan_term | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| credit_limit | float64 | 0.0 | 48972 | Not categorical or not low-cardinality |
| revolving_balance | float64 | 0.0 | 48960 | Not categorical or not low-cardinality |
| monthly_payment | float64 | 0.0 | 48963 | Not categorical or not low-cardinality |
| delinq_2yrs | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| days_past_due | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| collateral_value | float64 | 0.0 | 48961 | Not categorical or not low-cardinality |
| dti_ratio | float64 | 0.0 | 49642 | Not categorical or not low-cardinality |
| credit_utilization | float64 | 0.0 | 49535 | Not categorical or not low-cardinality |
| payment_burden_ratio | float64 | 0.0 | 49766 | Not categorical or not low-cardinality |
| loan_to_income_ratio | float64 | 0.0 | 49642 | Not categorical or not low-cardinality |
| collateral_coverage_ratio | float64 | 0.0 | 48903 | Not categorical or not low-cardinality |
| macro_sensitivity | float64 | 0.0 | 48932 | Not categorical or not low-cardinality |
| interest_rate_sensitivity | float64 | 0.0 | 48941 | Not categorical or not low-cardinality |
| unemployment_sensitivity | float64 | 0.0 | 48937 | Not categorical or not low-cardinality |
| behavioral_risk_score | float64 | 0.0 | 45052 | Not categorical or not low-cardinality |
| risk_migration_score | float64 | 0.0 | 46832 | Not categorical or not low-cardinality |
| early_warning_score | float64 | 0.0 | 47199 | Not categorical or not low-cardinality |
| ifrs_stage | str | 0.0 | 3 | STAGE 1, STAGE 2, STAGE 3 |
| watchlist_flag | int64 | 0.0 | 2 | 0, 1 |
| target_default | float64 | 0.0 | 2 | Not categorical or not low-cardinality |
| lgd_seed | float64 | 0.0 | 47743 | Not categorical or not low-cardinality |
| ead_seed | float64 | 0.0 | 48946 | Not categorical or not low-cardinality |
| total_delinquency | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| high_delinquency_flag | int64 | 0.0 | 2 | 0, 1 |
| young_borrower_flag | int64 | 0.0 | 2 | 0, 1 |
| senior_borrower_flag | int64 | 0.0 | 2 | 0, 1 |
| credit_headroom | float64 | 0.0 | 49573 | Not categorical or not low-cardinality |
| credit_buffer_ratio | float64 | 0.0 | 49534 | Not categorical or not low-cardinality |
| disposable_income | float64 | 0.0 | 49774 | Not categorical or not low-cardinality |
| employment_stability_score | float64 | 0.0 | 1048 | Not categorical or not low-cardinality |
| delinquency_severity | float64 | 0.0 | 20 | Not categorical or not low-cardinality |
| age_risk_score | int64 | 0.0 | 2 | 0, 1 |
| collateral_shortfall_ratio | float64 | 0.0 | 9320 | Not categorical or not low-cardinality |
| utilization_x_delinquency | float64 | 0.0 | 26778 | Not categorical or not low-cardinality |
| dti_x_behavioral_risk | float64 | 0.0 | 49969 | Not categorical or not low-cardinality |
| macro_x_behavioral | float64 | 0.0 | 49566 | Not categorical or not low-cardinality |
| risk_migration_x_ews | float64 | 0.0 | 47397 | Not categorical or not low-cardinality |
| ifrs_stage_2_flag | int64 | 0.0 | 1 | 0 |
| ifrs_stage_3_flag | int64 | 0.0 | 1 | 0 |
| risk_segment | str | 0.0 | 2 | LOW_RISK, HIGH_RISK |
| dataset_source | str | 0.0 | 1 | KRONOS_MASTER |

## CSV Profile: `data/processed/scored_portfolio.csv`

- Rows: `50000`
- Columns: `63`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| borrower_id | float64 | 0.0 | 50000 | Not categorical or not low-cardinality |
| pd_score | float64 | 0.0 | 41538 | Not categorical or not low-cardinality |
| lgd | float64 | 0.0 | 46609 | Not categorical or not low-cardinality |
| ead | float64 | 0.0 | 49375 | Not categorical or not low-cardinality |
| credit_score | int64 | 0.0 | 545 | Not categorical or not low-cardinality |
| risk_band | str | 0.0 | 5 | PRIME, DEFAULT RISK, HIGH RISK, NEAR PRIME, MODERATE RISK |
| risk_grade | str | 0.0 | 7 | AAA, CCC, B, A, BB, BBB, AA |
| underwriting_decision | str | 0.0 | 4 | APPROVE, REJECT, WATCH, HIGH RISK REVIEW |
| ifrs_stage | str | 0.0 | 3 | STAGE 1, STAGE 2, STAGE 3 |
| timestamp | str | 0.0 | 1 | 2026-06-02T03:57:14+00:00 |
| model_version | str | 0.0 | 1 | 2509ccceea0ae9d0 |
| run_id | str | 0.0 | 1 | 78aaea6cb609410baea6df30dfdd1625 |
| scoring_status | str | 0.0 | 1 | SCORED |
| age | float64 | 0.0 | 48 | Not categorical or not low-cardinality |
| annual_income | float64 | 0.0 | 46305 | Not categorical or not low-cardinality |
| employment_years | float64 | 0.0 | 35 | Not categorical or not low-cardinality |
| industry | str | 0.0 | 10 | Government, Construction, Manufacturing, Transportation, Retail, Financial Services, Technology, Healthcare, Education, Energy |
| region | str | 0.0 | 5 | East, South, West, Central, North |
| risk_profile | str | 0.0 | 4 | PRIME, HIGH_RISK, SUBPRIME, NEAR_PRIME |
| loan_amount | float64 | 0.0 | 48945 | Not categorical or not low-cardinality |
| interest_rate | float64 | 0.0 | 48926 | Not categorical or not low-cardinality |
| loan_term | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| credit_limit | float64 | 0.0 | 48972 | Not categorical or not low-cardinality |
| revolving_balance | float64 | 0.0 | 48960 | Not categorical or not low-cardinality |
| monthly_payment | float64 | 0.0 | 48963 | Not categorical or not low-cardinality |
| delinq_2yrs | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| days_past_due | float64 | 0.0 | 5 | Not categorical or not low-cardinality |
| collateral_value | float64 | 0.0 | 48961 | Not categorical or not low-cardinality |
| dti_ratio | float64 | 0.0 | 49642 | Not categorical or not low-cardinality |
| credit_utilization | float64 | 0.0 | 49535 | Not categorical or not low-cardinality |
| payment_burden_ratio | float64 | 0.0 | 49766 | Not categorical or not low-cardinality |
| loan_to_income_ratio | float64 | 0.0 | 49642 | Not categorical or not low-cardinality |
| collateral_coverage_ratio | float64 | 0.0 | 48903 | Not categorical or not low-cardinality |
| macro_sensitivity | float64 | 0.0 | 48932 | Not categorical or not low-cardinality |
| interest_rate_sensitivity | float64 | 0.0 | 48941 | Not categorical or not low-cardinality |
| unemployment_sensitivity | float64 | 0.0 | 48937 | Not categorical or not low-cardinality |
| behavioral_risk_score | float64 | 0.0 | 45052 | Not categorical or not low-cardinality |
| risk_migration_score | float64 | 0.0 | 46832 | Not categorical or not low-cardinality |
| early_warning_score | float64 | 0.0 | 47199 | Not categorical or not low-cardinality |
| watchlist_flag | int64 | 0.0 | 2 | 0, 1 |
| target_default | float64 | 0.0 | 2 | Not categorical or not low-cardinality |
| lgd_seed | float64 | 0.0 | 47743 | Not categorical or not low-cardinality |
| ead_seed | float64 | 0.0 | 48946 | Not categorical or not low-cardinality |
| total_delinquency | float64 | 0.0 | 8 | Not categorical or not low-cardinality |
| high_delinquency_flag | int64 | 0.0 | 2 | 0, 1 |
| young_borrower_flag | int64 | 0.0 | 2 | 0, 1 |
| senior_borrower_flag | int64 | 0.0 | 2 | 0, 1 |
| credit_headroom | float64 | 0.0 | 49573 | Not categorical or not low-cardinality |
| credit_buffer_ratio | float64 | 0.0 | 49534 | Not categorical or not low-cardinality |
| disposable_income | float64 | 0.0 | 49774 | Not categorical or not low-cardinality |
| employment_stability_score | float64 | 0.0 | 1048 | Not categorical or not low-cardinality |
| delinquency_severity | float64 | 0.0 | 20 | Not categorical or not low-cardinality |
| age_risk_score | int64 | 0.0 | 2 | 0, 1 |
| collateral_shortfall_ratio | float64 | 0.0 | 9320 | Not categorical or not low-cardinality |
| utilization_x_delinquency | float64 | 0.0 | 26778 | Not categorical or not low-cardinality |
| dti_x_behavioral_risk | float64 | 0.0 | 49969 | Not categorical or not low-cardinality |
| macro_x_behavioral | float64 | 0.0 | 49566 | Not categorical or not low-cardinality |
| risk_migration_x_ews | float64 | 0.0 | 47397 | Not categorical or not low-cardinality |
| ifrs_stage_2_flag | int64 | 0.0 | 1 | 0 |
| ifrs_stage_3_flag | int64 | 0.0 | 1 | 0 |
| risk_segment | str | 0.0 | 2 | LOW_RISK, HIGH_RISK |
| dataset_source | str | 0.0 | 1 | KRONOS_MASTER |
| scoring_error | float64 | 100.0 | 0 | Not categorical or not low-cardinality |

## CSV Profile: `data/live/fred_market_data.csv`

- Rows: `2136`
- Columns: `4`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| date | str | 0.0 | 713 | Not categorical or not low-cardinality |
| value | float64 | 0.14 | 1134 | Not categorical or not low-cardinality |
| series_name | str | 0.0 | 13 | fed_funds_rate, cpi, core_cpi, unemployment_rate, real_gdp, industrial_production, 10y_treasury, 2y_treasury, aaa_corporate_yield, bbb_corporate_yield, initial_jobless_claims, consumer_sentiment, recession_indicator |
| series_id | str | 0.0 | 13 | FEDFUNDS, CPIAUCSL, CPILFESL, UNRATE, GDPC1, INDPRO, GS10, GS2, AAA, BAA, ICSA, UMCSENT, USREC |

## CSV Profile: `data/live/sentiment_data.csv`

- Rows: `97`
- Columns: `3`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| headline | str | 0.0 | 96 | Not categorical or not low-cardinality |
| polarity | float64 | 0.0 | 32 | Not categorical or not low-cardinality |
| sentiment | str | 0.0 | 3 | NEUTRAL, BEARISH, BULLISH |

## CSV Profile: `data/live/sentiment_summary.csv`

- Rows: `1`
- Columns: `7`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| market_sentiment_score | float64 | 0.0 | 1 | Not categorical or not low-cardinality |
| stress_score | float64 | 0.0 | 1 | Not categorical or not low-cardinality |
| sentiment_regime | str | 0.0 | 1 | NEUTRAL |
| bullish_headlines | int64 | 0.0 | 1 | 23 |
| bearish_headlines | int64 | 0.0 | 1 | 4 |
| neutral_headlines | int64 | 0.0 | 1 | 73 |
| analysis_timestamp | str | 0.0 | 1 | 2026-06-03 12:53:54 |

## CSV Profile: `data/live/vix_data.csv`

- Rows: `1256`
- Columns: `9`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| date | str | 0.0 | 1256 | Not categorical or not low-cardinality |
| adj_close_^vix | float64 | 0.0 | 859 | Not categorical or not low-cardinality |
| close_^vix | float64 | 0.0 | 859 | Not categorical or not low-cardinality |
| high_^vix | float64 | 0.0 | 914 | Not categorical or not low-cardinality |
| low_^vix | float64 | 0.0 | 840 | Not categorical or not low-cardinality |
| open_^vix | float64 | 0.0 | 850 | Not categorical or not low-cardinality |
| volume_^vix | int64 | 0.0 | 1 | 0 |
| returns | float64 | 0.08 | 1248 | Not categorical or not low-cardinality |
| rolling_volatility | float64 | 2.389 | 1226 | Not categorical or not low-cardinality |

## CSV Profile: `reports/category_importance.csv`

- Rows: `16`
- Columns: `2`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| category | str | 0.0 | 16 | MACRO, BEHAVIORAL, EXPOSURE, COLLATERAL, EMPLOYMENT, INCOME, LOAN_STRUCTURE, OTHER, AFFORDABILITY, DEMOGRAPHICS, LOSS_SEVERITY, LEVERAGE, DELINQUENCY, CREDIT BEHAVIOR, EWS, IFRS9 |
| importance_pct | float64 | 0.0 | 16 | Not categorical or not low-cardinality |

## CSV Profile: `reports/feature_importance.csv`

- Rows: `61`
- Columns: `4`

| Column | Data Type | Null % | Distinct Values | Categorical Values |
| --- | --- | --- | --- | --- |
| feature | str | 0.0 | 61 | Not categorical or not low-cardinality |
| importance | float64 | 0.0 | 60 | Not categorical or not low-cardinality |
| importance_pct | float64 | 0.0 | 60 | Not categorical or not low-cardinality |
| category | str | 0.0 | 16 | MACRO, EMPLOYMENT, AFFORDABILITY, COLLATERAL, BEHAVIORAL, DEMOGRAPHICS, LOSS_SEVERITY, EXPOSURE, LEVERAGE, LOAN_STRUCTURE, INCOME, CREDIT BEHAVIOR, EWS, DELINQUENCY, OTHER, IFRS9 |

## Model Artifacts

| Artifact | Type | Count | Contents / Summary |
| --- | --- | --- | --- |
| models/ead_feature_cols.json | feature list | 62 | borrower_id, age, annual_income, employment_years, loan_amount, interest_rate, loan_term, credit_limit, revolving_balance, monthly_payment, delinq_2yrs, days_past_due, collateral_value, dti_ratio, credit_utilization, payment_burden_ratio, loan_to_income_ratio, collateral_coverage_ratio, macro_sensitivity, interest_rate_sensitivity, unemployment_sensitivity, behavioral_risk_score, risk_migration_score, early_warning_score, watchlist_flag, ... (+37 more) |
| models/ead_metrics.json | metrics/object | 6 | mae: 1572.2559; rmse: 1963.066; r2_score: 0.9839; train_samples: 40000; test_samples: 10000; feature_count: 62 |
| models/feature_cols.json | feature list | 62 | borrower_id, age, annual_income, employment_years, loan_amount, interest_rate, loan_term, credit_limit, revolving_balance, monthly_payment, delinq_2yrs, days_past_due, collateral_value, dti_ratio, credit_utilization, payment_burden_ratio, loan_to_income_ratio, collateral_coverage_ratio, macro_sensitivity, interest_rate_sensitivity, unemployment_sensitivity, behavioral_risk_score, risk_migration_score, early_warning_score, watchlist_flag, ... (+37 more) |
| models/lgd_feature_cols.json | feature list | 62 | borrower_id, age, annual_income, employment_years, loan_amount, interest_rate, loan_term, credit_limit, revolving_balance, monthly_payment, delinq_2yrs, days_past_due, collateral_value, dti_ratio, credit_utilization, payment_burden_ratio, loan_to_income_ratio, collateral_coverage_ratio, macro_sensitivity, interest_rate_sensitivity, unemployment_sensitivity, behavioral_risk_score, risk_migration_score, early_warning_score, watchlist_flag, ... (+37 more) |
| models/lgd_metrics.json | metrics/object | 6 | mae: 0.0348; rmse: 0.0466; r2_score: 0.9661; train_samples: 40000; test_samples: 10000; feature_count: 62 |
| models/model_metrics.json | metrics/object | 11 | accuracy: 0.8607; precision: 0.7402; recall: 0.6278; f1_score: 0.6794; roc_auc: 0.9059; ks_statistic: 0.653; population_stability_index: 0.0039; model_drift: NO DRIFT; train_auc: 0.9465; overfitting_risk: MODERATE OVERFITTING RISK; model_health_score: 78.74 |

## Engine Contracts

| Engine File | Expected / Referenced Stored Inputs | Generated DataFrame Columns | Returned Field Keys | Declared Lists / Artifacts |
| --- | --- | --- | --- | --- |
| src/credit_risk/credit_engine.py | None observed | None observed | credit_score, credit_utilization, default_odds, dti_ratio, expected_rating, high_delinquency_flag, loan_to_income_ratio, model_confidence, payment_burden_ratio, portfolio_segment, probability_of_default, risk_band, risk_grade, senior_borrower_flag, total_delinquency, underwriting_decision, young_borrower_flag | None observed |
| src/credit_risk/ead_engine.py | None observed | None observed | credit_limit, credit_utilization, dti_ratio, ead_percent_of_limit, exposure_band, facility_stress_level, high_delinquency_flag, loan_to_income_ratio, model_confidence, payment_burden_ratio, predicted_ead, senior_borrower_flag, total_delinquency, utilization_category, utilization_rate, young_borrower_flag | EAD_FEATURE_FILE: models/ead_feature_cols.json |
| src/credit_risk/lgd_engine.py | None observed | None observed | credit_utilization, dti_ratio, expected_loss_factor, high_delinquency_flag, lgd, lgd_percent, lgd_risk_band, loan_to_income_ratio, model_confidence, payment_burden_ratio, provisioning_severity, recovery_category, recovery_rate, senior_borrower_flag, total_delinquency, young_borrower_flag | LGD_FEATURE_FILE: models/lgd_feature_cols.json |
| src/credit_risk/model_validation.py | target_default | None observed | accuracy, f1_score, ks_statistic, model_drift, model_health_score, overfitting_risk, population_stability_index, precision, recall, roc_auc, train_auc | None observed |
| src/credit_risk/portfolio_scoring.py | credit_score, ead, ifrs_stage, lgd, model_version, pd_score, risk_band, risk_grade, run_id, scoring_error, scoring_status, timestamp, underwriting_decision | credit_score, ead, ifrs_stage, lgd, model_version, pd_score, risk_band, risk_grade, run_id, scoring_error, scoring_status, timestamp, underwriting_decision | column_count, columns, ead, ead_features, ead_model, ead_scaler, errors, lgd, lgd_features, lgd_model, lgd_scaler, missing_required_columns, model_version, output_path, pd, pd_features, pd_model, pd_scaler, ... (+6 more) | CANONICAL_OUTPUT_COLUMNS: borrower_id, credit_score, ead, ifrs_stage, lgd, model_version, pd_score, risk_band, risk_grade, run_id, scoring_status, timestamp, ... (+1 more) |
| src/credit_risk/scorecard.py | None observed | None observed | borrower_category, credit_grade, credit_score, default_risk, expected_loss, expected_loss_band, exposure_at_default, grade, lending_suitability, loss_given_default, max_score, min_score, monitoring_level, probability_of_default, risk_level | None observed |
| src/credit_risk/train_ead_model.py | None observed | ead_target | feature_count, mae, r2_score, rmse, test_samples, train_samples | EAD_FEATURE_FILE: models/ead_feature_cols.json<br>EAD_METRICS_FILE: models/ead_metrics.json<br>exclude_cols: dataset_source, ead_target, risk_segment, target_default |
| src/credit_risk/train_lgd_model.py | None observed | lgd_target | feature_count, mae, r2_score, rmse, test_samples, train_samples | LGD_FEATURE_FILE: models/lgd_feature_cols.json<br>LGD_METRICS_FILE: models/lgd_metrics.json<br>exclude_cols: dataset_source, lgd_target, risk_segment, target_default |
| src/credit_risk/train_pd_model.py | target_default | None observed | accuracy, auc_score, feature_count, test_samples, train_samples | exclude_cols: dataset_source, risk_segment, target_default |
| src/ews/anomaly_detection.py | None observed | anomaly_flag, anomaly_score, anomaly_status | alerts, anomalous_accounts, anomaly_percentage, anomaly_score, borrower_id, credit_utilization, current_pd, distress_signals, escalation, loan_to_income_ratio, payment_burden_ratio, portfolio_results, previous_pd, risk_concentration, risk_grade, severity, summary, total_accounts, ... (+1 more) | feature_cols: credit_utilization, current_pd, loan_to_income_ratio, payment_burden_ratio, total_delinquency |
| src/ews/ews_engine.py | None observed | None observed | affordability_score, alert_level, component_breakdown, credit_utilization, current_pd, delinquency_score, ews_score, executive_narrative, high_delinquency_flag, monitoring_priority, payment_burden_ratio, previous_pd, recommended_action, risk_grade, total_delinquency, trend, utilization_score, velocity_score | None observed |
| src/ews/migration_tracker.py | borrower_id | ifrs9_stage, migration_direction, migration_risk_score, migration_severity, watchlist_action | borrower_id, current_rating, downgrade_ratio, downgrades, portfolio_health_score, portfolio_results, previous_rating, stable_accounts, summary, total_accounts, transition_matrix, upgrades | None observed |
| src/ews/watchlist.py | borrower_id | escalation_action, executive_narrative, intervention_category, priority_score, review_frequency, total_accounts, watchlist_level | anomaly_score, anomaly_status, borrower_id, critical_queue, current_rating, ews_score, migration_direction, migration_risk_score, portfolio_risk_index, summary, watchlist | None observed |
| src/provisioning/ecl_calculator.py | borrower_id, ead, lgd, pd_score | ecl_segment, executive_narrative, expected_credit_loss, impairment_category, reserve_concentration, reserve_coverage_ratio, reserve_risk_grade | average_borrower_ecl, borrower_id, concentration_risk, current_stage, ead, ecl_segment_distribution, executive_narrative, largest_reserve_concentration, lgd, max_borrower_ecl, pd_score, portfolio_coverage_ratio, portfolio_results, stage3_ecl_amount, stage3_ecl_concentration, stage_distribution, stage_ecl_distribution, summary, ... (+3 more) | None observed |
| src/provisioning/provisioning_engine.py | None observed | None observed | borrower_id, coverage_band, current_rating, ead, ews_score, executive_narrative, expected_credit_loss, ifrs9_stage, impairment_severity, lgd, pd_score, provisioning_horizon, recommended_action, reserve_coverage_ratio, reserve_risk_grade, total_delinquency | None observed |
| src/provisioning/reserve_simulator.py | borrower_id, ead, lgd, pd_score | baseline_ecl, capital_impact, executive_narrative, impairment_shock, reserve_inflation_pct, reserve_pressure, scenario, stage_reserve_inflation_pct, stress_grade, stress_rank, stressed_ecl | average_reserve_inflation_pct, baseline_portfolio_ecl, borrower_id, capital_stress_grade, capital_warning, concentration_risk, current_stage, ead, ead_multiplier, executive_narrative, largest_stressed_exposure, lgd, lgd_multiplier, max_stressed_ecl, pd_multiplier, pd_score, portfolio_reserve_growth_pct, portfolio_results, ... (+6 more) | display_cols: baseline_portfolio_ecl, capital_stress_grade, capital_warning, concentration_risk, largest_stressed_exposure, portfolio_reserve_growth_pct, scenario, stressed_portfolio_ecl |
| src/provisioning/stage_migration.py | borrower_id | escalation_action, executive_narrative, impairment_trend, migration_direction, migration_risk_grade, migration_severity, reserve_pressure_score | borrower_id, current_ecl, current_stage, deterioration_accounts, deterioration_ratio, portfolio_results, portfolio_stage_health, previous_ecl, previous_stage, recovery_accounts, stable_accounts, stage3_concentration, summary, total_accounts, transition_matrix | None observed |
| src/stress_testing/capital_impact.py | None observed | None observed | baseline_capital, baseline_capital_ratio, capital_buffer_erosion_pct, capital_depletion_risk, capital_remaining_pct, capital_resilience_score, capital_status, critical, executive_narrative, healthy, loss_absorption_pct, recovery_action, regulatory_status, solvency_status, stressed, stressed_capital, stressed_capital_ratio, stressed_losses, ... (+1 more) | None observed |
| src/stress_testing/cvar_engine.py | ead, lgd, pd_score | None observed | black_swan_sensitivity, borrower_id, capital_preservation_status, conditional_var, cvar_percentage, cvar_results, ead, executive_narrative, extreme_loss_severity, lgd, loss_distribution, pd_score, portfolio_loss_capacity, portfolio_value, risk_gap, tail_capital_loss, tail_loss_amplification, tail_loss_ratio, ... (+6 more) | None observed |
| src/stress_testing/macro_shock.py | borrower_id, ead, lgd, pd_score | baseline_ecl, executive_narrative, final_stressed_pd, gdp_stressed_pd, macro_regime, portfolio_sensitivity_pct, stress_rank, stressed_ead, stressed_ecl, stressed_lgd, systemic_stress_score, unemployment_stressed_pd | average_stressed_pd, baseline_portfolio_ecl, borrower_id, ead, gdp_shock, inflation_shock, interest_rate_shock, largest_stressed_exposure, lgd, macro_regime, market_volatility_shock, pd_score, portfolio_results, portfolio_sensitivity_pct, scenario, stress_concentration, stressed_portfolio_ecl, summary, ... (+3 more) | None observed |
| src/stress_testing/stress_engine.py | borrower_id, ead, lgd, pd_score | baseline_ecl, capital_pressure, executive_narrative, loss_impact_pct, stress_rank, stress_severity, stress_watchlist, stressed_ecl | average_stressed_pd, baseline_portfolio_loss, borrower_id, concentration_risk, ead, ead_multiplier, executive_narrative, inflation_shock, interest_rate_shock, largest_stressed_exposure, lgd, lgd_multiplier, maximum_stressed_ecl, pd_multiplier, pd_score, portfolio_loss_deterioration_pct, portfolio_results, scenario, ... (+6 more) | None observed |
| src/stress_testing/var_engine.py | ead, lgd, pd_score | None observed | best_return, borrower_id, capital_at_risk, distribution_metrics, ead, executive_narrative, historical_var, kurtosis, lgd, loss_concentration, mean_return, monte_carlo_var, parametric_var, pd_score, portfolio_value, returns_distribution, risk_severity, skewness, ... (+4 more) | None observed |
| src/contagion/cascade_simulator.py | borrower_id, ead, pd_score | None observed | average_acceleration, average_cascade_loss, average_round_loss, borrower_id, cascade_acceleration, cascade_results, connection_strength, ead, executive_narrative, failure_wave, high_systemic_accounts, initial_default_impact, maximum_acceleration, maximum_cascade_loss, network_collapse_risk, pd_score, summary, systemic_failure_severity, ... (+1 more) | None observed |
| src/contagion/contagion_engine.py | borrower_id, ead, pd_score | None observed | average_concentration, average_contagion_risk, borrower_id, cascade_failure_risk, contagion_results, contagion_severity, ead, executive_narrative, exposure_concentration_pct, high_risk_borrowers, highest_contagion_risk, highest_systemic_score, network_stability, pd_score, portfolio_average_contagion, summary, systemic_impact_score, total_portfolio_exposure | None observed |
| src/contagion/network_builder.py | borrower_id, ead | cluster_classification | average_connection_weight, average_network_centrality, borrower_id, connection_weight, critical_nodes, ead, executive_narrative, exposure_concentration_pct, highest_systemic_score, network_centrality, network_edges, network_results, network_stability, source, summary, systemic_importance_score, systemic_node_classification, target, ... (+2 more) | None observed |
| src/contagion/systemic_risk.py | borrower_id, ead, pd_score | None observed | average_collapse_probability, average_enterprise_resilience, average_systemic_fragility, average_systemic_importance, borrower_id, collapse_probability, concentration_risk, contagion_risk, critical_systemic_entities, ead, enterprise_resilience_score, executive_narrative, financial_stability_status, maximum_collapse_probability, maximum_systemic_importance, network_instability, pd_score, portfolio_network_instability, ... (+5 more) | None observed |
| src/decisioning/decision_terminal.py | borrower_id, pd_score, underwriting_decision | None observed | aggregated_risk_score, approved_accounts, average_decision_confidence, average_risk_score, borrower_id, capital_allocation_signal, decision_confidence, decision_results, enhanced_monitoring_accounts, ews_score, executive_narrative, governance_action, intervention_priority, manual_review_accounts, maximum_risk_score, pd_score, policy_compliance, rejected_accounts, ... (+5 more) | None observed |
| src/decisioning/policy_rules.py | borrower_id, pd_score | None observed | approval_denials, approval_eligibility, average_governance_confidence, average_policy_alignment, average_violation_count, borrower_id, breach_severity, critical_governance_breaches, ead, executive_narrative, exposure_policy_status, governance_confidence, governance_escalation, manual_reviews, max_ead, max_pd_score, max_reserve_pressure, max_systemic_risk, ... (+12 more) | None observed |
| src/decisioning/recommendation_engine.py | borrower_id | None observed | aggregated_risk_score, average_recommendation_confidence, average_risk_score, average_systemic_risk, borrower_id, capital_preservation_strategy, critical_priority_accounts, ead, executive_action, executive_escalations, executive_narrative, exposure_reduction_strategy, governance_recommendation, high_priority_accounts, intervention_priority, maximum_risk_score, mitigation_strategy, policy_breach_accounts, ... (+7 more) | None observed |
| src/live_monitoring/live_alerts.py | borrower_id | None observed | alert_confidence, alert_priority, alert_timestamp, average_alert_confidence, borrower_id, critical_priority_alerts, executive_crisis_escalations, executive_escalation, executive_narrative, governance_breach, governance_breaches, high_priority_alerts, live_alert_results, live_risk_pulse_score, maximum_alert_confidence, minimum_alert_confidence, previous_risk_score, reserve_alert, ... (+12 more) | None observed |
| src/live_monitoring/regime_detector.py | None observed | None observed | average_enterprise_resilience, average_recession_probability, average_regime_confidence, average_regime_score, crisis_regime_periods, enterprise_resilience, executive_crisis_escalations, executive_escalation, executive_narrative, gdp_stress, highest_regime_score, inflation_stress, lowest_regime_score, macro_regime_score, market_stability, market_volatility, maximum_recession_probability, monitoring_timestamp, ... (+11 more) | None observed |
| src/live_monitoring/risk_pulse.py | borrower_id, pd_score | None observed | average_enterprise_resilience, average_live_risk_pulse, borrower_id, capital_pressure, critical_escalations, enterprise_resilience, executive_escalation, executive_narrative, high_risk_accounts, highest_live_risk, live_risk_pulse_score, lowest_live_risk, maximum_resilience, minimum_resilience, monitoring_timestamp, pd_score, portfolio_health, previous_pulse_score, ... (+7 more) | None observed |
| src/reporting/narrative_engine.py | None observed | None observed | ai_explainability_narrative, board_level_summary, capital_adequacy_narrative, enterprise_risk_narrative, executive_escalation_narrative, macro_regime_narrative, report_timestamp, strategic_recommendation, systemic_risk_narrative | None observed |
| src/reporting/pdf_builder.py | None observed | None observed | None observed | None observed |
| src/reporting/report_generator.py | stress_score | None observed | average_capital_ratio, average_enterprise_risk, average_risk_pulse, average_stress_score, average_systemic_risk, board_priority, capital_ratio, critical_entities, critical_risk_entities, enterprise_risk_score, executive_escalation, executive_summary, generated_timestamp, governance_status, governance_summary, live_risk_pulse_score, maximum_enterprise_risk, maximum_systemic_risk, ... (+11 more) | None observed |

## Canonical Column Dictionary

| Column Name | Data Type | Source File | Producing Engine | Consuming Dashboard | Business Definition |
| --- | --- | --- | --- | --- | --- |
| adj_close_^vix | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Risk Pulse Dashboard | Market time-series field from the VIX live data feed. |
| age | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Borrower age in years. |
| age_risk_score | int64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Engineered age-related risk score. |
| analysis_timestamp | str | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Not consumed by discovered dashboard code; available for engine contracts | Timestamp of sentiment analysis summary generation. |
| annual_income | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Borrower annual income used for affordability and credit capacity analytics. |
| bearish_headlines | int64 | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Credit Engine Dashboard | Exposure-at-default or exposure concentration field generated or consumed by KRONOS risk engines. |
| behavioral_risk_score | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Behavioral risk indicator used as a model and monitoring feature. |
| borrower_id | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, Credit Engine Dashboard, EWS Monitor, Stress Lab, Contagion Terminal, Provisioning Dashboard, Decision Terminal, Reports Dashboard | Unique borrower/account identifier used to join portfolio, scoring, and borrower-level engine outputs. |
| bullish_headlines | int64 | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Credit Engine Dashboard | Exposure-at-default or exposure concentration field generated or consumed by KRONOS risk engines. |
| category | str | reports/category_importance.csv<br>reports/feature_importance.csv | src/explainability/feature_importance.py | Executive Dashboard, Explainability Dashboard, Reports Dashboard | Feature category or explainability grouping. |
| close_^vix | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Executive Dashboard, Risk Pulse Dashboard | Market time-series field from the VIX live data feed. |
| collateral_coverage_ratio | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Collateral value relative to exposure. |
| collateral_shortfall_ratio | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Engineered ratio measuring collateral shortfall versus exposure. |
| collateral_value | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Estimated collateral value securing the exposure. |
| credit_buffer_ratio | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Credit Engine Dashboard | Relative credit buffer or unused capacity ratio. |
| credit_headroom | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Credit Engine Dashboard | Available credit capacity between credit limit and balance/exposure. |
| credit_limit | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Credit Engine Dashboard | Approved credit limit or facility ceiling. |
| credit_score | int64 | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard | Credit score generated by KRONOS scoring logic. |
| credit_utilization | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, Credit Engine Dashboard, EWS Monitor, Contagion Terminal | Utilized credit as a proportion of available limit. |
| dataset_source | str | data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/merge_datasets.py | Not consumed by discovered dashboard code; available for engine contracts | Dataset lineage flag identifying source/merged dataset membership. |
| date | str | data/live/fred_market_data.csv<br>data/live/vix_data.csv | src/data_pipeline/fetch_fred.py, src/data_pipeline/fetch_vix.py | Executive Dashboard, Risk Pulse Dashboard | Observation date for market or macro time series. |
| days_past_due | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Current delinquency age measured in days past due. |
| delinq_2yrs | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Count of delinquencies over the prior two-year observation period. |
| delinquency_severity | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | EWS Monitor | Engineered severity measure for delinquency status. |
| disposable_income | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Income remaining after payment burden calculation. |
| dti_ratio | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Debt-to-income ratio measuring borrower leverage relative to income. |
| dti_x_behavioral_risk | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Interaction feature between leverage and behavioral risk. |
| ead | float64 | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard, Stress Lab, Contagion Terminal, Provisioning Dashboard, Decision Terminal, Reports Dashboard | Model-estimated exposure at default. |
| ead_seed | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Credit Engine Dashboard | Seed/proxy exposure-at-default value used in model development. |
| early_warning_score | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | EWS Monitor | Early warning score for deterioration monitoring. |
| employment_stability_score | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Engineered score representing employment stability. |
| employment_years | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Years of borrower employment tenure. |
| feature | str | reports/feature_importance.csv | src/explainability/feature_importance.py | Executive Dashboard, Explainability Dashboard, Reports Dashboard | Model feature name in explainability output. |
| headline | str | data/live/sentiment_data.csv | src/data_pipeline/fetch_sentiment.py | Credit Engine Dashboard | News or market headline used for sentiment scoring. |
| high_^vix | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Risk Pulse Dashboard | Market time-series field from the VIX live data feed. |
| high_delinquency_flag | int64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | EWS Monitor | Engineered indicator for elevated delinquency behavior. |
| ifrs_stage | str | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/credit_risk/portfolio_scoring.py, src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, EWS Monitor, Stress Lab, Provisioning Dashboard, Decision Terminal, Reports Dashboard | IFRS 9 impairment stage stored in the portfolio dataset. |
| ifrs_stage_2_flag | int64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Provisioning Dashboard | Engineered binary indicator for IFRS Stage 2. |
| ifrs_stage_3_flag | int64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Provisioning Dashboard | Engineered binary indicator for IFRS Stage 3. |
| importance | float64 | reports/feature_importance.csv | src/explainability/feature_importance.py | Executive Dashboard, Explainability Dashboard, Reports Dashboard | Raw feature importance value. |
| importance_pct | float64 | reports/category_importance.csv<br>reports/feature_importance.csv | src/explainability/feature_importance.py | Executive Dashboard, Explainability Dashboard, Reports Dashboard | Feature or category importance as a percentage. |
| industry | str | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, Stress Lab, Contagion Terminal, Provisioning Dashboard, Decision Terminal | Industry or sector classification used for concentration, contagion, stress, and provisioning segmentation. |
| interest_rate | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard | Contractual loan interest rate. |
| interest_rate_sensitivity | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Sensitivity to interest-rate shocks. |
| lgd | float64 | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard, Stress Lab, Provisioning Dashboard, Reports Dashboard | Model-estimated loss given default. |
| lgd_seed | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Credit Engine Dashboard | Seed/proxy loss-given-default value used in model development. |
| loan_amount | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, Stress Lab | Original loan amount or facility amount. |
| loan_term | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Loan tenor or contractual term. |
| loan_to_income_ratio | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Loan amount relative to annual income. |
| low_^vix | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Risk Pulse Dashboard | Market time-series field from the VIX live data feed. |
| macro_sensitivity | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Risk Pulse Dashboard | Borrower/exposure sensitivity to macroeconomic deterioration. |
| macro_x_behavioral | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Risk Pulse Dashboard | Interaction feature between macro sensitivity and behavioral risk. |
| market_sentiment_score | float64 | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Executive Dashboard, Risk Pulse Dashboard | Aggregate market sentiment score. |
| model_version | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Credit Engine Dashboard, Explainability Dashboard | Model version identifier used during scoring. |
| monthly_payment | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Monthly payment obligation. |
| neutral_headlines | int64 | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Credit Engine Dashboard | Exposure-at-default or exposure concentration field generated or consumed by KRONOS risk engines. |
| open_^vix | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Risk Pulse Dashboard | Market time-series field from the VIX live data feed. |
| payment_burden_ratio | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, EWS Monitor | Monthly payment burden relative to income. |
| pd_score | float64 | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard, Stress Lab, Contagion Terminal, Provisioning Dashboard, Decision Terminal, Reports Dashboard | Model-estimated probability of default. |
| polarity | float64 | data/live/sentiment_data.csv | src/data_pipeline/fetch_sentiment.py | Risk Pulse Dashboard | Numeric sentiment polarity score. |
| region | str | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, Stress Lab, Contagion Terminal, Provisioning Dashboard, Decision Terminal | Geographic region classification used for concentration, stress, and regional vulnerability analytics. |
| returns | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Executive Dashboard, Risk Pulse Dashboard | KRONOS analytical field observed in data or source contracts; definition inferred from field name. |
| revolving_balance | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Current revolving balance outstanding. |
| risk_band | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard, Stress Lab, Contagion Terminal, Decision Terminal | Portfolio risk band assigned from model outputs. |
| risk_grade | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard, EWS Monitor, Stress Lab, Contagion Terminal, Provisioning Dashboard, Decision Terminal, Reports Dashboard | Portfolio risk grade assigned from score/model outputs. |
| risk_migration_score | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | EWS Monitor | Score indicating risk-grade or stage migration pressure. |
| risk_migration_x_ews | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | EWS Monitor | Interaction feature between migration pressure and early warning score. |
| risk_profile | str | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard | Original categorical borrower risk profile before model scoring. |
| risk_segment | str | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Credit Engine Dashboard | Engineered segment used for model development and portfolio grouping. |
| rolling_volatility | float64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Executive Dashboard, Risk Pulse Dashboard | KRONOS analytical field observed in data or source contracts; definition inferred from field name. |
| run_id | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Credit Engine Dashboard | Unique scoring run identifier. |
| scoring_error | float64 | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Not consumed by discovered dashboard code; available for engine contracts | Scoring error message if model inference failed. |
| scoring_status | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Credit Engine Dashboard | Status flag for scoring completion or failure. |
| senior_borrower_flag | int64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Engineered borrower age segment flag for older borrowers. |
| sentiment | str | data/live/sentiment_data.csv | src/data_pipeline/fetch_sentiment.py | Risk Pulse Dashboard | Categorical sentiment classification. |
| sentiment_regime | str | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Executive Dashboard, Risk Pulse Dashboard | Categorical sentiment regime classification. |
| series_id | str | data/live/fred_market_data.csv | src/data_pipeline/fetch_fred.py | Executive Dashboard, Risk Pulse Dashboard | FRED series identifier. |
| series_name | str | data/live/fred_market_data.csv | src/data_pipeline/fetch_fred.py | Executive Dashboard, Risk Pulse Dashboard | Human-readable FRED series name. |
| stress_score | float64 | data/live/sentiment_summary.csv | src/data_pipeline/fetch_sentiment.py | Executive Dashboard, Stress Lab, Risk Pulse Dashboard | Aggregate stress score from live sentiment or monitoring outputs. |
| target_default | float64, int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Executive Dashboard, Credit Engine Dashboard, Stress Lab, Provisioning Dashboard | Training target indicating realized/default outcome. |
| timestamp | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Not consumed by discovered dashboard code; available for engine contracts | Timestamp of scoring or data generation run. |
| total_delinquency | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | EWS Monitor | Engineered combined delinquency measure. |
| underwriting_decision | str | data/processed/scored_portfolio.csv | src/credit_risk/portfolio_scoring.py | Executive Dashboard, Credit Engine Dashboard, Decision Terminal | Decision outcome generated by scoring or credit policy rules. |
| unemployment_sensitivity | float64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | Not consumed by discovered dashboard code; available for engine contracts | Sensitivity to unemployment shock conditions. |
| utilization_x_delinquency | float64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | EWS Monitor | Interaction feature between utilization and delinquency. |
| value | float64 | data/live/fred_market_data.csv | src/data_pipeline/fetch_fred.py | Executive Dashboard, Risk Pulse Dashboard | FRED macroeconomic series value. |
| volume_^vix | int64 | data/live/vix_data.csv | src/data_pipeline/fetch_vix.py | Risk Pulse Dashboard | Market time-series field from the VIX live data feed. |
| watchlist_flag | int64 | data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv<br>data/raw/master_credit_dataset.csv | src/data_pipeline/fetch_credit_data.py, src/data_pipeline/preprocess_credit.py | EWS Monitor, Decision Terminal | Flag indicating whether the borrower is on a watchlist. |
| young_borrower_flag | int64 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv | src/data_pipeline/feature_engineering.py | Not consumed by discovered dashboard code; available for engine contracts | Engineered borrower age segment flag for younger borrowers. |

## Contract Gaps and Risks

### Duplicate Fields Across Files

| Column | File Count | Files |
| --- | --- | --- |
| age | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| age_risk_score | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| annual_income | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| behavioral_risk_score | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| borrower_id | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| category | 2 | reports/category_importance.csv<br>reports/feature_importance.csv |
| collateral_coverage_ratio | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| collateral_shortfall_ratio | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| collateral_value | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| credit_buffer_ratio | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| credit_headroom | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| credit_limit | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| credit_utilization | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| dataset_source | 2 | data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| date | 2 | data/live/fred_market_data.csv<br>data/live/vix_data.csv |
| days_past_due | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| delinq_2yrs | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| delinquency_severity | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| disposable_income | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| dti_ratio | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| dti_x_behavioral_risk | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| ead_seed | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| early_warning_score | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| employment_stability_score | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| employment_years | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| high_delinquency_flag | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| ifrs_stage | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| ifrs_stage_2_flag | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| ifrs_stage_3_flag | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| importance_pct | 2 | reports/category_importance.csv<br>reports/feature_importance.csv |
| industry | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| interest_rate | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| interest_rate_sensitivity | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| lgd_seed | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| loan_amount | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| loan_term | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| loan_to_income_ratio | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| macro_sensitivity | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| macro_x_behavioral | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| monthly_payment | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| payment_burden_ratio | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| region | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| revolving_balance | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| risk_migration_score | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| risk_migration_x_ews | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| risk_profile | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| risk_segment | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| senior_borrower_flag | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| target_default | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| total_delinquency | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| unemployment_sensitivity | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| utilization_x_delinquency | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| watchlist_flag | 5 | data/raw/master_credit_dataset.csv<br>data/processed/cleaned_credit_data.csv<br>data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |
| young_borrower_flag | 3 | data/processed/engineered_features.csv<br>data/processed/merged_credit_dataset.csv<br>data/processed/scored_portfolio.csv |

### Model Feature Columns Not Persisted as CSV Columns

These are mostly one-hot encoded feature names expected by model artifacts. They are not stored as raw columns in the inspected CSVs and must be regenerated by the scoring preprocessing path.

| Feature Column Missing From CSV |
| --- |
| ifrs_stage_Stage_2 |
| ifrs_stage_Stage_3 |
| industry_Education |
| industry_Energy |
| industry_Financial Services |
| industry_Government |
| industry_Healthcare |
| industry_Manufacturing |
| industry_Retail |
| industry_Technology |
| industry_Transportation |
| region_East |
| region_North |
| region_South |
| region_West |
| risk_profile_NEAR_PRIME |
| risk_profile_PRIME |
| risk_profile_SUBPRIME |

### Engine Generated Fields Not Persisted in CSV Outputs

These fields are generated in source contracts but do not appear in the inspected CSV outputs. Dashboards should calculate them at runtime, receive them from engine returns, or hide dependent UI when unavailable.

| Generated Field | Producing Engine(s) |
| --- | --- |
| anomaly_flag | src/ews/anomaly_detection.py |
| anomaly_score | src/ews/anomaly_detection.py |
| anomaly_status | src/ews/anomaly_detection.py |
| baseline_ecl | src/provisioning/reserve_simulator.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| capital_impact | src/provisioning/reserve_simulator.py |
| capital_pressure | src/stress_testing/stress_engine.py |
| cluster_classification | src/contagion/network_builder.py |
| ead_target | src/credit_risk/train_ead_model.py |
| ecl_segment | src/provisioning/ecl_calculator.py |
| escalation_action | src/ews/watchlist.py<br>src/provisioning/stage_migration.py |
| executive_narrative | src/ews/watchlist.py<br>src/provisioning/ecl_calculator.py<br>src/provisioning/reserve_simulator.py<br>src/provisioning/stage_migration.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| expected_credit_loss | src/provisioning/ecl_calculator.py |
| final_stressed_pd | src/stress_testing/macro_shock.py |
| gdp_stressed_pd | src/stress_testing/macro_shock.py |
| ifrs9_stage | src/ews/migration_tracker.py |
| impairment_category | src/provisioning/ecl_calculator.py |
| impairment_shock | src/provisioning/reserve_simulator.py |
| impairment_trend | src/provisioning/stage_migration.py |
| intervention_category | src/ews/watchlist.py |
| lgd_target | src/credit_risk/train_lgd_model.py |
| loss_impact_pct | src/stress_testing/stress_engine.py |
| macro_regime | src/stress_testing/macro_shock.py |
| migration_direction | src/ews/migration_tracker.py<br>src/provisioning/stage_migration.py |
| migration_risk_grade | src/provisioning/stage_migration.py |
| migration_risk_score | src/ews/migration_tracker.py |
| migration_severity | src/ews/migration_tracker.py<br>src/provisioning/stage_migration.py |
| portfolio_sensitivity_pct | src/stress_testing/macro_shock.py |
| priority_score | src/ews/watchlist.py |
| reserve_concentration | src/provisioning/ecl_calculator.py |
| reserve_coverage_ratio | src/provisioning/ecl_calculator.py |
| reserve_inflation_pct | src/provisioning/reserve_simulator.py |
| reserve_pressure | src/provisioning/reserve_simulator.py |
| reserve_pressure_score | src/provisioning/stage_migration.py |
| reserve_risk_grade | src/provisioning/ecl_calculator.py |
| review_frequency | src/ews/watchlist.py |
| scenario | src/provisioning/reserve_simulator.py |
| stage_reserve_inflation_pct | src/provisioning/reserve_simulator.py |
| stress_grade | src/provisioning/reserve_simulator.py |
| stress_rank | src/provisioning/reserve_simulator.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| stress_severity | src/stress_testing/stress_engine.py |
| stress_watchlist | src/stress_testing/stress_engine.py |
| stressed_ead | src/stress_testing/macro_shock.py |
| stressed_ecl | src/provisioning/reserve_simulator.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| stressed_lgd | src/stress_testing/macro_shock.py |
| systemic_stress_score | src/stress_testing/macro_shock.py |
| total_accounts | src/ews/watchlist.py |
| unemployment_stressed_pd | src/stress_testing/macro_shock.py |
| watchlist_action | src/ews/migration_tracker.py |
| watchlist_level | src/ews/watchlist.py |

### Engine Referenced Fields Not Present in CSV Outputs

Static scan detected these as subscripted field names in engines but they are not persisted in inspected CSVs. Some are intermediate dictionary keys rather than portfolio columns.

| Referenced Field | Referencing Engine(s) |
| --- | --- |
| aggregated_risk_score | src/decisioning/decision_terminal.py<br>src/decisioning/recommendation_engine.py |
| alert_confidence | src/live_monitoring/live_alerts.py |
| alert_priority | src/live_monitoring/live_alerts.py |
| anomaly_flag | src/ews/anomaly_detection.py |
| anomaly_score | src/ews/anomaly_detection.py |
| anomaly_status | src/ews/anomaly_detection.py |
| approval_eligibility | src/decisioning/policy_rules.py |
| average_capital_ratio | src/reporting/report_generator.py |
| average_contagion_risk | src/contagion/contagion_engine.py |
| average_enterprise_risk | src/reporting/report_generator.py |
| average_risk_pulse | src/reporting/report_generator.py |
| average_stress_score | src/reporting/report_generator.py |
| average_systemic_risk | src/reporting/report_generator.py |
| baseline_ecl | src/provisioning/reserve_simulator.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| borrower_count | src/provisioning/reserve_simulator.py |
| breach_severity | src/decisioning/policy_rules.py |
| capital_allocation_signal | src/decisioning/decision_terminal.py |
| capital_impact | src/provisioning/reserve_simulator.py |
| capital_pressure | src/live_monitoring/risk_pulse.py<br>src/stress_testing/stress_engine.py |
| capital_ratio | src/reporting/report_generator.py |
| cascade_acceleration | src/contagion/cascade_simulator.py |
| cascade_failure_risk | src/contagion/contagion_engine.py |
| cluster_classification | src/contagion/network_builder.py |
| collapse_probability | src/contagion/systemic_risk.py |
| connection_weight | src/contagion/network_builder.py |
| contagion_severity | src/contagion/contagion_engine.py |
| critical | src/stress_testing/capital_impact.py |
| critical_risk_entities | src/reporting/report_generator.py |
| current_ecl | src/provisioning/stage_migration.py |
| current_rating | src/ews/migration_tracker.py |
| current_stage | src/provisioning/ecl_calculator.py<br>src/provisioning/stage_migration.py |
| decision_confidence | src/decisioning/decision_terminal.py |
| default_risk | src/credit_risk/scorecard.py |
| deterioration_ratio | src/provisioning/stage_migration.py |
| downgrade_ratio | src/ews/migration_tracker.py |
| ead_features | src/credit_risk/portfolio_scoring.py |
| ead_model | src/credit_risk/portfolio_scoring.py |
| ead_multiplier | src/provisioning/reserve_simulator.py<br>src/stress_testing/stress_engine.py |
| ead_scaler | src/credit_risk/portfolio_scoring.py |
| ead_target | src/credit_risk/train_ead_model.py |
| ecl_segment | src/provisioning/ecl_calculator.py |
| enterprise_resilience | src/live_monitoring/regime_detector.py<br>src/live_monitoring/risk_pulse.py |
| enterprise_resilience_score | src/contagion/systemic_risk.py |
| enterprise_risk_score | src/reporting/report_generator.py |
| escalation_action | src/ews/watchlist.py<br>src/provisioning/stage_migration.py |
| executive_action | src/decisioning/recommendation_engine.py |
| executive_escalation | src/live_monitoring/live_alerts.py<br>src/live_monitoring/regime_detector.py<br>src/live_monitoring/risk_pulse.py |
| executive_narrative | src/ews/watchlist.py<br>src/provisioning/ecl_calculator.py<br>src/provisioning/reserve_simulator.py<br>src/provisioning/stage_migration.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| expected_credit_loss | src/provisioning/ecl_calculator.py |
| exposure_concentration_pct | src/contagion/contagion_engine.py<br>src/contagion/network_builder.py |
| failure_wave | src/contagion/cascade_simulator.py |
| final_stressed_pd | src/stress_testing/macro_shock.py |
| gdp_shock | src/stress_testing/macro_shock.py |
| gdp_stressed_pd | src/stress_testing/macro_shock.py |
| governance_action | src/decisioning/decision_terminal.py |
| governance_breach | src/live_monitoring/live_alerts.py |
| governance_confidence | src/decisioning/policy_rules.py |
| governance_escalation | src/decisioning/policy_rules.py |
| governance_recommendation | src/decisioning/recommendation_engine.py |
| grade | src/credit_risk/scorecard.py |
| healthy | src/stress_testing/capital_impact.py |
| ifrs9_stage | src/ews/migration_tracker.py |
| impairment_category | src/provisioning/ecl_calculator.py |
| impairment_shock | src/provisioning/reserve_simulator.py |
| impairment_trend | src/provisioning/stage_migration.py |
| inflation_shock | src/stress_testing/macro_shock.py |
| initial_default_impact | src/contagion/cascade_simulator.py |
| interest_rate_shock | src/stress_testing/macro_shock.py |
| intervention_category | src/ews/watchlist.py |
| intervention_priority | src/decisioning/recommendation_engine.py |
| lgd_features | src/credit_risk/portfolio_scoring.py |
| lgd_model | src/credit_risk/portfolio_scoring.py |
| lgd_multiplier | src/provisioning/reserve_simulator.py<br>src/stress_testing/stress_engine.py |
| lgd_scaler | src/credit_risk/portfolio_scoring.py |
| lgd_target | src/credit_risk/train_lgd_model.py |
| live_risk_pulse_score | src/live_monitoring/risk_pulse.py<br>src/reporting/report_generator.py |
| loss_impact_pct | src/stress_testing/stress_engine.py |
| macro_regime | src/stress_testing/macro_shock.py |
| macro_regime_score | src/live_monitoring/regime_detector.py |
| market_stability | src/live_monitoring/regime_detector.py |
| market_volatility_shock | src/stress_testing/macro_shock.py |
| max_ead | src/decisioning/policy_rules.py |
| max_pd_score | src/decisioning/policy_rules.py |
| max_reserve_pressure | src/decisioning/policy_rules.py |
| max_score | src/credit_risk/scorecard.py |
| max_systemic_risk | src/decisioning/policy_rules.py |
| maximum_enterprise_risk | src/reporting/report_generator.py |
| maximum_systemic_risk | src/reporting/report_generator.py |
| migration_direction | src/ews/migration_tracker.py<br>src/provisioning/stage_migration.py |
| migration_risk_grade | src/provisioning/stage_migration.py |
| migration_risk_score | src/ews/migration_tracker.py |
| migration_severity | src/ews/migration_tracker.py<br>src/provisioning/stage_migration.py |
| min_score | src/credit_risk/scorecard.py |
| minimum_capital_ratio | src/reporting/report_generator.py |
| network_centrality | src/contagion/network_builder.py |
| network_instability | src/contagion/systemic_risk.py |
| pd_features | src/credit_risk/portfolio_scoring.py |
| pd_model | src/credit_risk/portfolio_scoring.py |
| pd_multiplier | src/provisioning/reserve_simulator.py<br>src/stress_testing/stress_engine.py |
| pd_scaler | src/credit_risk/portfolio_scoring.py |
| period | src/live_monitoring/regime_detector.py |
| policy_alignment_score | src/decisioning/policy_rules.py |
| policy_compliance | src/decisioning/decision_terminal.py |
| policy_status | src/decisioning/recommendation_engine.py |
| portfolio_health | src/live_monitoring/risk_pulse.py |
| portfolio_sensitivity_pct | src/stress_testing/macro_shock.py |
| portfolio_size | src/reporting/report_generator.py |
| previous_ecl | src/provisioning/stage_migration.py |
| previous_rating | src/ews/migration_tracker.py |
| previous_stage | src/provisioning/stage_migration.py |
| priority_score | src/ews/watchlist.py |
| recession_probability | src/live_monitoring/regime_detector.py |
| recommendation_confidence | src/decisioning/recommendation_engine.py |
| regime_classification | src/live_monitoring/regime_detector.py |
| regime_confidence | src/live_monitoring/regime_detector.py |
| regime_transition | src/live_monitoring/regime_detector.py |
| reserve_concentration | src/provisioning/ecl_calculator.py |
| reserve_coverage_ratio | src/provisioning/ecl_calculator.py |
| reserve_inflation_pct | src/provisioning/reserve_simulator.py |
| reserve_pressure | src/provisioning/reserve_simulator.py |
| reserve_pressure_score | src/provisioning/stage_migration.py |
| reserve_risk_grade | src/provisioning/ecl_calculator.py |
| review_frequency | src/ews/watchlist.py |
| risk_deterioration | src/live_monitoring/live_alerts.py |
| risk_level | src/credit_risk/scorecard.py |
| risk_trend | src/live_monitoring/risk_pulse.py |
| scenario | src/provisioning/reserve_simulator.py |
| source | src/contagion/network_builder.py |
| stage | src/provisioning/reserve_simulator.py |
| stage_baseline_ecl | src/provisioning/reserve_simulator.py |
| stage_reserve_inflation_pct | src/provisioning/reserve_simulator.py |
| stage_stressed_ecl | src/provisioning/reserve_simulator.py |
| stress_alert | src/live_monitoring/live_alerts.py |
| stress_grade | src/provisioning/reserve_simulator.py |
| stress_rank | src/provisioning/reserve_simulator.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| stress_severity | src/stress_testing/stress_engine.py |
| stress_watchlist | src/stress_testing/stress_engine.py |
| stressed | src/stress_testing/capital_impact.py |
| stressed_ead | src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| stressed_ecl | src/provisioning/reserve_simulator.py<br>src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| stressed_lgd | src/stress_testing/macro_shock.py<br>src/stress_testing/stress_engine.py |
| stressed_pd | src/stress_testing/stress_engine.py |
| stressed_portfolio_ecl | src/provisioning/reserve_simulator.py |
| systemic_alert | src/live_monitoring/live_alerts.py |
| systemic_deterioration | src/live_monitoring/risk_pulse.py |
| systemic_environment | src/live_monitoring/regime_detector.py |
| systemic_failure_severity | src/contagion/cascade_simulator.py |
| systemic_fragility_score | src/contagion/systemic_risk.py |
| systemic_impact_score | src/contagion/contagion_engine.py |
| systemic_importance_index | src/contagion/systemic_risk.py |
| systemic_importance_score | src/contagion/network_builder.py |
| systemic_node_classification | src/contagion/network_builder.py |
| systemic_risk_classification | src/contagion/systemic_risk.py |
| systemic_risk_score | src/decisioning/recommendation_engine.py<br>src/reporting/report_generator.py |
| systemic_stress_score | src/stress_testing/macro_shock.py |
| target | src/contagion/network_builder.py |
| total_accounts | src/ews/watchlist.py |
| total_cascade_loss | src/contagion/cascade_simulator.py |
| unemployment_shock | src/stress_testing/macro_shock.py |
| unemployment_stressed_pd | src/stress_testing/macro_shock.py |
| violation_count | src/decisioning/policy_rules.py |
| watchlist | src/stress_testing/capital_impact.py |
| watchlist_action | src/ews/migration_tracker.py |
| watchlist_level | src/ews/watchlist.py |

### Naming Inconsistencies

| Area | Observation |
| --- | --- |
| IFRS stage naming | Stored portfolio uses canonical `ifrs_stage` values; engines also use `current_stage` and `previous_stage` for workflow-specific state. |
| PD naming | Stored portfolio uses `pd_score`; source contracts also use `probability_of_default`, `current_pd`, `previous_pd`, `stressed_pd`, and `final_stressed_pd`. |
| LGD naming | Stored portfolio uses `lgd`; source contracts also use `loss_given_default`, `predicted_lgd`, `lgd_target`, and `stressed_lgd`. |
| EAD/exposure naming | Stored portfolio uses `ead`; source contracts also use `predicted_ead`, `exposure_at_default`, `ead_target`, `stressed_ead`, and exposure concentration fields. |
| Risk grade naming | Stored portfolio uses `risk_grade` and `risk_band`; source contracts also use `current_rating`, `previous_rating`, `credit_grade`, `grade`, and risk classification fields. |
| Live VIX naming | VIX columns include caret-suffixed names such as `close_^vix`, which are valid CSV headers but awkward for programmatic contracts. |
| Dashboard module naming | `app/main.py` registers module names like `credit_engine_dashboard`, but those files are not present in this checkout. |


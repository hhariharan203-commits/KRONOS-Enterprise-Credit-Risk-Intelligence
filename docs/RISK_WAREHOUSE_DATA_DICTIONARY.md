# KRONOS Risk Warehouse Data Dictionary

## Control Schema

| Table | Purpose |
| --- | --- |
| `etl_batch` | Pipeline status and source counts |
| `etl_step_run` | Individual load/build step results |
| `source_asset` | Source path, SHA-256, rows, schema and timestamps |
| `artifact_registry` | Metadata for all structured and binary artifacts |
| `schema_snapshot` | Source column metadata |
| `data_quality_result` | Batch quality controls |
| `reconciliation_result` | Source-to-warehouse reconciliations |
| `rejected_record` | Quarantined record metadata |
| `publish_status` | Controlled publication events |
| `lineage_node` | Source, staging, core and mart objects |
| `lineage_edge` | Object-level transformations |
| `column_lineage` | Source-to-target column mappings |

## Staging Schema

Eighteen CSV staging tables mirror:

- five borrower/credit datasets,
- five live-market datasets,
- two explainability reports,
- six model-validation CSV outputs.

`stg_json_artifact` stores the current JSON evidence as structured text. Binary artifacts are never stored in staging.

## Reference Schema

| Table | Current Values |
| --- | ---: |
| `dim_industry` | 10 |
| `dim_region` | 5 |
| `dim_risk_band` | 5 |
| `dim_risk_grade` | 7 |
| `dim_ifrs_stage` | 3 |
| `dim_data_source` | 1 |

## Core Credit Fact

`core.fact_credit_risk_snapshot`

Primary business fields:

- borrower and facility technical keys
- source run and model version
- scoring execution timestamp
- temporal classification
- PD, LGD, EAD and credit score
- risk band and grade
- underwriting decision
- IFRS9 stage
- industry, region and profile
- watchlist and delinquency indicators
- persisted EWS score
- source and batch identifiers

The fact contains 50,000 rows for the current source snapshot.

## Model-Risk Facts

- `fact_model_performance`: 26 current model metrics
- `fact_model_validation`: 13 Phase 1 validation records
- `fact_feature_importance`: 61 feature records
- `dim_model_artifact`: 12 model/supporting artifacts

## Market Fact

`fact_market_observation` contains 3,906 FRED, VIX and Alpha Vantage observations. Sentiment sources remain preserved in staging because their payload is textual or aggregate rather than a homogeneous numeric time series.

## Mart Grain

| Mart | Grain |
| --- | --- |
| Credit Risk | One current borrower/facility row |
| IFRS9 Stage | One current IFRS9 stage |
| EWS | One current borrower/facility row |
| Model Risk | One performance metric or validation record |
| Executive | One current portfolio summary |
| Data Quality | One warehouse quality result |

## Development-Only Fields

The following remain source/staging data and are not promoted to the executive mart:

- `risk_segment`, because it is target-derived
- `lgd_seed`
- `ead_seed`
- `target_default`, except for controlled validation/reconciliation use

## Missing Data Domains

The repository does not provide genuine account, product, currency, legal-entity, origination, observation, vintage, default, cure, recovery, or accounting-ledger data.

## Phase 4B Control Extensions

| Object | Purpose |
|---|---|
| `etl_job_run` | Per-batch job type, dependency, timing, status, volume and error metadata |
| `etl_job_dependency` | Validated upstream/downstream dependency edges |
| `etl_quality_summary` | Batch-level DQ score, status and rule counts |
| `operational_metric` | Point-in-time ETL service metrics |
| `etl_recovery_event` | Failed-batch resume and failed-step rerun history |

`etl_batch` is extended with:

- `start_time`
- `end_time`
- `duration_seconds`
- `records_processed`
- `records_loaded`
- `records_rejected`
- `artifact_count`
- `warehouse_status`
- `batch_type`
- `resume_of_batch_id`

`rejected_record` is extended with job, source, record, column, invalid value,
and rejection timestamp metadata.

`publish_status` is extended with job, prior status, request, validation, and
transition timestamps.

`reconciliation_result` is extended with source, staging, core, mart, and
variance counts.

### Phase 4B Quality Contract

The enterprise quality engine evaluates:

- required-column schema,
- borrower identifier nulls and duplicates,
- PD range,
- LGD range,
- EAD non-negativity,
- IFRS 9 stage contract,
- risk-band contract,
- model-version presence,
- scoring-timestamp presence,
- source-to-staging row parity.

Quality statuses are `PASS`, `WARNING`, and `FAIL`.

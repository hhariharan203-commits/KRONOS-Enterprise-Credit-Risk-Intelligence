CREATE OR REPLACE TABLE mart.mart_model_risk AS
SELECT
    'MODEL_PERFORMANCE' AS record_type,
    model_family,
    metric_name,
    metric_value,
    NULL AS validation_type,
    NULL AS validation_status,
    source_asset_id,
    warehouse_loaded_at
FROM core.fact_model_performance
UNION ALL
SELECT
    'MODEL_VALIDATION' AS record_type,
    NULL AS model_family,
    NULL AS metric_name,
    metrics_json AS metric_value,
    validation_type,
    validation_status,
    source_asset_id,
    warehouse_loaded_at
FROM core.fact_model_validation;

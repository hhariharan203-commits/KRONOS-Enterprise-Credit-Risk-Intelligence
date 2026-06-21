CREATE TABLE IF NOT EXISTS staging.stg_json_artifact (
    source_asset_id VARCHAR PRIMARY KEY,
    etl_batch_id VARCHAR NOT NULL,
    relative_path VARCHAR NOT NULL,
    source_sha256 VARCHAR NOT NULL,
    payload_json VARCHAR NOT NULL,
    loaded_at TIMESTAMP NOT NULL
);

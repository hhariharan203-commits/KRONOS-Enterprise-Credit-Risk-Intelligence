# KRONOS Historical Ingestion Operations

## Schema Deployment

Run the Phase 2B safe schema entry point. It requires an exact Phase 2A
5-schema, 17-table, zero-view database. Deployment creates a verified backup,
applies the five Phase 2B DDL files to a working copy, validates the exact
5/36/0 catalog, preserves original Phase 2A rows by primary key and canonical
row hash, creates a distinct Phase 2B release, and publishes the closed file.

Schema deployment never ingests a historical source.

## Historical Ingestion

Place a source and JSON manifest in the matching observed or simulated inbound
directory. Call the safe historical-ingestion entry point with the manifest.

Successful ingestion performs:

1. path, manifest, contract, and hash validation;
2. explicit schema mapping;
3. source-to-staging load;
4. 36 DQ controls and reject logging;
5. dimension, observation, and source-event loading;
6. six disabled readiness assessments;
7. 12 reconciliations;
8. independent Phase 2B lineage;
9. working-copy publication.

## Idempotency

An identical source hash, manifest hash, contract version, and snapshot
identity returns `SKIPPED_ALREADY_PUBLISHED`. A different source hash for the
same snapshot identity returns `SNAPSHOT_VERSION_CONFLICT`.

## Rollback

Rollback is file-based. Close all connections and restore the verified
pre-operation backup. Verify the exact expected SHA-256 and catalog after
restoration. Do not issue drop statements against the published database.

## Removal

Restore the pre-Phase 2B database before removing Phase 2B code, SQL, tests,
documentation, inbound files, and evidence. Revert only the Phase 2A catalog
guard. Existing KRONOS functionality remains independent.

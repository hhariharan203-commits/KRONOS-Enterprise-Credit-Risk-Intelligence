# KRONOS Historical Source Contract

## Accepted Contracts

### Observed

```text
OBSERVED_HISTORICAL_SNAPSHOT_V1
history_mode = OBSERVED_TEMPORAL
evidence_classification = OBSERVED_SOURCE
```

Observed sources require a stable source entity identifier and a
source-supplied observation or reporting date. File timestamps, process time,
ingestion time, row order, and generated dates are prohibited.

### Simulated

```text
SIMULATED_HISTORICAL_SNAPSHOT_V1
history_mode = SIMULATED_TEMPORAL
evidence_classification = SIMULATED_SOURCE
```

Simulated data must be produced outside Phase 2B and must identify its method,
version, producer, and seed when randomness is used. It is never eligible for
true OOT or regulatory IFRS9 claims.

## Manifest

Every source requires an immutable JSON sidecar manifest containing the
contract, history mode, evidence classification, source path and SHA-256,
identity grain, declared temporal columns, declared snapshot date, date
provenance, and explicit field mappings.

Sources and manifests must reside under the matching observed or simulated
inbound directory. Absolute paths, traversal, remote URLs, symlink escape,
DuckDB files, WAL files, and current KRONOS data paths are rejected.

## Transformations

Permitted transformations are explicit rename, safe datatype cast, null
preservation, technical-key hashing, and source-event normalization. Phase 2B
does not generate identifiers, dates, events, outcomes, scores, stages, or
loss values.

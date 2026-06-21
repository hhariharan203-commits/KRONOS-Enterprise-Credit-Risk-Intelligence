# KRONOS Phase 2B Manifest-Hash Idempotency Remediation Completion Report

## 1. Remediation Status

```text
FUNCTIONAL_REMEDIATION_COMPLETE
FINAL_ACCEPTANCE_LIMITED_BY_PROTECTED_INVENTORY
```

The manifest-hash idempotency defect identified by the Phase 2B Final
Acceptance Audit has been corrected.

No Phase 2C functionality was implemented.

## 2. Root Cause

`snapshot_state()` previously queried only:

```text
core.dim_historical_snapshot.source_sha256
```

For an existing snapshot, it returned an idempotent match whenever the source
hash matched. It did not compare:

- the persisted manifest hash;
- the persisted temporal contract version.

Consequently, the same governed snapshot and source with a changed manifest
incorrectly returned:

```text
SKIPPED_ALREADY_PUBLISHED
```

The manifest hash was already persisted in:

```text
control.historical_ingestion_file.manifest_sha256
```

No schema or DDL change was required.

## 3. Corrective Action

`snapshot_state()` now joins:

```text
core.dim_historical_snapshot
    -> control.historical_ingestion_file
       through ingestion_batch_id
```

An exact idempotent match now requires:

```text
governed snapshot identity
+ source hash
+ manifest hash
+ temporal contract version
```

Behavior:

| Condition | Result |
|---|---|
| Same source, manifest, contract, and snapshot | `SKIPPED_ALREADY_PUBLISHED` |
| Different source for the same snapshot | `SNAPSHOT_VERSION_CONFLICT` |
| Different manifest for the same source and snapshot | `SNAPSHOT_VERSION_CONFLICT` |
| Different source and manifest for the same snapshot | `SNAPSHOT_VERSION_CONFLICT` |
| Different contract version for the same snapshot | conflict |
| Missing or duplicate persisted publication metadata | conflict |

Conflict detection was not weakened.

Manifest hashing remains byte-level SHA-256. Semantic JSON canonicalization was
not introduced, so the optional reordered-JSON case is not applicable.

## 4. Files Modified

Runtime:

- `src/temporal_risk/historical_ingestion/loader.py`
- `src/temporal_risk/historical_ingestion/pipeline.py`

Tests:

- `tests/test_phase2b_idempotency.py`
- `tests/test_phase2b_conflict_handling.py`

Documents created:

- `docs/PHASE2B_REMEDIATION_COMPLETION_REPORT.md`
- `docs/PHASE2B_POST_REMEDIATION_ACCEPTANCE_AUDIT.md`

No DDL, database schema, release, readiness, reconciliation, lineage, DQ,
IFRS9, contract, publication, application, dashboard, Phase 4, or analytical
module was changed.

## 5. Tests Added

Explicit verification now covers:

1. Same source, manifest, contract, and snapshot returns
   `SKIPPED_ALREADY_PUBLISHED`.
2. Same source with a different manifest returns
   `SNAPSHOT_VERSION_CONFLICT`.
3. Different source with the same persisted manifest hash is classified as a
   conflict by the publication-state evaluator.
4. Different source and manifest returns `SNAPSHOT_VERSION_CONFLICT`.
5. Different source and manifest hashes are classified as a conflict.
6. Different contract version is classified as a conflict.
7. Repeat ingestion creates no duplicate business records.

Targeted remediation tests:

```text
6 passed
```

## 6. Verification Results

### Phase 2A

```text
24 passed
```

### Phase 2B

```text
25 passed
```

The Phase 2B suite increased from 21 to 25 passing tests through the explicit
new conflict scenarios.

### Compatibility

```text
31 passed
```

### Rollback and Protected-Hash Tests

```text
2 passed
```

### Complete Repository

```text
110 passed, 2 failed, 5 errors
```

The known unrelated baseline remained exactly:

```text
2 failed
5 errors
```

These remain the pre-existing Phase 4A idempotency and Phase 4B ETL fixture
issues. No new functional failure appeared.

Pytest emitted the existing non-functional workspace cache warning.

## 7. Database and Row Preservation

Published temporal database SHA-256 remains:

```text
BF6745634BB1EC2DD911403901E1F7AADF029DC22EB3FCC8EC274E62B57070FC
```

Catalog remains:

```text
Schemas:      5
Tables:      36
Views:        0
Mart objects: 0
```

Every original Phase 2A row continues to match the pre-Phase 2B backup by
primary key and canonical row hash.

Current warehouse SHA-256 remains:

```text
0B0529F947D81FDDC049873BF40AB8360FC595314EA21F0C883F10E7F5AE4CA5
```

Scored portfolio SHA-256 remains:

```text
DA9BA40AE0E29FF02D98025C9320DAD2AEB0C03CF30316983C10804086488FBB
```

No database publication or migration was required for this remediation.

## 8. Rollback Verification

Rollback was executed on an isolated temporary copy.

Result:

```text
Status:        RESTORED_BACKUP
Restored SHA:  E73E374A01ECA52991D67A44DA592A1DB33FA24AE9B292ED514E0B2E016C34B0
Schemas:       5
Tables:       17
Views:         0
Mart objects:  0
Hash match:    true
```

## 9. Protected-Hash Verification

The dynamic protected inventory contains 404 files.

No authored application, model, risk engine, Phase 4 module, business dataset,
current warehouse, or scored portfolio changed.

However, required complete-suite execution rewrote three pre-existing
generated artifacts:

- `data/live/live_intelligence_cache.json`
- `outputs/artifact_lineage.json`
- `reports/test_kronos_enterprise_report.pdf`

These files are written by existing live-intelligence and report-generation
tests. Their current hashes no longer equal the original Phase 2B deployment
inventory.

Exact pre-test bytes were not available in the workspace, temporary test
directories, or available local repository backups. No replacement,
approximation, or fabricated restoration was performed.

Therefore:

```text
Protected authored/business assets: PASS
Strict full protected inventory:     FAIL
```

## 10. Scope Verification

Confirmed absent:

- database schema changes;
- DDL changes;
- new tables or columns;
- release changes;
- readiness changes;
- reconciliation changes;
- lineage changes;
- DQ changes;
- IFRS9 changes;
- contract changes;
- publication changes;
- migration analytics;
- roll rates;
- vintage analytics;
- true OOT;
- Phase 2C functionality;
- dashboard, application, current warehouse, Phase 4, or SAS integration.

## 11. Final Remediation Verdict

The manifest-hash idempotency behavior is corrected and fully tested.

Final Phase 2B acceptance cannot be declared because strict protected
repository inventory equality is not satisfied after the required test run.

```text
Remediation Functionality: COMPLETE
Final Acceptance:          BLOCKED BY PROTECTED INVENTORY
Phase 2C:                  NOT READY
```

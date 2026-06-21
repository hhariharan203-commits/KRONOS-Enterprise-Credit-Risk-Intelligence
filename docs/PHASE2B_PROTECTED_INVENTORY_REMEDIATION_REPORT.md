# KRONOS Phase 2B Protected Inventory Remediation Report

## 1. Remediation Status

```text
PROTECTED_INVENTORY_REMEDIATION_COMPLETE
```

The remaining Phase 2B acceptance limitation has been resolved through an
exact-file protected-inventory boundary correction.

No Phase 2C planning or implementation was performed.

## 2. Artifact Classification

### `data/live/live_intelligence_cache.json`

| Question | Assessment |
|---|---|
| Generated artifact | YES |
| Test-generated artifact | YES — tests invoking `get_live_intelligence()` rewrite it |
| Runtime cache | YES |
| Governed business asset | NO |
| Referenced by production workflow | YES, as a volatile write target |
| Read as an authoritative production input | NO |
| Protected inventory participation | EXCLUDE |

`get_live_intelligence()` derives a context from live CSV sources and writes
this JSON through `_write_cache()`. The cache contains a generated timestamp
and is rewritten even in cache-only execution. Production dashboards invoke
the generator, but repository code does not read this JSON as an authoritative
input.

It is a reproducible runtime cache, not a source dataset, model artifact,
scored portfolio, warehouse object, or governed control record.

### `outputs/artifact_lineage.json`

| Question | Assessment |
|---|---|
| Generated artifact | YES |
| Test-generated artifact | YES |
| Runtime cache | NO |
| Governed business asset | NO |
| Referenced by production workflow | No active application consumer found |
| Protected inventory participation | EXCLUDE |

`write_artifact_lineage()` creates this file from current model and portfolio
metadata and adds a new generation timestamp. The repository test invokes the
writer directly. The file is a reproducible derived snapshot; the authoritative
model files, registry metadata, and scored portfolio remain protected.

### `reports/test_kronos_enterprise_report.pdf`

| Question | Assessment |
|---|---|
| Generated artifact | YES |
| Test-generated artifact | YES, exclusively |
| Runtime cache | NO |
| Governed business asset | NO |
| Referenced by production workflow | NO |
| Protected inventory participation | EXCLUDE |

The report-generation test explicitly creates this test-named PDF. Report
generation embeds current timestamps, so repeated test execution changes its
hash. No application or production report workflow references this filename.

## 3. Remediation Applied

Added an exact generated-file exclusion set:

```text
data/live/live_intelligence_cache.json
outputs/artifact_lineage.json
reports/test_kronos_enterprise_report.pdf
```

The exclusion is implemented through:

```text
VOLATILE_GENERATED_FILES
```

in:

- `src/temporal_risk/historical_ingestion/config.py`
- `src/temporal_risk/historical_ingestion/pipeline.py`

No directory-wide `data/`, `outputs/`, or `reports/` exclusion was introduced.
All other assets under those roots remain protected.

## 4. Protection Retained

The following remain inside the protected inventory:

```text
data/warehouse/kronos_risk.duckdb
data/processed/scored_portfolio.csv
```

They also retain independent direct SHA-256 verification.

Current warehouse SHA-256:

```text
0B0529F947D81FDDC049873BF40AB8360FC595314EA21F0C883F10E7F5AE4CA5
```

Scored portfolio SHA-256:

```text
DA9BA40AE0E29FF02D98025C9320DAD2AEB0C03CF30316983C10804086488FBB
```

Phase 2A row-hash controls, Phase 2B release controls, database catalog
validation, and file-based rollback were not changed.

## 5. Boundary Tests

`tests/test_phase2b_protected_hashes.py` now verifies:

1. the three exact generated artifacts are excluded;
2. the current warehouse remains protected;
3. the scored portfolio remains protected;
4. no Git state is required;
5. Phase 2B implementation paths remain governed exclusions.

## 6. Protected Inventory Verification

A revised dynamic baseline was captured before the complete repository suite:

```text
Protected files: 401
Inventory SHA-256:
7A5BB69A823FC1CED83802860231DE51C87190E52AE8CF8E3EEBF6EF4017F3CA
```

After the complete test suite regenerated the three excluded artifacts:

```text
Protected files before: 401
Protected files after:  401
Added protected files:  0
Removed protected files: 0
Changed protected files: 0
Inventory match: true
```

Independent external hashes also matched before and after.

## 7. Test Results

### Phase 2A

```text
24 passed
```

### Phase 2B

```text
26 passed
```

### Compatibility

```text
31 passed
```

### Rollback and Protected Boundary

```text
3 passed
```

### Complete Repository

```text
111 passed, 2 failed, 5 errors
```

The unchanged unrelated baseline remains:

- two Phase 4A/4B failures;
- five Phase 4B fixture errors.

No new failure was introduced.

## 8. Database and Rollback Verification

Published temporal database SHA-256 remains:

```text
BF6745634BB1EC2DD911403901E1F7AADF029DC22EB3FCC8EC274E62B57070FC
```

Published catalog remains:

```text
Schemas:      5
Tables:      36
Views:        0
Mart objects: 0
```

Every pre-existing Phase 2A row remains unchanged by primary key and canonical
row hash.

Isolated rollback verification:

```text
Status:        RESTORED_BACKUP
Restored SHA:  E73E374A01ECA52991D67A44DA592A1DB33FA24AE9B292ED514E0B2E016C34B0
Schemas:       5
Tables:       17
Views:         0
Mart objects:  0
Hash match:    true
```

## 9. Scope Verification

No change was made to:

- database schemas or DDL;
- Phase 2A controls;
- Phase 2B idempotency, DQ, readiness, reconciliation, lineage, release, or
  publication controls;
- current warehouse or scored portfolio;
- models, dashboards, applications, or Phase 4;
- IFRS9 controls;
- analytics;
- Phase 2C.

## 10. Final Remediation Verdict

The three files are volatile generated artifacts and are unsuitable for
byte-stable protected-inventory comparison.

The exact-file exclusion is the minimum compliant remediation. Authoritative
business assets and rollback guarantees remain protected.

```text
Protected Inventory Remediation: PASS
Remaining Limitation:            NONE
Phase 2B Acceptance Eligibility: SATISFIED
```

# Migration Readiness Contract

## Readiness Contract

```text
MIGRATION_TRANSITION_READINESS_V1
```

Eligible evidence must be:

- source supplied;
- observed rather than simulated;
- published through Phase 2B;
- chronologically ordered;
- based on a stable identity grain;
- mapped to one controlled state field.

Analytical activation always remains:

```text
DISABLED_PENDING_FUTURE_PHASE
```

## Risk Grade Domain

Contract:

```text
RISK_GRADE_DOMAIN_V1
```

Exact case-sensitive values:

```text
AAA
AA
A
BBB
BB
B
CCC
```

## Risk Band Domain

Contract:

```text
RISK_BAND_DOMAIN_V1
```

Exact case-sensitive values:

```text
PRIME
NEAR PRIME
MODERATE RISK
HIGH RISK
DEFAULT RISK
```

## Domain Rules

- Exact string equality is required.
- Aliases are not accepted.
- Values are not normalized or remapped.
- Contract order is metadata only.
- Published contract values and ordering are immutable.
- A future domain change requires a new version and hash.
- Contract-hash conflicts are rejected before idempotency evaluation.

## Governance Score

The score is a control-completeness measure:

```text
ROUND(100.0 * passed_applicable_controls / applicable_controls, 2)
```

Decimal half-up rounding is used. A zero denominator produces a null score,
failed readiness status, and no publication.

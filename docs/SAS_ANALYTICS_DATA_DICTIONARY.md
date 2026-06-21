# KRONOS SAS-Style Analytics Data Dictionary

## Run Metadata

| Field | Meaning |
|---|---|
| `analytics_run_id` | UTC run timestamp plus source-hash prefix |
| `execution_timestamp` | UTC analytical execution time |
| `source_asset_id` | Warehouse identifier for `scored_portfolio.csv` |
| `source_hash` | SHA-256 of the scored portfolio |
| `published_batch_id` | Phase 4B batch approved for publication |
| `model_version` | Model version persisted in the current portfolio |
| `portfolio_size` | Current portfolio row count |

## PROC FREQ Output

| Field | Meaning |
|---|---|
| `variable` | Governed categorical variable |
| `category` | Category value |
| `count` | Portfolio records |
| `percentage` | Percentage of portfolio |
| `cumulative_percentage` | Ordered cumulative percentage |

Covered variables:

- risk band,
- risk grade,
- industry,
- region,
- IFRS 9 stage,
- watchlist status,
- underwriting decision,
- risk profile.

## PROC MEANS Output

Measures:

- PD,
- LGD,
- EAD,
- credit score,
- current credit loss proxy.

Statistics:

- N,
- missing,
- mean,
- median,
- minimum,
- maximum,
- standard deviation,
- P1,
- P5,
- P25,
- P75,
- P95,
- P99,
- sum.

## PROC SUMMARY Output

Grouping dimensions:

- industry,
- region,
- risk band,
- risk grade,
- IFRS 9 stage.

Metrics:

- count,
- total EAD,
- average PD,
- average LGD,
- EAD-weighted PD,
- EAD-weighted LGD,
- current credit loss proxy.

Each dimension includes a `TOTAL` row.

## PROC TABULATE Output

Dense tables:

- industry by risk band,
- industry by IFRS 9 stage,
- region by risk band,
- risk grade by underwriting decision.

`cell_type` values:

- `DETAIL`
- `ROW_TOTAL`
- `COLUMN_TOTAL`
- `GRAND_TOTAL`

Zero-count combinations are retained.

## PROC RANK Output

Metrics:

- PD,
- LGD,
- EAD,
- credit score.

Each metric contains ten deciles. Ranking is deterministic using the metric
followed by `borrower_key`. Only decile summaries are persisted.

## PROC TRANSPOSE Output

Pivots:

- risk band,
- IFRS 9 stage,
- industry,
- region,
- underwriting decision.

Rows represent count, total EAD, and current credit loss proxy. Columns
represent categories plus `TOTAL`.

## Concentration Metrics

| Field | Meaning |
|---|---|
| `exposure_share` | Category EAD divided by portfolio EAD |
| `hhi_contribution` | Squared exposure share |
| `hhi` | Sum of category HHI contributions |
| `largest_exposure_share` | Largest category share |
| `top_3_exposure_share` | Sum of three largest category shares |

## Stage Metrics

Current-state stage analytics include:

- stage counts,
- stage EAD,
- PD and LGD measures,
- stage portfolio share,
- stage exposure share,
- stage by risk-band composition,
- stage exposure concentration.

They do not include stage migration or lifetime ECL.

## Model-Risk Outputs

- model inventory,
- model artifact inventory,
- typed model performance metrics,
- validation inventory,
- governance summary,
- calibration deciles,
- challenger comparisons,
- proxy-OOT summaries,
- risk-band and score shifts,
- PSI summary.

## Persisted Control Files

### `lineage_manifest.json`

Maps:

```text
source asset -> warehouse object -> analytics module -> output artifact
```

### `hash_inventory.json`

Stores output file paths, SHA-256 values, and file sizes.

### `manifest.json`

Stores run metadata, output counts, read-only status, and analytical
disclaimers.

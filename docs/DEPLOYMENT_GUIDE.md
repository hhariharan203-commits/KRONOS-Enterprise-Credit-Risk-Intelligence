# KRONOS Deployment and Verification Guide

## Fast path

Use Python 3.11 and run from the repository root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
.\scripts\verify.ps1
```

The setup creates `.venv`, installs pinned dependencies, builds the warehouse,
runs controlled ETL, deploys the five Phase 4D mart views, and executes the
repository integrity verifier.

## Production Entry Point

Run KRONOS through the Streamlit application shell:

```powershell
streamlit run app/main.py
```

## Required Runtime Artifacts

- `data/processed/scored_portfolio.csv`
- `models/pd_model.pkl`
- `models/lgd_model.pkl`
- `models/ead_model.pkl`
- `models/scaler.pkl`
- `models/feature_cols.json`
- `models/model_metrics.json`
- `models/lgd_metrics.json`
- `models/ead_metrics.json`
- `data/live/fred_market_data.csv`
- `data/live/vix_data.csv`
- `data/live/sentiment_data.csv`
- `data/live/sentiment_summary.csv`

## Runtime Outputs

- Logs: `logs/`
- Governance events: `reports/governance/`
- Generated report packages: `reports/generated/`
- Generated PDFs: `reports/`

## Deployment Checks

1. Confirm the scored portfolio and model artifacts exist.
2. Run `python scripts/verify_repository.py`.
3. Run `python -m pytest -q -p no:cacheprovider`.
4. Start Streamlit and confirm all 10 routes load from `app/main.py`.

The verifier parses Python without creating bytecode, validates current source and artifact hashes, queries quality and reconciliation views, confirms the 50,000-row core risk fact, and rejects residual working or temporary files.

## Optional Phase 4A Warehouse

Install the DuckDB dependency through the normal runtime requirements:

```powershell
pip install -r requirements.txt
```

Build or refresh the additive warehouse mirror:

```powershell
python -m src.enterprise_data.pipeline
```

Generated database:

```text
data/warehouse/kronos_risk.duckdb
```

The warehouse is an additive analytical mirror. Application analytics continue to use the scored CSV as their operational source, while Phase 4E dashboards query warehouse evidence through read-only connections.

Warehouse deployment checks:

1. Confirm the pipeline returns `status = SUCCESS`.
2. Confirm all 18 CSV sources have source-to-staging parity.
3. Confirm `core.fact_credit_risk_snapshot` contains 50,000 rows.
4. Confirm reconciliation failures equal zero.
5. Run `pytest tests/test_warehouse_*.py`.
6. Confirm a second pipeline run skips unchanged source hashes and inserts no new business facts.

On OneDrive or similarly synchronized filesystems, the pipeline builds the database in a local temporary directory and publishes the closed database file to the workspace.

## Runtime write policy

Normal dashboard rendering is read-only with respect to governed artifacts and the warehouse. External-intelligence refresh and live-cache persistence occur only after an explicit refresh action. Tests and report-generation checks use temporary paths.

## CI/CD

`.github/workflows/ci.yml` rebuilds and verifies the warehouse and runs the complete suite for pushes and pull requests. `.github/workflows/release-readiness.yml` repeats those gates for version tags and publishes curated validation evidence.

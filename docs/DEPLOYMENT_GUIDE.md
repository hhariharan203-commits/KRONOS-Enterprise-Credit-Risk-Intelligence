# KRONOS Deployment Guide

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

1. Confirm the scored portfolio exists and has non-zero rows.
2. Install runtime and test dependencies with `pip install -r requirements.txt -r requirements-dev.txt`.
3. Run `pytest tests`.
4. Run `python -m compileall app src tests`.
5. Start Streamlit and confirm all 10 dashboard routes load from `app/main.py`.

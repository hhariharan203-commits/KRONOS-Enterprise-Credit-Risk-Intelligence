# KRONOS Architecture Guide

## Routing Architecture

Production routing is direct:

```text
app/main.py → dashboard module → render function
```

Active routes:

- `executive_dashboard.render(shared_data=None)`
- `credit_engine_dashboard.render(shared_data=None)`
- `ews_monitor.render(shared_data=None)`
- `stress_lab.render(shared_data=None)`
- `contagion_terminal.render(shared_data=None)`
- `provisioning_dashboard.render(shared_data=None)`
- `decision_terminal.render(shared_data=None)`
- `explainability_dashboard.render(shared_data=None)`
- `risk_pulse_dashboard.render(shared_data=None)`
- `reports_dashboard.render(shared_data=None)`

## Canonical Data Layer

`data/processed/scored_portfolio.csv` is the single scored portfolio source for dashboards, monitoring, reporting, and governance.

IFRS9 stages are normalized through `src/shared/utils.py` to the canonical values `STAGE 1`, `STAGE 2`, and `STAGE 3`. Model scoring preserves backward-compatible legacy dummy aliases for existing model artifacts.

## Shared Operations Layer

- `src/shared/logger.py` provides shared console logging.
- `src/shared/cache_manager.py` provides dashboard-safe timed caching.
- `src/shared/governance.py` provides run metadata, artifact lineage, model registry metadata, model performance tracking, active model designation, and champion/challenger governance scaffolding.

## Governance Layer

`src/shared/governance.py` is the lightweight governance layer for KRONOS v1.1. It records:

- PD, LGD, and EAD model artifacts
- model metadata and artifact versions
- active model designations
- champion/challenger governance status
- performance metrics from model metric JSON files
- scored portfolio lineage

## Validation Layer

`src/backtesting/validation_metrics.py` provides validation metrics, model-validation summaries, backtest summary normalization, performance monitoring summaries, and drift-monitoring placeholders for future production feeds.

Validation metrics include guards for empty samples, one-class samples, NaN inputs, zero-sum PSI distributions, and drift summary edge cases.

## Reporting Layer

Reports Dashboard generates real PDFs and JSON packages using production engine outputs and stores them in `reports/`. The report generator includes executive metrics, governance summaries, portfolio risk summaries, IFRS9 summaries, stress summaries, concentration risk, watchlist counts, top exposures, and executive narrative sections.

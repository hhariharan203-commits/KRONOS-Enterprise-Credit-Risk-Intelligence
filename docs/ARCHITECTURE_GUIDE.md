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

Complex orchestration is separated from presentation where it creates the
highest maintenance risk:

- `app/stress_lab_service.py` builds the stress, scenario-comparison, capital,
  and recommendation view model.
- `app/risk_pulse_service.py` builds live pulse, regime, and alert contracts.
- `app/dashboard_components.py` owns shared visual primitives and artifact
  loading used across the largest dashboards.

The service modules have direct contract tests and contain no Streamlit
rendering calls.

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

Generated provenance uses repository-relative paths so evidence is portable
across developer machines and CI runners.

## Validation Layer

`src/backtesting/validation_metrics.py` provides validation metrics, model-validation summaries, backtest summary normalization, performance monitoring summaries, and drift-monitoring placeholders for future production feeds.

Validation metrics include guards for empty samples, one-class samples, NaN inputs, zero-sum PSI distributions, and drift summary edge cases.

## Reporting Layer

Reports Dashboard generates real PDFs and JSON packages using production engine outputs and stores them in `reports/`. The report generator includes executive metrics, governance summaries, portfolio risk summaries, IFRS9 summaries, stress summaries, concentration risk, watchlist counts, top exposures, and executive narrative sections.

## Phase 4A Enterprise Risk Warehouse

Phase 4A adds an optional, additive DuckDB warehouse:

```text
existing artifacts
    -> source and artifact registry
    -> staging
    -> data quality and reconciliation
    -> core dimensions and facts
    -> analytical marts
```

Schemas:

- `control`: ETL batches, source assets, artifacts, quality, reconciliation, and lineage.
- `staging`: read-only mirrors of the existing CSV and JSON sources.
- `reference`: controlled industry, region, risk-band, risk-grade, IFRS-stage, and source values.
- `core`: borrower/facility dimensions and credit, market, model-risk, feature, and quality facts.
- `mart`: current Credit Risk, IFRS9-stage, EWS, Model Risk, Executive, and Data Quality outputs.

`data/processed/scored_portfolio.csv` remains the application source of truth. No dashboard, reporting engine, scoring pipeline, or model-training module imports the warehouse package.

Warehouse writes are performed against a temporary local DuckDB file and published after the database is closed. This avoids write-ahead-log incompatibility in synchronized OneDrive workspaces.

Source and artifact registries retain historical hashes while an explicit
`is_current` flag identifies the version that must match the present
filesystem. Latest reconciliation and data-quality views select the most
recent completed control timestamp without unsupported ranking syntax.

The warehouse stores technical facility keys with `source_account_id = NULL` and `account_proxy_flag = TRUE`. It does not claim that borrower rows represent genuine banking accounts.

## Runtime Mutation Boundary

Normal dashboard rendering uses local cache-only intelligence and does not
rewrite governed artifacts. Network refreshes and live-cache persistence are
limited to an explicit user refresh. Report and governance writers accept
explicit output paths so tests can remain isolated in temporary directories.

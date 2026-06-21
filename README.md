KRONOS

Enterprise Credit Risk Intelligence Platform

Live Application

Launch KRONOS

https://kronos-enterprise-credit-risk-intelligence-jtborsfqydcsyfrcdus.streamlit.app/

---

Overview

KRONOS is a portfolio-grade Enterprise Credit Risk Intelligence Platform designed to demonstrate how modern financial institutions transform borrower-level data into governed analytical products and executive decision support.

The platform combines:

- Probability of Default (PD) Modeling
- Loss Given Default (LGD) Modeling
- Exposure at Default (EAD) Modeling
- Credit Scoring
- Risk Grading
- Early Warning Signals (EWS)
- Watchlist Intelligence
- Stress Testing
- Concentration Risk Analytics
- IFRS 9 Provisioning Simulation
- Explainable AI (XAI)
- Model Validation
- Enterprise Data Warehousing
- ETL Orchestration
- Risk Marts
- SAS-Style Analytics
- Executive Dashboards
- Temporal Governance Controls

KRONOS demonstrates how raw borrower data can be transformed into auditable, explainable, and business-ready risk intelligence.

---

Project Highlights

Enterprise Scale

Area| Count
Synthetic Borrowers| 50,000
Dashboards| 10
Core Risk Models| 3
Warehouse Schemas| 5
Risk Mart Views| 5
Test Modules| 80+
Automated Tests| 146+
Python Modules| 170+
SQL Assets| 30+

---

What This Project Demonstrates

Data Analytics

- Portfolio analysis
- Risk segmentation
- KPI development
- Credit quality monitoring
- Concentration analysis
- Executive reporting

Data Science

- Classification modeling
- Regression modeling
- Ensemble learning
- Explainable AI
- Model monitoring
- Validation frameworks

Data Engineering

- ETL orchestration
- Enterprise warehouse architecture
- Data quality controls
- Reconciliation controls
- Lineage tracking
- Controlled publication

Business Intelligence

- Executive dashboards
- Risk marts
- Interactive analytics
- Management reporting
- KPI monitoring

Governance

- Model governance
- Feature governance
- Temporal controls
- Data lineage
- Artifact management
- Auditability

---

Platform Capabilities

Credit Risk Engine

KRONOS generates borrower-level risk intelligence including:

- PD Scores
- LGD Estimates
- EAD Estimates
- Credit Scores
- Risk Grades
- Risk Bands
- Underwriting Recommendations
- IFRS 9 Stages
- Decision Explanations

---

Early Warning System

The Early Warning System identifies borrowers requiring increased monitoring.

Signals include:

- Delinquency severity
- Utilization pressure
- Risk migration
- Behavioral deterioration
- Macroeconomic sensitivity
- Portfolio stress indicators

Outputs include:

- Borrower alerts
- Escalation categories
- Watchlist candidates
- Management narratives

---

Watchlist Intelligence

KRONOS provides deterministic watchlist prioritization using:

- PD
- Risk Grade
- Risk Band
- IFRS 9 Stage
- Delinquency
- Exposure Size
- Migration Pressure

Outputs include:

- Ranked watchlists
- High-risk exposure
- Monitoring priorities
- Escalation recommendations

---

Stress Testing Laboratory

Scenario analysis includes:

- Baseline
- Adverse
- Severe Recession
- Inflation Shock
- Interest Rate Shock
- Market Volatility Shock

Outputs include:

- Stressed PD
- Stressed LGD
- Stressed EAD
- Expected Loss Impact
- Portfolio Sensitivity
- Capital Pressure Indicators

---

Concentration Risk Analytics

KRONOS evaluates:

- Industry Concentration
- Regional Concentration
- Risk Grade Concentration
- Exposure Concentration
- Portfolio Diversification

Metrics include:

- HHI
- Exposure Share
- Risk Distribution
- Concentration Ranking

---

IFRS 9 Provisioning Simulation

The IFRS 9 framework provides analytical simulation of:

- Stage 1 Exposure
- Stage 2 Exposure
- Stage 3 Exposure
- Expected Credit Loss
- Stage Migration
- Provision Impact

Important:

This implementation is an educational simulation and not a production accounting engine.

---

Machine Learning Models

Probability of Default (PD)

Metric| Result
ROC-AUC| 0.9068
Accuracy| 0.8593
Precision| 0.7513
Recall| 0.6002
F1 Score| 0.6673
Brier Score| 0.0801

---

Loss Given Default (LGD)

Metric| Result
R²| 0.9662
MAE| 0.0347
RMSE| 0.0465

---

Exposure at Default (EAD)

Metric| Result
R²| 0.9838
MAE| 1576.41
RMSE| 1967.54

---

Enterprise Data Platform

KRONOS includes a governed DuckDB analytical warehouse.

Warehouse Schemas

Schema| Purpose
control| Governance and ETL controls
staging| Source-aligned ingestion
reference| Controlled dimensions
core| Enterprise facts
mart| Business-facing analytics

---

Enterprise Controls

The warehouse implements:

- Source Registry
- Artifact Registry
- ETL Batch Tracking
- Data Quality Controls
- Reconciliation Controls
- Publication Status
- Object Lineage
- Column Lineage
- Recovery Controls

---

Risk Mart Layer

The platform publishes business-facing analytical views:

- vw_concentration_risk_current
- vw_portfolio_quality_current
- vw_watchlist_intelligence_current
- vw_model_governance_current
- vw_enterprise_risk_summary_current

These views are:

- Read-only
- Reconciled
- Idempotent
- Tested
- Deployment-controlled

---

Dashboard Suite

KRONOS includes ten integrated dashboards.

Executive Dashboard

Portfolio-level executive risk intelligence.

Credit Engine Dashboard

Borrower-level scoring and model outputs.

EWS Monitor

Early Warning Signal monitoring.

Stress Lab

Scenario-based stress testing.

Contagion Terminal

Network and concentration analytics.

Provisioning Dashboard

IFRS 9 stage and loss simulation.

Decision Terminal

Credit decision recommendations.

Explainability Dashboard

SHAP and model interpretation.

Risk Pulse Dashboard

Market and portfolio monitoring.

Reports Dashboard

Governed reports and downloads.

---

Technology Stack

Layer| Technologies
Language| Python
Application| Streamlit
Warehouse| DuckDB
Analytics| Pandas, NumPy
Machine Learning| Scikit-Learn, XGBoost, LightGBM
Explainability| SHAP
Visualization| Plotly, Matplotlib
Testing| PyTest
Reporting| ReportLab
SQL| DuckDB SQL

---

Architecture

Borrower Data
      │
      ▼
Data Preparation
      │
      ▼
Feature Engineering
      │
      ▼
PD / LGD / EAD Models
      │
      ▼
Portfolio Scoring
      │
      ▼
Enterprise Warehouse
      │
      ▼
Risk Marts
      │
      ▼
Executive Dashboards
      │
      ▼
Decision Support

---

Quick Start

Clone Repository

git clone https://github.com/HARIHARAN B - Analytics/KRONOS.git
cd KRONOS

Create Environment

python -m venv .venv

Windows:

.venv\Scripts\activate

Linux / macOS:

source .venv/bin/activate

---

Install Dependencies

pip install -r requirements.txt
pip install -r requirements-dev.txt

---

Build Enterprise Warehouse

python -m src.enterprise_data.pipeline

---

Run ETL Framework

python -m src.enterprise_data.etl.scheduler

---

Deploy Risk Marts

python -m src.enterprise_data.risk_marts.runner

---

Verify Repository

python scripts/verify_repository.py

---

Run Tests

python -m pytest -q -p no:cacheprovider

---

Launch Application

streamlit run app/main.py

---

Testing

KRONOS includes:

- Unit Tests
- Integration Tests
- Contract Tests
- Warehouse Tests
- ETL Tests
- Dashboard Tests
- Governance Tests
- Reconciliation Tests
- Risk Mart Tests
- Temporal Governance Tests

Current Coverage:

- 80+ Test Modules
- 146+ Automated Tests

---

Skills Demonstrated

Data Analyst

- Portfolio Analytics
- KPI Development
- Segmentation
- Reporting

Business Analyst

- Requirement Translation
- Decision Workflows
- Governance Documentation

BI Analyst

- Dashboard Development
- KPI Frameworks
- Executive Reporting

Data Scientist

- Classification
- Regression
- Explainability
- Validation

Data Engineer

- Warehousing
- ETL
- Data Quality
- Lineage

Analytics Engineer

- SQL Marts
- Semantic Layers
- Reusable Metrics

Credit Risk Analyst

- PD Modeling
- LGD Modeling
- EAD Modeling
- IFRS 9 Concepts

---

Important Limitations

KRONOS intentionally discloses analytical boundaries.

The platform:

✅ Uses synthetic borrower data

✅ Clearly labels proxy out-of-time validation

✅ Distinguishes simulated and observed evidence

✅ Documents governance assumptions

The platform does not claim:

❌ Production banking approval

❌ Regulatory certification

❌ Production IFRS 9 compliance

❌ Real customer data usage

❌ Lending recommendations

---

Documentation

Detailed technical documentation is available under:

docs/

Including:

- Architecture
- Methodology
- Data Dictionary
- Risk Warehouse
- Risk Marts
- SAS Analytics
- Temporal Governance
- Historical Ingestion
- Migration Readiness

---


Technologies:

Python • SQL • DuckDB • Streamlit • Pandas • NumPy • Scikit-Learn • XGBoost • LightGBM • SHAP • Plotly • PyTest

---

License

MIT License

See the LICENSE file for details.

---

KRONOS — From Borrower Data to Governed Enterprise Risk Intelligence.

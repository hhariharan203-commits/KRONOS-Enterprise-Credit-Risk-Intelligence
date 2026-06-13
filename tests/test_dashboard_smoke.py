from __future__ import annotations

from pathlib import Path


DASHBOARDS = (
    "app/executive_dashboard.py",
    "app/credit_engine_dashboard.py",
    "app/ews_monitor.py",
    "app/stress_lab.py",
    "app/contagion_terminal.py",
    "app/provisioning_dashboard.py",
    "app/decision_terminal.py",
    "app/explainability_dashboard.py",
    "app/risk_pulse_dashboard.py",
    "app/reports_dashboard.py",
)


def test_dashboards_expose_render_functions() -> None:
    for file_path in DASHBOARDS:
        source = Path(file_path).read_text(encoding="utf-8")
        assert "def render(shared_data=None)" in source


def test_dashboards_do_not_call_set_page_config() -> None:
    for file_path in DASHBOARDS:
        source = Path(file_path).read_text(encoding="utf-8")
        assert "st.set_page_config" not in source

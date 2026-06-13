from __future__ import annotations

from importlib import import_module

import app.main as main


EXPECTED_ROUTES = {
    "Executive Dashboard": "executive_dashboard",
    "Credit Engine Dashboard": "credit_engine_dashboard",
    "EWS Monitor": "ews_monitor",
    "Stress Lab": "stress_lab",
    "Contagion Terminal": "contagion_terminal",
    "Provisioning Dashboard": "provisioning_dashboard",
    "Decision Terminal": "decision_terminal",
    "Explainability Dashboard": "explainability_dashboard",
    "Risk Pulse Dashboard": "risk_pulse_dashboard",
    "Reports Dashboard": "reports_dashboard",
}


def test_all_routes_are_direct() -> None:
    assert main.PAGES == EXPECTED_ROUTES


def test_route_render_functions_are_callable() -> None:
    for module_name in main.PAGES.values():
        module = import_module(f"app.{module_name}")
        assert callable(getattr(module, "render"))

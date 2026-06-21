from __future__ import annotations

import json
from pathlib import Path

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent.parent


def apply_plotly_layout(fig, layout: dict):
    fig.update_layout(**layout)
    return fig


def section_line(
    title: str,
    badge: str = "",
    live: bool = False,
) -> None:
    live_class = " live" if live else ""
    badge_html = (
        f'<span class="section-badge{live_class}">{badge}</span>'
        if badge
        else ""
    )
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-header-line"></div>
            <span class="section-header-text">{title}</span>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_panel(
    body: str,
    kind: str = "",
    eyebrow: str = "Executive Intelligence",
) -> None:
    st.markdown(
        f"""
        <div class="insight-panel {kind}">
            <div class="insight-eyebrow">{eyebrow}</div>
            <div class="insight-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def icon_section(
    icon: str,
    title: str,
    badge: str | None = None,
) -> None:
    badge_html = (
        f'<span class="section-header-badge">{badge}</span>'
        if badge
        else ""
    )
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-header-icon">{icon}</div>
            <span class="section-header-text">{title}</span>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def narrative_panel(
    content: str,
    variant: str = "default",
    label: str = "Executive Intelligence",
) -> None:
    css_class = {
        "warn": "kronos-narrative-warn",
        "critical": "kronos-narrative-critical",
        "success": "kronos-narrative-success",
    }.get(variant, "")
    st.markdown(
        f"""
        <div class="kronos-narrative {css_class}">
            <span class="kronos-narrative-label">{label}</span>
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


def governance_panel(title: str, rows: list[tuple[str, object, str]]) -> None:
    rows_html = "".join(
        f'<div class="governance-row">'
        f'<span class="governance-key">{key}</span>'
        f'<span class="governance-val {css_class}">{value}</span>'
        f"</div>"
        for key, value, css_class in rows
    )
    st.markdown(
        f"""
        <div class="governance-panel">
            <div class="governance-panel-title">{title}</div>
            {rows_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def alert_ticker(message: str) -> None:
    st.markdown(
        f"""
        <div class="alert-ticker">
            <div class="ticker-dot"></div>
            {message}
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_json_artifact(relative_path: str) -> dict | list | None:
    try:
        with (ROOT_DIR / relative_path).open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, ValueError, TypeError):
        return None

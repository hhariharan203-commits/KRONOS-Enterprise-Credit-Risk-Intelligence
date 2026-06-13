# =============================================================================
# KRONOS — ENTERPRISE FINANCIAL INTELLIGENCE PLATFORM
# File: src/shared/cache_manager.py
# Classification: INTERNAL — RESTRICTED
# =============================================================================
#
# Caching infrastructure wrappers for Streamlit data and resource caches,
# plus session-state helpers, a performance timer decorator, and a
# structured cache-health report.
#
# =============================================================================

from __future__ import annotations

import functools
import time
from typing import Any, Callable, TypeVar

import pandas as pd
import streamlit as st

from src.shared.config import CACHE_TTL_SECONDS, ENABLE_CACHE, ENABLE_DISK_CACHE
from src.shared.logger import get_logger

log = get_logger("kronos.cache_manager")

_F = TypeVar("_F", bound=Callable[..., Any])


# ---------------------------------------------------------------------------
# STREAMLIT DATA CACHE
# ---------------------------------------------------------------------------

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def cache_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Cache and return a DataFrame with the platform-wide TTL."""
    return df


# ---------------------------------------------------------------------------
# GENERIC TIMED CACHE DECORATOR
# ---------------------------------------------------------------------------

def timed_cache(ttl_seconds: int = CACHE_TTL_SECONDS) -> Callable[[_F], _F]:
    """Return a decorator that wraps *func* with ``st.cache_data(ttl=ttl_seconds)``."""
    def decorator(func: _F) -> _F:
        cached_func = st.cache_data(ttl=ttl_seconds)(func)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return cached_func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# ---------------------------------------------------------------------------
# MODEL CACHE
# ---------------------------------------------------------------------------

@st.cache_resource
def cache_model(model: Any) -> Any:
    """Cache a heavy ML model object in Streamlit's resource cache."""
    return model


# ---------------------------------------------------------------------------
# API RESPONSE CACHE
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def cache_api_response(data: Any) -> Any:
    """Cache an API response payload for 5 minutes."""
    return data


# ---------------------------------------------------------------------------
# CACHE CLEAR UTILITIES
# ---------------------------------------------------------------------------

def clear_data_cache() -> None:
    """Invalidate the entire Streamlit data cache."""
    st.cache_data.clear()


def clear_resource_cache() -> None:
    """Invalidate the entire Streamlit resource cache."""
    st.cache_resource.clear()


# ---------------------------------------------------------------------------
# PERFORMANCE TIMER DECORATOR
# ---------------------------------------------------------------------------

def performance_timer(func: _F) -> _F:
    """Decorator that logs the wall-clock execution time of *func*."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = round(time.monotonic() - start, 4)
        log.info("Function %s executed in %.4fs", func.__name__, elapsed)
        return result

    return wrapper  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# EXECUTION LOGGING HELPER
# ---------------------------------------------------------------------------

def execution_log(module_name: str, execution_time: float) -> None:
    """Emit a structured execution-timing log record."""
    log.info("Module %s completed in %ss", module_name, execution_time)


# ---------------------------------------------------------------------------
# SESSION STATE HELPERS
# ---------------------------------------------------------------------------

def init_session_state(key: str, default_value: Any) -> None:
    """Initialise *key* in ``st.session_state`` only when it is absent."""
    if key not in st.session_state:
        st.session_state[key] = default_value


def update_session_state(key: str, value: Any) -> None:
    """Unconditionally set *key* in ``st.session_state``."""
    st.session_state[key] = value


def get_session_state(key: str, default: Any = None) -> Any:
    """Return the value for *key* from ``st.session_state``, or *default*."""
    return st.session_state.get(key, default)


# ---------------------------------------------------------------------------
# CACHE STATUS / HEALTH
# ---------------------------------------------------------------------------

def cache_status() -> dict[str, Any]:
    """Return a structured cache-status report."""
    return {
        "cache_ttl_seconds":    CACHE_TTL_SECONDS,
        "streamlit_cache_active": ENABLE_CACHE,
        "disk_cache_enabled":   ENABLE_DISK_CACHE,
        "cache_health":         "HEALTHY" if ENABLE_CACHE else "DISABLED",
    }


def cache_health() -> dict[str, Any]:
    """Return a structured cache-health assessment (alias of :func:`cache_status`)."""
    return {
        "cache_enabled":      ENABLE_CACHE,
        "disk_cache_enabled": ENABLE_DISK_CACHE,
        "cache_ttl_seconds":  CACHE_TTL_SECONDS,
        "cache_status":       "HEALTHY" if ENABLE_CACHE else "DISABLED",
    }
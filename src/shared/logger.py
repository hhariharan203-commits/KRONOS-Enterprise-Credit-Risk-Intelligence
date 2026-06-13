from __future__ import annotations

import logging
import os

from src.shared.config import LOG_LEVEL

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str = "kronos") -> logging.Logger:
    level_name = os.getenv("KRONOS_LOG_LEVEL", LOG_LEVEL).upper()
    level = getattr(logging, level_name, logging.INFO)

    if name in _LOGGERS:
        logger = _LOGGERS[name]
        logger.setLevel(level)
        return logger

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)

    _LOGGERS[name] = logger
    return logger

"""
Shared logging setup for the whole project.

Usage:
    from src.utils.logger import get_logger
    logger = get_logger(__name__)
"""

import logging
from pathlib import Path

from config.settings import LOG_DIR, LOG_LEVEL

_LOG_FILE = Path(LOG_DIR) / "app.log"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )

    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

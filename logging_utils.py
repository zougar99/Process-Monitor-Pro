# -*- coding: utf-8 -*-
"""Process Monitor Pro - Logging to file."""
import logging
import os
from datetime import datetime

from config import get_log_dir


def setup_logging(log_name="app", level=logging.INFO):
    """Create logs dir, add file handler. Returns root logger."""
    log_dir = get_log_dir()
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception:
        return logging.getLogger()
    log_file = os.path.join(log_dir, f"{log_name}.log")
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(level)
    if not root.handlers:
        root.addHandler(handler)
    return root


def log_message(message, level="info"):
    """Convenience: log one message with level (info, warning, error, debug)."""
    logger = logging.getLogger("ProcessMonitorPro")
    getattr(logger, level.lower(), logger.info)(message)

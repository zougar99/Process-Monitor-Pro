# -*- coding: utf-8 -*-
"""Process Monitor Pro - Settings persistence."""
import json
import os
from config import get_settings_path


def load_settings():
    """Load settings from file. Returns dict."""
    path = get_settings_path()
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_settings(data):
    """Save settings dict to file."""
    path = get_settings_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError:
        pass

# -*- coding: utf-8 -*-
"""Process Monitor Pro - Manage and launch configured applications."""
import json
import os
import subprocess
import sys

from config import get_apps_config_path


def load_apps_list():
    """Load list of configured applications."""
    path = get_apps_config_path()
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_apps_list(apps):
    """Save applications list to disk."""
    path = get_apps_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)


def run_app(path_or_cmd):
    """Launch application by path or command. Returns True on success."""
    if not path_or_cmd or not str(path_or_cmd).strip():
        return False
    try:
        flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
        if sys.platform == "win32":
            subprocess.Popen(path_or_cmd, shell=True, creationflags=flags)
        else:
            subprocess.Popen(path_or_cmd, shell=True)
        return True
    except Exception:
        return False

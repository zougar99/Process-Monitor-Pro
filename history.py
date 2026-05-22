# -*- coding: utf-8 -*-
"""Process Monitor Pro - History of ended processes and actions."""
import json
import os
from datetime import datetime

from config import get_history_path


def load_history():
    """Load history from file. Returns list of entries (newest first in file)."""
    path = get_history_path()
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_history(entries):
    """Save history list to file. Keeps last 500 entries."""
    path = get_history_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries[-500:], f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def append_ended_process(pid, name, success=True):
    """Append one 'process ended' entry to history."""
    entries = load_history()
    entries.append({
        "action": "end_process",
        "pid": pid,
        "name": name or "?",
        "success": success,
        "at": datetime.now().isoformat(),
    })
    return save_history(entries)

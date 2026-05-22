# -*- coding: utf-8 -*-
"""Process Monitor Pro - Export process list to CSV or JSON."""
import csv
import json
import os
from datetime import datetime


def process_row_to_dict(row):
    """(pid, name, cpu, ram, critical, has_network) -> dict."""
    return {
        "pid": row[0],
        "name": row[1],
        "cpu_percent": row[2],
        "ram_mb": row[3],
        "critical": row[4],
        "has_network": row[5] if len(row) > 5 else False,
    }


def export_to_json(data, filepath):
    """Export list of process rows to JSON. Returns (success, error_message)."""
    try:
        out = [
            process_row_to_dict(row)
            for row in data
        ]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        return (True, None)
    except Exception as e:
        return (False, str(e))


def export_to_csv(data, filepath):
    """Export list of process rows to CSV. Returns (success, error_message)."""
    try:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["pid", "name", "cpu_percent", "ram_mb", "critical", "has_network"])
            for row in data:
                r = list(row[:6]) if len(row) >= 6 else list(row) + [False] * (6 - len(row))
                w.writerow(r)
        return (True, None)
    except Exception as e:
        return (False, str(e))


def suggest_export_filename(extension):
    """Suggested filename with timestamp."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"processes_{ts}.{extension}"

# -*- coding: utf-8 -*-
"""Process Monitor Pro - Backup and restore apps list + settings."""
import json
import os
import shutil
from datetime import datetime

from config import get_base_dir, get_apps_config_path, get_settings_path, get_backup_dir


def ensure_backup_dir():
    """Create backups dir if missing. Returns path."""
    path = get_backup_dir()
    os.makedirs(path, exist_ok=True)
    return path


def backup_now():
    """
    Copy apps_list.json and settings.json to backups/ with timestamp.
    Returns (success, path_or_error).
    """
    base = get_base_dir()
    backup_dir = ensure_backup_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(backup_dir, f"backup_{ts}")
    try:
        os.makedirs(folder, exist_ok=True)
        apps_path = get_apps_config_path()
        if os.path.isfile(apps_path):
            shutil.copy2(apps_path, os.path.join(folder, "apps_list.json"))
        settings_path = get_settings_path()
        if os.path.isfile(settings_path):
            shutil.copy2(settings_path, os.path.join(folder, "settings.json"))
        return (True, folder)
    except Exception as e:
        return (False, str(e))


def list_backups():
    """List backup folder names (newest first)."""
    path = get_backup_dir()
    if not os.path.isdir(path):
        return []
    names = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and d.startswith("backup_")]
    names.sort(reverse=True)
    return names


def restore_backup(backup_folder_name):
    """
    Restore apps_list.json and settings.json from a backup folder.
    backup_folder_name is e.g. 'backup_20250204_120000'.
    Returns (success, error_message).
    """
    backup_dir = get_backup_dir()
    folder = os.path.join(backup_dir, backup_folder_name)
    if not os.path.isdir(folder):
        return (False, "Backup folder not found")
    try:
        apps_src = os.path.join(folder, "apps_list.json")
        if os.path.isfile(apps_src):
            shutil.copy2(apps_src, get_apps_config_path())
        settings_src = os.path.join(folder, "settings.json")
        if os.path.isfile(settings_src):
            shutil.copy2(settings_src, get_settings_path())
        return (True, None)
    except Exception as e:
        return (False, str(e))

# -*- coding: utf-8 -*-
"""
Process Monitor Pro - Development application helpers.
Open project folder, run terminal in project, open hosts, env vars, logs, edit project files, etc.
"""
import os
import subprocess
import sys

from config import (
    get_base_dir,
    get_log_dir,
    get_backup_dir,
    get_apps_config_path,
    get_settings_path,
)


def open_project_folder():
    """Open project base folder in Explorer. Returns True if started."""
    path = get_base_dir()
    if not os.path.isdir(path):
        return False
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def run_cmd_in_project():
    """Start CMD with current directory set to project folder."""
    path = get_base_dir()
    try:
        if sys.platform == "win32":
            subprocess.Popen(f'cmd /k cd /d "{path}"', shell=True)
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", f"cd {path}; exec bash"])
        return True
    except Exception:
        return False


def run_powershell_in_project():
    """Start PowerShell with current directory set to project folder."""
    path = get_base_dir()
    try:
        if sys.platform == "win32":
            subprocess.Popen(["powershell", "-NoExit", "-Command", f"Set-Location '{path}'"])
        return True
    except Exception:
        return False


def open_hosts_file():
    """Open hosts file in Notepad (requires admin to edit). Returns True if started."""
    try:
        if sys.platform == "win32":
            path = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32", "drivers", "etc", "hosts")
            subprocess.Popen(["notepad", path])
            return True
        return False
    except Exception:
        return False


def open_env_vars():
    """Open Windows Environment Variables dialog. Returns True if started."""
    try:
        if sys.platform == "win32":
            subprocess.Popen("rundll32 sysdm.cpl,EditEnvironmentVariables", shell=True)
            return True
        return False
    except Exception:
        return False


def open_logs_folder():
    """Open logs folder in Explorer."""
    path = get_log_dir()
    os.makedirs(path, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def open_backups_folder():
    """Open backups folder in Explorer."""
    path = get_backup_dir()
    os.makedirs(path, exist_ok=True)
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except Exception:
        return False


def open_file_in_editor(filepath, editor="notepad"):
    """Open a file in notepad (Windows) or default editor."""
    if not filepath or not os.path.isfile(filepath):
        return False
    try:
        if sys.platform == "win32":
            subprocess.Popen([editor, filepath])
        else:
            subprocess.Popen(["xdg-open", filepath])
        return True
    except Exception:
        return False


def open_readme():
    """Open README.md in Notepad."""
    path = os.path.join(get_base_dir(), "README.md")
    return open_file_in_editor(path)


def open_settings_json():
    """Open settings.json in Notepad."""
    return open_file_in_editor(get_settings_path())


def open_apps_list_json():
    """Open apps_list.json in Notepad."""
    return open_file_in_editor(get_apps_config_path())


def open_config_py():
    """Open config.py in Notepad."""
    path = os.path.join(get_base_dir(), "config.py")
    return open_file_in_editor(path)


def open_main_script():
    """Open process_monitor.py in Notepad."""
    path = os.path.join(get_base_dir(), "process_monitor.py")
    return open_file_in_editor(path)


def run_python_in_project():
    """Start Python interactive shell in project folder."""
    path = get_base_dir()
    try:
        if sys.platform == "win32":
            subprocess.Popen(f'cmd /k cd /d "{path}" && py -3', shell=True)
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", f"cd {path}; exec python3"])
        return True
    except Exception:
        return False


def open_in_cursor():
    """Open project folder in Cursor (if in PATH)."""
    path = get_base_dir()
    try:
        if sys.platform == "win32":
            subprocess.Popen(["cursor", path], shell=False)
        else:
            subprocess.Popen(["cursor", path])
        return True
    except Exception:
        try:
            subprocess.Popen(f'start cursor "{path}"', shell=True)
            return True
        except Exception:
            return False


def open_in_vscode():
    """Open project folder in VS Code (if in PATH)."""
    path = get_base_dir()
    try:
        if sys.platform == "win32":
            subprocess.Popen(["code", path], shell=False)
        else:
            subprocess.Popen(["code", path])
        return True
    except Exception:
        try:
            subprocess.Popen(f'start code "{path}"', shell=True)
            return True
        except Exception:
            return False


def open_requirements():
    """Open requirements.txt in Notepad."""
    path = os.path.join(get_base_dir(), "requirements.txt")
    return open_file_in_editor(path)


def get_dev_actions():
    """List of (label, callback) for development section. Callback takes no args."""
    return [
        ("Open project folder", open_project_folder),
        ("CMD in project", run_cmd_in_project),
        ("PowerShell in project", run_powershell_in_project),
        ("Python in project", run_python_in_project),
        ("Open in Cursor", open_in_cursor),
        ("Open in VS Code", open_in_vscode),
        ("Open README.md", open_readme),
        ("Open config.py", open_config_py),
        ("Open process_monitor.py", open_main_script),
        ("Open settings.json", open_settings_json),
        ("Open apps_list.json", open_apps_list_json),
        ("Open requirements.txt", open_requirements),
        ("Open hosts file", open_hosts_file),
        ("Environment variables", open_env_vars),
        ("Open logs folder", open_logs_folder),
        ("Open backups folder", open_backups_folder),
    ]

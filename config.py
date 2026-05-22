# -*- coding: utf-8 -*-
"""
Configuration file for Process Monitor Pro
"""

import os
import json

APP_NAME = "Process Monitor Pro"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "A professional process monitoring and system management tool."

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CRITICAL_PROCESSES = {
    "System", "Idle", "Registry", "smss.exe", "csrss.exe", "wininit.exe",
    "winlogon.exe", "services.exe", "lsass.exe", "svchost.exe",
    "explorer.exe", "taskmgr.exe", "RuntimeBroker.exe",
    "SecurityHealthService.exe", "MsMpEng.exe", "spoolsv.exe",
    "dwm.exe", "fontdrvhost.exe",
}

def get_base_dir():
    return _BASE_DIR

def get_apps_config_path():
    return os.path.join(_BASE_DIR, "apps_config.json")

def get_settings_path():
    return os.path.join(_BASE_DIR, "settings.json")

def get_backup_dir():
    return os.path.join(_BASE_DIR, "backups")

def get_history_path():
    return os.path.join(_BASE_DIR, "history.json")

def get_log_dir():
    p = os.path.join(_BASE_DIR, "logs")
    os.makedirs(p, exist_ok=True)
    return p

# Language preference file (in project root)
LANG_PREF_FILE = os.path.join(_BASE_DIR, '.lang_pref.json')

def load_language():
    """Load saved language preference."""
    try:
        if os.path.exists(LANG_PREF_FILE):
            with open(LANG_PREF_FILE, 'r', encoding='utf-8') as f:
                d = json.load(f)
                return d.get('lang', DEFAULT_LANGUAGE)
    except:
        pass
    return DEFAULT_LANGUAGE

def save_language(lang):
    """Save language preference."""
    try:
        with open(LANG_PREF_FILE, 'w', encoding='utf-8') as f:
            json.dump({'lang': lang}, f)
    except:
        pass

# VirusTotal API Key
# Get your free API key from: https://www.virustotal.com/gui/join-us
# Set it as environment variable: VIRUSTOTAL_API_KEY
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')

# Default scan settings
DEFAULT_SCAN_EXTENSIONS = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.vbs', '.js', '.ps1', '.zip', '.rar', '.7z']

# Real-time monitoring settings
DEFAULT_MONITOR_PATHS = [
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Documents"),
]

# Auto-action settings (like Norton, Malwarebytes, Kaspersky)
# none = ask user | quarantine = auto quarantine | block = add to blocklist | quarantine_high = auto quarantine only high-risk (70+)
AUTO_ACTION_OPTIONS = ['none', 'quarantine', 'quarantine_high', 'block', 'delete']

# Config file for user preferences
CONFIG_FILE = os.path.join(_BASE_DIR, '.antivirus_config.json')

def load_config():
    """Load antivirus config (auto_action, etc.)"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {
        'auto_action': 'none',
        'professional_mode': False,
        'notify_threat': True,
        'notify_scan_complete': True,
        'notify_protection': True,
        'sound_threat': True,
        'sound_scan': False,
        'use_in_app_bar': False,  # False = Windows toasts only (like Norton, Malwarebytes)
        # General
        'theme': 'dark',
        'auto_updates': True,
        'start_with_windows': False,
        # Scan and detections
        'scan_rootkits': False,
        'scan_archives': True,
        'use_ai_detection': True,
        'scan_performance': 'fast',
        'context_menu_scan': True,
        'detect_pup': True,
        'detect_pum': True,
        # Protection modules - one toggle for Malwarebytes module
        'malwarebytes_module': True,
        'web_protection': True,
        'malware_protection': True,
        'ransomware_protection': True,
        'exploit_protection': True,
        'obfuscation_detection': True,
        'data_theft_detection': True,
        'registry_detection': True,
        'auto_quarantine': True,
        # Notifications
        'notify_close_after': 2,
    }

def save_config(cfg):
    """Save antivirus config"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except:
        pass

# Notification settings
NOTIFICATIONS_ENABLED = True

# Language: 'ar' = Arabic (العربية), 'en' = English
DEFAULT_LANGUAGE = 'ar'

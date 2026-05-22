# -*- coding: utf-8 -*-
"""
Process Monitor Pro - System tools (Windows).
List of (label, command) to launch system utilities. Use run_tool(cmd) to run.
"""
from apps_manager import run_app

# (display name, command or executable)
TOOLS = [
    # Task & performance
    ("Task Manager", "taskmgr"),
    ("Resource Monitor", "resmon"),
    ("Performance Monitor", "perfmon"),
    ("Event Viewer", "eventvwr"),
    ("Task Scheduler", "taskschd.msc"),
    # System
    ("System Config (msconfig)", "msconfig"),
    ("System Information", "msinfo32"),
    ("System Properties", "sysdm.cpl"),
    ("Control Panel", "control"),
    ("Computer Management", "compmgmt.msc"),
    ("Services", "services.msc"),
    ("Device Manager", "devmgmt.msc"),
    ("Registry Editor", "regedit"),
    # Disk & storage
    ("Disk Cleanup", "cleanmgr"),
    ("Disk Management", "diskmgmt.msc"),
    # Network
    ("Network Connections", "ncpa.cpl"),
    ("Windows Firewall", "wf.msc"),
    ("Remote Desktop", "mstsc"),
    # Programs & features
    ("Programs and Features", "appwiz.cpl"),
    # Settings / config
    ("Date and Time", "timedate.cpl"),
    ("Power Options", "powercfg.cpl"),
    ("Sound", "mmsys.cpl"),
    ("Display", "desk.cpl"),
    ("Mouse", "main.cpl"),
    ("Keyboard", "main.cpl keyboard"),
    ("Color Management", "colorcpl"),
    ("Region", "intl.cpl"),
    # Utilities
    ("Command Prompt", "cmd"),
    ("PowerShell", "powershell"),
    ("Notepad", "notepad"),
    ("Calculator", "calc"),
    ("Snipping Tool", "snippingtool"),
    ("Character Map", "charmap"),
    ("DirectX Diagnostic", "dxdiag"),
    # Recovery / backup
    ("System Restore", "rstrui"),
    ("Backup and Restore", "sdclt"),
    # Advanced (optional)
    ("Shared Folders", "fsmgmt.msc"),
    ("Print Management", "printmanagement.msc"),
    ("Local Security Policy", "secpol.msc"),
    ("Group Policy", "gpedit.msc"),
    # Additional tools
    ("Windows Security", "windowsdefender:"),
    ("Windows Update", "ms-settings:windowsupdate"),
    ("About Your PC", "ms-settings:about"),
    ("Bluetooth", "ms-settings:bluetooth"),
    ("Display Settings", "ms-settings:display"),
    ("Sound Settings", "ms-settings:sound"),
    ("Troubleshooting", "ms-settings:troubleshoot"),
    ("Taskbar Settings", "ms-settings:taskbar"),
    ("Storage", "ms-settings:storagesense"),
    ("Apps & Features", "ms-settings:appsfeatures"),
    ("Default Apps", "ms-settings:defaultapps"),
    ("Privacy & Security", "ms-settings:privacy"),
    ("Network & Internet", "ms-settings:network"),
    ("Gaming", "ms-settings:gaming"),
    ("Ease of Access", "ms-settings:easeofaccess"),
    ("Recovery Options", "ms-settings:recovery"),
    ("Multitasking", "ms-settings:multitasking"),
    ("Clipboard", "ms-settings:clipboard"),
    ("Windows Activation", "ms-settings:activation"),
    ("Windows PowerShell ISE", "powershell_ise"),
    ("File Explorer", "explorer"),
    ("On-Screen Keyboard", "osk"),
    ("Magnifier", "magnify"),
    ("Narrator", "narrator"),
    ("Windows Media Player", "wmplayer"),
    ("Paint", "mspaint"),
    ("WordPad", "write"),
    ("Sticky Notes", "stikynot"),
    ("Windows Fax and Scan", "wfs"),
    ("Steps Recorder", "psr"),
    ("Resource Monitor (perf)", "perfmon /res"),
    ("Reliability Monitor", "perfmon /rel"),
    ("Windows Memory Diagnostic", "MdSched"),
    ("Defragment Drives", "dfrgui"),
    ("iSCSI Initiator", "iscsicpl"),
    ("ODBC Data Sources", "odbcad32"),
    ("Windows Features", "optionalfeatures"),
    ("Credential Manager", "credwiz"),
    ("Performance Options", "systempropertiesperformance"),
    ("Environment Variables", "rundll32 sysdm.cpl,EditEnvironmentVariables"),
]


def get_tools_list():
    """Return list of (label, command)."""
    return list(TOOLS)


def run_tool(command):
    """Launch a system tool by command. Returns True if started."""
    return run_app(command)

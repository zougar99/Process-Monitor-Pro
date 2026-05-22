# 🖥️ Process Monitor Pro

A professional Windows process monitoring and system management tool built with Python and CustomTkinter. Monitor, analyze, and manage system processes with a modern dark-themed GUI.

---

## 📸 Screenshots

```
┌─────────────────────────────────────────────────────┐
│  Process Monitor Pro                  [⏳Refresh]   │
├──────────┬──────────────┬──────────┬───────────────┤
│Processes │Process Explorer│Tools...│System │Mix Mon│
├──────────┴──────────────┴──────────┴───────────────┤
│ PID  │ Name               │ CPU % │ RAM (MB) │ Net │
│ 1234 │ chrome.exe          │ 12.5  │ 345.2    │  🌐 │
│ 5678 │ python.exe          │ 8.2   │ 120.1    │     │
│ ...                                                │
└─────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🛠️ Process Management
- **📋 Live process list** — View all running processes with PID, name, CPU %, RAM usage, and network activity
- **🔍 Filtering** — Filter by name, safe-only, or network-only
- **⛔ End processes** — Kill single processes, top 5 RAM hogs, or all network-connected processes
- **🔒 Critical process lock** — Prevent accidental termination of system-critical processes
- **📤 Export** — Save process data to CSV or JSON

### 🔬 Process Explorer
- **📂 Detailed view** — See executable paths for every process
- **🔎 Search by path or name** — Find processes quickly
- **🗑️ End by path** — Kill all processes matching a path/name at once

### ⚡ System Tools
- **🔧 70+ Windows utilities** — Launch Task Manager, Regedit, Services, Device Manager, Disk Cleanup, PowerShell, and more
- **⚙️ Windows Settings integration** — Access Display, Sound, Bluetooth, Network, Privacy, and other settings panels

### 💻 System Information
- **🖧 Hardware overview** — OS version, CPU cores, RAM total/available/used, disk total/free/used
- **📊 Process statistics** — Total processes, safe vs critical count, RAM and CPU totals

### 📊 Mix Monitor (mz1)
- **📸 One-shot snapshot** — Combines system info + top CPU processes + top RAM processes
- **📑 Side-by-side view** — Compare top CPU and RAM consumers in parallel columns
- **🔄 Auto-load** — Data loads automatically when you open the tab

### 🚀 App Launcher
- **📌 Custom apps** — Register your own applications for quick launch
- **▶️ Multi-launch** — Run 1, 2, 3, or all registered apps at once

### 💾 History & Backup
- **📜 Ended process history** — Track which processes you've terminated
- **📦 Backup/Restore** — Save and restore your app lists and settings

### 🔔 Desktop Notifications
- **⚠️ Process alerts** — Get notified when high-memory processes are detected
- **⚙️ Configurable** — Enable/disable notifications in settings

---

## 📦 Requirements

| Dependency | Version | Purpose |
|-----------|---------|---------|
| 🐍 Python | 3.8+ | Runtime |
| 🎨 [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | latest | Modern dark-themed UI widgets |
| 📟 [psutil](https://github.com/giampaolo/psutil) | latest | System and process information |

---

## 💿 Installation

### ⚡ Quick install

```bash
pip install customtkinter psutil
```

### 📄 Using requirements.txt

```bash
pip install -r requirements.txt
```

### ✅ Verify installation

```bash
python -c "import customtkinter; import psutil; print('Ready')"
```

---

## 🚀 Usage

```bash
python main.py
```

### 📑 Tabs overview

| Tab | What you can do |
|-----|----------------|
| 🗂️ **Processes** | View, filter, and end processes. Export data. |
| 🔬 **Process Explorer** | Browse processes with executable paths. End by path. |
| 🔧 **Tools & Launch** | Launch system tools and your custom apps. |
| 💻 **System** | View hardware info, process stats, and mix snapshot. |
| 📊 **Mix Monitor** | Side-by-side top CPU and RAM with system overview. |

### ⌨️ Keyboard & controls

- 🔄 Use the **Refresh** button to reload process data
- 🔒 Toggle **Lock** to protect critical system processes
- 🔍 Use **Filter** to narrow down process lists
- ℹ️ Click **About** for version info

---

## 📁 Project Structure

```
├── 📄 main.py                  # Application entry point
├── 🖥️ process_monitor.py       # Main GUI (5 tabs, event handling)
├── ⚙️ config.py                # App settings, paths, critical process list
├── 🔄 process_utils.py         # Process enumeration, termination
├── 🔧 system_tools.py          # 70+ Windows system tool definitions
├── 📊 system_info.py           # CPU, RAM, disk, OS info
├── 📈 stats.py                 # Aggregate statistics, top CPU/RAM
├── 🔍 filters.py               # Process filtering logic
├── 📸 mix_mon.py               # Combined system + process snapshot
├── 📌 apps_manager.py          # Custom app registration & launch
├── 📤 export_utils.py          # CSV and JSON export
├── 📜 history.py               # Ended process history
├� 📦 backup_restore.py         # Backup/restore apps & settings
├── 💾 settings.py              # Settings persistence
├── ⏰ auto_refresh.py          # Periodic refresh timer
├── 📝 logging_utils.py         # File logging
├── 🔔 notifications.py         # Desktop notifications
├── 🛠️ dev_tools.py             # Developer utilities
├── ✅ validators.py            # Input validation
├── ➕ additional_tools.py      # Extra tool integrations
├── 🧪 advanced_tools.py        # Advanced system analysis
├── 🔬 advanced_system_analysis.py # Deep system analysis
├── ⚡ performance_optimizer.py # Performance tuning
├── 🏢 professional_main.py     # Professional mode entry
├── 📋 professional_modules.py  # Professional modules
├── 🎨 professional_ui.py       # Professional UI components
└── 📂 backups/                 # Backup storage directory
```

---

## ⚙️ Configuration

Settings are stored in `settings.json` in the project root. Key options:

| Setting | Default | Description |
|---------|---------|-------------|
| 🌗 `theme` | `dark` | UI theme (`dark`, `light`, `system`) |
| 🔒 `lock_critical` | `true` | Prevent ending critical processes |
| 📐 `window_width` | `920` | Initial window width |
| 📐 `window_height` | `620` | Initial window height |

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| ❌ `ImportError: no module named customtkinter` | Run `pip install customtkinter` |
| ❌ `ImportError: no module named psutil` | Run `pip install psutil` |
| 🚫 `Access denied` when ending a process | Run as Administrator |
| 💥 App doesn't start | Check Python version: `python --version` (needs 3.8+) |

---

## 📄 License

MIT — Free to use, modify, and distribute.

---

## 👤 Author

Developed as a professional system administration tool for Windows.

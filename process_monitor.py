# -*- coding: utf-8 -*-
"""
Process Monitor Pro - Manageable application.
Shows CPU & RAM per process, end processes, run system tools and configured apps.
"""
import os
import threading
from tkinter import messagebox, filedialog

import customtkinter as ctk

from config import APP_NAME, APP_VERSION, APP_DESCRIPTION
from process_utils import get_processes, get_processes_detailed, kill_process
from apps_manager import load_apps_list, save_apps_list, run_app
from system_tools import get_tools_list, run_tool
from system_info import get_summary
from export_utils import export_to_csv, export_to_json, suggest_export_filename
from settings import load_settings, save_settings
from logging_utils import setup_logging, log_message
from filters import filter_processes
from history import append_ended_process
from backup_restore import backup_now, list_backups, restore_backup
from auto_refresh import AutoRefreshTimer
from process_details import get_process_details
from stats import compute_stats, top_by_ram, top_by_cpu
from mix_mon import get_mix_snapshot_light, mix_summary_text
from dev_tools import get_dev_actions

setup_logging("app")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ProcessMonitorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.title(APP_NAME)
        w = self.settings.get("window_width", 920)
        h = self.settings.get("window_height", 620)
        self.geometry(f"{w}x{h}")
        self.minsize(720, 420)
        theme = self.settings.get("theme", "dark")
        ctk.set_appearance_mode(theme if theme in ("dark", "light", "system") else "dark")

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            header,
            text=APP_NAME,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")
        self.refresh_btn = ctk.CTkButton(
            header, text="⏳ Refresh", command=self.refresh, width=120
        )
        self.refresh_btn.pack(side="right", padx=5)
        self.kill_btn = ctk.CTkButton(
            header,
            text="🛑 End Process",
            command=self.do_kill,
            width=120,
            fg_color="#c0392b",
            hover_color="#a93226",
        )
        self.kill_btn.pack(side="right", padx=5)
        self.lock_var = ctk.BooleanVar(value=bool(self.settings.get("lock_critical", True)))
        self.lock_switch = ctk.CTkSwitch(
            header,
            text="🔒 Lock (don't end critical)",
            variable=self.lock_var,
            width=220,
        )
        self.lock_switch.pack(side="right", padx=10)
        ctk.CTkButton(header, text="About", width=70, command=self._show_about).pack(side="right", padx=5)

        # Tabs
        self.tabview = ctk.CTkTabview(self, width=800)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        tab_processes = self.tabview.add("Processes")
        tab_explorer = self.tabview.add("Process Explorer")
        tab_tools = self.tabview.add("Tools & Launch")
        tab_system = self.tabview.add("System")
        tab_mix = self.tabview.add("Mix Monitor")
        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.status_label.pack(pady=(0, 8))

        # --- Tab Processes ---
        filter_row = ctk.CTkFrame(tab_processes, fg_color="transparent")
        filter_row.pack(fill="x", pady=(0, 4))
        ctk.CTkLabel(filter_row, text="Filter name:", width=80).pack(side="left", padx=2)
        self.filter_entry = ctk.CTkEntry(filter_row, width=180, placeholder_text="process name...")
        self.filter_entry.pack(side="left", padx=4)
        self.filter_safe_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(filter_row, text="Safe only", variable=self.filter_safe_var, width=90).pack(side="left", padx=4)
        self.filter_net_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(filter_row, text="Network only", variable=self.filter_net_var, width=110).pack(side="left", padx=4)
        ctk.CTkButton(filter_row, text="Apply filter", width=90, command=self._apply_filter_click).pack(side="left", padx=4)
        table_header = ctk.CTkFrame(tab_processes, fg_color="transparent")
        table_header.pack(fill="x", padx=0, pady=(0, 5))
        for col, w in [("PID", 70), ("Name", 220), ("CPU %", 70), ("RAM (MB)", 70), ("Net", 40), ("Type", 80)]:
            ctk.CTkLabel(table_header, text=col, width=w, anchor="w").pack(side="left", padx=2)
        actions = ctk.CTkFrame(tab_processes, fg_color="transparent")
        actions.pack(fill="x", pady=(0, 4))
        ctk.CTkButton(
            actions,
            text="End top 5 RAM",
            width=120,
            fg_color="#8e44ad",
            hover_color="#7d3c98",
            command=self._kill_top_ram,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            actions,
            text="End with network",
            width=130,
            fg_color="#2980b9",
            hover_color="#1f6dad",
            command=self._kill_network_processes,
        ).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Export CSV", width=100, command=self._export_csv).pack(side="left", padx=4)
        ctk.CTkButton(actions, text="Export JSON", width=100, command=self._export_json).pack(side="left", padx=4)
        self.scroll = ctk.CTkScrollableFrame(tab_processes, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        self.rows = []
        self.selected_pid = None
        self.selected_critical = False
        self.last_process_data = []

        # --- Tab Process Explorer ---
        self._build_process_explorer_tab(tab_explorer)

        # --- Tab System ---
        self._build_system_tab(tab_system)

        # --- Tab Mix Monitor (mz1) ---
        self._build_mix_tab(tab_mix)

        # --- Tab Tools & Launch ---
        tools_frame = ctk.CTkFrame(tab_tools, fg_color="transparent")
        tools_frame.pack(fill="x", pady=(0, 5))
        ctk.CTkLabel(tools_frame, text="System tools", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        tools_scroll = ctk.CTkScrollableFrame(tools_frame, fg_color="transparent", height=200)
        tools_scroll.pack(fill="x", pady=5)
        tools_list = get_tools_list()
        cols = 4
        for row_start in range(0, len(tools_list), cols):
            row_frame = ctk.CTkFrame(tools_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            for col in range(cols):
                i = row_start + col
                if i >= len(tools_list):
                    break
                label, cmd = tools_list[i]
                btn = ctk.CTkButton(
                    row_frame, text=label, width=180, height=28,
                    command=lambda c=cmd: run_tool(c),
                )
                btn.pack(side="left", padx=4, pady=2)

        act_frame = ctk.CTkFrame(tab_tools, fg_color="transparent")
        act_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(
            act_frame,
            text="Launch apps — Run 1, 2, 3, or All",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w")
        self.apps_listbox_frame = ctk.CTkScrollableFrame(
            act_frame, fg_color="transparent", height=120
        )
        self.apps_listbox_frame.pack(fill="x", pady=8)
        self.apps_buttons = ctk.CTkFrame(act_frame, fg_color="transparent")
        self.apps_buttons.pack(fill="x", pady=5)
        for i, label in enumerate(["Launch 1", "Launch 2", "Launch 3"], 1):
            btn = ctk.CTkButton(
                self.apps_buttons,
                text=label,
                width=110,
                command=lambda n=i: self._run_n_apps(n),
            )
            btn.pack(side="left", padx=4, pady=4)
        ctk.CTkButton(
            self.apps_buttons,
            text="Launch All",
            width=110,
            fg_color="#27ae60",
            hover_color="#1e8449",
            command=self._run_all_apps,
        ).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(self.apps_buttons, text="➕ Add app", width=100, command=self._add_app).pack(
            side="left", padx=4, pady=4
        )
        ctk.CTkButton(
            self.apps_buttons, text="➕ Add path", width=100, command=self._add_app_by_path
        ).pack(side="left", padx=4, pady=4)
        backup_row = ctk.CTkFrame(tab_tools, fg_color="transparent")
        backup_row.pack(fill="x", pady=(15, 0))
        ctk.CTkLabel(backup_row, text="Backup / Restore", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        btn_row = ctk.CTkFrame(backup_row, fg_color="transparent")
        btn_row.pack(fill="x", pady=5)
        ctk.CTkButton(btn_row, text="💾 Backup now", width=120, command=self._backup_now).pack(side="left", padx=4, pady=4)
        self.restore_var = ctk.StringVar(value="")
        backups = list_backups()
        self.restore_menu = ctk.CTkOptionMenu(
            btn_row, variable=self.restore_var, values=backups if backups else ["(no backups)"], width=200
        )
        self.restore_menu.pack(side="left", padx=4, pady=4)
        ctk.CTkButton(btn_row, text="Restore", width=80, command=self._restore_backup).pack(side="left", padx=4, pady=4)
        dev_row = ctk.CTkFrame(tab_tools, fg_color="transparent")
        dev_row.pack(fill="x", pady=(15, 0))
        ctk.CTkLabel(dev_row, text="Development", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        dev_scroll = ctk.CTkScrollableFrame(dev_row, fg_color="transparent", height=140)
        dev_scroll.pack(fill="x", pady=5)
        dev_actions = get_dev_actions()
        dev_cols = 4
        for row_start in range(0, len(dev_actions), dev_cols):
            r = ctk.CTkFrame(dev_scroll, fg_color="transparent")
            r.pack(fill="x", pady=2)
            for col in range(dev_cols):
                i = row_start + col
                if i >= len(dev_actions):
                    break
                label, callback = dev_actions[i]
                ctk.CTkButton(r, text=label, width=170, height=26, command=callback).pack(side="left", padx=4, pady=2)
        self._refresh_apps_display()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._auto_refresh = None
        interval = self.settings.get("auto_refresh_seconds", 0)
        if interval and int(interval) > 0:
            self._auto_refresh = AutoRefreshTimer(int(interval), self.refresh)
            self._auto_refresh.start()
        self.refresh()

    def refresh(self):
        def _run():
            self.after(0, lambda: self.status_label.configure(text="Loading...", text_color="gray"))
            self.after(0, lambda: self.refresh_btn.configure(state="disabled", text="..."))
            data = get_processes()
            self.after(0, lambda: self._apply_filter_and_update(data))
            self.after(0, lambda: self.refresh_btn.configure(state="normal", text="⏳ Refresh"))
            self.after(0, lambda: None)  # status set in _apply_filter_and_update

        threading.Thread(target=_run, daemon=True).start()

    def _build_process_explorer_tab(self, tab):
        filter_row = ctk.CTkFrame(tab, fg_color="transparent")
        filter_row.pack(fill="x", pady=(5, 4))
        ctk.CTkLabel(filter_row, text="Search path/name:", width=120).pack(side="left", padx=2)
        self.explorer_filter_entry = ctk.CTkEntry(filter_row, width=250, placeholder_text="process name or path...")
        self.explorer_filter_entry.pack(side="left", padx=4)
        ctk.CTkButton(filter_row, text="Search", width=80, command=self._refresh_explorer).pack(side="left", padx=4)
        ctk.CTkButton(filter_row, text="Clear", width=80, command=lambda: (self.explorer_filter_entry.delete(0, "end"), self._refresh_explorer())).pack(side="left", padx=4)

        table_header = ctk.CTkFrame(tab, fg_color="transparent")
        table_header.pack(fill="x", padx=0, pady=(0, 5))
        for col, w in [("PID", 60), ("Name", 180), ("Path", 300), ("CPU %", 60), ("RAM (MB)", 70), ("Net", 40), ("Type", 60)]:
            ctk.CTkLabel(table_header, text=col, width=w, anchor="w").pack(side="left", padx=2)

        btn_row = ctk.CTkFrame(tab, fg_color="transparent")
        btn_row.pack(fill="x", pady=4)
        ctk.CTkButton(btn_row, text="End Selected Process", width=160, fg_color="#c0392b", hover_color="#a93226", command=self._explorer_kill).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="End by Path", width=140, fg_color="#8e44ad", hover_color="#7d3c98", command=self._explorer_kill_by_path).pack(side="left", padx=4)
        ctk.CTkButton(btn_row, text="Refresh", width=90, command=self._refresh_explorer).pack(side="left", padx=4)
        self.explorer_status = ctk.CTkLabel(btn_row, text="", text_color="gray")
        self.explorer_status.pack(side="left", padx=10)

        self.explorer_scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.explorer_scroll.pack(fill="both", expand=True, padx=0, pady=(0, 10))

        self.explorer_rows = []
        self._refresh_explorer()

    def _refresh_explorer(self):
        from process_utils import get_processes_detailed
        for row in self.explorer_rows:
            for w in row:
                w.destroy()
        self.explorer_rows.clear()
        query = self.explorer_filter_entry.get().strip().lower()
        try:
            procs = get_processes_detailed()
        except Exception:
            self.explorer_status.configure(text="Error loading processes")
            return
        if query:
            procs = [p for p in procs if query in p[1].lower() or query in p[6].lower()]
        for proc in procs:
            pid, name, cpu, ram, critical, has_net, exe = proc
            path = exe if exe else "—"
            if len(path) > 80:
                path = "..." + path[-77:]
            row_frame = ctk.CTkFrame(self.explorer_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=1)
            row_data = []
            for col, (val, w) in enumerate([
                (str(pid), 60),
                (name[:40], 180),
                (path, 300),
                (f"{cpu:.1f}", 60),
                (f"{ram:.0f}", 70),
                ("🌐" if has_net else "", 40),
                ("Critical" if critical else "Safe", 60),
            ]):
                kw = {"text": val, "width": w, "anchor": "w"}
                if col == 6 and critical:
                    kw["text_color"] = "#e74c3c"
                lbl = ctk.CTkLabel(row_frame, **kw)
                lbl.pack(side="left", padx=2)
                row_data.append(lbl)
            row_frame.bind("<Button-1>", lambda e, r=row_data, p=pid, c=critical: self._explorer_select(r, p, c))
            for lbl in row_data:
                lbl.bind("<Button-1>", lambda e, r=row_data, p=pid, c=critical: self._explorer_select(r, p, c))
            self.explorer_rows.append(row_data)
        self.explorer_selected_pid = None
        self.explorer_selected_critical = False
        self.explorer_status.configure(text=f"{len(procs)} processes")

    def _explorer_select(self, row_data, pid, critical):
        for row in self.explorer_rows:
            for lbl in row:
                lbl.configure(fg_color="")
        for lbl in row_data:
            lbl.configure(fg_color="#2a5a8a")
        self.explorer_selected_pid = pid
        self.explorer_selected_critical = critical

    def _explorer_kill(self):
        pid = getattr(self, "explorer_selected_pid", None)
        if pid is None:
            messagebox.showinfo("Info", "Select a process from the list.")
            return
        if getattr(self, "explorer_selected_critical", False) and self.lock_var.get():
            messagebox.showwarning("Locked", "Cannot end critical process while lock is on.")
            return
        if messagebox.askyesno("Confirm", f"End process PID {pid}?"):
            ok, err = kill_process(pid)
            if ok:
                self._refresh_explorer()
                self._refresh_process_list()
                self.explorer_status.configure(text=f"Process {pid} ended")
            else:
                messagebox.showerror("Error", f"Failed: {err}")

    def _explorer_kill_by_path(self):
        path = self.explorer_filter_entry.get().strip()
        if not path:
            messagebox.showinfo("Info", "Enter a path or name to search for, then click End by Path.")
            return
        from process_utils import get_processes_detailed
        try:
            procs = get_processes_detailed()
        except Exception:
            self.explorer_status.configure(text="Error loading processes")
            return
        q = path.lower()
        matches = [p for p in procs if q in p[1].lower() or q in p[6].lower()]
        if not matches:
            messagebox.showinfo("Info", f"No processes matching '{path}'")
            return
        count = 0
        errors = []
        for p in matches:
            pid, name, _, _, critical, _, _ = p
            if critical and self.lock_var.get():
                errors.append(f"{name} (PID {pid}): locked (critical)")
                continue
            ok, err = kill_process(pid)
            if ok:
                count += 1
            else:
                errors.append(f"{name} (PID {pid}): {err}")
        msg = f"Ended {count} process(es)"
        if errors:
            msg += "\nErrors:\n" + "\n".join(errors[:5])
        messagebox.showinfo("Result", msg)
        self._refresh_explorer()
        self._refresh_process_list()

    def _build_system_tab(self, tab):
        info = get_summary()
        frame = ctk.CTkFrame(tab, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        lines = [
            ("OS", info.get("os", "—")),
            ("CPU cores", str(info.get("cpu_count", 0))),
            ("RAM total", f"{info.get('memory_total_mb', 0):.0f} MB"),
            ("RAM available", f"{info.get('memory_available_mb', 0):.0f} MB"),
            ("RAM used %", f"{info.get('memory_percent', 0):.0f}%"),
            ("Disk total", f"{info.get('disk_total_gb', 0):.1f} GB"),
            ("Disk free", f"{info.get('disk_free_gb', 0):.1f} GB"),
            ("Disk used %", f"{info.get('disk_percent', 0):.0f}%"),
        ]
        for label, value in lines:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{label}:", width=140, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w").pack(side="left")
        ctk.CTkLabel(frame, text="Process stats (after Refresh)", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 5))
        self.system_stats_label = ctk.CTkLabel(frame, text="Refresh Processes tab first.", anchor="w", justify="left")
        self.system_stats_label.pack(fill="x")
        ctk.CTkLabel(frame, text="Mix Monitor", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(15, 5))
        mix_row = ctk.CTkFrame(frame, fg_color="transparent")
        mix_row.pack(fill="x", pady=4)
        ctk.CTkButton(mix_row, text="Refresh mix snapshot", width=160, command=self._refresh_mix).pack(side="left", padx=4, pady=4)
        self.mix_label = ctk.CTkLabel(frame, text="Click to load system + processes + tops in one shot.", anchor="w", justify="left")
        self.mix_label.pack(fill="x")

    def _update_system_stats(self, data=None):
        data = data if data is not None else getattr(self, "last_process_data", [])
        if not data:
            return
        st = compute_stats(data)
        text = (
            f"Total: {st['total_count']}  |  Safe: {st['safe_count']}  |  Critical: {st['critical_count']}  |  "
            f"With network: {st['network_count']}  |  Total RAM: {st['total_ram_mb']} MB  |  Total CPU: {st['total_cpu_percent']}%"
        )
        if getattr(self, "system_stats_label", None):
            self.system_stats_label.configure(text=text)

    def _show_about(self):
        messagebox.showinfo(
            "About",
            f"{APP_NAME}\nVersion {APP_VERSION}\n\n{APP_DESCRIPTION}",
        )

    def _build_mix_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="System Overview", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        self.mix_system_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.mix_system_frame.pack(fill="x", pady=5)

        sep = ctk.CTkFrame(scroll, height=2, fg_color="gray")
        sep.pack(fill="x", pady=10)

        row_top = ctk.CTkFrame(scroll, fg_color="transparent")
        row_top.pack(fill="x")
        ctk.CTkLabel(row_top, text="Top 10 CPU", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 40))
        ctk.CTkLabel(row_top, text="Top 10 RAM", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        frames_row = ctk.CTkFrame(scroll, fg_color="transparent")
        frames_row.pack(fill="x", pady=5)
        self.mix_cpu_frame = ctk.CTkFrame(frames_row, fg_color="transparent")
        self.mix_cpu_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.mix_ram_frame = ctk.CTkFrame(frames_row, fg_color="transparent")
        self.mix_ram_frame.pack(side="left", fill="x", expand=True)

        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", pady=10)
        ctk.CTkButton(btn_row, text="Refresh Mix Monitor", width=180, command=self._refresh_mix_tab).pack(side="left", padx=4)
        self.mix_tab_status = ctk.CTkLabel(btn_row, text="", text_color="gray")
        self.mix_tab_status.pack(side="left", padx=10)

        self.after(500, self._refresh_mix_tab)

    def _refresh_mix_tab(self):
        def _run():
            self.after(0, lambda: self.mix_tab_status.configure(text="Loading..."))
            import time
            time.sleep(0.1)
            try:
                snap = get_mix_snapshot_light(top_n=10)
                sys_info = snap.get("system", {})
                lines = [
                    f"OS: {sys_info.get('os', '—')}",
                    f"CPU cores: {sys_info.get('cpu_count', 0)}",
                    f"RAM: {sys_info.get('memory_total_mb', 0):.0f} MB total, {sys_info.get('memory_available_mb', 0):.0f} MB free ({sys_info.get('memory_percent', 0):.0f}% used)",
                    f"Disk: {sys_info.get('disk_total_gb', 0):.1f} GB total, {sys_info.get('disk_free_gb', 0):.1f} GB free ({sys_info.get('disk_percent', 0):.0f}% used)",
                ]
                self.after(0, lambda: self._update_mix_system(lines))
                procs = snap.get("processes", [])
                top_cpu = top_by_cpu(procs, n=10)
                top_ram = top_by_ram(procs, n=10)
                self.after(0, lambda: self._update_mix_lists(top_cpu, top_ram))
                st = snap.get("process_stats", {})
                summary = mix_summary_text(snap)
                self.after(0, lambda: self.mix_tab_status.configure(text=summary))
            except Exception as e:
                self.after(0, lambda: self.mix_tab_status.configure(text=f"Error: {e}"))

        threading.Thread(target=_run, daemon=True).start()

    def _update_mix_system(self, lines):
        for w in self.mix_system_frame.winfo_children():
            w.destroy()
        for line in lines:
            ctk.CTkLabel(self.mix_system_frame, text=line, anchor="w", justify="left").pack(fill="x", pady=1)

    def _update_mix_lists(self, top_cpu, top_ram):
        for w in self.mix_cpu_frame.winfo_children():
            w.destroy()
        for w in self.mix_ram_frame.winfo_children():
            w.destroy()
        for i, proc in enumerate(top_cpu, 1):
            pid, name, cpu, ram = proc[0], proc[1], proc[2], proc[3]
            text = f"{i}. {name} (PID {pid}) — CPU: {cpu:.1f}%, RAM: {ram:.0f} MB"
            ctk.CTkLabel(self.mix_cpu_frame, text=text, anchor="w", justify="left").pack(fill="x", pady=1)
        for i, proc in enumerate(top_ram, 1):
            pid, name, cpu, ram = proc[0], proc[1], proc[2], proc[3]
            text = f"{i}. {name} (PID {pid}) — CPU: {cpu:.1f}%, RAM: {ram:.0f} MB"
            ctk.CTkLabel(self.mix_ram_frame, text=text, anchor="w", justify="left").pack(fill="x", pady=1)

    def _refresh_mix(self):
        def _run():
            self.after(0, lambda: self.mix_label.configure(text="Loading mix..."))
            try:
                snap = get_mix_snapshot_light(top_n=5)
                line = mix_summary_text(snap)
                top = snap.get("top_ram", [])[:5]
                extra = "\nTop RAM: " + ", ".join(r[1] for r in top) if top else ""
                text = line + extra
            except Exception as e:
                text = f"Error: {e}"
            self.after(0, lambda: self.mix_label.configure(text=text))

        threading.Thread(target=_run, daemon=True).start()

    def _backup_now(self):
        ok, path_or_err = backup_now()
        if ok:
            messagebox.showinfo("Backup", f"Backup saved to:\n{path_or_err}")
            backups = list_backups()
            if getattr(self, "restore_menu", None) and backups:
                self.restore_var.set(backups[0])
                self.restore_menu.configure(values=backups)
        else:
            messagebox.showerror("Backup failed", path_or_err)

    def _restore_backup(self):
        name = self.restore_var.get().strip()
        if not name or name == "(no backups)" or not name.startswith("backup_"):
            messagebox.showinfo("Restore", "Select a backup from the list.")
            return
        if not messagebox.askyesno("Restore", f"Restore from {name}? App will use restored apps and settings."):
            return
        ok, err = restore_backup(name)
        if ok:
            messagebox.showinfo("Restore", "Restored. Restart the app to apply.")
            self._refresh_apps_display()
        else:
            messagebox.showerror("Restore failed", err or "Unknown error")

    def _export_csv(self):
        data = getattr(self, "last_process_data", [])
        if not data:
            messagebox.showinfo("Info", "Refresh first to get process list.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")],
            initialfile=suggest_export_filename("csv"),
        )
        if path:
            ok, err = export_to_csv(data, path)
            if ok:
                log_message(f"Exported CSV: {path}")
                messagebox.showinfo("OK", f"Saved to {path}")
            else:
                messagebox.showerror("Export failed", err or "Unknown error")

    def _export_json(self):
        data = getattr(self, "last_process_data", [])
        if not data:
            messagebox.showinfo("Info", "Refresh first to get process list.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("All", "*.*")],
            initialfile=suggest_export_filename("json"),
        )
        if path:
            ok, err = export_to_json(data, path)
            if ok:
                log_message(f"Exported JSON: {path}")
                messagebox.showinfo("OK", f"Saved to {path}")
            else:
                messagebox.showerror("Export failed", err or "Unknown error")

    def _on_close(self):
        if getattr(self, "_auto_refresh", None):
            self._auto_refresh.stop()
        self.settings["window_width"] = self.winfo_width()
        self.settings["window_height"] = self.winfo_height()
        self.settings["theme"] = ctk.get_appearance_mode()
        self.settings["lock_critical"] = self.lock_var.get()
        save_settings(self.settings)
        self.destroy()

    def _show_process_details(self, pid):
        details = get_process_details(pid)
        if not details:
            messagebox.showinfo("Process", f"Process {pid} not found or no access.")
            return
        lines = [f"{k}: {v}" for k, v in details.items()]
        messagebox.showinfo(f"Process {pid}", "\n".join(lines))

    def _apply_filter_click(self):
        data = getattr(self, "last_process_data", [])
        if data:
            self._apply_filter_and_update(data)

    def _get_filter_params(self):
        name = self.filter_entry.get().strip() if getattr(self, "filter_entry", None) else ""
        safe = getattr(self, "filter_safe_var", None)
        net = getattr(self, "filter_net_var", None)
        return (
            name,
            bool(safe and safe.get()) if safe else False,
            bool(net and net.get()) if net else False,
        )

    def _apply_filter_and_update(self, data):
        self.last_process_data = data  # keep full list for kill actions
        name, safe_only, network_only = self._get_filter_params()
        filtered = filter_processes(
            data,
            name_substring=name,
            safe_only=safe_only,
            network_only=network_only,
        )
        self._update_list(filtered)
        total = len(data)
        shown = len(filtered)
        if total != shown:
            self.status_label.configure(
                text=f"Showing {shown} of {total} processes (filter active).",
                text_color="gray",
            )
        else:
            self.status_label.configure(
                text=f"Ready. {len(data)} processes. Select row → End Process. If denied: Run as Administrator.",
                text_color="gray",
            )
        self._update_system_stats(data)  # stats on full list

    def _update_list(self, data):
        self.last_process_data = data
        for w in self.scroll.winfo_children():
            w.destroy()
        self.rows.clear()
        for item in data:
            pid, name, cpu, ram = item[0], item[1], item[2], item[3]
            critical = item[4]
            has_network = item[5] if len(item) > 5 else False
            row_color = ("#ffdddd", "#4a2020") if critical else ("gray85", "gray20")
            row = ctk.CTkFrame(self.scroll, fg_color=row_color, corner_radius=4)
            row.pack(fill="x", pady=2)
            row.bind("<Button-1>", lambda e, p=pid, c=critical: self._select(p, c))
            row.bind("<Double-1>", lambda e, p=pid: self._show_process_details(p))
            ctk.CTkLabel(row, text=str(pid), width=70, anchor="w").pack(side="left", padx=6, pady=5)
            ctk.CTkLabel(row, text=name[:32], width=200, anchor="w").pack(side="left", padx=6, pady=5)
            ctk.CTkLabel(row, text=f"{cpu:.1f}%", width=60, anchor="w").pack(side="left", padx=6, pady=5)
            ctk.CTkLabel(row, text=f"{ram:.1f}", width=70, anchor="w").pack(side="left", padx=6, pady=5)
            net_text = "Yes" if has_network else "-"
            net_color = "#3498db" if has_network else "gray"
            ctk.CTkLabel(row, text=net_text, width=40, anchor="w", text_color=net_color).pack(
                side="left", padx=4, pady=5
            )
            type_text = "Critical" if critical else "Safe"
            type_color = "#e74c3c" if critical else "#27ae60"
            ctk.CTkLabel(row, text=type_text, width=80, anchor="w", text_color=type_color).pack(
                side="left", padx=6, pady=5
            )
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, p=pid, c=critical: self._select(p, c))
                child.bind("<Double-1>", lambda e, p=pid: self._show_process_details(p))
            self.rows.append((row, pid, critical))

    def _select(self, pid, critical=False):
        self.selected_pid = pid
        self.selected_critical = critical
        for row, p, c in self.rows:
            if p == pid:
                row.configure(
                    fg_color=("gray70", "gray35") if not c else ("#ffcccc", "#5a3030")
                )
            else:
                row.configure(
                    fg_color=("#ffdddd", "#4a2020") if c else ("gray85", "gray20")
                )

    def do_kill(self):
        if self.selected_pid is None:
            messagebox.showinfo("Info", "Select a process first (click on a row).")
            return
        if getattr(self, "selected_critical", False) and self.lock_var.get():
            messagebox.showwarning(
                "Lock enabled",
                "This process is CRITICAL — do not end it or Windows may crash.\n\n"
                "Disable the lock to allow ending critical processes, or select a Safe process.",
            )
            return
        if messagebox.askyesno("Confirm", f"End process PID {self.selected_pid}?"):
            name = next((r[1] for r in (self.last_process_data or []) if r[0] == self.selected_pid), "?")
            ok, err = kill_process(self.selected_pid)
            append_ended_process(self.selected_pid, name, success=ok)
            if ok:
                self.status_label.configure(
                    text=f"Process PID {self.selected_pid} ended.", text_color="#27ae60"
                )
                messagebox.showinfo("OK", f"Process PID {self.selected_pid} ended.")
                self.refresh()
            else:
                msg = f"Could not end process. {err or 'Access denied'}. Try: Right-click app → Run as Administrator."
                self.status_label.configure(text=msg[:80] + "...", text_color="#e74c3c")
                messagebox.showerror("Access denied", msg)

    def _kill_top_ram(self):
        data = getattr(self, "last_process_data", [])
        safe = [x for x in data if not x[4]]
        by_ram = sorted(safe, key=lambda x: x[3], reverse=True)[:5]
        if not by_ram:
            messagebox.showinfo("Info", "No safe processes. Or disable the lock.")
            return
        names = [x[1] for x in by_ram]
        if not messagebox.askyesno("Confirm", f"End top {len(by_ram)} by RAM?\n\n" + "\n".join(names[:5])):
            return
        ok, fail = 0, []
        for x in by_ram:
            success, err = kill_process(x[0])
            append_ended_process(x[0], x[1], success=success)
            if success:
                ok += 1
            else:
                fail.append(f"{x[1]}: {err or 'denied'}")
        msg = f"Ended {ok} process(es)." + (
            f" Failed: {', '.join(fail[:3])}" if fail else ""
        )
        self.status_label.configure(
            text=msg[:100], text_color="#e74c3c" if fail else "#27ae60"
        )
        messagebox.showinfo("Result", msg + ("\n\nTry Run as Administrator." if fail else ""))
        self.refresh()

    def _kill_network_processes(self):
        data = getattr(self, "last_process_data", [])
        safe_net = [x for x in data if not x[4] and (x[5] if len(x) > 5 else False)]
        if not safe_net:
            messagebox.showinfo("Info", "No safe processes with network. Refresh and try again.")
            return
        if not messagebox.askyesno(
            "Confirm",
            f"End {len(safe_net)} process(es) with network?\n\n"
            + "\n".join(x[1] for x in safe_net[:10])
            + ("\n..." if len(safe_net) > 10 else ""),
        ):
            return
        ok, fail = 0, []
        for x in safe_net:
            success, err = kill_process(x[0])
            append_ended_process(x[0], x[1], success=success)
            if success:
                ok += 1
            else:
                fail.append(f"{x[1]}: {err or 'denied'}")
        msg = f"Ended {ok} process(es) with network." + (
            f" Failed: {', '.join(fail[:3])}" if fail else ""
        )
        self.status_label.configure(
            text=msg[:100], text_color="#e74c3c" if fail else "#27ae60"
        )
        messagebox.showinfo("Result", msg + ("\n\nTry Run as Administrator." if fail else ""))
        self.refresh()

    def _refresh_apps_display(self):
        for w in self.apps_listbox_frame.winfo_children():
            w.destroy()
        apps = load_apps_list()
        for i, app in enumerate(apps):
            name = app.get("name", "?") or "?"
            path = app.get("path", "") or app.get("cmd", "")
            row = ctk.CTkFrame(
                self.apps_listbox_frame, fg_color=("gray90", "gray25"), corner_radius=4
            )
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{i+1}. {name}", width=200, anchor="w").pack(
                side="left", padx=8, pady=4
            )
            ctk.CTkLabel(
                row,
                text=path[:50] + "..." if len(path) > 50 else path,
                anchor="w",
            ).pack(side="left", padx=4, pady=4)
            ctk.CTkButton(
                row,
                text="🗑",
                width=36,
                fg_color="#c0392b",
                hover_color="#a93226",
                command=lambda idx=i: self._remove_app(idx),
            ).pack(side="right", padx=4, pady=4)

    def _run_n_apps(self, n):
        apps = load_apps_list()
        for i in range(min(n, len(apps))):
            path = apps[i].get("path") or apps[i].get("cmd") or ""
            run_app(path)
        if n > len(apps):
            messagebox.showinfo(
                "Info", f"You have only {len(apps)} app(s) in the list. Add more with 'Add app'."
            )

    def _run_all_apps(self):
        apps = load_apps_list()
        if not apps:
            messagebox.showinfo("Info", "List is empty. Add apps with 'Add app'.")
            return
        for app in apps:
            path = app.get("path") or app.get("cmd") or ""
            run_app(path)
        messagebox.showinfo("OK", f"Launched {len(apps)} application(s).")

    def _add_app(self):
        path = filedialog.askopenfilename(
            title="Choose application",
            filetypes=[("Executables", "*.exe"), ("All", "*.*")],
        )
        if not path:
            return
        name = os.path.splitext(os.path.basename(path))[0]
        apps = load_apps_list()
        apps.append({"name": name, "path": path})
        save_apps_list(apps)
        self._refresh_apps_display()
        messagebox.showinfo("OK", f"Added '{name}'.")

    def _add_app_by_path(self):
        dialog = ctk.CTkInputDialog(
            text="Path or command (e.g. notepad, chrome):",
            title="Add app by path",
        )
        path = dialog.get_input()
        if not path or not path.strip():
            return
        path = path.strip()
        name = os.path.basename(path).split()[0] if path else "App"
        apps = load_apps_list()
        apps.append({"name": name, "path": path})
        save_apps_list(apps)
        self._refresh_apps_display()
        messagebox.showinfo("OK", f"Added '{name}'.")

    def _remove_app(self, index):
        apps = load_apps_list()
        if 0 <= index < len(apps):
            apps.pop(index)
            save_apps_list(apps)
            self._refresh_apps_display()


if __name__ == "__main__":
    app = ProcessMonitorApp()
    app.mainloop()

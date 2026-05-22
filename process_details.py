# -*- coding: utf-8 -*-
"""Process Monitor Pro - Detailed info for a single process (PID)."""
import os
import psutil


def get_process_details(pid):
    """
    Get detailed info for process pid.
    Returns dict or None if process not found. Keys: pid, name, status, username,
    cmdline, cwd, create_time, cpu_percent, memory_mb, num_threads, exe.
    """
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            mem = p.memory_info()
            memory_mb = mem.rss / (1024 * 1024)
            cmdline = p.cmdline()
            cmd_str = " ".join(cmdline) if cmdline else ""
            if len(cmd_str) > 500:
                cmd_str = cmd_str[:497] + "..."
            cwd = ""
            try:
                cwd = p.cwd() or ""
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            exe = ""
            try:
                exe = p.exe() or ""
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            username = ""
            try:
                username = p.username() or ""
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            create_time = 0
            try:
                create_time = p.create_time()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            return {
                "pid": pid,
                "name": p.name(),
                "status": p.status(),
                "username": username,
                "cmdline": cmd_str,
                "cwd": cwd,
                "exe": exe,
                "create_time": create_time,
                "cpu_percent": p.cpu_percent(),
                "memory_mb": round(memory_mb, 2),
                "num_threads": p.num_threads(),
            }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

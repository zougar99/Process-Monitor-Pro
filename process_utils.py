# -*- coding: utf-8 -*-
"""Process Monitor Pro - Process listing and termination."""
import time
import subprocess
import sys
import psutil

from config import CRITICAL_PROCESSES


def is_critical(name):
    """Return True if process is critical (should not be killed)."""
    return (name or "").strip().lower() in CRITICAL_PROCESSES


def get_network_pids():
    """PIDs that have network connections."""
    try:
        conns = psutil.net_connections(kind="inet")
        return {c.pid for c in conns if getattr(c, "pid", None) is not None}
    except (psutil.AccessDenied, psutil.Error):
        return set()


def get_processes():
    """Return list of (pid, name, cpu_percent, ram_mb, critical, has_network)."""
    network_pids = get_network_pids()
    result = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        try:
            pinfo = proc.info
            name = pinfo.get("name") or "?"
            pid = pinfo.get("pid")
            cpu = pinfo.get("cpu_percent")
            mem = pinfo.get("memory_info")
            if cpu is None:
                proc.cpu_percent()
                time.sleep(0.05)
                cpu = proc.cpu_percent()
            rss = (mem.rss / (1024 * 1024)) if mem else 0
            critical = is_critical(name)
            has_network = pid in network_pids
            result.append((pid, name, cpu or 0, round(rss, 2), critical, has_network))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    result.sort(key=lambda x: (x[2], x[3]), reverse=True)
    return result


def get_processes_detailed():
    """
    Return list of (pid, name, cpu_percent, ram_mb, critical, has_network, exe_path).
    Includes executable path for each process.
    """
    network_pids = get_network_pids()
    result = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "exe"]):
        try:
            pinfo = proc.info
            name = pinfo.get("name") or "?"
            pid = pinfo.get("pid")
            cpu = pinfo.get("cpu_percent")
            mem = pinfo.get("memory_info")
            exe = pinfo.get("exe") or ""
            if cpu is None:
                proc.cpu_percent()
                import time
                time.sleep(0.05)
                cpu = proc.cpu_percent()
            rss = (mem.rss / (1024 * 1024)) if mem else 0
            critical = is_critical(name)
            has_network = pid in network_pids
            result.append((pid, name, cpu or 0, round(rss, 2), critical, has_network, exe))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    result.sort(key=lambda x: (x[2], x[3]), reverse=True)
    return result


def kill_process(pid):
    """End process by PID. Returns (success, error_message)."""
    err = "Access denied"
    flags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F", "/T"],
                capture_output=True,
                timeout=5,
                creationflags=flags,
            )
            if r.returncode == 0:
                return (True, None)
            err = (r.stderr or b"").decode("utf-8", errors="ignore").strip() or "Access denied?"
        except subprocess.TimeoutExpired:
            err = "Timeout"
        except FileNotFoundError:
            err = "taskkill not found"
        except Exception as e:
            err = str(e)
    try:
        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(timeout=2)
        except psutil.TimeoutExpired:
            pass
        try:
            if p.is_running():
                p.kill()
                p.wait(timeout=1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return (True, None)
        try:
            if not p.is_running():
                return (True, None)
        except psutil.NoSuchProcess:
            return (True, None)
    except psutil.NoSuchProcess:
        return (True, None)
    except psutil.AccessDenied:
        pass
    if sys.platform == "win32":
        try:
            r = subprocess.run(
                ["taskkill", "/PID", str(pid), "/F", "/T"],
                capture_output=True,
                timeout=5,
                creationflags=flags,
            )
            if r.returncode == 0:
                return (True, None)
        except Exception:
            pass
    return (False, err)

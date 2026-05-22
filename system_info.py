# -*- coding: utf-8 -*-
"""Process Monitor Pro - System information (CPU, RAM, disk, OS)."""
import platform
import psutil


def get_cpu_count():
    """Logical CPU count."""
    try:
        return psutil.cpu_count(logical=True) or 0
    except Exception:
        return 0


def get_cpu_percent():
    """Overall CPU usage percent (blocking, ~1s)."""
    try:
        return psutil.cpu_percent(interval=0.5)
    except Exception:
        return 0.0


def get_memory_info():
    """Total and available RAM in MB. Returns (total_mb, available_mb, percent_used)."""
    try:
        v = psutil.virtual_memory()
        total_mb = v.total / (1024 * 1024)
        avail_mb = v.available / (1024 * 1024)
        return (round(total_mb, 1), round(avail_mb, 1), v.percent)
    except Exception:
        return (0, 0, 0)


def get_disk_info():
    """Main disk (C: on Windows) usage. Returns (total_gb, free_gb, percent)."""
    try:
        if platform.system() == "Windows":
            for part in psutil.disk_partitions():
                if "fixed" in part.opts and part.mountpoint.startswith("C"):
                    u = psutil.disk_usage(part.mountpoint)
                    total_gb = u.total / (1024 ** 3)
                    free_gb = u.free / (1024 ** 3)
                    return (round(total_gb, 2), round(free_gb, 2), u.percent)
        # Fallback: first partition
        part = psutil.disk_partitions()[0] if psutil.disk_partitions() else None
        if part:
            u = psutil.disk_usage(part.mountpoint)
            total_gb = u.total / (1024 ** 3)
            free_gb = u.free / (1024 ** 3)
            return (round(total_gb, 2), round(free_gb, 2), u.percent)
    except Exception:
        pass
    return (0, 0, 0)


def get_os_info():
    """OS name and version string."""
    try:
        return f"{platform.system()} {platform.release()} ({platform.machine()})"
    except Exception:
        return "Unknown"


def get_summary():
    """One dict with CPU count, memory (total/avail/percent), disk (total/free/percent), os."""
    total_mb, avail_mb, mem_pct = get_memory_info()
    total_gb, free_gb, disk_pct = get_disk_info()
    return {
        "cpu_count": get_cpu_count(),
        "memory_total_mb": total_mb,
        "memory_available_mb": avail_mb,
        "memory_percent": mem_pct,
        "disk_total_gb": total_gb,
        "disk_free_gb": free_gb,
        "disk_percent": disk_pct,
        "os": get_os_info(),
    }

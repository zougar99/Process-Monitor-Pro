# -*- coding: utf-8 -*-
"""
Process Monitor Pro - Mix Monitor.
Single entry point that mixes system info + process list + stats + top consumers.
"""
from process_utils import get_processes
from system_info import get_summary
from stats import compute_stats, top_by_ram, top_by_cpu


def get_mix_snapshot(top_n=10):
    """
    One-shot mixed monitor: system + processes + stats + top RAM/CPU.
    Returns dict:
      - system: from system_info.get_summary()
      - process_count: len(processes)
      - process_stats: from stats.compute_stats(processes)
      - top_ram: list of top_n (pid, name, cpu, ram_mb, ...)
      - top_cpu: list of top_n (pid, name, cpu, ram_mb, ...)
      - processes: full list (optional, can be large)
    """
    system = get_summary()
    processes = get_processes()
    stats = compute_stats(processes)
    return {
        "system": system,
        "process_count": len(processes),
        "process_stats": stats,
        "top_ram": top_by_ram(processes, n=top_n),
        "top_cpu": top_by_cpu(processes, n=top_n),
        "processes": processes,
    }


def get_mix_snapshot_light(top_n=10):
    """
    Lighter version: no full process list (processes key omitted).
    Use when you only need system + stats + tops.
    """
    system = get_summary()
    processes = get_processes()
    stats = compute_stats(processes)
    return {
        "system": system,
        "process_count": len(processes),
        "process_stats": stats,
        "top_ram": top_by_ram(processes, n=top_n),
        "top_cpu": top_by_cpu(processes, n=top_n),
    }


def mix_summary_text(snapshot):
    """
    Short one-line summary from a mix snapshot (from get_mix_snapshot or get_mix_snapshot_light).
    """
    s = snapshot.get("system", {})
    st = snapshot.get("process_stats", {})
    return (
        f"Processes: {snapshot.get('process_count', 0)}  |  "
        f"RAM: {st.get('total_ram_mb', 0):.0f} MB  |  "
        f"CPU: {st.get('total_cpu_percent', 0):.0f}%  |  "
        f"Memory: {s.get('memory_percent', 0):.0f}%  |  "
        f"Disk: {s.get('disk_percent', 0):.0f}%"
    )

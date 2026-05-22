# -*- coding: utf-8 -*-
"""Process Monitor Pro - Aggregate statistics from process list."""
from collections import defaultdict


def compute_stats(process_list):
    """
    process_list: list of (pid, name, cpu, ram_mb, critical, has_network).
    Returns dict: total_count, safe_count, critical_count, total_ram_mb, total_cpu,
    by_name (name -> count), network_count.
    """
    total_ram = 0.0
    total_cpu = 0.0
    safe = 0
    critical = 0
    network = 0
    by_name = defaultdict(int)
    for row in process_list:
        pid, name, cpu, ram, crit, has_net = (row[0], row[1], row[2], row[3], row[4], row[5] if len(row) > 5 else False)
        total_ram += ram or 0
        total_cpu += cpu or 0
        if crit:
            critical += 1
        else:
            safe += 1
        if has_net:
            network += 1
        by_name[name or "?"] += 1
    return {
        "total_count": len(process_list),
        "safe_count": safe,
        "critical_count": critical,
        "total_ram_mb": round(total_ram, 2),
        "total_cpu_percent": round(total_cpu, 1),
        "network_count": network,
        "by_name": dict(by_name),
    }


def top_by_ram(process_list, n=10):
    """Top n processes by RAM (MB)."""
    return sorted(process_list, key=lambda x: x[3] or 0, reverse=True)[:n]


def top_by_cpu(process_list, n=10):
    """Top n processes by CPU %."""
    return sorted(process_list, key=lambda x: x[2] or 0, reverse=True)[:n]

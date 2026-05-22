# -*- coding: utf-8 -*-
"""Process Monitor Pro - Filter process list by name, CPU, RAM, type, network."""
import re


def filter_processes(data, name_substring="", min_cpu=0, min_ram=0, safe_only=False, network_only=False):
    """
    Filter list of (pid, name, cpu, ram, critical, has_network).
    - name_substring: case-insensitive match in process name
    - min_cpu: minimum CPU %
    - min_ram: minimum RAM MB
    - safe_only: only non-critical
    - network_only: only processes with network
    """
    result = data
    name_substring = (name_substring or "").strip().lower()
    if name_substring:
        result = [r for r in result if name_substring in (r[1] or "").lower()]
    if min_cpu > 0:
        result = [r for r in result if (r[2] or 0) >= min_cpu]
    if min_ram > 0:
        result = [r for r in result if (r[3] or 0) >= min_ram]
    if safe_only:
        result = [r for r in result if not r[4]]
    if network_only:
        result = [r for r in result if len(r) > 5 and r[5]]
    return result


def filter_by_regex(data, pattern):
    """Filter by regex on process name. pattern can be str or compiled re."""
    if not pattern:
        return data
    try:
        if isinstance(pattern, str):
            pat = re.compile(pattern, re.IGNORECASE)
        else:
            pat = pattern
        return [r for r in data if pat.search(r[1] or "")]
    except re.error:
        return data

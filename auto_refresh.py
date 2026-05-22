# -*- coding: utf-8 -*-
"""Process Monitor Pro - Optional auto-refresh timer for process list."""
import threading
import time


class AutoRefreshTimer:
    """Calls refresh_callback every interval_seconds. Start/stop from main thread preferred."""

    def __init__(self, interval_seconds, refresh_callback):
        self.interval = max(1, int(interval_seconds))
        self.callback = refresh_callback
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self.interval + 1)
        self._thread = None

    def _run(self):
        while not self._stop.is_set():
            if self._stop.wait(timeout=self.interval):
                break
            try:
                self.callback()
            except Exception:
                pass

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

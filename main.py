#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main entry point for Project 6 - Process Monitor
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from process_monitor import ProcessMonitorApp

if __name__ == '__main__':
    app = ProcessMonitorApp()
    app.mainloop()

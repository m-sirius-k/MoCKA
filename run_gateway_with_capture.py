#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run gateway with stderr/stdout capture for HAB recording audit
"""
import subprocess
import sys
import os
from pathlib import Path

# Set working directory
os.chdir(Path(__file__).parent / "gateway")

# Start gateway with output capture
print("[AUDIT] Starting Gateway with stderr/stdout capture...")
print("[AUDIT] Working directory:", os.getcwd())

process = subprocess.Popen(
    [sys.executable, "gateway.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,  # Line buffered
)

print(f"[AUDIT] Gateway PID: {process.pid}")
print("[AUDIT] Waiting 3 seconds for gateway startup...")

import time
time.sleep(3)

# Check if process is still running
if process.poll() is None:
    print("[AUDIT] Gateway started successfully")
    print("[AUDIT] Ready for test requests")
    print("[AUDIT] PID:", process.pid)

    # Keep process alive and capture output
    try:
        while process.poll() is None:
            # Non-blocking read from stderr
            line = process.stderr.readline()
            if line:
                print(f"[STDERR] {line.rstrip()}")
            line = process.stdout.readline()
            if line:
                print(f"[STDOUT] {line.rstrip()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[AUDIT] Shutting down gateway...")
        process.terminate()
        process.wait(timeout=5)
else:
    print("[ERROR] Gateway failed to start")
    stderr_output = process.stderr.read()
    stdout_output = process.stdout.read()
    print("STDERR:", stderr_output)
    print("STDOUT:", stdout_output)
    sys.exit(1)

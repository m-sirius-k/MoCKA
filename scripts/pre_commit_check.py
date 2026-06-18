import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
﻿#!/usr/bin/env python
import subprocess, sys

def run(cmd):
    return subprocess.call(cmd,shell=True)

if run("python runtime/security_gate.py") != 0:
    print("BLOCK: security violation")
    sys.exit(1)

print("PRE-COMMIT OK")

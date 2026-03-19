#!/usr/bin/env python
import subprocess, sys

def run(cmd):
    return subprocess.call(cmd,shell=True)

if run("python runtime/security_gate.py") != 0:
    print("BLOCK: security violation")
    sys.exit(1)

print("PRE-COMMIT OK")

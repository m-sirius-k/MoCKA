#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug orchestra_one_host.py --test mode"""

import json
import subprocess
import sys
from pathlib import Path

orchestra_path = Path(__file__).parent.parent / \
    "PlanningCaliber" / "workshop" / "Orchestra_Project" / \
    "orchestra_one" / "orchestra_one_host.py"

request_msg = {'type': 'RUN_ORCHESTRA', 'prompt': 'test'}

print("=" * 80)
print("DEBUG: orchestra_one_host.py --test mode")
print("=" * 80)
print()

print(f"Path: {orchestra_path}")
print(f"Exists: {orchestra_path.exists()}")
print(f"Request: {request_msg}")
print()

try:
    print("Executing subprocess...")
    result = subprocess.run(
        [sys.executable, str(orchestra_path), "--test"],
        input=json.dumps(request_msg, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
        timeout=60,
    )

    print(f"Return code: {result.returncode}")
    print()

    stdout_text = result.stdout.decode("utf-8", errors="replace")
    stderr_text = result.stderr.decode("utf-8", errors="replace")

    print(f"STDOUT ({len(stdout_text)} bytes):")
    print("-" * 80)
    print(stdout_text[:1000])
    print()

    print(f"STDERR ({len(stderr_text)} bytes):")
    print("-" * 80)
    print(stderr_text[:1000])
    print()

    # Try to parse JSON from stdout
    if stdout_text.strip():
        try:
            parsed = json.loads(stdout_text)
            print("Parsed JSON:")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

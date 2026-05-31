"""
CI用: test_field/reports/last_run.json を読んでPASS率を検証する。
PowerShell上でのインライン python -c のエスケープ問題を回避するため外部スクリプト化。
"""
import json
import sys
from pathlib import Path

p = Path("test_field/reports/last_run.json")
if not p.exists():
    print("last_run.json not found")
    sys.exit(1)

r = json.loads(p.read_text(encoding="utf-8"))
total = r["total"]
passed = r["passed"]
failed = r["failed"]

print(f"vasAI Regression: {passed}/{total} PASS")

if failed > 0:
    print(f"REGRESSION DETECTED: {failed} failure(s)")
    for d in r.get("details", []):
        if not d.get("success"):
            print(f"  FAIL: {d['id']} {d['name']}")
    sys.exit(1)

print("All scenarios PASS - L4.9 Proof of Reproducibility: VERIFIED")
sys.exit(0)

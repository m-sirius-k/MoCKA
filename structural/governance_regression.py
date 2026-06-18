import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 — Governance Regression Runner

Governance Layer v1.1 Baselineを基準として、以降の変更が
品質基準を維持していることをワンコマンドで確認する。

実行順:
  1. Governance Integration Test (gl_integration_test.py)
  2. Dogfooding (dogfood_run.py)
  3. Audit (governance_audit_check.py)
  4. Summary生成 (GOVERNANCE_REGRESSION_SUMMARY.md)

途中でFAILした場合は即終了する(exit code 1)。

使い方:
  python governance_regression.py
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STRUCTURAL_DIR = Path(__file__).resolve().parent
BASELINE_VERSION = "Governance Layer v1.1"
BASELINE_COMMIT = "e35724b97b7abcdc68ce5df5574537581faf0dfb"
BASELINE_EVENT = "E20260613_067"

STEPS = [
    ("Integration Test", "gl_integration_test.py"),
    ("Dogfood", "dogfood_run.py"),
    ("Audit", "governance_audit_check.py"),
]


def run_step(script_name):
    proc = subprocess.run(
        [sys.executable, script_name],
        cwd=STRUCTURAL_DIR,
        capture_output=True,
        text=True,
    )
    passed = proc.returncode == 0
    return passed, proc.stdout + proc.stderr


def main():
    print("=" * 29)
    print("Governance Regression")
    print("=" * 29)
    print()

    results = {}
    overall = "PASS"

    for label, script in STEPS:
        passed, output = run_step(script)
        status = "PASS" if passed else "FAIL"
        results[label] = status

        print(label)
        print(status)
        print()

        if not passed:
            overall = "FAIL"
            print("--- output ---")
            print(output)
            break

    print("Overall")
    print(overall)

    write_summary(results, overall)

    if overall != "PASS":
        raise SystemExit(1)


def write_summary(results, overall):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "# Governance Summary",
        "",
        f"- 実施日時: {timestamp}",
        f"- Version: {BASELINE_VERSION}",
        f"- Commit: {BASELINE_COMMIT}",
        f"- Event: {BASELINE_EVENT}",
        "",
        f"- Integration: {results.get('Integration Test', 'SKIPPED')}",
        f"- Dogfood: {results.get('Dogfood', 'SKIPPED')}",
        f"- Audit: {results.get('Audit', 'SKIPPED')}",
        "",
        f"## Overall {overall}",
        "",
    ]

    summary_path = STRUCTURAL_DIR / "GOVERNANCE_REGRESSION_SUMMARY.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()

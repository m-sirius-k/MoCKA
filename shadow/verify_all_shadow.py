#!/usr/bin/env python3
# Shadow verifier (diagnostic-only).
# Constraints:
# - Read-only: never modify Primary artifacts.
# - No pass-through: outputs diagnostics only.
# - No repair actions.

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(msg: str, code: int = 1) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def safe_write_report(out_path: Path, report_obj: dict) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report_obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_python(script_path: Path, cwd: Path, extra_args: list[str]) -> dict:
    cmd = [sys.executable, str(script_path)] + extra_args
    p = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    stdout = (p.stdout or "").strip()
    stderr = (p.stderr or "").strip()
    return {
        "cmd": cmd,
        "cwd": str(cwd),
        "returncode": p.returncode,
        "stdout": stdout,
        "stderr": stderr,
    }


def resolve_script(primary_root: Path, p: str) -> Path:
    sp = Path(p)
    if not sp.is_absolute():
        sp = (primary_root / sp).resolve()
    else:
        sp = sp.resolve()
    if not sp.exists():
        fail(f"SCRIPT_NOT_FOUND: {sp}")
    return sp


def main() -> int:
    ap = argparse.ArgumentParser(description="MoCKA Shadow verifier (diagnostic-only).")
    ap.add_argument(
        "--primary-root",
        default=".",
        help="Primary repo root (read-only). Default: current directory.",
    )
    ap.add_argument(
        "--verify-all-v4",
        required=True,
        help="Path to verify_all_v4.py (absolute or relative to primary-root).",
    )
    ap.add_argument(
        "--out",
        default="shadow/reports/shadow_diagnostic_report.json",
        help="Output report path.",
    )
    args = ap.parse_args()

    primary_root = Path(args.primary_root).resolve()
    out_path = Path(args.out).resolve()

    if not (primary_root / ".git").exists():
        fail(f"PRIMARY_ROOT_NOT_GIT_REPO: {primary_root}")

    verify_all_v4 = resolve_script(primary_root, args.verify_all_v4)

    checks = []

    v4_run = run_python(verify_all_v4, cwd=primary_root, extra_args=[])
    checks.append(
        {
            "name": "primary_verify_all_v4",
            "type": "subprocess",
            "script": str(verify_all_v4),
            "result": v4_run,
        }
    )

    status = "PASS" if v4_run["returncode"] == 0 else "FAIL"

    report = {
        "shadow_verifier": "verify_all_shadow.py",
        "mode": "diagnostic_only",
        "generated_at_utc": utc_now_iso(),
        "primary_root": str(primary_root),
        "checks": checks,
        "summary": {
            "status": status,
            "notes": [
                "Shadow runs Primary verifiers in read-only mode and records diagnostics.",
                "Shadow does not repair or modify Primary artifacts.",
            ],
        },
    }

    safe_write_report(out_path, report)
    print(f"SHADOW_REPORT_WRITTEN: {out_path}")
    print(f"SHADOW_SUMMARY_STATUS: {status}")
    return 0 if status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

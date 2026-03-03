#!/usr/bin/env python3
# Shadow verifier (diagnostic-only).
# - Read-only: never modify Primary artifacts.
# - No pass-through: outputs diagnostics only.
# - No repair actions.
#
# Hard safety:
# - Detects working-tree mutation during run and fails if any is observed.
#
# Diagnostic evolution:
# - Classifies failure lines into FAIL_KIND vocabulary (no auto-fix).

import argparse
import json
import re
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


def run_cmd(cmd: list[str], cwd: Path) -> dict:
    p = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True)
    return {
        "cmd": cmd,
        "cwd": str(cwd),
        "returncode": p.returncode,
        "stdout": (p.stdout or ""),
        "stderr": (p.stderr or ""),
    }


def run_python(script_path: Path, cwd: Path, extra_args: list[str]) -> dict:
    cmd = [sys.executable, str(script_path)] + extra_args
    return run_cmd(cmd, cwd)


def resolve_script(primary_root: Path, p: str) -> Path:
    sp = Path(p)
    if not sp.is_absolute():
        sp = (primary_root / sp).resolve()
    else:
        sp = sp.resolve()
    if not sp.exists():
        fail(f"SCRIPT_NOT_FOUND: {sp}")
    return sp


def git_porcelain(primary_root: Path) -> str:
    r = run_cmd(["git", "status", "--porcelain"], primary_root)
    if r["returncode"] != 0:
        fail("GIT_STATUS_FAILED")
    return r["stdout"]


def classify_fail_kind(line: str) -> str:
    u = line.upper()

    if "INSUFFICIENT SIGNATURE" in u:
        return "insufficient_signatures"
    if "DUPLICATE SIGNER" in u:
        return "duplicate_signer"
    if "INVALID SIGNATURE" in u:
        return "invalid_signature"
    if "EXPECTED_FAIL_BUT_PASSED" in u:
        return "unexpected_pass"
    if "CANONICAL" in u and ("TAMPER" in u or "DETERMIN" in u):
        return "canonical_violation"
    if "REVOK" in u and ("USED" in u or "ENFORC" in u or "REVOKED" in u):
        return "revocation_related"
    if "REGISTRY" in u and "FAIL" in u:
        return "registry_failure"

    return "unknown"


def extract_v4_diagnostics(stdout: str, stderr: str) -> dict:
    lines_out = [ln.rstrip("\r\n") for ln in stdout.splitlines()]
    lines_err = [ln.rstrip("\r\n") for ln in stderr.splitlines()]

    fails = []
    passes = []
    infos = []

    for ln in lines_out:
        u = ln.upper()
        if "FAIL" in u:
            fails.append(ln)
        elif "PASS" in u or "OK" in u:
            passes.append(ln)
        else:
            if ln.strip():
                infos.append(ln)

    err_nonempty = [ln for ln in lines_err if ln.strip()]

    fail_kinds = []
    fail_kind_counts = {}

    for ln in fails:
        k = classify_fail_kind(ln)
        fail_kinds.append({"kind": k, "line": ln})
        fail_kind_counts[k] = fail_kind_counts.get(k, 0) + 1

    unexpected_pass_count = fail_kind_counts.get("unexpected_pass", 0)

    # Heuristic: identify whether fails are expected
    # If output contains "(expected)" on fail lines, treat as expected tests unless unexpected_pass appears.
    expected_fail_lines = [ln for ln in fails if "(expected" in ln.lower()]
    expected_fail_count = len(expected_fail_lines)

    return {
        "stdout_lines": len(lines_out),
        "stderr_lines": len(lines_err),
        "pass_markers": passes[:50],
        "fail_markers": fails[:50],
        "info_head": infos[:50],
        "stderr_head": err_nonempty[:50],
        "fail_kinds": fail_kinds[:100],
        "fail_kind_counts": fail_kind_counts,
        "expected_fail_count": expected_fail_count,
        "unexpected_pass_count": unexpected_pass_count,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="MoCKA Shadow verifier (diagnostic-only).")
    ap.add_argument("--primary-root", default=".", help="Primary repo root (read-only).")
    ap.add_argument(
        "--verify-all-v4",
        required=True,
        help="Path to verify_all_v4.py (absolute or relative to primary-root).",
    )
    ap.add_argument("--out", default="shadow/reports/shadow_diagnostic_report.json")
    args = ap.parse_args()

    primary_root = Path(args.primary_root).resolve()
    out_path = Path(args.out).resolve()

    if not (primary_root / ".git").exists():
        fail(f"PRIMARY_ROOT_NOT_GIT_REPO: {primary_root}")

    verify_all_v4 = resolve_script(primary_root, args.verify_all_v4)

    pre_porcelain = git_porcelain(primary_root).strip()

    v4_run = run_python(verify_all_v4, cwd=primary_root, extra_args=[])
    diag = extract_v4_diagnostics(v4_run["stdout"], v4_run["stderr"])
    v4_status = "PASS" if v4_run["returncode"] == 0 else "FAIL"

    post_porcelain = git_porcelain(primary_root).strip()
    mutation_detected = (pre_porcelain != post_porcelain)

    # Overall status logic:
    # - FAIL if verifier returncode != 0
    # - FAIL if mutation detected
    # - PASS otherwise
    overall_status = "PASS"
    if v4_status != "PASS":
        overall_status = "FAIL"
    if mutation_detected:
        overall_status = "FAIL"

    report = {
        "shadow_verifier": "verify_all_shadow.py",
        "mode": "diagnostic_only",
        "generated_at_utc": utc_now_iso(),
        "primary_root": str(primary_root),
        "checks": [
            {
                "name": "working_tree_immutability_check",
                "type": "git_status_porcelain",
                "pre": pre_porcelain,
                "post": post_porcelain,
                "mutation_detected": mutation_detected,
            },
            {
                "name": "primary_verify_all_v4",
                "type": "subprocess",
                "script": str(verify_all_v4),
                "result": {
                    "cmd": v4_run["cmd"],
                    "cwd": v4_run["cwd"],
                    "returncode": v4_run["returncode"],
                },
                "diagnostics": diag,
            },
        ],
        "summary": {
            "status": overall_status,
            "v4_status": v4_status,
            "mutation_detected": mutation_detected,
            "fail_kind_counts": diag.get("fail_kind_counts", {}),
            "expected_fail_count": diag.get("expected_fail_count", 0),
            "unexpected_pass_count": diag.get("unexpected_pass_count", 0),
            "notes": [
                "Shadow executes Primary verifier read-only and records diagnostics only.",
                "Shadow performs no mutation and no repair.",
                "If working tree changes during run, Shadow fails (immutability breach).",
                "FAIL_KIND is a diagnostic vocabulary, not an enforcement mechanism.",
            ],
        },
    }

    safe_write_report(out_path, report)
    print(f"SHADOW_REPORT_WRITTEN: {out_path}")
    print(f"SHADOW_SUMMARY_STATUS: {overall_status}")
    print(f"SHADOW_MUTATION_DETECTED: {mutation_detected}")
    return 0 if overall_status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

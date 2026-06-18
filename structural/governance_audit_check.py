import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
MoCKA 3.0 — Governance Layer v1.1 Baseline Audit Check

GL_AUDIT_REPORT.md v1.1で確定した不変条件を静的検査し、
Baseline以降の変更でこれらが崩れていないことを確認する。

判定ロジック・GLロジック自体は変更しない（検査のみ）。
"""

import re
from pathlib import Path

STRUCTURAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = STRUCTURAL_DIR.parent


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    pipeline_src = (STRUCTURAL_DIR / "governance_pipeline.py").read_text(encoding="utf-8")
    server_src = (REPO_ROOT / "mocka_mcp_server.py").read_text(encoding="utf-8")
    thinking_mode_src = (STRUCTURAL_DIR / "thinking_mode.py").read_text(encoding="utf-8")
    audit_report = (STRUCTURAL_DIR / "GL_AUDIT_REPORT.md").read_text(encoding="utf-8")

    # #1 Fail Closed: mocka_mcp_server must guard execute_tool with Fail Closed
    results.append(check(
        "Fail Closed: mocka_mcp_server references GL_FAIL_CLOSED / READ_ONLY_TOOLS",
        "GL_FAIL_CLOSED" in server_src and "READ_ONLY_TOOLS" in server_src,
    ))

    # #2 GL6 enforcement: allowed must depend on checklist.ok
    results.append(check(
        "GL6 enforcement: GovernanceDecision.allowed depends on checklist.ok",
        re.search(r"allowed\s*=.*checklist[_.]ok", pipeline_src) is not None,
    ))

    # #3 GL3 word-boundary keyword matching
    results.append(check(
        "GL3 word-boundary: detect_mode uses \\b regex matching",
        r"\b" in thinking_mode_src and "re." in thinking_mode_src,
    ))

    # #4 GL7 Default Deny: READ_ONLY_TOOLS allowlist (not WRITE_TOOLS-only governance)
    results.append(check(
        "GL7 Default Deny: READ_ONLY_TOOLS defined in governance_pipeline",
        "READ_ONLY_TOOLS" in pipeline_src,
    ))

    # #5 Audit report records v1.1 overall PASS
    results.append(check(
        "GL_AUDIT_REPORT.md records v1.1 overall PASS",
        "総合判定(v1.1適用後)" in audit_report and "PASS" in audit_report.split("総合判定(v1.1適用後)")[1][:50],
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

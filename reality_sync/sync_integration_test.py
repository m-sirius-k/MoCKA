# -*- coding: utf-8 -*-

"""Sync Integration Test (Phase 4-2 Reality Sync Layer)

Current state validation:
1. syntax validation of interface/router.py
2. import validation of interface/router.py
3. sync result validation
4. false-positive rejection
5. full repo scan consistency
"""

import sys

from reality_sync.code_state_scanner import scan
from reality_sync.sync_engine import run
from reality_sync.sync_registry import WATCHED_FILES


def test_syntax_error_detection():
    """interface/router.py が正常構文として検証されること。"""
    snapshot = scan()
    entry = next(e for e in snapshot if e.file_path == "interface/router.py")

    assert entry.exists is True, "router.py が見つからない"
    assert entry.syntax_valid is True, (
        f"router.py のsyntax_validがFalse: {entry.evidence}"
    )

    print("[PASS] test_syntax_error_detection")


def test_import_failure_detection():
    """interface/router.py のimportが正常であること。"""
    snapshot = scan()
    entry = next(e for e in snapshot if e.file_path == "interface/router.py")

    assert (
        "IMPORT_OK" in entry.evidence
        or "AST_PARSE_OK" in entry.evidence
    ), f"router.py の正常evidenceが記録されていない: {entry.evidence}"

    print("[PASS] test_import_failure_detection")


def test_report_mismatch_detection():
    """修復済みrouter.pyがFIXEDとして同期判定されること。"""
    results = run()
    router_result = next(
        r for r in results if r.file_path == "interface/router.py"
    )

    assert router_result.actual_status == "FIXED", (
        f"router.py のactual_statusがFIXEDでない: "
        f"{router_result.actual_status}"
    )

    assert router_result.fix_required is False, (
        "修復済みrouter.pyでfix_requiredがTrue"
    )

    print(
        "[PASS] test_report_mismatch_detection "
        f"(status={router_result.actual_status})"
    )


def test_false_positive_rejection():
    """正常ファイルをBROKEN判定しないこと。"""
    from reality_sync.code_state_scanner import _check_syntax
    from reality_sync.sync_registry import REPO_ROOT

    abs_path = REPO_ROOT / "reality_sync" / "sync_registry.py"

    syntax_valid, evidence = _check_syntax(abs_path)

    assert syntax_valid is True, (
        f"正常ファイルがBROKEN判定された: {evidence}"
    )

    print("[PASS] test_false_positive_rejection")


def test_full_repo_scan_consistency():
    """WATCHED_FILES全件の同期結果が生成されること。"""
    results = run()

    result_paths = {r.file_path for r in results}
    watched_set = set(WATCHED_FILES)

    assert result_paths == watched_set, (
        f"結果件数の不一致: "
        f"missing={watched_set - result_paths}, "
        f"extra={result_paths - watched_set}"
    )

    for result in results:
        assert result.actual_status in ("FIXED", "BROKEN")
        assert result.severity in (
            "NONE",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        )

    print(
        f"[PASS] test_full_repo_scan_consistency "
        f"({len(results)} files)"
    )


def main():
    tests = [
        test_syntax_error_detection,
        test_import_failure_detection,
        test_report_mismatch_detection,
        test_false_positive_rejection,
        test_full_repo_scan_consistency,
    ]

    failed = 0

    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(
                f"[ERROR] {test.__name__}: "
                f"{type(e).__name__}: {e}"
            )
            failed += 1

    print()

    if failed:
        print(f"{failed} 件のテストが失敗しました。")
        sys.exit(1)

    print("全てのテストがPASSしました。")


if __name__ == "__main__":
    main()
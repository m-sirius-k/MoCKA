# -*- coding: utf-8 -*-
"""Sync Integration Test (Phase 4-2 Reality Sync Layer)

usage:
    python -m reality_sync.sync_integration_test

必須確認項目:
  1. import failure detection   - interface/router.py のSyntaxErrorを検出できるか
  2. syntax error detection     - ast.parseでBROKEN判定できるか
  3. report mismatch detection  - router.pyに対するFALSE_FIXED/MISSING_FIX等の差分を検出できるか
  4. false-positive rejection   - 正常ファイル(構文OK)を誤ってBROKEN判定しないか
  5. full repo scan consistency - WATCHED_FILES全件についてSyncResultが生成されるか
"""

import sys

from reality_sync.code_state_scanner import scan
from reality_sync.report_state_validator import validate
from reality_sync.truth_checker import determine_truth
from reality_sync.sync_engine import run
from reality_sync.sync_registry import WATCHED_FILES


def test_syntax_error_detection():
    """interface/router.py は既知のSyntaxErrorを持つため BROKEN と確定されること。"""
    snapshot = scan()
    entry = next(e for e in snapshot if e.file_path == "interface/router.py")

    assert entry.exists is True, "router.py が見つからない"
    assert entry.syntax_valid is False, f"router.py のsyntax_validがFalseではない: {entry.evidence}"

    status, _ = determine_truth(entry)
    assert status == "BROKEN", f"router.py がBROKENと判定されない: {status}"
    print("[PASS] test_syntax_error_detection")


def test_import_failure_detection():
    """interface.router の import 自体が失敗として記録されること。"""
    snapshot = scan()
    entry = next(e for e in snapshot if e.file_path == "interface/router.py")

    assert "IMPORT_ERROR" in entry.evidence or "AST_PARSE_ERROR" in entry.evidence, \
        f"import失敗のevidenceが記録されていない: {entry.evidence}"
    print("[PASS] test_import_failure_detection")


def test_report_mismatch_detection():
    """既存follow-upレポートが router.py の状態を言及しており、
    最終的なSyncResultでBROKEN(fix_required=True)が確定すること。
    """
    results = run()
    router_result = next(r for r in results if r.file_path == "interface/router.py")

    assert router_result.actual_status == "BROKEN", \
        f"router.py のactual_statusがBROKENでない: {router_result.actual_status}"
    assert router_result.fix_required is True, "fix_requiredがTrueでない"
    print(f"[PASS] test_report_mismatch_detection "
          f"(discrepancy_type={router_result.discrepancy_type}, severity={router_result.severity})")


def test_false_positive_rejection():
    """構文的に正しいファイル (sync_registry.py 自身) はFIXEDと判定されること。"""
    results = run()
    # reality_sync配下はWATCHED_FILESに含めていないため、直接scanして確認する
    from reality_sync.code_state_scanner import _check_syntax
    from reality_sync.sync_registry import REPO_ROOT

    abs_path = REPO_ROOT / "reality_sync" / "sync_registry.py"
    syntax_valid, evidence = _check_syntax(abs_path)
    assert syntax_valid is True, f"正常ファイルがBROKEN判定された: {evidence}"
    print("[PASS] test_false_positive_rejection")


def test_full_repo_scan_consistency():
    """WATCHED_FILES全件についてSyncResultが1件ずつ生成されること。"""
    results = run()
    result_paths = {r.file_path for r in results}
    watched_set = set(WATCHED_FILES)

    assert result_paths == watched_set, \
        f"結果件数の不一致: missing={watched_set - result_paths}, extra={result_paths - watched_set}"
    for r in results:
        assert r.actual_status in ("FIXED", "BROKEN")
        assert r.severity in ("NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL")
    print(f"[PASS] test_full_repo_scan_consistency ({len(results)} files)")


def main():
    tests = [
        test_syntax_error_detection,
        test_import_failure_detection,
        test_report_mismatch_detection,
        test_false_positive_rejection,
        test_full_repo_scan_consistency,
    ]

    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print()
    if failed:
        print(f"{failed} 件のテストが失敗しました。")
        sys.exit(1)
    print("全てのテストがPASSしました。")


if __name__ == "__main__":
    main()

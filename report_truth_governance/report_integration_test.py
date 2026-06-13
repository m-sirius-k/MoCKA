# -*- coding: utf-8 -*-
"""Report Integration Test (Phase 4-3 Report Truth Governance Layer)

usage:
    python -m report_truth_governance.report_integration_test

必須確認項目:
  1. multi-report conflict detection - 複数レポート間の不一致を検出できるか
  2. false FIX detection             - "FIXED"主張 vs 実態BROKEN を検出できるか
  3. outdated report detection       - 古いレポートのFIXED主張をOUTDATEDとして検出できるか
  4. evidence mismatch handling       - evidence不在ファイルをNO_EVIDENCE/BROKENとして扱えるか
  5. arbitration correctness          - 全Conflictがresolved=Trueかつtruth_state優先で解決されるか
"""

import sys

from report_truth_governance.report_pipeline import run


def test_multi_report_conflict_detection():
    results, _, _ = run()
    inter = [r for r in results for c in r.conflicts if c.conflict_type == "INTER_REPORT"]
    assert inter, "INTER_REPORT conflictが1件も検出されない"
    print(f"[PASS] test_multi_report_conflict_detection ({len(inter)} 件)")


def test_false_fix_detection():
    results, _, _ = run()
    router = next(r for r in results if r.file_path == "interface/router.py")
    assert router.truth_state == "BROKEN", "router.pyのtruth_stateがBROKENでない"
    assert "FIXED" in router.claim_state, "router.pyに対するFIXED主張が見つからない"
    assert router.conflict_flag is True
    print("[PASS] test_false_fix_detection (interface/router.py: claim=FIXED系を含むがtruth=BROKEN)")


def test_outdated_report_detection():
    results, _, _ = run()
    outdated = [r for r in results for c in r.conflicts if c.conflict_type == "OUTDATED_CLAIM"]
    assert outdated, "OUTDATED_CLAIM conflictが1件も検出されない"
    for r in results:
        for c in r.conflicts:
            if c.conflict_type == "OUTDATED_CLAIM":
                assert c.resolved is True
    print(f"[PASS] test_outdated_report_detection ({len(outdated)} 件)")


def test_evidence_mismatch_handling():
    results, _, _ = run()
    auto_gate = next(r for r in results if r.file_path == "interface/auto_gate.py")
    assert auto_gate.truth_state == "BROKEN"
    assert "FILE_NOT_FOUND" in auto_gate.evidence
    print("[PASS] test_evidence_mismatch_handling (interface/auto_gate.py -> FILE_NOT_FOUND/BROKEN)")


def test_arbitration_correctness():
    results, statuses, _ = run()
    for r in results:
        for c in r.conflicts:
            assert c.resolved is True, f"未解決conflictが残存: {r.file_path} {c}"
            assert c.resolution, "resolution文字列が空"
        # governance: 全conflict resolved -> PASS
        assert statuses[r.file_path] == "PASS", f"{r.file_path} のgovernance_statusがFAIL"
    print(f"[PASS] test_arbitration_correctness ({len(results)} files, all governance PASS)")


def main():
    tests = [
        test_multi_report_conflict_detection,
        test_false_fix_detection,
        test_outdated_report_detection,
        test_evidence_mismatch_handling,
        test_arbitration_correctness,
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
        print(f"{failed} tests failed.")
        sys.exit(1)
    print("ALL TESTS PASSED.")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Report Conflict Test (Phase 4-3 Report Truth Governance Layer)

usage:
    python -m report_truth_governance.report_conflict_test

report_integration_test.py がパイプライン全体の正しさを確認するのに対し、
本モジュールは Conflict 分類体系の網羅性 ("conflict完全検出") を確認する。
合成データ(synthetic ReportClaim/Evidence)を用いて、各 conflict_type が
report_conflict_detector / report_arbitrator によって正しく検出・解決される
ことを単体で検証する。
"""

import sys

from report_truth_governance.report_claim_model import ReportClaim, ReportClaimSet, Evidence
from report_truth_governance.report_conflict_detector import detect
from report_truth_governance.report_arbitrator import arbitrate


def _evidence_map(file_path, truth_status, detail="synthetic"):
    return {
        file_path: [
            Evidence(file_path=file_path, source="code_state_scanner", status=truth_status, detail=detail),
            Evidence(file_path=file_path, source="reality_sync.sync_engine", status=truth_status, detail=detail),
        ]
    }


def test_intra_report_conflict():
    """同一レポート内でFIXEDとBROKENの両主張 -> INTRA_REPORT検出"""
    fp = "synthetic/intra.py"
    cs = ReportClaimSet(claims=[
        ReportClaim(fp, "report_A.md", 10, "FIXED", "L10: 修正済み"),
        ReportClaim(fp, "report_A.md", 50, "BROKEN", "L50: FAIL"),
    ])
    conflicts = detect(fp, cs, "BROKEN")
    types = [c.conflict_type for c in conflicts]
    assert "INTRA_REPORT" in types, f"INTRA_REPORT未検出: {types}"
    print("[PASS] test_intra_report_conflict")


def test_inter_report_conflict():
    """report_A=FIXED, report_B=BROKEN -> INTER_REPORT検出"""
    fp = "synthetic/inter.py"
    cs = ReportClaimSet(claims=[
        ReportClaim(fp, "report_A.md", 5, "FIXED", "修正済み"),
        ReportClaim(fp, "report_B.md", 7, "BROKEN", "FAIL"),
    ])
    conflicts = detect(fp, cs, "BROKEN")
    types = [c.conflict_type for c in conflicts]
    assert "INTER_REPORT" in types, f"INTER_REPORT未検出: {types}"
    print("[PASS] test_inter_report_conflict")


def test_claim_vs_truth_conflict():
    """単一レポートがFIXEDと主張、truthはBROKEN -> CLAIM_VS_TRUTH検出"""
    fp = "synthetic/claim_vs_truth.py"
    cs = ReportClaimSet(claims=[
        ReportClaim(fp, "report_A.md", 1, "FIXED", "修正済み"),
    ])
    conflicts = detect(fp, cs, "BROKEN")
    types = [c.conflict_type for c in conflicts]
    assert "CLAIM_VS_TRUTH" in types, f"CLAIM_VS_TRUTH未検出: {types}"
    print("[PASS] test_claim_vs_truth_conflict")


def test_outdated_claim_conflict():
    """単一レポートがFIXEDと主張、truthはBROKEN -> OUTDATED_CLAIMも併発検出"""
    fp = "synthetic/outdated.py"
    cs = ReportClaimSet(claims=[
        ReportClaim(fp, "report_old.md", 1, "FIXED", "修正済み(過去時点)"),
    ])
    conflicts = detect(fp, cs, "BROKEN")
    types = [c.conflict_type for c in conflicts]
    assert "OUTDATED_CLAIM" in types, f"OUTDATED_CLAIM未検出: {types}"
    print("[PASS] test_outdated_claim_conflict")


def test_no_conflict_when_aligned():
    """claimとtruthが一致する場合は conflict が生成されないこと"""
    fp = "synthetic/aligned.py"
    cs = ReportClaimSet(claims=[
        ReportClaim(fp, "report_A.md", 1, "FIXED", "修正済み"),
        ReportClaim(fp, "report_B.md", 1, "FIXED", "PASS"),
    ])
    conflicts = detect(fp, cs, "FIXED")
    assert conflicts == [], f"一致しているのにconflictが生成された: {conflicts}"
    print("[PASS] test_no_conflict_when_aligned")


def test_arbitrator_resolves_all_types():
    """report_conflict_detectorが生成する全conflict_typeをarbitrateできること"""
    fp = "synthetic/all_types.py"
    cs = ReportClaimSet(claims=[
        ReportClaim(fp, "report_A.md", 1, "FIXED", "修正済み"),
        ReportClaim(fp, "report_A.md", 2, "BROKEN", "FAIL"),
        ReportClaim(fp, "report_B.md", 1, "BROKEN", "FAIL"),
    ])
    truth = "BROKEN"
    conflicts = detect(fp, cs, truth)
    evidence_map = _evidence_map(fp, truth)

    assert conflicts, "conflictが生成されない"
    for c in conflicts:
        resolved = arbitrate(c, evidence_map, truth)
        assert resolved.resolved is True
        assert resolved.resolution
        assert truth in resolved.resolution
    print(f"[PASS] test_arbitrator_resolves_all_types ({len(conflicts)} 件 全resolved)")


def main():
    tests = [
        test_intra_report_conflict,
        test_inter_report_conflict,
        test_claim_vs_truth_conflict,
        test_outdated_claim_conflict,
        test_no_conflict_when_aligned,
        test_arbitrator_resolves_all_types,
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
    print("ALL CONFLICT TESTS PASSED.")


if __name__ == "__main__":
    main()

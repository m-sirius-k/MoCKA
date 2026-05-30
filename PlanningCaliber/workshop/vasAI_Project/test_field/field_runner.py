"""
vasAI 実装模擬試験 全シナリオ一括実行エンジン (Phase 6)
実行: python test_field/field_runner.py
目標: 18/18 PASS — L4.9 Proof of Reproducibility
"""
import os
import sys
import time
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from scenarios import (
    scenario_00_why_vasai,
    scenario_01_basic,
    scenario_02_shadow,
    scenario_03_caliber,
    scenario_04_governance,
    scenario_05_stress,
    scenario_06_hostile,
    scenario_07_continuity,
    scenario_08_multidept,
    scenario_09_reproducibility,
    scenario_10_auditor,
    scenario_11_fault_injection,
    scenario_12_business_value,
    scenario_13_evidence,
    scenario_14_phi,
    scenario_15_180day_org,
    scenario_16_intentional_break,
    scenario_17_failure_dna,
)
from operation_report_generator import generate_operation_report
from institutional_report_generator import generate_institutional_report

SCENARIOS = [
    # Phase 1
    ("SCENARIO-01", "基本記録・監査",                  scenario_01_basic),
    ("SCENARIO-02", "shadow縮退・回復",                scenario_02_shadow),
    ("SCENARIO-03", "3業種caliber",                   scenario_03_caliber),
    ("SCENARIO-04", "Human Gate",                     scenario_04_governance),
    # Phase 2
    ("SCENARIO-00", "なぜvasAIが必要か",               scenario_00_why_vasai),
    ("SCENARIO-05", "負荷3段階（1K/10K/100K）",        scenario_05_stress),
    ("SCENARIO-06", "Hostile Environment Test",       scenario_06_hostile),
    # Phase 3
    ("SCENARIO-07", "30日連続運用",                   scenario_07_continuity),
    ("SCENARIO-08", "マルチ部門運用",                  scenario_08_multidept),
    ("SCENARIO-09", "AI再現性",                       scenario_09_reproducibility),
    ("SCENARIO-10", "監査官試験",                     scenario_10_auditor),
    ("SCENARIO-11", "障害注入強化",                   scenario_11_fault_injection),
    ("SCENARIO-12", "経営価値",                       scenario_12_business_value),
    # Phase 4-5
    ("SCENARIO-13", "Evidence Ledger",               scenario_13_evidence),
    ("SCENARIO-14", "PHI Layer + MoCKA Bridge",      scenario_14_phi),
    ("SCENARIO-15", "180日組織運用",                  scenario_15_180day_org),
    # Phase 6 — L4.9 追加
    ("SCENARIO-16", "故意破壊試験",                   scenario_16_intentional_break),
    ("SCENARIO-17", "失敗DNA試験",                    scenario_17_failure_dna),
]


def _save_ci_result(results: list, passed: int, total: int) -> None:
    import json, subprocess
    from datetime import datetime, timezone
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True,
            cwd=str(PROJECT_ROOT)
        ).stdout.strip()
    except Exception:
        commit = "unknown"

    ci = {
        "total":     total,
        "passed":    passed,
        "failed":    total - passed,
        "pass_rate": f"{passed}/{total}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "commit":    commit,
        "details": [
            {
                "id":      sid,
                "name":    name,
                "success": result.get("success", False),
                "elapsed": round(result.get("elapsed", 0), 2),
            }
            for sid, name, result in results
        ],
    }
    out = Path(__file__).parent / "reports" / "last_run.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ci, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    print("=" * 60)
    print("  vasAI TestField Phase 6 START")
    print("  Target: 18/18 PASS -- L4.9 Proof of Reproducibility")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    results = []

    for sid, name, module in SCENARIOS:
        print(f"\n>> {sid}: {name}")

        db_file = tempfile.mktemp(suffix=".db", prefix=f"vasai_{sid.replace('-','')}_")

        import core.governance as gov
        gov._pending.clear()

        import movement.mocka_movement as mm
        mm._shadow_listeners.clear()

        start = time.time()
        try:
            result = module.run(db_path=db_file)
        except Exception as e:
            import traceback
            result = {
                "success": False, "error": str(e),
                "steps": [("UNHANDLED_ERROR", False, str(e))],
                "details": {"trace": traceback.format_exc()},
            }
        elapsed = time.time() - start
        result["elapsed"] = elapsed

        status_str = "[PASS]" if result.get("success") else "[FAIL]"
        print(f"  {status_str} ({elapsed:.2f}sec)")
        for step_name, ok, detail in result.get("steps", []):
            print(f"  {'OK' if ok else 'NG'} {step_name}: {detail}")

        try:
            Path(db_file).unlink(missing_ok=True)
        except Exception:
            pass

        results.append((sid, name, result))

    # 報告書生成
    report_path = Path(__file__).parent / "reports" / "VASAI_OPERATION_REPORT.md"
    generate_operation_report(results, report_path)

    inst_path = Path(__file__).parent / "reports" / "VASAI_INSTITUTIONAL_REPORT.md"
    generate_institutional_report(results, inst_path)

    passed = sum(1 for _, _, r in results if r.get("success"))
    total = len(results)

    # CI用 last_run.json 生成
    _save_ci_result(results, passed, total)

    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} PASS")
    print(f"  L4.9 Proof of Reproducibility: {'ACHIEVED' if passed == total else 'INCOMPLETE'}")
    print(f"  Report: {report_path}")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

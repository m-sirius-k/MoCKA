"""
vasAI 実装模擬試験 全シナリオ一括実行エンジン
実行: python test_field/field_runner.py
"""
import os
import sys
import time
import tempfile
from datetime import datetime, timezone
from pathlib import Path

# vasAI_Project をsys.pathに追加
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from scenarios import (
    scenario_01_basic,
    scenario_02_shadow,
    scenario_03_caliber,
    scenario_04_governance,
    scenario_05_stress,
)
from report_generator import generate_report

SCENARIOS = [
    ("SCENARIO-01", "基本記録・監査",          scenario_01_basic),
    ("SCENARIO-02", "shadow縮退・回復",         scenario_02_shadow),
    ("SCENARIO-03", "3業種caliber実装",         scenario_03_caliber),
    ("SCENARIO-04", "Human Gate承認フロー",     scenario_04_governance),
    ("SCENARIO-05", "負荷・整合性（1000件）",   scenario_05_stress),
]


def main():
    print("=" * 60)
    print("  vasAI 実装模擬試験 開始")
    print(f"  実行日時: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    results = []

    for sid, name, module in SCENARIOS:
        print(f"\n▶ {sid}: {name}")

        # シナリオごとに独立したDBを使用
        db_file = tempfile.mktemp(suffix=".db", prefix=f"vasai_{sid}_")

        # governance のインメモリ状態をリセット
        import core.governance as gov
        gov._pending.clear()

        start = time.time()
        try:
            result = module.run(db_path=db_file)
        except Exception as e:
            import traceback
            result = {"success": False, "error": str(e),
                      "steps": [("UNHANDLED_ERROR", False, str(e))],
                      "details": {"trace": traceback.format_exc()}}
        elapsed = time.time() - start
        result["elapsed"] = elapsed

        status_str = "✅ PASS" if result.get("success") else "❌ FAIL"
        print(f"  {status_str} ({elapsed:.2f}秒)")

        # ステップ詳細表示
        for step_name, ok, detail in result.get("steps", []):
            icon = "  ✓" if ok else "  ✗"
            print(f"  {icon} {step_name}: {detail}")

        # DBクリーンアップ
        try:
            Path(db_file).unlink(missing_ok=True)
        except Exception:
            pass

        results.append((sid, name, result))

    # 報告書生成
    report_path = Path(__file__).parent / "reports" / "VASAI_TEST_REPORT.md"
    generate_report(results, report_path)

    passed = sum(1 for _, _, r in results if r.get("success"))
    total = len(results)

    print("\n" + "=" * 60)
    print(f"  総合結果: {passed}/{total} PASS")
    print(f"  試験報告書: {report_path}")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

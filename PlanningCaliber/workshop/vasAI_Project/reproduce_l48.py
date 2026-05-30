"""
vasAI L4.9 Proof of Reproducibility — 再現スクリプト

使い方:
  git clone https://github.com/m-sirius-k/vasAI.git
  cd vasAI
  pip install -r requirements.txt
  python reproduce_l48.py

成功時:
  vasAI L4.9 Proof of Reproducibility: VERIFIED
  Reproduction Hash: sha256:xxxxxxxx
  Result saved: REPRODUCE_RESULT.md
"""
import os
import sys
import json
import time
import hashlib
import platform
import sqlite3
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
RESULT_FILE = PROJECT_ROOT / "REPRODUCE_RESULT.md"
REQUIRED_PYTHON = (3, 12)


# ─── ヘッダー表示 ───────────────────────────────────────────
def print_header() -> None:
    print("=" * 60)
    print("  vasAI L4.9 Proof of Reproducibility")
    print("  「第三者が再現できた瞬間、それは証明になる」")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)


# ─── 環境確認 ────────────────────────────────────────────────
def check_environment() -> dict:
    print("\n[1/5] 環境確認...")
    py_ver = sys.version_info
    if py_ver < REQUIRED_PYTHON:
        print(f"  ERROR: Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ が必要です (現在: {py_ver.major}.{py_ver.minor})")
        sys.exit(1)
    sqlite_ver = sqlite3.sqlite_version

    missing = []
    for pkg in ["flask", "pydantic", "dotenv"]:
        try:
            __import__(pkg if pkg != "dotenv" else "dotenv")
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"  WARNING: 以下のパッケージが見つかりません: {missing}")
        print("  pip install -r requirements.txt を実行してください")

    env_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "python": f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}",
        "sqlite": sqlite_ver,
        "hostname": platform.node(),
    }
    print(f"  OS      : {env_info['os']} {env_info['os_version'][:40]}")
    print(f"  Python  : {env_info['python']}")
    print(f"  SQLite  : {env_info['sqlite']}")
    print("  OK")
    return env_info


# ─── DB クリーン ─────────────────────────────────────────────
def clean_install() -> None:
    print("\n[2/5] DB クリーン（環境依存除去）...")
    data_dir = PROJECT_ROOT / "data"
    cleaned = 0
    if data_dir.exists():
        for db_file in data_dir.glob("*.db"):
            try:
                db_file.unlink()
                cleaned += 1
            except Exception:
                pass
    print(f"  {cleaned}件のDBファイルを削除")
    print("  OK")


# ─── 全シナリオ実行 ───────────────────────────────────────────
def run_all_scenarios() -> list:
    print("\n[3/5] 全18シナリオ実行中...")
    sys.path.insert(0, str(PROJECT_ROOT))
    sys.path.insert(0, str(PROJECT_ROOT / "test_field"))

    results = []

    try:
        from test_field.scenarios import (
            scenario_00_why_vasai, scenario_01_basic, scenario_02_shadow,
            scenario_03_caliber, scenario_04_governance, scenario_05_stress,
            scenario_06_hostile, scenario_07_continuity, scenario_08_multidept,
            scenario_09_reproducibility, scenario_10_auditor, scenario_11_fault_injection,
            scenario_12_business_value, scenario_13_evidence, scenario_14_phi,
            scenario_15_180day_org, scenario_16_intentional_break, scenario_17_failure_dna,
        )
        import core.governance as gov
        import movement.mocka_movement as mm
    except ImportError as e:
        print(f"  ERROR: インポート失敗: {e}")
        sys.exit(1)

    scenarios = [
        ("S-01", "基本記録・監査",              scenario_01_basic),
        ("S-02", "shadow縮退・回復",            scenario_02_shadow),
        ("S-03", "3業種caliber",               scenario_03_caliber),
        ("S-04", "Human Gate",                 scenario_04_governance),
        ("S-00", "なぜvasAIが必要か",           scenario_00_why_vasai),
        ("S-05", "負荷3段階",                  scenario_05_stress),
        ("S-06", "Hostile Environment",        scenario_06_hostile),
        ("S-07", "30日連続運用",               scenario_07_continuity),
        ("S-08", "マルチ部門運用",              scenario_08_multidept),
        ("S-09", "AI再現性",                   scenario_09_reproducibility),
        ("S-10", "監査官試験",                 scenario_10_auditor),
        ("S-11", "障害注入強化",               scenario_11_fault_injection),
        ("S-12", "経営価値",                   scenario_12_business_value),
        ("S-13", "Evidence Ledger",           scenario_13_evidence),
        ("S-14", "PHI Layer + MoCKA Bridge",  scenario_14_phi),
        ("S-15", "180日組織運用",              scenario_15_180day_org),
        ("S-16", "故意破壊試験",               scenario_16_intentional_break),
        ("S-17", "失敗DNA試験",                scenario_17_failure_dna),
    ]

    for sid, name, module in scenarios:
        gov._pending.clear()
        mm._shadow_listeners.clear()

        db_file = tempfile.mktemp(suffix=".db", prefix=f"repro_{sid}_")
        start = time.time()
        try:
            result = module.run(db_path=db_file)
        except Exception as e:
            import traceback
            result = {"success": False, "error": str(e), "trace": traceback.format_exc()}
        elapsed = round(time.time() - start, 2)

        ok = result.get("success", False)
        print(f"  {'PASS' if ok else 'FAIL'} {sid} {name} ({elapsed}s)")
        results.append({
            "id": sid,
            "name": name,
            "success": ok,
            "elapsed": elapsed,
            "error": result.get("error", ""),
        })
        try:
            Path(db_file).unlink(missing_ok=True)
        except Exception:
            pass

    return results


# ─── レポート生成 ─────────────────────────────────────────────
def generate_report(results: list, env_info: dict) -> dict:
    print("\n[4/5] レポート生成...")
    ts = datetime.now(timezone.utc).isoformat()
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    verdict = "VERIFIED" if passed == total else "FAILED"

    # SHA-256 再現ハッシュ（全結果を結合）
    hash_payload = json.dumps(
        [{"id": r["id"], "success": r["success"]} for r in results],
        sort_keys=True, ensure_ascii=False,
    )
    reproduction_hash = hashlib.sha256(hash_payload.encode("utf-8")).hexdigest()

    report = {
        "title": "vasAI L4.9 Proof of Reproducibility",
        "generated_at": ts,
        "environment": env_info,
        "results": results,
        "passed": passed,
        "total": total,
        "verdict": verdict,
        "hash": reproduction_hash,
    }

    # REPRODUCE_RESULT.md 生成
    lines = [
        "# vasAI L4.9 Proof of Reproducibility — 再現結果",
        "",
        f"**生成日時**: {ts}",
        f"**総合判定**: {verdict}",
        f"**結果**: {passed}/{total} PASS",
        f"**再現ハッシュ**: sha256:{reproduction_hash}",
        "",
        "## 実行環境",
        "",
        f"| 項目 | 値 |",
        f"|------|-----|",
        f"| OS | {env_info['os']} |",
        f"| OS Version | {env_info['os_version'][:60]} |",
        f"| Python | {env_info['python']} |",
        f"| SQLite | {env_info['sqlite']} |",
        f"| Hostname | {env_info['hostname']} |",
        "",
        "## シナリオ結果",
        "",
        "| ID | シナリオ | 結果 | 時間(s) |",
        "|----|---------|------|---------|",
    ]
    for r in results:
        mark = "PASS" if r["success"] else "FAIL"
        lines.append(f"| {r['id']} | {r['name']} | {mark} | {r['elapsed']} |")

    lines += [
        "",
        "## 判定",
        "",
        f"**{verdict}**: {passed}/{total} シナリオが成功",
        "",
        "## 再現ハッシュ（SHA-256）",
        "",
        f"```",
        f"sha256:{reproduction_hash}",
        f"```",
        "",
        "> このハッシュは全シナリオの合否結果から生成されます。",
        "> 同じ環境・同じコードで実行した場合、同じハッシュが生成されます。",
    ]

    RESULT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"  保存: {RESULT_FILE}")
    print("  OK")
    return report


# ─── 最終判定・終了 ───────────────────────────────────────────
def verify_and_exit(results: list, report: dict) -> None:
    print("\n[5/5] 最終判定...")
    passed = sum(1 for r in results if r["success"])
    total = len(results)

    print("\n" + "=" * 60)
    if passed == total:
        print("  vasAI L4.9 Proof of Reproducibility: VERIFIED")
        print(f"  Reproduction Hash: sha256:{report['hash']}")
        print(f"  Result: {passed}/{total} PASS")
        print(f"  Result saved: {RESULT_FILE}")
        print("=" * 60)
        sys.exit(0)
    else:
        failed = [r for r in results if not r["success"]]
        print(f"  VERIFICATION FAILED: {passed}/{total} PASS")
        for r in failed:
            print(f"  FAIL: {r['id']} {r['name']} — {r.get('error', '')[:80]}")
        print("=" * 60)
        sys.exit(1)


# ─── メイン ──────────────────────────────────────────────────
def main() -> None:
    print_header()
    env_info = check_environment()
    clean_install()
    results = run_all_scenarios()
    report = generate_report(results, env_info)
    verify_and_exit(results, report)


if __name__ == "__main__":
    main()

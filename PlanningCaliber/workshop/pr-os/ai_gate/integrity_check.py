"""
AI Gate — Integrity Check
MoCKA蓄積知識との整合性検証
Phase 1: 基本的な日付・数値・固有名詞の整合性チェック
"""
import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class IntegrityResult:
    passed: bool
    issues: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


# MoCKA固有名詞・バージョン情報（将来的にDBから読み込む）
MOCKA_FACTS = {
    "current_version": "v4",
    "project_names": ["MoCKA", "PlanningCaliber", "PR-OS", "NTP", "TSI"],
    "known_dates": {
        "mocka_v4_release": "2026",
    }
}


def check_date_consistency(text: str) -> list:
    """日付の整合性チェック（未来日付の無意識混入検出など）"""
    issues = []
    # YYYY-MM-DD 形式の日付を抽出
    dates = re.findall(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    for y, m, d in dates:
        try:
            dt = datetime(int(y), int(m), int(d))
            # 極端に過去の日付（2020年以前）をチェック
            if dt.year < 2020:
                issues.append({
                    "type": "date",
                    "severity": "warning",
                    "message": f"古い日付が含まれています: {y}-{m}-{d}"
                })
        except ValueError:
            issues.append({
                "type": "date",
                "severity": "error",
                "message": f"無効な日付: {y}-{m}-{d}"
            })
    return issues


def check_version_consistency(text: str) -> list:
    """バージョン表記の整合性チェック"""
    issues = []
    # MoCKA バージョン表記検出
    versions = re.findall(r"MoCKA\s+(v\d+(?:\.\d+)?)", text, re.IGNORECASE)
    current = MOCKA_FACTS["current_version"]
    for v in versions:
        if v.lower() != current.lower():
            issues.append({
                "type": "version",
                "severity": "warning",
                "message": f"MoCKAバージョン表記 '{v}' が現行 '{current}' と異なります。意図的な場合は無視可。"
            })
    return issues


def check_project_names(text: str) -> list:
    """固有名詞の表記ゆれ検出"""
    issues = []
    name_variants = {
        "mocka": "MoCKA",
        "planning caliber": "PlanningCaliber",
        "pr os": "PR-OS",
    }
    text_lower = text.lower()
    for variant, correct in name_variants.items():
        if variant in text_lower:
            # 正しい表記も含まれているか確認
            if correct not in text:
                issues.append({
                    "type": "naming",
                    "severity": "warning",
                    "message": f"表記ゆれの可能性: '{variant}' → '{correct}' を確認してください"
                })
    return issues


def check_url_placeholders(text: str) -> list:
    """未設定URLプレースホルダーの検出"""
    issues = []
    placeholders = re.findall(r"(https?://(?:example\.com|your-site|placeholder)[^\s]*)", text)
    for p in placeholders:
        issues.append({
            "type": "placeholder",
            "severity": "error",
            "message": f"プレースホルダーURLが残っています: {p}"
        })
    return issues


def run_integrity_check(text: str) -> IntegrityResult:
    """
    整合性チェック全実行。
    Returns IntegrityResult(passed, issues, warnings)
    """
    all_issues = []
    all_issues.extend(check_date_consistency(text))
    all_issues.extend(check_version_consistency(text))
    all_issues.extend(check_project_names(text))
    all_issues.extend(check_url_placeholders(text))

    errors = [i for i in all_issues if i.get("severity") == "error"]
    warnings = [i for i in all_issues if i.get("severity") == "warning"]

    passed = len(errors) == 0

    return IntegrityResult(
        passed=passed,
        issues=errors,
        warnings=warnings
    )


if __name__ == "__main__":
    sample = """
MoCKA v3 の機能について説明します。
リリース日は 2019-12-01 です。
詳細は https://example.com/mocka をご覧ください。
"""
    result = run_integrity_check(sample)
    print(f"整合性チェック: {'PASS' if result.passed else 'FAIL'}")
    for i in result.issues:
        print(f"  [ERROR] {i['message']}")
    for w in result.warnings:
        print(f"  [WARN]  {w['message']}")

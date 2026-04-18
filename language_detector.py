"""
language_detector.py
MoCKA Language Algorithm v1.0
役割: テキストから危険信号を検知し、INFO/WARNING/DANGER/CRITICALを判定
E20260418_015 / TODO_030
API通信: なし (0円)
"""

import json
import re
from pathlib import Path
from datetime import datetime

PATTERNS_FILE = Path(__file__).parent / "danger_patterns.json"


class LanguageDetector:

    def __init__(self, patterns_path: Path = None):
        p = patterns_path or PATTERNS_FILE
        self.patterns = json.loads(p.read_text(encoding="utf-8"))
        self.scoring = self.patterns["scoring"]

    def _match(self, text: str, pattern_list: list) -> list:
        """テキストにパターンが含まれるか検索。マッチしたものを返す。"""
        found = []
        text_lower = text.lower()
        for p in pattern_list:
            if p.lower() in text_lower:
                found.append(p)
        return found

    def _match_regex(self, text: str, pattern: str) -> bool:
        try:
            return bool(re.search(pattern, text, re.IGNORECASE))
        except:
            return False

    def analyze(self, text: str) -> dict:
        """
        テキストを解析して危険度スコアと検知パターンを返す。
        戻り値: {
            level: INFO/WARNING/DANGER/CRITICAL,
            score: int,
            findings: {tier1:[...], tier2:[...], ...},
            rules_triggered: [...],
            summary: str
        }
        """
        findings = {}
        total_score = 0

        # 各Tierのパターン検索
        tier_map = {
            "tier1":         self.patterns["tier1"]["weight"],
            "tier2":         self.patterns["tier2"]["weight"],
            "tier3":         self.patterns["tier3"]["weight"],
            "escalation":    self.patterns["escalation"]["weight"],
            "silent_danger": self.patterns["silent_danger"]["weight"],
        }

        for tier, weight in tier_map.items():
            matched = self._match(text, self.patterns[tier]["patterns"])
            if matched:
                findings[tier] = matched
                total_score += len(matched) * weight

        # 文脈ルール適用
        rules_triggered = []
        for rule in self.patterns["context_rules"]["rules"]:
            rid = rule["id"]
            if rid == "RULE_001":
                # 環境忘れ検知（bash/linux/macが含まれ、powershellが含まれない）
                if self._match_regex(text, r'\b(bash|linux|mac os)\b') and \
                   not self._match_regex(text, r'powershell|python'):
                    rules_triggered.append({"id": rid, "name": rule["name"], "severity": rule["severity"]})
                    total_score += 3
            elif rid == "RULE_004":
                # ツール未確認検知
                if self._match_regex(text, r'〜のはず|だと思います|おそらく|たぶん'):
                    rules_triggered.append({"id": rid, "name": rule["name"], "severity": rule["severity"]})
                    total_score += 4

        # スコアからレベル判定
        level = "INFO"
        for lv, rng in self.scoring.items():
            if rng["min"] <= total_score <= rng["max"]:
                level = lv
                break
        if total_score >= self.scoring["CRITICAL"]["min"]:
            level = "CRITICAL"

        # エスカレーション語が1つでもあればCRITICAL確定
        if findings.get("escalation") or findings.get("silent_danger"):
            level = "CRITICAL"

        # サマリ生成
        all_found = []
        for tier, words in findings.items():
            all_found.extend(words)

        summary = self._build_summary(level, total_score, findings, rules_triggered)

        return {
            "level":           level,
            "score":           total_score,
            "findings":        findings,
            "rules_triggered": rules_triggered,
            "matched_words":   all_found,
            "summary":         summary,
            "analyzed_at":     datetime.now().isoformat()
        }

    def _build_summary(self, level: str, score: float, findings: dict, rules: list) -> str:
        lines = [f"[{level}] スコア={score:.1f}"]

        if findings.get("escalation"):
            lines.append(f"⚡ ESCALATION: {findings['escalation']}")
        if findings.get("silent_danger"):
            lines.append(f"🔇 SILENT DANGER: {findings['silent_danger']}")
        if findings.get("tier1"):
            lines.append(f"🔴 Tier1: {findings['tier1']}")
        if findings.get("tier2"):
            lines.append(f"🟠 Tier2: {findings['tier2']}")
        if findings.get("tier3"):
            lines.append(f"🟡 Tier3: {findings['tier3']}")
        for r in rules:
            lines.append(f"📋 RULE [{r['id']}] {r['name']} ({r['severity']})")

        # 推奨アクション
        if level == "CRITICAL":
            lines.append("→ 即停止。きむら博士に確認を求める。")
        elif level == "DANGER":
            lines.append("→ 現在の回答方針を中断。ツールで事実確認してから再回答。")
        elif level == "WARNING":
            lines.append("→ 回答を短縮・具体化。PowerShell/Python形式を確認。")
        else:
            lines.append("→ 通常継続。")

        return " | ".join(lines)


# ============================================================
# 単体テスト
# ============================================================
if __name__ == "__main__":
    detector = LanguageDetector()

    test_cases = [
        ("通常の会話", "app.pyを修正しました。動作確認してください。"),
        ("軽い否定", "そうじゃなくて、もう少し具体的に教えてください。"),
        ("危険信号", "なぜそうなるの？根拠は？さっきと言ってることが違う。動かない。"),
        ("エスカレーション", "最悪。時間の無駄。MoCKAの法に反する。一回止まれ。"),
        ("サイレント撤退", "もういい。今日はここまでにする。"),
        ("環境忘れ", "以下のbashコマンドで実行してください: sudo apt-get install"),
        ("博士特有パターン", "勝手に変えるな。そんな指示はしていない。また同じミスをしている。"),
    ]

    print("=" * 60)
    print("MoCKA Language Detector v1.0 — テスト実行")
    print("=" * 60)

    for name, text in test_cases:
        result = detector.analyze(text)
        print(f"\n【{name}】")
        print(f"  入力: {text[:50]}...")
        print(f"  {result['summary']}")

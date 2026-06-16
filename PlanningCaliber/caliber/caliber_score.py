#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Caliber スコアリングエンジン v1.0
PlanningCaliber 公式評価ツール

Usage:
    python caliber_score.py                  対話モード（スコア入力）
    python caliber_score.py --project <name> プロジェクト指定評価
    python caliber_score.py --json <path>    評価JSONを読み込んで判定
    python caliber_score.py --list           評価履歴一覧
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "evaluation_history.jsonl")


# ── 定数 ──────────────────────────────────────────
SPECS_THRESHOLD      = 0.85
CANDIDATES_THRESHOLD = 0.65

AXES = [
    ("reproducibility",   "再現性        (R)", "同条件で同結果が出るか"),
    ("structure_clarity", "構造明確性    (S)", "モジュール分離の明確さ"),
    ("stability",         "実装安定性    (St)", "workshopでの動作安定性"),
    ("extensibility",     "拡張性        (E)", "他システムへの展開可能性"),
    ("external_impact",   "外部価値      (X)", "PR / SEO / 実務価値"),
]

FORCED_RULES = [
    ("reproducibility",   0.5, "強制再設計（再現性が低すぎる）"),
    ("structure_clarity", 0.4, "即分解対象（構造が不明瞭すぎる）"),
]


# ── ANSI Colors ───────────────────────────────────
class C:
    RESET  = "\033[0m"; BOLD = "\033[1m"
    GREEN  = "\033[92m"; YELLOW = "\033[93m"
    RED    = "\033[91m"; BLUE   = "\033[94m"
    CYAN   = "\033[96m"; GRAY   = "\033[90m"
    def g(t): return f"\033[92m{t}\033[0m"
    def y(t): return f"\033[93m{t}\033[0m"
    def r(t): return f"\033[91m{t}\033[0m"
    def b(t): return f"\033[94m{t}\033[0m"
    def c(t): return f"\033[96m{t}\033[0m"
    def dim(t): return f"\033[90m{t}\033[0m"


def _sep(): print(C.dim("─" * 60))


# ── スコア計算 ────────────────────────────────────

def calculate(scores: dict) -> dict:
    """
    5軸スコアからCaliber総合スコアと判定を算出する。

    Args:
        scores: {"reproducibility": float, "structure_clarity": float,
                 "stability": float, "extensibility": float, "external_impact": float}

    Returns:
        {"caliber_score": float, "judgment": str, "forced_rules": list, "valid": bool}
    """
    # バリデーション
    for key, _, _ in AXES:
        v = scores.get(key)
        if v is None:
            raise ValueError(f"スコア未入力: {key}")
        if not (0.0 <= float(v) <= 1.0):
            raise ValueError(f"スコアは0.0〜1.0の範囲: {key}={v}")

    # 強制ルール確認
    forced = []
    for key, threshold, message in FORCED_RULES:
        if float(scores[key]) < threshold:
            forced.append({"axis": key, "value": float(scores[key]),
                           "threshold": threshold, "action": message})

    # 総合スコア
    total = sum(float(scores[k]) for k, _, _ in AXES) / len(AXES)
    total = round(total, 3)

    # 強制ルール発動時はスコア無効
    if forced:
        judgment = "FORCED_REDESIGN"
        valid    = False
    elif total >= SPECS_THRESHOLD:
        judgment = "specs"
        valid    = True
    elif total >= CANDIDATES_THRESHOLD:
        judgment = "candidates"
        valid    = True
    else:
        judgment = "workshop"
        valid    = True

    return {
        "caliber_score": total,
        "judgment":      judgment,
        "forced_rules":  forced,
        "valid":         valid,
    }


# ── 結果表示 ──────────────────────────────────────

def _print_result(project: str, scores: dict, result: dict):
    print(f"\n  {C.BOLD}Caliber 評価結果{C.RESET}")
    _sep()
    print(f"  Project    : {C.c(project)}")
    print(f"  評価日時    : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    _sep()

    for key, label, _ in AXES:
        v   = float(scores[key])
        bar = "█" * int(v * 20) + "░" * (20 - int(v * 20))
        col = C.g if v >= 0.7 else (C.y if v >= 0.5 else C.r)
        print(f"  {label:<24} {col(f'{v:.2f}')}  {C.dim(bar)}")

    _sep()
    cs = result["caliber_score"]
    col = C.g if cs >= SPECS_THRESHOLD else (C.y if cs >= CANDIDATES_THRESHOLD else C.r)
    print(f"  CaliberScore: {col(f'{cs:.3f}')}")

    j = result["judgment"]
    jmap = {
        "specs":            C.g("✅ specs昇格"),
        "candidates":       C.y("🔶 candidates（追加実験）"),
        "workshop":         C.r("🔁 workshop再実験"),
        "FORCED_REDESIGN":  C.r("🚨 強制再設計（スコア無効）"),
    }
    print(f"  判定        : {jmap.get(j, j)}")

    if result["forced_rules"]:
        print(f"\n  {C.r('【強制ルール発動】')}")
        for fr in result["forced_rules"]:
            print(f"    ❌ {fr['action']} ({fr['axis']}={fr['value']:.2f} < {fr['threshold']})")

    _sep()


# ── 保存 ─────────────────────────────────────────

def _save(project: str, scores: dict, result: dict, notes: str = ""):
    record = {
        "project":       project,
        "evaluated_at":  datetime.now(timezone.utc).isoformat(),
        "evaluator":     "caliber_score.py",
        "scores":        {k: float(scores[k]) for k, _, _ in AXES},
        "caliber_score": result["caliber_score"],
        "judgment":      result["judgment"],
        "forced_rules":  result["forced_rules"],
        "valid":         result["valid"],
        "notes":         notes,
    }
    with open(HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"  {C.dim(f'[記録] {HISTORY_PATH}')}")
    return record


# ── コマンド ──────────────────────────────────────

def cmd_interactive(project: str):
    """対話モードでスコアを入力して評価"""
    print(f"\n  {C.BOLD}Caliber スコアリング — 対話モード{C.RESET}")
    _sep()
    print(f"  Project: {C.c(project)}")
    print(f"  各軸のスコアを 0.0〜1.0 で入力してください\n")

    scores = {}
    for key, label, hint in AXES:
        while True:
            try:
                val = input(f"  {label}  [{hint}]: ").strip()
                v   = float(val)
                if not (0.0 <= v <= 1.0):
                    print(f"  {C.r('0.0〜1.0の範囲で入力してください')}")
                    continue
                scores[key] = v
                break
            except ValueError:
                print(f"  {C.r('数値で入力してください（例: 0.75）')}")

    notes = input(f"\n  メモ（任意）: ").strip()

    result = calculate(scores)
    _print_result(project, scores, result)
    _save(project, scores, result, notes)

    # 昇格アクション案内
    j = result["judgment"]
    if j == "specs":
        print(f"\n  {C.g('次のアクション: 博士に specs 昇格を申請してください。')}")
    elif j == "candidates":
        print(f"\n  {C.y('次のアクション: candidates/ に移動 → 追加実験 → 再評価。')}")
    elif j == "workshop":
        print(f"\n  {C.r('次のアクション: 設計見直し → workshop で再実験 → 再提出。')}")
    else:
        print(f"\n  {C.r('次のアクション: 強制再設計。DESIGN.md を見直してください。')}")
    print()


def cmd_from_json(json_path: str):
    """JSONファイルから評価を読み込んで判定"""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    project = data.get("project", os.path.basename(json_path))
    scores  = data["scores"]
    notes   = data.get("notes", "")
    result  = calculate(scores)
    _print_result(project, scores, result)
    _save(project, scores, result, notes)


def cmd_list():
    """評価履歴一覧を表示"""
    if not os.path.exists(HISTORY_PATH):
        print(C.dim("  評価履歴がありません。"))
        return

    records = []
    with open(HISTORY_PATH, encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line.strip()))
            except Exception:
                pass

    print(f"\n  {C.BOLD}Caliber 評価履歴 ({len(records)}件){C.RESET}")
    _sep()
    print(f"  {'Project':<25} {'Score':<8} {'Judgment':<20} 評価日")
    _sep()

    jmap = {
        "specs":           C.g("specs"),
        "candidates":      C.y("candidates"),
        "workshop":        C.r("workshop"),
        "FORCED_REDESIGN": C.r("FORCED_REDESIGN"),
    }
    for r in reversed(records):
        j   = jmap.get(r["judgment"], r["judgment"])
        dt  = r["evaluated_at"][:10]
        cs  = r["caliber_score"]
        col = C.g if cs >= SPECS_THRESHOLD else (C.y if cs >= CANDIDATES_THRESHOLD else C.r)
        print(f"  {C.c(r['project']):<25} {col(f'{cs:.3f}'):<18} {j:<30} {C.dim(dt)}")
    print()


# ── エントリーポイント ────────────────────────────

def main():
    p = argparse.ArgumentParser(
        prog="caliber_score",
        description="Caliber スコアリングエンジン v1.0 — PlanningCaliber 公式評価ツール"
    )
    p.add_argument("--project", default="", help="プロジェクト名")
    p.add_argument("--json",    default="", help="評価JSONファイルパス")
    p.add_argument("--list",    action="store_true", help="評価履歴一覧")

    args = p.parse_args()

    if args.list:
        cmd_list()
    elif args.json:
        cmd_from_json(args.json)
    else:
        project = args.project or input("  Project名: ").strip() or "unnamed"
        cmd_interactive(project)


if __name__ == "__main__":
    main()

"""
MoCKA incident_learner.py — Language Algorithm自己進化エンジン
チェック方式: 候補提示 → きむら博士承認 → danger_patterns.jsonに追加

機能:
  1. events.csvからCRITICAL/DANGERイベントを検知
  2. そのイベントのテキストを5軸で分解
  3. 未登録語彙を候補として提示
  4. 承認された語彙をdanger_patterns.jsonの指定軸に追加
  5. 学習記録をevents.csvに保存

実行:
  python incident_learner.py scan      # 新規インシデントを検知・候補提示
  python incident_learner.py approve   # 候補を確認・承認
  python incident_learner.py status    # 学習状況表示
"""

import sys
import json
import csv
import re
from pathlib import Path
from datetime import datetime

BASE          = Path("C:/Users/sirok/MoCKA")
EVENTS_CSV    = BASE / "data/events.csv"
PATTERNS_JSON = BASE / "interface/danger_patterns.json"
CANDIDATES_JSON = BASE / "data/learn_candidates.json"
LEARNED_LOG   = BASE / "data/learned_events.json"

# 5軸定義（language_detector.pyと同一）
AXES = {
    "ax1_negative": {
        "label": "否定/疑問語",
        "words": ["違う","ダメ","なぜ","なんで","どうして","おかしい",
                  "意味がない","わからない","理解できない","思い出せ","本当に"]
    },
    "ax2_repeat": {
        "label": "繰り返し語",
        "words": ["また","何度も","さっきも","前も","同じ","繰り返し",
                  "もう一度","また同じ","前も言った","何回も"]
    },
    "ax3_emotion": {
        "label": "感情語",
        "words": ["困った","詰まった","疲れた","もう","やばい",
                  "つらい","しんどい","限界","嫌になった","怒"]
    },
    "ax4_environment": {
        "label": "環境語",
        "words": ["動かない","止まった","落ちた","消えた","壊れた",
                  "起動しない","応答しない","タイムアウト","接続できない",
                  "死んだ","固まった","クラッシュ"]
    },
    "ax5_target": {
        "label": "対象語",
        "words": ["サーバー","ポート","拡張機能","Chrome","ngrok",
                  "bat","BAT","スクリプト","パイプライン","ループ",
                  "MoCKA","Caliber","caliber"]
    },
}

INCIDENT_MARKERS = {"INCIDENT","CRITICAL","ERROR","インシデント","クレーム"}


# ── ユーティリティ ───────────────────────────────────────

def load_patterns() -> dict:
    with open(PATTERNS_JSON, encoding="utf-8") as f:
        return json.load(f)

def save_patterns(patterns: dict):
    with open(PATTERNS_JSON, "w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

def load_events() -> list:
    if not EVENTS_CSV.exists():
        return []
    with open(EVENTS_CSV, encoding="utf-8", errors="replace") as f:
        return [{k: (v or "").strip() for k, v in row.items()}
                for row in csv.DictReader(f)]

def load_candidates() -> dict:
    if CANDIDATES_JSON.exists():
        with open(CANDIDATES_JSON, encoding="utf-8") as f:
            return json.load(f)
    return {"pending": [], "generated_at": None}

def save_candidates(data: dict):
    data["generated_at"] = datetime.now().isoformat()
    with open(CANDIDATES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_learned() -> set:
    if LEARNED_LOG.exists():
        data = json.loads(LEARNED_LOG.read_text(encoding="utf-8"))
        return set(data.get("learned_event_ids", []))
    return set()

def save_learned(learned: set):
    LEARNED_LOG.write_text(
        json.dumps({"learned_event_ids": sorted(list(learned)),
                    "count": len(learned),
                    "updated_at": datetime.now().isoformat()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8")

def extract_text(event: dict) -> str:
    """人間が書いたフィールドのみ"""
    fields = ["title", "why_purpose", "how_trigger", "free_note"]
    return " ".join(event.get(f, "") for f in fields)

def is_incident(event: dict) -> bool:
    risk = event.get("risk_level", "")
    if risk in {"INCIDENT", "CRITICAL", "ERROR"}:
        return True
    text = extract_text(event)
    free = event.get("free_note", "")
    return any(m in text or m in free for m in INCIDENT_MARKERS)

def is_noise(event: dict) -> bool:
    eid = event.get("event_id", "")
    return eid.startswith("EN8N_") or eid.startswith("ECOL_")

def get_all_known_words(patterns: dict) -> set:
    known = set()
    for axis_name, axis_data in AXES.items():
        known.update(axis_data["words"])
    for tier in ["Tier1", "Tier2", "Tier3"]:
        known.update(patterns["patterns"][tier].get("words", []))
        known.update(patterns["patterns"][tier].get("auto_learned", []))
    return known

def tokenize_japanese(text: str) -> list:
    """日本語2〜6文字のフレーズ抽出"""
    tokens = re.findall(r'[\u3040-\u9fff]{2,6}', text)
    return [t for t in tokens if len(t) >= 2]

def guess_axis(word: str) -> str:
    """語彙がどの軸に近いか推定"""
    negative = ["ない","ダメ","なぜ","違","おかし","わから","できな"]
    repeat   = ["また","何度","同じ","繰り返","もう一"]
    emotion  = ["困","疲","やば","つら","しんど","限界","嫌"]
    environment = ["動か","止ま","落ち","消え","壊れ","起動","応答","クラ"]

    for kw in negative:
        if kw in word: return "ax1_negative"
    for kw in repeat:
        if kw in word: return "ax2_repeat"
    for kw in emotion:
        if kw in word: return "ax3_emotion"
    for kw in environment:
        if kw in word: return "ax4_environment"
    return "ax5_target"


# ── SCAN: 新規インシデントから候補抽出 ──────────────────

def cmd_scan():
    print("=== incident_learner: インシデントスキャン ===\n")

    events   = load_events()
    patterns = load_patterns()
    learned  = load_learned()
    known    = get_all_known_words(patterns)

    # 未学習のインシデントイベントを特定
    new_incidents = [
        ev for ev in events
        if not is_noise(ev)
        and is_incident(ev)
        and ev.get("event_id", "") not in learned
    ]

    print(f"未学習インシデント: {len(new_incidents)}件\n")

    if not new_incidents:
        print("新規インシデントなし。")
        return

    # 各インシデントから未登録語彙を抽出
    candidates = []
    for ev in new_incidents:
        text   = extract_text(ev)
        tokens = tokenize_japanese(text)
        new_words = [t for t in tokens if t not in known and len(t) >= 2]

        if new_words:
            for word in set(new_words):
                axis = guess_axis(word)
                candidates.append({
                    "word":        word,
                    "suggested_axis": axis,
                    "axis_label":  AXES[axis]["label"],
                    "source_event": ev.get("event_id", ""),
                    "source_title": ev.get("title", "")[:50],
                    "approved":    None  # None=未判断 True=承認 False=却下
                })

        learned.add(ev.get("event_id", ""))

    # 重複除去
    seen = set()
    unique = []
    for c in candidates:
        if c["word"] not in seen:
            seen.add(c["word"])
            unique.append(c)

    save_candidates({"pending": unique})
    save_learned(learned)

    print(f"候補語彙: {len(unique)}件\n")
    print("【承認待ち候補】")
    for i, c in enumerate(unique):
        print(f"  [{i:02d}] 「{c['word']}」→ {c['axis_label']}({c['suggested_axis']})")
        print(f"       出典: {c['source_title']}")
    print(f"\n承認するには: python incident_learner.py approve")


# ── APPROVE: 候補を確認・承認 ────────────────────────────

def cmd_approve():
    print("=== incident_learner: 候補承認 ===\n")

    data = load_candidates()
    pending = [c for c in data["pending"] if c["approved"] is None]

    if not pending:
        print("承認待ち候補なし。先に scan を実行してください。")
        return

    patterns = load_patterns()
    approved_count = 0
    rejected_count = 0

    print(f"承認待ち: {len(pending)}件\n")
    print("各語彙について y(承認)/n(却下)/q(終了) を入力してください\n")

    for c in pending:
        print(f"「{c['word']}」→ {c['axis_label']}({c['suggested_axis']})")
        print(f"  出典: {c['source_title']}")

        while True:
            ans = input("  承認? [y/n/q]: ").strip().lower()
            if ans in ("y", "n", "q"):
                break

        if ans == "q":
            print("\n中断しました。")
            break
        elif ans == "y":
            # 承認 → danger_patterns.jsonの対応軸に追加
            # Tier2のauto_learnedに追加（5軸はdanger_patterns内のTier2/3で管理）
            tier = "Tier2" if c["suggested_axis"] in ("ax1_negative","ax2_repeat","ax3_emotion") else "Tier3"
            if c["word"] not in patterns["patterns"][tier]["auto_learned"]:
                patterns["patterns"][tier]["auto_learned"].append(c["word"])
            c["approved"] = True
            approved_count += 1
            print(f"  ✅ 承認 → {tier}に追加")
        else:
            c["approved"] = False
            rejected_count += 1
            print(f"  ❌ 却下")

    save_patterns(patterns)
    save_candidates(data)

    print(f"\n承認: {approved_count}件 / 却下: {rejected_count}件")
    print("danger_patterns.json更新完了")


# ── STATUS: 学習状況表示 ─────────────────────────────────

def cmd_status():
    print("=== incident_learner: 学習状況 ===\n")

    patterns = load_patterns()
    learned  = load_learned()
    data     = load_candidates()

    pending = [c for c in data.get("pending",[]) if c["approved"] is None]
    approved = [c for c in data.get("pending",[]) if c["approved"] is True]

    print(f"学習済みインシデント: {len(learned)}件")
    print(f"承認待ち候補:         {len(pending)}件")
    print(f"承認済み語彙:         {len(approved)}件")
    print()

    for tier in ["Tier1","Tier2","Tier3"]:
        auto = patterns["patterns"][tier].get("auto_learned",[])
        print(f"{tier} auto_learned: {len(auto)}件 {auto[:5]}")


# ── エントリーポイント ───────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "scan"
    if   cmd == "scan":    cmd_scan()
    elif cmd == "approve": cmd_approve()
    elif cmd == "status":  cmd_status()
    else: print("使い方: python incident_learner.py [scan|approve|status]")

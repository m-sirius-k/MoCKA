"""
SCAMPER Creative Engine v2.0
MoCKA第三の柱「発明する文明」— 4trigger完全版

INCIDENT / SUCCESS / OPERATION / VOICE の全データをSCAMPER展開する

Usage:
    python scamper_engine.py                        # 各trigger直近1件ずつ展開
    python scamper_engine.py --trigger VOICE        # VOICEのみ
    python scamper_engine.py --trigger SUCCESS      # SUCCESSのみ
    python scamper_engine.py --trigger INCIDENT     # INCIDENTのみ
    python scamper_engine.py --trigger OPERATION    # OPERATIONのみ
    python scamper_engine.py --event E20260514_026  # 特定イベント
    python scamper_engine.py --interactive          # 対話モード
    python scamper_engine.py --all                  # 全trigger・各3件
"""

import json
import sqlite3
import os
import sys
import re
import argparse
from datetime import datetime
from pathlib import Path

# ── パス設定 ──────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
MOCKA_DIR   = Path("C:/Users/sirok/MoCKA")
TEMPLATES_PATH = BASE_DIR / "scamper_templates.json"
DB_PATH     = MOCKA_DIR / "data" / "mocka_events.db"
OUTPUT_DIR  = BASE_DIR / "scamper_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── trigger分類マップ ───────────────────────────────────────
TRIGGER_TYPES = {
    "INCIDENT":  ["MATAKA","INCIDENT","CLAIM","ai_violation","OVERDUE_INCIDENT",
                  "governance_degradation","config_error","incident","environment_error","security"],
    "SUCCESS":   ["success_hint","success_great","DECISION_APPROVED"],
    "OPERATION": ["collaboration","phl_decision","OPERATION","save","process",
                  "broadcast","storage","record","caliber"],
    "VOICE":     ["user_voice"],
}

def detect_trigger(what_type):
    for trigger, types in TRIGGER_TYPES.items():
        if what_type in types:
            return trigger
    return "INCIDENT"  # デフォルト

# ── テンプレート読み込み ────────────────────────────────────
def load_templates():
    if not TEMPLATES_PATH.exists():
        print(f"[ERROR] テンプレートが見つかりません: {TEMPLATES_PATH}")
        sys.exit(1)
    with open(TEMPLATES_PATH, encoding="utf-8") as f:
        return json.load(f)

# ── events.dbからイベント取得 ───────────────────────────────
def fetch_events(trigger_name=None, event_id=None, limit=3):
    if not DB_PATH.exists():
        print(f"[ERROR] DB未検出: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    if event_id:
        rows = conn.execute(
            "SELECT * FROM events WHERE event_id=? LIMIT 1", (event_id,)
        ).fetchall()
    elif trigger_name and trigger_name in TRIGGER_TYPES:
        types = TRIGGER_TYPES[trigger_name]
        placeholders = ",".join("?" * len(types))
        rows = conn.execute(
            f"SELECT * FROM events WHERE what_type IN ({placeholders}) ORDER BY when_ts DESC LIMIT ?",
            types + [limit]
        ).fetchall()
    else:
        # 全trigger各limit件
        rows = []
        for t_name, types in TRIGGER_TYPES.items():
            placeholders = ",".join("?" * len(types))
            r = conn.execute(
                f"SELECT * FROM events WHERE what_type IN ({placeholders}) ORDER BY when_ts DESC LIMIT ?",
                types + [1]
            ).fetchall()
            rows.extend(r)

    conn.close()
    return [dict(r) for r in rows]

# ── 変数抽出 ────────────────────────────────────────────────
def extract_variables(event):
    title   = event.get("title", "") or ""
    who     = event.get("who_actor", "") or "Claude"
    what_t  = event.get("what_type", "") or ""
    why     = event.get("why_purpose", "") or ""
    how     = event.get("how_trigger", "") or ""
    note    = event.get("free_note", "") or ""
    summary = event.get("short_summary", "") or ""

    trigger = detect_trigger(what_t)

    # whatの優先順位: title > short_summary > free_note先頭 > what_type
    what = title.strip()
    if not what:
        what = summary.strip()
    if not what and note:
        what = note[:60].strip()
    if not what:
        what = what_t

    what = what[:60]

    return {
        "trigger":  trigger,
        "title":    what,
        "what":     what,
        "who":      who,
        "why":      (why or "不明")[:60],
        "how":      (how or "不明")[:60],
        "n":        1,
        "operation": what,
        "philosophy": what if trigger == "VOICE" else "AIを信じるな、システムで縛れ",
        "freq":     "5分",
    }

# ── テンプレート変数置換 ────────────────────────────────────
def fill_template(question, variables):
    return re.sub(r"\{(\w+)\}", lambda m: str(variables.get(m.group(1), "{"+m.group(1)+"}")), question)

# ── SCAMPER展開 ─────────────────────────────────────────────
def expand_scamper(event, templates):
    variables = extract_variables(event)
    trigger   = variables["trigger"]
    scamper   = templates["scamper"]
    rules     = templates["expansion_rules"]
    apply_ids = rules.get(trigger, rules["INCIDENT"])

    expansions = []
    for vk, vd in scamper.items():
        for tmpl in vd["templates"]:
            if tmpl["id"] not in apply_ids:
                continue
            expansions.append({
                "scamper_id":   tmpl["id"],
                "view":         f"{vk}: {vd['label']}",
                "question":     fill_template(tmpl["question"], variables),
                "output_type":  tmpl["output_type"],
                "example_output": tmpl["example_output"],
            })

    eid = event.get("event_id") or event.get("when_ts", "MANUAL")
    return {
        "event_id":    eid,
        "event_title": variables["what"],
        "what_type":   event.get("what_type", ""),
        "trigger":     trigger,
        "variables":   variables,
        "generated_at": datetime.now().isoformat(),
        "expansions":  expansions,
    }

# ── 表示 ────────────────────────────────────────────────────
TRIGGER_ICON = {"INCIDENT":"🔴","SUCCESS":"🟢","OPERATION":"🔵","VOICE":"💬"}

def print_result(result):
    icon = TRIGGER_ICON.get(result["trigger"], "🔬")
    print("\n" + "="*70)
    print(f"{icon} [{result['trigger']}] {result['event_id']}")
    print(f"   内容: {result['event_title'][:55]}")
    print(f"   type: {result['what_type']}")
    print("="*70)
    for exp in result["expansions"]:
        print(f"\n[{exp['scamper_id']}] {exp['view']}")
        print(f"  💡 {exp['question']}")
        print(f"  → {exp['output_type']}: {exp['example_output'][:60]}...")
    print(f"\n展開数: {len(result['expansions'])}件")

# ── 保存 ────────────────────────────────────────────────────
def save_result(result):
    ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_id = str(result["event_id"])
    safe   = re.sub(r'[\\/:*?"<>|\s]', '_', raw_id)[:40]
    path   = OUTPUT_DIR / f"scamper_{result['trigger']}_{safe}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"💾 {path.name}")
    return path

# ── 対話モード ──────────────────────────────────────────────
def interactive_mode(templates):
    print("\n🎯 SCAMPER Creative Engine v2.0 — 対話モード")
    what    = input("内容（インシデント・発言・成功内容など）: ").strip()
    who     = input("WHO: ").strip() or "Claude"
    trigger = input("Trigger [INCIDENT/SUCCESS/OPERATION/VOICE] (Enter=INCIDENT): ").strip().upper()
    if trigger not in TRIGGER_TYPES:
        trigger = "INCIDENT"

    event = {
        "event_id":  "MANUAL_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "title":     what,
        "what_type": list(TRIGGER_TYPES[trigger])[0],
        "who_actor": who,
        "why_purpose": "",
        "how_trigger": "",
        "free_note":   "",
        "short_summary": "",
    }
    result = expand_scamper(event, templates)
    print_result(result)
    save_result(result)

# ── エントリポイント ────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SCAMPER Creative Engine v2.0")
    parser.add_argument("--event",       help="特定event_id")
    parser.add_argument("--trigger",     help="INCIDENT/SUCCESS/OPERATION/VOICE")
    parser.add_argument("--limit",       type=int, default=3)
    parser.add_argument("--all",         action="store_true", help="全trigger各3件")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    templates = load_templates()

    if args.interactive:
        interactive_mode(templates)
        return

    limit = args.limit if not args.all else 3
    events = fetch_events(trigger_name=args.trigger, event_id=args.event, limit=limit)

    if not events:
        print("[INFO] 対象イベントなし")
        return

    label = args.trigger or ("全trigger" if not args.event else args.event)
    print(f"\n📋 {len(events)}件をSCAMPER展開 [{label}]...")

    for event in events:
        result = expand_scamper(event, templates)
        print_result(result)
        save_result(result)

    print(f"\n✅ 完了 → {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

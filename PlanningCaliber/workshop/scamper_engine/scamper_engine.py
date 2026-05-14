"""
SCAMPER Creative Engine v1.0
MoCKA第三の柱「発明する文明」— Phase2実装

events.dbのインシデント/OPERATION/PHILOSOPHYデータを
SCAMPER7視点で自動展開し、発明的解決案を生成する。

Usage:
    python scamper_engine.py                      # 直近インシデント5件を展開
    python scamper_engine.py --event E20260514_026 # 特定イベントを展開
    python scamper_engine.py --trigger INCIDENT    # triggerタイプ指定
    python scamper_engine.py --all                 # 全テンプレート展開
    python scamper_engine.py --interactive         # 対話モード
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
BASE_DIR = Path(__file__).parent
MOCKA_DIR = Path("C:/Users/sirok/MoCKA")
TEMPLATES_PATH = BASE_DIR / "scamper_templates.json"
DB_PATH = MOCKA_DIR / "mocka_events.db"
OUTPUT_DIR = BASE_DIR / "scamper_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── テンプレート読み込み ────────────────────────────────────
def load_templates():
    if not TEMPLATES_PATH.exists():
        print(f"[ERROR] テンプレートが見つかりません: {TEMPLATES_PATH}")
        sys.exit(1)
    with open(TEMPLATES_PATH, encoding="utf-8") as f:
        return json.load(f)

# ── events.dbからイベント取得 ───────────────────────────────
def fetch_events(trigger_type=None, event_id=None, limit=5):
    if not DB_PATH.exists():
        print(f"[ERROR] events.dbが見つかりません: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if event_id:
        cur.execute(
            "SELECT * FROM events WHERE event_id = ? LIMIT 1",
            (event_id,)
        )
    elif trigger_type:
        cur.execute(
            """SELECT * FROM events
               WHERE what_type LIKE ? OR tags LIKE ?
               ORDER BY when_ts DESC LIMIT ?""",
            (f"%{trigger_type}%", f"%{trigger_type}%", limit)
        )
    else:
        # インシデント系を優先取得
        cur.execute(
            """SELECT * FROM events
               WHERE what_type IN ('INCIDENT','DANGER','CRITICAL','MATAKA','CLAIM')
                  OR tags LIKE '%INCIDENT%'
                  OR tags LIKE '%DANGER%'
               ORDER BY when_ts DESC LIMIT ?""",
            (limit,)
        )

    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── イベントからSCAMPER入力変数を抽出 ──────────────────────
def extract_variables(event):
    desc = event.get("description", "") or ""
    title = event.get("title", "") or ""
    tags = event.get("tags", "") or ""

    # triggerタイプ判定
    trigger = "INCIDENT"
    if any(t in tags.upper() for t in ["OPERATION", "CHANGE_DONE", "CHANGE_START"]):
        trigger = "OPERATION"
    elif any(t in tags.upper() for t in ["PHILOSOPHY", "DESIGN"]):
        trigger = "PHILOSOPHY"

    # 5W1H抽出（正規表現）
    def extract_field(pattern, text, default=""):
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        return m.group(1).strip() if m else default

    who  = extract_field(r"WHO\s*[:：]\s*(.+)", desc) or "Claude"
    what = extract_field(r"WHAT\s*[:：]\s*(.+)", desc) or title
    why  = extract_field(r"WHY\s*[:：]\s*(.+)", desc) or ""
    how  = extract_field(r"HOW\s*[:：]\s*(.+)", desc) or ""

    # タイトルから短いwhatを生成
    short_what = title.replace("INCIDENT:", "").replace("CHANGE_DONE:", "").strip()
    short_what = short_what[:40] if len(short_what) > 40 else short_what

    return {
        "trigger": trigger,
        "title": short_what,
        "what": what[:60] if what else short_what,
        "who": who,
        "why": why[:60] if why else "不明",
        "how": how[:60] if how else "不明",
        "n": 1,
        "operation": short_what,
        "philosophy": "AIを信じるな、システムで縛れ",
        "freq": "5分",
        "operation_a": "morphology_engine",
        "operation_b": "PHL-OS",
    }

# ── テンプレート変数置換 ────────────────────────────────────
def fill_template(question, variables):
    def replacer(m):
        key = m.group(1)
        return str(variables.get(key, f"{{{key}}}"))
    return re.sub(r"\{(\w+)\}", replacer, question)

# ── SCAMPER展開メイン ───────────────────────────────────────
def expand_scamper(event, templates, use_all=False):
    variables = extract_variables(event)
    trigger = variables["trigger"]
    scamper = templates["scamper"]
    rules = templates["expansion_rules"]["trigger_mapping"]

    # 適用テンプレートID一覧
    if use_all:
        apply_ids = []
        for ids in rules.values():
            apply_ids.extend(ids)
    else:
        apply_ids = rules.get(trigger, rules["INCIDENT"])

    results = []
    for view_key, view_data in scamper.items():
        for tmpl in view_data["templates"]:
            if tmpl["id"] not in apply_ids:
                continue
            filled_q = fill_template(tmpl["question"], variables)
            results.append({
                "scamper_id": tmpl["id"],
                "view": f"{view_key}: {view_data['label']}",
                "core_question": view_data["core_question"],
                "question": filled_q,
                "output_type": tmpl["output_type"],
                "example_output": tmpl["example_output"],
            })

    return {
        "event_id": event.get("event_id", "MANUAL"),
        "event_title": event.get("title", ""),
        "trigger": trigger,
        "variables": variables,
        "generated_at": datetime.now().isoformat(),
        "expansions": results,
    }

# ── 結果表示 ────────────────────────────────────────────────
def print_result(result):
    print("\n" + "="*70)
    print(f"🔬 SCAMPER展開: {result['event_id']}")
    print(f"   イベント: {result['event_title'][:60]}")
    print(f"   Trigger : {result['trigger']}")
    print(f"   生成日時: {result['generated_at'][:19]}")
    print("="*70)

    for i, exp in enumerate(result["expansions"], 1):
        print(f"\n[{exp['scamper_id']}] {exp['view']}")
        print(f"  問い: {exp['question']}")
        print(f"  期待出力タイプ: {exp['output_type']}")
        print(f"  展開例: {exp['example_output']}")

    print(f"\n→ 展開数: {len(result['expansions'])}件")

# ── JSON保存 ────────────────────────────────────────────────
def save_result(result):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_id = result["event_id"].replace("/", "_")
    out_path = OUTPUT_DIR / f"scamper_{event_id}_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 保存: {out_path}")
    return out_path

# ── 対話モード ──────────────────────────────────────────────
def interactive_mode(templates):
    print("\n🎯 SCAMPER Creative Engine — 対話モード")
    print("インシデントを手動入力してSCAMPERを展開します。\n")

    title = input("インシデントタイトル: ").strip()
    what  = input("WHAT（何が起きた）: ").strip()
    who   = input("WHO（誰が）: ").strip() or "Claude"
    why   = input("WHY（なぜ）: ").strip() or "調査中"

    trigger = input("Trigger [INCIDENT/OPERATION/PHILOSOPHY] (Enter=INCIDENT): ").strip().upper()
    if trigger not in ("INCIDENT", "OPERATION", "PHILOSOPHY"):
        trigger = "INCIDENT"

    event = {
        "event_id": "MANUAL_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        "title": title,
        "description": f"WHO: {who}\nWHAT: {what}\nWHY: {why}",
        "tags": trigger,
        "what_type": trigger,
    }

    result = expand_scamper(event, templates)
    print_result(result)
    save_result(result)

# ── エントリポイント ────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SCAMPER Creative Engine v1.0")
    parser.add_argument("--event",       help="特定event_idを展開")
    parser.add_argument("--trigger",     help="triggerタイプ指定 (INCIDENT/OPERATION/PHILOSOPHY)")
    parser.add_argument("--limit",       type=int, default=3, help="取得件数 (default: 3)")
    parser.add_argument("--all",         action="store_true", help="全テンプレート展開")
    parser.add_argument("--interactive", action="store_true", help="対話モード")
    args = parser.parse_args()

    templates = load_templates()

    if args.interactive:
        interactive_mode(templates)
        return

    events = fetch_events(
        trigger_type=args.trigger,
        event_id=args.event,
        limit=args.limit
    )

    if not events:
        print("[INFO] 対象イベントが見つかりません。--interactiveで手動入力できます。")
        return

    print(f"\n📋 {len(events)}件のイベントをSCAMPER展開します...\n")

    all_results = []
    for event in events:
        result = expand_scamper(event, templates, use_all=args.all)
        print_result(result)
        saved = save_result(result)
        all_results.append(result)

    print(f"\n✅ 完了: {len(all_results)}件展開 → {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

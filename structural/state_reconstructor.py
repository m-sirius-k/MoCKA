"""
MoCKA 3.0 — Phase 3
state_reconstructor.py

責務:
  EventAからEventBの間の「状態差分」を復元する。
  Git diffではなく「状態遷移」として説明する。

  対象状態:
    - UI状態 (Chat Button / Router / Navigation)
    - Search状態 (PRIMARY_FIELDS / search scope)
    - Event Binding状態 (before/after)
    - Router状態 (save / share / collaboration)
"""

import json
import sqlite3
import datetime
import re
from pathlib import Path

REPO_ROOT       = Path(r"C:\Users\sirok\MoCKA")
MOCKA_DB        = REPO_ROOT / "data" / "mocka_events.db"
EVENT_FILE_MAP  = REPO_ROOT / "data" / "mocka" / "event_file_map.json"
OUTPUT_PATH     = REPO_ROOT / "data" / "mocka" / "state_reconstructor_output.json"

# ============================================================
# 状態抽出パターン定義
# ============================================================

STATE_PATTERNS = {
    "ui": {
        "chat_button":   re.compile(r"chat[^\w]*(button|ボタン|btn|navigation|遷移)", re.I),
        "popup":         re.compile(r"popup\.(js|html)", re.I),
        "ui_change":     re.compile(r"(UI|画面|表示|レイアウト).*(変更|追加|修正|削除)", re.I),
    },
    "search": {
        "primary_fields":re.compile(r"PRIMARY_FIELDS", re.I),
        "search_scope":  re.compile(r"(search|検索).*(scope|対象|範囲|field)", re.I),
        "caliber_search":re.compile(r"caliber.*(search|検索)", re.I),
        "search_quality":re.compile(r"(検索|search).*(劣化|品質|壊|broken|degraded)", re.I),
    },
    "router": {
        "save":          re.compile(r"router[/\s]*save|save.*router", re.I),
        "share":         re.compile(r"router[/\s]*share|share.*router", re.I),
        "collaboration": re.compile(r"router[/\s]*collab|collaboration", re.I),
    },
    "event_binding": {
        "rebind":        re.compile(r"(event|イベント).*(bind|handler|listener|再登録|rebind)", re.I),
        "onclick":       re.compile(r"onclick|addEventListener|removeEventListener", re.I),
    },
    "security": {
        "api_key":       re.compile(r"(API[_\s]*key|APIキー).*(削除|漏洩|制限|restrict|delete|leak)", re.I),
        "git_leak":      re.compile(r"(git|GitHub).*(leak|漏洩|混入|secret)", re.I),
    },
}

# ============================================================
# DBからイベントを取得
# ============================================================

def fetch_event_range(db_path: Path, event_id_a: str, event_id_b: str) -> list[dict]:
    """event_id_a から event_id_b の間のイベントを取得する。"""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    event_table = next((t for t in tables if "event" in t.lower()), None)
    if not event_table:
        conn.close()
        return []
    # 両IDの rowid を取得
    try:
        cur.execute(f"SELECT rowid FROM {event_table} WHERE event_id=? OR when_ts=?",
                    (event_id_a, event_id_a))
        row_a = cur.fetchone()
        cur.execute(f"SELECT rowid FROM {event_table} WHERE event_id=? OR when_ts=?",
                    (event_id_b, event_id_b))
        row_b = cur.fetchone()
        if row_a and row_b:
            lo, hi = sorted([row_a[0], row_b[0]])
            cur.execute(f"SELECT * FROM {event_table} WHERE rowid BETWEEN ? AND ?", (lo, hi))
        else:
            # どちらか見つからない場合は最新100件
            cur.execute(f"SELECT * FROM {event_table} ORDER BY rowid DESC LIMIT 100")
        rows = [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[state_reconstructor] クエリエラー: {e}")
        rows = []
    conn.close()
    return rows


def fetch_single_event(db_path: Path, event_id: str) -> dict | None:
    """単一イベントを取得する。"""
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    event_table = next((t for t in tables if "event" in t.lower()), None)
    if not event_table:
        conn.close()
        return None
    try:
        cur.execute(f"SELECT * FROM {event_table} WHERE event_id=? LIMIT 1", (event_id,))
        row = cur.fetchone()
        result = dict(row) if row else None
    except Exception:
        result = None
    conn.close()
    return result


# ============================================================
# 状態抽出
# ============================================================

def extract_state_signals(event: dict) -> dict:
    """イベントテキストから状態シグナルを抽出する。"""
    text = " ".join(str(v) for v in event.values() if v)
    signals = {}
    for category, patterns in STATE_PATTERNS.items():
        matched = []
        for signal_name, pattern in patterns.items():
            if pattern.search(text):
                matched.append(signal_name)
        if matched:
            signals[category] = matched
    return signals


# ============================================================
# 状態差分生成
# ============================================================

def reconstruct_state_diff(event_id_a: str, event_id_b: str) -> dict:
    """
    EventA → EventB の状態差分を復元する。
    event_id_b が None の場合は event_id_a 単体を分析する。
    """
    print(f"[state_reconstructor] 状態復元: {event_id_a} → {event_id_b or '(single)'}")

    if event_id_b:
        events = fetch_event_range(MOCKA_DB, event_id_a, event_id_b)
    else:
        ev = fetch_single_event(MOCKA_DB, event_id_a)
        events = [ev] if ev else []

    if not events:
        return {"error": "イベントが見つかりませんでした", "event_id_a": event_id_a}

    # 各イベントの状態シグナルを収集
    timeline = []
    state_accumulator = {}  # category → {signal: [event_ids]}

    for ev in events:
        eid = ev.get("event_id") or ev.get("when_ts") or "unknown"
        signals = extract_state_signals(ev)
        if signals:
            timeline.append({
                "event_id": eid,
                "title":    (ev.get("title") or "")[:60],
                "signals":  signals,
            })
            for cat, sigs in signals.items():
                if cat not in state_accumulator:
                    state_accumulator[cat] = {}
                for s in sigs:
                    if s not in state_accumulator[cat]:
                        state_accumulator[cat][s] = []
                    state_accumulator[cat][s].append(eid)

    # event_file_map との照合
    file_changes = []
    if EVENT_FILE_MAP.exists():
        with open(EVENT_FILE_MAP, encoding="utf-8-sig") as f:
            fmap = json.load(f).get("map", {})
        for ev in events:
            eid = ev.get("event_id") or ""
            if eid in fmap:
                entry = fmap[eid]
                if entry.get("files"):
                    file_changes.append({
                        "event_id": eid,
                        "title":    entry.get("title", "")[:60],
                        "files":    entry["files"],
                        "symbols":  entry.get("symbols", []),
                        "commits":  entry.get("commits", []),
                    })

    # 人間が読める状態差分サマリを生成
    summary_lines = []
    if "search" in state_accumulator:
        sigs = state_accumulator["search"]
        if "primary_fields" in sigs:
            summary_lines.append(
                f"PRIMARY_FIELDS変更: イベント {sigs['primary_fields']} で検索対象フィールドが再定義された可能性"
            )
        if "search_quality" in sigs:
            summary_lines.append(
                f"検索品質劣化シグナル: イベント {sigs['search_quality']} で検索劣化が報告された"
            )
    if "ui" in state_accumulator:
        sigs = state_accumulator["ui"]
        if "chat_button" in sigs:
            summary_lines.append(
                f"ChatButton追加: イベント {sigs['chat_button']} でUI変更が発生"
            )
    if "event_binding" in state_accumulator:
        sigs = state_accumulator["event_binding"]
        summary_lines.append(
            f"EventBinding再登録: イベント {list(sigs.values())[0]} でイベントハンドラが変更された可能性"
        )
    if "router" in state_accumulator:
        sigs = state_accumulator["router"]
        summary_lines.append(
            f"Router変更: {list(sigs.keys())} が影響を受けた可能性"
        )

    result = {
        "generated_at":       datetime.datetime.now().isoformat(timespec="seconds"),
        "event_range":        {"from": event_id_a, "to": event_id_b or "(single)"},
        "events_analyzed":    len(events),
        "state_signals":      state_accumulator,
        "file_changes":       file_changes,
        "timeline":           timeline,
        "summary":            summary_lines if summary_lines else ["状態変化シグナルなし — 詳細はtimelineを参照"],
    }
    return result


# ============================================================
# P1専用: Orchestra検索劣化の状態復元
# ============================================================

def analyze_p1_orchestra_search_degradation() -> dict:
    """
    P1インシデント専用分析:
    E20260611_343 (content_orchestra.js v5修正) 前後の状態復元。
    """
    print("[state_reconstructor] P1: Orchestra検索劣化の状態復元開始...")

    # v5修正イベント前後を分析
    result = reconstruct_state_diff("E20260611_343", "E20260613_015")

    # P1専用の結論を追加
    result["p1_diagnosis"] = {
        "trigger_event":  "E20260611_343",
        "trigger_title":  "content_orchestra.js v5 — 送信直前focus再取得・sendBtn.click()単純化",
        "hypothesis":     [
            "execCommand/focus/sendBtnの再実装時に検索系イベントハンドラが再バインドされた",
            "PRIMARY_FIELDSが再初期化されて検索スコープが縮小した",
            "chatに飛ぶボタン追加によるrouting状態の変化が検索制約に波及した",
        ],
        "state_before":   "全件検索・正確な保存が動作していた",
        "state_after":    "キーワード一致の羅列のみ。昨日のイベントすら検索でヒットしない",
        "next_action":    "content_orchestra.jsのsearch関連イベントハンドラを直接確認する",
        "git_needed":     False,
        "note":           "コミットハッシュは不要。イベント索引から起点特定済み。",
    }
    return result


# ============================================================
# メイン
# ============================================================

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # P1専用分析を実行
    result = analyze_p1_orchestra_search_degradation()

    with open(OUTPUT_PATH, "w", encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=True, indent=2)

    print("\n========= State Reconstruction: P1 Summary =========")
    for line in result.get("summary", []):
        print(f"  • {line}")
    print("\n[P1 Diagnosis]")
    diag = result.get("p1_diagnosis", {})
    print(f"  起点イベント: {diag.get('trigger_event')}")
    print(f"  状態Before : {diag.get('state_before')}")
    print(f"  状態After  : {diag.get('state_after')}")
    print("  仮説:")
    for h in diag.get("hypothesis", []):
        print(f"    → {h}")
    print(f"  次アクション: {diag.get('next_action')}")
    print(f"\n[出力]: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

"""
MoCKA 3.0 — Phase 2
event_file_resolver.py

責務:
  イベントID → 変更ファイル → 変更シンボル → 影響Module
  を自動解決する。
  MoCKA events DB + repository_index.json を組み合わせて
  「どのイベントがどのファイルを変えたか」を索引化する。
出力:
  event_file_map.json
"""

import os
import re
import json
import sqlite3
import datetime
from pathlib import Path

REPO_ROOT      = Path(r"C:\Users\sirok\MoCKA")
MOCKA_DB       = REPO_ROOT / "data" / "mocka_events.db"
REPO_INDEX     = REPO_ROOT / "structural" / "repository_index.json"
OUTPUT_PATH    = REPO_ROOT / "structural" / "event_file_map.json"

# ============================================================
# ファイル名・シンボルの抽出パターン
# ============================================================

FILE_PATTERN   = re.compile(
    r"([a-zA-Z0-9_\-]+\.(js|py|json|ts|html|css|md|txt|sh|bat))"
)
SYMBOL_PATTERN = re.compile(
    r"\b([a-zA-Z_][a-zA-Z0-9_]{3,})\s*[\(=]"  # 関数名・変数名っぽいもの
)
COMMIT_PATTERN = re.compile(r"\b([0-9a-f]{7,40})\b")

# ============================================================
# Repository Index からファイルパスを検索
# ============================================================

def load_repo_index() -> dict:
    """repository_index.json を読み込み、ファイル名→パスの逆引き辞書を返す。"""
    if not REPO_INDEX.exists():
        return {}
    with open(REPO_INDEX, encoding="utf-8-sig") as f:
        idx = json.load(f)
    name_to_paths = {}
    for module in idx.get("modules", []):
        for fi in module.get("files", []):
            name = fi["name"]
            path = fi["path"]
            if name not in name_to_paths:
                name_to_paths[name] = []
            name_to_paths[name].append({
                "path":   path,
                "module": module["name"],
                "mtime":  fi.get("mtime"),
                "sha256": fi.get("sha256"),
            })
    return name_to_paths


# ============================================================
# イベントDBからイベントを取得
# ============================================================

def fetch_events(db_path: Path, limit: int = 500) -> list[dict]:
    """MoCKA events DB から最新N件を取得する。"""
    if not db_path.exists():
        print(f"[event_file_resolver] DB not found: {db_path}")
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # テーブル名を確認
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    # events テーブルを探す
    event_table = None
    for t in tables:
        if "event" in t.lower():
            event_table = t
            break
    if not event_table:
        print(f"[event_file_resolver] eventテーブルが見つかりません。tables: {tables}")
        conn.close()
        return []
    try:
        cur.execute(f"SELECT * FROM {event_table} ORDER BY rowid DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[event_file_resolver] クエリエラー: {e}")
        rows = []
    conn.close()
    return rows


# ============================================================
# イベントテキストからファイル・シンボル・コミットを抽出
# ============================================================

def extract_from_event(event: dict, name_to_paths: dict) -> dict:
    """イベント1件を解析し、関連ファイル・シンボル・コミットを返す。"""
    text = " ".join(str(v) for v in event.values() if v)

    # ファイル名マッチ
    raw_files = FILE_PATTERN.findall(text)
    file_names = list(dict.fromkeys(f[0] for f in raw_files))  # 重複除去

    # リポジトリ索引で解決
    resolved_files = []
    modules_hit = set()
    for fname in file_names:
        if fname in name_to_paths:
            for entry in name_to_paths[fname]:
                resolved_files.append(entry)
                modules_hit.add(entry["module"])

    # シンボル抽出（重複除去・上位20件）
    symbols = list(dict.fromkeys(SYMBOL_PATTERN.findall(text)))[:20]

    # コミットハッシュ抽出
    commits = list(dict.fromkeys(COMMIT_PATTERN.findall(text)))[:5]

    return {
        "files":    resolved_files,
        "symbols":  symbols,
        "commits":  commits,
        "modules":  list(modules_hit),
    }


# ============================================================
# メイン: event_file_map 生成
# ============================================================

def build_map() -> dict:
    print("[event_file_resolver] repository_index 読み込み...")
    name_to_paths = load_repo_index()
    print(f"  → {len(name_to_paths)} ファイル名を索引化")

    print("[event_file_resolver] イベントDB読み込み...")
    events = fetch_events(MOCKA_DB, limit=1000)
    print(f"  → {len(events)} イベント取得")

    event_map = {}
    for ev in events:
        event_id = (
            ev.get("event_id") or
            ev.get("id") or
            ev.get("when_ts") or
            str(ev.get("rowid", "unknown"))
        )
        result = extract_from_event(ev, name_to_paths)
        # ファイルかシンボルかコミットがある場合のみ記録
        if result["files"] or result["commits"]:
            event_map[event_id] = {
                "title":   (ev.get("title") or "")[:80],
                "when_ts": ev.get("when_ts") or ev.get("created_at") or "",
                **result,
            }

    output = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "event_count":  len(events),
        "mapped_count": len(event_map),
        "map":          event_map,
    }
    return output


def resolve(event_id: str) -> dict | None:
    """単一イベントIDの解決（外部から呼び出し用）。"""
    if not OUTPUT_PATH.exists():
        print("[event_file_resolver] マップ未生成。先に main() を実行してください。")
        return None
    with open(OUTPUT_PATH, encoding="utf-8-sig") as f:
        data = json.load(f)
    return data["map"].get(event_id)


def main():
    print("[event_file_resolver] event_file_map生成開始...")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = build_map()
    with open(OUTPUT_PATH, "w", encoding="utf-8-sig") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[event_file_resolver] 完了: {result['mapped_count']} events mapped")
    print(f"[event_file_resolver] 出力: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

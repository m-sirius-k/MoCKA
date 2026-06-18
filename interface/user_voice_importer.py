#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user_voice_importer.py (TODO_139)
claude export / gpt export JSON -> MoCKA DB投入 -> essence更新 -> seal

Usage:
  python user_voice_importer.py <json_file>
  python user_voice_importer.py --watch   (watchdogモード)
"""
import sys
import os
import json
import re
import sqlite3
import argparse
import hashlib
import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = __import__('io').TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path("C:/Users/sirok/MoCKA")
DB_PATH = ROOT / "data" / "mocka_events.db"
IMPORT_DIR = Path("X:/down/mocka_import")
DONE_DIR   = IMPORT_DIR / "done"
MCP_URL    = "http://localhost:5002/agent/mocka_write_event"

# MoCKA関連キーワード (フィルタ)
MOCKA_KEYWORDS = [
    "mocka", "todo", "phase", "seal", "event", "incident",
    "guideline", "essence", "phi-os", "vasai", "orchestra", "relay",
    "caliber", "cursor", "claude", "chatgpt", "gpt", "gemini",
    "cloudflare", "notion", "github", "python", "endpoint",
    "utf-8", "cp932", "encoding", "bug", "error", "fix",
    "trust", "gate", "audit", "phi_os", "institution",
]

MOCKA_FILTER = re.compile(
    "|".join(MOCKA_KEYWORDS), re.IGNORECASE
)


def detect_format(data: dict | list) -> str:
    """Claude export vs GPT export の判定"""
    if isinstance(data, list):
        # GPT export: [{title, create_time, mapping, ...}, ...]
        if data and isinstance(data[0], dict) and "mapping" in data[0]:
            return "gpt"
        # Claude export: [{uuid, name, created_at, chat_messages, ...}]
        if data and isinstance(data[0], dict) and "chat_messages" in data[0]:
            return "claude"
    if isinstance(data, dict):
        if "mapping" in data:
            return "gpt"
        if "chat_messages" in data:
            return "claude"
    return "unknown"


def extract_human_messages_claude(data: list) -> list[dict]:
    """Claude export から human発言を抽出"""
    messages = []
    for conv in (data if isinstance(data, list) else [data]):
        title = conv.get("name", "")
        for msg in conv.get("chat_messages", []):
            if msg.get("sender") == "human":
                text = ""
                for content in msg.get("content", []):
                    if isinstance(content, dict) and content.get("type") == "text":
                        text += content.get("text", "")
                    elif isinstance(content, str):
                        text += content
                if text.strip():
                    messages.append({
                        "text": text.strip(),
                        "source": "claude",
                        "conversation": title,
                        "created_at": msg.get("created_at", ""),
                    })
    return messages


def extract_human_messages_gpt(data: list) -> list[dict]:
    """GPT export から human発言を抽出"""
    messages = []
    for conv in (data if isinstance(data, list) else [data]):
        title = conv.get("title", "")
        mapping = conv.get("mapping", {})
        for node_id, node in mapping.items():
            msg = node.get("message")
            if not msg:
                continue
            if msg.get("author", {}).get("role") != "user":
                continue
            parts = msg.get("content", {}).get("parts", [])
            text = " ".join(str(p) for p in parts if p).strip()
            if text:
                messages.append({
                    "text": text,
                    "source": "gpt",
                    "conversation": title,
                    "created_at": str(msg.get("create_time", "")),
                })
    return messages


def filter_mocka(messages: list[dict]) -> list[dict]:
    """MoCKA関連発言のみ残す"""
    return [m for m in messages if MOCKA_FILTER.search(m["text"])]


def insert_user_voices(messages: list[dict], source_file: str) -> int:
    """user_voice テーブルに投入 (重複スキップ)"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_voice (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_hash TEXT UNIQUE,
            text TEXT,
            source TEXT,
            conversation TEXT,
            created_at TEXT,
            imported_at TEXT,
            source_file TEXT
        )
    """)
    conn.commit()
    inserted = 0
    now = datetime.datetime.now().isoformat()
    for m in messages:
        h = hashlib.sha256(m["text"].encode("utf-8")).hexdigest()[:16]
        try:
            conn.execute(
                "INSERT OR IGNORE INTO user_voice "
                "(text_hash, text, source, conversation, created_at, imported_at, source_file) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (h, m["text"], m["source"], m["conversation"], m["created_at"], now, source_file)
            )
            if conn.execute("SELECT changes()").fetchone()[0]:
                inserted += 1
        except Exception as e:
            print(f"  [SKIP] insert error: {e}")
    conn.commit()
    conn.close()
    return inserted


def write_event(title: str, desc: str):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title, "description": desc,
            "tags": "user_voice,import,todo_139",
            "why_purpose": "user_voice自動取込",
            "how_trigger": "user_voice_importer.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST"
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


def run_essence_update():
    """essence自動更新 (ping_generator + seal)"""
    try:
        import subprocess
        subprocess.run(
            ["python", str(ROOT / "interface" / "ping_generator.py")],
            cwd=str(ROOT), timeout=30, check=False
        )
        print("  [OK] ping_generator completed")
    except Exception as e:
        print(f"  [WARN] ping_generator: {e}")


def process_file(json_path: Path) -> bool:
    """1ファイルを処理して完了フォルダに移動"""
    print(f"[IMPORT] {json_path.name}")
    try:
        raw = json_path.read_bytes()
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        data = json.loads(raw.decode("utf-8", errors="replace"))
    except Exception as e:
        print(f"  [ERROR] JSON parse: {e}")
        return False

    fmt = detect_format(data)
    print(f"  format: {fmt}")

    if fmt == "claude":
        messages = extract_human_messages_claude(data if isinstance(data, list) else [data])
    elif fmt == "gpt":
        messages = extract_human_messages_gpt(data if isinstance(data, list) else [data])
    else:
        print("  [ERROR] unknown format")
        return False

    filtered = filter_mocka(messages)
    print(f"  human messages: {len(messages)} -> MoCKA関連: {len(filtered)}")

    inserted = insert_user_voices(filtered, json_path.name)
    print(f"  inserted: {inserted} (duplicates skipped)")

    write_event(
        f"USER_VOICE_IMPORT: {json_path.name}",
        f"format={fmt} total={len(messages)} filtered={len(filtered)} inserted={inserted}"
    )

    # 完了フォルダへ移動
    DONE_DIR.mkdir(parents=True, exist_ok=True)
    dst = DONE_DIR / json_path.name
    json_path.rename(dst)
    print(f"  moved -> done/{json_path.name}")

    if inserted > 0:
        run_essence_update()

    return True


def watch_mode():
    """watchdogでIMPORT_DIRを監視"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("[ERROR] watchdog not installed: pip install watchdog")
        sys.exit(1)

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if event.is_directory:
                return
            p = Path(event.src_path)
            if p.suffix.lower() == ".json":
                import time; time.sleep(1)  # write complete wait
                process_file(p)

    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    observer = Observer()
    observer.schedule(Handler(), str(IMPORT_DIR), recursive=False)
    observer.start()
    print(f"[WATCH] Monitoring: {IMPORT_DIR}")
    print("[WATCH] Drop claude_export.json or gpt_export.json to import")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MoCKA user_voice importer (TODO_139)")
    parser.add_argument("file", nargs="?", help="JSONファイルパス")
    parser.add_argument("--watch", action="store_true", help="watchdogモード")
    args = parser.parse_args()

    if args.watch:
        watch_mode()
    elif args.file:
        process_file(Path(args.file))
    else:
        # 監視フォルダの既存ファイルを一括処理
        IMPORT_DIR.mkdir(parents=True, exist_ok=True)
        files = list(IMPORT_DIR.glob("*.json"))
        if not files:
            print(f"[INFO] no JSON files in {IMPORT_DIR}")
        for f in files:
            process_file(f)

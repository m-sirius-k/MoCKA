"""
tech_watcher.py  -- TIC Tech Watcher
外部ソースの変更を差分検知して evaluation_queue.jsonl に流す。
"""

import json
import sys
import io
import hashlib
import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TIC_DIR      = Path("C:/Users/sirok/MoCKA/data/tic")
SOURCES_PATH = TIC_DIR / "watch_sources.json"
HASHES_PATH  = TIC_DIR / "watch_hashes.json"
QUEUE_PATH   = TIC_DIR / "evaluation_queue.jsonl"
MCP_URL      = "http://localhost:5002/agent/mocka_write_event"

TIMEOUT = 15


def fetch_hash(url: str) -> tuple:
    """URL の HTML を取得して SHA-256 ハッシュ(16桁) を返す"""
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "MoCKA-TIC-Watcher/1.0"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            content = r.read()
        h = hashlib.sha256(content).hexdigest()[:16]
        return h, None
    except Exception as e:
        return None, str(e)


def load_hashes() -> dict:
    if HASHES_PATH.exists():
        return json.loads(HASHES_PATH.read_text(encoding="utf-8"))
    return {}


def save_hashes(hashes: dict):
    HASHES_PATH.parent.mkdir(parents=True, exist_ok=True)
    HASHES_PATH.write_text(json.dumps(hashes, ensure_ascii=False, indent=2), encoding="utf-8")


def next_queue_id() -> str:
    count = 0
    if QUEUE_PATH.exists():
        with open(QUEUE_PATH, encoding="utf-8") as f:
            count = sum(1 for _ in f)
    return f"TQ{(count + 1):03d}"


def append_queue(entry: dict):
    QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_event(title: str, description: str, tags: str = "tic,tech_watcher"):
    try:
        import urllib.request
        payload = json.dumps({
            "title": title, "description": description, "tags": tags,
            "why_purpose": "外部技術変更の差分監視",
            "how_trigger": "tech_watcher.py",
        }).encode("utf-8")
        req = urllib.request.Request(
            MCP_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


def run():
    if not SOURCES_PATH.exists():
        print(f"[ERROR] {SOURCES_PATH} not found")
        sys.exit(1)

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))["sources"]
    hashes  = load_hashes()
    now     = datetime.datetime.now().isoformat()

    print()
    print("=" * 50)
    print(f"  MoCKA Tech Watcher  {datetime.date.today()}")
    print("=" * 50)

    changed = []
    errors  = []

    for src in sources:
        sid  = src["id"]
        name = src["name"]
        url  = src["url"]

        h, err = fetch_hash(url)

        if err:
            print(f"  [ERROR ] {name}")
            print(f"           {err}")
            errors.append(src)
            write_event(
                f"TECH_WATCH_ERROR: {name}",
                f"URL取得失敗: {url} / {err}",
                "tic,tech_watcher,error",
            )
            continue

        prev = hashes.get(sid, {}).get("hash")

        if prev and prev != h:
            print(f"  [CHANGE] {name}")
            print(f"           前回: {prev}  今回: {h}")
            changed.append(src)

            entry = {
                "id": next_queue_id(),
                "detected_at": now,
                "source_id": sid,
                "source_name": name,
                "url": url,
                "status": "NEW",
                "impact_components": src.get("impact_components", []),
                "prev_hash": prev,
                "new_hash": h,
                "risk_score": None,
                "sandbox_result": None,
                "human_decision": None,
            }
            append_queue(entry)
            write_event(
                f"TECH_CHANGE_DETECTED: {name}",
                f"ハッシュ変更: {prev} -> {h} | URL: {url}",
                "tic,tech_watcher,change_detected",
            )
        else:
            status = "初回登録" if not prev else "変更なし"
            print(f"  [OK    ] {name}  ({status}, hash: {h})")
            write_event(
                f"TECH_WATCH_OK: {name}",
                f"変更なし hash={h}",
                "tic,tech_watcher,ok",
            )

        hashes[sid] = {"hash": h, "url": url, "checked_at": now, "name": name}

    save_hashes(hashes)

    print()
    print(f"  変更検出: {len(changed)}件  エラー: {len(errors)}件  正常: {len(sources)-len(changed)-len(errors)}件")
    print("=" * 50)
    print()

    return {"changed": changed, "errors": errors, "hashes": hashes}


if __name__ == "__main__":
    run()

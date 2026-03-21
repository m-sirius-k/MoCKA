import os
import json
import hashlib
from datetime import datetime
import csv

BASE = os.getcwd()
RUNTIME = os.path.join(BASE, "runtime")
INDEX = os.path.join(RUNTIME, "index")
DOCS = os.path.join(BASE, "docs")

CSV_PATH = os.path.join(INDEX, "event_timeline.csv")

TYPE_MAP = {
    "section": "sections",
    "partial": "partials",
    "incident": "incidents"
}

def ensure():
    os.makedirs(INDEX, exist_ok=True)
    for v in TYPE_MAP.values():
        os.makedirs(os.path.join(DOCS, v), exist_ok=True)

def csv_init():
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", encoding="utf-8-sig") as f:
            f.write("event_id,timestamp,type,subtype,title,source,storage_path,hash,status\n")

def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ★ 重複判定用ハッシュ（IDや時間を除外）
def content_hash(content, t, subtype):
    base = json.dumps({
        "type": t,
        "subtype": subtype,
        "content": content
    }, ensure_ascii=False, sort_keys=True)
    return sha(base)

def exists(hash_value):
    if not os.path.exists(CSV_PATH):
        return False
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["hash"] == hash_value:
                return True
    return False

def gid(p):
    return f"{p}_{int(datetime.utcnow().timestamp()*1000)}"

def save(content, t, subtype, title):
    ensure()
    csv_init()

    ts = datetime.utcnow().isoformat()
    eid = gid("E")
    did = gid("DOC")

    # ★ 正しい重複判定
    h = content_hash(content, t, subtype)

    if exists(h):
        print("SKIP: duplicate content")
        return

    folder = TYPE_MAP[t]
    rel = f"docs/{folder}/{did}.json"
    full = os.path.join(BASE, rel)

    data = {
        "id": did,
        "event_id": eid,
        "type": t,
        "subtype": subtype,
        "title": title,
        "created_at": ts,
        "source": "chat",
        "content": content,
        "hash": h
    }

    with open(full, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(CSV_PATH, "a", encoding="utf-8-sig") as f:
        f.write(f"{eid},{ts},{t},{subtype},{title},chat,{rel},{h},active\n")

def save_section(content, title):
    save(content, "section", "chat_section", title)

def save_partial(content, title):
    save(content, "partial", "copy_partial", title)

def save_incident(content, title):
    save(content, "incident", "incident_record", title)

import csv
import os
from datetime import datetime

EVENTS_CSV = r"C:\Users\sirok\MoCKA\data\events.csv"

FIELDNAMES = [
    "event_id","when","who_actor","what_type","where_component","where_path",
    "why_purpose","how_trigger","channel_type","lifecycle_phase","risk_level",
    "category_ab","target_class","title","short_summary",
    "before_state","after_state","change_type",
    "impact_scope","impact_result","related_event_id","trace_id","free_note"
]

def safe_value(v):
    if v is None:
        return ""
    v = str(v).replace("\n"," ").replace("\r"," ")
    return v[:500]

def next_event_id():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    n = 1
    if os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                eid = row.get("event_id","")
                if eid.startswith(prefix):
                    try:
                        num = int(eid.split("_")[1])
                        if num >= n:
                            n = num + 1
                    except:
                        pass
    return f"{prefix}{n:03d}"

def write_safe_csv(row):
    os.makedirs(os.path.dirname(EVENTS_CSV), exist_ok=True)

    base = {k:"" for k in FIELDNAMES}
    base.update(row)
    base = {k: safe_value(v) for k,v in base.items()}

    if not base["event_id"]:
        base["event_id"] = next_event_id()

    if not base["when"]:
        base["when"] = datetime.now().isoformat(timespec="seconds")

    write_header = not os.path.exists(EVENTS_CSV)

    with open(EVENTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL)
        if write_header:
            writer.writeheader()
        writer.writerow(base)

def save(title, summary=""):
    row = {
        "event_id": "",
        "when": "",
        "who_actor": "mocka_router",
        "what_type": "save",
        "where_component": "router",
        "where_path": "interface/router.py",
        "title": title,
        "short_summary": summary,
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",
        "channel_type": "internal"
    }
    write_safe_csv(row)
    print("[OK]", title)

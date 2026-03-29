import csv
import os
import json
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request

app = Flask(__name__)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
EVENTS_CSV = os.path.join(DATA_DIR, "events.csv")

BASE_DIR = ROOT_DIR
RECORDS_DIR = os.path.join(BASE_DIR, "records")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OLD_DIR = os.path.join(BASE_DIR, "OLD_FILES")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

# =========================
# 22蛻励ヵ繝ｫ繝｡繧ｿ繝ｻ繧ｹ繧ｭ繝ｼ繝・# =========================
FIELDNAMES = [
    "event_id",
    "when",
    "who_actor",
    "what_type",

    "where_component",
    "where_path",

    "why_purpose",
    "how_trigger",

    "channel_type",
    "lifecycle_phase",
    "risk_level",

    "category_ab",
    "target_class",

    "title",
    "short_summary",

    "before_state",
    "after_state",
    "change_type",

    "impact_scope",
    "impact_result",

    "related_event_id",
    "trace_id",

    "free_note",
]


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "master"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "summary"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "context"), exist_ok=True)
    os.makedirs(os.path.join(RECORDS_DIR, "audit"), exist_ok=True)

    os.makedirs(os.path.join(LOGS_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "structured"), exist_ok=True)
    os.makedirs(os.path.join(LOGS_DIR, "timeline"), exist_ok=True)

    os.makedirs(OLD_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, "decisions"), exist_ok=True)


def ensure_events_csv():
    ensure_dirs()
    if not os.path.exists(EVENTS_CSV):
        with open(EVENTS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def next_event_id():
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"E{today}_"
    ensure_events_csv()
    last_n = 0
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ev = (r.get("event_id") or "").strip()
            if ev.startswith(prefix):
                parts = ev.split("_")
                if len(parts) == 2:
                    try:
                        n = int(parts[1])
                        if n > last_n:
                            last_n = n
                    except ValueError:
                        pass
    return f"{prefix}{last_n+1:03d}"


def create_summary_and_context_templates(eid, name, summary, category, target):
    summary_path = os.path.join(RECORDS_DIR, "summary", f"{eid}.txt")
    if not os.path.exists(summary_path):
        line = f"{eid}: {name} / {summary} category={category}, target={target}"
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(line)

    context_path = os.path.join(RECORDS_DIR, "context", f"{eid}.md")
    if not os.path.exists(context_path):
        md = f"""# {eid} {name}

## 閭梧勹
縺薙％縺ｫ縲後↑縺懊％縺ｮ繧､繝吶Φ繝医′蠢・ｦ√□縺｣縺溘°縲阪ｒ譖ｸ縺上・
## 蝠城｡・縺薙％縺ｫ縲瑚ｧ｣豎ｺ縺励ｈ縺・→縺励◆蝠城｡後・繝ｪ繧ｹ繧ｯ縲阪ｒ譖ｸ縺上・
## 蛻､譁ｭ
{summary}

## 邨先棡
縺薙％縺ｫ縲檎樟譎らせ縺ｮ邨先棡繝ｻ蠖ｱ髻ｿ縲阪ｒ譖ｸ縺上・"""
        with open(context_path, "w", encoding="utf-8") as f:
            f.write(md)


def append_event(meta: dict):
    """
    22蛻励ヵ繝ｫ繝｡繧ｿ events.csv 縺ｫ1陦瑚ｿｽ險倥☆繧九・    - 譛ｪ謖・ｮ壼・縺ｯ縺吶∋縺ｦ "N/A" 縺ｧ蛻晄悄蛹・    - event_id / when 縺ｯ閾ｪ蜍戊｣懷ｮ・    """
    ensure_events_csv()

    row = {key: "N/A" for key in FIELDNAMES}
    for k, v in meta.items():
        if k in row and v is not None:
            row[k] = str(v)

    if row["event_id"] == "N/A":
        row["event_id"] = next_event_id()
    if row["when"] == "N/A":
        row["when"] = datetime.now().isoformat(timespec="seconds")

    eid = row["event_id"]
    name = row.get("title", "N/A")
    summary = row.get("short_summary", "N/A")
    category = row.get("category_ab", "N/A")
    target = row.get("target_class", "N/A")

    master_path = os.path.join(RECORDS_DIR, "master", f"{eid}.json")
    master_obj = {
        "event_id": eid,
        "timestamp": row["when"],
        "what_type": row.get("what_type", "N/A"),
        "status": "recorded",
        "category": category,
        "target": target,
    }
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master_obj, f, ensure_ascii=False, indent=2)

    with open(EVENTS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)

    create_summary_and_context_templates(eid, name, summary, category, target)


def load_history(limit=None):
    ensure_events_csv()
    rows = []
    with open(EVENTS_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            clean = {k: (v if v is not None else "") for k, v in r.items()}
            rows.append(clean)
    if limit is not None:
        rows = rows[-int(limit):]
    return rows


# =========================
# Flask 繝ｫ繝ｼ繝・# =========================

@app.route("/")
def index():
    return send_from_directory(ROOT_DIR, "index.html")


@app.route("/get_history")
def get_history():
    rows = load_history()
    return jsonify(rows)


@app.route("/ask", methods=["POST"])
def ask():
    """
    index.html 縺九ｉ縺ｮ POST: {c: 'A'|'B', o: 'infield'|...}
    縺薙％縺九ｉ 22蛻励Γ繧ｿ縺ｫ繝槭ャ繝斐Φ繧ｰ縺励※ append_event 縺ｫ貂｡縺吶・    """
    payload = request.get_json(force=True, silent=True) or {}
    c = payload.get("c")
    o = payload.get("o")
    memo = payload.get("memo", "").strip()
    o = payload.get("o")

    if c not in ("A", "B") or not o:
        return jsonify({"status": "error", "message": "invalid payload"}), 400

    if c == "A":
        what_type = "storage"
        title = f"菫晏ｭ・ {o}"
        short_summary = "Storage mission dispatched"
    else:
        what_type = "broadcast"
        title = f"蜈ｱ譛・ {o}"
        short_summary = "Broadcast mission dispatched"

    meta = {
        "what_type": what_type,
        "category_ab": c,
        "target_class": o,
        "title": title,
        "short_summary": memo if memo else short_summary,

        "who_actor": "human_nsjsiro",
        "where_component": "panel_ui",
        "where_path": "index.html",
        "why_purpose": "N/A",
        "how_trigger": "manual_click",
        "channel_type": "browser_ui",
        "lifecycle_phase": "in_operation",
        "risk_level": "normal",

        "before_state": "N/A",
        "after_state": "N/A",
        "change_type": "N/A",
        "impact_scope": "local",
        "impact_result": "N/A",
        "related_event_id": "N/A",
        "trace_id": "N/A",
        "free_note": memo if memo else "N/A",
    }

    append_event(meta)
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("--- MoCKA STARTING (Event Memory Core) ---")
    print(f"Directory: {ROOT_DIR}")
    ensure_dirs()
    ensure_events_csv()
    app.run(host="127.0.0.1", port=5000)

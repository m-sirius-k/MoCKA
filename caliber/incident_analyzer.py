"""
incident_analyzer.py
events.csvからインシデント/クレームを抽出し
Claude APIで5W1H + 否定5W1H → guidelines.json生成
使い方: python caliber/incident_analyzer.py [--all] [--event EVENT_ID]
"""
import argparse, csv, hashlib, json, os, re, requests
from datetime import datetime, timezone
from pathlib import Path

ROOT      = Path("C:/Users/sirok/MoCKA")
EVENTS    = ROOT / "data" / "events.csv"
GUIDELINES= ROOT / "data" / "guidelines.json"
API_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
API_URL   = "https://api.anthropic.com/v1/messages"
MODEL     = "claude-sonnet-4-20250514"
UTC       = timezone.utc

INCIDENT_TYPES = ["incident", "error", "complaint", "クレーム", "インシデント", "failure", "bug"]

def load_guidelines():
    if GUIDELINES.exists():
        return json.load(open(GUIDELINES, encoding="utf-8"))
    return {"guidelines": [], "meta": {"version": "1.0", "created": datetime.now(UTC).isoformat()}}

def save_guidelines(data):
    GUIDELINES.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, open(GUIDELINES, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[OK] guidelines.json saved: {len(data['guidelines '])} entries")

def load_events():
    if not EVENTS.exists(): return []
    rows = []
    with open(EVENTS, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(dict(row))
    return rows

def is_incident(row):
    text = " ".join([row.get("what_type",""), row.get("title",""), row.get("free_note",""), row.get("short_summary","")]).lower()
    return any(t in text for t in INCIDENT_TYPES)

def call_claude(prompt):
    if not API_KEY:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        return None
    headers = {"x-api-key": API_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    body = {
        "model": MODEL,
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": prompt}]
    }
    r = requests.post(API_URL, headers=headers, json=body, timeout=60)
    if r.status_code != 200:
        print(f"[ERROR] API {r.status_code}: {r.text[:200]}")
        return None
    return r.json()["content"][0]["text"]

def analyze_incident(row):
    event_id = row.get("event_id", "")
    title = row.get("title", "")
    summary = row.get("short_summary", "")
    note = row.get("free_note", "")
    when = row.get("when", "")
    who = row.get("who_actor", "")
    what = row.get("what_type", "")
    where = row.get("where_component", "")

    prompt = f"""以下のインシデント/クレーム記録を分析し、JSONのみで回答してください。余分な説明は不要です。

【インシデント記録】
- event_id: {event_id}
- 日時: {when}
- 担当: {who}
- 種別: {what}
- 場所: {where}
- タイトル: {title}
- 概要: {summary}
- 備考: {note}

以下のJSON形式で回答してください:
{{
  "5w1h": {{
    "who": "誰が",
    "when": "いつ",
    "where": "どこで",
    "what": "何を",
    "why": "なぜ",
    "how": "どのように"
  }},
  "negation_5w1h": {{
    "who": "誰が（防止主体）",
    "when": "いつまでに",
    "where": "どこで（防止場所）",
    "what": "何をしてはならないか",
    "why": "なぜ防止が必要か",
    "how": "どのように防止するか"
  }},
  "root_cause": "根本原因（1文）",
  "prevention_action": "具体的防止策（1文）",
  "recurrence_probability": "再発確率（high/medium/low）",
  "guideline_text": "行動指針（命令形・1文）"
}}"""

    print(f"[ANALYZE] {event_id}: {title[:40]}")
    result = call_claude(prompt)
    if not result: return None

    try:
        m = re.search(r"\{.*\}", result, re.DOTALL)
        if m: return json.loads(m.group())
    except: pass
    print(f"[WARN] JSON parse failed for {event_id}")
    return None

def generate_guideline_id():
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    return f"GL_{ts}"

def process_event(row, guidelines_data):
    event_id = row.get("event_id", "")
    existing_ids = [g.get("source_event_ids", []) for g in guidelines_data["guidelines"]]
    existing_flat = [eid for sublist in existing_ids for eid in sublist]
    if event_id in existing_flat:
        print(f"[SKIP] {event_id} already analyzed")
        return False

    analysis = analyze_incident(row)
    if not analysis: return False

    gl_id = generate_guideline_id()
    h = hashlib.sha256((gl_id + event_id).encode()).hexdigest()[:8]
    gl_id = gl_id + "_" + h

    guideline = {
        "guideline_id": gl_id,
        "source_event_ids": [event_id],
        "created": datetime.now(UTC).isoformat(),
        "event_title": row.get("title", ""),
        "event_type": row.get("what_type", ""),
        "5w1h": analysis.get("5w1h", {}),
        "negation_5w1h": analysis.get("negation_5w1h", {}),
        "root_cause": analysis.get("root_cause", ""),
        "prevention_action": analysis.get("prevention_action", ""),
        "recurrence_probability": analysis.get("recurrence_probability", ""),
        "guideline_text": analysis.get("guideline_text", ""),
        "trust_score": 0.5,
        "validation_status": "pending",
        "evidence_chain": [event_id],
        "applied_count": 0,
        "improvement_rate": None
    }
    guidelines_data["guidelines"].append(guideline)
    print(f"[OK] guideline created: {gl_id}")
    print(f"     指針: {guideline['guideline_text ']}")
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="全インシデントを分析")
    parser.add_argument("--event", help="特定event_idを分析")
    parser.add_argument("--list", action="store_true", help="既存guidelines一覧")
    args = parser.parse_args()

    guidelines_data = load_guidelines()

    if args.list:
        gls = guidelines_data["guidelines"]
        print(f"[guidelines.json] {len(gls)} entries")
        for g in gls:
            print(f"  {g['guideline_id ']} [{g['validation_status ']}] {g['guideline_text '][:60]}")
        return

    events = load_events()
    incidents = [r for r in events if is_incident(r)]
    print(f"[INFO] events: {len(events)} / incidents: {len(incidents)}")

    if args.event:
        target = [r for r in events if r.get("event_id") == args.event]
        if not target:
            print(f"[ERROR] event not found: {args.event}")
            return
        process_event(target[0], guidelines_data)
    elif args.all:
        count = 0
        for row in incidents:
            if process_event(row, guidelines_data):
                count += 1
        print(f"[DONE] {count} guidelines generated")
    else:
        if not incidents:
            print("[INFO] no incidents found")
            return
        process_event(incidents[-1], guidelines_data)

    save_guidelines(guidelines_data)

if __name__ == "__main__":
    main()
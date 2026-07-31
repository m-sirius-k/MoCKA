import argparse, sqlite3, os, sys
from datetime import datetime, timezone
from pathlib import Path

MOCKA_DB_PATH = Path(os.environ.get("MOCKA_DB_PATH", r"C:\Users\sirok\MoCKA\data\mocka_events.db"))
NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_DB_IDS = {
    "decisions": "5381e156-b742-4906-9b94-7e90f2842456",
    "events":    "04071d78-33af-4b8e-a554-22f0cd854980",
    "incidents": "99ed2fc3-fc22-4315-89af-73a50b7b1919",
}
DECISION_TYPES = ("DECISION_APPROVED", "phl_decision", "DECISION_REJECTED")
INCIDENT_TYPES = ("INCIDENT", "incident", "OVERDUE_INCIDENT")

def get_conn():
    return sqlite3.connect(str(MOCKA_DB_PATH))

def check_types():
    conn = get_conn()
    rows = conn.execute("SELECT what_type, COUNT(*) FROM events GROUP BY what_type ORDER BY 2 DESC").fetchall()
    conn.close()
    for r in rows: print(f"  {r[0]:50s} {r[1]:>6}")

def get_decisions(since=None):
    conn = get_conn()
    ph = ",".join("?"*len(DECISION_TYPES))
    q = f"SELECT event_id,COALESCE(title,short_summary,'') AS title,what_type,when_ts,who_actor,COALESCE(short_summary,'') AS summary,severity,lifecycle_phase,free_note FROM events WHERE what_type IN ({ph})"
    p = list(DECISION_TYPES)
    if since: q += " AND when_ts >= ?"; p.append(since)
    q += " ORDER BY when_ts DESC"
    cur = conn.execute(q, p)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols,r)) for r in cur.fetchall()]
    conn.close()
    return rows

def get_events(since=None, limit=500):
    conn = get_conn()
    q = "SELECT event_id,what_type,when_ts,COALESCE(short_summary,title,'') AS summary,lifecycle_phase,related_event_id,COALESCE(severity,'normal') AS severity FROM events WHERE 1=1"
    p = []
    if since: q += " AND when_ts >= ?"; p.append(since)
    q += " ORDER BY when_ts DESC LIMIT ?"; p.append(limit)
    cur = conn.execute(q, p)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols,r)) for r in cur.fetchall()]
    conn.close()
    return rows

def get_incidents():
    conn = get_conn()
    ph = ",".join("?"*len(INCIDENT_TYPES))
    q = f"SELECT event_id,risk_level,COALESCE(severity,'Normal') AS severity,when_ts,COALESCE(short_summary,title,'') AS summary,before_state,related_event_id,after_state FROM events WHERE what_type IN ({ph}) ORDER BY when_ts DESC"
    cur = conn.execute(q, list(INCIDENT_TYPES))
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols,r)) for r in cur.fetchall()]
    conn.close()
    return rows

def get_stats():
    conn = get_conn()
    ph_d = ",".join("?"*len(DECISION_TYPES))
    ph_i = ",".join("?"*len(INCIDENT_TYPES))
    s = {
        "total_events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
        "total_decisions": conn.execute(f"SELECT COUNT(*) FROM events WHERE what_type IN ({ph_d})", list(DECISION_TYPES)).fetchone()[0],
        "open_incidents": conn.execute(f"SELECT COUNT(*) FROM events WHERE what_type IN ({ph_i})", list(INCIDENT_TYPES)).fetchone()[0],
    }
    conn.close()
    return s

def txt(v, n=2000):
    return [{"text":{"content":str(v or "")[:n]}}]

def parse_date(v):
    """when_ts から ISO 8601 日付 (YYYY-MM-DD) を安全に抽出"""
    s = str(v or "").strip()
    if not s:
        return None
    # YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    # 20260429_112308 形式
    if len(s) >= 8 and s[:8].isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    return None

def notion_post(endpoint, payload):
    import requests
    r = requests.post(f"{NOTION_API_BASE}/{endpoint}",
        headers={"Authorization":f"Bearer {NOTION_API_KEY}","Content-Type":"application/json","Notion-Version":"2022-06-28"},
        json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def push_decision(d):
    st = "Active" if d.get("what_type") == "DECISION_APPROVED" else "Archived"
    props = {
        "Decision ID":{"title":txt(d.get("event_id",""),100)},
        "Title":{"rich_text":txt(d.get("title",""))},
        "Status":{"select":{"name":st}},
        "Approved By":{"rich_text":txt(d.get("who_actor",""),500)},
        "Summary":{"rich_text":txt(d.get("summary",""))},
    }
    dt = parse_date(d.get("when_ts",""))
    if dt: props["Approved Date"]={"date":{"start":dt}}
    if d.get("free_note"): props["Paper Reference"]={"rich_text":txt(d["free_note"],500)}
    if NOTION_API_KEY:
        try:
            res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["decisions"]},"properties":props})
            return bool(res.get("id"))
        except Exception as e:
            print(f"  [SKIP decision] {e}")
            return False
    print(f"  [DRY] decision {str(d.get('event_id',''))[:30]} / {str(d.get('title',''))[:40]}")
    return True

def push_event(e):
    raw = str(e.get("what_type","")).upper()
    etype = {"DECISION_APPROVED":"Decision","PHL_DECISION":"Decision","DECISION_REJECTED":"Decision",
             "INCIDENT":"Incident","OVERDUE_INCIDENT":"Incident","AUTO_SEAL_PENDING":"Seal","SEAL_READY":"Seal"}.get(raw,"Implementation")
    sev = {"critical":"Critical","high":"High","normal":"Normal","low":"Info","info":"Info"}.get(str(e.get("severity","")).lower(),"Normal")
    ph = {"genesis":"Genesis","phase1":"Phase1","phase2":"Phase2","phase3":"Phase3","phase4":"Phase4"}.get(str(e.get("lifecycle_phase","")).lower().replace(" ","").replace("-",""),"Phase4")
    props = {
        "Event ID":{"title":txt(e.get("event_id",""),100)},
        "Type":{"select":{"name":etype}},
        "Severity":{"select":{"name":sev}},
        "Phase":{"select":{"name":ph}},
        "Summary":{"rich_text":txt(e.get("summary",""))},
    }
    dt = parse_date(e.get("when_ts",""))
    if dt: props["Date"]={"date":{"start":dt}}
    if e.get("related_event_id"): props["Related Decision"]={"rich_text":txt(e["related_event_id"],200)}
    if NOTION_API_KEY:
        try:
            res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["events"]},"properties":props})
            return bool(res.get("id"))
        except Exception as e:
            print(f"  [SKIP event] {e}")
            return False
    print(f"  [DRY] event {str(e.get('event_id',''))[:30]} / {etype} / {dt}")
    return True

def push_incident(i):
    sev = {"critical":"Critical","high":"High","normal":"Normal","low":"Low"}.get(str(i.get("severity","")).lower(),"Normal")
    props = {
        "Incident ID":{"title":txt(i.get("event_id",""),100)},
        "Status":{"select":{"name":"Resolved"}},
        "Severity":{"select":{"name":sev}},
        "Summary":{"rich_text":txt(i.get("summary",""))},
    }
    dt = parse_date(i.get("when_ts",""))
    if dt: props["Occurred Date"]={"date":{"start":dt}}
    if i.get("before_state"): props["Root Cause"]={"rich_text":txt(i["before_state"])}
    if i.get("after_state"): props["Resolution"]={"rich_text":txt(i["after_state"])}
    if NOTION_API_KEY:
        try:
            res = notion_post("pages",{"parent":{"database_id":NOTION_DB_IDS["incidents"]},"properties":props})
            return bool(res.get("id"))
        except Exception as e:
            print(f"  [SKIP incident] {e}")
            return False
    print(f"  [DRY] incident {str(i.get('event_id',''))[:30]}")
    return True

def main():
    global MOCKA_DB_PATH
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["all","check","decisions","events","incidents","dashboard"], default="all")
    parser.add_argument("--since", default=None)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--db-path", default=str(MOCKA_DB_PATH))
    args = parser.parse_args()
    MOCKA_DB_PATH = Path(args.db_path)
    if not MOCKA_DB_PATH.exists():
        print(f"[ERROR] DB not found: {MOCKA_DB_PATH}"); sys.exit(1)

    if args.target == "check":
        check_types()
    elif args.target == "decisions":
        items = get_decisions(args.since)
        ok = sum(1 for d in items if push_decision(d))
        print(f"[SYNC] Decisions: {ok}/{len(items)}")
    elif args.target == "events":
        items = get_events(args.since, args.limit)
        ok = sum(1 for e in items if push_event(e))
        print(f"[SYNC] Events: {ok}/{len(items)}")
    elif args.target == "incidents":
        items = get_incidents()
        ok = sum(1 for i in items if push_incident(i))
        print(f"[SYNC] Incidents: {ok}/{len(items)}")
    elif args.target == "dashboard":
        print(get_stats())
    elif args.target == "all":
        check_types(); print()
        d = get_decisions(args.since); ok_d = sum(1 for x in d if push_decision(x))
        print(f"[SYNC] Decisions: {ok_d}/{len(d)}")
        e = get_events(args.since, args.limit); ok_e = sum(1 for x in e if push_event(x))
        print(f"[SYNC] Events: {ok_e}/{len(e)}")
        i = get_incidents(); ok_i = sum(1 for x in i if push_incident(x))
        print(f"[SYNC] Incidents: {ok_i}/{len(i)}")
        print(f"[SYNC] Stats: {get_stats()}")
        print(f"[SYNC] ALL DONE")

if __name__ == "__main__":
    main()

import sqlite3, requests, os, json

k = os.environ.get('NOTION_API_KEY', '')
DB = r'C:\Users\sirok\MoCKA\data\mocka_events.db'
DB_ID = '5381e156-b742-4906-9b94-7e90f2842456'

def txt(v, n=2000):
    return [{"text": {"content": str(v or "")[:n]}}]

conn = sqlite3.connect(DB)
rows = conn.execute(
    "SELECT event_id,title,what_type,when_ts,who_actor,short_summary,free_note "
    "FROM events WHERE what_type IN ('DECISION_APPROVED','phl_decision','DECISION_REJECTED') "
    "ORDER BY when_ts DESC"
).fetchall()
conn.close()

for row in rows:
    event_id, title, what_type, when_ts, who_actor, summary, free_note = row
    status = "Active" if what_type == "DECISION_APPROVED" else "Archived"
    props = {
        "Decision ID": {"title": txt(event_id, 100)},
        "Title": {"rich_text": txt(title)},
        "Status": {"select": {"name": status}},
        "Approved By": {"rich_text": txt(who_actor, 500)},
        "Summary": {"rich_text": txt(summary)},
    }
    dt = str(when_ts or "")[:10]
    if len(dt) == 10:
        props["Approved Date"] = {"date": {"start": dt}}
    if free_note:
        props["Paper Reference"] = {"rich_text": txt(free_note, 500)}

    r = requests.post('https://api.notion.com/v1/pages',
        headers={'Authorization': 'Bearer ' + k, 'Content-Type': 'application/json', 'Notion-Version': '2022-06-28'},
        json={'parent': {'database_id': DB_ID}, 'properties': props})

    if r.status_code != 200:
        print(f"FAIL {event_id}: {r.text[:300]}")
        print(f"  who_actor={repr(who_actor)[:80]}")
        print(f"  title={repr(title)[:80]}")
        break
    else:
        print(f"OK {event_id}")

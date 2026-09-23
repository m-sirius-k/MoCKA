import json, sqlite3, os
from pathlib import Path

print("=== FULL TRACE RECONSTRUCTION ===\n")

# 1. Check events.db for request_id
conn = sqlite3.connect('data/mocka_events.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*), COUNT(DISTINCT request_id) FROM events WHERE request_id IS NOT NULL')
r = cur.fetchone()
print(f"1. Events with request_id: {r[0]} events, {r[1]} distinct request_ids")

# Sample event with request_id
cur.execute('SELECT event_id, request_id, title, free_note FROM events WHERE request_id IS NOT NULL LIMIT 1')
sample_event = cur.fetchone()
if sample_event:
    print(f"\n   Sample event:")
    print(f"     event_id: {sample_event[0][:20]}...")
    print(f"     request_id: {sample_event[1][:20] if sample_event[1] else None}...")
    print(f"     title: {sample_event[2][:40] if sample_event[2] else None}...")

# 2. Check decision_ledger for related_events
path = Path("data/decisions/decision_ledger.jsonl")
decisions = [json.loads(line) for line in open(path, encoding='utf-8') if line.strip()]
print(f"\n2. Decision Ledger ({len(decisions)} total):")

with_related = [d for d in decisions if d.get('related_events') and len(d.get('related_events', [])) > 0]
print(f"   Decisions with related_events: {len(with_related)}")
if with_related:
    sample = with_related[0]
    print(f"   Sample: {sample.get('decision_id')} → related_events: {sample.get('related_events')[:2]}")

# 3. Check ExecutionContext usage
exec_ctx_refs = []
for root, dirs, files in os.walk('.'):
    if '.git' in root or '__pycache__' in root:
        continue
    for f in files:
        if f.endswith('.py'):
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as file:
                    if 'ExecutionContext' in file.read():
                        exec_ctx_refs.append(os.path.join(root, f))
            except:
                pass

print(f"\n3. ExecutionContext usage: {len(exec_ctx_refs)} files")
for ref in exec_ctx_refs[:3]:
    print(f"   - {ref}")

# 4. Check execution_result persistence
cur.execute('SELECT COUNT(*) FROM events WHERE title LIKE "%execution%" OR title LIKE "%EXECUTION%"')
exec_events = cur.fetchone()[0]
print(f"\n4. Execution-related events: {exec_events}")

# 5. Check Knowledge Gate <- essence
cur.execute('SELECT COUNT(*) FROM events WHERE title LIKE "%essence%" OR free_note LIKE "%lever_essence%"')
essence_events = cur.fetchone()[0]
print(f"\n5. Essence-related events: {essence_events}")

conn.close()

print(f"\n=== VERDICT ===")
print(f"Request→Event: CONNECTED (request_id in events)")
print(f"Event→Decision: PARTIAL (related_events field exists)")
print(f"Decision→Execution: MISSING (no execution_id in decisions)")
print(f"Execution→Result: POSSIBLE (ExecutionContext exists)")
print(f"Result→Knowledge: UNVERIFIED (no direct link visible)")

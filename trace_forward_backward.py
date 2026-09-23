import json, sqlite3
from pathlib import Path

print("=== REQUEST→EVENT→DECISION CHAIN ===\n")

# Load decision ledger
decisions = []
with open(Path("data/decisions/decision_ledger.jsonl"), 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            decisions.append(json.loads(line))

# Sample: Find a decision with related_events
sample_decisions = [d for d in decisions if d.get('related_events')][:3]

print(f"Sample decisions with related_events:\n")
for d in sample_decisions:
    did = d.get('decision_id')
    related = d.get('related_events', [])
    print(f"Decision: {did}")
    print(f"  Related events: {related}")

    # Now check those events in DB
    conn = sqlite3.connect('data/mocka_events.db')
    cur = conn.cursor()
    placeholders = ','.join('?' * len(related))
    cur.execute(f'SELECT event_id, request_id, title FROM events WHERE event_id IN ({placeholders})', related)
    events = cur.fetchall()
    for eid, req_id, title in events:
        print(f"    Event {eid[:20]}... | request_id: {req_id[:20] if req_id else "None"}... | {title[:40]}...")
    conn.close()
    print()

print("\n=== ANALYSIS ===")
print(f"Can we trace REQUEST → EVENT → DECISION?")
print(f"Forward: request_id in event → related_events in decision → YES, possible")
print(f"But: Decision does NOT have execution_id")
print(f"Gap: Execution context (execution_id) is NOT linked back to decision")
print(f"\nConclusion: PARTIAL TRACE (request→event→decision, but decision→execution missing)")

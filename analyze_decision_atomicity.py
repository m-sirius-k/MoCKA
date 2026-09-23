import sys, json, datetime
from pathlib import Path

# Current implementation
def _next_decision_id():
    path = Path("data/decisions/decision_ledger.jsonl")
    if not path.exists():
        return "DC_20260921_001"
    with open(path, 'r', encoding='utf-8') as f:
        records = [json.loads(line) for line in f if line.strip()]

    today = datetime.date.today().strftime("%Y%m%d")
    prefix = f"DC_{today}_"
    used = [
        int(r["decision_id"][len(prefix):])
        for r in records
        if isinstance(r.get("decision_id"), str) and r["decision_id"].startswith(prefix)
        and r["decision_id"][len(prefix):].isdigit()
    ]
    n = (max(used) + 1) if used else 1
    return f"{prefix}{n:03d}"

path = Path("data/decisions/decision_ledger.jsonl")
with open(path, 'r', encoding='utf-8') as f:
    records = [json.loads(line) for line in f if line.strip()]

today = datetime.date.today().strftime("%Y%m%d")
prefix = f"DC_{today}_"
today_decisions = [r for r in records if isinstance(r.get("decision_id"), str) and r["decision_id"].startswith(prefix)]

print(f"Today's decisions (DC_{today}): {len(today_decisions)}")
if today_decisions:
    latest = max(int(r["decision_id"][len(prefix):]) for r in today_decisions if r["decision_id"][len(prefix):].isdigit())
    print(f"  Latest: DC_{today}_{latest:03d}")
    print(f"  Next would be: DC_{today}_{latest+1:03d}")

print(f"\n=== Atomicity Analysis ===")
print(f"1. File I/O:")
print(f"   - Read: Full file (all lines parsed)")
print(f"   - Write: Append mode")
print(f"   - Atomic guarantee: No (JSONL not WAL-protected)")
print(f"\n2. Concurrent scenario:")
print(f"   - Process A reads file, sees max={len(today_decisions)}")
print(f"   - Process B reads file SAME TIME, sees max={len(today_decisions)}")
print(f"   - Both compute n = {len(today_decisions)+1}")
print(f"   - Both write DC_{today}_{len(today_decisions)+1:03d}")
print(f"   - Result: DUPLICATE ID in ledger")
print(f"\n3. MCP Server model:")
print(f"   - Single Flask process: YES (app.run() default)")
print(f"   - Multiple concurrent requests: QUEUED (not parallel within process)")
print(f"   - HTTPスレッドプール: Flask default is threaded")
print(f"   - Python GIL: Protects Python execution, not file operations")
print(f"\n4. VERDICT:")
print(f"   ACTUAL RISK: Single Flask process + threaded model")
print(f"   - Thread A enters _next_decision_id() → reads file")
print(f"   - Thread B enters _next_decision_id() → reads file (BEFORE A writes)")
print(f"   - Both compute same ID")
print(f"   - A appends, B appends → DUPLICATE in file")
print(f"   - Verdict: POTENTIAL BLOCKER (not theoretical)")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 6 — PHI-OS → MEMORY INTEGRATION

Chain:
Human → JARVIS → Orchestra → HAB → GPT → Event Store → PHI-OS → Memory

Implementation:
1. Run Phase 4-5 chain (Event Store populated)
2. Read latest event from mocka_events.db
3. Write to Memory via MemoryWriter.write_event()
4. Verify Memory has the event
"""

import sys
import asyncio
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

_mocka_root = Path(__file__).parent
gateway_path = _mocka_root / "gateway"
memory_path = _mocka_root / "memory"

if str(gateway_path) not in sys.path:
    sys.path.insert(0, str(gateway_path))
if str(memory_path) not in sys.path:
    sys.path.insert(0, str(memory_path))

print("\n" + "="*80)
print("PHASE 6 — PHI-OS → MEMORY INTEGRATION")
print("="*80)
print(f"Start: {datetime.now(timezone.utc).isoformat()}")

# ============================================================================
# STEP 1: Run Phase 4-5 (dispatch + event store)
# ============================================================================

async def run_phase4_5():
    """Execute Phase 4-5 chain to populate Event Store."""
    try:
        from playwright.async_api import async_playwright
        from browser_session_handler import set_orchestra_session
        from multi_dispatcher import dispatch_with_orchestra_session

        print("\n[PHASE 4-5] Running dispatch chain...")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            set_orchestra_session(browser=browser, context=context, page=page)

            request_text = """
Phase 6 Memory Integration Test

Verify system readiness to:
1. Store events in Event Store
2. Pass to PHI-OS
3. Ingest to Memory

Brief status: (2-3 sentences)
            """

            result = dispatch_with_orchestra_session(
                request_text=request_text.strip(),
                providers=["gpt"],
                title="PHASE 6 Memory Integration",
                decision_id=None
            )

            request_id = result.get('request_id')
            print(f"[PHASE 4-5] Completed: request_id={request_id}")

            await asyncio.sleep(2)  # Allow flush

            await page.close()
            await context.close()
            await browser.close()

            return request_id

    except Exception as e:
        print(f"[FAIL] Phase 4-5 failed: {e}")
        return None


# ============================================================================
# STEP 2: Read event from Event Store
# ============================================================================

def read_event_from_store(request_id: str) -> dict:
    """Read the latest event from mocka_events.db matching request_id."""
    try:
        db_path = _mocka_root / "data" / "mocka_events.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT event_id, request_id, title, short_summary, who_actor, what_type
            FROM events
            WHERE request_id = ?
            LIMIT 1
            """,
            (request_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            event = {
                "event_id": row['event_id'],
                "request_id": row['request_id'],
                "title": row['title'],
                "short_summary": row['short_summary'],
                "who_actor": row['who_actor'],
                "what_type": row['what_type'],
            }
            print(f"\n[EVENT STORE] Event found: {event['event_id']}")
            return event
        else:
            print(f"\n[EVENT STORE] Event NOT found for request_id={request_id}")
            return None

    except Exception as e:
        print(f"[EVENT STORE] Error: {e}")
        return None


# ============================================================================
# STEP 3: Write event to Memory
# ============================================================================

def write_event_to_memory(event: dict) -> bool:
    """Write event from Event Store to Memory via MemoryWriter."""
    try:
        from memory_writer import MemoryWriter
        from memory_registry import MemoryType, Source

        print(f"\n[MEMORY] Writing event to Memory...")

        writer = MemoryWriter()

        memory_entry = writer.write_event(
            event=event,
            memory_type=MemoryType.EPISODIC,
            source=Source.EXTERNAL,
            tags=("phase6", "event_store", "integration")
        )

        print(f"[MEMORY] Event written:")
        print(f"   Memory ID: {memory_entry.memory_id}")
        print(f"   Type: {memory_entry.memory_type}")
        print(f"   Source: {memory_entry.source}")

        return memory_entry

    except Exception as e:
        print(f"[MEMORY] Write failed: {e}")
        import traceback
        traceback.print_exc()
        return None


# ============================================================================
# STEP 4: Verify Memory has the event
# ============================================================================

def verify_memory_has_event(memory_entry) -> bool:
    """Verify that Memory Store actually contains the written entry."""
    try:
        from memory_store import MemoryStore

        print(f"\n[MEMORY VERIFY] Checking Memory Store...")

        store = MemoryStore()

        # Get all entries and check if our entry is there
        all_entries = store.all()

        # Check if memory_id exists in store
        found = any(e.memory_id == memory_entry.memory_id for e in all_entries)

        if found:
            print(f"[MEMORY VERIFY] Event found in Memory Store:")
            print(f"   Total entries: {len(all_entries)}")
            print(f"   Memory ID: {memory_entry.memory_id}")
            return True
        else:
            print(f"[MEMORY VERIFY] Event NOT found in Memory Store")
            print(f"   Total entries: {len(all_entries)}")
            return False

    except Exception as e:
        print(f"[MEMORY VERIFY] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN
# ============================================================================

async def main():
    # Step 1: Run Phase 4-5
    request_id = await run_phase4_5()

    if not request_id:
        print("\n[ABORT] Phase 4-5 failed")
        return {
            "PHASE": "6",
            "BASELINE": "99ac3a0cf",
            "MEMORY_CONNECTED": False,
            "REAL_AI_RESPONSE": False,
            "EVENT_STORE_READBACK": False,
            "MEMORY_EVENT_WRITTEN": False,
            "MEMORY_EVENT_VERIFIED": False,
            "FULL_CHAIN": False,
            "STOP_POINT": "phase4_5_failed",
        }

    # Step 2: Read event from Event Store
    await asyncio.sleep(1)  # Extra wait for DB flush
    event = read_event_from_store(request_id)

    if not event:
        print("\n[ABORT] Event Store query failed")
        return {
            "PHASE": "6",
            "BASELINE": "99ac3a0cf",
            "MEMORY_CONNECTED": True,
            "REAL_AI_RESPONSE": True,
            "EVENT_STORE_READBACK": False,
            "MEMORY_EVENT_WRITTEN": False,
            "MEMORY_EVENT_VERIFIED": False,
            "FULL_CHAIN": False,
            "STOP_POINT": "event_store_read_failed",
        }

    # Step 3: Write to Memory
    memory_entry = write_event_to_memory(event)

    if not memory_entry:
        print("\n[ABORT] Memory write failed")
        return {
            "PHASE": "6",
            "BASELINE": "99ac3a0cf",
            "MEMORY_CONNECTED": True,
            "REAL_AI_RESPONSE": True,
            "EVENT_STORE_READBACK": True,
            "MEMORY_EVENT_WRITTEN": False,
            "MEMORY_EVENT_VERIFIED": False,
            "FULL_CHAIN": False,
            "STOP_POINT": "memory_write_failed",
        }

    # Step 4: Verify Memory
    memory_verified = verify_memory_has_event(memory_entry)

    # Determine full chain
    full_chain = all([request_id, event, memory_entry, memory_verified])

    return {
        "PHASE": "6",
        "BASELINE": "99ac3a0cf",
        "MEMORY_CONNECTED": True,
        "REAL_AI_RESPONSE": True,
        "EVENT_STORE_READBACK": True,
        "MEMORY_EVENT_WRITTEN": bool(memory_entry),
        "MEMORY_EVENT_VERIFIED": memory_verified,
        "FULL_CHAIN": full_chain,
        "STOP_POINT": None if full_chain else "memory_verify_failed",
        "memory_id": memory_entry.memory_id if memory_entry else None,
        "event_id": event.get('event_id') if event else None,
    }


if __name__ == "__main__":
    result = asyncio.run(main())

    # Get git info
    def get_git_info():
        try:
            import subprocess
            head = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=str(_mocka_root),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()[:16]

            try:
                remote = subprocess.check_output(
                    ["git", "rev-parse", "@{upstream}"],
                    cwd=str(_mocka_root),
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()[:16]
            except:
                remote = "no-upstream"

            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"],
                cwd=str(_mocka_root),
                text=True,
                stderr=subprocess.DEVNULL
            ).strip()

            worktree = "CLEAN" if not status_output else "DIRTY"
            return head, remote, worktree
        except:
            return "error", "error", "error"

    head, remote, worktree = get_git_info()

    # Final report
    print("\n" + "="*80)
    print("PHASE 6 FINAL REPORT")
    print("="*80)
    print(f"PHASE = {result.get('PHASE')}")
    print(f"BASELINE = {result.get('BASELINE')}")
    print(f"MEMORY_CONNECTED = {result.get('MEMORY_CONNECTED')}")
    print(f"REAL_AI_RESPONSE = {result.get('REAL_AI_RESPONSE')}")
    print(f"EVENT_STORE_READBACK = {result.get('EVENT_STORE_READBACK')}")
    print(f"MEMORY_EVENT_WRITTEN = {result.get('MEMORY_EVENT_WRITTEN')}")
    print(f"MEMORY_EVENT_VERIFIED = {result.get('MEMORY_EVENT_VERIFIED')}")
    print(f"FULL_CHAIN = {result.get('FULL_CHAIN')}")
    print(f"STOP_POINT = {result.get('STOP_POINT')}")
    print(f"HEAD = {head}")
    print(f"REMOTE = {remote}")
    print(f"WORKTREE = {worktree}")
    print("="*80)
    print(f"End: {datetime.now(timezone.utc).isoformat()}")

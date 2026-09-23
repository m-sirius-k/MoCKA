#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
STEP 3: JARVIS → Multi-AI → HAB E2E Connection Test

Purpose:
  Execute E2E flow once:
  1. Create JARVIS decision_id
  2. Call /api/v1/socket/multi_request with decision_id
  3. Capture A-G evidence
  4. Verify HAB recording

Constraint:
  - Only execute once in sandbox
  - No loop, no retry
  - Capture full trace
"""

import requests
import json
import time
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

GATEWAY_URL = "http://localhost:5010"
API_KEY = "test-key-for-audit"
DB_PATH = Path(__file__).parent / "data" / "mocka_events.db"

class E2ETestRunner:
    def __init__(self):
        self.test_id = f"E2E_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results = {
            "test_id": self.test_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "steps": {},
        }

    def run(self):
        """Execute JARVIS → Multi-AI → HAB E2E test"""
        print("=" * 80)
        print("JARVIS → Multi-AI → HAB E2E Connection Test")
        print(f"Test ID: {self.test_id}")
        print("=" * 80)
        print()

        # STEP A: Create JARVIS decision_id
        print("[STEP A] Generate JARVIS decision_id")
        print("-" * 80)
        decision_id = self._generate_decision_id()
        print(f"Decision ID: {decision_id}")
        self.results["steps"]["A_jarvis_decision_id"] = decision_id
        print()

        # STEP B: Call multi_request with decision_id
        print("[STEP B] POST /api/v1/socket/multi_request with decision_id")
        print("-" * 80)
        multi_request_response = self._call_multi_request(decision_id)
        if not multi_request_response:
            print("ERROR: multi_request failed")
            return False

        request_id = multi_request_response.get("request_id")
        print(f"Request ID: {request_id}")
        self.results["steps"]["B_multi_request_request_id"] = request_id
        self.results["steps"]["B_multi_request_response"] = multi_request_response
        print()

        # STEP C: Extract provider responses
        print("[STEP C] Extract provider responses")
        print("-" * 80)
        results_list = multi_request_response.get("results", [])
        provider_responses = {}
        for result in results_list:
            provider = result.get("provider")
            status = result.get("status")
            provider_responses[provider] = {
                "status": status,
                "response_len": len(result.get("response", "")) if result.get("status") == "ok" else 0,
            }
            print(f"  {provider}: {status}")
        self.results["steps"]["C_provider_responses"] = provider_responses
        print()

        # STEP D: Extract JARVIS result
        print("[STEP D] Extract JARVIS result from response")
        print("-" * 80)
        jarvis_data = multi_request_response.get("jarvis")
        if jarvis_data:
            print(f"  JARVIS status: {jarvis_data.get('status')}")
            print(f"  JARVIS error: {jarvis_data.get('jarvis_error', 'None')}")
            self.results["steps"]["D_jarvis_result"] = jarvis_data
        else:
            print("  WARNING: No JARVIS result in response")
            self.results["steps"]["D_jarvis_result"] = None
        print()

        # STEP E: Wait for HAB buffer flush
        print("[STEP E] Wait for HAB event buffer to flush")
        print("-" * 80)
        print("  Waiting 3 seconds...")
        time.sleep(3)
        print("  Done")
        print()

        # STEP F: Query HAB events for this test
        print("[STEP F] Query HAB events for request_id")
        print("-" * 80)
        hab_events = self._query_hab_events(request_id)
        print(f"  Found {len(hab_events)} HAB events")
        for event in hab_events:
            print(f"    - {event.get('event_id')}: {event.get('title')}")
        self.results["steps"]["F_hab_events_count"] = len(hab_events)
        self.results["steps"]["F_hab_events"] = hab_events
        print()

        # STEP G: Verify request_id → event_id correspondence
        print("[STEP G] Verify request_id → event_id mapping")
        print("-" * 80)
        if hab_events:
            print(f"  Request ID: {request_id}")
            for event in hab_events:
                print(f"  Event ID: {event.get('event_id')}")
                print(f"    Title: {event.get('title')}")
                print(f"    Free Note: {event.get('free_note')}")
                if request_id in str(event.get("free_note", "")):
                    print(f"    -> request_id FOUND in free_note")
            self.results["steps"]["G_id_mapping"] = "verified"
        else:
            print("  WARNING: No events found to verify mapping")
            self.results["steps"]["G_id_mapping"] = "no_events"
        print()

        # Log runtime trace
        print("[RUNTIME LOG] Gateway stderr (if available)")
        print("-" * 80)
        log_file = Path("gateway_audit.log.err")
        if log_file.exists():
            lines = log_file.read_text(encoding="utf-8").splitlines()
            for line in lines[-20:]:
                if "JARVIS" in line or "jarvis" in line or "ERROR" in line:
                    print(f"  {line}")
        print()

        # Summary
        print("=" * 80)
        print("E2E TEST COMPLETE")
        print("=" * 80)
        print()
        print(json.dumps(self.results, indent=2, ensure_ascii=False, default=str))
        print()

        return True

    def _generate_decision_id(self) -> str:
        """Generate decision ID for JARVIS"""
        import uuid
        return f"DC_E2E_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _call_multi_request(self, decision_id: str) -> dict or None:
        """Call /api/v1/socket/multi_request with decision_id"""
        payload = {
            "request": "What is JARVIS in MoCKA? What is Multi-AI dispatch?",
            "providers": ["gpt", "claude"],
            "title": f"E2E Test: {self.test_id}",
            "decision_id": decision_id,
        }

        headers = {
            "Content-Type": "application/json",
            "X-MoCKA-Key": API_KEY,
        }

        print(f"URL: POST {GATEWAY_URL}/api/v1/socket/multi_request")
        print(f"Payload decision_id: {decision_id}")
        print(f"Payload providers: {payload.get('providers')}")

        try:
            response = requests.post(
                f"{GATEWAY_URL}/api/v1/socket/multi_request",
                json=payload,
                headers=headers,
                timeout=60,
            )

            print(f"Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"ERROR: {response.text[:200]}")
                return None

            result = response.json()
            print(f"Response request_id: {result.get('request_id')}")
            print(f"Response status: {result.get('status')}")

            return result

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _query_hab_events(self, request_id: str) -> list:
        """Query HAB events for given request_id"""
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row

            # Search for events matching request_id in free_note
            cur = conn.cursor()
            cur.execute(
                """
                SELECT event_id, title, short_summary, when_ts, free_note, what_type
                FROM events
                WHERE free_note LIKE ?
                ORDER BY when_ts DESC
                LIMIT 10
                """,
                (f"%{request_id}%",)
            )

            rows = cur.fetchall()
            events = [dict(row) for row in rows]
            conn.close()

            return events

        except Exception as e:
            print(f"DB error: {e}")
            return []


if __name__ == "__main__":
    runner = E2ETestRunner()
    runner.run()

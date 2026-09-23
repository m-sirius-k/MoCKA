#!/usr/bin/env python3
"""
BLOCK PERSISTENCE Runtime Verification Script
実ランタイムで BLOCK → GOVERNANCE_BLOCK event → persistence → read-back を検証
"""

import json
import requests
import sys
from datetime import datetime
from pathlib import Path

# Configuration
MCP_URL = "http://localhost:5002/mcp"
HEALTH_URL = "http://localhost:5002/health"
RESULT_FILE = Path(__file__).parent / "block_persistence_results.json"

# Test cases
CASES = [
    {
        "name": "Case 1: decision_id missing",
        "req_id": "req-001-missing-id",
        "tool": "mocka_write_event",
        "args": {
            "title": "Test BLOCK Case 1",
            "description": "Missing decision_id",
            "author": "test-ai"
        },
        "expected_reason_contains": "BA04_DECISION_ID_MISSING"
    },
    {
        "name": "Case 2: unknown decision_id",
        "req_id": "req-002-unknown-id",
        "tool": "mocka_write_event",
        "args": {
            "title": "Test BLOCK Case 2",
            "description": "Unknown decision_id",
            "author": "test-ai",
            "decision_id": "DC_99999999_999"
        },
        "expected_reason_contains": "BA04_DECISION_NOT_FOUND"
    },
    {
        "name": "Case 3: inactive decision (setup first)",
        "req_id": None,  # Generated dynamically
        "setup": {
            "req_id": "setup-case3-create-decision",
            "tool": "mocka_decision_write",
            "args": {
                "title": "Inactive test decision",
                "context": "Test case 3",
                "decision": "Test",
                "rationale": "For BLOCK test",
                "impact": "Test only",
                "approved_by": "test-ai",
                "alternatives": [{"option": "N/A", "rejected_reason": "N/A"}],
                "status": "Superseded"
            }
        },
        "tool": "mocka_write_event",
        "args_template": {
            "title": "Test BLOCK Case 3",
            "description": "Inactive decision",
            "author": "test-ai",
            "decision_id": None  # Will be set from setup response
        },
        "expected_reason_contains": "BA04_DECISION_NOT_ACTIVE"
    },
    {
        "name": "Case 4: Present Standing DEFERRED",
        "req_id": "req-004-deferred-ps",
        "tool": "mocka_update_todo",
        "args": {
            "id": "TODO-TEST-004",
            "status": "completed"
        },
        "expected_reason_contains": "BA04_PRESENT_STANDING_DEFERRED"
    },
    {
        "name": "Case 5: Authority Scope DEFERRED",
        "req_id": "req-005-deferred-scope",
        "tool": "mocka_add_todo",
        "args": {
            "id": "TODO-TEST-005",
            "title": "Test"
        },
        "expected_reason_contains": "BA04_AUTHORITY_SCOPE_DEFERRED"
    }
]

def call_mcp(tool_name, arguments, req_id):
    """Call MCP tool via JSON-RPC"""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    try:
        response = requests.post(
            MCP_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        return response.status_code, response.json()
    except Exception as e:
        return None, {"error": str(e)}

def read_back_events(limit=100):
    """Read back GOVERNANCE_BLOCK events"""
    status, response = call_mcp("mocka_list_events", {"n": limit}, "readback-events")
    if status == 200 and "result" in response:
        events = response["result"].get("content", [])
        if events and isinstance(events, list) and len(events) > 0:
            try:
                events_data = json.loads(events[0]["text"]) if isinstance(events[0], dict) else events[0]
                if "events" in events_data:
                    return [e for e in events_data["events"] if "GOVERNANCE_BLOCK" in e.get("title", "")]
            except:
                pass
    return []

def verify_server():
    """Verify server is running"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def run_verification():
    """Run all verification cases"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "server_available": False,
        "cases": [],
        "duplicate_test": None,
        "fallback_test": None,
        "summary": {}
    }

    # Check server
    print("[*] Checking server availability...")
    if not verify_server():
        print("[!] Server not available at", HEALTH_URL)
        results["error"] = "Server not available"
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        return False

    results["server_available"] = True
    print("[+] Server available")

    # Run cases
    for case in CASES:
        case_result = {"name": case["name"], "req_id": case.get("req_id")}

        # Setup phase (for Case 3)
        if "setup" in case:
            print(f"\n[*] {case['name']} - Setup phase")
            setup = case["setup"]
            status, response = call_mcp(setup["tool"], setup["args"], setup["req_id"])
            case_result["setup_response"] = {"status": status, "body": response}

            if status == 200 and "result" in response:
                try:
                    result_text = response["result"]["content"][0]["text"]
                    result_json = json.loads(result_text)
                    generated_id = result_json.get("decision_id")
                    if generated_id:
                        case_result["generated_decision_id"] = generated_id
                        case["args_template"]["decision_id"] = generated_id
                        case["req_id"] = f"req-003-inactive-{generated_id}"
                except:
                    pass

        # Main request
        req_id = case.get("req_id")
        if not req_id:
            continue

        print(f"\n[*] {case['name']}")
        print(f"    req_id: {req_id}")

        args = case.get("args") or case.get("args_template")
        status, response = call_mcp(case["tool"], args, req_id)

        case_result["request_id"] = req_id
        case_result["response_status"] = status
        case_result["response_body"] = response

        # Extract BLOCK details
        if status == 200 and "result" in response:
            try:
                result_text = response["result"]["content"][0]["text"]
                result_json = json.loads(result_text)

                if "error" in result_json:
                    case_result["error"] = result_json["error"]
                    case_result["reason"] = result_json.get("reason", "")
                    print(f"    [BLOCK] {result_json['error']}: {result_json.get('reason', '')[:80]}")
                else:
                    case_result["execution_not_blocked"] = True
                    print(f"    [!] Request was NOT blocked (unexpected)")
            except Exception as e:
                case_result["parse_error"] = str(e)

        # Read back GOVERNANCE_BLOCK events
        print(f"    [*] Reading back GOVERNANCE_BLOCK events...")
        block_events = read_back_events(200)
        matching_events = [e for e in block_events if str(req_id) in str(e.get("description", ""))]

        if matching_events:
            case_result["block_event_found"] = True
            event = matching_events[0]
            case_result["event_id"] = event.get("event_id", "N/A")
            case_result["timestamp"] = event.get("when_ts", event.get("timestamp", "N/A"))
            case_result["read_back"] = event
            print(f"    [+] GOVERNANCE_BLOCK event found: {event.get('event_id', 'N/A')}")
        else:
            case_result["block_event_found"] = False
            print(f"    [!] GOVERNANCE_BLOCK event NOT found in read-back")

        results["cases"].append(case_result)

    # Duplicate test
    print(f"\n[*] Duplicate test: re-sending Case 1 request...")
    dup_case = results["cases"][0]
    status, response = call_mcp("mocka_write_event", CASES[0]["args"], CASES[0]["req_id"])

    dup_result = {
        "original_req_id": CASES[0]["req_id"],
        "response_status": status,
        "response_body": response
    }

    if status == 200 and "result" in response:
        try:
            result_text = response["result"]["content"][0]["text"]
            result_json = json.loads(result_text)
            if "error" in result_json:
                dup_result["result"] = result_json.get("error")
                if "DUPLICATE" in result_json.get("error", ""):
                    dup_result["duplicate_detected"] = True
                    print(f"    [+] Duplicate detected: {result_json['error']}")
            else:
                dup_result["duplicate_detected"] = False
                print(f"    [!] Request was processed (not marked as duplicate)")
        except:
            pass

    results["duplicate_test"] = dup_result

    # Save results
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Results saved to {RESULT_FILE}")

    # Print summary
    print("\n" + "="*60)
    print("RUNTIME VERIFICATION SUMMARY")
    print("="*60)
    for i, case_result in enumerate(results["cases"], 1):
        status = "VERIFIED" if case_result.get("block_event_found") else "UNKNOWN"
        print(f"Case {i}: {status}")
        print(f"  req_id: {case_result.get('request_id')}")
        print(f"  reason: {case_result.get('reason', 'N/A')[:60]}...")
        print(f"  event_id: {case_result.get('event_id', 'N/A')}")

    print(f"\nDuplicate test: {'DETECTED' if results['duplicate_test'].get('duplicate_detected') else 'NOT DETECTED'}")
    print(f"\nResults file: {RESULT_FILE}")

    return True

if __name__ == "__main__":
    run_verification()

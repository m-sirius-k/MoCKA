import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA\structural")))
sys.path.insert(0, str(Path(r"C:\Users\sirok\MoCKA")))

import requests
import mocka_mcp_server

# Monkey-patch to trace HTTP responses
original_post = requests.post

def traced_post(url, **kwargs):
    if "gate" in url.lower():
        print(f"[TRACE HTTP] POST {url}")
        try:
            result = original_post(url, **kwargs)
            print(f"[TRACE HTTP] Status: {result.status_code}")
            if result.status_code != 201:
                print(f"[TRACE HTTP] Response: {result.text[:300]}")
            else:
                print(f"[TRACE HTTP] Response: {result.json()}")
            return result
        except Exception as e:
            print(f"[TRACE HTTP] Exception: {type(e).__name__}: {str(e)[:100]}")
            raise
    return original_post(url, **kwargs)

requests.post = traced_post

print("=" * 70)
print("STEP 4B — TRACE HTTP RESPONSE AFTER SCHEMA UPDATE")
print("=" * 70)
print()

args = {
    "decision_id": "DC_20260705_001",
    "title": "Test TODO",
}

result_json = mocka_mcp_server.execute_tool("mocka_add_todo", args, req_id="req_trace_001")
result = json.loads(result_json)

print()
print("=" * 70)
print("Result:")
print(json.dumps(result, indent=2, ensure_ascii=False))

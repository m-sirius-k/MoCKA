#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from app import app

client = app.test_client()

# A. UI ENTRY
print("=" * 80)
print("A. UI ENTRY")
print("=" * 80)
r = client.get("/")
html = r.get_data(as_text=True)
has_hab = "hab-input" in html and "habAsk" in html
print(f"hab-input element: {'YES' if 'hab-input' in html else 'NO'}")
print(f"habAsk function: {'YES' if 'habAsk' in html else 'NO'}")
print(f"RESULT: {'PASS' if has_hab else 'FAIL'}")

# B. API CONNECTION
print()
print("=" * 80)
print("B. API CONNECTION")
print("=" * 80)
r = client.get("/api/v1/hab/health")
print(f"Status: {r.status_code}")
print(f"RESULT: {'PASS' if r.status_code == 200 else 'FAIL'}")

# C, D, E
print()
print("=" * 80)
print("C. JARVIS RECALL")
print("=" * 80)
r = client.post("/api/v1/hab/ask", json={"question": "What about C-001?"})
data = r.get_json()
jarvis = data.get("jarvis")
if jarvis:
    print(f"Decision ID: {jarvis.get('decision_id')}")
    print(f"Title: {jarvis.get('decision_title')}")
    print("RESULT: PASS")
else:
    print("RESULT: FAIL")

print()
print("=" * 80)
print("D. GPT RESPONSE")
print("=" * 80)
responses = data.get("responses", [])
gpt = next((x for x in responses if x.get("provider") == "gpt"), None)
if gpt and gpt.get("status") == "ok":
    print(f"Provider: {gpt.get('provider')}")
    print(f"Status: {gpt.get('status')}")
    print(f"Response: {gpt.get('response')[:80]}...")
    print("RESULT: PASS")
else:
    print("RESULT: FAIL")

print()
print("=" * 80)
print("E. HUMAN VISIBLE RESPONSE")
print("=" * 80)
print(f"HTTP Status: {r.status_code}")
print(f"Question: {data.get('question')}")
print(f"JARVIS: Found" if jarvis else "JARVIS: Not found")
print(f"GPT: OK" if (gpt and gpt.get('status') == 'ok') else "GPT: Error/Missing")
all_ok = (r.status_code == 200 and jarvis and gpt and gpt.get('status') == 'ok')
print(f"RESULT: {'PASS' if all_ok else 'FAIL'}")

print()
print("=" * 80)
print("F. MODIFIED FILES")
print("=" * 80)
print("- templates/index.html (added HAB Question section)")
print("- index.html (root) (copied from templates/index.html)")

print()
print("=" * 80)
print("G. E2E RESULT")
print("=" * 80)
if has_hab and all_ok:
    print("✓ UI Entry visible in COMMAND CENTER")
    print("✓ HAB API connection working")
    print("✓ JARVIS recall functioning")
    print("✓ GPT response received")
    print("✓ Human can send question and see HAB→JARVIS→GPT response chain")
    print("RESULT: PASS")
else:
    print("RESULT: FAIL")

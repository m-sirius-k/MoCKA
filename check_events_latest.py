#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from pathlib import Path

file = Path("data/events_latest.json")
data = json.loads(file.read_text(encoding="utf-8"))

request_id = "6689157c-9814-488a-ad46-d09a95e26f9d"

recent = data.get("recent_events", [])
print(f"Total events in recent_events: {len(recent)}")
print()

# Find our event
found = False
for i, event in enumerate(recent):
    if event.get("free_note") and request_id in event.get("free_note", ""):
        print(f"[FOUND] Position {i}:")
        print(f"  event_id: {event.get('event_id')}")
        print(f"  title: {event.get('title')}")
        print(f"  what_type: {event.get('what_type')}")
        print(f"  when_ts: {event.get('when_ts')}")
        print(f"  free_note: {event.get('free_note')}")
        found = True
        break

if not found:
    print(f"Event NOT found in recent_events")
    print()
    print("First 3 recent events (for comparison):")
    for event in recent[:3]:
        print(f"  {event.get('what_type')}: {event.get('title')}")

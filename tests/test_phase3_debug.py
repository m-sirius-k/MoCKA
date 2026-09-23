#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug: Check if contextual matching is working"""

import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from runtime.jarvis.core.engine import JarvisEngine

jarvis = JarvisEngine()

# Test intent
intent = "Decision Ledger adoption"

# Call with debug
print(f"Intent: {intent}")
print(f"Expected keywords: {intent.lower().split()}\n")

# Run recall_experience
result = jarvis.recall_experience(intent)

print(f"Result status: {result['status']}")
print(f"Search mode: {result.get('search_mode')}")
print(f"Gap: {result.get('gap')}")
print(f"Matches: {len(result.get('matches', []))}")

if result['matches']:
    match = result['matches'][0]
    print(f"\nMatched Decision:")
    print(f"  ID: {match.get('decision_id')}")
    title_safe = match.get('title', '').encode('ascii', 'replace').decode('ascii')[:60]
    print(f"  Title: {title_safe}")

    # Check title for keywords
    title_lower = match.get('title', '').lower()
    decision_lower = match.get('decision', '').lower()
    rationale_lower = match.get('rationale', '').lower()

    print(f"\n  Keyword match check:")
    for kw in ['decision', 'ledger']:
        in_title = kw in title_lower
        in_decision = kw in decision_lower
        in_rationale = kw in rationale_lower
        print(f"    '{kw}': title={in_title}, decision={in_decision}, rationale={in_rationale}")

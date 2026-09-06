#!/usr/bin/env python3
"""
Minimal Traceability Index Builder

Purpose:
  Map existing Event/Index/Decision/Evidence/Audit/Authority records
  using existing IDs and references without modifying source data.

Priority:
  1. Event <-> Index (via source_record in MOCKA_REGISTRY.json)
  2. Event <-> Decision (via related_events in decision_ledger.jsonl)
  3. Event <-> Evidence (UNKNOWN if not found)
  4. Event <-> Audit (UNKNOWN if not found)
  5. Event <-> Authority (UNKNOWN if not found)
  6. Preserve UNKNOWN/NOT_ESTABLISHED states

Output:
  data/traceability_index.jsonl - bidirectional mappings
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def load_events_latest(path):
    """Load events from events_latest.json"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    event_map = {}
    for evt in data:
        event_id = evt.get('event_id')
        if event_id:
            event_map[event_id] = evt
    return event_map

def load_registry(path):
    """Load registry from MOCKA_REGISTRY.json"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    links = defaultdict(list)

    # Priority 1: Event <-> Index via source_record
    for section_name in ['identity', 'atlas', 'reference', 'classification', 'lifecycle', 'metadata']:
        entries = data.get(section_name, [])
        for entry in entries:
            source_record = entry.get('source_record')
            if source_record:
                entry_id = entry.get(f'{section_name[:-1]}_id') if section_name != 'identity' else entry.get('identity_id')
                if entry_id:
                    links['index_to_event'].append({
                        'index_id': entry_id,
                        'index_type': section_name,
                        'event_id': source_record
                    })
                    links['event_to_index'].append({
                        'event_id': source_record,
                        'index_id': entry_id,
                        'index_type': section_name
                    })

    return links

def load_decision_ledger(path):
    """Load decision ledger from decision_ledger.jsonl"""
    links = defaultdict(list)

    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    decision = json.loads(line)
                    decision_id = decision.get('decision_id')
                    related_events = decision.get('related_events', [])

                    # Priority 2: Event <-> Decision via related_events
                    for event_id in related_events:
                        links['decision_to_event'].append({
                            'decision_id': decision_id,
                            'event_id': event_id
                        })
                        links['event_to_decision'].append({
                            'event_id': event_id,
                            'decision_id': decision_id
                        })
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass

    return links

def build_traceability_index(repo_root):
    """Build minimal traceability index from existing data"""

    repo_path = Path(repo_root)
    events_file = repo_path / 'data' / 'events_latest.json'
    registry_file = repo_path / 'data' / 'MOCKA_REGISTRY.json'
    decision_file = repo_path / 'data' / 'decisions' / 'decision_ledger.jsonl'
    output_file = repo_path / 'data' / 'traceability_index.jsonl'

    print("[1/4] Loading events...")
    events = load_events_latest(events_file)
    print(f"  Loaded {len(events)} events")

    print("[2/4] Loading registry (Event <-> Index)...")
    registry_links = load_registry(registry_file)
    print(f"  Found {len(registry_links['event_to_index'])} Event->Index links")
    print(f"  Found {len(registry_links['index_to_event'])} Index->Event links")

    print("[3/4] Loading decision ledger (Event <-> Decision)...")
    decision_links = load_decision_ledger(decision_file)
    print(f"  Found {len(decision_links['event_to_decision'])} Event->Decision links")
    print(f"  Found {len(decision_links['decision_to_event'])} Decision->Event links")

    print("[4/4] Writing traceability index...")

    # Collect all links by event_id
    event_traceability = defaultdict(lambda: {
        'event_id': None,
        'index_entries': [],
        'decisions': [],
        'evidence': [],
        'audit': [],
        'authority': [],
        'status': 'OK'
    })

    # Add Event->Index links
    for link in registry_links['event_to_index']:
        event_id = link['event_id']
        event_traceability[event_id]['event_id'] = event_id
        event_traceability[event_id]['index_entries'].append({
            'index_id': link['index_id'],
            'index_type': link['index_type']
        })

    # Add Event->Decision links
    for link in decision_links['event_to_decision']:
        event_id = link['event_id']
        event_traceability[event_id]['event_id'] = event_id
        event_traceability[event_id]['decisions'].append({
            'decision_id': link['decision_id']
        })

    # Mark Evidence/Audit/Authority as NOT_ESTABLISHED
    for event_id in event_traceability:
        if not event_traceability[event_id]['evidence']:
            event_traceability[event_id]['evidence'].append({
                'status': 'NOT_ESTABLISHED'
            })
        if not event_traceability[event_id]['audit']:
            event_traceability[event_id]['audit'].append({
                'status': 'NOT_ESTABLISHED'
            })
        if not event_traceability[event_id]['authority']:
            event_traceability[event_id]['authority'].append({
                'status': 'NOT_ESTABLISHED'
            })

    # Write traceability index
    with open(output_file, 'w', encoding='utf-8') as f:
        for event_id in sorted(event_traceability.keys()):
            record = event_traceability[event_id]
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

    print(f"  Written {len(event_traceability)} traceability records to {output_file}")
    print("\nTraceability Index Build Complete")
    print(f"Output: {output_file}")

    return True

if __name__ == '__main__':
    repo_root = Path(__file__).parent
    try:
        build_traceability_index(repo_root)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

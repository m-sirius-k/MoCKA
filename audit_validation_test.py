#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from phi_os.gate_validator import validate

# Reconstruct the lineage_payload from runtime
lineage_payload = {
    'what_type': 'audit',
    'who_actor': 'orchestra_multi_dispatcher',
    'who_role': 'automation',
    'who_session': 'SESSION_20260929_045657',
    'what_title': 'AI Lineage: gpt (gpt-4)',
    'where_component': 'orchestra',
    'where_path': '/path/to/multi_dispatcher.py',
    'why_purpose': 'Record AI provider execution lineage (orchestrator audit)',
    'how_trigger': 'dispatch_multi_request()',
    'after_hash': '6a64762ef671a810',
    'vendor': 'gpt',
    'model': 'gpt-4',
    'runtime': 'orchestra_dispatch',
    'source': 'orchestra_runtime',
    'request_id': 'b8a518a2-2016-4c7b-8ef0-86126ba41760',
    'when_ts': '2026-09-29T04:56:23.000000+00:00',
    'description': 'Provider: gpt, Model: gpt-4, Status: ok',
}

print('Testing lineage_payload against validate():')
errors = validate(lineage_payload)

if errors:
    print('VALIDATION FAILED:')
    for err in errors:
        print(f'  - {err}')
else:
    print('VALIDATION PASSED')

print('\nPayload analysis:')
print(f'  request_id present: {("request_id" in lineage_payload)}')
print(f'  request_id value: {lineage_payload.get("request_id")}')
print(f'  who_session: {lineage_payload.get("who_session")}')
print(f'  what_type: {lineage_payload.get("what_type")}')

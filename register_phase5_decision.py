#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Register Phase 5.0 HAB-JARVIS Runtime Decision to Decision Ledger.
Purpose: Create authoritative decision_id for mocka_dispatch_multi_ai_request
"""

import json
from datetime import datetime, timezone
from pathlib import Path

def register_phase5_decision():
    ledger_path = Path(__file__).parent / "data" / "decisions" / "decision_ledger.jsonl"

    # Generate decision ID in DC_YYYYMMDD_NNN format
    now = datetime.now(timezone.utc)
    decision_id = f"DC_{now.strftime('%Y%m%d')}_P5_HAB_JARVIS_001"

    decision_entry = {
        "decision_id": decision_id,
        "title": "PHASE 5.0: mocka_dispatch_multi_ai_request — Standard Runtime Tool Authorization",
        "context": "Phase 5.0 Genesis Bootstrap / HAB-JARVIS Runtime Verification. HG judgment complete. Implementation cd31c94 verified: authorization_scope validation enforced, runtime_scope validation enforced, no BA04 bypass, no READ_ONLY exemption.",
        "decision": "AUTHORIZE mocka_dispatch_multi_ai_request as Standard Runtime Tool (Classification B) with mandatory decision_id, authorization_scope (PHASE_5_0/mocka_dispatch_multi_ai_request/HAB-JARVIS Runtime Verification), and runtime_scope (KUROKO local runtime) validation.",
        "rationale": "Implementation cd31c94 verified: (1) authorization_scope validation hardcoded in mocka_mcp_server.py:1320-1326, (2) runtime_scope validation hardcoded in mocka_mcp_server.py:1328-1334, (3) no BA04 bypass (governance_rejected enforced), (4) no READ_ONLY exemption, (5) existing dispatch_multi_request() pathway preserved. Governance conditions met.",
        "impact": "Enables Phase 5.0 HAB-JARVIS Runtime Verification within KUROKO local runtime. Conditions: valid decision_id required, BA04 bypass prohibited, READ_ONLY exemption prohibited, AI/JARVIS self-approval prohibited, Production activation prohibited, Scope expansion prohibited, Phase 4–7 freeze modification prohibited.",
        "authorization_scope": "PHASE_5_0/mocka_dispatch_multi_ai_request/HAB-JARVIS Runtime Verification",
        "runtime_scope": "KUROKO local runtime: JARVIS → mocka_dispatch_multi_ai_request → dispatch_multi_request() → existing Orchestra/HAB → REAL AI → Event Store",
        "approved_by": "HG (Human Gate)",
        "decision_type": "Tactical",
        "status": "Active",
        "timestamp": now.isoformat(),
        "alternatives": [
            {
                "option": "Defer authorization pending additional verification",
                "rejected_reason": "Implementation already verified; HG judgment complete; deferral unnecessary"
            }
        ],
        "related_documents": [
            "cd31c94:gateway/multi_dispatcher.py",
            "cd31c94:mocka_mcp_server.py",
            "PHASE5_0_HG_DECISION_4POINT_FINAL_20260928.md"
        ]
    }

    # Append to ledger
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(decision_entry, ensure_ascii=False) + "\n")

    return decision_id, ledger_path, decision_entry

if __name__ == "__main__":
    decision_id, ledger_path, entry = register_phase5_decision()
    print(f"Decision ID: {decision_id}")
    print(f"Ledger Path: {ledger_path}")
    print(f"Status: WRITTEN")
    print(f"\nEntry Summary:")
    print(f"  Title: {entry['title']}")
    print(f"  Authorization Scope: {entry['authorization_scope']}")
    print(f"  Runtime Scope: {entry['runtime_scope']}")
    print(f"  Status: {entry['status']}")

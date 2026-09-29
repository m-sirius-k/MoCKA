#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PHASE 5.0 — SINGLE RUNTIME EXECUTION
ONE request only with exact authorization/decision_id
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from gateway.multi_dispatcher import dispatch_multi_request

def main():
    # Exact authorization from Decision Ledger
    decision_id = "DC_20260929_P5_HAB_JARVIS_001"
    authorization_scope = "PHASE_5_0/mocka_dispatch_multi_ai_request/HAB-JARVIS Runtime Verification"
    runtime_scope = "KUROKO local runtime: JARVIS → mocka_dispatch_multi_ai_request → dispatch_multi_request() → existing Orchestra/HAB → REAL AI → Event Store"

    # Runtime execution
    request_text = "Phase 5.0 HAB-JARVIS Runtime Verification: Test dispatch to multiple AI providers"
    providers = ["gpt", "claude"]
    title = "PHASE 5.0 HAB-JARVIS Runtime Test"

    print("[PHASE 5.0 RUNTIME EXECUTION START]", flush=True)
    print(f"Decision ID: {decision_id}", flush=True)
    print(f"Authorization Scope: {authorization_scope}", flush=True)
    print(f"Runtime Scope: {runtime_scope}", flush=True)
    print(f"Request Text: {request_text}", flush=True)
    print(f"Providers: {providers}", flush=True)
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}", flush=True)
    print()

    # Execute dispatch_multi_request
    result = dispatch_multi_request(
        request_text=request_text,
        providers=providers,
        title=title,
        decision_id=decision_id
    )

    # Capture critical fields
    request_id = result.get("request_id")
    status = result.get("status")
    summary = result.get("summary", {})
    provider_results = result.get("results", [])

    print("[RUNTIME EXECUTION COMPLETE]", flush=True)
    print(f"Request ID: {request_id}", flush=True)
    print(f"Status: {status}", flush=True)
    print(f"Summary: ok={summary.get('ok')}, error={summary.get('error')}, not_verified={summary.get('not_verified')}", flush=True)
    print()

    # Report each provider result
    for i, pres in enumerate(provider_results, 1):
        provider = pres.get("provider")
        pstatus = pres.get("status")
        print(f"Provider {i}: {provider}", flush=True)
        print(f"  Status: {pstatus}", flush=True)
        if pstatus == "ok":
            response_text = pres.get("response", "")
            preview = (response_text[:120] + "...") if len(response_text) > 120 else response_text
            print(f"  Response: {preview}", flush=True)
        elif pstatus == "NOT_VERIFIED":
            print(f"  Reason: {pres.get('error')}", flush=True)
        else:
            print(f"  Error: {pres.get('error')}", flush=True)

    print()

    # Save result for Event Store read-back
    result_file = Path(__file__).parent / "runtime_result.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump({
            "decision_id": decision_id,
            "request_id": request_id,
            "authorization_scope": authorization_scope,
            "runtime_scope": runtime_scope,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)

    print(f"[RUNTIME RESULT SAVED]", flush=True)
    print(f"File: {result_file}", flush=True)
    print(f"Request ID: {request_id}", flush=True)
    print(f"Decision ID: {decision_id}", flush=True)

if __name__ == "__main__":
    main()

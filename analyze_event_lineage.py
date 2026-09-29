#!/usr/bin/env python3
"""
Analyze: Orchestra response → Event lineage preservation

Question: Do Orchestra-specific fields (provider="orchestra_web", vendor, model, method)
get preserved in the Event Object pushed to buffer?
"""

# Gateway.py:socket_multi_request() CREATES event:
event_created = {
    "title": f"Multi-AI Request: {title}",
    "short_summary": summary_text,  # "ok=X, error=Y, not_verified=Z"
    "when": now.isoformat(),
    "who_actor": "MultiAI/Dispatcher",  # GENERIC - NOT provider-specific
    "ai_actor": "Socket",  # GENERIC
    "what_type": "multi_ai_request",
    "free_note": f"request_id={result.get('request_id')}",  # Only request_id
    "where_component": "gateway_multi_dispatcher",
    "lifecycle_phase": "in_operation",
    "why_purpose": "multi_ai_e2e_test",
}

# Meanwhile, dispatch_multi_request() RETURNS:
dispatch_result = {
    "status": "all_ok",
    "request_id": common_request_id,
    "results": [
        {
            "provider": "orchestra_web",  # ← This is HERE
            "status": "ok",
            "response": aggregated_response,
            "model": "default",
            "usage": {
                "ais_queried": 3,
                "model": "orchestra_web",
                "method": "subprocess_orchestra_one_host",
            },
            "timestamp": timestamp,
            "request_id": request_id,
        },
        {
            "provider": "gpt",
            "status": "ok",
            "response": gpt_response,
            "model": "gpt-4",
            ...
        },
        # ... other providers
    ],
    "summary": {
        "total": 5,
        "ok": 5,
        "error": 0,
        "not_verified": 0,
    },
    "timestamp": timestamp,
}

# CRITICAL ANALYSIS:
print("=== Lineage Preservation Analysis ===\n")

print("What SHOULD be preserved for Orchestra:")
print("  - provider: 'orchestra_web'")
print("  - method: 'subprocess_orchestra_one_host'")
print("  - vendor: 'Google/OpenAI/Anthropic' (from Gemini/ChatGPT/Perplexity)")
print("  - model: 'orchestra_web' or 'default'")
print("  - response: aggregated_response")
print()

print("What IS pushed to buffer:")
print("  - title: 'Multi-AI Request: ...'")
print("  - who_actor: 'MultiAI/Dispatcher' (GENERIC)")
print("  - ai_actor: 'Socket' (GENERIC)")
print("  - what_type: 'multi_ai_request' (GENERIC)")
print("  - free_note: request_id only (NO provider info)")
print()

print("VERDICT:")
print("  ✗ provider field NOT in event")
print("  ✗ method field NOT in event")
print("  ✗ vendor field NOT in event")
print("  ✗ model field NOT in event")
print("  ✓ request_id preserved")
print("  ✓ response accessible via request_id lookup")
print()

print("Lineage Chain:")
print("  Orchestra response → dispatch_multi_request() ✓ (in result)")
print("  → gateway.socket_multi_request() ✓ (in result)")
print("  → event object creation ✗ (fields not copied)")
print("  → get_buffer().push(event) ✗ (generic event without provider info)")
print("  → Event Store ✗ (receives generic event only)")
print()

print("Result:")
print("  - Provider-specific lineage is LOST at Event creation stage")
print("  - Event Store receives only aggregated summary")
print("  - Orchestra-specific details must be reconstructed from request_id→result lookup")

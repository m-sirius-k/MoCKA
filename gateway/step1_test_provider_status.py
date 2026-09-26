# -*- coding: utf-8 -*-
"""
STEP 1: Verify current Provider connection status

Objective:
  Determine which providers are actually available (have valid API keys)
  and can be used for multi-AI testing.

Principle:
  1. Do NOT write API keys to code
  2. Only use providers with credentials
  3. Record all findings
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Setup path
gateway_path = Path(__file__).parent
sys.path.insert(0, str(gateway_path))

# Load env from explicit .env path
from dotenv import load_dotenv
env_file = gateway_path / ".env"
if env_file.exists():
    load_dotenv(env_file)

from multi_dispatcher import dispatch_multi_request

print("\n" + "="*70)
print("STEP 1: Provider Connection Status - Verification")
print("="*70)

print(f"\nTimestamp: {datetime.now(timezone.utc).isoformat()}")
print(f"Date: 2026-09-23")

# Check environment credentials
print("\n--- Credential Status ---")
creds = {
    "OPENAI_API_KEY": "OpenAI/GPT",
    "ANTHROPIC_API_KEY": "Anthropic/Claude",
    "GEMINI_API_KEY": "Google/Gemini",
    "PERPLEXITY_API_KEY": "Perplexity",
}

available_providers = []
for env_key, provider_name in creds.items():
    status = "SET" if os.environ.get(env_key) else "NOT SET"
    print(f"  {env_key:25} {status:10} ({provider_name})")
    if os.environ.get(env_key):
        available_providers.append(provider_name)

print(f"\nAvailable providers (have API keys): {available_providers}")

# Test each provider
print("\n--- Provider Testing ---")

test_request = "What is 2+2? Answer briefly."
provider_map = {
    "gpt": "OpenAI/GPT",
    "claude": "Anthropic/Claude",
    "gemini": "Google/Gemini",
    "perplexity": "Perplexity",
}

results = {}

for provider_key in ["gpt", "claude", "gemini", "perplexity"]:
    print(f"\nTesting: {provider_key:12} ({provider_map[provider_key]})")

    result = dispatch_multi_request(
        request_text=test_request,
        providers=[provider_key],
        title=f"STEP1: Provider test for {provider_key}"
    )

    if result["results"]:
        pr = result["results"][0]
        status = pr.get("status")
        results[provider_key] = status

        print(f"  Status: {status:15}", end="")

        if status == "ok":
            print(" [WORKING]")
            resp = pr.get("response", "")[:60]
            print(f"  Response: {resp}")
        elif status == "NOT_VERIFIED":
            error = pr.get("error", "")
            print(f" [NO API KEY]")
            print(f"  Error: {error}")
        else:
            error = pr.get("error", "")[:70]
            print(f" [ERROR]")
            print(f"  Error: {error}")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

working = [p for p, s in results.items() if s == "ok"]
not_verified = [p for p, s in results.items() if s == "NOT_VERIFIED"]
errors = [p for p, s in results.items() if s == "error"]

print(f"\nWorking providers:        {working if working else 'NONE'}")
print(f"Not verified (no API key): {not_verified if not_verified else 'NONE'}")
print(f"Errors:                   {errors if errors else 'NONE'}")

if len(working) >= 2:
    print(f"\n[RESULT] READY FOR MULTI-AI TEST")
    print(f"         {len(working)} providers are working")
    print(f"         Proceeding to STEP 2: MultiDispatcher execution")
elif len(working) == 1:
    print(f"\n[RESULT] SINGLE PROVIDER AVAILABLE")
    print(f"         {working[0]} is available")
    print(f"         MultiDispatcher test will run but NOT_VERIFIED status expected")
else:
    print(f"\n[RESULT] NO PROVIDERS AVAILABLE")
    print(f"         Setup required before proceeding")

print("\n" + "="*70)

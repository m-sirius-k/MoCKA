# -*- coding: utf-8 -*-
"""
Multi-AI Dispatcher - Distribute single request to multiple AI providers.

Purpose:
  Take one HAB request and dispatch it to multiple AI provider sockets.
  Collect individual responses and record each separately in HAB.

Design:
  - Supports: GPT, Claude, Gemini, Perplexity
  - Each provider is called independently
  - Failures in one provider do not block others
  - API key missing is recorded as NOT_VERIFIED status
  - No decision logic; responses are recorded but not used for decisions

Date: 2026-09-22
Status: E2E Multi-AI implementation
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

_gateway_path = Path(__file__).parent
if str(_gateway_path) not in sys.path:
    sys.path.insert(0, str(_gateway_path))


def dispatch_multi_request(request_text: str,
                          providers: List[str] = None,
                          models: Dict[str, str] = None,
                          title: str = "Multi-AI Request") -> Dict[str, Any]:
    """
    Dispatch single request to multiple AI providers and collect responses.

    Args:
        request_text: Text to send to all AI providers
        providers: List of provider names (default: all available)
        models: Dict of provider -> model mapping (default: use provider defaults)
        title: Title for HAB event logging

    Returns:
        {
            "status": "all_ok" | "partial_ok" | "all_error",
            "request_id": str (common request ID for all providers),
            "results": [
                {
                    "provider": "gpt"|"claude"|"gemini"|"perplexity",
                    "status": "ok" | "error" | "NOT_VERIFIED",
                    "response": str (if ok),
                    "model": str,
                    "usage": dict (if ok),
                    "error": str (if error),
                    "timestamp": str,
                }
            ],
            "summary": {
                "total": int,
                "ok": int,
                "error": int,
                "not_verified": int,
            },
            "timestamp": str,
        }
    """
    if not providers:
        providers = ["gpt", "claude", "gemini", "perplexity"]

    if not models:
        models = {
            "gpt": "gpt-4",
            "claude": "claude-opus-5",
            "gemini": "gemini-2.0-flash",
            "perplexity": "sonar-pro",
        }

    # Generate common request ID for all providers
    import uuid
    common_request_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    results = []
    summary = {
        "total": len(providers),
        "ok": 0,
        "error": 0,
        "not_verified": 0,
    }

    for provider in providers:
        result = _call_provider(
            provider=provider,
            request_text=request_text,
            model=models.get(provider, ""),
            title=title,
            common_request_id=common_request_id,
            timestamp=timestamp,
        )
        results.append(result)

        if result["status"] == "ok":
            summary["ok"] += 1
        elif result["status"] == "NOT_VERIFIED":
            summary["not_verified"] += 1
        else:
            summary["error"] += 1

    # Determine overall status
    if summary["ok"] == summary["total"]:
        overall_status = "all_ok"
    elif summary["ok"] > 0:
        overall_status = "partial_ok"
    else:
        overall_status = "all_error"

    return {
        "status": overall_status,
        "request_id": common_request_id,
        "results": results,
        "summary": summary,
        "timestamp": timestamp,
    }


def _call_provider(provider: str,
                   request_text: str,
                   model: str,
                   title: str,
                   common_request_id: str,
                   timestamp: str) -> Dict[str, Any]:
    """
    Call individual AI provider and return structured result.

    Returns:
        {
            "provider": str,
            "status": "ok" | "error" | "NOT_VERIFIED",
            "response": str (if ok),
            "model": str,
            "usage": dict (if ok),
            "error": str (if error),
            "timestamp": str,
            "request_id": str (common),
        }
    """
    try:
        if provider == "gpt":
            from adapter_gpt import call_api as gpt_call_api
            api_result = gpt_call_api(request_text, model or "gpt-4")
            return _format_result(
                provider="gpt",
                api_result=api_result,
                model=model or "gpt-4",
                timestamp=timestamp,
                request_id=common_request_id,
            )

        elif provider == "claude":
            from adapter_claude import call_api as claude_call_api
            api_result = claude_call_api(request_text, model or "claude-opus-5")
            return _format_result(
                provider="claude",
                api_result=api_result,
                model=model or "claude-opus-5",
                timestamp=timestamp,
                request_id=common_request_id,
            )

        elif provider == "gemini":
            from adapter_gemini import call_api as gemini_call_api
            api_result = gemini_call_api(request_text, model or "gemini-2.0-flash")
            return _format_result(
                provider="gemini",
                api_result=api_result,
                model=model or "gemini-2.0-flash",
                timestamp=timestamp,
                request_id=common_request_id,
            )

        elif provider == "perplexity":
            from adapter_perplexity import call_api as perplexity_call_api
            api_result = perplexity_call_api(request_text, model or "sonar-pro")
            return _format_result(
                provider="perplexity",
                api_result=api_result,
                model=model or "sonar-pro",
                timestamp=timestamp,
                request_id=common_request_id,
            )

        else:
            return {
                "provider": provider,
                "status": "error",
                "error": f"Unsupported provider: {provider}",
                "timestamp": timestamp,
                "request_id": common_request_id,
                "model": model,
            }

    except ImportError as e:
        # Adapter module not found
        return {
            "provider": provider,
            "status": "error",
            "error": f"Adapter not available: {str(e)}",
            "timestamp": timestamp,
            "request_id": common_request_id,
            "model": model,
        }

    except Exception as e:
        # Unexpected error
        return {
            "provider": provider,
            "status": "error",
            "error": f"Dispatch error: {str(e)}",
            "timestamp": timestamp,
            "request_id": common_request_id,
            "model": model,
        }


def _format_result(provider: str,
                   api_result: Dict[str, Any],
                   model: str,
                   timestamp: str,
                   request_id: str) -> Dict[str, Any]:
    """
    Format API result into standard multi-request structure.
    Handle API_KEY_MISSING case.
    """
    status = api_result.get("status", "error")

    # Check for API key missing error
    if status == "error":
        error_msg = api_result.get("error", "")
        if "API_KEY" in error_msg or "not set" in error_msg:
            return {
                "provider": provider,
                "status": "NOT_VERIFIED",
                "error": f"API_KEY_MISSING: {error_msg}",
                "model": model,
                "timestamp": timestamp,
                "request_id": request_id,
            }

    # Status ok
    if status == "ok":
        return {
            "provider": provider,
            "status": "ok",
            "response": api_result.get("response", ""),
            "model": model,
            "usage": api_result.get("usage", {}),
            "timestamp": timestamp,
            "request_id": request_id,
        }

    # Other error
    return {
        "provider": provider,
        "status": "error",
        "error": api_result.get("error", "Unknown error"),
        "model": model,
        "timestamp": timestamp,
        "request_id": request_id,
    }

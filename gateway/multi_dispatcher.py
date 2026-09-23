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



# AI Socket registry: 各providerは既存の adapters_<provider>_socket.py の
# Socket class(GPTSocket/ClaudeSocket/GeminiSocket/PerplexitySocket)を
# そのまま再利用する。新規Socket実装は行わない。
_PROVIDER_SOCKETS = {
    "gpt":        ("adapters_gpt_socket", "GPTSocket", "gpt-4"),
    "claude":     ("adapters_claude_socket", "ClaudeSocket", "claude-opus-5"),
    "gemini":     ("adapters_gemini_socket", "GeminiSocket", "gemini-2.0-flash"),
    "perplexity": ("adapters_perplexity_socket", "PerplexitySocket", "sonar-pro"),
}


def _call_provider(provider: str,
                   request_text: str,
                   model: str,
                   title: str,
                   common_request_id: str,
                   timestamp: str) -> Dict[str, Any]:
    """
    Call individual AI provider Socket and return structured result.

    HAB -> Socket(既存 adapters_<provider>_socket.py) -> AI API -> HAB という
    経路に統一する(各providerで個別にadapterをimportして直接呼ぶ実装を廃止)。

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
    if provider not in _PROVIDER_SOCKETS:
        return {
            "provider": provider,
            "status": "error",
            "error": f"Unsupported provider: {provider}",
            "timestamp": timestamp,
            "request_id": common_request_id,
            "model": model,
        }

    module_name, class_name, default_model = _PROVIDER_SOCKETS[provider]
    resolved_model = model or default_model

    try:
        socket_module = __import__(module_name)
        socket = getattr(socket_module, class_name)()
        api_result = socket.request(request_text, resolved_model, title)
        return _format_result(
            provider=provider,
            api_result=api_result,
            model=resolved_model,
            timestamp=timestamp,
            request_id=common_request_id,
        )

    except ImportError as e:
        # Socket/Adapter module not found
        return {
            "provider": provider,
            "status": "error",
            "error": f"Adapter not available: {str(e)}",
            "timestamp": timestamp,
            "request_id": common_request_id,
            "model": resolved_model,
        }

    except Exception as e:
        # Unexpected error
        return {
            "provider": provider,
            "status": "error",
            "error": f"Dispatch error: {str(e)}",
            "timestamp": timestamp,
            "request_id": common_request_id,
            "model": resolved_model,
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

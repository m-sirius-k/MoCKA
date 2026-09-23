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
  - JARVIS integration: E2E connection via evaluate() (minimal)

Date: 2026-09-22
Status: E2E Multi-AI implementation + JARVIS integration
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

_gateway_path = Path(__file__).parent
_mocka_root = _gateway_path.parent
if str(_gateway_path) not in sys.path:
    sys.path.insert(0, str(_gateway_path))
if str(_mocka_root) not in sys.path:
    sys.path.insert(0, str(_mocka_root))


def dispatch_multi_request(request_text: str,
                          providers: List[str] = None,
                          models: Dict[str, str] = None,
                          title: str = "Multi-AI Request",
                          decision_id: str = None) -> Dict[str, Any]:
    """
    Dispatch single request to multiple AI providers and collect responses.

    STEP 2: JARVIS integration - E2E minimal connection.
    If decision_id provided, call JARVIS evaluate() before dispatching to providers.

    Args:
        request_text: Text to send to all AI providers
        providers: List of provider names (default: all available)
        models: Dict of provider -> model mapping (default: use provider defaults)
        title: Title for HAB event logging
        decision_id: Optional decision ID for JARVIS evaluate

    Returns:
        {
            "status": "all_ok" | "partial_ok" | "all_error",
            "request_id": str (common request ID for all providers),
            "jarvis": {} (JARVIS evaluate result, if decision_id provided),
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

    jarvis_result = None

    # STEP 2: Call JARVIS evaluate if decision_id provided
    if decision_id:
        jarvis_result = _call_jarvis(
            decision_id=decision_id,
            request_id=common_request_id,
            request_text=request_text,
            title=title,
            timestamp=timestamp
        )
        print(f"[dispatch_multi_request] JARVIS evaluate called for decision_id={decision_id}")
        print(f"  JARVIS result: {jarvis_result}")

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

    response = {
        "status": overall_status,
        "request_id": common_request_id,
        "results": results,
        "summary": summary,
        "timestamp": timestamp,
    }

    # STEP 2: Include JARVIS result in response if available
    if jarvis_result:
        response["jarvis"] = jarvis_result

    return response


def _call_jarvis(decision_id: str,
                request_id: str,
                request_text: str,
                title: str,
                timestamp: str) -> Dict[str, Any]:
    """
    STEP 2: Call JARVIS evaluate() before dispatching to Multi-AI providers.

    Minimal connection: JARVIS receives decision_id and returns evaluation result.
    Failures in JARVIS do not block multi-AI dispatch (fail-open design).

    Args:
        decision_id: Decision ID for JARVIS to evaluate
        request_id: Common request ID (for tracing)
        request_text: Original request text
        title: Request title
        timestamp: Request timestamp

    Returns:
        {
            "decision_id": str,
            "request_id": str,
            "status": "evaluated" | "error",
            "jarvis_decision": dict (if evaluated),
            "jarvis_error": str (if error),
            "timestamp": str,
        }
    """
    try:
        from runtime.jarvis.core.engine import JarvisEngine

        jarvis = JarvisEngine()
        jarvis_decision = jarvis.evaluate(decision_id)

        print(f"[_call_jarvis] JarvisEngine.evaluate() succeeded for decision_id={decision_id}")
        print(f"  Result: {jarvis_decision}")

        return {
            "decision_id": decision_id,
            "request_id": request_id,
            "status": "evaluated",
            "jarvis_decision": jarvis_decision,
            "timestamp": timestamp,
        }

    except ImportError as e:
        # JARVIS module not available
        print(f"[_call_jarvis] Import error (JARVIS module not found): {e}")
        return {
            "decision_id": decision_id,
            "request_id": request_id,
            "status": "error",
            "jarvis_error": f"JARVIS module import failed: {str(e)}",
            "timestamp": timestamp,
        }

    except Exception as e:
        # Other error in JARVIS evaluate
        print(f"[_call_jarvis] JARVIS evaluate error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "decision_id": decision_id,
            "request_id": request_id,
            "status": "error",
            "jarvis_error": f"JARVIS evaluate failed: {str(e)}",
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

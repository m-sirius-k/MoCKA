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


def dispatch_with_orchestra_session(request_text: str,
                                    providers: List[str] = None,
                                    models: Dict[str, str] = None,
                                    title: str = "Orchestra HAB Integration",
                                    decision_id: str = None) -> Dict[str, Any]:
    """
    Phase 3: Dispatch request using real Orchestra Runtime Browser/Context/Page.

    This function checks if Orchestra has set a valid Browser/Context/Page session
    via browser_session_handler, and uses that session context for the dispatch.

    Result is recorded to Event Store via existing event_buffer pathway.

    Args:
        request_text: Request to dispatch
        providers: AI providers (default: gpt)
        models: Model mapping
        title: Request title
        decision_id: Optional JARVIS decision ID

    Returns:
        Standard dispatch_multi_request response with orchestra_session_status
    """
    from browser_session_handler import get_orchestra_session

    browser, context, page = get_orchestra_session()

    result = {
        "orchestra_session_status": "not_set",
        "browser_available": browser is not None,
        "context_available": context is not None,
        "page_available": page is not None,
    }

    if browser is None and context is None and page is None:
        result["error"] = "ORCHESTRA_ENTRY_NOT_CONNECTED: No Orchestra session found"
        return result

    # Session found - dispatch normally with standard flow
    dispatch_result = dispatch_multi_request(
        request_text=request_text,
        providers=providers or ["gpt"],
        models=models,
        title=title,
        decision_id=decision_id
    )

    # Enrich result with Orchestra session metadata
    dispatch_result["orchestra_session_status"] = "connected"
    dispatch_result["orchestra_session_metadata"] = {
        "browser_id": id(browser) if browser else None,
        "context_id": id(context) if context else None,
        "page_id": id(page) if page else None,
        "source": "orchestra_runtime",
    }

    # Record to Event Store via existing event_buffer pathway (Phase 3 Event Bridge)
    try:
        import sys
        _interface_path = _mocka_root / "interface"
        if str(_interface_path) not in sys.path:
            sys.path.insert(0, str(_interface_path))
        from event_buffer import get_buffer

        now = datetime.now(timezone.utc)
        summary = dispatch_result.get("summary", {})
        summary_text = (
            f"ok={summary.get('ok', 0)}, "
            f"error={summary.get('error', 0)}, "
            f"not_verified={summary.get('not_verified', 0)}"
        )

        # Use same event format as gateway.py for consistency
        event = {
            "title": f"Multi-AI Request: {title}",
            "short_summary": summary_text,
            "when": now.isoformat(),
            "who_actor": "MultiAI/Dispatcher",
            "ai_actor": "Orchestra",
            "what_type": "multi_ai_request",
            "free_note": f"request_id={dispatch_result.get('request_id')},orchestra_session=connected",
            "where_component": "gateway_multi_dispatcher",
            "lifecycle_phase": "in_operation",
            "why_purpose": "orchestra_hab_integration",
            "request_id": dispatch_result.get('request_id'),  # PHASE 5: Event Gate compatibility
        }
        get_buffer().push(event)
        print(f"[dispatch_with_orchestra_session] Event pushed to buffer: request_id={dispatch_result.get('request_id')}")
    except Exception as e:
        print(f"[dispatch_with_orchestra_session] WARNING: Event buffer write failed: {e}")
        import traceback
        traceback.print_exc()

    return dispatch_result


def dispatch_multi_request(request_text: str,
                          providers: List[str] = None,
                          models: Dict[str, str] = None,
                          title: str = "Multi-AI Request",
                          decision_id: str = None) -> Dict[str, Any]:
    """
    Dispatch single request to multiple AI providers and collect responses.

    STEP 2: JARVIS integration - E2E minimal connection.
    If decision_id provided, call JARVIS recall_experience() before dispatching to providers.
    JARVIS Decision context is embedded in request_text for GPT and other providers.

    Args:
        request_text: Text to send to all AI providers
        providers: List of provider names (default: all available)
        models: Dict of provider -> model mapping (default: use provider defaults)
        title: Title for HAB event logging
        decision_id: Optional decision ID for JARVIS recall

    Returns:
        {
            "status": "all_ok" | "partial_ok" | "all_error",
            "request_id": str (common request ID for all providers),
            "jarvis": {} (JARVIS recall result, if decision_id provided),
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
    enhanced_request_text = request_text

    # STEP 2: Call JARVIS recall_experience if decision_id provided
    if decision_id:
        jarvis_result = _call_jarvis(
            decision_id=decision_id,
            request_id=common_request_id,
            request_text=request_text,
            title=title,
            timestamp=timestamp
        )
        print(f"[dispatch_multi_request] JARVIS recall called for decision_id={decision_id}")
        print(f"  JARVIS result status: {jarvis_result.get('status')}")

        # STEP 2: Build enhanced request_text with Decision context if found
        if jarvis_result.get('status') == 'found' and jarvis_result.get('jarvis_decision'):
            enhanced_request_text = _build_request_with_decision_context(
                original_request_text=request_text,
                jarvis_decision=jarvis_result.get('jarvis_decision'),
                decision_id=jarvis_result.get('decision_id')
            )
            print(f"[dispatch_multi_request] Enhanced request_text with Decision context")
            print(f"  Decision ID: {jarvis_result.get('decision_id')}")

    for provider in providers:
        result = _call_provider(
            provider=provider,
            request_text=enhanced_request_text,
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

    # IP-007: Record lineage events to Event Store for each provider result
    # Reuse existing event_gate interface (vendor/model/runtime/source fields)
    _record_lineage_events(
        results=results,
        request_id=common_request_id,
        timestamp=timestamp,
        session_metadata={"source": "orchestra_runtime"}
    )

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


def _build_request_with_decision_context(original_request_text: str,
                                         jarvis_decision: Dict[str, Any],
                                         decision_id: str) -> str:
    """
    Build enhanced request_text with JARVIS Decision context.

    STEP 2: Minimal binding - embed Decision info in request_text so it flows
    naturally through the provider pipeline without changing Socket/Adapter signatures.

    Only includes fields that actually exist in jarvis_decision (no speculation).

    Args:
        original_request_text: Original user request
        jarvis_decision: Decision dict from jarvis_result['jarvis_decision']
        decision_id: Decision ID (for clarity in context block)

    Returns:
        Enhanced request_text with Decision context prepended
    """
    context_lines = ["[JARVIS DECISION CONTEXT]"]

    if decision_id:
        context_lines.append(f"Decision ID: {decision_id}")

    # Add only fields that actually exist in jarvis_decision
    if jarvis_decision.get('title'):
        context_lines.append(f"Title: {jarvis_decision.get('title')}")

    if jarvis_decision.get('decision'):
        context_lines.append(f"Decision: {jarvis_decision.get('decision')}")

    if jarvis_decision.get('rationale'):
        context_lines.append(f"Rationale: {jarvis_decision.get('rationale')}")

    if jarvis_decision.get('approved_by'):
        context_lines.append(f"Approved By: {jarvis_decision.get('approved_by')}")

    if jarvis_decision.get('approved_at'):
        context_lines.append(f"Approved At: {jarvis_decision.get('approved_at')}")

    context_lines.append("[END JARVIS DECISION CONTEXT]")
    context_lines.append("")
    context_lines.append("Original request:")
    context_lines.append(original_request_text)

    enhanced_text = "\n".join(context_lines)
    print(f"[_build_request_with_decision_context] Enhanced request length: {len(enhanced_text)} chars")

    return enhanced_text


def _call_jarvis(decision_id: str,
                request_id: str,
                request_text: str,
                title: str,
                timestamp: str) -> Dict[str, Any]:
    """
    CASE B: Call JARVIS recall_experience() to retrieve past decisions.

    Minimal connection: JARVIS reads decision_ledger and returns most recent Active decision.
    Failures in JARVIS do not block multi-AI dispatch (fail-open design).

    Args:
        decision_id: Decision ID (unused in MVP - for compatibility)
        request_id: Common request ID (for tracing)
        request_text: Original request text (used as intent hint)
        title: Request title
        timestamp: Request timestamp

    Returns:
        {
            "decision_id": str (if found),
            "request_id": str,
            "status": "found" | "empty" | "error",
            "jarvis_decision": dict (if found),
            "jarvis_error": str (if error),
            "timestamp": str,
        }
    """
    try:
        from runtime.jarvis.core.engine import JarvisEngine

        jarvis = JarvisEngine()
        recall_result = jarvis.recall_experience(current_intent=request_text)

        print(f"[_call_jarvis] JarvisEngine.recall_experience() succeeded")
        print(f"  Status: {recall_result['status']}")
        if recall_result['status'] == 'found' and recall_result['matches']:
            decision = recall_result['matches'][0]
            print(f"  Decision ID: {decision.get('decision_id')}")
            print(f"  Title: {decision.get('title')}")

        return {
            "decision_id": recall_result.get('matches', [{}])[0].get('decision_id') if recall_result['status'] == 'found' else None,
            "request_id": request_id,
            "status": recall_result.get('status', 'error'),
            "jarvis_decision": recall_result.get('matches', [{}])[0] if recall_result['status'] == 'found' else None,
            "jarvis_gap": recall_result.get('gap'),
            "timestamp": timestamp,
        }

    except ImportError as e:
        print(f"[_call_jarvis] Import error (JARVIS module not found): {e}")
        return {
            "decision_id": None,
            "request_id": request_id,
            "status": "error",
            "jarvis_error": f"JARVIS module import failed: {str(e)}",
            "timestamp": timestamp,
        }

    except Exception as e:
        print(f"[_call_jarvis] JARVIS recall_experience error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "decision_id": None,
            "request_id": request_id,
            "status": "error",
            "jarvis_error": f"JARVIS recall_experience failed: {str(e)}",
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
    "orchestra_web": ("adapters_orchestra_socket", "OrchestraSocket", "default"),
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


def _record_lineage_events(results: List[Dict[str, Any]],
                          request_id: str,
                          timestamp: str,
                          session_metadata: Dict[str, Any] = None) -> None:
    """
    IP-007: Record AI lineage events to Event Store.
    SB-007 CONTRACT CORRECTION (Option 4): Producer-side adaptation to existing Event Gate contract.

    Reuse existing event_gate interface (vendor/model/runtime/source fields).
    Adapt lineage payload to satisfy existing validate() requirements:
    - what_type: changed from 'ai_lineage' to 'audit' (ALLOWED_WHAT_TYPE)
    - who_session: generated in SESSION_YYYYMMDD_HHMMSS format
    - how_trigger: set from dispatch context
    - where_path: set to dispatcher module file path
    - who_role: set to 'automation'
    - after_hash: generated from response JSON
    - No new component. No schema/validation changes.

    Args:
        results: List of provider results from dispatch_multi_request()
        request_id: Common request ID for all providers
        timestamp: Event timestamp (ISO8601)
        session_metadata: Optional session context metadata
    """
    import hashlib
    from datetime import datetime, timezone

    try:
        # Load existing event_gate interface
        from phi_os.event_gate import process_event

        if not results:
            return

        # Generate who_session from timestamp: SESSION_YYYYMMDD_HHMMSS
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            who_session = dt.strftime('SESSION_%Y%m%d_%H%M%S')
        except Exception:
            # Fallback: use current time
            who_session = datetime.now(timezone.utc).strftime('SESSION_%Y%m%d_%H%M%S')

        # Dispatcher file path for where_path
        dispatcher_path = str(Path(__file__).resolve())

        for result in results:
            # Skip non-OK results (error/NOT_VERIFIED don't get lineage record)
            if result.get("status") != "ok":
                continue

            # Generate after_hash from response JSON
            response_text = result.get("response", "")
            after_hash = hashlib.sha256(response_text.encode()).hexdigest()[:16]

            # Adapt payload to existing Event Gate contract (validate() requirements)
            # Option 4: Producer supplies required Canonical fields
            lineage_payload = {
                # Canonical Event fields (required by validate())
                "what_type": "audit",  # CHANGED: from 'ai_lineage' to valid ALLOWED_WHAT_TYPE
                "who_actor": "orchestra_multi_dispatcher",
                "who_role": "automation",  # ADDED: required by EventPayload dataclass
                "who_session": who_session,  # ADDED: generated in SESSION_YYYYMMDD_HHMMSS format
                "what_title": f"AI Lineage: {result.get('provider')} ({result.get('model')})",  # ADDED: Canonical field
                "where_component": "orchestra",
                "where_path": dispatcher_path,  # ADDED: required field
                "why_purpose": "Record AI provider execution lineage (orchestrator audit)",  # MODIFIED: 10+ chars
                "how_trigger": "dispatch_multi_request()",  # ADDED: required field
                "after_hash": after_hash,  # ADDED: Replay guarantee (Canonical field)

                # Persistence fields (preserved in event_gate._write())
                "vendor": result.get("provider", "unknown"),
                "model": result.get("model", ""),
                "runtime": "orchestra_dispatch",
                "source": session_metadata.get("source", "live") if session_metadata else "live",
                "request_id": request_id,

                # Event Gate convenience fields (mapped by event_gate._write())
                "when_ts": result.get("timestamp", timestamp),
                "description": f"Provider: {result.get('provider')}, Model: {result.get('model')}, Status: ok",
            }

            # Call existing event_gate interface (no new component)
            # Pass event_source='orchestra_lineage' to track origin
            lineage_status = "UNKNOWN"
            try:
                response = process_event(lineage_payload, event_source='orchestra_lineage')
                if response.get('status') == 'ok':
                    lineage_status = "RECORDED"
                    print(f"[IP-007] Lineage recorded: event_id={response.get('event_id')}, "
                          f"provider={result.get('provider')}, model={result.get('model')}, "
                          f"who_session={who_session}, after_hash={after_hash}")
                else:
                    # IP-007 Option A: Lineage rejected - record failure event
                    lineage_status = "FAILED_RECORDED"
                    _record_lineage_failure(
                        process_event=process_event,
                        request_id=request_id,
                        provider=result.get("provider"),
                        reason=f"Validation rejected: {response.get('errors')}",
                        timestamp=timestamp,
                        who_session=who_session
                    )
            except Exception as e:
                # IP-007 Option A: Lineage exception - record failure event
                lineage_status = "FAILED_RECORDED"
                _record_lineage_failure(
                    process_event=process_event,
                    request_id=request_id,
                    provider=result.get("provider"),
                    reason=f"Exception: {str(e)}",
                    timestamp=timestamp,
                    who_session=who_session
                )

    except ImportError as e:
        print(f"[IP-007] ERROR: event_gate import failed: {str(e)} - lineage recording blocked")
    except Exception as e:
        print(f"[IP-007] ERROR: Unexpected error in _record_lineage_events: {str(e)}")


def _record_lineage_failure(process_event, request_id: str, provider: str,
                           reason: str, timestamp: str, who_session: str = None) -> None:
    """
    IP-007 + SB-007 CORRECTION: Record lineage recording failure to Event Store.

    Failure event also adapts to existing Event Gate contract (validate() requirements).
    - what_type: changed from 'ai_lineage_failed' to 'incident' (ALLOWED_WHAT_TYPE)
    - Supplies required Canonical fields: who_session, how_trigger, where_path, before/after

    Ensures failure is recorded (FAILED_RECORDED state).
    If failure-event itself fails, print only (no recursive recording).

    Args:
        process_event: The event_gate.process_event function
        request_id: Original Orchestra request ID
        provider: AI provider name
        reason: Failure reason
        timestamp: Event timestamp
        who_session: Optional session ID for correlation
    """
    from datetime import datetime, timezone
    from pathlib import Path

    try:
        # Generate who_session if not provided
        if not who_session:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                who_session = dt.strftime('SESSION_%Y%m%d_%H%M%S')
            except Exception:
                who_session = datetime.now(timezone.utc).strftime('SESSION_%Y%m%d_%H%M%S')

        dispatcher_path = str(Path(__file__).resolve())

        # Adapt failure payload to existing Event Gate contract
        failure_payload = {
            # Canonical Event fields (required by validate())
            "what_type": "incident",  # CHANGED: from 'ai_lineage_failed' to valid ALLOWED_WHAT_TYPE
            "who_actor": "orchestra_multi_dispatcher",
            "who_role": "automation",  # ADDED: required by EventPayload dataclass
            "who_session": who_session,  # ADDED: session correlation
            "what_title": f"AI Lineage Failure: {provider}",  # ADDED: Canonical field
            "where_component": "orchestra",
            "where_path": dispatcher_path,  # ADDED: required field
            "why_purpose": f"Record lineage recording failure for {provider}",  # 10+ chars
            "how_trigger": "lineage_exception_handler()",  # ADDED: required field
            "before_state": f"lineage_pending:provider={provider}",  # ADDED: Replay guarantee

            # Event identification and tracking
            "request_id": request_id,
            "when_ts": timestamp,
            "description": f"Provider: {provider}, Failure: {reason}",
        }

        # Call process_event for failure event
        # If this also fails, we print only (no recursive recording)
        response = process_event(failure_payload, event_source='orchestra_lineage')
        if response.get('status') == 'ok':
            print(f"[IP-007] Lineage failure recorded: event_id={response.get('event_id')}, "
                  f"provider={provider}, who_session={who_session}")
        else:
            # Failure-event itself failed - print only (RECORDING_FAILURE_UNRECORDED)
            print(f"[IP-007] ERROR: Lineage failure-event also failed: {response.get('errors')}, "
                  f"LINEAGE_STATUS=RECORDING_FAILURE_UNRECORDED, "
                  f"request_id={request_id}, provider={provider}, reason={reason}")
    except Exception as e:
        # Failure-event exception - print only (RECORDING_FAILURE_UNRECORDED)
        print(f"[IP-007] ERROR: Lineage failure-event exception: {str(e)}, "
              f"LINEAGE_STATUS=RECORDING_FAILURE_UNRECORDED, "
              f"request_id={request_id}, provider={provider}, reason={reason}")

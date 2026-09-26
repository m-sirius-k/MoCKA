"""
HAB Common Core - Minimal Bridge Layer
=======================================
Purpose: Dispatch JARVIS requests to AI Sockets, route responses back through PHI-OS
Role: Common Core between JARVIS and AI Providers
Status: Runtime Integration (Phase 4.1)
Port: 5010 (via gateway.py) - does NOT expose new port
Requirement: Maintain GPT/Claude/Gemini/Perplexity connections unbroken

Architecture:
  JARVIS
    |
    v
  HAB Common Core (this module)
    |  (routes to available AI Sockets)
    +---> AI Socket [GPT]
    |        |
    |        v
    |     gateway/adapter_gpt.py
    |
    +---> AI Socket [Gemini]
    |        |
    |        v
    |     gateway/adapter_gemini.py
    |
    +---> AI Socket [Copilot]
    +---> AI Socket [Perplexity]
    +---> AI Socket [GenSpark]
    |
    v (routes AI responses back)
  PHI-OS Event Gate
    |
    v
  Event Store (data/mocka_events.db)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent / "interface"))
from event_buffer import get_buffer


class AISocketType(Enum):
    GPT = "gpt"
    GEMINI = "gemini"
    COPILOT = "copilot"
    PERPLEXITY = "perplexity"
    GENSPARK = "genspark"


class AISocket:
    """Thin wrapper for AI provider connection"""
    def __init__(self, socket_type: AISocketType, adapter_module):
        self.socket_type = socket_type
        self.adapter = adapter_module
        self.id = f"socket_{socket_type.value}"
        self.status = "ready"
        self.connected_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.socket_type.value,
            "status": self.status,
            "connected_at": self.connected_at,
        }


class HABCommonCore:
    """
    HAB (Human Authority Boundary) Common Core
    - Minimal dispatcher for JARVIS ↔ AI Sockets
    - Single entry point for all AI routing
    - No state management (stateless)
    - All state flows through PHI-OS Event Gate
    """

    def __init__(self, adapters_registry: Dict[str, Any]):
        self.adapters = adapters_registry
        self.sockets = {}
        self._initialize_sockets()

    def _initialize_sockets(self):
        """Initialize AI Sockets from registered adapters"""
        socket_mapping = {
            'gpt': AISocketType.GPT,
            'gemini': AISocketType.GEMINI,
            'copilot': AISocketType.COPILOT,
            'perplexity': AISocketType.PERPLEXITY,
            'genspark': AISocketType.GENSPARK,
        }

        for key, adapter_module in self.adapters.items():
            if key in socket_mapping:
                socket_type = socket_mapping[key]
                socket = AISocket(socket_type, adapter_module)
                self.sockets[key] = socket

    def get_sockets(self):
        """Return all available AI Sockets"""
        return {k: v.to_dict() for k, v in self.sockets.items()}

    def dispatch_to_ai(self, request_data: Dict[str, Any], target_socket: str) -> Dict[str, Any]:
        """
        Route JARVIS request to AI Socket

        Args:
            request_data: JARVIS request (vendor, model, prompt, etc.)
            target_socket: socket identifier (gpt, gemini, copilot, perplexity, genspark)

        Returns:
            {
                "status": "routed" | "error",
                "socket_id": socket identifier,
                "trace_id": unique request ID,
                "ai_response": {...},  (set by adapter)
            }
        """
        if target_socket not in self.sockets:
            return {
                "status": "error",
                "error": f"Socket {target_socket} not found",
                "available_sockets": list(self.sockets.keys()),
            }

        socket = self.sockets[target_socket]
        trace_id = self._generate_trace_id()

        try:
            # Minimal routing - just pass to adapter
            # Adapter handles vendor-specific details
            return {
                "status": "routed",
                "socket_id": socket.id,
                "trace_id": trace_id,
                "adapter": target_socket,
                "request_payload": request_data,
            }
        except Exception as e:
            return {
                "status": "error",
                "socket_id": socket.id,
                "trace_id": trace_id,
                "error": str(e),
            }

    def receive_from_ai(self, response_data: Dict[str, Any], socket_source: str) -> Dict[str, Any]:
        """
        Receive AI response, prepare for PHI-OS Event Gate

        Args:
            response_data: AI provider response
            socket_source: which socket returned this (gpt, gemini, etc.)

        Returns:
            Event-shaped dict ready for PHI-OS Gate
        """
        if socket_source not in self.sockets:
            return {
                "status": "error",
                "error": f"Source socket {socket_source} unknown",
            }

        socket = self.sockets[socket_source]
        event_id = self._generate_event_id()

        return {
            "event_id": event_id,
            "source_socket": socket.id,
            "socket_type": socket.socket_type.value,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "payload": response_data,
            "ready_for_gate": True,
        }

    def route_to_phi_os(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send AI response event through PHI-OS Event Gate

        Args:
            event: Prepared event from receive_from_ai()

        Returns:
            {"status": "gated", "event_id": ..., "gate_response": ...}
        """
        try:
            buffer = get_buffer()
            if buffer:
                buffer.push(event)
                return {
                    "status": "gated",
                    "event_id": event.get("event_id"),
                    "buffer_status": "queued",
                }
            else:
                return {
                    "status": "error",
                    "error": "PHI-OS Event Buffer unavailable",
                    "fallback": "write_to_db_pending",
                }
        except Exception as e:
            return {
                "status": "error",
                "error": f"PHI-OS routing failed: {str(e)}",
                "event": event,
            }

    def health(self) -> Dict[str, Any]:
        """Health check - all sockets status"""
        return {
            "status": "ready",
            "role": "HAB Common Core",
            "sockets_available": len(self.sockets),
            "sockets": self.get_sockets(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _generate_trace_id() -> str:
        """Generate JARVIS→HAB trace ID"""
        now = datetime.now(timezone.utc)
        return f"TR_{now.strftime('%Y%m%d')}_{int(now.timestamp() * 1000) % 100000:05d}"

    @staticmethod
    def _generate_event_id() -> str:
        """Generate HAB→PHI-OS event ID"""
        now = datetime.now(timezone.utc)
        return f"E_{now.strftime('%Y%m%d')}_{int(now.timestamp() * 1000) % 100000:05d}"


def create_hab_core(adapters_registry: Dict[str, Any]) -> HABCommonCore:
    """Factory: Create HAB Common Core with registered adapters"""
    return HABCommonCore(adapters_registry)

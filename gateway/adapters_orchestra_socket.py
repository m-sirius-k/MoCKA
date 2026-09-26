# -*- coding: utf-8 -*-
"""
Orchestra Socket - Web AI Provider Socket (Playwright-based)

Purpose:
  Integrate existing Orchestra (orchestra_one_host.py) as a MultiDispatcher provider.
  Calls existing orchestra_one_host.py via subprocess + --test mode.
  Returns responses in standard Socket format.

Design:
  - Uses existing orchestra_one_host.py (no modifications)
  - Invokes via subprocess + --test flag (stdin/stdout JSON)
  - No Chrome Extension dependency (Playwright handles automation)
  - Minimal adapter layer (50 lines)

Status: Minimal implementation, E2E verification required
"""

import json
import subprocess
import sys
import struct
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone


class OrchestraSocket:
    """Orchestra Web AI Socket - invoke existing orchestra_one_host.py"""

    def __init__(self):
        self.orchestra_path = Path(__file__).parent.parent / \
            "PlanningCaliber" / "workshop" / "Orchestra_Project" / \
            "orchestra_one" / "orchestra_one_host.py"
        self.timeout_seconds = 120  # 2 minutes max

    def request(self, request_text: str, model: str = "default",
                title: str = "Orchestra Request") -> dict:
        """
        Standard Socket interface - called by MultiDispatcher.

        Args:
            request_text: Prompt/query to send to all Web AIs
            model: Model identifier (unused for Orchestra, kept for compatibility)
            title: Request title (for logging)

        Returns:
            {
                "status": "ok" | "error",
                "response": str (if ok),
                "usage": dict,
                "error": str (if error),
            }
        """
        try:
            # Invoke existing orchestra_one_host.py
            results = self._invoke_orchestra(request_text)

            if results is None or "results" not in results:
                return {
                    "status": "error",
                    "error": "Invalid Orchestra response format",
                }

            # Aggregate results from all AIs
            aggregated_response = self._aggregate_results(results["results"])

            return {
                "status": "ok",
                "response": aggregated_response,
                "usage": {
                    "ais_queried": len(results.get("results", {})),
                    "model": "orchestra_web",
                    "method": "subprocess_orchestra_one_host",
                },
            }

        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "error": f"Orchestra timeout after {self.timeout_seconds}s",
            }

        except FileNotFoundError:
            return {
                "status": "error",
                "error": f"orchestra_one_host.py not found at {self.orchestra_path}",
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Orchestra invocation failed: {str(e)}",
            }

    def _invoke_orchestra(self, prompt: str) -> dict:
        """
        Invoke existing orchestra_one_host.py via subprocess.

        Method: --test flag + stdin/stdout JSON (Native Messaging format)

        Args:
            prompt: User prompt/query

        Returns:
            Parsed response dict from orchestra_one_host.py
            Format: {'type': 'ORCHESTRA_RESULT', 'results': {...}}
        """
        # Build request in orchestra_one_host.py format
        request_msg = {
            "type": "RUN_ORCHESTRA",
            "prompt": prompt,
        }

        try:
            # Invoke orchestra_one_host.py with --test flag
            process = subprocess.run(
                [sys.executable, str(self.orchestra_path), "--test"],
                input=json.dumps(request_msg, ensure_ascii=False).encode("utf-8"),
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,  # Don't raise CalledProcessError
            )

            # Parse response from stdout
            if process.returncode != 0:
                stderr_text = process.stderr.decode("utf-8", errors="replace")
                raise RuntimeError(f"Orchestra process failed (code {process.returncode}): {stderr_text[:200]}")

            response_bytes = process.stdout
            if not response_bytes:
                raise RuntimeError("Orchestra returned empty response")

            # Handle Native Messaging format: 4-byte length + JSON
            # orchestra_one_host.py sends in Native Messaging format even in --test mode
            import struct
            try:
                # Try to parse Native Messaging format (4 bytes little-endian length)
                if len(response_bytes) >= 4:
                    message_length = struct.unpack('<I', response_bytes[:4])[0]
                    if 4 < message_length + 4 <= len(response_bytes):
                        # Valid Native Messaging format
                        json_bytes = response_bytes[4:4+message_length]
                        response_text = json_bytes.decode("utf-8", errors="replace")
                    else:
                        # Invalid format, try direct JSON parsing
                        response_text = response_bytes.decode("utf-8", errors="replace").strip()
                else:
                    # Too short, direct parsing
                    response_text = response_bytes.decode("utf-8", errors="replace").strip()
            except struct.error:
                # Struct unpacking failed, direct JSON parsing
                response_text = response_bytes.decode("utf-8", errors="replace").strip()

            # Find JSON start (handle potential logging output before JSON)
            json_start = response_text.find('{')
            if json_start >= 0:
                response_text = response_text[json_start:]

            if not response_text:
                raise RuntimeError("No JSON found in Orchestra response")

            # Parse JSON response
            response_msg = json.loads(response_text)

            # Validate response structure
            if not isinstance(response_msg, dict):
                raise RuntimeError(f"Invalid response type: {type(response_msg)}")

            if response_msg.get("type") != "ORCHESTRA_RESULT":
                raise RuntimeError(f"Unexpected response type: {response_msg.get('type')}")

            return response_msg

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Orchestra JSON response: {str(e)}. Response was: {response_text[:100]}" if response_text else str(e))

    def _aggregate_results(self, results: Dict[str, str]) -> str:
        """
        Aggregate responses from multiple AIs into single string.

        Args:
            results: Dict of {AI_name: response_text}

        Returns:
            Formatted aggregated response
        """
        if not results:
            return "[No responses from Orchestra AIs]"

        lines = ["[Orchestra Web AI Responses]", ""]

        for ai_name, response_text in results.items():
            # Handle error responses
            if response_text.startswith("ERROR:"):
                lines.append(f"[{ai_name}] (FAILED)")
                lines.append(response_text[:100])
            else:
                lines.append(f"[{ai_name}]")
                lines.append(response_text[:500])  # Truncate to 500 chars per AI

            lines.append("")

        return "\n".join(lines)

# -*- coding: utf-8 -*-
"""
Copilot Socket - Microsoft Copilot AI Provider Socket
"""

from socket_base import submit_to_hab


class CopilotSocket:
    """Minimal Copilot Socket using common HAB submission."""

    def submit(self, model: str, runtime: str, title: str,
               description: str, tags: list = None) -> dict:
        """Submit Copilot request to HAB."""
        return submit_to_hab(model, runtime, title, description, tags)

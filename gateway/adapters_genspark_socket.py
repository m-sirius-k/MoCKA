# -*- coding: utf-8 -*-
"""
GenSpark Socket - GenSpark AI Provider Socket
"""

from socket_base import submit_to_hab


class GenSparkSocket:
    """Minimal GenSpark Socket using common HAB submission."""

    def submit(self, model: str, runtime: str, title: str,
               description: str, tags: list = None) -> dict:
        """Submit GenSpark request to HAB."""
        return submit_to_hab(model, runtime, title, description, tags)

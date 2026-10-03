#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoCKA 3.0 Governance Constants
Shared constants for governance pipeline and authorization.
"""

import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# Default Deny: Read-only tools bypass GL8-GL12 authorization checks.
# Any tool NOT in this list requires authorization (_authz envelope).
READ_ONLY_TOOLS = {
    "mocka_get_overview",
    "mocka_get_essence",
    "mocka_get_todo",
    "mocka_list_events",
    "mocka_read_event",
    "mocka_search",
    "mocka_get_incidents",
    "mocka_get_guidelines",
    "mocka_get_command_center",
    "mocka_check_utf8",
    "mocka_registry_get",
    "mocka_registry_current_state",
    "mocka_decision_get",
    "mocka_decision_list",
    "mocka_integrity_get",
    "mocka_integrity_list",
}

# Write tools require governance checks (GL7 dry run).
WRITE_TOOLS = {
    "mocka_write_event",
    "mocka_add_todo",
    "mocka_update_todo",
    "mocka_seal",
}

# Governance timing parameters
GROUNDING_REFRESH_SECONDS = 60

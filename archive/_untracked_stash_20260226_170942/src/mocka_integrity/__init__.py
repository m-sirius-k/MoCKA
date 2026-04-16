"""
MoCKA Phase16 Autonomous Integrity Layer
date: 2026-02-24

note:
- This package defines an autonomous integrity subsystem.
- It MUST NOT mutate governance DB.
- It MAY create/verify anchors in a separate integrity DB.
- All serialization for signed payloads is deterministic.
"""

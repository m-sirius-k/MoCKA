"""
Phase15 -> Phase16 bridge (read-only, real crypto verify)
date: 2026-02-24

note:
- Phase15 audit scan must not mutate governance DB.
- This bridge reads integrity DB and verifies signature with a public key.
- Public key path is provided explicitly (env or argument).
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .integrity_db import IntegrityDBConfig
from .verify_anchor import verify_anchor_by_final_chain_hash


def phase15_anchor_proof_check(
    final_chain_hash: str,
    integrity_db_path: Optional[str] = None,
    public_key_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Returns Phase15-compatible structure:
      { "status": "OK"|"NG", "reason": "...", "detail": {...} }
    """

    if public_key_path is None:
        public_key_path = os.environ.get("MOCKA_PHASE16_PUBKEY_PATH")

    cfg = IntegrityDBConfig(db_path=integrity_db_path) if integrity_db_path else IntegrityDBConfig()

    res = verify_anchor_by_final_chain_hash(
        cfg,
        final_chain_hash=final_chain_hash,
        public_key_path=public_key_path,
    )

    return {"status": res.status, "reason": res.reason, "detail": res.detail}

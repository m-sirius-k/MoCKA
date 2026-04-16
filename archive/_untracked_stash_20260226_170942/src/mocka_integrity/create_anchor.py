"""
Phase16 create_anchor (Ed25519 real signature)
date: 2026-02-24
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from .payload import AnchorPayload
from .integrity_db import IntegrityDBConfig, connect_rw


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_private_key(path: str) -> Ed25519PrivateKey:
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def create_anchor(
    source_event_id: str,
    source_chain_hash: str,
    final_chain_hash: str,
    private_key_path: str,
    public_key_id: str,
    integrity_db_path: Optional[str] = None,
) -> dict:

    payload = AnchorPayload(
        source_event_id=source_event_id,
        source_chain_hash=source_chain_hash,
        final_chain_hash=final_chain_hash,
    )

    canonical_bytes = payload.canonical_bytes()
    anchor_id = _sha256_hex(canonical_bytes)

    private_key = _load_private_key(private_key_path)
    signature = private_key.sign(canonical_bytes).hex()

    cfg = IntegrityDBConfig(db_path=integrity_db_path) if integrity_db_path else IntegrityDBConfig()
    conn = connect_rw(cfg)
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO proof_anchor (
              anchor_id,
              created_utc,
              source_event_id,
              source_chain_hash,
              final_chain_hash,
              signature_ed25519,
              public_key_id,
              note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                anchor_id,
                _utc_now_iso(),
                source_event_id,
                source_chain_hash,
                final_chain_hash,
                signature,
                public_key_id,
                "ed25519_signed",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "status": "OK",
        "anchor_id": anchor_id,
        "crypto_verified": True,
    }
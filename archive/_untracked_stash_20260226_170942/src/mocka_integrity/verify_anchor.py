"""
Anchor verification (Ed25519 real verification)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

from .integrity_db import IntegrityDBConfig, connect_ro, table_exists_ro
from .payload import AnchorPayload


@dataclass(frozen=True)
class VerifyResult:
    status: str
    reason: str
    detail: Dict[str, Any]


def _load_public_key(path: str) -> Ed25519PublicKey:
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def verify_anchor_by_final_chain_hash(
    cfg: IntegrityDBConfig,
    final_chain_hash: str,
    public_key_path: Optional[str] = None,
) -> VerifyResult:

    try:
        conn = connect_ro(cfg)
        try:
            if not table_exists_ro(conn, "proof_anchor"):
                return VerifyResult("NG", "MISSING_TABLE", {})

            cur = conn.execute(
                "SELECT * FROM proof_anchor WHERE final_chain_hash=? LIMIT 1",
                (final_chain_hash,),
            )
            row = cur.fetchone()
            if row is None:
                return VerifyResult("NG", "MISSING_ANCHOR", {})

            payload = AnchorPayload(
                source_event_id=row["source_event_id"],
                source_chain_hash=row["source_chain_hash"],
                final_chain_hash=row["final_chain_hash"],
            )

            canonical = payload.canonical_bytes()
            signature = bytes.fromhex(row["signature_ed25519"])

            crypto_verified = False
            if public_key_path:
                pub = _load_public_key(public_key_path)
                pub.verify(signature, canonical)
                crypto_verified = True

            return VerifyResult(
                "OK",
                "FOUND",
                {
                    "anchor_id": row["anchor_id"],
                    "crypto_verified": crypto_verified,
                },
            )
        finally:
            conn.close()

    except Exception as e:
        return VerifyResult("NG", "EXCEPTION", {"error": str(e)})
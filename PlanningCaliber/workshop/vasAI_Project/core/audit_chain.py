"""
vasAI Core: HMAC-SHA256 audit chain.
"""
import hashlib
import hmac as _hmac
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core import event_store
from core.models import AuditReport

_DEFAULT_KEY = "vasai-default-dev-key-change-in-prod"


def _key() -> bytes:
    return os.environ.get("VASAI_HMAC_KEY", _DEFAULT_KEY).encode("utf-8")


def _sign(payload: str) -> str:
    return _hmac.new(_key(), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def sign(event_id: str, content_hash: str, prev_sig: str) -> str:
    payload = f"{event_id}:{content_hash}:{prev_sig}"
    return _sign(payload)


def verify(event_id: str, content_hash: str, prev_sig: str, sig: str) -> bool:
    expected = sign(event_id, content_hash, prev_sig)
    return _hmac.compare_digest(expected, sig)


def verify_chain(store=None) -> AuditReport:
    """全イベントを順番にverifyしてAuditReportを返す。"""
    event_store.initialize()

    chain_ok = event_store.verify_chain()
    events = event_store.list_events(limit=10000)

    broken: list[str] = []
    if not chain_ok:
        broken = ["hash_chain_broken"]

    return AuditReport(
        chain_valid=chain_ok and len(broken) == 0,
        total_events=len(events),
        broken_events=broken,
        generated_at=datetime.now(timezone.utc),
    )


def seal() -> str:
    """現在のチェーン末尾にSEALイベントを記録してhashを返す。"""
    latest_hash = event_store.get_latest_hash()
    sealed_at = datetime.now(timezone.utc).isoformat()
    payload = f"SEAL:{sealed_at}:{latest_hash}"
    sig = _sign(payload)

    event_store.append(
        who_actor="vasAI.audit_chain",
        what_type="AUDIT_SEAL",
        why_purpose="定期封印",
        content={"sealed_at": sealed_at, "latest_hash": latest_hash, "signature": sig},
        stage="AUDIT",
    )
    return sig

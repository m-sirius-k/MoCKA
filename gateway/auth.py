# -*- coding: utf-8 -*-
import hashlib
import hmac
import os
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from flask import request, abort

from actor_binding import verify_actor_id_binding, get_authenticated_actor_id

# ---- 設定 ----------------------------------------------------------------
VALID_KEYS   = set(filter(None, os.environ.get("MOCKA_API_KEYS",   "").split(",")))
HMAC_SECRET  = os.environ.get("MOCKA_HMAC_SECRET", "").encode()
DB_PATH      = Path(__file__).parent.parent / "data" / "mocka_events.db"
NONCE_TTL    = 600          # 10分（秒）
TIMESTAMP_MARGIN = 300      # ±5分（秒）

PUBLIC_PATHS = {"/api/v1/phase", "/api/v1/health", "/api/v1/connector/health"}
HMAC_PATHS   = {"/api/v1/event"}   # POST のみ HMAC 検証

# ---- nonce テーブル初期化 -------------------------------------------------
def _init_nonce_table():
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS gateway_nonces "
            "(nonce TEXT PRIMARY KEY, created_at REAL)"
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

_init_nonce_table()


# ---- メインフック ---------------------------------------------------------
def require_api_key():
    if request.path in PUBLIC_PATHS:
        return

    key = request.headers.get("X-MoCKA-Key", "").strip()
    if not key:
        abort(401, "X-MoCKA-Key header missing")
    if key not in VALID_KEYS:
        abort(403, "Invalid API key")

    if request.method == "POST" and request.path in HMAC_PATHS:
        _verify_hmac_request()


# ---- HMAC + Replay 防止 ---------------------------------------------------
def _verify_hmac_request():
    data = request.get_json(silent=True) or {}

    # --- timestamp ±5分 ---
    ts_str = data.get("timestamp", "")
    if not ts_str:
        abort(401, "timestamp is required")
    try:
        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = abs((now - ts).total_seconds())
        if diff > TIMESTAMP_MARGIN:
            abort(401, f"timestamp out of range ({int(diff)}s)")
    except Exception:
        abort(401, "timestamp parse error")

    # --- nonce 重複チェック ---
    nonce = data.get("nonce", "")
    if not nonce:
        abort(401, "nonce is required")
    if _nonce_used(nonce):
        abort(409, "Duplicate nonce — replay attack detected")
    _record_nonce(nonce)

    # --- HMAC 署名検証（秘密鍵が設定されている場合のみ） ---
    sig = data.get("hmac_sig", "")
    if HMAC_SECRET and sig:
        _check_hmac(data, sig)


def _check_hmac(data: dict, sig: str):
    payload_keys = ["title", "description", "timestamp", "nonce", "request_id"]
    payload = "&".join(f"{k}={data.get(k,'')}" for k in sorted(payload_keys))
    expected = "sha256:" + hmac.new(HMAC_SECRET, payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        abort(403, "HMAC signature mismatch")


def _nonce_used(nonce: str) -> bool:
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        cur  = conn.cursor()
        # 期限切れnonceを先に削除
        cur.execute("DELETE FROM gateway_nonces WHERE created_at < ?",
                    (time.time() - NONCE_TTL,))
        cur.execute("SELECT 1 FROM gateway_nonces WHERE nonce = ?", (nonce,))
        found = cur.fetchone() is not None
        conn.commit()
        conn.close()
        return found
    except Exception:
        return False


def _record_nonce(nonce: str):
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=10)
        conn.execute("INSERT OR IGNORE INTO gateway_nonces (nonce, created_at) VALUES (?, ?)",
                     (nonce, time.time()))
        conn.commit()
        conn.close()
    except Exception:
        pass


# ---- Actor_ID Binding (Phase 2) -----------------------------------------------

def get_request_actor_id() -> str:
    """
    Extract authenticated actor_id from current request's X-MoCKA-Key header.

    This is the CANONICAL SOURCE for actor identity.
    Must be called after require_api_key() has validated the key.

    Returns:
        actor_id derived from authenticated X-MoCKA-Key
        Raises abort(401) if key is invalid or missing
    """
    key = request.headers.get("X-MoCKA-Key", "").strip()
    if not key:
        abort(401, "X-MoCKA-Key header missing")

    actor_id = get_authenticated_actor_id(key)
    if actor_id is None:
        abort(401, "Invalid X-MoCKA-Key")

    return actor_id


def verify_event_actor_id(payload_actor_id: str = None) -> None:
    """
    Verify that payload actor_id matches authenticated identity.

    Phase 2 Boundary Enforcement:
    - Derive canonical authenticated actor_id from X-MoCKA-Key
    - Verify payload actor_id matches authenticated actor_id
    - Fail-closed (abort 401/403) on any mismatch or missing required field

    Args:
        payload_actor_id: The actor_id from request payload (may be None)

    Raises:
        abort(401) if authentication fails
        abort(403) if payload actor_id doesn't match authenticated identity
    """
    key = request.headers.get("X-MoCKA-Key", "").strip()
    if not key:
        abort(401, "X-MoCKA-Key header missing")

    # Verify the binding
    if not verify_actor_id_binding(key, payload_actor_id):
        abort(403, "Actor identity mismatch or invalid")


# institution_contract.py
from __future__ import annotations
import hmac, hashlib, time
from dataclasses import dataclass
from .capability_table import is_capability_valid, is_trust_sufficient
from .ai_session_state import AISessionStore

HMAC_SECRET = b"MOCKA_ISE_SECRET_CHANGE_IN_PRODUCTION"
REPLAY_WINDOW_SEC = 300   # 5分以内のリクエストのみ受け付ける

@dataclass
class KnockRequest:
    ai_id:            str
    capability:       list[str]   # Capability ID リスト
    role:             str
    signature:        str
    current_revision: int
    timestamp:        int = 0     # Unix timestamp（Replay Attack防止）

@dataclass
class ContractResult:
    allowed:  bool
    reason:   str = ""

def verify_signature(req: KnockRequest) -> bool:
    """HMAC-SHA256 検証。timestamp + ai_id + revision を署名対象にする。"""
    message = f"{req.timestamp}:{req.ai_id}:{req.current_revision}".encode()
    expected = hmac.new(HMAC_SECRET, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, req.signature)

def check_contract(req: KnockRequest,
                   session_store: AISessionStore) -> ContractResult:
    """
    Institution Contract 検証フロー:
      1. タイムスタンプ（Replay Attack防止）
      2. AI Registry 存在確認（未登録なら trial で自動登録）
      3. Capability ID の有効性
      4. Trust Level の充足確認
      5. HMAC Signature 検証
    """
    # 1. Replay Attack 防止
    now = int(time.time())
    if req.timestamp and abs(now - req.timestamp) > REPLAY_WINDOW_SEC:
        return ContractResult(allowed=False, reason="timestamp_expired")

    # 2. AI Registry 確認（未登録なら trial で自動登録）
    entry = session_store.get(req.ai_id)
    if entry is None:
        entry = session_store.register_new(req.ai_id, role=req.role)

    # 3. Capability ID 有効性
    for cap in req.capability:
        if not is_capability_valid(cap):
            return ContractResult(
                allowed=False,
                reason=f"unknown_capability: {cap}"
            )

    # 4. Trust Level 充足確認
    for cap in req.capability:
        if not is_trust_sufficient(cap, entry.trust_level):
            return ContractResult(
                allowed=False,
                reason=f"trust_insufficient for {cap}: "
                       f"requires more than {entry.trust_level}"
            )

    # 5. HMAC 検証（timestamp=0 は開発環境用スキップ）
    if req.timestamp != 0 and not verify_signature(req):
        return ContractResult(allowed=False, reason="signature_invalid")

    return ContractResult(allowed=True)

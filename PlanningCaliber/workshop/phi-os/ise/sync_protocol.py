# sync_protocol.py
from __future__ import annotations
import json
from pathlib import Path
from .schema import InstitutionState
from .ai_session_state import AISessionStore
from .institution_contract import KnockRequest, check_contract
from .diff_generator import get_diff_since

class ISESyncProtocol:
    """
    Knock / ACK の処理を担当する。
    app.py のエンドポイントから呼び出す。
    """

    def __init__(
        self,
        state_path:      Path,
        snapshots_dir:   Path,
        session_store:   AISessionStore,
    ):
        self.state_path    = state_path
        self.snapshots_dir = snapshots_dir
        self.session_store = session_store

    def _load_current_state(self) -> InstitutionState | None:
        if not self.state_path.exists():
            return None
        with open(self.state_path, encoding="utf-8") as f:
            d = json.load(f)
        from .schema import (
            InstitutionState, ProjectStatus, Warning, TodoItem
        )
        return InstitutionState(
            state_version       = d.get("state_version", 1),
            revision            = d.get("revision", 0),
            state_hash          = d.get("state_hash", ""),
            generated_at        = d.get("generated_at", ""),
            project             = ProjectStatus(**d.get("project", {})),
            warnings            = [Warning(**w) for w in d.get("warnings", [])],
            todos               = [TodoItem(**t) for t in d.get("todos", [])],
            decision_ledger_rev = d.get("decision_ledger_rev", 0),
            guideline_revision  = d.get("guideline_revision", 0),
        )

    def handle_knock(self, payload: dict) -> dict:
        """
        Knock 処理フロー:
          1. Institution Contract 検証
          2. 拒否 → エラー返却 + 記録
          3. 許可 → Diff 生成 → 返却
        """
        req = KnockRequest(
            ai_id            = payload.get("ai_id", ""),
            capability       = payload.get("capability", []),
            role             = payload.get("role", ""),
            signature        = payload.get("signature", ""),
            current_revision = payload.get("current_revision", 0),
            timestamp        = payload.get("timestamp", 0),
        )

        result = check_contract(req, self.session_store)

        if not result.allowed:
            return {
                "status": "rejected",
                "reason": result.reason,
            }

        # 現在の State 取得
        current = self._load_current_state()
        if current is None:
            return {"status": "error", "reason": "state_not_found"}

        # Diff 生成
        diff_response = get_diff_since(
            from_revision  = req.current_revision,
            snapshots_dir  = self.snapshots_dir,
            current_state  = current,
        )

        return {
            "status": "ok",
            **diff_response,
        }

    def handle_ack(self, payload: dict) -> dict:
        """
        ACK 処理:
          1. AI Session State を更新（last_revision / last_knock）
          2. Hash 検証（任意）
        """
        ai_id           = payload.get("ai_id", "")
        applied         = payload.get("applied", 0)
        verified_hash   = payload.get("verified_hash", "")

        current = self._load_current_state()

        # Hash 検証（送られてきた場合のみ）
        if verified_hash and current and verified_hash != current.state_hash:
            return {
                "status": "hash_mismatch",
                "expected": current.state_hash,
                "received": verified_hash,
            }

        self.session_store.update_knock(ai_id, applied)

        return {"status": "ok", "applied": applied}

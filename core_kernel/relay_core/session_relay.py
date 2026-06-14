"""
MoCKA Core Kernel — relay_core.session_relay

責務:
  時間的文脈とセッション連続性を管理するインメモリ層(SessionRelay)。

  Relayは「記憶」ではなく「流れ」を扱う。

  絶対禁止:
    - 永続化(DB / JSON / file)
    - Memoryへの書き込み
    - AI/LLM呼び出し
    - Orchestra連携
    - Workflow制御

  許可:
    - インメモリ管理のみ
    - PHI-OSからの参照
    - Contextの集約
"""

from datetime import datetime, timezone

from .relay_session import RelaySession


class SessionRelay:
    """セッション単位の時間的文脈を管理する(インメモリのみ)。"""

    def __init__(self):
        self._sessions: dict[str, RelaySession] = {}

    # ------------------------------------------------------------------
    # 公開API
    # ------------------------------------------------------------------

    def create_session(self, session_id: str) -> dict:
        """セッションを作成する。既に存在する場合は既存のものを返す。"""
        if session_id not in self._sessions:
            self._sessions[session_id] = RelaySession(session_id=session_id)
        return self._sessions[session_id].to_dict()

    def append_context(self, session_id: str, context, timestamp: str = None) -> dict:
        """セッションにContextを追加する。

        セッションが存在しない場合は自動的に作成する(参照のみであり、
        外部への書き込みや制御は発生しない)。
        """
        if session_id not in self._sessions:
            self.create_session(session_id)

        self._sessions[session_id].append_context(context, timestamp=timestamp)
        return self._sessions[session_id].to_dict()

    def get_session(self, session_id: str):
        """セッションのスナップショット(dict)を返す。存在しない場合はNone。"""
        session = self._sessions.get(session_id)
        return session.to_dict() if session is not None else None

    def merge_sessions(self, session_a: str, session_b: str, merged_session_id: str = None) -> dict:
        """2つのセッションを統合した新しいセッションを作成する。

        event_ids/context_chain/timestampsを時系列順に結合する。
        元のセッションは変更しない。
        """
        a = self._sessions.get(session_a)
        b = self._sessions.get(session_b)

        merged_id = merged_session_id or f"{session_a}+{session_b}"
        merged = RelaySession(session_id=merged_id)

        for session in (a, b):
            if session is None:
                continue
            for event_id in session.event_ids:
                if event_id not in merged.event_ids:
                    merged.event_ids.append(event_id)
            merged.context_chain.extend(session.context_chain)
            merged.timestamps.extend(session.timestamps)

        merged.metadata = {
            "merged_from": [session_a, session_b],
            "merged_at": datetime.now(timezone.utc).isoformat(),
        }

        self._sessions[merged_id] = merged
        return merged.to_dict()

    # ------------------------------------------------------------------
    # 補助
    # ------------------------------------------------------------------

    def list_sessions(self) -> list:
        """既知のsession_idの一覧を返す。"""
        return list(self._sessions.keys())

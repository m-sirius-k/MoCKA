# phi_os/phi_bridge_governance.py
# PHI-OS 統治層 v1 — ConflictEvent → Decision パイプライン
#
# 責務:
#   Bridge から流れてくる ConflictEvent を受け取り、
#   Severity に基づいて OBSERVE / TAG / ROUTE の3分岐 Decision を生成する。
#
# 絶対制約:
#   - 意味の変更・統合は禁止
#   - merge 禁止 / overwrite 禁止
#   - Decision はログのみ保持（副作用なし）

from __future__ import annotations
import datetime
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────────────────────────
# ConflictEvent — Bridge から PHI-OS 統治層へ流れる入力単位
# ─────────────────────────────────────────────────────────────

@dataclass
class ConflictEvent:
    term: str
    phi_os_meaning: Optional[str]
    personal_meaning: Optional[str]
    conflict_state: str          # BridgeRecord.state の値文字列
    conflict_reason: str
    severity: float              # 0.0–1.0 (外部が算出して注入する)
    event_id: str = field(
        default_factory=lambda: f"CE_{uuid.uuid4().hex[:10]}"
    )
    occurred_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


# ─────────────────────────────────────────────────────────────
# DecisionKind — 統治層の分岐結果
# ─────────────────────────────────────────────────────────────

class DecisionKind(str, Enum):
    OBSERVE = "OBSERVE"   # 低 (severity < 0.3): 記録して監視のみ
    TAG     = "TAG"       # 中 (0.3 <= severity < 0.7): タグ付けして保留
    ROUTE   = "ROUTE"     # 高 (severity >= 0.7): 上位層へルーティング


# ─────────────────────────────────────────────────────────────
# Decision — 統治層が生成する判断ログ
# ─────────────────────────────────────────────────────────────

@dataclass
class Decision:
    event_id: str
    term: str
    severity: float
    kind: DecisionKind
    note: str
    decided_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return {
            "event_id":   self.event_id,
            "term":       self.term,
            "severity":   self.severity,
            "kind":       self.kind.value,
            "note":       self.note,
            "decided_at": self.decided_at,
        }


# ─────────────────────────────────────────────────────────────
# Severity 閾値
# ─────────────────────────────────────────────────────────────

SEVERITY_OBSERVE_MAX = 0.3
SEVERITY_TAG_MAX     = 0.7
# >= SEVERITY_TAG_MAX → ROUTE


# ─────────────────────────────────────────────────────────────
# PhiBridgeGovernance
# ─────────────────────────────────────────────────────────────

class PhiBridgeGovernance:
    """
    ConflictEvent を受け取り、Severity ベースの3分岐 Decision を生成する。

    生成した Decision はインメモリログに保持するのみ。
    意味の書き換え・統合・自動解決は一切行わない。
    """

    def __init__(self):
        self._log: list[Decision] = []

    # ── メイン処理 ────────────────────────────────────────────

    def process(self, event: ConflictEvent) -> Decision:
        """
        ConflictEvent → Decision 変換。
        Severity に基づいて OBSERVE / TAG / ROUTE を決定し、ログに追記する。
        """
        kind, note = self._route(event)
        decision = Decision(
            event_id=event.event_id,
            term=event.term,
            severity=event.severity,
            kind=kind,
            note=note,
        )
        self._log.append(decision)
        return decision

    def _route(self, event: ConflictEvent) -> tuple[DecisionKind, str]:
        """Severity ベース3分岐。意味には一切触れない。"""
        s = event.severity
        state = event.conflict_state

        if s < SEVERITY_OBSERVE_MAX:
            return (
                DecisionKind.OBSERVE,
                f"severity={s:.3f} — 低強度衝突。記録して監視継続。state={state}",
            )
        if s < SEVERITY_TAG_MAX:
            return (
                DecisionKind.TAG,
                f"severity={s:.3f} — 中強度衝突。タグ付けして保留。state={state} / reason={event.conflict_reason}",
            )
        return (
            DecisionKind.ROUTE,
            f"severity={s:.3f} — 高強度衝突。上位層へルーティング。state={state} / reason={event.conflict_reason}",
        )

    # ── ログ参照 ──────────────────────────────────────────────

    def decisions(self) -> list[Decision]:
        """全 Decision ログを返す（コピー）。"""
        return list(self._log)

    def decisions_for(self, term: str) -> list[Decision]:
        return [d for d in self._log if d.term == term]

    def decisions_by_kind(self, kind: DecisionKind) -> list[Decision]:
        return [d for d in self._log if d.kind == kind]

    def clear_log(self) -> None:
        """ログをリセットする（テスト用途向け）。意味には触れない。"""
        self._log.clear()


# ─────────────────────────────────────────────────────────────
# ユーティリティ: BridgeRecord → ConflictEvent 変換ヘルパー
# ─────────────────────────────────────────────────────────────

def severity_from_state(conflict_state: str) -> float:
    """
    BridgeRecord の state 文字列から severity を算出するデフォルト実装。
    呼び出し元は独自の severity 計算でオーバーライドしてよい。
    """
    mapping = {
        "NORMAL":   0.0,
        "DRIFT":    0.5,
        "CONFLICT": 0.9,
        "LOCKED":   0.1,  # ロックは管理対象外として低強度扱い
    }
    return mapping.get(conflict_state.upper(), 0.5)


def event_from_bridge_record(record) -> ConflictEvent:
    """
    BridgeRecord (bridge.conflict_types.BridgeRecord) を
    ConflictEvent に変換する便利関数。
    severity は state から自動算出する。
    """
    state_str = record.state.value if hasattr(record.state, "value") else str(record.state)
    return ConflictEvent(
        term=record.term,
        phi_os_meaning=record.phi_os_meaning,
        personal_meaning=record.personal_meaning,
        conflict_state=state_str,
        conflict_reason=record.conflict_reason,
        severity=severity_from_state(state_str),
    )

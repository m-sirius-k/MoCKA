# phi_os/runtime/authority_manager.py
# Institution Runtime — Authority管理
# 参照: PHI_OS_CONSTITUTION_v1.md 第3章 Authority体系
from typing import Optional

from .runtime_types import Authority, AuthorityType, GateId
from .runtime_errors import AuthorityConflictError


# Constitution 3.1 に基づく正規Authority割当
_CANONICAL_AUTHORITY: dict[AuthorityType, Authority] = {
    AuthorityType.GATE: Authority(
        authority_type=AuthorityType.GATE,
        holder="PHI-OS",
    ),
    AuthorityType.EVENT: Authority(
        authority_type=AuthorityType.EVENT,
        holder="PHI-OS / Event Gate",
    ),
    AuthorityType.KNOWLEDGE: Authority(
        authority_type=AuthorityType.KNOWLEDGE,
        holder="PHI-OS / Knowledge Gate",
    ),
    AuthorityType.VERSION: Authority(
        authority_type=AuthorityType.VERSION,
        holder="PHI-OS / Release Gate",
    ),
    AuthorityType.VERIFICATION: Authority(
        authority_type=AuthorityType.VERIFICATION,
        holder="PHI-OS / Compliance Runtime",
    ),
    AuthorityType.INSTITUTION: Authority(
        authority_type=AuthorityType.INSTITUTION,
        holder="PHI-OS",
    ),
}

# Constitution 4.1 Gate→Authority 対応表 (GATE_ARCHITECTURE_v1.md 4.1)
_GATE_AUTHORITY_MAP: dict[GateId, AuthorityType] = {
    GateId.EVENT:      AuthorityType.EVENT,
    GateId.KNOWLEDGE:  AuthorityType.KNOWLEDGE,
    GateId.MODULE:     AuthorityType.INSTITUTION,
    GateId.PROMPT:     AuthorityType.GATE,
    GateId.RELEASE:    AuthorityType.VERSION,
    GateId.EXPERIMENT: AuthorityType.GATE,
    GateId.DOCUMENT:   AuthorityType.GATE,
}

# Constitution 3.3 Authority継承ツリー (上位→下位)
_AUTHORITY_HIERARCHY: dict[AuthorityType, list[AuthorityType]] = {
    AuthorityType.GATE: [
        AuthorityType.INSTITUTION,
        AuthorityType.EVENT,
        AuthorityType.KNOWLEDGE,
        AuthorityType.VERSION,
        AuthorityType.VERIFICATION,
    ],
    AuthorityType.INSTITUTION: [],
    AuthorityType.EVENT: [],
    AuthorityType.KNOWLEDGE: [],
    AuthorityType.VERSION: [],
    AuthorityType.VERIFICATION: [],
}


class AuthorityManager:
    """
    Authority検索・一意性確認・競合検知・継承管理。
    Constitution原則: 同一制度行為にAuthorityが重複してはならない (3.2)。
    """

    def __init__(self) -> None:
        self._store: dict[AuthorityType, Authority] = dict(_CANONICAL_AUTHORITY)
        self._delegations: dict[AuthorityType, list[tuple[str, str]]] = {}

    # ── 検索 ─────────────────────────────────────────────────────────────────

    def get(self, authority_type: AuthorityType) -> Authority:
        return self._store[authority_type]

    def get_for_gate(self, gate_id: GateId) -> Authority:
        at = _GATE_AUTHORITY_MAP[gate_id]
        return self._store[at]

    def all_authorities(self) -> list[Authority]:
        return list(self._store.values())

    # ── 一意性確認 ───────────────────────────────────────────────────────────

    def assert_unique(self, authority_type: AuthorityType, claimant: str) -> None:
        """
        claimantが既存holderと異なる場合、AuthorityConflictErrorを送出する。
        Constitution 3.2: Authority一意性原則。
        """
        current = self._store[authority_type]
        effective_holder = current.delegated_to or current.holder
        if effective_holder != claimant and claimant != current.holder:
            raise AuthorityConflictError(authority_type.value, effective_holder, claimant)

    # ── 競合検知 ─────────────────────────────────────────────────────────────

    def detect_conflicts(self) -> list[dict]:
        """
        複数のAuthorityが同一行為に重複しているかを検査する。
        現在の委譲状態を含めて評価する。
        """
        conflicts: list[dict] = []
        seen_holders: dict[str, list[AuthorityType]] = {}
        for at, auth in self._store.items():
            holder = auth.delegated_to or auth.holder
            seen_holders.setdefault(holder, []).append(at)
        for holder, types in seen_holders.items():
            if len(types) > 1:
                # Gate Authorityが複数Authorityを保持するのは正規 (Constitution 3.3)
                non_gate = [t for t in types if t != AuthorityType.GATE]
                if len(non_gate) > 1:
                    conflicts.append({
                        "holder": holder,
                        "authority_types": [t.value for t in non_gate],
                        "reason": "同一主体が複数の非GATE Authorityを保持",
                    })
        return conflicts

    # ── 委譲管理 (Constitution 3.2: 委譲は記録を伴う場合のみ有効) ──────────

    def delegate(
        self,
        authority_type: AuthorityType,
        to: str,
        delegation_event_id: str,
    ) -> None:
        auth = self._store[authority_type]
        # GATE/EVENT Authorityは委譲不可 (GATE_ARCHITECTURE_v1.md 4.1)
        if authority_type in (AuthorityType.GATE, AuthorityType.EVENT):
            raise AuthorityConflictError(
                authority_type.value, auth.holder, to,
            )
        auth.delegated_to = to
        auth.delegation_event_id = delegation_event_id
        self._delegations.setdefault(authority_type, []).append(
            (to, delegation_event_id)
        )

    def revoke_delegation(self, authority_type: AuthorityType) -> None:
        auth = self._store[authority_type]
        auth.delegated_to = None
        auth.delegation_event_id = None

    # ── 継承 ─────────────────────────────────────────────────────────────────

    def subordinates(self, authority_type: AuthorityType) -> list[AuthorityType]:
        """上位Authorityに帰属する下位Authority一覧を返す。"""
        return _AUTHORITY_HIERARCHY.get(authority_type, [])

    def can_override(self, superior: AuthorityType, inferior: AuthorityType) -> bool:
        """superiorがinferiorを停止・審査できるかを返す。"""
        return inferior in _AUTHORITY_HIERARCHY.get(superior, [])

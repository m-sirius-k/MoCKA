# phi_os/runtime/gate_registry.py
# Institution Runtime — Gate管理
# 参照: GATE_ARCHITECTURE_v1.md 第1〜2章
from .runtime_types import Gate, GateId, GateStatus, AuthorityType, MeaningClass
from .runtime_errors import GateValidationError


# GATE_ARCHITECTURE_v1.md 第1章 Gate一覧の正規定義
_CANONICAL_GATES: list[Gate] = [
    Gate(
        gate_id=GateId.EVENT,
        name="Event Gate",
        authority_type=AuthorityType.EVENT,
        status=GateStatus.ACTIVE,
        required_meanings=[],  # 全Meaningのイベントを受け付ける
        description="MoCKA制度における事実の唯一の受け付け口",
    ),
    Gate(
        gate_id=GateId.KNOWLEDGE,
        name="Knowledge Gate",
        authority_type=AuthorityType.KNOWLEDGE,
        status=GateStatus.ACTIVE,
        required_meanings=[
            MeaningClass.KNOWLEDGE,
            MeaningClass.DESIGN,
            MeaningClass.PHASE_RECORD,
            MeaningClass.REQUIREMENT,
        ],
        description="知識Artifactの制度的登録・参照・版管理・廃止",
    ),
    Gate(
        gate_id=GateId.MODULE,
        name="Module Gate",
        authority_type=AuthorityType.INSTITUTION,
        status=GateStatus.ACTIVE,
        required_meanings=[MeaningClass.SYSTEM_CORE],
        description="システムモジュールの本番稼働への制度的な受け付け口",
    ),
    Gate(
        gate_id=GateId.PROMPT,
        name="Prompt Gate",
        authority_type=AuthorityType.GATE,
        status=GateStatus.DEFINED,
        required_meanings=[MeaningClass.GOVERNANCE],
        description="AIへの指示書・プロンプト・CLAUDE.mdの制度的検証と発行",
    ),
    Gate(
        gate_id=GateId.RELEASE,
        name="Release Gate",
        authority_type=AuthorityType.VERSION,
        status=GateStatus.ACTIVE,
        required_meanings=[],
        description="外部公開・配布物の制度的検査と承認",
    ),
    Gate(
        gate_id=GateId.EXPERIMENT,
        name="Experiment Gate",
        authority_type=AuthorityType.GATE,
        status=GateStatus.ACTIVE,
        required_meanings=[],
        description="実験・試験的Artifactの制度的管理",
    ),
    Gate(
        gate_id=GateId.DOCUMENT,
        name="Document Gate",
        authority_type=AuthorityType.GATE,
        status=GateStatus.ACTIVE,
        required_meanings=[
            MeaningClass.GOVERNANCE,
            MeaningClass.DESIGN,
            MeaningClass.REQUIREMENT,
            MeaningClass.PHASE_RECORD,
        ],
        description="制度文書・設計文書・ガバナンス文書の制度的登録・版管理・廃止",
    ),
]

# Gate遷移許可テーブル (GATE_ARCHITECTURE_v1.md 3.1)
_VALID_TRANSITIONS: dict[GateId, list[GateId]] = {
    GateId.DOCUMENT:   [GateId.KNOWLEDGE, GateId.MODULE, GateId.EXPERIMENT, GateId.RELEASE, GateId.EVENT],
    GateId.KNOWLEDGE:  [GateId.RELEASE, GateId.EVENT],
    GateId.MODULE:     [GateId.RELEASE, GateId.EVENT],
    GateId.EXPERIMENT: [GateId.MODULE, GateId.EVENT],
    GateId.RELEASE:    [GateId.EVENT],
    GateId.PROMPT:     [GateId.DOCUMENT, GateId.MODULE, GateId.EVENT],
    GateId.EVENT:      [],  # 終端
}


class GateRegistry:
    """
    Gate登録・検索・能力取得・遷移検証。
    GATE_ARCHITECTURE_v1.md に定義された7 Gateを管理する。
    """

    def __init__(self) -> None:
        self._store: dict[GateId, Gate] = {}
        for gate in _CANONICAL_GATES:
            self._store[gate.gate_id] = gate

    # ── 登録 ─────────────────────────────────────────────────────────────────

    def register(self, gate: Gate) -> None:
        self._store[gate.gate_id] = gate

    # ── 検索 ─────────────────────────────────────────────────────────────────

    def get(self, gate_id: GateId) -> Gate:
        if gate_id not in self._store:
            raise GateValidationError(gate_id.value, [f"Gate {gate_id.value} 未登録"])
        return self._store[gate_id]

    def all_gates(self) -> list[Gate]:
        return list(self._store.values())

    def active_gates(self) -> list[Gate]:
        return [g for g in self._store.values() if g.status == GateStatus.ACTIVE]

    # ── 能力取得 ─────────────────────────────────────────────────────────────

    def get_capabilities(self, gate_id: GateId) -> dict:
        gate = self.get(gate_id)
        return {
            "gate_id": gate.gate_id.value,
            "name": gate.name,
            "status": gate.status.value,
            "authority": gate.authority_type.value,
            "required_meanings": [m.value for m in gate.required_meanings],
            "valid_next_gates": [g.value for g in _VALID_TRANSITIONS.get(gate_id, [])],
            "description": gate.description,
        }

    # ── 遷移検証 ─────────────────────────────────────────────────────────────

    def validate_transition(self, from_gate: GateId, to_gate: GateId) -> tuple[bool, list[str]]:
        """
        Gate間遷移が制度上正規かを検証する。
        GATE_ARCHITECTURE_v1.md 3.1 標準制度接続フロー準拠。
        """
        issues: list[str] = []
        allowed = _VALID_TRANSITIONS.get(from_gate, [])
        if to_gate not in allowed:
            issues.append(
                f"{from_gate.value} → {to_gate.value} 遷移は非正規 "
                f"(許可: {[g.value for g in allowed]})"
            )
        to = self._store.get(to_gate)
        if to and to.status == GateStatus.PLANNED:
            issues.append(f"{to_gate.value} は PLANNED 状態で未実装")
        return len(issues) == 0, issues

    def validate_meaning_for_gate(
        self, gate_id: GateId, meaning_class: MeaningClass
    ) -> tuple[bool, list[str]]:
        """GateがそのMeaningClassのArtifactを受け付けられるかを検証する。"""
        gate = self.get(gate_id)
        issues: list[str] = []
        if gate.required_meanings and meaning_class not in gate.required_meanings:
            issues.append(
                f"{gate_id.value} は {meaning_class.value} を受け付けない "
                f"(許可: {[m.value for m in gate.required_meanings]})"
            )
        return len(issues) == 0, issues

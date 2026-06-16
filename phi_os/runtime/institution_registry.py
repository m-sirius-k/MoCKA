# phi_os/runtime/institution_registry.py
# Institution Runtime — Institution管理
# 参照: PHI_OS_CONSTITUTION_v1.md 原則7 / INSTITUTION_BINDING_MAP_v1.md
from .runtime_types import Institution, GateId
from .runtime_errors import InstitutionResolutionError


# INSTITUTION_BINDING_MAP_v1.md Institution定義を初期値として登録
_DEFAULT_INSTITUTIONS: list[Institution] = [
    Institution(
        institution_id="PHI-OS",
        name="PHI-OS",
        description="制度OS。Event Gate・Knowledge Gate・Module Gateの制度権威",
        primary_gate=GateId.EVENT,
        secondary_gates=[GateId.KNOWLEDGE, GateId.MODULE, GateId.DOCUMENT, GateId.EXPERIMENT],
    ),
    Institution(
        institution_id="MoCKA",
        name="MoCKA",
        description="中核制度機関。全Artifactの制度登録・ガバナンス主体",
        primary_gate=GateId.DOCUMENT,
        secondary_gates=[GateId.EVENT, GateId.RELEASE],
    ),
    Institution(
        institution_id="Orchestra",
        name="Orchestra",
        description="イベント実行・セッション管理・タイムライン機関",
        primary_gate=GateId.EVENT,
        secondary_gates=[GateId.MODULE],
    ),
    Institution(
        institution_id="Relay",
        name="Relay",
        description="セッション間引き継ぎ・外部インターフェース機関",
        primary_gate=GateId.MODULE,
        secondary_gates=[],
    ),
    Institution(
        institution_id="Memory",
        name="Memory",
        description="知識保全・記憶管理機関",
        primary_gate=GateId.KNOWLEDGE,
        secondary_gates=[],
    ),
    Institution(
        institution_id="vasAI",
        name="vasAI",
        description="自律エージェント実験機関",
        primary_gate=GateId.EXPERIMENT,
        secondary_gates=[],
    ),
    Institution(
        institution_id="mini-MoCKA",
        name="mini-MoCKA",
        description="MoCKA縮小実験機関",
        primary_gate=GateId.EXPERIMENT,
        secondary_gates=[],
    ),
    Institution(
        institution_id="共通制度",
        name="共通制度",
        description="公開・外部向け制度。複数Institutionが共有",
        primary_gate=GateId.RELEASE,
        secondary_gates=[GateId.DOCUMENT],
    ),
]


class InstitutionRegistry:
    """
    Institutionの登録・検索・責任範囲取得・所属判定。
    Constitution原則7: すべてのArtifactは単一の主Institutionに帰属する。
    """

    def __init__(self) -> None:
        self._store: dict[str, Institution] = {}
        for inst in _DEFAULT_INSTITUTIONS:
            self._store[inst.institution_id] = inst

    # ── 登録 ─────────────────────────────────────────────────────────────────

    def register(self, institution: Institution) -> None:
        self._store[institution.institution_id] = institution

    # ── 検索 ─────────────────────────────────────────────────────────────────

    def get(self, institution_id: str) -> Institution:
        if institution_id not in self._store:
            raise InstitutionResolutionError(institution_id, "未登録Institution")
        return self._store[institution_id]

    def exists(self, institution_id: str) -> bool:
        return institution_id in self._store

    def all_institutions(self) -> list[Institution]:
        return list(self._store.values())

    # ── 責任範囲取得 ─────────────────────────────────────────────────────────

    def get_scope(self, institution_id: str) -> dict:
        """InstitutionのGate責任範囲を返す。"""
        inst = self.get(institution_id)
        return {
            "institution_id": inst.institution_id,
            "primary_gate": inst.primary_gate.value,
            "secondary_gates": [g.value for g in inst.secondary_gates],
            "artifact_count": len(inst.artifact_ids),
        }

    # ── 所属判定 ─────────────────────────────────────────────────────────────

    def is_member(self, artifact_id: str, institution_id: str) -> bool:
        """ArtifactがInstitutionに帰属しているかを返す。"""
        if not self.exists(institution_id):
            return False
        return artifact_id in self._store[institution_id].artifact_ids

    def register_artifact(self, artifact_id: str, institution_id: str) -> None:
        """ArtifactをInstitutionに帰属登録する。"""
        inst = self.get(institution_id)
        if artifact_id not in inst.artifact_ids:
            inst.artifact_ids.append(artifact_id)

    def find_institution_of(self, artifact_id: str) -> str | None:
        """ArtifactのInstitutionを逆引きする。なければNone。"""
        for inst in self._store.values():
            if artifact_id in inst.artifact_ids:
                return inst.institution_id
        return None

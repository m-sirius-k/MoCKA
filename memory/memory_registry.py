"""
MoCKA 3.0 — Memory Layer
memory_registry.py

責務:
  記憶分類ルールを一元管理する。

  - memory_type定義(4種類の記憶)
  - タグ体系
  - 優先度ルール
  - 保存ポリシー

  Memory Store / Writer / Retriever / Index はこのRegistryを参照するのみで、
  分類名・優先度・保存上限をコード中に直接埋め込まない。
"""

from dataclasses import dataclass, field


class MemoryType:
    """4種類の記憶分類(memory_typeに格納される値)。"""

    EPISODIC = "episodic"      # エピソード記憶: 過去の意思決定/実行履歴/会話・イベント履歴
    SEMANTIC = "semantic"      # 意味記憶: 概念・定義・Registry情報・固定知識
    PROCEDURAL = "procedural"  # 手続き記憶: 実行フロー/Pipeline構造/Decisionルール
    SKILL = "skill"            # 技能記憶: 最適化された処理パターン/成功パターン/再利用可能な構造

    ALL = (EPISODIC, SEMANTIC, PROCEDURAL, SKILL)


class Source:
    """MemoryEntry.sourceに格納される値(記憶の発生元)。"""

    SEMANTIC_LAYER = "Semantic"
    DECISION_LAYER = "Decision"
    GOVERNANCE_LAYER = "Governance"
    EXTERNAL = "External"

    ALL = (SEMANTIC_LAYER, DECISION_LAYER, GOVERNANCE_LAYER, EXTERNAL)


@dataclass(frozen=True)
class RetentionPolicy:
    """memory_type別の保存ポリシー。"""

    memory_type: str
    max_entries: int       # Memory Storeに保持する最大件数(超過分は古いものから除外)
    default_priority: float  # 0-1。Retrieverのrelevance_score算出時の基礎重み
    default_tags: tuple = field(default_factory=tuple)


# memory_type別の保存ポリシー(優先度ルール・保存ポリシー)
RETENTION_POLICIES = {
    MemoryType.EPISODIC: RetentionPolicy(
        memory_type=MemoryType.EPISODIC,
        max_entries=500,
        default_priority=0.6,
        default_tags=("episodic", "history"),
    ),
    MemoryType.SEMANTIC: RetentionPolicy(
        memory_type=MemoryType.SEMANTIC,
        max_entries=200,
        default_priority=0.5,
        default_tags=("semantic", "concept"),
    ),
    MemoryType.PROCEDURAL: RetentionPolicy(
        memory_type=MemoryType.PROCEDURAL,
        max_entries=100,
        default_priority=0.55,
        default_tags=("procedural", "pipeline"),
    ),
    MemoryType.SKILL: RetentionPolicy(
        memory_type=MemoryType.SKILL,
        max_entries=100,
        default_priority=0.7,
        default_tags=("skill", "pattern"),
    ),
}


def get_retention_policy(memory_type: str) -> RetentionPolicy:
    """memory_typeに対応するRetentionPolicyを取得する。未知の場合はEPISODICを既定とする。"""
    return RETENTION_POLICIES.get(memory_type, RETENTION_POLICIES[MemoryType.EPISODIC])


def all_memory_types() -> tuple:
    return MemoryType.ALL

"""
MoCKA 3.0 — Semantic Layer
semantic_registry.py

責務:
  Semantic Layerが扱う「意味カテゴリ(Intent)」を一元管理する。

  Intent Classifier / Semantic Pipeline はこのRegistryを参照するのみで、
  分類名やキーワードをコード中に直接埋め込まない。

  新しいIntentを追加する場合、INTENT_REGISTRY に1エントリを
  追加するだけで Classifier / Pipeline / Result すべてに反映される。

注意:
  Semantic LayerはGovernance Layer(GL1-7)とは独立した層であり、
  安全性・実行可否・品質保証の判断は一切行わない。
  本Registryが提供する recommended_action は「判断支援のための提案」
  であり、実行はGovernance Layerの管轄である。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class IntentDefinition:
    """1つの意味カテゴリ(Intent)の定義。"""

    key: str                 # 内部識別子 (英語スネークケース)
    label_ja: str            # 表示名(日本語)
    label_en: str            # 表示名(英語)
    keywords: tuple          # 単語境界マッチに使うキーワード群(日英混在)
    recommended_action: str  # この意味カテゴリで推奨されるアクション(提案)
    related_topics: tuple = field(default_factory=tuple)  # 関連トピックのヒント


# Intentの優先順位は登場順とする(複数キーワードが一致した場合の
# tie-break、および INTENT_REGISTRY のイテレーション順に使われる)。
INTENT_REGISTRY = (
    IntentDefinition(
        key="information_retrieval",
        label_ja="情報取得",
        label_en="Information Retrieval",
        keywords=(
            "教えて", "確認", "見せて", "what is", "show", "get", "fetch",
            "list", "一覧", "状況", "status",
        ),
        recommended_action="関連情報を取得して提示する",
        related_topics=("overview", "status", "search"),
    ),
    IntentDefinition(
        key="design",
        label_ja="設計",
        label_en="Design",
        keywords=(
            "設計", "design", "architecture", "アーキテクチャ", "構造",
            "structure", "schema", "スキーマ",
        ),
        recommended_action="設計案を提示し、トレードオフを整理する",
        related_topics=("architecture", "schema", "structure"),
    ),
    IntentDefinition(
        key="implementation",
        label_ja="実装",
        label_en="Implementation",
        keywords=(
            "実装", "implement", "作成", "create", "新規", "add", "追加",
            "build", "実装して",
        ),
        recommended_action="実装方針を整理し、必要なファイルを作成・編集する",
        related_topics=("code", "feature", "module"),
    ),
    IntentDefinition(
        key="fix",
        label_ja="修正",
        label_en="Fix",
        keywords=(
            "修正", "fix", "バグ", "bug", "直して", "エラー", "error",
            "不具合", "patch",
        ),
        recommended_action="原因を特定し、最小限の修正を適用する",
        related_topics=("bugfix", "error", "patch"),
    ),
    IntentDefinition(
        key="audit",
        label_ja="監査",
        label_en="Audit",
        keywords=(
            "監査", "audit", "コンプライアンス", "compliance", "規約",
            "policy",
        ),
        recommended_action="対象を監査し、結果を報告書として記録する",
        related_topics=("governance", "policy", "report"),
    ),
    IntentDefinition(
        key="verification",
        label_ja="検証",
        label_en="Verification",
        keywords=(
            "検証", "verify", "verification", "確認して", "テスト", "test",
            "動作確認", "regression",
        ),
        recommended_action="テスト・検証を実行し、結果を確認する",
        related_topics=("test", "regression", "verification"),
    ),
    IntentDefinition(
        key="record",
        label_ja="記録",
        label_en="Record",
        keywords=(
            "記録", "record", "ログ", "log", "event", "イベント", "保存",
            "save",
        ),
        recommended_action="作業内容をEvent/Logとして記録する",
        related_topics=("event", "log", "history"),
    ),
    IntentDefinition(
        key="comparison",
        label_ja="比較",
        label_en="Comparison",
        keywords=(
            "比較", "compare", "comparison", "差分", "diff", "vs",
            "どちらが",
        ),
        recommended_action="対象同士を比較し、差異を整理する",
        related_topics=("diff", "comparison", "tradeoff"),
    ),
    IntentDefinition(
        key="summary",
        label_ja="要約",
        label_en="Summary",
        keywords=(
            "要約", "summary", "summarize", "まとめ", "まとめて", "tl;dr",
            "概要",
        ),
        recommended_action="対象の内容を要約して提示する",
        related_topics=("summary", "overview", "digest"),
    ),
    IntentDefinition(
        key="planning",
        label_ja="計画",
        label_en="Planning",
        keywords=(
            "計画", "plan", "planning", "ロードマップ", "roadmap",
            "スケジュール", "schedule", "次のフェーズ", "next phase",
        ),
        recommended_action="作業計画を整理し、フェーズ・優先順位を提示する",
        related_topics=("roadmap", "schedule", "phase"),
    ),
)


# key -> IntentDefinition の参照用インデックス
INTENT_BY_KEY = {definition.key: definition for definition in INTENT_REGISTRY}

# 既知のIntentに該当しない場合に使うフォールバック
UNKNOWN_INTENT = IntentDefinition(
    key="unknown",
    label_ja="不明",
    label_en="Unknown",
    keywords=(),
    recommended_action="意図を明確化するため、利用者に追加情報を確認する",
    related_topics=(),
)


def get_intent(key: str) -> IntentDefinition:
    """キーからIntentDefinitionを取得する。未知のキーはUNKNOWN_INTENTを返す。"""
    return INTENT_BY_KEY.get(key, UNKNOWN_INTENT)


def all_intent_keys() -> tuple:
    """登録済みIntentキーの一覧(登録順)を返す。"""
    return tuple(definition.key for definition in INTENT_REGISTRY)

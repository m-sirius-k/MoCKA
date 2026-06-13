"""
MoCKA 3.0 — Decision Layer
decision_registry.py

責務:
  Intentごとの「デフォルト行動マッピング」「評価重み」を一元管理する。

  Priority Scorer / Risk Analyzer / Decision Engine はこのRegistryを
  参照するのみで、Intentごとの重み・既定行動をコード中に直接埋め込まない。

  新しいIntent(Semantic Registry側)に対応する場合、
  DECISION_REGISTRY に1エントリを追加するだけで反映される。

注意:
  Decision LayerはGovernance Layer(GL1-7)の判断を代替しない。
  ここで定義する重み・既定行動は「中間意思決定の材料」であり、
  最終的な実行可否はGovernance Layerに委ねる。
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionProfile:
    """1つのIntentに対する意思決定プロファイル。"""

    intent_key: str            # semantic_registry の IntentDefinition.key と対応
    action_profile: str        # "read_heavy" | "write_heavy" | "verification_first" | "analysis_heavy"
    default_action: str        # 推奨アクション(雛形文字列)
    alternative_actions: tuple # 代替アクション(雛形文字列)
    priority_weight: float     # Intent重要度 (0-1)
    base_risk: float           # 基礎リスク (0-1) — action_profileに基づく副作用リスクの目安
    risk_factors: tuple = field(default_factory=tuple)  # 既知のリスク要因(説明文)


# action_profile別の既定リスク要因(risk_analyzerが追加要因と合成する)
_DEFAULT_RISK_FACTORS = {
    "read_heavy": ("読み取り専用のため副作用リスクは低い",),
    "write_heavy": (
        "ファイル/状態の変更を伴うため副作用リスクが高い",
        "Governance Layer (GL7 Default Deny) によるDry Run対象",
    ),
    "verification_first": ("検証結果次第で追加対応が必要になる可能性がある",),
    "analysis_heavy": ("分析結果の解釈に主観が入る可能性がある",),
}


DECISION_REGISTRY = (
    DecisionProfile(
        intent_key="information_retrieval",
        action_profile="read_heavy",
        default_action="関連情報を取得して提示する",
        alternative_actions=("関連トピックを横断検索する", "要約して提示する"),
        priority_weight=0.5,
        base_risk=0.1,
        risk_factors=_DEFAULT_RISK_FACTORS["read_heavy"],
    ),
    DecisionProfile(
        intent_key="design",
        action_profile="analysis_heavy",
        default_action="設計案とトレードオフを整理して提示する",
        alternative_actions=("既存アーキテクチャ文書を確認する", "比較表を作成する"),
        priority_weight=0.6,
        base_risk=0.2,
        risk_factors=_DEFAULT_RISK_FACTORS["analysis_heavy"],
    ),
    DecisionProfile(
        intent_key="implementation",
        action_profile="write_heavy",
        default_action="実装方針を整理し、対象ファイルを作成・編集する",
        alternative_actions=("設計を先に確認する", "テストケースを先に作成する"),
        priority_weight=0.8,
        base_risk=0.7,
        risk_factors=_DEFAULT_RISK_FACTORS["write_heavy"],
    ),
    DecisionProfile(
        intent_key="fix",
        action_profile="write_heavy",
        default_action="原因を特定し、最小限の修正を適用する",
        alternative_actions=("再現手順を確認する", "影響範囲を調査する"),
        priority_weight=0.85,
        base_risk=0.65,
        risk_factors=_DEFAULT_RISK_FACTORS["write_heavy"],
    ),
    DecisionProfile(
        intent_key="audit",
        action_profile="verification_first",
        default_action="対象を監査し、結果を報告書として記録する",
        alternative_actions=("Regressionを再実行する", "既存の監査報告書を確認する"),
        priority_weight=0.7,
        base_risk=0.3,
        risk_factors=_DEFAULT_RISK_FACTORS["verification_first"],
    ),
    DecisionProfile(
        intent_key="verification",
        action_profile="verification_first",
        default_action="テスト・検証を実行し、結果を確認する",
        alternative_actions=("Regressionを再実行する", "影響範囲のテストを追加する"),
        priority_weight=0.65,
        base_risk=0.25,
        risk_factors=_DEFAULT_RISK_FACTORS["verification_first"],
    ),
    DecisionProfile(
        intent_key="record",
        action_profile="write_heavy",
        default_action="作業内容をEvent/Logとして記録する",
        alternative_actions=("関連Eventを検索してから記録する",),
        priority_weight=0.4,
        base_risk=0.35,
        risk_factors=_DEFAULT_RISK_FACTORS["write_heavy"],
    ),
    DecisionProfile(
        intent_key="comparison",
        action_profile="analysis_heavy",
        default_action="対象同士を比較し、差異を整理する",
        alternative_actions=("差分を要約する", "比較表を作成する"),
        priority_weight=0.5,
        base_risk=0.15,
        risk_factors=_DEFAULT_RISK_FACTORS["analysis_heavy"],
    ),
    DecisionProfile(
        intent_key="summary",
        action_profile="read_heavy",
        default_action="対象の内容を要約して提示する",
        alternative_actions=("詳細情報を取得してから要約する",),
        priority_weight=0.45,
        base_risk=0.1,
        risk_factors=_DEFAULT_RISK_FACTORS["read_heavy"],
    ),
    DecisionProfile(
        intent_key="planning",
        action_profile="analysis_heavy",
        default_action="作業計画を整理し、フェーズ・優先順位を提示する",
        alternative_actions=("現状のTODO/Eventを確認する", "リスクの高い項目を先に検討する"),
        priority_weight=0.55,
        base_risk=0.2,
        risk_factors=_DEFAULT_RISK_FACTORS["analysis_heavy"],
    ),
)


DECISION_REGISTRY_BY_INTENT = {profile.intent_key: profile for profile in DECISION_REGISTRY}

# Semantic Layer側で intent="unknown" となった場合のフォールバック
UNKNOWN_DECISION_PROFILE = DecisionProfile(
    intent_key="unknown",
    action_profile="verification_first",
    default_action="意図を明確化するため、利用者に追加情報を確認する",
    alternative_actions=("関連すると思われるIntent候補を提示する",),
    priority_weight=0.3,
    base_risk=0.3,
    risk_factors=("Intentが特定できないため、不確実性が高い",),
)


def get_decision_profile(intent_key: str) -> DecisionProfile:
    """Intentキーに対応するDecisionProfileを取得する。未知のキーはフォールバックを返す。"""
    return DECISION_REGISTRY_BY_INTENT.get(intent_key, UNKNOWN_DECISION_PROFILE)

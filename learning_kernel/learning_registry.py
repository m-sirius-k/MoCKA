"""
MoCKA 3.0 — Self-Learning Kernel
learning_registry.py

責務:
  Self-Learning Kernelが扱う「学習可能パラメータ」の定義・許容範囲・
  最大変化量(max_delta)・安全閾値・rollbackルールを一元管理する。

  本Registryは定義のみを行い、実際のパラメータ値の変更は
  weight_state_store.WeightStateStore が担う。
"""


class TargetLayer:
    DECISION = "decision"
    MEMORY = "memory"
    SEMANTIC = "semantic"

    ALL = (DECISION, MEMORY, SEMANTIC)


class UpdateStatus:
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"

    ALL = (PENDING, APPROVED, REJECTED, APPLIED, ROLLED_BACK)


# 初期Learning State。weight_state_store.WeightStateStoreの初期値として使用する。
DEFAULT_LEARNING_STATE = {
    "decision": {
        "priority_weights": {
            "intent_importance": 0.30,
            "context_strength": 0.20,
            "dependency": 0.15,
            "urgency": 0.15,
            "intent_clarity": 0.20,
        },
        "risk_weights": {
            "base_risk": 0.40,
            "governance_violation": 0.20,
            "unknown_behavior": 0.20,
            "context_uncertainty": 0.20,
        },
        "rationale_weight_bias": 0.0,
    },
    "memory": {
        "relevance_decay_rate": 0.15,
        "recency_bias": 0.15,
        "compression_threshold": 0.30,
    },
    "semantic": {
        "intent_confidence_threshold": 0.50,
        "context_expansion_rate": 0.20,
    },
}


# 学習対象として許可されるパラメータパス -> (min, max)
# "decision.priority_weights.intent_clarity" のような "." 区切りパスで表現する。
PARAM_BOUNDS = {
    "decision.priority_weights.intent_importance": (0.0, 1.0),
    "decision.priority_weights.context_strength": (0.0, 1.0),
    "decision.priority_weights.dependency": (0.0, 1.0),
    "decision.priority_weights.urgency": (0.0, 1.0),
    "decision.priority_weights.intent_clarity": (0.0, 1.0),
    "decision.risk_weights.base_risk": (0.0, 1.0),
    "decision.risk_weights.governance_violation": (0.0, 1.0),
    "decision.risk_weights.unknown_behavior": (0.0, 1.0),
    "decision.risk_weights.context_uncertainty": (0.0, 1.0),
    "decision.rationale_weight_bias": (-0.5, 0.5),
    "memory.relevance_decay_rate": (0.0, 1.0),
    "memory.recency_bias": (0.0, 1.0),
    "memory.compression_threshold": (0.0, 1.0),
    "semantic.intent_confidence_threshold": (0.0, 1.0),
    "semantic.context_expansion_rate": (0.0, 1.0),
}


# Feedback Layer(feedback/weight_optimizer.py)が出力するparameter名から、
# Learning Stateのパラメータパスへの対応表。
# "invert" がTrueの場合、suggested_deltaの符号を反転して適用する
# (例: 「再利用性向上のためintent_match重みを上げる」提案を、
#  「memoryのdecay_rateを下げる(=減衰を弱める)」学習アクションへ変換する)。
LEARNING_PARAM_MAP = {
    ("decision", "intent_clarity"): {
        "path": "decision.priority_weights.intent_clarity",
        "invert": False,
    },
    ("decision", "governance_violation"): {
        "path": "decision.risk_weights.governance_violation",
        "invert": False,
    },
    ("memory", "intent_match"): {
        "path": "memory.relevance_decay_rate",
        "invert": True,
    },
    ("memory", "recency_decay"): {
        "path": "memory.recency_bias",
        "invert": False,
    },
    ("semantic", "confidence_threshold"): {
        "path": "semantic.intent_confidence_threshold",
        "invert": False,
    },
}


# 1回の学習アクションあたりの最大変化量(絶対値)。
MAX_DELTA = 0.10

# decision.risk_weights.* を「増加」させる場合の追加上限。
# risk上昇防止のため、通常のMAX_DELTAより厳しい値を用いる。
RISK_INCREASE_LIMIT = 0.05

# stability_score(0-1)がこの値未満の場合、Update Validatorは
# 当該更新をstability不足としてrejectする。
STABILITY_THRESHOLD = 0.5

# stability_score算出時に参照する「直近の適用済み更新数」の上限。
# 直近 STABILITY_WINDOW 件中の適用数が多いほどstability_scoreは下がる。
STABILITY_WINDOW = 10

# Rollbackが推奨されるトリガー条件(ドキュメント・テスト用の定義)。
ROLLBACK_TRIGGERS = (
    "performance_degradation",
    "audit_failure",
    "stability_drop",
)


def get_param_bounds(path: str):
    """パラメータパスの (min, max) を返す。未定義の場合はNone。"""
    return PARAM_BOUNDS.get(path)


def is_allowed_target(path: str) -> bool:
    """pathが学習対象として許可されているかどうかを返す。"""
    return path in PARAM_BOUNDS


def get_param_mapping(target_layer: str, parameter: str):
    """
    Feedback Layerのtarget_layer/parameterからLearning Stateの
    パラメータパスとinvertフラグを返す。未対応の場合はNone。
    """
    return LEARNING_PARAM_MAP.get((target_layer, parameter))


def is_risk_weight(path: str) -> bool:
    return path.startswith("decision.risk_weights.")

"""
MoCKA 3.0 — Self-Learning Kernel
learning_state.py

責務:
  Learning Kernelが保持する「学習対象パラメータ(重み)」を表す
  不変(frozen)データクラス。実際のDecision/Memory/Semantic Layerの
  コード・Registryには一切触れず、Learning Kernel内部の
  shadow weight-state としてのみ機能する。
"""

from dataclasses import dataclass, field
from typing import Dict

from learning_registry import DEFAULT_LEARNING_STATE


@dataclass(frozen=True)
class DecisionLearningState:
    priority_weights: Dict[str, float]
    risk_weights: Dict[str, float]
    rationale_weight_bias: float

    def to_dict(self) -> dict:
        return {
            "priority_weights": dict(self.priority_weights),
            "risk_weights": dict(self.risk_weights),
            "rationale_weight_bias": self.rationale_weight_bias,
        }

    @staticmethod
    def from_dict(data: dict) -> "DecisionLearningState":
        return DecisionLearningState(
            priority_weights=dict(data["priority_weights"]),
            risk_weights=dict(data["risk_weights"]),
            rationale_weight_bias=data["rationale_weight_bias"],
        )


@dataclass(frozen=True)
class MemoryLearningState:
    relevance_decay_rate: float
    recency_bias: float
    compression_threshold: float

    def to_dict(self) -> dict:
        return {
            "relevance_decay_rate": self.relevance_decay_rate,
            "recency_bias": self.recency_bias,
            "compression_threshold": self.compression_threshold,
        }

    @staticmethod
    def from_dict(data: dict) -> "MemoryLearningState":
        return MemoryLearningState(
            relevance_decay_rate=data["relevance_decay_rate"],
            recency_bias=data["recency_bias"],
            compression_threshold=data["compression_threshold"],
        )


@dataclass(frozen=True)
class SemanticLearningState:
    intent_confidence_threshold: float
    context_expansion_rate: float

    def to_dict(self) -> dict:
        return {
            "intent_confidence_threshold": self.intent_confidence_threshold,
            "context_expansion_rate": self.context_expansion_rate,
        }

    @staticmethod
    def from_dict(data: dict) -> "SemanticLearningState":
        return SemanticLearningState(
            intent_confidence_threshold=data["intent_confidence_threshold"],
            context_expansion_rate=data["context_expansion_rate"],
        )


@dataclass(frozen=True)
class LearningState:
    decision: DecisionLearningState
    memory: MemoryLearningState
    semantic: SemanticLearningState
    version: int = 1

    def to_dict(self) -> dict:
        return {
            "decision": self.decision.to_dict(),
            "memory": self.memory.to_dict(),
            "semantic": self.semantic.to_dict(),
            "version": self.version,
        }

    @staticmethod
    def from_dict(data: dict) -> "LearningState":
        return LearningState(
            decision=DecisionLearningState.from_dict(data["decision"]),
            memory=MemoryLearningState.from_dict(data["memory"]),
            semantic=SemanticLearningState.from_dict(data["semantic"]),
            version=data.get("version", 1),
        )

    @staticmethod
    def default() -> "LearningState":
        return LearningState.from_dict(DEFAULT_LEARNING_STATE | {"version": 1})


def get_value(state: LearningState, path: str):
    """'decision.priority_weights.intent_clarity' のようなdotパスから値を取得する。"""
    data = state.to_dict()
    node = data
    for part in path.split("."):
        node = node[part]
    return node


def with_value(state: LearningState, path: str, new_value) -> LearningState:
    """
    pathで指定されたパラメータをnew_valueに置き換えた新しいLearningStateを返す
    (元のstateは変更しない、frozen dataclassのため)。
    """
    data = state.to_dict()
    parts = path.split(".")
    node = data
    for part in parts[:-1]:
        node = node[part]
    node[parts[-1]] = new_value
    data["version"] = state.version + 1
    return LearningState.from_dict(data)

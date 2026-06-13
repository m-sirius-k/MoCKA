"""
MoCKA 3.0 — Semantic Layer
semantic_sample_cases.py

semantic_integration_test.py から参照するサンプルケース集。
各ケースは「入力テキスト」「コンテキスト」「期待されるIntentキー」を持つ。
"""

SAMPLE_CASES = (
    {
        "name": "information_retrieval_overview",
        "text": "現在のOverviewを見せて",
        "context": {"phase": "phase2-1", "active_task": "TODO_999"},
        "expected_intent": "information_retrieval",
    },
    {
        "name": "design_architecture",
        "text": "Semantic Layerのアーキテクチャを設計してください",
        "context": {"phase": "phase2-1"},
        "expected_intent": "design",
    },
    {
        "name": "implementation_new_module",
        "text": "Intent Classifierを実装して新しいモジュールを追加して",
        "context": {"phase": "phase2-1", "active_task": "TODO_implement_semantic"},
        "expected_intent": "implementation",
    },
    {
        "name": "fix_bug",
        "text": "このエラーを修正してください、バグがあります",
        "context": {"recent_events": ("E1", "E2")},
        "expected_intent": "fix",
    },
    {
        "name": "audit_governance",
        "text": "Governance Layerの監査を実施してcomplianceを確認したい",
        "context": {"phase": "audit"},
        "expected_intent": "audit",
    },
    {
        "name": "verification_test",
        "text": "テストを実行して動作確認してください",
        "context": {},
        "expected_intent": "verification",
    },
    {
        "name": "record_event",
        "text": "この作業内容をeventとして記録して",
        "context": {},
        "expected_intent": "record",
    },
    {
        "name": "comparison_diff",
        "text": "v1.0とv1.1の差分を比較してください",
        "context": {},
        "expected_intent": "comparison",
    },
    {
        "name": "summary_overview",
        "text": "今回の変更内容を要約してまとめてください",
        "context": {},
        "expected_intent": "summary",
    },
    {
        "name": "planning_roadmap",
        "text": "次のフェーズの計画とロードマップを立てたい",
        "context": {"phase": "planning"},
        "expected_intent": "planning",
    },
    {
        "name": "unknown_intent",
        "text": "xyzzy plugh quux",
        "context": {},
        "expected_intent": "unknown",
    },
)

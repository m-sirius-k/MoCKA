"""
MoCKA 3.0 — Decision Layer
decision_sample_cases.py

decision_integration_test.py から参照するサンプルケース集。
各ケースは「入力テキスト」「コンテキスト」「期待されるaction_profile」を持つ。
"""

DECISION_SAMPLE_CASES = (
    {
        "name": "information_retrieval_read_heavy",
        "text": "現在のOverviewを見せて",
        "context": {"phase": "phase2-2", "active_task": "TODO_999"},
        "expected_action_profile": "read_heavy",
    },
    {
        "name": "implementation_write_heavy",
        "text": "Decision Engineを実装して新しいモジュールを追加して",
        "context": {"phase": "phase2-2", "active_task": "TODO_implement_decision"},
        "expected_action_profile": "write_heavy",
    },
    {
        "name": "fix_write_heavy_high_risk",
        "text": "このエラーを修正してください、バグがあります",
        "context": {"recent_events": ("E1", "E2")},
        "expected_action_profile": "write_heavy",
    },
    {
        "name": "audit_verification_first",
        "text": "Governance Layerの監査を実施してcomplianceを確認したい",
        "context": {"phase": "audit"},
        "expected_action_profile": "verification_first",
    },
    {
        "name": "verification_verification_first",
        "text": "テストを実行して動作確認してください",
        "context": {},
        "expected_action_profile": "verification_first",
    },
    {
        "name": "planning_analysis_heavy",
        "text": "次のフェーズの計画とロードマップを立てたい",
        "context": {"phase": "planning", "active_task": "TODO_roadmap"},
        "expected_action_profile": "analysis_heavy",
    },
    {
        "name": "unknown_intent_fallback",
        "text": "xyzzy plugh quux",
        "context": {},
        "expected_action_profile": "verification_first",
    },
)

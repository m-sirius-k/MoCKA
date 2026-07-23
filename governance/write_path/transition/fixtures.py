"""WP-Schema-02 検証用サンプルレコード(テスト専用、実データではない)"""

EXAMPLE_GOVERNANCE_TRANSITION_RECORD = {
    "governance_transition_id": "GTR_20260723_001",
    "decision_id": "DC-WP-001",
    "commit_reference": "f1f0b6932c8f1995f133b7801477214cdcd1b7b0",
    "anchor_reference": "37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5",
    "approval_state": "Active",
    "immutable_boundary": True,
}

INVALID_EXAMPLE_BAD_APPROVAL_STATE = {
    "governance_transition_id": "GTR_20260723_002",
    "decision_id": "DC-WP-001",
    "commit_reference": "f1f0b6932c8f1995f133b7801477214cdcd1b7b0",
    "anchor_reference": "37b603b8b0d5782bff54bd24efb4ca38adb52d00dad7a3a47702194aa471e7d5",
    "approval_state": "approved",  # 不正値(正規enumはActive/Superseded/Withdrawn)
    "immutable_boundary": True,
}

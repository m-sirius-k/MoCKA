"""
WP-Schema-02: Governance Transition Record

Phase2A調査で確定: Decision Ledger(data/decisions/decision_ledger.jsonl)は
.gitignoreのdata/*ルールで完全に非追跡であり、commit_reference/anchor_referenceに
相当するフィールドを持たない。Governance Seal(governance/anchor_record.json)との
接続点が存在しないことが、Restore Authorityへの経路が欠落していた根本原因の一つだった。

本schemaはこの欠落を埋める「橋渡し」層である。Authorityそのものではなく、
Decision LedgerをGovernance Sealへ追跡可能にするための記録種別。

設計方針(Phase3 R01修正版):
    commit_reference / anchor_reference を主キーにしない。
    governance_transition_id を中心に置き、Decision / Commit / Seal は
    その従属参照として扱う(Transitionは制度イベント、Commitは実装artifact)。

commit_reference / anchor_reference は Core側で自動解決する値であり、
呼び出し側(人間・AI問わず)が手入力することを禁止する(虚偽のSeal参照を防ぐため、
Phase5 R01判断に準拠)。
"""

from typing import TypedDict, Literal


ApprovalState = Literal["Active", "Superseded", "Withdrawn"]


class GovernanceTransitionRecord(TypedDict):
    governance_transition_id: str    # 主キー。例: GTR_YYYYMMDD_NNN
    decision_id: str                 # Decision Ledgerへの参照(data/decisions/decision_ledger.jsonl)
    commit_reference: str            # 直近git commit sha(Core側で自動解決、手入力不可)
    anchor_reference: str            # 直近anchor_record.sealed_summary_hash(Core側で自動解決)
    approval_state: ApprovalState    # 対応するDecisionのstatusと同期
    immutable_boundary: bool         # 常にTrue


REQUIRED_FIELDS = (
    "governance_transition_id",
    "decision_id",
    "commit_reference",
    "anchor_reference",
    "approval_state",
    "immutable_boundary",
)

VALID_APPROVAL_STATES = ("Active", "Superseded", "Withdrawn")


def validate(record: dict) -> list:
    """GovernanceTransitionRecordの構造を検証する。エラー文字列のリストを返す(空なら妥当)。"""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")

    if "approval_state" in record and record["approval_state"] not in VALID_APPROVAL_STATES:
        errors.append(
            f"approval_state must be one of {VALID_APPROVAL_STATES}, "
            f"got: {record['approval_state']!r}"
        )

    if "immutable_boundary" in record and record["immutable_boundary"] is not True:
        errors.append("immutable_boundary must be True (append-only invariant)")

    return errors

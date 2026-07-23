"""
WP-Schema-03: Restore Packet v1

Legacy(PlanningCaliber/fp/restore_packet.json)との違い:
    Legacyは immutable / restore_5points / session_context / generated_at の
    4フィールドのみで、生成コード自体が存在しなかった(Phase0/Phase3 legacy調査で確定)。
    その結果、2026-05-28生成のまま約8週間、無警告で新規セッションへ注入され続けた
    (TODO_439)。

Freshness Contract(WP-05, Phase4-03確定):
    Primary Freshness Condition は時間経過ではなく Authority一致。
        packet.governance_anchor_hash == current governance sealed_summary_hash
    不一致の場合は STALE_CONTEXT として扱う。
    Reader側の挙動は Mode C(縮退): immutable層のみ許可、dynamic contextは拒否
    (HG-WP-04, R01推奨)。

Supersede Resolution(HG-WP-05, Phase6/8確定):
    「最新」判定は 単純timestamp最大ではなく、
    Governance Seal一致 + sequence最大 + supersedes chain有効 の複合条件とする。
    そのため sequence フィールドを必須とする。

immutable の意味は WP-Schema-01と同様、append-only運用規約を指す。
"""

from typing import TypedDict, Optional, List


class RestorePayload(TypedDict):
    immutable: dict          # philosophy / forbidden / values 等(Legacy互換)
    restore_5points: dict    # Legacy互換(2_current_goal / 4_tensions 等)
    session_context: str     # Legacy互換


class RestorePacketV1(TypedDict):
    schema_version: str              # 例: "1.0"
    packet_id: str                   # 例: RP_YYYYMMDD_NNN
    governance_anchor_hash: str      # 生成時点のGovernance Seal値(WP-05 Primary Freshness Condition)
    runtime_evidence_ref: str        # WP-Schema-01 record_idへの参照
    decision_refs: List[str]         # WP-Schema-02 governance_transition_id群への参照
    event_range: dict                # {from_event_id, to_event_id, event_count}
    generated_at: str                # ISO8601 UTC(補助情報。Authority一致がPrimary判定基準)
    content_hash: str                # packetペイロード自体のハッシュ(governance_anchor_hashとは別物)
    immutable: bool                  # 常にTrue
    supersedes: Optional[str]        # 直前packet_id(なければNone)
    sequence: int                    # supersede chain resolution用の単調増加番号
    payload: RestorePayload


REQUIRED_FIELDS = (
    "schema_version",
    "packet_id",
    "governance_anchor_hash",
    "runtime_evidence_ref",
    "decision_refs",
    "event_range",
    "generated_at",
    "content_hash",
    "immutable",
    "sequence",
    "payload",
)

REQUIRED_PAYLOAD_FIELDS = ("immutable", "restore_5points", "session_context")


def validate(record: dict) -> list:
    """RestorePacketV1の構造を検証する。エラー文字列のリストを返す(空なら妥当)。"""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")

    if "decision_refs" in record and not isinstance(record["decision_refs"], list):
        errors.append("decision_refs must be a list")

    if "sequence" in record and not isinstance(record["sequence"], int):
        errors.append("sequence must be an integer")

    if "immutable" in record and record["immutable"] is not True:
        errors.append("immutable must be True (append-only invariant)")

    if "payload" in record:
        payload = record["payload"]
        if not isinstance(payload, dict):
            errors.append("payload must be an object")
        else:
            for field in REQUIRED_PAYLOAD_FIELDS:
                if field not in payload:
                    errors.append(f"missing required field: payload.{field}")

    return errors


def is_fresh(packet: dict, current_governance_anchor_hash: str) -> bool:
    """
    Freshness Verification API相当の判定ロジック(WP-05)。
    Authority一致のみを基準とし、generated_atの経過時間は判定に用いない。
    """
    return packet.get("governance_anchor_hash") == current_governance_anchor_hash

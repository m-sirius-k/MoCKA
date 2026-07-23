"""
WP-Schema-01: Runtime Evidence Record

現行の mocka_seal() は events.db 全件から即時に SHA-256 を計算するのみで、
結果はどこにも永続化されず、呼び出しのたびに集合が変化する(Phase1A/6-01調査で確定)。
本schemaは、この一時的な観測値を「再検証可能なEvidence」として固定するための
最小フィールド定義である(WRITE_PATH_v1_FINAL_SPEC WP-05準拠)。

Authority relation:
    Runtime Evidence Record は Authority ではない(DC-WP-001)。
    Governance Seal(governance/anchor_record.json)に従属する Evidence として扱う。

immutable の意味:
    物理的なDB変更不能ではなく、append-only運用規約を指す。
    訂正が必要な場合は既存レコードを書き換えず、新規record_idのレコードを追加する
    (Phase3 R01判断に準拠)。
"""

from typing import TypedDict, Optional


class SourceEventRange(TypedDict):
    from_event_id: str
    to_event_id: str
    event_count: int


class RuntimeEvidenceRecord(TypedDict):
    record_id: str                      # 例: RER_YYYYMMDD_NNN
    source_event_range: SourceEventRange
    hash: str                           # sha256(json.dumps(rows, ensure_ascii=False, sort_keys=True))
    hash_method_spec: str                # 例: "sha256_json_sorted_v1"
    generated_at: str                   # ISO8601 UTC
    generated_by: str                    # 呼び出し主体(AI識別子 / session_id)
    governance_anchor_hash: Optional[str]  # 生成時点で有効だったGovernance Seal値(任意)
    immutable: bool                     # 常にTrue。append-only運用規約であることを表す


REQUIRED_FIELDS = (
    "record_id",
    "source_event_range",
    "hash",
    "hash_method_spec",
    "generated_at",
    "generated_by",
    "immutable",
)

REQUIRED_RANGE_FIELDS = ("from_event_id", "to_event_id", "event_count")


def validate(record: dict) -> list:
    """RuntimeEvidenceRecordの構造を検証する。エラー文字列のリストを返す(空なら妥当)。"""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in record:
            errors.append(f"missing required field: {field}")

    if "source_event_range" in record:
        rng = record["source_event_range"]
        if not isinstance(rng, dict):
            errors.append("source_event_range must be an object")
        else:
            for field in REQUIRED_RANGE_FIELDS:
                if field not in rng:
                    errors.append(f"missing required field: source_event_range.{field}")
            if "event_count" in rng and not isinstance(rng["event_count"], int):
                errors.append("source_event_range.event_count must be an integer")

    if "immutable" in record and record["immutable"] is not True:
        errors.append("immutable must be True (append-only invariant)")

    return errors

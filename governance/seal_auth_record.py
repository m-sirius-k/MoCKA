"""
governance/seal_auth_record.py
AUTO_SEAL M1: Auth Model record layer (Model B / DC_20260713_003).

sandbox/一時パス限定。既存seal経路(SealGovernanceGate/anchor_update.py)には
接続しない(M2)。本番 decision_ledger.jsonl には書かない。記録層のみで、
seal/hash/commit の実処理は呼ばない。

Model B(DC_20260713_003)の Auth Model:
approved_by=human を成立条件とし、AI/自動処理系が自己判断だけで封印権限を
成立させる構造を禁止する。verify はその判定を返すのみで、実seal停止(強制)は
しない(強制の接続はM2)。
"""
import json
from pathlib import Path

REQUIRED_FIELDS = (
    "seal_request_id", "requester", "decision_id",
    "approved_by", "approval_timestamp",
)


def write_auth_record(ledger_path, record):
    """Auth拡張レコードを append-only JSONL で追記する(sandbox限定)。"""
    p = Path(ledger_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def read_auth_records(ledger_path):
    """JSONL全行を読む。旧行(拡張なし)も新行も同様に parse する(後方互換)。"""
    p = Path(ledger_path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def verify_auth_record(record):
    """
    Model B成立条件を判定する。強制(実seal停止)はしない(M2)。
    Returns (ok: bool, reasons: list[str])。
    """
    reasons = []
    for k in REQUIRED_FIELDS:
        if not record.get(k):
            reasons.append("missing:" + k)
    approved_by = str(record.get("approved_by", ""))
    if approved_by == "" or approved_by.startswith("system"):
        reasons.append("approved_by_not_human")
    requester = str(record.get("requester", ""))
    if requester.startswith("system:auto_audit_loop") and not record.get("pending_ref"):
        reasons.append("missing:pending_ref")
    return (len(reasons) == 0, reasons)


def find_duplicate_request_ids(ledger_path):
    """seal_request_id の重複を検出する(一意性チェック)。"""
    ids = [r.get("seal_request_id") for r in read_auth_records(ledger_path)
           if r.get("seal_request_id")]
    return sorted({i for i in ids if ids.count(i) > 1})

"""ISE Decision Ledger v1"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from .taxonomy_validator import get_category

LEDGER_PATH = Path("data/ise/decision_ledger.jsonl")

# Decision Ledgerへの記録が許される Taxonomy v1.1 カテゴリ。
# "incident" はタイムアウト等の異常記録のため許可（既存運用との後方互換）。
ALLOWED_DECISION_CATEGORIES = {"governance", "audit", "state_transition", "incident"}


def _hash(entry: dict) -> str:
    payload = json.dumps(entry, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def append_decision(
    decision_type: str,   # "state_transition" | "knock_response" | "provider_select"
    actor: str,           # AI識別子
    before: str,
    after: str,
    reason: str,
    prev_hash: str = ""
) -> dict:
    category = get_category(decision_type)
    if category is not None and category not in ALLOWED_DECISION_CATEGORIES:
        raise ValueError(
            f"decision_type '{decision_type}' belongs to category '{category}'. "
            f"Must be one of: {ALLOWED_DECISION_CATEGORIES}"
        )

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": decision_type,
        "actor": actor,
        "before": before,
        "after": after,
        "reason": reason,
        "prev_hash": prev_hash,
    }
    entry["hash"] = _hash(entry)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_ledger() -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    with open(LEDGER_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def verify_chain() -> tuple[bool, str]:
    """チェーン整合性検証。(ok, message)を返す"""
    entries = read_ledger()
    for i, entry in enumerate(entries):
        stored_hash = entry.pop("hash", "")
        computed = _hash(entry)
        entry["hash"] = stored_hash
        if stored_hash != computed:
            return False, f"Hash mismatch at entry {i}: {stored_hash} != {computed}"
    return True, f"Chain verified: {len(entries)} entries OK"

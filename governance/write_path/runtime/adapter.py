"""
Decision Transition -> GovernanceTransitionRecord 変換経路(Phase8-2)

decision_ledger.jsonl / anchor_record.json はいずれも読み取り専用でアクセスする。
mocka_mcp_server.py(Flask app)は起動副作用を持つためimportせず、
本モジュール内で同等の読み取りロジックを自己完結で実装する。

commit_reference / anchor_reference はいずれもCore側(本モジュール)が
自動解決する値であり、呼び出し側からの手入力は受け付けない
(Phase5 R01判断: 虚偽のSeal参照を防止するため)。
"""

import json
import subprocess
import sys
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
DECISION_LEDGER_PATH = MOCKA_ROOT / "data" / "decisions" / "decision_ledger.jsonl"
ANCHOR_RECORD_PATH = MOCKA_ROOT / "governance" / "anchor_record.json"

sys.path.insert(0, str(MOCKA_ROOT))
from governance.write_path.transition import schema as transition_schema  # noqa: E402


def _read_decision(decision_id: str):
    """decision_ledger.jsonlを読み取り専用で走査し、指定decision_idの最新行を返す。
    同一decision_idの複数行がある場合は末尾行(最新状態)を優先する(既存仕様と同一)。"""
    if not DECISION_LEDGER_PATH.exists():
        return None
    latest = None
    with open(DECISION_LEDGER_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("decision_id") == decision_id:
                latest = rec
    return latest


def _resolve_commit_reference() -> str:
    """直近のgit commit shaを読み取り専用のgitコマンドで解決する。"""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H"],
        capture_output=True, text=True, cwd=MOCKA_ROOT
    )
    return result.stdout.strip()


def _resolve_anchor_reference() -> str:
    """governance/anchor_record.json(正本、HG-WP-05確定)を読み取り専用で参照する。"""
    if not ANCHOR_RECORD_PATH.exists():
        return ""
    ar = json.loads(ANCHOR_RECORD_PATH.read_text(encoding="utf-8"))
    return ar.get("sealed_summary_hash", "")


def build_transition_record(decision_id: str, sequence: int = 1) -> dict:
    """
    指定decision_idについて GovernanceTransitionRecord を組み立てる。
    commit_reference/anchor_referenceは本関数が自動解決する(手入力パラメータなし)。
    永続化は行わない(in-memoryでの生成・検証のみ)。
    """
    decision = _read_decision(decision_id)
    if decision is None:
        raise ValueError(f"decision_id not found in decision_ledger.jsonl: {decision_id}")

    record = {
        "governance_transition_id": f"GTR_{decision_id}_{sequence:03d}",
        "decision_id": decision_id,
        "commit_reference": _resolve_commit_reference(),
        "anchor_reference": _resolve_anchor_reference(),
        "approval_state": decision.get("status", "Active"),
        "immutable_boundary": True,
    }

    errors = transition_schema.validate(record)
    if errors:
        raise ValueError(f"generated GovernanceTransitionRecord failed validation: {errors}")

    return record

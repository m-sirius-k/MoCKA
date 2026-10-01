# phi_os/decision_reader.py
# BE-002: Decision Ledger Query / Access Capability
# Decision Ledger読み取り・クエリ機能の実装

import json
from pathlib import Path
from typing import dict, list, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
DECISION_LEDGER_PATH = _REPO_ROOT / 'data' / 'decisions' / 'decision_ledger.jsonl'


def get_decision(decision_id: str) -> Optional[dict]:
    """
    Decision Ledgerから単一の決定を取得する。

    Args:
        decision_id: 取得対象のDecision ID (DC_YYYYMMDD_NNN形式)

    Returns:
        dict: Decision Record、またはNone (見つからない場合)
    """
    if not DECISION_LEDGER_PATH.exists():
        return None

    try:
        with DECISION_LEDGER_PATH.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if record.get('decision_id') == decision_id:
                        return record
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return None


def list_decisions_by_status(status: str) -> list:
    """
    指定ステータスの決定を一覧取得する。

    Args:
        status: ステータス ('Active', 'Superseded', 'Expired', etc.)

    Returns:
        list: マッチした Decision Records
    """
    results = []
    if not DECISION_LEDGER_PATH.exists():
        return results

    try:
        with DECISION_LEDGER_PATH.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    if record.get('status') == status:
                        results.append(record)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return results


def list_decisions_by_scope(authorization_scope: str) -> list:
    """
    指定Authorization Scopeの決定を一覧取得する。

    Args:
        authorization_scope: Authorization Scope (tool名、component名など)

    Returns:
        list: マッチした Decision Records
    """
    results = []
    if not DECISION_LEDGER_PATH.exists():
        return results

    try:
        with DECISION_LEDGER_PATH.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    scope = record.get('authorization_scope', '')
                    if scope == authorization_scope or authorization_scope in str(scope):
                        results.append(record)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return results


def list_all_decisions() -> list:
    """
    Decision Ledger内のすべての決定を取得する。

    Returns:
        list: すべての Decision Records
    """
    results = []
    if not DECISION_LEDGER_PATH.exists():
        return results

    try:
        with DECISION_LEDGER_PATH.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    results.append(record)
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return results


def is_decision_active(decision_id: str) -> bool:
    """
    決定がアクティブ状態か確認する。

    Args:
        decision_id: Decision ID

    Returns:
        bool: Activeの場合True
    """
    decision = get_decision(decision_id)
    if decision is None:
        return False
    return decision.get('status') == 'Active'

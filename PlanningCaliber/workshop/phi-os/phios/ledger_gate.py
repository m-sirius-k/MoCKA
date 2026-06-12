# phi_os/ledger_gate.py
"""
Decision Ledgerを唯一の信頼源(source of truth)として扱うためのヘルパー。

current_state.json (revision_store.json等) は Ledger からの「派生物
(cache)」であり、いつでも Ledger から再構築できる。
"""
from __future__ import annotations

from ise import decision_ledger


def rebuild_state_from_ledger() -> dict:
    """
    Decision Ledgerの全エントリからrevisionを再計算する。
    revision = state_transitionカテゴリのうちrevision_increment対象の件数。
    （現状のDecision Ledgerはrevision_incrementを保持しないため、
     "type"がSTATE_DEGRADED/STATE_RECOVERED/STATE_SUSPENDED等の
     revision増加対象エントリ数を数える簡易再構築を行う）
    """
    from ise.taxonomy_validator import get_category, is_revision_update

    entries = decision_ledger.read_ledger()
    revision = 0
    for entry in entries:
        event_type = entry.get("type")
        if get_category(event_type) is not None and is_revision_update(event_type):
            revision += 1

    return {
        "revision": revision,
        "entry_count": len(entries),
    }


def verify_ledger_is_source_of_truth() -> tuple[bool, str]:
    """Decision Ledgerのチェーン整合性を検証する（Ledger自体の信頼性確認）"""
    return decision_ledger.verify_chain()

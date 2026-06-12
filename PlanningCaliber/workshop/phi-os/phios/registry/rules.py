# phi_os/registry/rules.py
"""
Registry層 — PHI-OS全体に適用される静的ルール定義。

すべて読み取り専用の定数。実行時に変更されない。
"""
from __future__ import annotations

# emit_event / EventPipeline 経由でも禁止される操作
FORBIDDEN_OPERATIONS = frozenset({
    "taxonomy.write",
    "taxonomy.delete",
    "decision_ledger.modify",
    "decision_ledger.delete",
    "registry.write",
    "ledger.rewrite_history",
})

# Decision Ledgerへの記録が許されるTaxonomy v1.1カテゴリ
# (ise.decision_ledger.ALLOWED_DECISION_CATEGORIES と整合させること)
ALLOWED_DECISION_CATEGORIES = frozenset({
    "governance",
    "audit",
    "state_transition",
})

# safe_boot() のフルゲート起動シーケンス（順序固定）
BOOT_SEQUENCE = (
    "taxonomy_load",
    "rules_load",
    "event_pipeline_init",
    "adapter_registry_init",
    "mock_adapter_register",
    "execution_gate_check",
)

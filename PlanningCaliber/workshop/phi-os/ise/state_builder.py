# state_builder.py
from __future__ import annotations
from .schema import InstitutionState, CURRENT_SCHEMA_VERSION
from .state_provider import StateProvider


def build_state(provider: StateProvider) -> InstitutionState:
    """
    Pure Function。
    - 副作用なし（DBへの書き込み・ファイル変更を行わない）
    - Revision採番を行わない（revision=0 で返す）
    - revision / state_hash / generated_at は revision_manager が付与する
    入力: StateProvider（データソース抽象）
    出力: InstitutionState（revision=0, state_hash="" の未完成State）
    """
    return InstitutionState(
        state_version       = CURRENT_SCHEMA_VERSION,
        project             = provider.get_project_status(),
        warnings            = provider.get_active_warnings(),
        todos               = provider.get_active_todos(),
        decision_ledger_rev = provider.get_decision_revision(),
        guideline_revision  = provider.get_guideline_revision(),
    )

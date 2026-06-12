# state_builder.py
from __future__ import annotations
from .schema import InstitutionState, CURRENT_SCHEMA_VERSION
from .state_provider import StateProvider
from .taxonomy_validator import validate_event_type, is_revision_update, get_category


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


def emit_event(event_type: str, **kwargs) -> dict:
    """
    Event Taxonomy v1.1 検証付きのイベント発行記述子を生成する。
    Pure Function（副作用なし）。実際の書き込み・revision更新は
    呼び出し側（revision_manager等）が responsibility を持つ。

    戻り値: {"event_type", "category", "revision_increment", ...kwargs}
    """
    if not validate_event_type(event_type):
        raise ValueError(f"Unknown event_type: '{event_type}'. Must be defined in taxonomy v1.1")

    return {
        "event_type": event_type,
        "category": get_category(event_type),
        "revision_increment": is_revision_update(event_type),
        **kwargs,
    }

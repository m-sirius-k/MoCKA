# phi_os/boot.py
"""safe_boot — PHI-OS起動シーケンス（フルゲート / 最低保証モード）"""
from __future__ import annotations

import os


def safe_boot(full: bool = True) -> bool:
    """
    full=True  -> フルゲート（通常起動）
    full=False -> 最小起動（degradedモード・debug用）
    """
    try:
        # 必須（どちらのモードでも実行）
        from phios.registry.taxonomy import get_taxonomy
        get_taxonomy()  # FROZENチェック

        from phios.registry import rules
        assert rules.FORBIDDEN_OPERATIONS

        from phios.core.event_pipeline import pipeline
        assert pipeline

        from phios.core import adapter_manager
        from phios.adapter.mock_adapter import MockAdapter
        adapter_manager.register("mock", MockAdapter())

        if full:
            from phios.core.execution_gate import gate_check
            if not gate_check():
                print("[PHI-OS] WARNING: verify_all failed. Falling back to degraded mode.")
                return _degraded_boot()

            if os.getenv("OPENAI_API_KEY"):
                from phios.adapter.openai_adapter import OpenAIAdapter
                adapter_manager.register("openai", OpenAIAdapter(api_key=os.getenv("OPENAI_API_KEY")))

        print("[PHI-OS] Boot complete.")
        return True

    except Exception as e:
        print(f"[PHI-OS] Boot failed: {e}")
        return False


def _degraded_boot() -> bool:
    """最低保証モード: taxonomy + registry のみ保証"""
    print("[PHI-OS] Degraded mode: taxonomy and registry only.")
    print("[PHI-OS] Boot complete.")
    return True

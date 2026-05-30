"""
vasAI API: アプリケーション状態 (movement / shadow シングルトン管理)
"""
from typing import Optional

_movement = None
_shadow = None


def init_app_state() -> None:
    global _movement, _shadow
    from movement.mocka_movement import MoCKAMovement
    from movement.shadow_movement import ShadowMovement
    from caliber.base_caliber import register
    from caliber.example_medical import MedicalCALIBER
    from caliber.example_finance import FinanceCALIBER

    _movement = MoCKAMovement()
    _shadow = ShadowMovement()

    register(MedicalCALIBER())
    register(FinanceCALIBER())


def get_movement():
    return _movement


def get_shadow():
    return _shadow

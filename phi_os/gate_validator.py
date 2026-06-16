# phi_os/gate_validator.py
# PHI-OS EVENT GATE v1 — Validation Logic
from .gate_schema import ALLOWED_WHAT_TYPES, ALLOWED_WHO_ROLES

LEGACY_ACTORS = {'Claude', 'claude', '', None}


def validate(payload: dict) -> list[str]:
    errors = []

    # REJECT-01: who_actor必須・レガシー値禁止
    a = payload.get('who_actor', '')
    if not a or a in LEGACY_ACTORS:
        errors.append('REJECT-01: who_actor必須 (例: Claude-sonnet-4-6)')

    # REJECT-02: who_session形式検査
    if not payload.get('who_session', '').startswith('SESSION_'):
        errors.append('REJECT-02: who_session形式不正 (SESSION_YYYYMMDD_HHMMSS)')

    # REJECT-03: why_purpose 10文字以上
    if len(payload.get('why_purpose', '')) < 10:
        errors.append('REJECT-03: why_purpose 10文字以上必須')

    # REJECT-04: how_trigger必須
    if not payload.get('how_trigger'):
        errors.append('REJECT-04: how_trigger必須')

    # REJECT-05: where_path必須
    if not payload.get('where_path'):
        errors.append('REJECT-05: where_path必須')

    # REJECT-06: what_type検査
    wt = payload.get('what_type', '')
    if wt not in ALLOWED_WHAT_TYPES:
        errors.append(f'REJECT-06: what_type不正 ({wt!r}) 許可値: {ALLOWED_WHAT_TYPES}')

    # REJECT-07: before/after どちらかが必須（Replay保証）
    b = payload.get('before_hash') or payload.get('before_state')
    a2 = payload.get('after_hash') or payload.get('after_state')
    if not b and not a2:
        errors.append('REJECT-07: before/afterどちらか必須(Replay不能)')

    return errors

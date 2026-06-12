# hash_generator.py
from __future__ import annotations
import json
import hashlib
from .schema import InstitutionState

# ハッシュ計算から除外するキー（比較不要な値）
HASH_EXCLUDED_KEYS = frozenset({"generated_at", "state_hash", "revision"})


def compute_state_hash(state: InstitutionState) -> str:
    """
    正規化ルール（必ず守ること）:
      1. キー順を固定（sort_keys=True）
      2. HASH_EXCLUDED_KEYS を除外
      3. JSON正規化（ensure_ascii=True, separators=(',',':')）
      4. UTF-8 encode → SHA-256

    同じ内容ならシリアライズ順に関わらず常に同じハッシュを返す。
    タイムスタンプが変わっても内容が同じならハッシュは変わらない。
    """
    d = state.to_dict()
    for key in HASH_EXCLUDED_KEYS:
        d.pop(key, None)

    normalized = json.dumps(
        d,
        sort_keys=True,
        ensure_ascii=True,
        separators=(',', ':'),
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

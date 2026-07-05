# -*- coding: utf-8 -*-
# ReferenceResolver: ID/エイリアスの正規化・存在検証のみを行う独立モジュール。
# DC_20260705_010準拠。KN-004 Registry(mocka_registry_get/add)とは別レイヤーであり、
# KN-004の書込・仕様(参照整合性は非保証)には一切変更を加えない。
#
# 責務:
#   - resolve:  誤参照ID(alias) -> 正規ID(canonical) への変換のみ。判断はしない。
#   - validate: 変換結果が既知IDの集合に実在するかを確認するだけ。意味の解釈はしない。
#   - register_alias: 誤参照が判明した場合の記録(上書きは事故防止のため拒否する)。
#
# 経緯: 2026-07-05、サブエージェント調査結果を検証せずDecision Ledgerへ書き込み、
# TODO_387(無関係の別件)をPHI-OS-HUMAN-GATE-STATE-MODEL-V1の代わりに誤参照した
# (DC_20260705_008→DC_20260705_009で訂正)。同種の再発を防ぐための最小実装。

import json
from pathlib import Path

ALIAS_FILE = Path(__file__).resolve().parent.parent / "data" / "reference_aliases.json"


class ReferenceError(Exception):
    pass


class ReferenceResolver:
    """ID/エイリアスの正規化のみを行う。良し悪しの判断はしない。"""

    def __init__(self, alias_file: Path = ALIAS_FILE):
        self.alias_file = alias_file
        self._aliases = self._load()

    def _load(self) -> dict:
        if not self.alias_file.exists():
            return {}
        return json.loads(self.alias_file.read_text(encoding="utf-8"))

    def resolve(self, ref_id: str) -> str:
        """ref_idの正規ID(canonical)を返す。エイリアス未登録ならref_id自身を返す
        (未登録であることを理由にエラーにはしない。存在確認はvalidateで行う)。"""
        return self._aliases.get(ref_id, ref_id)

    def validate(self, ref_id: str, known_ids) -> dict:
        """resolve結果がknown_idsに実在するかだけを確認する。

        known_ids: 実在するIDの集合(呼び出し側が用意する。例:
        MOCKA_TODO_ACTIVE.jsonのid一覧、decision_ledger.jsonlのdecision_id一覧等)。
        ReferenceResolver自身はこれらのファイルを読みに行かない(責務外)。
        """
        canonical = self.resolve(ref_id)
        return {
            "input": ref_id,
            "resolved_to": canonical,
            "is_alias": canonical != ref_id,
            "exists": canonical in known_ids,
        }

    def register_alias(self, wrong_id: str, canonical_id: str) -> None:
        """誤参照が判明した場合に記録する。

        既存エイリアスと矛盾する上書きは事故防止のため拒否する
        (同じwrong_idが別のcanonical_idに変わることは想定しない設計)。
        """
        existing = self._aliases.get(wrong_id)
        if existing is not None and existing != canonical_id:
            raise ReferenceError(
                f"alias conflict: {wrong_id!r} already resolves to "
                f"{existing!r}, not {canonical_id!r}"
            )
        self._aliases[wrong_id] = canonical_id
        self.alias_file.write_text(
            json.dumps(self._aliases, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

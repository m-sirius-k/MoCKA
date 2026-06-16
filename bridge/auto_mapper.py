# bridge/auto_mapper.py
# 自動マッピングアルゴリズム v1
#
# 処理フロー:
#   INPUT term
#   → fetch PHI-OS meaning
#   → fetch Personal meaning
#   → conflict_engine.check()
#   → IF conflict: mark CONFLICT, store in bridge only
#   → ELSE: create mapping
#   → update registry
#
# 制約:
#   自動修正禁止 / 意味改変禁止 / 必ず状態を残す

from __future__ import annotations
import sys
import os
from typing import Callable, Optional

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bridge.conflict_types import BridgeRecord, ConflictJudgment, ConflictState
from bridge.phi_personal_bridge import PhiPersonalBridge


# ─────────────────────────────────────────────────────────────
# Fetcher プロトコル
# ─────────────────────────────────────────────────────────────

# 呼び出し元が PHI-OS / Personal のアダプタを注入する
PhiOSFetcher    = Callable[[str], Optional[str]]
PersonalFetcher = Callable[[str], Optional[str]]


# ─────────────────────────────────────────────────────────────
# AutoMapper
# ─────────────────────────────────────────────────────────────

class AutoMapper:
    """
    term を受け取り、両系から意味を取得して Bridge に自動登録する。

    外部から PHI-OS / Personal へのアクセサ関数を注入することで、
    実際のストレージ実装に依存しない設計にしている。

    禁止事項:
      - 取得した意味の書き換え
      - CONFLICT 状態の自動解決
      - 状態なしでの registry 保存（PhiPersonalBridge 側が保証）
    """

    def __init__(
        self,
        bridge: PhiPersonalBridge,
        phi_os_fetcher: PhiOSFetcher,
        personal_fetcher: PersonalFetcher,
    ):
        self.bridge = bridge
        self._fetch_phi    = phi_os_fetcher
        self._fetch_personal = personal_fetcher

    # ─────────────────────────────────────────────────────────
    # Public
    # ─────────────────────────────────────────────────────────

    def map_term(self, term: str) -> BridgeRecord:
        """
        term を自動マッピングして BridgeRecord を返す。
        処理フロー通りに実行し、状態を必ず残す。
        """
        phi_meaning      = self._fetch_phi(term)
        personal_meaning = self._fetch_personal(term)

        # Bridge に判定を委譲（conflict_engine が内部で呼ばれる）
        record = self.bridge.register_mapping(
            term=term,
            phi_os_meaning=phi_meaning,
            personal_meaning=personal_meaning,
        )
        return record

    def map_batch(self, terms: list[str]) -> dict[str, BridgeRecord]:
        """
        複数 term を順次マッピングする。
        失敗した term はスキップせず例外を伝播する（暴走防止）。
        """
        results: dict[str, BridgeRecord] = {}
        for term in terms:
            results[term] = self.map_term(term)
        return results

    def resync_all(self) -> list[BridgeRecord]:
        """
        registry 内の全 term を再フェッチして同期する。
        LOCKED レコードはスキップされる（Bridge 側が保証）。
        """
        all_records = self.bridge.registry.list_all()
        updated: list[BridgeRecord] = []

        for record in all_records:
            if record.state == ConflictState.LOCKED:
                updated.append(record)
                continue

            new_phi      = self._fetch_phi(record.term)
            new_personal = self._fetch_personal(record.term)

            if new_phi is not None:
                record = self.bridge.sync_from_phi_os(record.term, new_phi)
            if new_personal is not None:
                record = self.bridge.sync_from_personal(record.term, new_personal)

            updated.append(record)

        return updated

    # ─────────────────────────────────────────────────────────
    # 診断ユーティリティ
    # ─────────────────────────────────────────────────────────

    def report(self) -> dict:
        """
        Bridge 全体の状態サマリを返す（デバッグ・監視用）。
        状態を変更する操作は行わない。
        """
        all_records = self.bridge.registry.list_all()
        by_state: dict[str, list[str]] = {
            ConflictState.NORMAL.value:   [],
            ConflictState.DRIFT.value:    [],
            ConflictState.CONFLICT.value: [],
            ConflictState.LOCKED.value:   [],
        }
        for r in all_records:
            by_state[r.state.value].append(r.term)

        return {
            "total":    len(all_records),
            "by_state": by_state,
        }

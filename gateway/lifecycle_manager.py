#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lifecycle Manager (TODO_275)

connector_log (TODO_274) と events.db を読み込み、
MoCKAの知識ライフサイクルを自動管理する。

処理フロー:
  1. Index       — connector_logの直近ログを収集
  2. Essence候補 — reusable=1 のログからKS記事候補を識別
  3. Relay候補   — 重要Connector結果を次セッションへ引き継ぐ候補を識別
  4. TODO候補    — エラーログ・パターンからTODO追加候補を提案
  5. Audit       — 実行サマリーをMoCKAイベント台帳に記録

実行方法:
  python lifecycle_manager.py [--window N]  # N=直近N件のログを処理（デフォルト100）
  または gateway.py から定期呼び出し

連携:
  connector_log.py (TODO_274) → 入力
  mocka_write_event             → 監査イベント記録
  interface/proposal_schema.py  → TODO候補をPRPとして提案
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# MoCKAルートをパスに追加
_MOCKA_ROOT = Path(os.environ.get("MOCKA_ROOT", r"C:\Users\sirok\MoCKA"))
if str(_MOCKA_ROOT) not in sys.path:
    sys.path.insert(0, str(_MOCKA_ROOT))
if str(_MOCKA_ROOT / "gateway") not in sys.path:
    sys.path.insert(0, str(_MOCKA_ROOT / "gateway"))
if str(_MOCKA_ROOT / "interface") not in sys.path:
    sys.path.insert(0, str(_MOCKA_ROOT / "interface"))

from connector_log import ConnectorLog


# ── 判定閾値 ──────────────────────────────────────────────────
_ESSENCE_MIN_REUSABLE    = 2    # 同一AI+capabilityでreusable=1が2件以上 → Essence候補
_RELAY_MIN_SUCCESS       = 3    # 同一capabilityで成功3件以上 → Relay候補
_TODO_ERROR_THRESHOLD    = 2    # 同一capabilityで失敗2件以上 → TODO候補


class LifecycleReport:
    """Lifecycle Manager の実行結果"""

    def __init__(self):
        self.essence_candidates: list[dict] = []
        self.relay_candidates:   list[dict] = []
        self.todo_candidates:    list[dict] = []
        self.audit_summary:      str = ""
        self.processed_count:    int = 0
        self.run_at:             str = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "run_at":             self.run_at,
            "processed_count":    self.processed_count,
            "essence_candidates": self.essence_candidates,
            "relay_candidates":   self.relay_candidates,
            "todo_candidates":    self.todo_candidates,
            "audit_summary":      self.audit_summary,
        }

    def print_summary(self):
        print(f"\n=== Lifecycle Manager 実行結果 ({self.run_at[:19]}) ===")
        print(f"処理件数: {self.processed_count}")
        print(f"\n[Essence候補] {len(self.essence_candidates)}件")
        for c in self.essence_candidates:
            print(f"  - {c['ai_name']} / {c['capability']}: reusable={c['reusable_count']}件")
        print(f"\n[Relay候補] {len(self.relay_candidates)}件")
        for c in self.relay_candidates:
            print(f"  - capability={c['capability']}: success={c['success_count']}件")
        print(f"\n[TODO候補] {len(self.todo_candidates)}件")
        for c in self.todo_candidates:
            print(f"  - [{c['capability']}] {c['title']}")
        print(f"\n{self.audit_summary}")


class LifecycleManager:
    """
    MoCKA知識ライフサイクル管理。
    connector_logを分析し、Essence/Relay/TODOの候補を識別する。
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._log = ConnectorLog(db_path)

    def run(self, window: int = 100) -> LifecycleReport:
        """
        Lifecycle管理を1サイクル実行する。

        Args:
            window: 処理対象の直近ログ件数

        Returns:
            LifecycleReport
        """
        report = LifecycleReport()

        logs = self._log.recent(limit=window)
        report.processed_count = len(logs)

        if not logs:
            report.audit_summary = "connector_logにデータなし — スキップ"
            return report

        report.essence_candidates = self._extract_essence_candidates(logs)
        report.relay_candidates   = self._extract_relay_candidates(logs)
        report.todo_candidates    = self._extract_todo_candidates(logs)
        report.audit_summary      = self._build_audit_summary(report, logs)

        # 監査イベントをMoCKAに記録
        self._record_audit_event(report)

        # TODO候補をProposal Schemaに投稿
        self._submit_todo_proposals(report.todo_candidates)

        return report

    def _extract_essence_candidates(self, logs: list[dict]) -> list[dict]:
        """
        reusable=1 のログをAI + capabilityでグループ化し、
        繰り返し再利用された知識をEssence候補として識別する。
        """
        counter: Counter = Counter()
        for log in logs:
            if log.get("reusable") == 1 and log.get("success") == 1:
                key = (log.get("ai_name", ""), log.get("capability") or "general")
                counter[key] += 1

        candidates = []
        for (ai_name, capability), count in counter.most_common():
            if count >= _ESSENCE_MIN_REUSABLE:
                candidates.append({
                    "ai_name":       ai_name,
                    "capability":    capability,
                    "reusable_count": count,
                    "suggestion":    (
                        f"{ai_name}の{capability}結果が{count}回再利用された。"
                        "KS記事化またはEssenceへの昇格を検討してください。"
                    ),
                })
        return candidates

    def _extract_relay_candidates(self, logs: list[dict]) -> list[dict]:
        """
        同一capabilityで複数回成功した結果をRelay候補として識別する。
        次セッションへ引き継ぐべき重要情報の目印。
        """
        counter: Counter = Counter()
        for log in logs:
            if log.get("success") == 1:
                cap = log.get("capability") or "general"
                counter[cap] += 1

        candidates = []
        for capability, count in counter.most_common():
            if count >= _RELAY_MIN_SUCCESS:
                candidates.append({
                    "capability":    capability,
                    "success_count": count,
                    "suggestion":    (
                        f"{capability}に関するConnector結果が{count}件蓄積されています。"
                        "次セッションのContext BriefingにRelayとして追加することを推奨します。"
                    ),
                })
        return candidates

    def _extract_todo_candidates(self, logs: list[dict]) -> list[dict]:
        """
        エラーパターンからTODO追加候補を識別する。
        同一capabilityで繰り返し失敗している場合は対応TODO化を提案する。
        """
        error_counter: Counter = Counter()
        error_details: dict[str, str] = {}
        for log in logs:
            if log.get("success") == 0:
                cap = log.get("capability") or "general"
                error_counter[cap] += 1
                if cap not in error_details and log.get("error_detail"):
                    error_details[cap] = log["error_detail"]

        candidates = []
        for capability, count in error_counter.most_common():
            if count >= _TODO_ERROR_THRESHOLD:
                detail = error_details.get(capability, "詳細不明")
                candidates.append({
                    "capability":   capability,
                    "error_count":  count,
                    "title":        f"Connector失敗対応: {capability}が{count}回エラー",
                    "evidence":     f"connector_log: capability={capability} errors={count} / {detail[:200]}",
                    "confidence":   min(0.9, 0.6 + count * 0.1),
                    "recommended_action": (
                        f"{capability}に対応するAdapterのエラーハンドリングを改善する。"
                        f"または代替AIへのフォールバックをConnectorRouterに実装する。"
                    ),
                })
        return candidates

    def _build_audit_summary(self, report: LifecycleReport, logs: list[dict]) -> str:
        stats = self._log.stats()
        success_rate = (
            f"{stats['success'] / stats['total'] * 100:.1f}%"
            if stats.get("total") else "N/A"
        )
        return (
            f"Lifecycle実行: {report.processed_count}件処理 / "
            f"成功率={success_rate} / "
            f"Essence候補={len(report.essence_candidates)}件 / "
            f"Relay候補={len(report.relay_candidates)}件 / "
            f"TODO候補={len(report.todo_candidates)}件"
        )

    def _record_audit_event(self, report: LifecycleReport):
        """監査イベントをMoCKAイベント台帳に記録する"""
        try:
            import db_helper as db
            eid = db.get_next_event_id()
            db.write_event({
                "event_id":        eid,
                "when":            report.run_at,
                "who_actor":       "LifecycleManager",
                "what_type":       "LIFECYCLE_AUDIT",
                "where_component": "gateway/lifecycle_manager.py",
                "why_purpose":     "MoCKA知識ライフサイクル自動管理",
                "how_trigger":     "LifecycleManager.run()",
                "title":           "LIFECYCLE: Connector Log分析完了",
                "short_summary":   report.audit_summary[:200],
                "free_note":       json.dumps({
                    "essence": len(report.essence_candidates),
                    "relay":   len(report.relay_candidates),
                    "todo":    len(report.todo_candidates),
                }, ensure_ascii=False),
            })
        except Exception:
            pass

    def _submit_todo_proposals(self, todo_candidates: list[dict]):
        """TODO候補をProposal Schemaに自動投稿する"""
        if not todo_candidates:
            return
        try:
            from interface.proposal_schema import submit_proposal
            for cand in todo_candidates:
                submit_proposal(
                    category   = "process",
                    summary    = cand["title"][:200],
                    reason     = f"connector_logでcapability={cand['capability']}が{cand['error_count']}回失敗",
                    evidence   = cand["evidence"],
                    confidence = cand["confidence"],
                    recommended_action = cand["recommended_action"],
                    proposer   = "LifecycleManager",
                )
        except Exception:
            pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MoCKA Lifecycle Manager")
    parser.add_argument("--window", type=int, default=100, help="処理対象ログ件数")
    args = parser.parse_args()

    mgr = LifecycleManager()
    report = mgr.run(window=args.window)
    report.print_summary()

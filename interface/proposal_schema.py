#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Proposal Schema (TODO_278縮小) — AI提案フォーマット固定化

PRP（Proposal Record Protocol）: AI提案を検索・監査可能な制度資産として記録する。

7フィールド固定フォーマット:
  proposal_id       — 自動採番 (PRP_YYYYMMDD_NNN)
  category          — 提案カテゴリ (architecture/governance/feature/process/security/other)
  summary           — 提案の一文要約（50文字以内推奨）
  reason            — 提案の根拠・背景
  evidence          — 裏付けデータ・参照イベント・TODO IDなど
  confidence        — 確信度 (0.0-1.0)
  recommended_action — 推奨アクション（承認/却下/保留の場合の具体的行動）

記録先:
  1. MoCKA イベント台帳 (events.db) — mocka_write_eventで記録
  2. data/proposals.jsonl — append-only、検索・監査用

Decision Ledgerとの連携:
  record()が返すproposal_idをDecision Ledger記録時に参照することで
  「なぜその決定に至ったか」の制度的追跡が可能になる。
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

_DATA_DIR       = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
_PROPOSALS_FILE = os.path.join(_DATA_DIR, "proposals.jsonl")

VALID_CATEGORIES = {
    "architecture", "governance", "feature",
    "process", "security", "other",
}


# ── データ構造 ─────────────────────────────────────────────────

@dataclass
class ProposalRecord:
    """PRP固定フォーマット — 7フィールド"""
    proposal_id:        str
    category:           str
    summary:            str
    reason:             str
    evidence:           str
    confidence:         float          # 0.0-1.0
    recommended_action: str
    proposer:           str = ""       # 提案者AI名 (e.g., "ChatGPT", "Claude")
    status:             str = "open"   # open / accepted / rejected / deferred
    created_at:         str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    decision_note:      str = ""       # 承認/却下時の理由（Decision Ledger連携）
    decision_at:        str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_summary_line(self) -> str:
        conf_pct = int(self.confidence * 100)
        return (
            f"[{self.proposal_id}] [{self.category}] {self.summary} "
            f"(conf={conf_pct}%, status={self.status})"
        )


# ── Proposal Schema ────────────────────────────────────────────

class ProposalSchema:
    """
    AI提案の記録・検索・監査インターフェース。

    Usage:
        schema = ProposalSchema()
        prp = schema.record(
            category="governance",
            summary="handshake.pyにtrustレベル昇格フローを追加すべき",
            reason="現状R03はwrite=Falseだが、監査承認後の昇格経路がない",
            evidence="TODO_277 / E20260617_105",
            confidence=0.85,
            recommended_action="TODO追加: Institution Contract v2にtrust昇格APIを定義する",
            proposer="Claude",
        )
        print(prp.proposal_id)  # PRP_20260617_001
    """

    def __init__(self):
        os.makedirs(_DATA_DIR, exist_ok=True)

    def _next_id(self) -> str:
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        prefix = f"PRP_{today}_"
        count = 0
        if os.path.exists(_PROPOSALS_FILE):
            with open(_PROPOSALS_FILE, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        if rec.get("proposal_id", "").startswith(prefix):
                            count += 1
                    except json.JSONDecodeError:
                        continue
        return f"{prefix}{count + 1:03d}"

    def record(self,
               category:           str,
               summary:            str,
               reason:             str,
               evidence:           str,
               confidence:         float,
               recommended_action: str,
               proposer:           str = "") -> ProposalRecord:
        """
        AI提案をPRPフォーマットで記録する。

        Args:
            category:           提案カテゴリ (VALID_CATEGORIES のいずれか)
            summary:            提案の一文要約
            reason:             提案の根拠・背景
            evidence:           裏付けデータ・参照イベント/TODO ID
            confidence:         確信度 0.0-1.0
            recommended_action: 推奨アクション
            proposer:           提案者AI名

        Returns:
            ProposalRecord — proposal_id が採番済みのレコード
        """
        if category not in VALID_CATEGORIES:
            category = "other"
        confidence = max(0.0, min(1.0, float(confidence)))

        prp = ProposalRecord(
            proposal_id        = self._next_id(),
            category           = category,
            summary            = summary[:200],
            reason             = reason[:1000],
            evidence           = evidence[:500],
            confidence         = round(confidence, 2),
            recommended_action = recommended_action[:500],
            proposer           = proposer[:100],
        )

        # 1. proposals.jsonl に append-only 記録
        with open(_PROPOSALS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(prp.to_dict(), ensure_ascii=False) + "\n")

        # 2. MoCKAイベント台帳に記録（MoCKAサーバーが落ちていても例外を伝播しない）
        self._write_to_event_ledger(prp)

        return prp

    def _write_to_event_ledger(self, prp: ProposalRecord):
        """mocka_mcp_server経由でイベント台帳に記録する"""
        try:
            import sys
            mocka_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if mocka_root not in sys.path:
                sys.path.insert(0, mocka_root)
            from event_buffer import get_buffer  # Phase5-1: db.write_event直接禁止 → Gate経由
            get_buffer().push({
                "when":            prp.created_at,
                "who_actor":       prp.proposer or "ProposalSchema",
                "what_type":       "PROPOSAL",
                "where_component": "interface/proposal_schema.py",
                "why_purpose":     "AI提案のPRPフォーマット記録",
                "how_trigger":     "ProposalSchema.record()",
                "title":           f"PROPOSAL [{prp.category}]: {prp.summary[:60]}",
                "short_summary":   (
                    f"{prp.proposal_id} conf={prp.confidence:.0%} "
                    f"action={prp.recommended_action[:80]}"
                ),
                "free_note":       prp.evidence[:200],
            })
        except Exception:
            pass  # イベント台帳への記録失敗はProposal自体をブロックしない

    def decide(self,
               proposal_id:   str,
               decision:      str,
               decision_note: str = "") -> Optional[ProposalRecord]:
        """
        提案に対する決定（承認/却下/保留）を記録する。
        proposals.jsonlの対象レコードを更新版として追記する（append-only）。

        Args:
            proposal_id:   対象のPRP ID
            decision:      "accepted" | "rejected" | "deferred"
            decision_note: 決定理由

        Returns:
            更新後のProposalRecord（見つからなければNone）
        """
        original = self.get(proposal_id)
        if original is None:
            return None

        updated = ProposalRecord(**{**original.to_dict(),
                                    "status":       decision,
                                    "decision_note": decision_note[:500],
                                    "decision_at":  datetime.now(timezone.utc).isoformat()})

        with open(_PROPOSALS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(updated.to_dict(), ensure_ascii=False) + "\n")

        return updated

    def get(self, proposal_id: str) -> Optional[ProposalRecord]:
        """proposal_idで最新レコードを取得する"""
        found = None
        if not os.path.exists(_PROPOSALS_FILE):
            return None
        with open(_PROPOSALS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    if d.get("proposal_id") == proposal_id:
                        found = ProposalRecord(**d)
                except (json.JSONDecodeError, TypeError):
                    continue
        return found

    def list(self,
             category:  Optional[str] = None,
             status:    Optional[str] = None,
             proposer:  Optional[str] = None,
             limit:     int = 50) -> list[ProposalRecord]:
        """
        提案一覧を取得する（最新ステータスのみ）。

        各proposal_idの最終状態（最後の行）のみを返す。
        """
        latest: dict[str, ProposalRecord] = {}
        if not os.path.exists(_PROPOSALS_FILE):
            return []
        with open(_PROPOSALS_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    latest[d["proposal_id"]] = ProposalRecord(**d)
                except (json.JSONDecodeError, TypeError, KeyError):
                    continue

        results = list(latest.values())
        if category:
            results = [r for r in results if r.category == category]
        if status:
            results = [r for r in results if r.status == status]
        if proposer:
            results = [r for r in results if r.proposer == proposer]

        results.sort(key=lambda r: r.created_at, reverse=True)
        return results[:limit]

    def stats(self) -> dict:
        """提案集計（監査用）"""
        all_prp = self.list(limit=10000)
        by_status   = {}
        by_category = {}
        for r in all_prp:
            by_status[r.status]     = by_status.get(r.status, 0) + 1
            by_category[r.category] = by_category.get(r.category, 0) + 1
        return {
            "total":       len(all_prp),
            "by_status":   by_status,
            "by_category": by_category,
        }


# ── 簡易ヘルパー ───────────────────────────────────────────────

_schema = ProposalSchema()


def submit_proposal(category:           str,
                    summary:            str,
                    reason:             str,
                    evidence:           str,
                    confidence:         float,
                    recommended_action: str,
                    proposer:           str = "") -> ProposalRecord:
    """
    シングルトンProposalSchemaへの簡易投稿ヘルパー。

    Usage:
        from interface.proposal_schema import submit_proposal
        prp = submit_proposal(
            category="feature",
            summary="Connector RouterにGenspark対応を追加すべき",
            reason="TODO_270で実装予定のGenspark Connectorが未接続",
            evidence="TODO_270 / TODO_273",
            confidence=0.9,
            recommended_action="TODO_273実装時にai_capability_registryのgenspark adapter_keyを参照する",
            proposer="Claude",
        )
    """
    return _schema.record(
        category=category,
        summary=summary,
        reason=reason,
        evidence=evidence,
        confidence=confidence,
        recommended_action=recommended_action,
        proposer=proposer,
    )


if __name__ == "__main__":
    schema = ProposalSchema()

    print("=== ProposalSchema 動作確認 ===")
    prp = schema.record(
        category="governance",
        summary="Orchestra Context BridgeのGateway依存をオプション化すべき",
        reason="Gateway未起動時にOrchestra全体がブロックされるリスクがある",
        evidence="TODO_258 / E20260617_108",
        confidence=0.80,
        recommended_action="inject_context()のフォールバック動作をデフォルト有効にする（実装済み）",
        proposer="Claude",
    )
    print(f"記録完了: {prp.to_summary_line()}")

    print("\n=== 一覧 ===")
    for r in schema.list():
        print(f"  {r.to_summary_line()}")

    print("\n=== Stats ===")
    import json as _json
    print(_json.dumps(schema.stats(), ensure_ascii=False, indent=2))

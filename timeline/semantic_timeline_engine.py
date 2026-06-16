# timeline/semantic_timeline_engine.py
# MoCKA v1.1 — Semantic Timeline Engine
# 責務: conflict発生の時系列化・意味進化ログ生成・PHI/Personal乖離検出
# 設計原則: 意味を変更しない。記録するだけ。

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ─────────────────────────────────────────────────────────────
# SemanticEvent — 時系列の最小単位
# ─────────────────────────────────────────────────────────────

@dataclass
class SemanticEvent:
    id: str
    timestamp: datetime
    term: str
    phi_value: Any
    personal_value: Any
    conflict_state: str   # ConflictState.value
    phi_decision: str     # PHI-OSの判断ラベル (OBSERVE / TAG / ROUTE / BLOCK)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":             self.id,
            "timestamp":      self.timestamp.isoformat(),
            "term":           self.term,
            "phi_value":      self.phi_value,
            "personal_value": self.personal_value,
            "conflict_state": self.conflict_state,
            "phi_decision":   self.phi_decision,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SemanticEvent":
        return cls(
            id=d["id"],
            timestamp=datetime.fromisoformat(d["timestamp"]),
            term=d["term"],
            phi_value=d.get("phi_value"),
            personal_value=d.get("personal_value"),
            conflict_state=d.get("conflict_state", "NORMAL"),
            phi_decision=d.get("phi_decision", "OBSERVE"),
        )


# ─────────────────────────────────────────────────────────────
# SemanticTimelineEngine
# ─────────────────────────────────────────────────────────────

class SemanticTimelineEngine:
    """
    Bridge → PHI-OS → UI を時系列保存し、意味の「進化ログ」を生成する。
    ストレージはJSONL（1行1イベント）。書き込みのみ。上書きしない。
    """

    DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "semantic_timeline.jsonl"

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self._path = storage_path or self.DEFAULT_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)

    # ── 書き込み ──────────────────────────────────────────────

    def append_event(
        self,
        term: str,
        phi_value: Any,
        personal_value: Any,
        conflict_state: str,
        phi_decision: str,
    ) -> SemanticEvent:
        """Bridge → PHI-OS → UI の1サイクルを時系列保存する。"""
        event = SemanticEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            term=term,
            phi_value=phi_value,
            personal_value=personal_value,
            conflict_state=conflict_state,
            phi_decision=phi_decision,
        )
        with self._path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
        return event

    # ── 読み込み ─────────────────────────────────────────────

    def _load_all(self) -> List[SemanticEvent]:
        if not self._path.exists():
            return []
        events: List[SemanticEvent] = []
        with self._path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(SemanticEvent.from_dict(json.loads(line)))
                    except Exception:
                        pass
        return events

    # ── 単語単位の意味進化取得 ────────────────────────────────

    def get_timeline(self, term: str) -> List[SemanticEvent]:
        """単語単位の意味進化を時系列で返す。"""
        return [e for e in self._load_all() if e.term == term]

    # ── 乖離検出 ──────────────────────────────────────────────

    def detect_drift(self, term: Optional[str] = None, window: int = 20) -> Dict[str, Any]:
        """
        PHI / Personal の乖離増加を検出する。
        直近 window 件のイベントで conflict_state != NORMAL の比率を計算。
        term を指定すると単語絞り込み。
        """
        events = self._load_all()
        if term:
            events = [e for e in events if e.term == term]
        recent = events[-window:] if len(events) > window else events

        if not recent:
            return {"term": term, "window": 0, "drift_rate": 0.0, "status": "NO_DATA"}

        drift_count = sum(1 for e in recent if e.conflict_state != "NORMAL")
        drift_rate = round(drift_count / len(recent), 4)

        status = "STABLE"
        if drift_rate >= 0.6:
            status = "HIGH_DRIFT"
        elif drift_rate >= 0.3:
            status = "MODERATE_DRIFT"

        return {
            "term":       term,
            "window":     len(recent),
            "drift_rate": drift_rate,
            "status":     status,
        }

    # ── サマリ ───────────────────────────────────────────────

    def summary(self) -> Dict[str, Any]:
        """全タームの件数・conflict比率サマリを返す。"""
        events = self._load_all()
        terms: Dict[str, Dict[str, int]] = {}
        for e in events:
            t = terms.setdefault(e.term, {"total": 0, "conflict": 0})
            t["total"] += 1
            if e.conflict_state != "NORMAL":
                t["conflict"] += 1
        return {
            "total_events": len(events),
            "terms": {
                k: {
                    "total":        v["total"],
                    "conflict":     v["conflict"],
                    "conflict_rate": round(v["conflict"] / v["total"], 4) if v["total"] else 0.0,
                }
                for k, v in sorted(terms.items())
            },
        }

    # ── 未来傾向推定（ルールベース） ─────────────────────────

    def predict_next_state(self, window: int = 20) -> Dict[str, Any]:
        """
        未来のconflict傾向をルールベースで推定する。
        学習・書き込みは一切しない。読んで計算するだけ。

        Returns:
            next_drift_probability  : 次windowでのdrift発生確率 (0.0〜1.0)
            expected_conflict_growth: conflict件数の増加傾向 (positive=増加)
            term_instability_ranking: タームを不安定度順にランク付け
        """
        events = self._load_all()
        if not events:
            return {
                "next_drift_probability":   0.0,
                "expected_conflict_growth": 0.0,
                "term_instability_ranking": [],
            }

        # 全体driftを前半/後半で比較して増加傾向を計算
        mid = len(events) // 2
        first_half  = events[:mid] if mid else []
        second_half = events[mid:]

        def drift_rate(evs: List[SemanticEvent]) -> float:
            if not evs:
                return 0.0
            return sum(1 for e in evs if e.conflict_state != "NORMAL") / len(evs)

        r_first  = drift_rate(first_half)
        r_second = drift_rate(second_half)
        growth   = round(r_second - r_first, 4)

        # 次windowのdrift確率: 直近windowの率 + 増加傾向の半分を加算（上限1.0）
        recent      = events[-window:] if len(events) > window else events
        r_recent    = drift_rate(recent)
        next_prob   = round(min(1.0, r_recent + max(0.0, growth * 0.5)), 4)

        # タームごとの不安定度ランキング
        term_stats: Dict[str, Dict[str, Any]] = {}
        for e in events:
            s = term_stats.setdefault(e.term, {"total": 0, "conflict": 0})
            s["total"] += 1
            if e.conflict_state != "NORMAL":
                s["conflict"] += 1

        ranking = sorted(
            [
                {
                    "term":             k,
                    "instability":      round(v["conflict"] / v["total"], 4) if v["total"] else 0.0,
                    "total":            v["total"],
                    "conflict":         v["conflict"],
                }
                for k, v in term_stats.items()
            ],
            key=lambda x: x["instability"],
            reverse=True,
        )

        return {
            "next_drift_probability":   next_prob,
            "expected_conflict_growth": growth,
            "term_instability_ranking": ranking,
        }

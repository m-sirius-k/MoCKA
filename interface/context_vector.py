"""
context_vector.py v1.0
JARVIS Context Reasoning Layer -- Situational Influence Set (S) Extractor

Reconstructs multi-factor influence context from decision/event logs.
S = {H, P, B, T, TC, SD, OC} at time t for state P(X,Y,Z,t,S)
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB_PATH = Path("/home/user/MoCKA/data/mocka_events.db")
DECISION_LEDGER_PATH = Path("/home/user/MoCKA/data/decisions/decision_ledger.jsonl")
TRAJECTORY_PATH = Path("/home/user/MoCKA/data/trajectory.csv")
CONTEXT_VECTOR_PATH = Path("/home/user/MoCKA/data/context_vectors.jsonl")


@dataclass
class SituationalInfluenceSet:
    """Multi-factor influence set at time t"""
    timestamp: str
    H_historical: float      # Historical Context (0-1): past precedent relevance
    P_political: float       # Political Dynamics (0-1): stakeholder consensus
    B_budget: float          # Budget Constraint (0-1): resource availability
    T_timeline: float        # Timeline Pressure (0-1): deadline urgency
    TC_technical: float      # Technical Capability (0-1): implementation feasibility
    SD_social: float         # Social Dynamics (0-1): team cohesion
    OC_organizational: float # Organizational Capacity (0-1): maturity level

    @property
    def S_mean(self) -> float:
        """Mean influence strength across all factors"""
        factors = [self.H_historical, self.P_political, self.B_budget,
                   self.T_timeline, self.TC_technical, self.SD_social,
                   self.OC_organizational]
        return sum(factors) / len(factors) if factors else 0.5

    @property
    def S_variance(self) -> float:
        """Variance indicator: high variance = uncertain context"""
        factors = [self.H_historical, self.P_political, self.B_budget,
                   self.T_timeline, self.TC_technical, self.SD_social,
                   self.OC_organizational]
        mean = self.S_mean
        if not factors:
            return 0.0
        return sum((f - mean) ** 2 for f in factors) / len(factors)


class ContextVectorExtractor:
    """Extract S (Situational Influence Set) from event/decision logs"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.con = None

    def connect(self):
        """Connect to SQLite event store"""
        self.con = sqlite3.connect(str(self.db_path))
        self.con.row_factory = sqlite3.Row

    def disconnect(self):
        if self.con:
            self.con.close()

    def extract_historical_context(self, timestamp: str) -> float:
        """H: Historical Context

        Measures precedent relevance from past decisions.
        Score: 0.0 (no precedent) to 1.0 (highly relevant precedent)
        """
        if not self.con:
            return 0.5

        try:
            # Extract timestamp
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=180)  # 6 months lookback

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as cnt FROM events
                WHERE timestamp >= ? AND timestamp < ?
                AND (what_type = 'decision' OR what_type = 'incident')
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            precedent_count = result[0] if result else 0

            # Normalize: 0-20 precedents = 0.2-1.0
            return min(1.0, 0.2 + (precedent_count / 100.0))
        except Exception as e:
            print(f"[WARN] H extraction error: {e}")
            return 0.5

    def extract_political_dynamics(self, timestamp: str) -> float:
        """P: Political Dynamics

        Measures stakeholder consensus from decision approvals.
        Score: 0.0 (no consensus/veto) to 1.0 (unanimous approval)
        """
        if not self.con:
            return 0.5

        try:
            # Check for recent Human Gate approvals
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=7)  # 1 week lookback

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN who_decision = 'approve' THEN 1 ELSE 0 END) as approvals
                FROM events
                WHERE timestamp >= ? AND timestamp < ?
                AND who_decision IN ('approve', 'veto')
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            total = result[0] if result and result[0] else 1
            approvals = result[1] if result and result[1] else 0

            consensus_ratio = approvals / total if total > 0 else 0.5
            return max(0.0, min(1.0, consensus_ratio))
        except Exception as e:
            print(f"[WARN] P extraction error: {e}")
            return 0.5

    def extract_budget_constraint(self, timestamp: str) -> float:
        """B: Budget Constraint

        Inferred from resource availability signals in logs.
        Score: 0.0 (severe shortage) to 1.0 (ample resources)
        """
        if not self.con:
            return 0.5

        try:
            # Look for budget/resource keywords in recent events
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=30)  # 1 month lookback

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN description LIKE '%budget%' OR description LIKE '%resource%' THEN 1 ELSE 0 END) as constraint_signals
                FROM events
                WHERE timestamp >= ? AND timestamp < ?
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            total = result[0] if result and result[0] else 1
            constraints = result[1] if result and result[1] else 0

            # High constraint signals = low budget score
            constraint_ratio = constraints / total if total > 0 else 0.0
            return max(0.2, 1.0 - (constraint_ratio * 0.5))
        except Exception as e:
            print(f"[WARN] B extraction error: {e}")
            return 0.5

    def extract_timeline_pressure(self, timestamp: str) -> float:
        """T: Timeline Pressure

        Measures urgency from event frequency and deadline signals.
        Score: 0.0 (relaxed) to 1.0 (critical deadline)
        """
        if not self.con:
            return 0.5

        try:
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=14)  # 2 weeks lookback

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as event_count FROM events
                WHERE timestamp >= ? AND timestamp < ?
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            event_count = result[0] if result else 0

            # High event frequency = high pressure
            # Normalize: 0-50 events = 0.2-1.0
            return min(1.0, 0.2 + (event_count / 100.0))
        except Exception as e:
            print(f"[WARN] T extraction error: {e}")
            return 0.5

    def extract_technical_capability(self, timestamp: str) -> float:
        """TC: Technical Capability

        Measures implementation feasibility from system health metrics.
        Score: 0.0 (broken/incapable) to 1.0 (fully capable)
        """
        if not self.con:
            return 0.75

        try:
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=7)

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN what_type = 'error' THEN 1 ELSE 0 END) as errors
                FROM events
                WHERE timestamp >= ? AND timestamp < ?
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            total = result[0] if result and result[0] else 1
            errors = result[1] if result and result[1] else 0

            error_rate = errors / total if total > 0 else 0.0
            return max(0.3, 1.0 - (error_rate * 1.5))
        except Exception as e:
            print(f"[WARN] TC extraction error: {e}")
            return 0.75

    def extract_social_dynamics(self, timestamp: str) -> float:
        """SD: Social Dynamics

        Estimates team cohesion from collaboration signals.
        Score: 0.0 (conflicted) to 1.0 (highly collaborative)
        """
        if not self.con:
            return 0.6

        try:
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=30)

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN what_type = 'collaboration' THEN 1 ELSE 0 END) as collab_events
                FROM events
                WHERE timestamp >= ? AND timestamp < ?
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            total = result[0] if result and result[0] else 1
            collab = result[1] if result and result[1] else 0

            collab_ratio = collab / total if total > 0 else 0.3
            return min(1.0, collab_ratio + 0.3)
        except Exception as e:
            print(f"[WARN] SD extraction error: {e}")
            return 0.6

    def extract_organizational_capacity(self, timestamp: str) -> float:
        """OC: Organizational Capacity

        Inferred from process maturity and completion rates.
        Score: 0.0 (immature) to 1.0 (highly mature)
        """
        if not self.con:
            return 0.7

        try:
            event_date = datetime.fromisoformat(timestamp.split('T')[0])
            lookback_start = event_date - timedelta(days=90)

            cur = self.con.cursor()
            cur.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN what_type = 'completion' THEN 1 ELSE 0 END) as completions
                FROM events
                WHERE timestamp >= ? AND timestamp < ?
            """, (lookback_start.isoformat(), event_date.isoformat()))

            result = cur.fetchone()
            total = result[0] if result and result[0] else 1
            completions = result[1] if result and result[1] else 0

            completion_rate = completions / total if total > 0 else 0.5
            return max(0.4, completion_rate)
        except Exception as e:
            print(f"[WARN] OC extraction error: {e}")
            return 0.7

    def extract_at(self, timestamp: str) -> SituationalInfluenceSet:
        """Extract complete S vector at given timestamp"""
        return SituationalInfluenceSet(
            timestamp=timestamp,
            H_historical=self.extract_historical_context(timestamp),
            P_political=self.extract_political_dynamics(timestamp),
            B_budget=self.extract_budget_constraint(timestamp),
            T_timeline=self.extract_timeline_pressure(timestamp),
            TC_technical=self.extract_technical_capability(timestamp),
            SD_social=self.extract_social_dynamics(timestamp),
            OC_organizational=self.extract_organizational_capacity(timestamp),
        )

    def export_jsonl(self, output_path: Path = CONTEXT_VECTOR_PATH):
        """Export all context vectors to JSONL (append-only)"""
        if not self.con:
            return

        try:
            with open(output_path, 'a', encoding='utf-8') as f:
                now = datetime.utcnow().isoformat()
                s = self.extract_at(now)
                record = {
                    'timestamp': s.timestamp,
                    'S_vector': asdict(s),
                    'S_mean': s.S_mean,
                    'S_variance': s.S_variance,
                    'exported_at': now,
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            print(f"[OK] Context vector exported: {output_path}")
        except Exception as e:
            print(f"[ERROR] Export failed: {e}")


def main():
    """CLI: Extract and display current context vector"""
    extractor = ContextVectorExtractor()
    extractor.connect()

    try:
        now = datetime.utcnow().isoformat()
        s = extractor.extract_at(now)

        print("\n=== Situational Influence Set (S) ===")
        print(f"Timestamp: {s.timestamp}")
        print(f"H (Historical Context):  {s.H_historical:.3f}")
        print(f"P (Political Dynamics):  {s.P_political:.3f}")
        print(f"B (Budget Constraint):   {s.B_budget:.3f}")
        print(f"T (Timeline Pressure):   {s.T_timeline:.3f}")
        print(f"TC (Technical Capability): {s.TC_technical:.3f}")
        print(f"SD (Social Dynamics):    {s.SD_social:.3f}")
        print(f"OC (Organizational Cap): {s.OC_organizational:.3f}")
        print(f"\nS_mean:     {s.S_mean:.3f}")
        print(f"S_variance: {s.S_variance:.3f}")
        print("====================================\n")

        extractor.export_jsonl()
    finally:
        extractor.disconnect()


if __name__ == '__main__':
    main()

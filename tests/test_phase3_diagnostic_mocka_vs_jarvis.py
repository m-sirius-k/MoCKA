#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Diagnostic Test: mocka_search直接 vs JARVIS比較

目的: Contextual Recall の問題がJARVIS側か既存API側か切り分ける
"""

import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from runtime.jarvis.core.engine import JarvisEngine


class DiagnosticSearchTester:
    """mocka_search とJARVIS recall_experience の比較"""

    def __init__(self):
        self.jarvis = JarvisEngine()
        # Decision Ledgerを直接読み込み (mocka_searchの代わり)
        self.decision_ledger_path = Path(_REPO_ROOT) / "data" / "decisions" / "decision_ledger.jsonl"
        self._load_all_decisions()

    def _load_all_decisions(self):
        """全Decisionを読み込む"""
        self.all_decisions = []
        if self.decision_ledger_path.exists():
            with open(self.decision_ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            self.all_decisions.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

    def mock_mocka_search(self, query: str):
        """mocka_search の動作を再現（全文検索）"""
        query_lower = query.lower()
        results = []

        for decision in self.all_decisions:
            # 全フィールドを検索対象
            searchable = (
                (decision.get("title", "") or "").lower() +
                " " +
                (decision.get("context", "") or "").lower() +
                " " +
                (decision.get("decision", "") or "").lower() +
                " " +
                (decision.get("rationale", "") or "").lower()
            )

            # キーワードのいずれかが含まれていれば候補
            if query_lower in searchable:
                results.append(decision)

        return results

    def run_diagnostic(self):
        """診断実行"""
        print("\n" + "="*80)
        print("DIAGNOSTIC: mocka_search vs JARVIS Comparison")
        print("="*80)

        # テスト用intent
        intent = "Decision Ledger"
        print(f"\nTest Intent: {intent}")

        # TEST-1: mocka_search 直接
        print("\n[TEST-1] mocka_search Direct Call")
        print(f"  Query: {intent}")
        direct_results = self.mock_mocka_search(intent)
        print(f"  Hit count: {len(direct_results)}")

        if direct_results:
            print(f"  Sample results:")
            for i, d in enumerate(direct_results[:3]):
                did = d.get("decision_id")
                title = d.get("title", "")[:50].encode('ascii', 'replace').decode('ascii')
                print(f"    [{i+1}] {did}: {title}...")

        # TEST-2: JARVIS recall_experience
        print("\n[TEST-2] JARVIS recall_experience()")
        jarvis_result = self.jarvis.recall_experience(intent)
        print(f"  Status: {jarvis_result['status']}")
        print(f"  Search mode: {jarvis_result.get('search_mode')}")
        print(f"  Matches: {len(jarvis_result.get('matches', []))}")
        print(f"  Gap: {jarvis_result.get('gap')}")

        if jarvis_result['matches']:
            match = jarvis_result['matches'][0]
            print(f"  JARVIS returned:")
            print(f"    decision_id: {match.get('decision_id')}")
            title_safe = match.get('title', '').encode('ascii', 'replace').decode('ascii')[:50]
            print(f"    title: {title_safe}...")

        # TEST-3: 比較
        print("\n[TEST-3] Comparison")
        print("="*80)

        if not direct_results:
            print("  mocka_search: No results")
            direct_ids = []
        else:
            direct_ids = [d.get("decision_id") for d in direct_results]
            print(f"  mocka_search hit IDs: {direct_ids[:5]}")

        if jarvis_result['status'] != 'found':
            jarvis_id = None
            print(f"  JARVIS: No match (status={jarvis_result['status']})")
        else:
            jarvis_id = jarvis_result['matches'][0].get('decision_id')
            print(f"  JARVIS returned ID: {jarvis_id}")

        # 判定
        print("\n[DIAGNOSTIC RESULT]")
        print("="*80)

        if len(direct_results) == 0:
            # Case D: 両方とも結果なし
            print("VERDICT: D - Both mocka_search and JARVIS return no results")
            print("  → Issue may be in test case or source data")
            return 'D'

        elif jarvis_id and jarvis_id in direct_ids:
            # Case B: mocka_search正しい、JARVIS=同じ
            print("VERDICT: B - Contextual recall基盤は既存APIで成立")
            print(f"  JARVIS returned decision in mocka_search candidates")
            print(f"  → Existing API reusable, no JARVIS-specific search needed")
            return 'B'

        elif jarvis_id and jarvis_id not in direct_ids:
            # Case A: mocka_search正しい、JARVIS間違う
            print("VERDICT: A - JARVIS implementation issue detected")
            print(f"  mocka_search found {len(direct_results)} candidates")
            print(f"  JARVIS returned {jarvis_id} (NOT in candidates)")
            print(f"  → JARVIS連携・変換問題")
            return 'A'

        else:
            # mocka_searchあり、JARVISなし
            print("VERDICT: A-variant - JARVIS returns nothing when mocka_search finds results")
            print(f"  → JARVIS implementation issue")
            return 'A'


def main():
    tester = DiagnosticSearchTester()
    verdict = tester.run_diagnostic()

    print(f"\nFinal Diagnosis: {verdict}")
    print("="*80)


if __name__ == "__main__":
    main()

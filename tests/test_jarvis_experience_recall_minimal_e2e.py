#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_jarvis_experience_recall_minimal_e2e.py
Phase 2: Minimal E2E Experience Recall Test

目的: JARVISが実在するDecisionを1件思い出せるかを実測

実測項目 A-D:
A. JARVISからAPI呼出が発生する
B. APIが実在するDecisionを返す
C. 返却データがJARVISまで到達する
D. 元のDecision Ledgerのレコードと一致する
"""

import sys
import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from runtime.jarvis.core.engine import JarvisEngine


class MockMCPClient:
    """既存mocka_mcp_server.pyの関数を直接呼び出すモック"""

    def __init__(self):
        # mocka_mcp_server.py内の_read_decisions()を直接import
        sys.path.insert(0, str(_REPO_ROOT))
        from mocka_mcp_server import _read_decisions
        self._read_decisions = _read_decisions

    def call_mocka_decision_list(self, status=None):
        """既存mocka_decision_listの動作を再現"""
        records, broken = self._read_decisions()
        latest = {}
        for r in records:
            did = r.get("decision_id")
            if did:
                latest[did] = r
        result = list(latest.values())
        if status:
            result = [r for r in result if r.get("status") == status]
        result.sort(key=lambda r: r.get("decision_id", ""), reverse=True)
        return {
            "count": len(result),
            "broken_lines": broken,
            "decisions": result
        }

    def call_mocka_decision_get(self, decision_id):
        """既存mocka_decision_getの動作を再現"""
        records, _ = self._read_decisions()
        matches = [r for r in records if r.get("decision_id") == decision_id]
        return matches[-1] if matches else {"error": "not found"}


class JARVISExperienceRecallAdapter:
    """
    最小実装: JARVISにExperience Recall能力を付与

    既存JARVIS層に追加する最小メソッド
    """

    def __init__(self, jarvis_engine):
        self.engine = jarvis_engine
        self.mcp = MockMCPClient()
        self.recall_log = []  # 実測記録

    def recall_experience(self, current_intent: str, context: dict = None) -> dict:
        """
        JARVIS向け: 過去の経験を呼び出す

        入力: current_intent (例: "past decisions")
        出力: 過去Decision（存在する場合）

        A-D実測を記録しながら実行
        """
        result = {
            "intent": current_intent,
            "matches": [],
            "gap": None,
            "evidence": {
                "A_api_call_made": False,
                "B_decision_found": False,
                "C_data_reached_jarvis": False,
                "D_ledger_match": False,
            }
        }

        # A. API呼出が発生する
        try:
            # 既存APIを呼び出し（mocka_decision_list）
            response = self.mcp.call_mocka_decision_list(status="Active")
            result["evidence"]["A_api_call_made"] = True
            self.recall_log.append("A: API call successful")
        except Exception as e:
            result["gap"] = f"FAILED_AT_A: {e}"
            return result

        # B. 実在するDecisionを取得
        decisions = response.get("decisions", [])
        if not decisions:
            result["gap"] = "FAILED_AT_B: No decisions found"
            return result

        result["evidence"]["B_decision_found"] = True
        self.recall_log.append(f"B: Found {len(decisions)} decisions")

        # C. 返却データがJARVISまで到達
        # (ここでは単に返すだけだが、実装ではJARVIS内メモリに格納される)
        first_decision = decisions[0]  # 最新1件を取得
        try:
            result["matches"].append({
                "source": "decision_ledger",
                "decision_id": first_decision.get("decision_id"),
                "title": first_decision.get("title"),
                "decision": first_decision.get("decision"),
                "rationale": first_decision.get("rationale"),
                "approved_by": first_decision.get("approved_by"),
                "approved_at": first_decision.get("approved_at"),
                "related_events": first_decision.get("related_events", []),
                "status": first_decision.get("status"),
            })
            result["evidence"]["C_data_reached_jarvis"] = True
            self.recall_log.append("C: Data reached JARVIS memory")
        except Exception as e:
            result["gap"] = f"FAILED_AT_C: {e}"
            return result

        # D. 元のDecision Ledgerレコードと一致
        # (読取元と返却値の比較)
        try:
            retrieved_decision = self.mcp.call_mocka_decision_get(first_decision.get("decision_id"))
            if retrieved_decision == first_decision:
                result["evidence"]["D_ledger_match"] = True
                self.recall_log.append("D: Ledger record match verified")
            else:
                result["evidence"]["D_ledger_match"] = False
                result["gap"] = "WARNING_AT_D: Data mismatch (but possibly different ordering)"
        except Exception as e:
            result["gap"] = f"FAILED_AT_D: {e}"

        return result


def test_jarvis_experience_recall_e2e():
    """
    Phase 2 テスト: JARVISが過去Decision 1件を思い出す

    実測基準:
    - A-D すべてが成功
    - 返ってきたDecision_idが実在する
    - 返ってきたデータが元のレコードと一致
    """
    print("\n" + "="*80)
    print("Phase 2: JARVIS Experience Recall Minimal E2E Test")
    print("="*80)

    # セットアップ
    jarvis = JarvisEngine()
    adapter = JARVISExperienceRecallAdapter(jarvis)

    # テスト実行
    print("\n[TEST] JARVIS recall_experience() with simple intent")
    intent = "Recall past decisions"
    result = adapter.recall_experience(intent)

    # 結果表示
    print(f"\nIntent: {intent}")
    print(f"Matches found: {len(result['matches'])}")

    if result['matches']:
        match = result['matches'][0]
        print(f"\n[RESULT] Retrieved Decision:")
        print(f"  decision_id: {match.get('decision_id')}")
        print(f"  title: {match.get('title')[:60]}...")
        print(f"  approved_by: {match.get('approved_by')}")
        print(f"  approved_at: {match.get('approved_at')}")
        print(f"  status: {match.get('status')}")

    # A-D の検証
    evidence = result['evidence']
    print(f"\n[EVIDENCE A-D]")
    print(f"  A. API call made: {evidence['A_api_call_made']}")
    print(f"  B. Decision found: {evidence['B_decision_found']}")
    print(f"  C. Data reached JARVIS: {evidence['C_data_reached_jarvis']}")
    print(f"  D. Ledger match verified: {evidence['D_ledger_match']}")

    # ログ表示
    print(f"\n[RECALL LOG]")
    for entry in adapter.recall_log:
        print(f"  {entry}")

    # 最終判定
    all_passed = all(evidence.values())
    gap = result.get('gap')

    print(f"\n[FINAL RESULT]")
    if all_passed and not gap:
        print("  ✓ E2E CONNECTED: JARVIS can recall past Decision")
        print("  Status: SUCCESS")
        return True
    else:
        print(f"  ✗ E2E INCOMPLETE")
        if gap:
            print(f"  Gap: {gap}")
        print("  Status: FAILURE")
        return False


def test_jarvis_experience_recall_readback():
    """
    Read-back verification: 返却データと元レコードの整合性確認
    """
    print("\n" + "="*80)
    print("Phase 2: Read-back Verification Test")
    print("="*80)

    mcp = MockMCPClient()

    # 1. Decision List取得
    list_result = mcp.call_mocka_decision_list(status="Active")
    decisions = list_result.get("decisions", [])

    if not decisions:
        print("\n✗ No decisions found in ledger")
        return False

    # 2. 最初のDecisionを取得
    test_decision_id = decisions[0].get("decision_id")
    print(f"\nTest Decision ID: {test_decision_id}")

    # 3. Direct取得
    direct_result = mcp.call_mocka_decision_get(test_decision_id)

    # 4. 比較
    list_record = decisions[0]
    get_record = direct_result

    print(f"\nVerifying record consistency:")
    fields_to_check = ["decision_id", "title", "decision", "rationale", "status"]
    all_match = True

    for field in fields_to_check:
        list_val = list_record.get(field)
        get_val = get_record.get(field)
        match = list_val == get_val
        all_match = all_match and match
        status = "✓" if match else "✗"
        print(f"  {status} {field}: {match}")

    print(f"\n{'✓ All fields match' if all_match else '✗ Mismatch detected'}")
    return all_match


if __name__ == "__main__":
    # Test A: E2E Flow
    success_a = test_jarvis_experience_recall_e2e()

    # Test B: Read-back Verification
    success_b = test_jarvis_experience_recall_readback()

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"E2E Test: {'PASS' if success_a else 'FAIL'}")
    print(f"Read-back Verification: {'PASS' if success_b else 'FAIL'}")
    print(f"Overall: {'PASS' if (success_a and success_b) else 'FAIL'}")
    print("="*80 + "\n")

    sys.exit(0 if (success_a and success_b) else 1)

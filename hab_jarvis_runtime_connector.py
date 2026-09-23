"""
hab_jarvis_runtime_connector.py
HAB/JARVIS → Human Gate → Authorization State → Runtime /approve Connection
2026-09-22

目的:
既存の Human Gate / HG-AS-01 / Authorization State を利用して
Runtime /approve へ接続する最小実装。

フロー:
1. HAB/JARVIS decision を受け取る
2. Human Gate approve() で HG-AS-01 検証・承認
3. authorization_id を取得
4. Runtime /approve へ渡す
5. Runtime authorization 確認
6. Execution 実行

制約:
- 既存 Human Gate API を変更しない
- 既存 HG-AS-01 / Authorization Bridge を変更しない
- 新しい governance rule は追加しない
- retry / rollback / compensation 不追加
- spec_id は Sandbox 用最小値のみ生成（本番仕様ではない）
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# DB access
import sqlite3

REPO_ROOT = Path(__file__).resolve().parent
DB_PATH = str(REPO_ROOT / 'data' / 'mocka_events.db')

# Endpoints (Sandbox)
HUMAN_GATE_URL = "http://localhost:5001"  # phi_os/human_gate.py Flask app
RUNTIME_APPROVAL_URL = "http://localhost:5000/runtime/approve"  # Placeholder for Runtime /approve


class HABJARVISRuntimeConnector:
    """
    最小接続実装。
    既存の器を一本通すだけ。
    """

    def __init__(self):
        self.db_path = DB_PATH

    def approve_with_human_gate(self, decision_id: str, actor: str, scope: list,
                                 authority_role: str, evidence_ref=None) -> dict:
        """
        Step 1: Human Gate approve() を呼ぶ

        Args:
            decision_id: Decision record ID (既存値)
            actor: Human identity (e.g., 'kimura_phd')
            scope: Approval scope (e.g., ['component_A'])
            authority_role: Authority role (e.g., 'HG_AUTHORITY_HOLDER_01')
            evidence_ref: Optional evidence references

        Returns:
            {
                "success": bool,
                "authorization_id": str or None,
                "event": dict (full Human Gate event),
                "error": str or None
            }
        """
        # Human Gate request payload (HG-AS-01 required fields)
        payload = {
            "request_id": f"HAB_JARVIS_{decision_id}",
            "actor": actor,
            "scope": scope,
            "authority_role": authority_role,
            "decision_id": decision_id,
        }
        if evidence_ref:
            payload["evidence_ref"] = evidence_ref

        try:
            # POST to existing Human Gate endpoint
            response = requests.post(
                f"{HUMAN_GATE_URL}/api/human_gate/approve",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                event = result.get("event", {})

                # Extract authorization_id from response
                authorization_id = event.get("authorization_id")
                authorization_state_issued = event.get("authorization_state_issued", False)

                return {
                    "success": True,
                    "authorization_id": authorization_id,
                    "event": event,
                    "authorization_state_issued": authorization_state_issued,
                    "error": None
                }
            else:
                error_detail = response.json().get("reason", response.text)
                return {
                    "success": False,
                    "authorization_id": None,
                    "event": None,
                    "error": f"Human Gate returned {response.status_code}: {error_detail}"
                }

        except requests.ConnectionError as e:
            return {
                "success": False,
                "authorization_id": None,
                "event": None,
                "error": f"Connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "authorization_id": None,
                "event": None,
                "error": f"Unexpected error: {str(e)}"
            }

    def verify_authorization_state(self, authorization_id: str) -> dict:
        """
        Step 2: Authorization state を verify する

        Args:
            authorization_id: UUID from Human Gate response

        Returns:
            {
                "exists": bool,
                "status": str or None ("APPROVED", "UNKNOWN", etc.),
                "subject": str or None,
                "scope": list or None,
                "granted_by": str or None,
                "record": dict (full authorization_state record) or None
            }
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

            row = conn.execute(
                "SELECT * FROM authorization_state WHERE authorization_id = ?",
                (authorization_id,)
            ).fetchone()

            if row:
                record = dict(row)
                scope = json.loads(record.get("scope", "[]")) if record.get("scope") else []
                return {
                    "exists": True,
                    "status": record.get("status"),
                    "subject": record.get("subject"),
                    "scope": scope,
                    "granted_by": record.get("granted_by"),
                    "record": record
                }
            else:
                return {
                    "exists": False,
                    "status": None,
                    "subject": None,
                    "scope": None,
                    "granted_by": None,
                    "record": None
                }

        except Exception as e:
            return {
                "exists": False,
                "status": None,
                "subject": None,
                "scope": None,
                "granted_by": None,
                "record": None,
                "error": f"DB query error: {str(e)}"
            }
        finally:
            conn.close()

    def call_runtime_approve(self, authorization_id: str, decision_id: str,
                            human_identity: str, spec_id: str = None) -> dict:
        """
        Step 3: Runtime /approve を呼ぶ

        Args:
            authorization_id: UUID from authorization_state
            decision_id: Decision record ID
            human_identity: Actor who approved
            spec_id: (Optional) Specification ID; generated for Sandbox if not provided

        Returns:
            {
                "success": bool,
                "runtime_status": str or None,
                "permit": bool or None,
                "error": str or None
            }
        """
        # Generate minimal spec_id for Sandbox if not provided
        if not spec_id:
            spec_id = f"SPEC_SANDBOX_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        payload = {
            "authorization_id": authorization_id,
            "decision_record_id": decision_id,
            "human_identity": human_identity,
            "confirmed": True,
            "spec_id": spec_id,
        }

        try:
            response = requests.post(
                RUNTIME_APPROVAL_URL,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "runtime_status": result.get("status"),
                    "permit": result.get("permit", False),
                    "response": result,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "runtime_status": None,
                    "permit": False,
                    "error": f"Runtime returned {response.status_code}: {response.text}"
                }

        except requests.ConnectionError as e:
            return {
                "success": False,
                "runtime_status": None,
                "permit": False,
                "error": f"Runtime connection error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "runtime_status": None,
                "permit": False,
                "error": f"Unexpected error: {str(e)}"
            }

    def execute_decision_flow(self, decision_id: str, actor: str, scope: list,
                              authority_role: str) -> dict:
        """
        Complete flow: Human Gate → Authorization → Runtime

        Returns:
            {
                "decision_id": str,
                "step_1_hg_approve": dict,
                "step_2_auth_verify": dict,
                "step_3_runtime_approve": dict,
                "overall_success": bool,
                "authorization_id": str or None
            }
        """
        result = {
            "decision_id": decision_id,
            "step_1_hg_approve": None,
            "step_2_auth_verify": None,
            "step_3_runtime_approve": None,
            "overall_success": False,
            "authorization_id": None
        }

        # Step 1: Human Gate
        hg_result = self.approve_with_human_gate(decision_id, actor, scope, authority_role)
        result["step_1_hg_approve"] = hg_result

        if not hg_result["success"]:
            result["error"] = f"Step 1 failed: {hg_result['error']}"
            return result

        authorization_id = hg_result.get("authorization_id")
        if not authorization_id:
            result["error"] = "Step 1: No authorization_id returned"
            return result

        result["authorization_id"] = authorization_id

        # Step 2: Verify Authorization State
        auth_result = self.verify_authorization_state(authorization_id)
        result["step_2_auth_verify"] = auth_result

        if not auth_result.get("exists"):
            result["error"] = f"Step 2 failed: Authorization state not found"
            return result

        if auth_result.get("status") != "APPROVED":
            result["error"] = f"Step 2 failed: Authorization status is {auth_result.get('status')}, not APPROVED"
            return result

        # Step 3: Call Runtime /approve
        runtime_result = self.call_runtime_approve(
            authorization_id=authorization_id,
            decision_id=decision_id,
            human_identity=actor
        )
        result["step_3_runtime_approve"] = runtime_result

        if not runtime_result.get("success"):
            result["error"] = f"Step 3 failed: {runtime_result['error']}"
            return result

        if not runtime_result.get("permit"):
            result["error"] = f"Step 3 failed: Runtime did not grant permit"
            return result

        result["overall_success"] = True
        return result


def main():
    """
    Sandbox test execution
    """
    print("=" * 70)
    print("HAB/JARVIS → Runtime Connection Test")
    print("=" * 70)
    print()

    connector = HABJARVISRuntimeConnector()

    # Test parameters (Sandbox values)
    test_decision_id = "DC_20260922_TEST_001"
    test_actor = "kimura_phd"
    test_scope = ["component_A", "component_J"]
    test_authority_role = "HG_AUTHORITY_HOLDER_01"

    print(f"Decision ID: {test_decision_id}")
    print(f"Actor: {test_actor}")
    print(f"Scope: {test_scope}")
    print(f"Authority Role: {test_authority_role}")
    print()

    result = connector.execute_decision_flow(
        decision_id=test_decision_id,
        actor=test_actor,
        scope=test_scope,
        authority_role=test_authority_role
    )

    print("RESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    print()

    if result["overall_success"]:
        print("✓ FLOW SUCCESSFUL")
        print(f"  Authorization ID: {result['authorization_id']}")
        print(f"  Runtime permit granted: {result['step_3_runtime_approve'].get('permit')}")
    else:
        print("✗ FLOW FAILED")
        print(f"  Error: {result.get('error')}")
        if result["step_1_hg_approve"].get("error"):
            print(f"  Step 1: {result['step_1_hg_approve']['error']}")
        if result["step_2_auth_verify"].get("error"):
            print(f"  Step 2: {result['step_2_auth_verify']['error']}")
        if result["step_3_runtime_approve"].get("error"):
            print(f"  Step 3: {result['step_3_runtime_approve']['error']}")

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()

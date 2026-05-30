"""
SCENARIO-13: Evidence Ledger 試験
証明: 「なぜその判断をしたか」を追跡できる構造
"""
import os
import time


def run(db_path: str) -> dict:
    os.environ["VASAI_DB_PATH"] = db_path
    # Evidence Ledgerは別DBを使用
    import tempfile
    ev_db = tempfile.mktemp(suffix="_ev.db")
    os.environ["VASAI_EV_DB_PATH"] = ev_db

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from core import event_store
        from core.evidence_ledger import EvidenceLedger

        ledger = EvidenceLedger()

        # ── Step1: Decision記録 + 根拠4種登録 ────────────
        # 「サーバA更新」という判断を記録
        event_id = event_store.append(
            who_actor="CTO",
            what_type="SERVER_UPDATE_DECISION",
            where_component="infrastructure/server_A",
            why_purpose="サーバAの更新実施判断",
            content={
                "server": "server_A",
                "decision": "UPDATE_APPROVED",
                "risk_level": "HIGH",
            },
            stage="DECISION",
        )
        decision_id = f"DEC_{event_id}"

        # FACT: 事実根拠
        ev_fact = ledger.add_evidence(
            event_id=event_id,
            decision_id=decision_id,
            evidence_type="FACT",
            content={
                "description": "過去30日で障害率3.2倍上昇（2.1% → 6.7%）",
                "metric": "failure_rate",
                "baseline": 0.021,
                "current": 0.067,
                "trend": "3.2x_increase_30days",
            },
            source="monitoring_system/grafana",
            confidence=0.98,
        )

        # ASSUMPTION: 前提
        ev_assump = ledger.add_evidence(
            event_id=event_id,
            decision_id=decision_id,
            evidence_type="ASSUMPTION",
            content={
                "description": "更新により障害率80%改善見込み（ベンダー試験結果より）",
                "basis": "vendor_test_report_2026_Q1",
                "expected_improvement": 0.80,
            },
            source="vendor/support_ticket_12345",
            confidence=0.75,
        )

        # CONSTRAINT: 制約
        ev_constraint = ledger.add_evidence(
            event_id=event_id,
            decision_id=decision_id,
            evidence_type="CONSTRAINT",
            content={
                "description": "月次メンテナンス窓（毎月第2日曜 02:00-06:00）以外での実施不可",
                "window": "every_2nd_sunday_0200_0600",
                "sla_impact": "4hours_max_downtime",
            },
            source="operations/sla_agreement_v3",
            confidence=1.0,
        )

        # INTENT: 意図
        ev_intent = ledger.add_evidence(
            event_id=event_id,
            decision_id=decision_id,
            evidence_type="INTENT",
            content={
                "description": "年間SLA 99.9%維持（年間8.76時間ダウンタイム上限）",
                "target_sla": 0.999,
                "current_sla": 0.9931,
                "goal": "restore_sla_compliance",
            },
            source="management/annual_objectives_2026",
            confidence=1.0,
        )

        ev_ids = [ev_fact, ev_assump, ev_constraint, ev_intent]
        all_recorded = all(e.startswith("EV") for e in ev_ids)
        steps.append(("Step1: 根拠4種登録",
                      all_recorded,
                      f"FACT/ASSUMPTION/CONSTRAINT/INTENT → IDs: {[e[:12] for e in ev_ids]}"))
        details["evidence_ids"] = ev_ids
        details["event_id"] = event_id
        details["decision_id"] = decision_id

        # ── Step2: Decision→Result全追跡 ─────────────────
        t0 = time.time()
        chain = ledger.get_decision_chain(decision_id)
        t_chain = time.time() - t0

        chain_ok = (
            chain["total_evidence"] == 4 and
            len(chain["facts"]) == 1 and
            len(chain["assumptions"]) == 1 and
            len(chain["constraints"]) == 1 and
            len(chain["intents"]) == 1
        )
        steps.append(("Step2: Decision→Result全追跡",
                      chain_ok,
                      f"total={chain['total_evidence']} "
                      f"FACT={len(chain['facts'])} ASSUMPTION={len(chain['assumptions'])} "
                      f"CONSTRAINT={len(chain['constraints'])} INTENT={len(chain['intents'])} "
                      f"時間={t_chain*1000:.1f}ms"))
        details["chain"] = {
            "total": chain["total_evidence"],
            "by_type": {k: len(v) for k, v in chain["by_type"].items()},
        }

        # ── Step3: 自然言語説明生成 ───────────────────────
        t0 = time.time()
        explanation = ledger.why_was_this_decided(event_id)
        t_explain = time.time() - t0

        has_explanation = (
            len(explanation) > 50 and
            "事実" in explanation and
            "前提" in explanation and
            "制約" in explanation and
            "意図" in explanation
        )
        steps.append(("Step3: 自然言語説明生成",
                      has_explanation,
                      f"{len(explanation)}文字 時間={t_explain*1000:.1f}ms"))
        details["explanation_length"] = len(explanation)
        details["explanation_preview"] = explanation[:120] + "..."

        # ── Step4: verify_chain() → VALID ────────────────
        t0 = time.time()
        chain_valid = ledger.verify_chain()
        t_verify = time.time() - t0
        steps.append(("Step4: Evidence verify_chain",
                      chain_valid,
                      f"verify_chain()={chain_valid} 時間={t_verify*1000:.1f}ms"))
        details["chain_valid"] = chain_valid

        # ── Step5: 30秒以内の根拠到達（SCENARIO-10より深い）─
        t0 = time.time()
        # 深い追跡: event_id → evidence → chain → explanation → verify
        ev_list = ledger.list_by_event(event_id)
        chain2 = ledger.get_decision_chain(decision_id)
        explanation2 = ledger.why_was_this_decided(event_id)
        verify2 = ledger.verify_chain()
        t_total = time.time() - t0

        deep_trace_ok = (
            len(ev_list) == 4 and
            chain2["total_evidence"] == 4 and
            verify2 and
            t_total < 30.0
        )
        steps.append(("Step5: 30秒以内 深層根拠追跡",
                      deep_trace_ok,
                      f"evidence={len(ev_list)}件 chain={chain2['total_evidence']}件 "
                      f"verify={verify2} 合計={t_total:.3f}秒（30秒以内）"))
        details["deep_trace_sec"] = round(t_total, 3)

        # ── Step6: confidence分布確認 ────────────────────
        confs = [r["confidence"] for r in ev_list]
        conf_ok = all(0.0 <= c <= 1.0 for c in confs)
        steps.append(("Step6: confidence 0.0〜1.0範囲",
                      conf_ok,
                      f"confidences={[round(c,2) for c in confs]}"))
        details["confidences"] = [round(c, 2) for c in confs]

        # クリーンアップ
        try:
            import pathlib
            pathlib.Path(ev_db).unlink(missing_ok=True)
        except Exception:
            pass

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
        }

    except Exception as e:
        import traceback
        try:
            import pathlib
            pathlib.Path(ev_db).unlink(missing_ok=True)
        except Exception:
            pass
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }

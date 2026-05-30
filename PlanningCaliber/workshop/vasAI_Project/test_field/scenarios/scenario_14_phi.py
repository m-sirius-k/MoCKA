"""
SCENARIO-14: PHI Layer + MoCKA Bridge 試験
証明: 「判断の遺伝子」の記録・継承・還流
WHY→REASON→EVIDENCE→DECISION→OUTCOME の全チェーン
"""
import os
import tempfile
import time


def run(db_path: str) -> dict:
    os.environ["VASAI_DB_PATH"] = db_path

    phi_db = tempfile.mktemp(suffix="_phi.db")
    ev_db = tempfile.mktemp(suffix="_ev.db")
    os.environ["VASAI_PHI_DB_PATH"] = phi_db
    os.environ["VASAI_EV_DB_PATH"] = ev_db

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from core import event_store
        from core.phi_layer import PHILayer
        from core.evidence_ledger import EvidenceLedger
        from core.mocka_bridge import MoCKABridge

        phi = PHILayer()
        ledger = EvidenceLedger()
        bridge = MoCKABridge(phi)

        # ── Step1: Decision記録 + Evidence登録 + DNA記録 ──
        # ベースとなるDecisionをevent_storeに記録
        event_id = event_store.append(
            who_actor="CTO",
            what_type="INFRA_MIGRATION_DECISION",
            where_component="infrastructure/server_cluster",
            why_purpose="サーバ移設判断（コスト削減・性能向上）",
            content={"decision": "MIGRATE_APPROVED", "budget_yen": 500000,
                     "risk_level": "HIGH"},
            stage="DECISION",
        )
        decision_id = f"DEC_{event_id}"

        # Evidence Ledger に根拠記録
        ev_fact = ledger.add_evidence(
            event_id=event_id, decision_id=decision_id,
            evidence_type="FACT",
            content={"description": "過去30日障害率3.2倍増（2.1%→6.7%）",
                     "source_metric": "monitoring/grafana"},
            source="grafana_dashboard", confidence=0.98,
        )
        ev_intent = ledger.add_evidence(
            event_id=event_id, decision_id=decision_id,
            evidence_type="INTENT",
            content={"description": "SLA 99.9%維持（年間8.76時間以内）"},
            source="sla_agreement_v3", confidence=1.0,
        )

        # PHI DNA 記録
        dna_id = phi.record_dna(
            decision_id=decision_id,
            why="競合他社のシステム障害で顧客離れが加速。自社も同リスクあり。",
            reason="サーバ負荷が過去30日で3.2倍増加。SLA違反リスク高。移設によりコスト30%削減見込み。",
            evidence_ids=[ev_fact, ev_intent],
            decision_summary="サーバA移設を承認（予算50万円・第2日曜実施）",
        )

        dna_recorded = dna_id.startswith("PHI")
        steps.append(("Step1: WHY→REASON→EVIDENCE→DECISION記録",
                      dna_recorded,
                      f"dna_id={dna_id} evidence_ids=[{ev_fact[:8]}, {ev_intent[:8]}]"))
        details["dna_id"] = dna_id

        # ── Step2: 全チェーン取得 ─────────────────────────
        t0 = time.time()
        full = phi.get_full_dna(decision_id)
        t_chain = time.time() - t0

        chain_ok = (full["found"] and full["dna_count"] >= 1 and
                    full["dna"][0]["why"] != "" and
                    full["dna"][0]["reason"] != "")
        steps.append(("Step2: WHY→DECISION 全チェーン取得",
                      chain_ok,
                      f"dna_count={full['dna_count']} "
                      f"stages={full['chain_stages']} 時間={t_chain*1000:.1f}ms"))
        details["chain"] = {"found": full["found"], "dna_count": full["dna_count"]}

        # ── Step3: OUTCOME 事後記録 ───────────────────────
        phi.record_outcome(dna_id, "障害率-74%（3ヶ月後実測）。SLA 99.93%達成。コスト削減28%実現。")
        full_with_outcome = phi.get_full_dna(decision_id)
        has_outcome = bool(full_with_outcome["dna"][0]["outcome"])
        steps.append(("Step3: OUTCOME 事後記録",
                      has_outcome,
                      f"outcome='{full_with_outcome['dna'][0]['outcome'][:40]}...'"))

        # ── Step4: 自然言語説明生成 ───────────────────────
        t0 = time.time()
        explanation = phi.explain_decision(decision_id)
        t_explain = time.time() - t0
        has_all_stages = all(
            kw in explanation for kw in ["背景・文脈", "推論プロセス", "判断", "根拠", "結果"]
        )
        steps.append(("Step4: 自然言語説明（5要素）",
                      has_all_stages,
                      f"{len(explanation)}文字 {t_explain*1000:.1f}ms "
                      f"5要素={'全有' if has_all_stages else '不足'}"))
        details["explanation_len"] = len(explanation)
        details["explanation_preview"] = explanation[:100]

        # ── Step5: MoCKA essence エクスポート ─────────────
        essence = phi.export_to_essence(dna_id)
        essence_ok = (
            "PHILOSOPHY" in essence and
            "OPERATION" in essence and
            essence["PHILOSOPHY"].get("why") != "" and
            essence["OPERATION"].get("decision") != ""
        )
        steps.append(("Step5: MoCKA essence エクスポート",
                      essence_ok,
                      f"PHILOSOPHY={bool(essence.get('PHILOSOPHY'))} "
                      f"OPERATION={bool(essence.get('OPERATION'))} "
                      f"INCIDENT={bool(essence.get('INCIDENT'))}"))
        details["essence"] = {
            "axes": list(essence.keys()),
            "philosophy_why": essence.get("PHILOSOPHY", {}).get("why", "")[:40],
        }

        # ── Step6: MoCKA Bridge 全軸還流 ─────────────────
        export_result = bridge.full_export(dna_id)
        bridge_ok = (export_result["philosophy"] and export_result["operation"])
        steps.append(("Step6: MoCKA Bridge 全軸還流",
                      bridge_ok,
                      f"philosophy={export_result['philosophy']} "
                      f"operation={export_result['operation']} "
                      f"incident={export_result['incident']}"))
        details["bridge"] = export_result

        # ── Step7: PHI verify_chain ───────────────────────
        chain_valid = phi.verify_chain()
        steps.append(("Step7: PHI verify_chain",
                      chain_valid,
                      f"verify_chain()={chain_valid}"))
        details["phi_chain_valid"] = chain_valid

        # ── Step8: 還流状態確認 ───────────────────────────
        sync = bridge.verify_sync()
        steps.append(("Step8: MoCKA Bridge 還流状態確認",
                      sync["total_dna"] >= 1,
                      f"total_dna={sync['total_dna']} exported={sync['exported']} "
                      f"pending={sync['pending']}"))

        # ── Step9: Evidence + PHI 複合チェーン ────────────
        ev_list = ledger.list_by_event(event_id)
        ev_chain = ledger.get_decision_chain(decision_id)
        phi_dna = phi.get_full_dna(decision_id)
        combined_ok = (
            len(ev_list) == 2 and
            ev_chain["total_evidence"] == 2 and
            phi_dna["dna_count"] == 1 and
            phi_dna["dna"][0]["has_outcome"]
        )
        steps.append(("Step9: Evidence + PHI 複合チェーン",
                      combined_ok,
                      f"evidence={len(ev_list)}件 phi_dna={phi_dna['dna_count']}件 "
                      f"outcome={'有' if phi_dna['dna'][0]['has_outcome'] else '無'}"))
        details["combined_chain"] = {
            "evidence_count": len(ev_list),
            "phi_dna_count": phi_dna["dna_count"],
            "has_outcome": phi_dna["dna"][0]["has_outcome"],
        }

        # クリーンアップ
        for f in [phi_db, ev_db]:
            try:
                import pathlib; pathlib.Path(f).unlink(missing_ok=True)
            except Exception: pass

        all_pass = all(s[1] for s in steps)
        return {"success": all_pass, "steps": steps, "details": details}

    except Exception as e:
        import traceback
        for f in [phi_db, ev_db]:
            try:
                import pathlib; pathlib.Path(f).unlink(missing_ok=True)
            except Exception: pass
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
        }

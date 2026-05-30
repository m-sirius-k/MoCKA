"""
SCENARIO-08: マルチ部門運用試験
証明: 組織横断で履歴追跡・監査が可能
"""


DEPARTMENTS = {
    "HR":          {"what_types": ["HIRING_DECISION", "HR_APPROVAL", "PERSONNEL_CHANGE"],
                    "caliber_id": "hr_dept"},
    "Sales":       {"what_types": ["DEAL_DECISION", "CUSTOMER_DECISION", "QUOTE_APPROVAL"],
                    "caliber_id": "sales_dept"},
    "Quality":     {"what_types": ["QUALITY_INCIDENT", "CORRECTIVE_ACTION", "QA_APPROVAL"],
                    "caliber_id": "quality_dept"},
    "Development": {"what_types": ["TECH_DECISION", "RELEASE_APPROVAL", "CODE_REVIEW"],
                    "caliber_id": "dev_dept"},
}

EVENTS_PER_DEPT = 25


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    import movement.mocka_movement as mm
    mm._shadow_listeners.clear()

    steps = []
    details = {}

    try:
        from core import event_store, governance
        from core.models import DecisionStatus

        # 1. 4部門が同一vasAIを同時利用（逐次シミュレーション）
        dept_event_ids: dict[str, list[str]] = {d: [] for d in DEPARTMENTS}

        for dept, cfg in DEPARTMENTS.items():
            for i in range(EVENTS_PER_DEPT):
                wt = cfg["what_types"][i % len(cfg["what_types"])]
                eid = event_store.append(
                    who_actor=f"{dept}_User_{i%3}",
                    what_type=wt,
                    where_component=f"dept/{dept.lower()}",
                    why_purpose=f"{dept}の業務処理 {i+1}件目",
                    content={"dept": dept, "seq": i, "type": wt,
                             "risk_level": "HIGH" if i % 10 == 0 else "NORMAL"},
                    caliber_id=cfg["caliber_id"],
                    stage="RECORD",
                )
                dept_event_ids[dept].append(eid)

        total_recorded = sum(len(v) for v in dept_event_ids.values())
        steps.append(("4部門独立稼働",
                      total_recorded == len(DEPARTMENTS) * EVENTS_PER_DEPT,
                      f"各部門{EVENTS_PER_DEPT}件 合計{total_recorded}件記録"))
        details["dept_event_counts"] = {d: len(ids) for d, ids in dept_event_ids.items()}

        # 2. 部門別フィルタリング（HR記録だけ抽出・混在ゼロ確認）
        hr_events = event_store.list_events(limit=1000, caliber_id="hr_dept")
        hr_contaminated = [e for e in hr_events if e["caliber_id"] != "hr_dept"]
        dept_isolated = len(hr_events) == EVENTS_PER_DEPT and len(hr_contaminated) == 0
        steps.append(("部門別分離（混在0件）",
                      dept_isolated,
                      f"HR取得={len(hr_events)}件 混在={len(hr_contaminated)}件"))
        details["hr_events"] = len(hr_events)
        details["contamination"] = len(hr_contaminated)

        # 3. 部門横断検索（全部門のDecision/Approval系を追跡）
        cross_events = []
        for dept, cfg in DEPARTMENTS.items():
            for wt in cfg["what_types"]:
                evs = event_store.list_events(limit=100, what_type=wt)
                cross_events.extend(evs)
        cross_ok = len(cross_events) >= len(DEPARTMENTS) * 2
        steps.append(("部門横断追跡",
                      cross_ok,
                      f"横断追跡={len(cross_events)}件（全部門Decision/Approval）"))
        details["cross_events"] = len(cross_events)

        # 4. 部門間承認フロー（HR→Development承認依頼シミュレーション）
        # HRがDevelopmentへの承認依頼を作成
        hr_to_dev_eid = event_store.append(
            who_actor="HR_Manager",
            what_type="INCIDENT",  # HIGHリスク → Human Gate
            where_component="cross_dept/hr_to_dev",
            why_purpose="HR→Dev クロス部門承認依頼",
            content={"from_dept": "HR", "to_dept": "Development",
                     "request": "エンジニア採用技術評価依頼",
                     "risk_level": "HIGH"},
            caliber_id="hr_dept",
        )
        cross_decision = governance.process(
            hr_to_dev_eid, event_store.get(hr_to_dev_eid) or {}
        )
        # Developmentが承認
        if cross_decision.status == DecisionStatus.PENDING:
            approved = governance.approve(
                cross_decision.decision_id,
                reason="技術評価完了・採用候補承認",
                approver="Dev_Tech_Lead",
            )
            cross_approved = approved.status == DecisionStatus.APPROVED
        else:
            cross_approved = False
        steps.append(("HR→Dev 部門間承認フロー",
                      cross_approved,
                      f"status={cross_decision.status.value}→APPROVED by Dev_Tech_Lead"))
        details["cross_approval"] = cross_approved

        # 5. 全部門統合監査レポート生成
        all_events = event_store.list_events(limit=10000)
        audit_report: dict = {}
        for dept, cfg in DEPARTMENTS.items():
            dept_evs = [e for e in all_events if e.get("caliber_id") == cfg["caliber_id"]]
            audit_report[dept] = {
                "count": len(dept_evs),
                "latest_id": dept_evs[0]["id"] if dept_evs else None,
            }
        report_ok = all(audit_report[d]["count"] > 0 for d in DEPARTMENTS)
        steps.append(("統合監査レポート生成",
                      report_ok,
                      f"4部門合計={sum(v['count'] for v in audit_report.values())}件"))
        details["audit_report"] = audit_report

        # チェーン整合
        chain_ok = event_store.verify_chain()
        steps.append(("全体チェーン整合",
                      chain_ok,
                      f"verify_chain()={chain_ok}"))
        details["chain_valid"] = chain_ok

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }

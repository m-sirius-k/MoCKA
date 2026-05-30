"""
3業種caliber自動生成ファクトリ。
製造業caliberはここで定義（vasAI_Projectには追加しない）。
"""
from caliber.base_caliber import BaseCALIBER
from core.models import ApprovalRule, Artifact, RiskLevel


class ManufacturingCALIBER(BaseCALIBER):
    """製造業向けcaliber。設備停止・品質管理・ライン制御。"""

    def get_caliber_id(self) -> str:
        return "manufacturing_v1"

    def classify_event(self, raw_data: dict) -> str:
        event_type = raw_data.get("event_type", "")
        if event_type in ("equipment_stop", "quality_alert", "line_control"):
            return "decision"
        if event_type == "equipment_failure":
            return "incident"
        return "message"

    def get_approval_rules(self) -> list[ApprovalRule]:
        return [
            ApprovalRule(rule_id="mfg_normal", risk_level=RiskLevel.NORMAL,
                         auto_approve=True, approver_role="SYSTEM"),
            ApprovalRule(rule_id="mfg_high", risk_level=RiskLevel.HIGH,
                         auto_approve=False, approver_role="LINE_SUPERVISOR",
                         conditions={"production_halt_allowed": True}),
            ApprovalRule(rule_id="mfg_critical", risk_level=RiskLevel.CRITICAL,
                         auto_approve=False, approver_role="PLANT_MANAGER",
                         conditions={"emergency_stop": True}),
        ]

    def format_for_intranet(self, artifact: Artifact) -> dict:
        from datetime import datetime, timezone
        return {
            "system":        "MES",
            "work_order_id": artifact.artifact_id,
            "equipment_data": artifact.content,
            "processed_at":  datetime.now(timezone.utc).isoformat(),
            "vasai_hash":    artifact.hash,
            "status":        artifact.status,
            "caliber":       self.get_caliber_id(),
            "line_action":   "HOLD" if artifact.content.get("risk_level") == "HIGH" else "CONTINUE",
        }

    def receive_from_intranet(self, data: dict) -> Artifact:
        event_type = data.get("event_type", "sensor_data")
        risk_hint = "HIGH" if event_type in ("equipment_stop", "equipment_failure") else "NORMAL"
        return Artifact(
            artifact_type=self.classify_event(data),
            source_app="MES",
            source_service="manufacturing_plant",
            content={
                "equipment_id": data.get("equipment_id", "EQ-001"),
                "event_type":   event_type,
                "sensor_value": data.get("sensor_value", 0),
                "line_id":      data.get("line_id", "LINE-A"),
                "risk_level":   risk_hint,
            },
            tags=["manufacturing", "mes", risk_hint.lower()],
        )

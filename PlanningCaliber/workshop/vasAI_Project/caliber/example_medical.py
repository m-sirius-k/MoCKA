"""
vasAI caliber実装例: 医療施設向け。
電子カルテ連携・診断根拠記録・承認フロー。
"""
from datetime import datetime, timezone

from caliber.base_caliber import BaseCALIBER
from core.models import ApprovalRule, Artifact, RiskLevel


class MedicalCALIBER(BaseCALIBER):
    """
    医療施設向けcaliber。
    - 処置・投薬はHIGH以上のリスクで Human Gate
    - 記録のみはNORMAL自動承認
    """

    def get_caliber_id(self) -> str:
        return "medical_v1"

    def classify_event(self, raw_data: dict) -> str:
        event_type = raw_data.get("event_type", "")
        if event_type in ("treatment", "medication", "surgery"):
            return "decision"
        if event_type == "incident":
            return "incident"
        return "message"

    def get_approval_rules(self) -> list[ApprovalRule]:
        return [
            ApprovalRule(
                rule_id="med_normal",
                risk_level=RiskLevel.NORMAL,
                auto_approve=True,
                approver_role="SYSTEM",
            ),
            ApprovalRule(
                rule_id="med_high",
                risk_level=RiskLevel.HIGH,
                auto_approve=False,
                approver_role="CHIEF_PHYSICIAN",
                conditions={"requires_signature": True},
            ),
            ApprovalRule(
                rule_id="med_critical",
                risk_level=RiskLevel.CRITICAL,
                auto_approve=False,
                approver_role="HOSPITAL_DIRECTOR",
                conditions={"requires_emergency_protocol": True},
            ),
        ]

    def format_for_intranet(self, artifact: Artifact) -> dict:
        return {
            "system":       "EMR",
            "record_id":    artifact.artifact_id,
            "patient_data": artifact.content,
            "recorded_at":  datetime.now(timezone.utc).isoformat(),
            "vasai_hash":   artifact.hash,
            "status":       artifact.status,
            "caliber":      self.get_caliber_id(),
        }

    def receive_from_intranet(self, data: dict) -> Artifact:
        return Artifact(
            artifact_type=self.classify_event(data),
            source_app="EMR",
            source_service="hospital_system",
            content={
                "patient_id":  data.get("patient_id", "ANON"),
                "event_type":  data.get("event_type", "record"),
                "description": data.get("description", ""),
                "physician":   data.get("physician", ""),
            },
            tags=["medical", data.get("department", "general")],
        )

"""
vasAI caliber実装例: 金融機関向け。
取引判断・リスク承認・法的証跡。
"""
from datetime import datetime, timezone

from caliber.base_caliber import BaseCALIBER
from core.models import ApprovalRule, Artifact, RiskLevel


class FinanceCALIBER(BaseCALIBER):
    """
    金融機関向けcaliber。
    - 大口取引はHIGH/CRITICAL → Human Gate
    - 通常取引はNORMAL/CAUTION → 自動承認
    """

    LARGE_TX_THRESHOLD = 10_000_000  # 1000万円以上はHIGH

    def get_caliber_id(self) -> str:
        return "finance_v1"

    def classify_event(self, raw_data: dict) -> str:
        tx_type = raw_data.get("transaction_type", "")
        if tx_type in ("transfer", "settlement", "trade"):
            return "decision"
        if tx_type == "suspicious":
            return "incident"
        return "message"

    def get_approval_rules(self) -> list[ApprovalRule]:
        return [
            ApprovalRule(
                rule_id="fin_normal",
                risk_level=RiskLevel.NORMAL,
                auto_approve=True,
                approver_role="SYSTEM",
            ),
            ApprovalRule(
                rule_id="fin_caution",
                risk_level=RiskLevel.CAUTION,
                auto_approve=True,
                approver_role="SYSTEM",
                conditions={"log_required": True},
            ),
            ApprovalRule(
                rule_id="fin_high",
                risk_level=RiskLevel.HIGH,
                auto_approve=False,
                approver_role="COMPLIANCE_OFFICER",
                conditions={"amount_threshold": self.LARGE_TX_THRESHOLD},
            ),
            ApprovalRule(
                rule_id="fin_critical",
                risk_level=RiskLevel.CRITICAL,
                auto_approve=False,
                approver_role="CFO",
                conditions={"regulatory_report": True, "freeze_account": True},
            ),
        ]

    def format_for_intranet(self, artifact: Artifact) -> dict:
        return {
            "system":        "CORE_BANKING",
            "transaction_id": artifact.artifact_id,
            "tx_data":       artifact.content,
            "processed_at":  datetime.now(timezone.utc).isoformat(),
            "vasai_hash":    artifact.hash,
            "status":        artifact.status,
            "caliber":       self.get_caliber_id(),
            "audit_trail":   True,
        }

    def receive_from_intranet(self, data: dict) -> Artifact:
        amount = data.get("amount", 0)
        risk_hint = "HIGH" if amount >= self.LARGE_TX_THRESHOLD else "NORMAL"

        return Artifact(
            artifact_type=self.classify_event(data),
            source_app="CORE_BANKING",
            source_service="finance_system",
            content={
                "transaction_type": data.get("transaction_type", "transfer"),
                "amount":           amount,
                "currency":         data.get("currency", "JPY"),
                "from_account":     data.get("from_account", ""),
                "to_account":       data.get("to_account", ""),
                "risk_level":       risk_hint,
            },
            tags=["finance", "transaction", risk_hint.lower()],
        )

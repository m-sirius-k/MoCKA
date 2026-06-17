"""
Context Runtime v2 — ContextValidator
責務: 4層の整合性・完全性を検証する。
AIがMemoryから作業再開できるかを判定する基準として使う。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .institution_context import InstitutionContext
    from .working_context import WorkingContext
    from .memory_context import MemoryContext
    from .execution_context import ExecutionContext


@dataclass
class ValidationIssue:
    layer: str
    field: str
    severity: str  # CRITICAL / WARN / INFO
    message: str

    def to_dict(self) -> dict:
        return {"layer": self.layer, "field": self.field,
                "severity": self.severity, "message": self.message}


class ContextValidator:
    def validate(
        self,
        institution: "InstitutionContext",
        working: "WorkingContext",
        memory: "MemoryContext",
        execution: "ExecutionContext",
    ) -> dict:
        issues: list[ValidationIssue] = []

        issues.extend(self._validate_institution(institution))
        issues.extend(self._validate_working(working))
        issues.extend(self._validate_memory(memory))
        issues.extend(self._validate_execution(execution))

        criticals = [i for i in issues if i.severity == "CRITICAL"]
        warns = [i for i in issues if i.severity == "WARN"]

        resumable = len(criticals) == 0

        return {
            "resumable": resumable,
            "critical_count": len(criticals),
            "warn_count": len(warns),
            "issues": [i.to_dict() for i in issues],
            "verdict": "RESUMABLE" if resumable else "BLOCKED — 作業再開不可",
        }

    def _validate_institution(self, ctx: "InstitutionContext") -> list[ValidationIssue]:
        issues = []
        if not ctx.allowed_modules:
            issues.append(ValidationIssue(
                "Institution", "allowed_modules", "CRITICAL",
                "ARCHITECTURE_REGISTRY が未ロード。実装前に境界確認不可。"
            ))
        if not ctx.latest_seal:
            issues.append(ValidationIssue(
                "Institution", "latest_seal", "WARN",
                "seal未確認。最新コミット整合性が不明。"
            ))
        if ctx.open_incidents:
            issues.append(ValidationIssue(
                "Institution", "open_incidents", "WARN",
                f"{len(ctx.open_incidents)}件のオープンインシデントあり。"
            ))
        return issues

    def _validate_working(self, ctx: "WorkingContext") -> list[ValidationIssue]:
        issues = []
        if not ctx.current_task:
            issues.append(ValidationIssue(
                "Working", "current_task", "CRITICAL",
                "current_task が未設定。AIは何をすべきか不明。"
            ))
        if not ctx.current_goal:
            issues.append(ValidationIssue(
                "Working", "current_goal", "CRITICAL",
                "current_goal が未設定。AIはゴールを把握できない。"
            ))
        if not ctx.next_action:
            issues.append(ValidationIssue(
                "Working", "next_action", "WARN",
                "next_action が未設定。次の一手が不明。"
            ))
        if ctx.blockers:
            issues.append(ValidationIssue(
                "Working", "blockers", "WARN",
                f"ブロッカーが{len(ctx.blockers)}件存在する。"
            ))
        return issues

    def _validate_memory(self, ctx: "MemoryContext") -> list[ValidationIssue]:
        issues = []
        w = ctx.five_w1h
        if not w.what:
            issues.append(ValidationIssue(
                "Memory", "five_w1h.what", "CRITICAL",
                "5W1H.what が未設定。何をしているか不明。"
            ))
        if not w.why:
            issues.append(ValidationIssue(
                "Memory", "five_w1h.why", "WARN",
                "5W1H.why が未設定。理由が記録されていない。"
            ))
        if ctx.event_count == 0:
            issues.append(ValidationIssue(
                "Memory", "event_count", "WARN",
                "events.db にイベントが0件。MoCKA接続確認が必要。"
            ))
        return issues

    def _validate_execution(self, ctx: "ExecutionContext") -> list[ValidationIssue]:
        issues = []
        if not ctx.architecture_registry:
            issues.append(ValidationIssue(
                "Execution", "architecture_registry", "CRITICAL",
                "ARCHITECTURE_REGISTRY 未ロード。Execution Gate が機能しない。"
            ))
        if ctx.validation_result == "BLOCK":
            issues.append(ValidationIssue(
                "Execution", "validation_result", "CRITICAL",
                "直前のExecution Gateが BLOCK。実装を停止すること。"
            ))
        return issues

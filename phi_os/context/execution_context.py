"""
Context Runtime v2 — Layer 4: ExecutionContext + ExecutionGate
責務: 実装開始判定。Architecture Boundary・Ownership・Permission・Incidentを検査し
Execution Gateが通過しない限り実装を開始してはならない。
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

_REGISTRY_PATH = Path(__file__).parents[2] / "ARCHITECTURE_REGISTRY.json"


class GateStatus(str, Enum):
    PASS = "PASS"
    BLOCK = "BLOCK"
    WARN = "WARN"


@dataclass
class GateCheck:
    name: str
    status: GateStatus
    reason: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "status": self.status.value, "reason": self.reason}


@dataclass
class GateResult:
    passed: bool
    checks: list = field(default_factory=list)   # list[GateCheck]
    blocked_by: str = ""
    warnings: list = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "checks": [c.to_dict() for c in self.checks],
            "blocked_by": self.blocked_by,
            "warnings": self.warnings,
            "timestamp": self.timestamp,
        }


class ExecutionGate:
    """
    実装開始判定ゲート。
    run() が GateResult(passed=False) を返した場合、
    くろこは実装を停止し博士に確認を求めなければならない。
    """

    def __init__(self) -> None:
        self._registry: dict = {}
        self._load_registry()

    def _load_registry(self) -> None:
        if _REGISTRY_PATH.exists():
            try:
                self._registry = json.loads(
                    _REGISTRY_PATH.read_text(encoding="utf-8")
                )
            except Exception:
                pass

    def run(self, project: str, module: str,
            open_incidents: list | None = None,
            locked_files: list | None = None,
            target_file: str = "") -> GateResult:
        checks: list[GateCheck] = []
        warnings: list[str] = []
        blocked_by = ""

        # 1. Architecture Registry Check
        arch_check = self._check_architecture(project, module)
        checks.append(arch_check)

        # 2. Ownership Check
        own_check = self._check_ownership(project)
        checks.append(own_check)

        # 3. Incident Check
        inc_check = self._check_incidents(open_incidents or [])
        checks.append(inc_check)

        # 4. Boundary Check (file path)
        if target_file:
            boundary_check = self._check_boundary(project, target_file)
            checks.append(boundary_check)

        # 5. Permission Check (locked files)
        if locked_files and target_file:
            perm_check = self._check_permission(target_file, locked_files)
            checks.append(perm_check)

        # 集約
        blocked = [c for c in checks if c.status == GateStatus.BLOCK]
        warned = [c for c in checks if c.status == GateStatus.WARN]
        for c in warned:
            warnings.append(c.reason)

        if blocked:
            blocked_by = blocked[0].reason
            passed = False
        else:
            passed = True

        return GateResult(
            passed=passed,
            checks=checks,
            blocked_by=blocked_by,
            warnings=warnings,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _check_architecture(self, project: str, module: str) -> GateCheck:
        projects = self._registry.get("projects", {})
        proj_data = projects.get(project)
        if not proj_data:
            return GateCheck(
                "ArchitectureRegistry",
                GateStatus.WARN,
                f"project '{project}' はregistryに未登録",
            )
        forbidden = proj_data.get("forbidden_modules", [])
        for fm in forbidden:
            if fm.lower() in module.lower() or module.lower() in fm.lower():
                return GateCheck(
                    "ArchitectureRegistry",
                    GateStatus.BLOCK,
                    f"module '{module}' は {project} の forbidden_modules に該当: '{fm}'",
                )
        allowed = proj_data.get("allowed_modules", [])
        matched = any(
            a.lower() in module.lower() or module.lower() in a.lower()
            for a in allowed
        )
        if not matched:
            return GateCheck(
                "ArchitectureRegistry",
                GateStatus.WARN,
                f"module '{module}' は {project} の allowed_modules に明示されていない",
            )
        return GateCheck("ArchitectureRegistry", GateStatus.PASS,
                         f"module '{module}' は allowed")

    def _check_ownership(self, project: str) -> GateCheck:
        known = {"MoCKA", "PlanningCaliber"}
        if project not in known:
            return GateCheck("Ownership", GateStatus.WARN,
                             f"project '{project}' は未知のプロジェクト")
        return GateCheck("Ownership", GateStatus.PASS, f"project '{project}' は既知")

    def _check_incidents(self, open_incidents: list) -> GateCheck:
        blocking = [i for i in open_incidents if "CRITICAL" in str(i).upper()]
        if blocking:
            return GateCheck("IncidentCheck", GateStatus.BLOCK,
                             f"CRITICALインシデントが未解決: {blocking[0]}")
        if open_incidents:
            return GateCheck("IncidentCheck", GateStatus.WARN,
                             f"{len(open_incidents)}件のオープンインシデントあり")
        return GateCheck("IncidentCheck", GateStatus.PASS, "オープンインシデントなし")

    def _check_boundary(self, project: str, target_file: str) -> GateCheck:
        project_roots = {
            "MoCKA": "C:/Users/sirok/MoCKA",
            "PlanningCaliber": "C:/Users/sirok/MoCKA/PlanningCaliber",
        }
        root = project_roots.get(project, "")
        norm = target_file.replace("\\", "/")
        # 相対パスは境界チェックをスキップ（呼び出し元が正しいプロジェクトを指定している前提）
        is_absolute = len(norm) > 1 and norm[1] == ":"
        if root and is_absolute and not norm.startswith(root):
            return GateCheck(
                "BoundaryCheck",
                GateStatus.BLOCK,
                f"'{target_file}' は project '{project}' の境界外",
            )
        return GateCheck("BoundaryCheck", GateStatus.PASS, "境界内")

    def _check_permission(self, target_file: str, locked_files: list) -> GateCheck:
        norm = target_file.replace("\\", "/")
        for lf in locked_files:
            if lf.replace("\\", "/") == norm:
                return GateCheck("PermissionCheck", GateStatus.BLOCK,
                                 f"'{target_file}' はロック中")
        return GateCheck("PermissionCheck", GateStatus.PASS, "ロックなし")


@dataclass
class ExecutionContext:
    # --- Registry ---
    architecture_registry: dict = field(default_factory=dict)
    project_registry: list = field(default_factory=list)
    directory_registry: dict = field(default_factory=dict)

    # --- Gate State ---
    last_gate_result: Optional[GateResult] = None
    validation_result: str = "PENDING"

    # --- Meta ---
    updated_at: str = ""

    _gate: ExecutionGate = field(default_factory=ExecutionGate, repr=False, compare=False)

    @classmethod
    def load(cls) -> "ExecutionContext":
        ctx = cls()
        ctx.updated_at = datetime.now(timezone.utc).isoformat()
        ctx._load_registry()
        return ctx

    def _load_registry(self) -> None:
        if _REGISTRY_PATH.exists():
            try:
                reg = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
                self.architecture_registry = reg
                self.project_registry = list(reg.get("projects", {}).keys())
            except Exception:
                pass

    def check(self, project: str, module: str,
              open_incidents: list | None = None,
              locked_files: list | None = None,
              target_file: str = "") -> GateResult:
        result = self._gate.run(
            project=project,
            module=module,
            open_incidents=open_incidents,
            locked_files=locked_files,
            target_file=target_file,
        )
        self.last_gate_result = result
        self.validation_result = "PASS" if result.passed else "BLOCK"
        self.updated_at = datetime.now(timezone.utc).isoformat()
        return result

    def to_dict(self) -> dict:
        return {
            "layer": "Execution",
            "architecture_registry": self.architecture_registry,
            "project_registry": self.project_registry,
            "directory_registry": self.directory_registry,
            "last_gate_result": self.last_gate_result.to_dict() if self.last_gate_result else None,
            "validation_result": self.validation_result,
            "updated_at": self.updated_at,
        }

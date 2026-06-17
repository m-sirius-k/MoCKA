"""
Context Runtime v2 — Layer 1: InstitutionContext
責務: 制度情報。プロジェクト・フェーズ・アーキテクチャ・警告・インシデントの正本。
AIはすべての判断の前にここを参照する。
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_REGISTRY_PATH = Path(__file__).parents[2] / "ARCHITECTURE_REGISTRY.json"
_OVERVIEW_PATH = Path(__file__).parents[2] / ".." / "MOCKA_OVERVIEW.json"


@dataclass
class InstitutionContext:
    # --- Project ---
    project: str = "MoCKA"
    repository: str = "github.com/m-sirius-k/MoCKA"
    current_phase: str = "Phase 4"
    mission: str = "制度カーネル — AIが制度・文脈・作業状態を共有し途中から再開できる制度OS"
    current_version: str = "v6.1"
    branch: str = "main"

    # --- Priority & Roles ---
    priority: str = "商用展開 + 制度化"
    roles: dict = field(default_factory=lambda: {
        "制度執行官": "くろこ (Claude-sonnet-4-6)",
        "統治者": "nsjp_kimura",
    })

    # --- Architecture ---
    architecture: dict = field(default_factory=dict)
    allowed_modules: list = field(default_factory=list)
    forbidden_modules: list = field(default_factory=list)

    # --- Status ---
    verification_status: str = "UNVERIFIED"
    top_todos: list = field(default_factory=list)

    # --- Risk ---
    warnings: list = field(default_factory=list)
    known_risks: list = field(default_factory=list)
    open_incidents: list = field(default_factory=list)

    # --- Seal ---
    latest_seal: str = ""

    @classmethod
    def load(cls) -> "InstitutionContext":
        ctx = cls()
        ctx._load_architecture_registry()
        ctx._load_overview()
        return ctx

    def _load_architecture_registry(self) -> None:
        if not _REGISTRY_PATH.exists():
            self.warnings.append("ARCHITECTURE_REGISTRY.json が存在しません")
            return
        try:
            reg = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
            proj = reg.get("projects", {}).get("MoCKA", {})
            self.allowed_modules = proj.get("allowed_modules", [])
            self.forbidden_modules = proj.get("forbidden_modules", [])
            self.architecture["registry_version"] = reg.get("version", "")
            self.architecture["gate_rule"] = reg.get("gate_rule", "")
        except Exception as e:
            self.warnings.append(f"ARCHITECTURE_REGISTRY 読み込み失敗: {e}")

    def _load_overview(self) -> None:
        p = _OVERVIEW_PATH.resolve()
        if not p.exists():
            # フォールバック: 既知の値をハードコード
            return
        try:
            ov = json.loads(p.read_text(encoding="utf-8"))
            gov = ov.get("governance", {})
            seal = gov.get("latest_seal", {})
            self.latest_seal = seal.get("commit", "")
            self.verification_status = "VERIFIED" if seal.get("status") == "ALL CHECKS PASSED" else "UNVERIFIED"
            next_a = ov.get("next_actions", {})
            self.top_todos = next_a.get("immediate", [])
            issues = ov.get("current_issues", {})
            self.open_incidents = [
                f"{k}: {v}" for k, v in issues.items()
                if v.startswith("[ACTIVE]")
            ]
        except Exception as e:
            self.warnings.append(f"MOCKA_OVERVIEW 読み込み失敗: {e}")

    def is_module_allowed(self, module_name: str) -> bool:
        name_lower = module_name.lower()
        for fm in self.forbidden_modules:
            if fm.lower() in name_lower or name_lower in fm.lower():
                return False
        return True

    def to_dict(self) -> dict:
        return {
            "layer": "Institution",
            "project": self.project,
            "repository": self.repository,
            "current_phase": self.current_phase,
            "mission": self.mission,
            "current_version": self.current_version,
            "branch": self.branch,
            "priority": self.priority,
            "roles": self.roles,
            "architecture": self.architecture,
            "allowed_modules": self.allowed_modules,
            "forbidden_modules": self.forbidden_modules,
            "verification_status": self.verification_status,
            "top_todos": self.top_todos,
            "warnings": self.warnings,
            "known_risks": self.known_risks,
            "open_incidents": self.open_incidents,
            "latest_seal": self.latest_seal,
        }

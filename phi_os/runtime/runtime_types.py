# phi_os/runtime/runtime_types.py
# Institution Runtime — 共通型定義
# 参照: PHI_OS_CONSTITUTION_v1.md / GATE_ARCHITECTURE_v1.md
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# ── Binding状態 (Constitution 4.2) ──────────────────────────────────────────

class BindingStatus(str, Enum):
    CONNECTED  = "CONNECTED"
    PARTIAL    = "PARTIAL"
    SHADOW     = "SHADOW"
    ORPHAN     = "ORPHAN"
    DEPRECATED = "DEPRECATED"
    UNKNOWN    = "UNKNOWN"


# ── Meaning分類 (Constitution 原則6) ────────────────────────────────────────

class MeaningClass(str, Enum):
    SYSTEM_CORE   = "SYSTEM_CORE"
    GOVERNANCE    = "GOVERNANCE"
    KNOWLEDGE     = "KNOWLEDGE"
    DESIGN        = "DESIGN"
    PHASE_RECORD  = "PHASE_RECORD"
    REQUIREMENT   = "REQUIREMENT"
    TOOL          = "TOOL"
    INCIDENT      = "INCIDENT"
    UNCLASSIFIED  = "UNCLASSIFIED"


# ── Authority種別 (Constitution 3.1) ────────────────────────────────────────

class AuthorityType(str, Enum):
    GATE         = "Gate Authority"
    EVENT        = "Event Authority"
    KNOWLEDGE    = "Knowledge Authority"
    VERSION      = "Version Authority"
    VERIFICATION = "Verification Authority"
    INSTITUTION  = "Institution Authority"


# ── Gate識別子 (GATE_ARCHITECTURE_v1.md 第1章) ──────────────────────────────

class GateId(str, Enum):
    EVENT      = "GATE-EVENT"
    KNOWLEDGE  = "GATE-KNOW"
    MODULE     = "GATE-MOD"
    PROMPT     = "GATE-PROMPT"
    RELEASE    = "GATE-REL"
    EXPERIMENT = "GATE-EXP"
    DOCUMENT   = "GATE-DOC"


class GateStatus(str, Enum):
    ACTIVE  = "ACTIVE"
    DEFINED = "DEFINED"
    PLANNED = "PLANNED"


# ── 制度違反分類 (Constitution 6.2) ─────────────────────────────────────────

class ViolationSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH     = "High"
    MEDIUM   = "Medium"
    LOW      = "Low"


# ── データ構造 ───────────────────────────────────────────────────────────────

@dataclass
class Meaning:
    meaning_id: str
    name: str
    meaning_class: MeaningClass
    description: str
    version: str = "1.0"
    history: list[dict] = field(default_factory=list)


@dataclass
class Authority:
    authority_type: AuthorityType
    holder: str               # "PHI-OS" / "Event Gate" 等
    delegated_to: Optional[str] = None
    delegation_event_id: Optional[str] = None


@dataclass
class Institution:
    institution_id: str
    name: str
    description: str
    primary_gate: GateId
    secondary_gates: list[GateId] = field(default_factory=list)
    artifact_ids: list[str] = field(default_factory=list)


@dataclass
class Gate:
    gate_id: GateId
    name: str
    authority_type: AuthorityType
    status: GateStatus
    required_meanings: list[MeaningClass] = field(default_factory=list)
    description: str = ""


@dataclass
class Artifact:
    artifact_id: str
    name: str
    path: str
    meaning_id: str
    institution_id: str
    binding_status: BindingStatus = BindingStatus.UNKNOWN
    gate_id: Optional[GateId] = None
    version: str = "1.0"
    tags: list[str] = field(default_factory=list)


@dataclass
class BindingResult:
    artifact_id: str
    binding_status: BindingStatus
    meaning_id: Optional[str]
    institution_id: Optional[str]
    gate_id: Optional[GateId]
    is_valid: bool
    issues: list[str] = field(default_factory=list)


@dataclass
class ComplianceViolation:
    violation_id: str
    severity: ViolationSeverity
    violation_type: str
    target_artifact_id: Optional[str]
    description: str
    remediation: str


@dataclass
class ComplianceResult:
    audit_id: str
    is_compliant: bool
    violations: list[ComplianceViolation] = field(default_factory=list)
    audited_artifacts: int = 0
    summary: str = ""


@dataclass
class EventContext:
    context_id: str
    artifact_id: str
    institution_id: str
    gate_id: GateId
    binding_status: BindingStatus
    authority_type: AuthorityType
    is_gate_valid: bool
    issues: list[str] = field(default_factory=list)

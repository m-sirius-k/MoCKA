# phi_os/runtime/runtime_errors.py
# Institution Runtime — 専用例外定義


class InstitutionRuntimeError(Exception):
    """Runtime基底例外"""


class BindingError(InstitutionRuntimeError):
    """Binding接続の異常"""
    def __init__(self, artifact_id: str, reason: str):
        self.artifact_id = artifact_id
        self.reason = reason
        super().__init__(f"BindingError [{artifact_id}]: {reason}")


class AuthorityConflictError(InstitutionRuntimeError):
    """Authority一意性違反 (Constitution 3.2)"""
    def __init__(self, authority_type: str, holder_a: str, holder_b: str):
        self.authority_type = authority_type
        super().__init__(
            f"AuthorityConflict: {authority_type} は {holder_a} と {holder_b} が重複保持"
        )


class MeaningNotFoundError(InstitutionRuntimeError):
    """Meaning未登録"""
    def __init__(self, meaning_id: str):
        self.meaning_id = meaning_id
        super().__init__(f"MeaningNotFound: '{meaning_id}' は登録されていない")


class GateValidationError(InstitutionRuntimeError):
    """Gate通過検証失敗"""
    def __init__(self, gate_id: str, reasons: list[str]):
        self.gate_id = gate_id
        self.reasons = reasons
        super().__init__(f"GateValidation [{gate_id}]: {'; '.join(reasons)}")


class InstitutionResolutionError(InstitutionRuntimeError):
    """Institution解決失敗"""
    def __init__(self, institution_id: str, reason: str):
        self.institution_id = institution_id
        super().__init__(f"InstitutionResolution [{institution_id}]: {reason}")


class ComplianceViolationError(InstitutionRuntimeError):
    """制度違反検知 (Constitution 6.1)"""
    def __init__(self, violation_type: str, artifact_id: str, detail: str):
        self.violation_type = violation_type
        self.artifact_id = artifact_id
        super().__init__(f"ComplianceViolation [{violation_type}] on {artifact_id}: {detail}")


class OrphanArtifactError(BindingError):
    """Institution未所属 (Constitution 原則7)"""
    def __init__(self, artifact_id: str):
        super().__init__(artifact_id, "ORPHAN: Institution未所属。制度操作不可")


class ShadowArtifactError(BindingError):
    """Gate外部存在 (Constitution 4.2)"""
    def __init__(self, artifact_id: str):
        super().__init__(artifact_id, "SHADOW: 正規経路外に存在。制度操作不可")


class DuplicateBindingError(BindingError):
    """Binding重複登録"""
    def __init__(self, artifact_id: str):
        super().__init__(artifact_id, "Binding重複: 同一Artifactの重複CONNECTED登録は禁止")

# capability_table.py

CAPABILITY_TABLE = {
    "CAP_STATE_READ": {
        "desc":      "Institution State 読み取り",
        "trust_min": "trial",
    },
    "CAP_STATE_WRITE": {
        "desc":      "Institution State 更新（承認後）",
        "trust_min": "verified",
    },
    "CAP_EVENT_WRITE": {
        "desc":      "events.db へのイベント記録",
        "trust_min": "verified",
    },
    "CAP_LEDGER_READ": {
        "desc":      "Decision Ledger 読み取り",
        "trust_min": "verified",
    },
    "CAP_LEDGER_WRITE": {
        "desc":      "Decision Ledger 記録",
        "trust_min": "institution_certified",
    },
    "CAP_SIMULATION": {
        "desc":      "Simulation Mode 実行",
        "trust_min": "institution_certified",
    },
    "CAP_AUDIT": {
        "desc":      "監査ログ閲覧",
        "trust_min": "institution_certified",
    },
    "CAP_REGISTRY_ADMIN": {
        "desc":      "AI Registry 管理",
        "trust_min": "institution_certified",
    },
}

TRUST_LEVELS = ["trial", "verified", "institution_certified", "critical_operation"]

def is_capability_valid(cap_id: str) -> bool:
    return cap_id in CAPABILITY_TABLE

def is_trust_sufficient(cap_id: str, ai_trust_level: str) -> bool:
    if cap_id not in CAPABILITY_TABLE:
        return False
    required = CAPABILITY_TABLE[cap_id]["trust_min"]
    return (TRUST_LEVELS.index(ai_trust_level)
            >= TRUST_LEVELS.index(required))

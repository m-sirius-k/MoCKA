"""ISE Version Policy v1"""

VERSION_POLICY = {
    "snapshot_retention": 10,        # 世代数
    "snapshot_interval_revisions": 100,
    "snapshot_interval_hours": 24,
    "major_version_triggers": [      # メジャー版上げ条件
        "state_machine_change",
        "taxonomy_breaking_change",
        "institution_contract_update",
    ],
    "minor_version_triggers": [
        "provider_added",
        "capability_expanded",
    ],
}


def get_policy() -> dict:
    return VERSION_POLICY

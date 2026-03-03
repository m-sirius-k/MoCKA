# CALIBER_RECORD_SCHEMA (Frozen Contract)

Status: FROZEN
schema_version: 0.1.0

Caliber record is a derived artifact from a Shadow report.
It must not depend on raw stdout/stderr text.
It must not modify Primary or Shadow.

## Top-level required keys

schema_version (string)
generated_at_utc (string RFC3339)
source (object)
signals (object)
evidence (array)

## source (required)

shadow_report_id (string)
shadow_schema_version (string)
shadow_tool (object)
primary_verifier (string)
primary_exit_code (int or null)

## signals (required)

ok (bool)
fail_kinds (array of string)
mutation_detected (bool)
stdout_sha256 (string hex)
stderr_sha256 (string hex)

## evidence (required)

Each item:
kind (string)
evidence_sha256 (string hex)

Rules:
- evidence_sha256 is sha256 of canonical JSON of the original evidence object (sorted keys, compact separators).
- No raw text fields from stdout/stderr may be copied into Caliber record.

## Determinism rules

- UTF-8
- sorted keys
- newline at EOF
- stable ordering
- schema_version bump required for structure change

## Operational Standard (Windows PowerShell)

# NOTE: produce Shadow report as UTF-8 without BOM
$j=(python shadow\verify_all_shadow.py --primary verify_pack_v4_sample/verify_all_v4.py)
[System.IO.File]::WriteAllText((Resolve-Path .\outbox\shadow_last.json),$j,(New-Object System.Text.UTF8Encoding($false)))

# NOTE: extract Caliber record
python caliber\extract_caliber_record.py --shadow-report outbox\shadow_last.json --out outbox\caliber_last.json

# NOTE: parse with utf-8
python -c "import json; r=json.load(open(r'outbox\caliber_last.json','r',encoding='utf-8')); print('CALIBER', r['schema_version'], r['signals']['ok'], r['signals']['fail_kinds'])"

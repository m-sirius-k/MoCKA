# SHADOW_REPORT_SCHEMA (Frozen Contract)

Status: FROZEN
schema_version: 1.0.0

Shadow report is diagnostic-only.
Primary is read-only.
Shadow never repairs or grants exceptions.

## Top-level required keys

schema_version (string)
report_id (string)
generated_at_utc (string RFC3339)
tool (object)
repo (object)
primary_run (object)
working_tree (object)
io (object)
result (object)

## FAIL_KIND vocabulary (v1)

PRIMARY_FAILED
MUTATION_DETECTED
PRIMARY_STDERR
PRIMARY_STDOUT_PATTERN
TOOL_ERROR
GIT_UNAVAILABLE
UNKNOWN

## Determinism rules

- UTF-8
- sorted keys
- newline at EOF
- stable ordering
- version bump required for structure change
## Operational Standard (Windows PowerShell)

# NOTE: write Shadow report as UTF-8 without BOM for machine parsing stability
$j=(python shadow\verify_all_shadow.py --primary verify_pack_v4_sample/verify_all_v4.py); [System.IO.File]::WriteAllText((Resolve-Path .\outbox\shadow_last.json),$j,(New-Object System.Text.UTF8Encoding($false)))

# NOTE: parse with utf-8
python -c "import json; r=json.load(open(r'outbox\shadow_last.json','r',encoding='utf-8')); print('OK', r['schema_version'], r['result']['ok'])"

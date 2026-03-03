# SHADOW_REPORT_SCHEMA (Frozen Contract)

Status: FROZEN
schema_version: 1.3.0

Shadow report is diagnostic-only.
Primary is read-only.
Shadow never repairs or grants exceptions.

## Top-level required keys

schema_version (string)
report_id (string)
generated_at_utc (string RFC3339)
tool (object)
primary_run (object)
working_tree (object)
io (object)
result (object)

## io.stdout (v1.2.0)

lines (array of {n:int, text:string})
sha256 (string hex)
trimmed (bool)
total_lines (int)

Rules:
- If trimmed=true, lines contains head N + tail N plus any evidence-hit lines.
- Evidence-hit lines must be preserved even when trimming.

## FAIL_KIND vocabulary (v1.3.0)
PRIMARY_FAILED
MUTATION_DETECTED
PRIMARY_STDERR
PRIMARY_STDOUT_PATTERN
EXPECTED_FAIL_BUT_PASSED
SCHEMA_MISMATCH
VOCAB_MISMATCH
TOOL_ERROR
GIT_UNAVAILABLE
UNKNOWN

## Determinism rules

- UTF-8
- sorted keys
- newline at EOF
- stable ordering
- schema_version bump required for structure change

## Meaning notes

EXPECTED_FAIL_BUT_PASSED:
A sample that was expected to fail but passed verification.
Diagnostic integrity breach signal for sample packs.

## Operational Standard (Windows PowerShell)

# NOTE: write Shadow report as UTF-8 without BOM for machine parsing stability
$j=(python shadow\verify_all_shadow.py --primary verify_pack_v4_sample/verify_all_v4.py); [System.IO.File]::WriteAllText((Resolve-Path .\outbox\shadow_last.json),$j,(New-Object System.Text.UTF8Encoding($false)))

# NOTE: parse with utf-8
python -c "import json; r=json.load(open(r'outbox\shadow_last.json','r',encoding='utf-8')); print('OK', r['schema_version'], r['result']['ok'], r['io']['stdout']['trimmed'], r['io']['stdout']['total_lines'])"

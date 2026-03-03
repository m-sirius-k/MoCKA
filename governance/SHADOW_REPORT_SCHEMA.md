SHADOW_REPORT_SCHEMA
Frozen Contract
Status: FROZEN
schema_version: 1.3.0

Purpose
Shadow report is diagnostic-only.
Primary verifier is read-only.
Shadow never mutates state, repairs artifacts, or grants exceptions.
Shadow produces structured, deterministic evidence about Primary execution.

Top-Level Required Keys
schema_version (string)
report_id (string)
generated_at_utc (string RFC3339 UTC)
tool (object)
primary_run (object)
working_tree (object)
io (object)
result (object)

io.stdout Structure (since v1.2.0)
lines (array of objects)
  n (int)
  text (string)
sha256 (string lowercase hex, 64 characters)
trimmed (boolean)
total_lines (integer)

Trimming Contract
If trimmed = true:
  lines MUST contain:
    - first N lines (head)
    - last N lines (tail)
    - any lines referenced by evidence
Evidence-hit lines MUST be preserved even when trimming is active.

FAIL_KIND Vocabulary (authoritative list, v1.3.0)
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

Vocabulary Rules
All FAIL_KIND values:
  - uppercase
  - characters: A-Z 0-9 underscore
  - no spaces
  - must appear in this list
Adding or removing a FAIL_KIND requires schema_version bump.

Determinism Rules
Encoding: UTF-8
Key ordering: sorted
JSON formatting: deterministic
Newline: single newline at EOF
Hash values: lowercase hex
Schema structure changes require schema_version increment.

Meaning Notes

EXPECTED_FAIL_BUT_PASSED
A test case marked as expected failure was verified as success.
Indicates sample integrity breach.
This is a diagnostic integrity signal, not a repair action.

PRIMARY_FAILED
Primary verifier returned non-zero exit code.

MUTATION_DETECTED
Working tree mutation detected before or after primary run.

SCHEMA_MISMATCH
Governance schema_version does not match tool implementation.

VOCAB_MISMATCH
FAIL_KIND value not listed in governance vocabulary.

TOOL_ERROR
Internal Shadow tool failure.

Operational Standard (Windows PowerShell)

Write Shadow report as UTF-8 without BOM:

$j=(python shadow\verify_all_shadow.py --primary verify_pack_v4_sample/verify_all_v4.py)
[System.IO.File]::WriteAllText((Resolve-Path .\outbox\shadow_last.json),$j,(New-Object System.Text.UTF8Encoding($false)))

Parse with UTF-8:

python -c "import json; r=json.load(open(r'outbox\shadow_last.json','r',encoding='utf-8')); print('OK', r['schema_version'], r['result']['ok'], r['io']['stdout']['trimmed'], r['io']['stdout']['total_lines'])"

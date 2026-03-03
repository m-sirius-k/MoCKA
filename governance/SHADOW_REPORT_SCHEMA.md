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

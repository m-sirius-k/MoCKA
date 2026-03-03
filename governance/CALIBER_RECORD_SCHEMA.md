# CALIBER_RECORD_SCHEMA (Frozen Contract)

Status: FROZEN
schema_version: 0.2.0

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
summary (string)

Rules:
- summary must be derived only from ok + fail_kinds + mutation_detected.
- summary must not contain raw stdout/stderr text.

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

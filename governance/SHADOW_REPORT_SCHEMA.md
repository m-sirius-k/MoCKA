SHADOW\_REPORT\_SCHEMA

Frozen Contract

Status: FROZEN

schema\_version: 1.3.0



Purpose

Shadow report is diagnostic-only.

Primary verifier is read-only.

Shadow never mutates state, repairs artifacts, or grants exceptions.

Shadow produces structured, deterministic evidence about Primary execution.



Top-Level Required Keys

schema\_version (string)

report\_id (string)

generated\_at\_utc (string RFC3339 UTC)

tool (object)

primary\_run (object)

working\_tree (object)

io (object)

result (object)



io.stdout Structure (since v1.2.0)

lines (array of objects)

&nbsp; n (int)

&nbsp; text (string)

sha256 (string lowercase hex, 64 characters)

trimmed (boolean)

total\_lines (integer)



Trimming Contract

If trimmed = true:

&nbsp; lines MUST contain:

&nbsp;   - first N lines (head)

&nbsp;   - last N lines (tail)

&nbsp;   - any lines referenced by evidence

Evidence-hit lines MUST be preserved even when trimming is active.



\## FAIL\_KIND vocabulary (v1.3.0)

PRIMARY\_FAILED

MUTATION\_DETECTED

PRIMARY\_STDERR

PRIMARY\_STDOUT\_PATTERN

EXPECTED\_FAIL\_BUT\_PASSED

SCHEMA\_MISMATCH

VOCAB\_MISMATCH

TOOL\_ERROR

GIT\_UNAVAILABLE

UNKNOWN



FAIL\_KIND Vocabulary (authoritative list, v1.3.0)

PRIMARY\_FAILED

MUTATION\_DETECTED

PRIMARY\_STDERR

PRIMARY\_STDOUT\_PATTERN

EXPECTED\_FAIL\_BUT\_PASSED

SCHEMA\_MISMATCH

VOCAB\_MISMATCH

TOOL\_ERROR

GIT\_UNAVAILABLE

UNKNOWN



Vocabulary Rules

All FAIL\_KIND values:

&nbsp; - uppercase

&nbsp; - characters: A-Z 0-9 underscore

&nbsp; - no spaces

&nbsp; - must appear in this list

Adding or removing a FAIL\_KIND requires schema\_version bump.



Determinism Rules

Encoding: UTF-8

Key ordering: sorted

JSON formatting: deterministic

Newline: single newline at EOF

Hash values: lowercase hex

Schema structure changes require schema\_version increment.



Meaning Notes



EXPECTED\_FAIL\_BUT\_PASSED

A test case marked as expected failure was verified as success.

Indicates sample integrity breach.

This is a diagnostic integrity signal, not a repair action.



PRIMARY\_FAILED

Primary verifier returned non-zero exit code.



MUTATION\_DETECTED

Working tree mutation detected before or after primary run.



SCHEMA\_MISMATCH

Governance schema\_version does not match tool implementation.



VOCAB\_MISMATCH

FAIL\_KIND value not listed in governance vocabulary.



TOOL\_ERROR

Internal Shadow tool failure.



Operational Standard (Windows PowerShell)



Write Shadow report as UTF-8 without BOM:



$j=(python shadow\\verify\_all\_shadow.py --primary verify\_pack\_v4\_sample/verify\_all\_v4.py)

\[System.IO.File]::WriteAllText((Resolve-Path .\\outbox\\shadow\_last.json),$j,(New-Object System.Text.UTF8Encoding($false)))



Parse with UTF-8:



python -c "import json; r=json.load(open(r'outbox\\shadow\_last.json','r',encoding='utf-8')); print('OK', r\['schema\_version'], r\['result']\['ok'], r\['io']\['stdout']\['trimmed'], r\['io']\['stdout']\['total\_lines'])"


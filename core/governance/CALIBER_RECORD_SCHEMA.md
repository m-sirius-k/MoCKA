CALIBER\_RECORD\_SCHEMA

Frozen Contract

Status: FROZEN

schema\_version: 0.2.0



Purpose

Caliber record is a minimal, deterministic, machine-friendly abstraction

derived strictly from a valid Shadow report.

Caliber never modifies Shadow, Primary, or repository state.



Authority

Shadow report is the only input source.

Governance schema\_version must match tool implementation.



Top-Level Required Keys

schema\_version (string)

generated\_at\_utc (string, RFC3339 UTC)

source (object)

signals (object)

evidence (array)



source

shadow\_report\_id (string)

shadow\_schema\_version (string)

shadow\_tool (object)

primary\_verifier (string)

primary\_exit\_code (int or null)



signals

ok (boolean)

fail\_kinds (array of string)

mutation\_detected (boolean)

stdout\_sha256 (string, lowercase hex, 64 characters)

stderr\_sha256 (string, lowercase hex, 64 characters)

summary (string, short deterministic phrase)



evidence (array of objects)

kind (string)

evidence\_sha256 (string, lowercase hex, 64 characters)



Fail\_Kinds Vocabulary

Fail kinds must be derived from governance/SHADOW\_REPORT\_SCHEMA.md.

No hardcoded vocabulary allowed.

Any value outside governance vocabulary is a fatal error.



Determinism Rules

Encoding: UTF-8

Key ordering: sorted

Formatting: deterministic JSON

Newline: single newline at EOF

Hash format: lowercase hex

Schema structure change requires schema\_version bump.



Operational Standard (Windows PowerShell)



Caliber is derived only from Shadow:



$j=(python shadow\\verify\_all\_shadow.py --primary verify\_pack\_v4\_sample/verify\_all\_v4.py)

\[System.IO.File]::WriteAllText((Resolve-Path .\\outbox\\shadow\_last.json),$j,(New-Object System.Text.UTF8Encoding($false)))



python caliber\\extract\_caliber\_record.py --shadow-report outbox\\shadow\_last.json --out outbox\\caliber\_last.json



Validation example:



python -c "import json; r=json.load(open(r'outbox\\caliber\_last.json','r',encoding='utf-8')); print('CALIBER', r\['schema\_version'], r\['signals']\['ok'], r\['signals']\['fail\_kinds'])"



Restrictions

Caliber must not:

\- modify Shadow report

\- alter Primary artifacts

\- access network resources

\- auto-repair data


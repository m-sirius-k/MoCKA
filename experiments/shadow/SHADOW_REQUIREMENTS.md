# Movement Shadow Requirements (Private)

## Purpose
Shadow exists only for diagnostics when Primary integrity is compromised.

## Non-Goals
- No repair
- No rewrite
- No bypass
- No exception approvals
- No alternative truth

## Allowed Outputs
- diagnostic report
- minimal evidence package
- reproduction steps

## Mandatory Constraints
- read-only against Primary artifacts
- MUST NOT modify Primary files
- MUST NOT create artifacts that claim Primary equivalence

## Repository Hygiene
- shadow/reports/* is runtime output and SHOULD NOT be committed (except a one-time proof record).


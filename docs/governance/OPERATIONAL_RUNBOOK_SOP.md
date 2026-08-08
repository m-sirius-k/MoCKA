# Operational Runbook SOP

## 1. Purpose

This document defines the human operational response procedure when a FAIL-CLOSED condition is detected.

The purpose is preservation of evidence integrity and prevention of uncontrolled recovery actions.

## 2. Scope

Applicable to:

- Event integrity failures
- Signature and evidence inconsistency
- Runtime boundary violations
- Governance validation failures

## 3. Human Response Procedure

### Step 1: Stop

Stop affected operations.

Do not attempt automatic recovery.

### Step 2: Preserve Evidence

Preserve:

- Event records
- Runtime logs
- Decision references
- Environment state

### Step 3: Duplicate Investigation Copy

Create an analysis copy.

Original evidence remains immutable.

### Step 4: Analyze

Review:

- Evidence integrity
- Decision Ledger relation
- Applicable governance rules

### Step 5: Human Decision Record

Only Human Authority may determine:

- Recovery approval
- Additional investigation
- Permanent rejection

## 4. Forbidden Actions

- Direct evidence modification
- Ledger rewriting
- Unauthorized schema change
- Automated approval

## 5. Recovery Criteria

Recovery requires confirmed Human Authority decision and preserved audit trace.

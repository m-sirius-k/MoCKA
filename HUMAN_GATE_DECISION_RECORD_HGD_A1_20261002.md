# HUMAN_GATE_DECISION_RECORD_HGD_A1

**Document ID**: HGDR_HGD_A1_20261002  
**Date**: 2026-10-02  
**Prepared by**: KUROKO  
**Status**: PENDING CONFIRMATION  
**Revision**: 2 (2026-10-02 — Authorization Flow and Class Separation fixed)  
**Supersedes**: HGD_A1_AUTH_PROPAGATION_DECISION_PACKAGE.md (analysis document)  
**References**: DC_20261002_PHASE5_1_A_REMEDIATION, PHASE5_1_A_C1_STAGE1_VERIFICATION_REPORT.md

---

## 1. Current State

### What C1 Stage 1 Verified

Test 1 confirmed: any write tool call without `decision_id` is blocked at
GL8_FAIL_1_MISSING_DECISION_ID. This is a verified DENY.

Test 2 confirmed: when `decision_id` is present and valid (Active decision,
authorized approver, correct scope, matching content_hash, registered tool,
UTF-8 ledger), the pipeline returns AUTHZ_OK. This is a verified ALLOW.

### What C1 Stage 1 Did NOT Verify

- That the `_authz` envelope extraction (proposed in Option A) works in GL8/GL9
- That READ_ONLY_TOOLS bypass (proposed in Option B) is correctly wired
- FAIL_2 through FAIL_5 scenarios remain untested
- No production environment verification

### GAP-2 Confirmed Active

Standard MoCKA tool calls do NOT include `decision_id`. The Authorization
Pipeline as deployed (commit 916bef7) blocks ALL write tools at GL8_FAIL_1.
GAP-2 is a verified, blocking operational gap.

### Infrastructure UNKNOWN

UNKNOWN-1 from C1 Stage 1: the Decision Ledger path in GL8 hardcodes
`/home/user/MoCKA/data/decisions/decision_ledger.jsonl`. In the cloud
container, this file is empty. If production runs in the cloud container,
GL8 would return FAIL_2 (decision not found) even with correct decision_id.

This UNKNOWN does NOT change the GAP-2 design decision. It is an
environment configuration concern for the production deployment gate (Step 4).

---

## 2. Decision Question

How should Authorization Context (decision_id and scope) be conveyed to the
GL8-GL12 pipeline for write tool executions, without:
a. Changing existing MoCKA tool signatures (breaking API compatibility)
b. Blocking read-only tool operations (operational regression)
c. Introducing new modules beyond DC_20261002_GL8_GL12_ARCHITECTURE scope
d. Allowing AI/Tool caller to self-generate Human Gate authority

---

## 3. Human Gate Authority Chain (Fixed)

This section defines the mandatory authority flow. Implementation MUST
preserve this chain without shortcutting.

```
Human Gate Decision (きむら博士)
         |
         v
Decision Ledger (data/decisions/decision_ledger.jsonl)
    [decision_id, status=Active, approved_by=きむら博士]
         |
         v
Authorization Context Generation (KUROKO or human operator)
    - References an existing, Active decision_id
    - Does NOT create or modify decisions
    - Cannot fabricate authority: GL8 verifies against the Ledger
         |
         v
_authz Envelope (packaged in tool args)
    args["_authz"] = {
        "decision_id": "<existing Active decision_id>",
        "scope": ["data", "events"]
    }
         |
         v
GL8 Verification (Human Gate Authorization Integrity)
    - Looks up decision_id in Decision Ledger
    - Confirms status=Active
    - Confirms approved_by in AUTHORIZED_APPROVERS (きむら博士)
         |
         v
GL9 Verification (Authorization Scope Binding)
    - Confirms requested scope is subset of authorized scope
         |
         v
GL10 / GL11 / GL12 Verification
         |
         v
Tool Execution (if all layers pass)
```

### Prohibition: AI Self-Generated Human Gate Authority

The following is PROHIBITED in any implementation:

- KUROKO calling mocka_decision_write() and then immediately using the
  resulting decision_id as `_authz.decision_id` in a write operation
- Any mechanism that bypasses the requirement for the Human Gate decision
  to pre-exist in the Decision Ledger before being referenced in `_authz`
- Any code that generates, caches, or automatically refreshes `_authz`
  context without explicit human operator input
- Treating `_authz` envelope presence as proof of authorization (GL8 MUST
  verify the referenced decision exists and is Active)

The authority chain is: Human Gate decides -> KUROKO references. Not:
KUROKO decides -> KUROKO references.

---

## 4. Class-Based Authorization Context Separation

The B+A design implements Class-based Authorization Context Separation.
This section clarifies the class boundaries.

### Class Definition

```
Class A: READ_ONLY_TOOLS
  - Tools that only read state (no side effects)
  - Authorization Pipeline bypassed (AUTHZ_BYPASS_READ_ONLY)
  - Still subject to GL1-GL7 governance pipeline
  - Examples: mocka_get_overview, mocka_list_events, Read, Glob

Class B: WRITE_TOOLS (default)
  - All tools NOT in READ_ONLY_TOOLS
  - Full GL8-GL12 Authorization Pipeline required
  - Must supply _authz envelope with valid decision_id and scope
  - Examples: mocka_write_event, mocka_add_todo, Write, Edit, Bash
```

### Critical Distinctions

**READ is NOT Authorization Bypass**:
READ_ONLY_TOOLS do not bypass security — they bypass the authorization
requirement because they create no persistent state change. They remain
subject to GL1-GL7 (grounding, thinking mode, governance checks). There is
no expanded privilege for read tools; they are simply not subject to the
Human Gate authorization requirement.

**WRITE is NOT the only Authorization Class**:
The class structure is binary today (READ vs WRITE). Future extensions may
introduce additional classes (e.g., EXTERNAL_CALL, SCHEMA_CHANGE). The
implementation must not hardcode the assumption that only two classes exist.
The `READ_ONLY_TOOLS` set defines what is exempt; everything else is governed.

**Class Assignment is a Governance Decision**:
Moving a tool from Class A (READ) to Class B (WRITE) or vice versa requires
a CHANGE_START/CHANGE_DONE governance record. The `READ_ONLY_TOOLS` set is
a governance artifact, not an engineering convenience.

---

## 5. Selected Option: B+A Combined

**Option B (READ_ONLY_TOOLS Class Bypass)**:
Read-only tools skip the Authorization Pipeline entirely.
Reuses existing `READ_ONLY_TOOLS` set from governance_pipeline.py.

**Option A (_authz Envelope Field)**:
Write tools pass authorization context via reserved `_authz` dict in args.

```python
# Option B: READ bypass in authorization_pipeline.py
READ_ONLY_TOOLS = {
    "mocka_get_overview", "mocka_get_essence", "mocka_get_todo",
    "mocka_list_events", "mocka_read_event", "mocka_search",
    "mocka_get_incidents", "mocka_get_guidelines", "mocka_get_command_center",
    "mocka_check_utf8", "mocka_registry_get", "mocka_registry_current_state",
    "mocka_decision_get", "mocka_decision_list",
    "mocka_integrity_get", "mocka_integrity_list",
    "Read", "Glob", "Grep",
}

def execute(self, tool_name: str, args: dict) -> AuthorizationDecision:
    if tool_name in READ_ONLY_TOOLS:
        return AuthorizationDecision(
            allowed=True,
            tool_name=tool_name,
            failure_code="AUTHZ_BYPASS_READ_ONLY"
        )
    # ... GL8-GL12 pipeline for write tools
```

```python
# Option A: _authz envelope extraction in GL8
def verify_authorization(self, tool_name: str, args: dict) -> GL8Result:
    authz = args.get("_authz", {})
    decision_id = authz.get("decision_id")
    ...

# Option A: _authz envelope extraction in GL9
def verify_scope_binding(self, authorized_scope, args: dict) -> GL9Result:
    authz = args.get("_authz", {})
    requested_scope = authz.get("scope", [])
    ...
```

```python
# Caller provides authorization context (per operation):
# The decision_id MUST be an existing, Active decision in the Ledger.
# KUROKO cannot create a decision and immediately use it.
args = {
    "title": "event title",
    "description": "...",
    "_authz": {
        "decision_id": "DC_20261002_GL8_GL12_ARCHITECTURE",  # pre-existing Active decision
        "scope": ["data", "events"]
    }
}
```

**Why B+A combined**:
- Option B alone: write tools still blocked (no decision_id path)
- Option A alone: read tools still blocked at GL8_FAIL_1 (no decision_id)
- B+A: read tools bypass pipeline (zero regression); write tools require
  explicit `_authz` envelope (per-operation authorization traceability)

**Why NOT Option C (Session-level)**:
- Architectural expansion beyond approved scope
- Session lifecycle management required (new module)
- A compromised session could execute all authorized writes

**Why NOT Option D (GL11-first)**:
- Requires GAP-5 registry completion as prerequisite
- Higher dependency chain risk

---

## 6. Authority Boundary

### Before B+A Implementation

```
ALL tool calls -> GL8 -> GL8_FAIL_1 (no decision_id in args)
Result: COMPLETE OPERATIONAL BREAKDOWN
```

### After B+A Implementation

```
Read tools (Class A) -> AUTHZ_BYPASS_READ_ONLY -> GL1-GL7 (no regression)

Write tools (Class B) with valid _authz ->
  GL8: decision_id found in Ledger, Active, authorized approver -> GL8_OK
  GL9: requested scope subset of authorized scope -> GL9_OK
  GL10: content hash matches -> GL10_OK
  GL11: tool in registry -> GL11_OK
  GL12: ledger UTF-8 -> GL12_OK
  -> ALLOW -> GL1-GL7 -> execute

Write tools (Class B) without _authz ->
  GL8: args["_authz"] absent -> decision_id=None -> GL8_FAIL_1 -> DENY
```

### What Changes

- authorization_pipeline.py: +15 lines (READ_ONLY_TOOLS check at entry)
- human_gate_authorization_integrity.py: +5 lines (read from args["_authz"])
- authorization_scope_binding.py: +3 lines (read from args["_authz"])
- governance_pipeline.py: BOM strip only (GAP-4, same commit scope)

### What Does NOT Change

- GL8-GL12 engine verification logic (algorithms unchanged)
- GL1-GL7 governance pipeline behavior
- Decision Ledger schema and storage
- Human Gate approval process for decisions
- AUTHORIZED_APPROVERS set (きむら博士)
- Existing read-only tool access (zero regression)

---

## 7. Allowed Scope (for Implementation when authorized)

Allowed when HGD-D1 Implementation Authorization is granted:

- Modify `structural/authorization_pipeline.py`:
  Add READ_ONLY_TOOLS bypass at entry of `execute()` method
  Total change: approximately +15 lines

- Modify `structural/human_gate_authorization_integrity.py`:
  Change `args.get("decision_id")` to `args.get("_authz", {}).get("decision_id")`
  Total change: approximately +5 lines

- Modify `structural/authorization_scope_binding.py`:
  Change `args.get("scope", [])` to `args.get("_authz", {}).get("scope", [])`
  Total change: approximately +3 lines

- Strip BOM from `structural/governance_pipeline.py` (GAP-4):
  Remove leading \xef\xbb\xbf from file (0 logic changes)

---

## 8. Prohibited Scope

- Changing GL8-GL12 verification logic (algorithms, FAIL codes, thresholds)
- Adding new FAIL scenarios beyond the existing GL8_FAIL_1-4 / GL9_FAIL_1-3
- Modifying `AUTHORIZED_APPROVERS` set in GL8
- Changing Decision Ledger schema or path
- Adding session-level authorization state (Option C scope)
- Activating the Authorization Pipeline in production
- Amending or rewriting commit 916bef7
- Changing GL11 TOOL_REGISTRY content (that is HGD-B1 scope)
- Modifying any file not listed in Allowed Scope above
- Creating or referencing a self-generated decision_id in _authz context
- Expanding READ_ONLY_TOOLS without CHANGE_START/CHANGE_DONE governance record

---

## 9. Implementation Preconditions

All must be satisfied before implementation begins:

1. HUMAN_GATE_DECISION_RECORD_HGD_A1_20261002.md: confirmed by きむら博士
2. HUMAN_GATE_DECISION_RECORD_HGD_B1_20261002.md: confirmed by きむら博士
3. HGD-D1 Implementation Authorization: granted by きむら博士
4. CHANGE_START event recorded before any file modification
5. UTF-8 check (via local Python3) on each modified file after change
6. CHANGE_DONE event recorded after file modification
7. Implementation Read-Back: verify modified files behave as expected
   on KUROKO PC (actual tool call environment) before declaring complete
8. git commit message: "fix(GL8-GL12): GAP-2/4 remediation (HGD-A1, Class-based Authorization Separation + Authz Envelope)"
9. git push to claude/youthful-gates-51qxdo only

### .gitignore Audit Not Required for This Decision

HGD-A1 modifies existing files in structural/. No new files in data/ or
other excluded directories. TODO_390 audit is required only for HGD-B1.

---

## Decision Status

```
HGD-A1 Design:          APPROVED (DC_20261002_PHASE5_1_A_REMEDIATION)
HGD-A1 C1 Stage 1:      VERIFIED (PHASE5_1_A_C1_STAGE1_VERIFICATION_REPORT.md)
Authorization Flow:      FIXED (Section 3 - Human Gate Authority Chain)
Class Separation:        FIXED (Section 4 - READ/WRITE class definitions)
HGD-A1 Implementation:  PENDING CONFIRMATION (this document)
HGD-D1:                 NOT YET CREATED (blocked until A1+B1 confirmed)
```

Registration as individual decision record in Decision Ledger is pending
until きむら博士 confirms this document.

KUROKO will call `mocka_decision_write(decision_id="DC_20261002_HGD_A1_IMPLEMENTATION_SCOPE")` upon explicit confirmation.

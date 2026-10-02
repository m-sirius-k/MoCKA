# PHASE 5.1-A Remediation Design

**Status**: IMPLEMENTATION COMPLETE / VERIFICATION BLOCKED  
**Verified at**: 2026-10-02  
**Author**: KUROKO  
**Basis**: PHASE 5.1-A Implementation Verification Report  
**Decision Reference**: DC_20261002_GL8_GL12_ARCHITECTURE  
**Constraint**: Design Only. No code change. No commit. No runtime modification.

---

## Background

PHASE 5.1-A Verification identified 3 blocking gaps that prevent GL8-GL12
Authorization Pipeline from functioning as Runtime Enforcement:

- GAP-2: All tool calls would be blocked at GL8_FAIL_1 (no decision_id)
- GAP-5: 16+ current MoCKA tools not in GL11 registry (unknown tool = DENY)
- GAP-3: Integration tests are empty stubs. FAIL 1-5 blocking is unverified.

This document defines the Remediation Contracts for each gap. Remediation
implementation requires new Human Gate approval before any code change.

---

## GAP-2: Authorization Context Propagation Contract

### 1. Current Contract (as implemented in 916bef7)

```
AuthorizationPipeline.execute(tool_name, args) runs for ALL tool calls.
GL8.verify_authorization() requires args.get("decision_id") to be non-empty.
GL9.verify_scope_binding() requires args.get("scope") to be non-empty.

Current MoCKA tool call signature:
  mocka_write_event(title, description, tags, author)
  mocka_get_overview()
  ... (no decision_id, no scope field)
```

Contract gap: The Authorization Pipeline contract assumes all tool calls
carry `decision_id` and `scope`. The MoCKA MCP API contract does NOT.
These two contracts are incompatible.

### 2. Root Cause

Two architectural assumptions were not reconciled at design time:

(a) Assumption A (Authorization Pipeline): "Every tool execution must be
    traceable to an authorized Human Gate decision via decision_id."

(b) Assumption B (Existing MCP API): "Tool args contain only functional
    parameters (title, description, tags, author, keyword, etc.)."

No bridging contract was defined between A and B.
GL9's `scope` requirement has the same structural gap: scope is an
authorization concept, not a functional parameter.

The design correctly identified that authorization context must accompany
tool execution but did not define HOW that context is conveyed to the
pipeline without modifying every tool's existing arg schema.

### 3. Fix Candidates

**Option A: Authorization Envelope Field**

Add a reserved field `_authz` to tool args, carrying authorization context
as a nested object. Example:

```python
args = {
    "title": "some event",
    "description": "...",
    "_authz": {
        "decision_id": "DC_20261002_GL8_GL12_ARCHITECTURE",
        "scope": ["data", "events"]
    }
}
```

GL8/GL9 extract from `args.get("_authz", {})` instead of top-level.
Existing tools remain backward-compatible (missing `_authz` = no change).
Authorization context is injected by the caller (KUROKO session) before
each write operation, not by MCP tool definitions.

Strength: Clean separation. No tool signature change. Auditable.
Weakness: Caller must always supply `_authz` for write tools. Forgetting
it still triggers GL8_FAIL_1. Enforcement depends on caller discipline.

**Option B: Tool-Class Based Bypass (Recommended baseline)**

Classify tools into two classes before executing GL8-GL12:

- Class READ: READ_ONLY_TOOLS (existing set in governance_pipeline.py)
  -> GL8-GL12 skipped entirely. Proceed directly to GL1-GL7.
- Class WRITE: all other tools
  -> GL8-GL12 applied. decision_id required.

```python
# In AuthorizationPipeline.execute() or GovernancePipeline.before_tool():
if tool_name in READ_ONLY_TOOLS:
    return AuthorizationDecision(allowed=True, tool_name=tool_name,
                                  failure_code="AUTHZ_BYPASS_READ_ONLY")
# else: run GL8-GL12
```

READ_ONLY_TOOLS is already defined and maintained in governance_pipeline.py.
No new concept required. Decision_id is required only for write operations.

Strength: Minimal change. Preserves existing read behavior. Clear policy.
Weakness: READ_ONLY_TOOLS list must be kept in sync. Read tool misclassified
as write would still require decision_id. GL9 scope still needed for writes.

**Option C: Session-Level Authorization Token**

Authorization is established once per session and stored in GovernancePipeline
state. Individual tool calls look up the active session authorization.

```python
# Session init:
pipeline.authorize_session(decision_id="DC_...", scope=[...])

# Per-tool: GL8 reads session authorization, not args
```

Strength: Clean UX. No per-call burden.
Weakness: New session management layer. Complex lifecycle. Higher risk of
session scope leakage.

**Option D: GL11 requires_authorization Flag as GL8 Bypass**

GL11 registry already has `requires_authorization` per tool.
Use this flag: if requires_authorization=False in GL11, skip GL8-GL9.

```python
# In AuthorizationPipeline.execute():
metadata = gl11.get_tool_metadata(tool_name)
if metadata and not metadata.requires_authorization:
    return AuthorizationDecision(allowed=True, ...)
```

Strength: Reuses existing registry data. No new concept.
Weakness: GL11 must run BEFORE GL8 (reverses current order). GL11 "unknown
tool" case: no metadata -> what is the default? Fail-closed would still
block all unlisted tools at step 0.

### 4. Scope Impact

| Option | Files changed | Scope boundary |
|--------|--------------|----------------|
| A: Envelope | authorization_pipeline.py (+12L), human_gate_authorization_integrity.py (+8L), authorization_scope_binding.py (+5L) | Within GL8-GL9 scope |
| B: Class Bypass | authorization_pipeline.py (+10L) or governance_pipeline.py (+6L) | Within approved scope |
| C: Session Token | governance_pipeline.py (+40L), new session_authorization.py | SCOPE EXPANSION - new module |
| D: GL11-first | authorization_pipeline.py (reorder logic, +15L) | Within approved scope |

Options A and B are within the scope of DC_20261002_GL8_GL12_ARCHITECTURE.
Options C and D require Human Gate review of architectural change.

GAP-2 resolution is prerequisite for GAP-3 (integration tests cannot be
written correctly until the propagation contract is defined).

### 5. New Human Gate Decision Candidate: HGD-A1

**Title**: Authorization Context Propagation Contract Selection  
**Question**: Which Option (A/B/C/D) resolves GAP-2 while remaining within
              the approved DC_20261002_GL8_GL12_ARCHITECTURE scope?

**Recommended by KUROKO**: Option B (Class Bypass) as baseline.
Rationale: Minimal scope, uses existing READ_ONLY_TOOLS contract, no new
concept. Can be combined with Option A for write-tool traceability if needed.

**Required before**: Any code change to resolve GAP-2.

---

## GAP-5: Tool Registry Coverage Contract

### 1. Current Contract (as implemented in 916bef7)

GL11 TOOL_REGISTRY has 11 entries:

```
mocka_get_overview      (ACTIVE, requires_authorization=False)
mocka_get_todo          (ACTIVE, requires_authorization=False)
mocka_get_essence       (ACTIVE, requires_authorization=False)
mocka_write_event       (ACTIVE, requires_authorization=True)
mocka_decision_write    (ACTIVE, requires_authorization=True)
mocka_decision_get      (ACTIVE, requires_authorization=False)
mocka_decision_list     (ACTIVE, requires_authorization=False)
mocka_check_utf8        (ACTIVE, requires_authorization=False)
Write                   (ACTIVE, requires_authorization=True)
Edit                    (ACTIVE, requires_authorization=True)
Read                    (ACTIVE, requires_authorization=False)
```

Contract gap: Unknown tools -> GL11_FAIL_1_UNKNOWN_TOOL (DENY).
Current MoCKA server exposes 25+ tools. 16+ are unregistered.

### 2. Root Cause

TOOL_REGISTRY was hand-authored at implementation time with only the tools
directly relevant to the PHASE 5.1-A scenario. No systematic enumeration
of all MoCKA MCP tools was performed.

Missing tools (confirmed from mocka_mcp_server.py and MCP tool listings):

```
mocka_add_todo          (write, requires_authorization=True)
mocka_update_todo       (write, requires_authorization=True)
mocka_seal              (write, requires_authorization=True)
mocka_list_events       (read,  requires_authorization=False)
mocka_read_event        (read,  requires_authorization=False)
mocka_search            (read,  requires_authorization=False)
mocka_get_guidelines    (read,  requires_authorization=False)
mocka_get_command_center (read, requires_authorization=False)
mocka_get_incidents     (read,  requires_authorization=False)
mocka_integrity_write   (write, requires_authorization=True)
mocka_integrity_get     (read,  requires_authorization=False)
mocka_integrity_list    (read,  requires_authorization=False)
mocka_decision_write    (write, requires_authorization=True) [already listed]
mocka_registry_get      (read,  requires_authorization=False)
mocka_registry_current_state (read, requires_authorization=False)
mocka_registry_add      (write, requires_authorization=True)
Bash                    (write, requires_authorization=True)
Glob                    (read,  requires_authorization=False)
Grep                    (read,  requires_authorization=False)
```

Additionally, the TOOL_REGISTRY is a hardcoded class variable. Adding a tool
requires modifying tool_registry_enforcement.py source code each time.

### 3. Fix Candidates

**Option A: Manual Registry Completion**

Add all missing tools to TOOL_REGISTRY in tool_registry_enforcement.py.

```python
TOOL_REGISTRY = {
    # ... existing 11 entries ...
    "mocka_add_todo": ToolMetadata(
        name="mocka_add_todo",
        status=ToolLifecycleStatus.ACTIVE,
        requires_authorization=True,
        description="Add new TODO item"
    ),
    "mocka_update_todo": ToolMetadata(...),
    # ... complete list
}
```

Strength: Simple. Explicit. Auditable.
Weakness: Manual maintenance. Every new tool requires a code change.

**Option B: Registry Schema File (Recommended)**

Extract TOOL_REGISTRY to a JSON file loaded at startup.

```
data/governance/tool_registry.json
{
  "tools": [
    {"name": "mocka_write_event", "status": "ACTIVE",
     "requires_authorization": true, "description": "..."},
    ...
  ]
}
```

ToolRegistryEnforcementEngine loads from file on __init__().
New tools added by updating the JSON (no code change required).
tool_registry.json is versioned and auditable.

Strength: Maintainable. Data-driven. No code change per tool addition.
Weakness: File load path must be stable. JSON schema must be validated.

**Option C: Auto-Discovery from MCP Server**

ToolRegistryEnforcementEngine calls mocka_mcp_server's tool listing
endpoint to populate its registry at startup.

```python
def __init__(self):
    response = requests.get("http://localhost:5002/tools")
    for tool in response.json():
        self.TOOL_REGISTRY[tool["name"]] = ToolMetadata(...)
```

Strength: Always in sync. Zero maintenance.
Weakness: Circular dependency (GL11 inside MCP server calling MCP server).
Runtime dependency on server being up at pipeline init time.

**Option D: Default-Permit with Explicit Deny List**

Flip from fail-closed to: unknown tools are WARN+AUDIT (not DENY).
Only explicitly DISABLED tools are blocked.

```python
metadata = self.TOOL_REGISTRY.get(tool_name)
if not metadata:
    # Unknown tool: log audit event, ALLOW with WARNING
    return GL11Result(allowed=True, failure_code="GL11_WARN_UNREGISTERED")
```

Strength: No operational disruption.
Weakness: Weakens security model. Changes from deny-by-default to
permit-by-default. Requires explicit Human Gate approval for this policy change.

### 4. Scope Impact

| Option | Files changed | Scope boundary |
|--------|--------------|----------------|
| A: Manual completion | tool_registry_enforcement.py (+80-120L) | Within approved scope |
| B: Schema file | tool_registry_enforcement.py (+30L) + new data/governance/tool_registry.json | New data file - within scope |
| C: Auto-discovery | tool_registry_enforcement.py (+20L) | Circular dependency risk |
| D: Default-permit | tool_registry_enforcement.py (+10L) | POLICY CHANGE - requires Human Gate |

Option A or B are within DC_20261002_GL8_GL12_ARCHITECTURE scope.
Option D changes the security model and requires separate Human Gate approval.

Note: GAP-5 is partially dependent on GAP-2 resolution. If Option B
(Class Bypass) is selected for GAP-2, read-only tools skip GL11 entirely,
reducing the registry gap to write-only tools only (9 tools instead of 20+).

### 5. New Human Gate Decision Candidate: HGD-B1

**Title**: Tool Registry Coverage Strategy  
**Question**: Option A (manual complete) or Option B (schema file) for
              completing GL11 TOOL_REGISTRY coverage?

**Recommended by KUROKO**: Option B (Schema file) if GAP-2 is resolved
via Option B (Class Bypass). Read-only tools skip GL11, limiting registry
to write tools only. Schema file for write tools is manageable and
maintainable.

If GAP-2 is NOT resolved with bypass, Option A (manual) is needed as
immediate remediation while Option B is designed for the long term.

**Required before**: Any code change to resolve GAP-5.

---

## GAP-3: Integration Test Real Execution Contract

### 1. Current Contract (as implemented in 916bef7)

test_authorization_pipeline_integration.py defines 15+ test classes and
methods covering FAIL_1-5, E2E, and Performance scenarios.

All method bodies are `pass`. pytest returns 0 (all pass) but no assertions
are executed. This is a structural integrity violation: tests exist in name
but not in substance.

Unit tests (test_gl8_human_gate_authorization.py) are REAL (7 tests with
assertions, fixture setup, mock Decision Ledger). Only integration tests
are stubs.

### 2. Root Cause

Integration tests require a functioning Authorization Pipeline end-to-end.
At the time of commit 916bef7, the pipeline had the GAP-2 and GAP-5 issues.
Writing integration tests against a broken pipeline would result in all
tests failing at GL8_FAIL_1 (no decision_id), not at the intended FAIL_1-5
scenarios. Rather than deferring the commit or accepting all-red tests,
the stubs were committed.

This is a documentation integrity violation: the commit message states
"30+ test cases" and "FAIL_1-5 scenarios per PHASE 5.0-C investigation"
implying verification, when the actual verification coverage is zero.

Dependency chain:
```
GAP-3 (integration tests) depends on
  GAP-2 (propagation contract) which determines
    HOW decision_id is conveyed for test scenarios
      -> which affects test fixture setup for all integration tests
```

### 3. Fix Candidates

**Option A: Integration Test Full Implementation (Sequential)**

Wait for GAP-2 and GAP-5 to be resolved. Then implement all integration
test stubs with real assertions.

Minimum requirements per test:
- FAIL_1: create args without decision_id -> assert pipeline returns DENY
           with GL8_FAIL_1_MISSING_DECISION_ID
- FAIL_2: create args with valid decision_id but out-of-scope scope ->
           assert GL9_FAIL_3_SCOPE_MISMATCH
- FAIL_3: create tampered decision record (content != hash) ->
           assert GL10_FAIL_4_HASH_MISMATCH_TAMPERING_DETECTED
- FAIL_4: call unregistered tool name ->
           assert GL11_FAIL_1_UNKNOWN_TOOL
- FAIL_5: create BOM-encoded decision_ledger.jsonl ->
           assert GL12 encoding failure
- Happy path: all fields valid -> assert pipeline returns ALLOW

Each test needs:
1. A mock/temp Decision Ledger with controlled decision records
2. Control over file encoding (for FAIL_5)
3. AuthorizationPipeline instance using the mock ledger

Strength: Complete verification.
Weakness: Blocked by GAP-2/GAP-5 resolution. Timeline: after those remediation.

**Option B: Staged Stub Replacement**

Replace stubs in priority order:
Stage 1 (immediate): FAIL_1 only (does NOT require GAP-2 resolution,
because FAIL_1 is deliberately triggered by omitting decision_id).
Stage 2: FAIL_3, FAIL_4, FAIL_5 (do not require full propagation contract).
Stage 3: FAIL_2, E2E, Performance (require GAP-2 resolution).

Strength: Begins verification immediately. Partial coverage quickly.
Weakness: Multi-stage complexity. Risk of partial coverage being
misrepresented as complete.

**Option C: Separate Verification Script (Non-pytest)**

Create verification/phase5_1_a_verify.py as a standalone script
(not pytest) that performs the 5 blocking scenario checks using the
actual production Decision Ledger and pipeline. Output: structured
VERIFICATION_RESULT.json.

Strength: Can be run as an operational verification, not just a test.
Weakness: Not integrated into standard test suite. Separate maintenance.

### 4. Scope Impact

| Option | Files changed | Prerequisite |
|--------|--------------|--------------|
| A: Full implementation | test_authorization_pipeline_integration.py (full rewrite) | GAP-2 + GAP-5 resolved |
| B: Staged | test_authorization_pipeline_integration.py (partial updates per stage) | Stage 1 standalone; Stage 2+ needs partial GAP-2/5 |
| C: Verification script | new verification/phase5_1_a_verify.py | Partial GAP-2 needed |

All options are within DC_20261002_GL8_GL12_ARCHITECTURE scope.

Commit message integrity violation note: The existing commit message
("30+ test cases") should be corrected in a follow-up commit note or
acknowledged in the Decision Ledger. No force-push or history rewrite
(TODO_382 prohibition).

### 5. New Human Gate Decision Candidate: HGD-C1

**Title**: Integration Test Remediation Sequencing  
**Question**: What is the minimum acceptance criterion for PHASE 5.1-A
              to be declared IMPLEMENTATION COMPLETE (not just
              IMPLEMENTATION COMPLETE / VERIFICATION BLOCKED)?

**Sub-question 1**: Is Stage 1 of Option B (FAIL_1 test only, runnable
now) sufficient to unblock the VERIFICATION BLOCKED status?

**Sub-question 2**: Does the commit message inaccuracy require a formal
Decision Ledger record of the discrepancy?

**Recommended by KUROKO**:
- Minimum criterion: FAIL_1-5 all have real assertions (not pass)
- Stage 1 of Option B can be done immediately (no GAP-2 dependency)
- Commit message discrepancy should be recorded in Decision Ledger
  (not in a code commit - in governance record only)

**Required before**: Declaring PHASE 5.1-A IMPLEMENTATION COMPLETE.

---

## Remediation Dependency Map

```
GAP-2 resolution
  Option B (Class Bypass) [Recommended]
    |
    +-> reduces GAP-5 scope from 20+ tools to ~9 write-only tools
    |     |
    |     +-> GAP-5 Option A or B (manual or schema file)
    |
    +-> unblocks GAP-3 Stage 2+ integration tests
          |
          +-> GAP-3 Option A or B Stage 2

GAP-3 Stage 1 (FAIL_1 test)
  No dependency. Can be executed immediately.
```

Recommended execution order:
1. HGD-C1: Approve GAP-3 Stage 1 immediately (FAIL_1 test only)
2. HGD-A1: Approve GAP-2 propagation contract (Option B recommended)
3. HGD-B1: Approve GAP-5 registry coverage (Option A/B depending on HGD-A1)
4. HGD-C1 completion: Approve GAP-3 full integration test after GAP-2+5

---

## Additional Gap Records (from Verification Report, design deferred)

**GAP-1 (Production Deployment)**: 916bef7 is on GitHub but not synced
to local production server. Deployment timing is a separate operational
decision after GAP-2/5/3 remediation.

**GAP-4 (BOM Contamination)**: governance_pipeline.py starts with UTF-8
BOM in the GitHub version. This violates TODO_333. Remediation: strip BOM
in a minimal targeted fix commit (one-line change). No design needed.
Recommend addressing in the same commit as GAP-2 fix.

**GAP-6 (GL12 unread)**: encoding_integrity.py not directly verified.
Should be read and verified before deployment.

**GAP-7 (GL9 scope)**: Partially resolved by GAP-2 Option B (read-only
tools skip GL9). For write tools, scope must be defined in the
_authz envelope (Option A) or session context (Option C).

**GAP-8 (Event search overflow)**: Minor operational issue. Not blocking.

---

## Document Status

This document is a Design-Only deliverable.  
No code has been changed. No commits made. No runtime modified.  
All remediation requires new Human Gate Decision approval before implementation.

Human Gate Decisions required:
- HGD-A1: GAP-2 propagation contract selection
- HGD-B1: GAP-5 registry coverage strategy selection
- HGD-C1: GAP-3 integration test minimum criterion and sequencing

Prepared by: KUROKO  
Date: 2026-10-02

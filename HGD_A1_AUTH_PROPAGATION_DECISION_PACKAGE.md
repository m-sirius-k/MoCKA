# HGD-A1: Authorization Context Propagation Contract Decision Package

**Package Type**: Human Gate Decision Draft  
**Status**: PENDING APPROVAL  
**Prepared by**: KUROKO  
**Date**: 2026-10-02  
**Reference**: GAP-2 in PHASE5_1_A_REMEDIATION_DESIGN.md  
**Unblocks**: GAP-5 scope reduction, GAP-3 Stage 2+

---

## Decision Question

Which Authorization Context Propagation method resolves GAP-2 while remaining
within the approved scope of DC_20261002_GL8_GL12_ARCHITECTURE?

---

## Background

### The Incompatibility

GL8 requires `decision_id` in tool args:
```python
decision_id = args.get("decision_id")
if not decision_id:
    return GL8Result(allowed=False, failure_code="GL8_FAIL_1_MISSING_DECISION_ID")
```

Current MoCKA tool calls do NOT include `decision_id`:
```python
mocka_write_event(title="...", description="...", tags="...", author="...")
# No decision_id field in standard MoCKA tool API
```

Result: Every MoCKA tool call fails at GL8_FAIL_1. The Authorization Pipeline,
as currently integrated into GovernancePipeline.before_tool(), would BLOCK ALL
operations if deployed to the production server.

### Scope of the Problem

Affected tool classes:
- WRITE tools (mocka_write_event, mocka_add_todo, etc.): Must have authorization
- READ tools (mocka_get_overview, mocka_search, etc.): Authorization intent unclear

The original DC_20261002_GL8_GL12_ARCHITECTURE decision rationale states:
"All 5 FAIL scenarios covered by GL8-GL12 verification contracts."
It does not explicitly specify whether READ tools require authorization.

---

## Option Comparison

### Option A: Authorization Envelope Field

**Mechanism**: Add reserved `_authz` field to tool args at call site.

```python
# Caller provides authorization context:
args = {
    "title": "event title",
    "_authz": {
        "decision_id": "DC_20261002_GL8_GL12_ARCHITECTURE",
        "scope": ["data", "events"]
    }
}
pipeline.execute("mocka_write_event", args)
```

```python
# GL8 modified to read from envelope:
authz = args.get("_authz", {})
decision_id = authz.get("decision_id")
```

**Authority Boundary Impact**:
- The decision_id source is the CALLER (KUROKO or human operator)
- Caller must explicitly supply a valid, active decision for each write operation
- Mis-supplying a decision_id (wrong scope) is caught by GL9
- This creates a per-operation authorization chain (traceable to decision)

**Runtime Impact**:
- Existing read tool calls (no `_authz`): GL8 receives empty authz -> FAIL_1
- Write tool calls: must be updated by caller to include `_authz`
- READ tools remain broken unless Class Bypass (Option B) is combined

**Recommendation as standalone**: NOT sufficient. Option A must be combined
with Option B (Class Bypass for reads) to be functional.

**Scope**: Within DC_20261002_GL8_GL12_ARCHITECTURE scope (modification of
arg extraction logic in GL8/GL9, no new modules).

---

### Option B: Tool-Class Based Bypass (READ_ONLY bypass)

**Mechanism**: Read-only tools bypass the Authorization Pipeline entirely.
Write tools continue through GL8-GL12.

```python
# In AuthorizationPipeline.execute() or GovernancePipeline.before_tool():
READ_ONLY_TOOLS = {
    "mocka_get_overview", "mocka_get_essence", "mocka_get_todo",
    "mocka_list_events", "mocka_read_event", "mocka_search",
    "mocka_get_incidents", "mocka_get_guidelines", "mocka_get_command_center",
    "mocka_check_utf8", "mocka_registry_get", "mocka_registry_current_state",
    "mocka_decision_get", "mocka_decision_list",
    "mocka_integrity_get", "mocka_integrity_list",
}  # Same set as existing READ_ONLY_TOOLS in governance_pipeline.py

def execute(self, tool_name: str, args: dict) -> AuthorizationDecision:
    if tool_name in READ_ONLY_TOOLS:
        return AuthorizationDecision(
            allowed=True,
            tool_name=tool_name,
            failure_code="AUTHZ_BYPASS_READ_ONLY"
        )
    # ... GL8-GL12 for non-read tools
```

**Authority Boundary Impact**:
- Read operations are NOT subject to Human Gate authorization verification
- This is consistent with the existing GovernancePipeline design (GL7 Dry Run
  also exempts READ_ONLY_TOOLS from execution governance)
- Write operations must carry authorization context (via Option A envelope)
- The boundary is: reading is free; writing requires Human Gate decision

**Runtime Impact**:
- Read tool calls: BYPASS Authorization Pipeline -> proceed to GL1-GL7 (same as today)
- Write tool calls: GL8-GL12 applied (requires `_authz` envelope via Option A)
- ZERO regression for existing read operations

**Combined with Option A**:
- Read tools: bypassed (Option B)
- Write tools: require `_authz` envelope (Option A)
- This combination is fully functional and maintains fail-closed for writes

**Scope**: Within DC_20261002_GL8_GL12_ARCHITECTURE scope. Minimal change:
+6-10 lines in authorization_pipeline.py. READ_ONLY_TOOLS set reuses existing.

---

### Option C: Session-Level Authorization Token

**Mechanism**: Authorization established once per GovernancePipeline session.
Individual tool calls look up active session authorization.

```python
class GovernancePipeline:
    def authorize_session(self, decision_id: str, scope: list):
        """Establish session-level authorization."""
        self._session_authz = {"decision_id": decision_id, "scope": scope}
        # Verify decision in GL8, store result in session state

    def before_tool(self, tool_name: str, args: dict):
        # GL8-GL12 use session authorization, not args
        authz_args = {**args, "_authz": self._session_authz}
        authz_decision = self.authorization_pipeline.execute(tool_name, authz_args)
```

**Authority Boundary Impact**:
- A single decision authorizes all operations within one session
- Session scope determines what the session can do (all writes within scope)
- Risk: session scope leakage (if session is compromised, all authorized writes
  could be executed without per-operation human oversight)
- Requires session lifecycle management (session start / end / expiry)

**Runtime Impact**:
- Requires GovernancePipeline to be called with authorize_session() before
  tool calls are made
- Existing caller code needs session initialization step
- Session state must be thread-safe if concurrent tool calls occur

**Scope**: Adds new module concept (session authorization). This is an
architectural expansion BEYOND DC_20261002_GL8_GL12_ARCHITECTURE scope.
Requires new Human Gate decision.

---

### Option D: GL11 requires_authorization Flag as Bypass

**Mechanism**: Check GL11 registry FIRST. If tool has requires_authorization=False,
skip GL8-GL9. Otherwise apply full GL8-GL12.

```python
def execute(self, tool_name: str, args: dict) -> AuthorizationDecision:
    # Pre-check: does this tool require authorization?
    metadata = self.gl11.get_tool_metadata(tool_name)
    if metadata is None:
        # Unknown tool: fail-closed
        return AuthorizationDecision(allowed=False, failure_code="GL11_FAIL_1_UNKNOWN_TOOL")
    if not metadata.requires_authorization:
        # Tool explicitly does not require authorization
        return AuthorizationDecision(allowed=True, tool_name=tool_name,
                                      failure_code="AUTHZ_BYPASS_NO_AUTH_REQUIRED")
    # Full GL8-GL12 pipeline
```

**Authority Boundary Impact**:
- requires_authorization=False is a claim in the GL11 registry
- Anyone who can modify tool_registry_enforcement.py can bypass GL8
- This moves authorization bypass control into a data definition (safer to audit)
- Unknown tools are blocked at entry (fail-closed for unknowns)

**Runtime Impact**:
- GL11 must run BEFORE GL8 (current order: GL8->GL9->GL10->GL11->GL12)
- Reorders execution: GL11 pre-check -> GL8-GL12 for authorized tools
- Solves both GAP-2 (read tools skip GL8) and partially GAP-5 (unknown tools caught)
- Still requires GAP-5 fix: unknown tools blocked by GL11 pre-check

**Scope**: Execution order change in authorization_pipeline.py. Within approved scope.
Requires GL11 full registry coverage (GAP-5) to avoid blocking unknown tools.

---

## Option Comparison Matrix

| Criterion | A: Envelope | B: Bypass (Rec) | C: Session | D: GL11-first |
|-----------|------------|-----------------|------------|---------------|
| Resolves read-tool blocking | No (partial) | YES | YES | YES (if registry complete) |
| Resolves write-tool blocking | YES | Partial (needs A) | YES | YES (needs A for args) |
| Within approved scope | YES | YES | NO | YES |
| Minimal code change | YES (+15L) | YES (+10L) | NO (+60L+new) | YES (+20L) |
| Audit trail per operation | YES | Partial | Partial | Partial |
| Requires GAP-5 first | No | No | No | YES |
| Production risk | Low | Low | Medium | Low-Medium |

**KUROKO Recommendation**: Option B + Option A combined.

- Option B handles read tools (zero regression, reuses existing READ_ONLY_TOOLS)
- Option A handles write tools (explicit authorization envelope per operation)
- Combined: all tools functional + writes traceable to decision
- Both within DC_20261002_GL8_GL12_ARCHITECTURE scope

---

## Authority Boundary Impact (B+A Combined)

### What changes

**Before (current state with GAP-2)**:
- ALL tools blocked at GL8 (no decision_id in args)
- No operations possible through Authorization Pipeline

**After (B+A implemented)**:
- READ tools: Authorization Pipeline bypassed -> direct to GL1-GL7 (same behavior as before 916bef7)
- WRITE tools: Authorization Pipeline enforced -> caller must supply `_authz.decision_id` matching an Active decision

### Authority model

```
KUROKO writes event:
  args = {
    "title": "...",
    "_authz": {"decision_id": "DC_20261002_...", "scope": ["data"]}
  }
  ->  GL8: decision exists and is Active? YES
  ->  GL9: scope ["data"] subset of authorized ["data", "events"]? YES
  -> GL10: content hash matches? YES
  -> GL11: mocka_write_event is ACTIVE in registry? YES
  -> GL12: decision_ledger.jsonl is UTF-8? YES
  -> ALLOW -> GL1-GL7 -> execute
```

This is the intended Runtime Enforcement behavior from DC_20261002_GL8_GL12_ARCHITECTURE.

### What does NOT change

- Human Gate approval process for decisions
- Decision Ledger schema and storage
- GL1-GL7 governance pipeline behavior
- Read-only tool access (no regression)

---

## Runtime Impact Analysis

### Deployment risk without this fix (current)

If 916bef7 is synced to production WITHOUT GAP-2 fix:
- ALL mocka_write_event calls fail: KUROKO cannot record events
- ALL mocka_add_todo calls fail: TODO management broken
- ALL mocka_update_todo calls fail: TODO status updates broken
- ALL mocka_seal calls fail: governance seal broken
- Impact: COMPLETE OPERATIONAL BREAKDOWN

This is why GAP-2 is Critical priority.

### Deployment risk WITH B+A fix

If 916bef7 + B+A fix is synced to production:
- Read tools: operate normally (no change)
- Write tools without _authz: blocked at GL8 (intentional - enforcement working)
- Write tools with valid _authz: operate normally
- Write tools with invalid decision_id: blocked at GL8 (intentional)
- Impact: TARGETED ENFORCEMENT, no collateral breakage

---

## Decision Options for Approval

**Option 1 (Recommended)**: Approve Option B + Option A combined  
Implement:
1. READ_ONLY_TOOLS bypass in authorization_pipeline.py (Option B, ~10 lines)
2. `_authz` envelope extraction in GL8/GL9 (Option A, ~15 lines)

**Option 2**: Approve Option D (GL11-first) + Option A  
Implement GL11 pre-check + `_authz` envelope.
Requires GAP-5 registry completion FIRST (dependency).

**Option 3**: Defer authorization to PHASE 5.2  
Keep 916bef7 commit NOT deployed until full design is resolved.
No code change now. Remediation in next phase.

---

## Required Approvals

1. きむら博士: Select propagation option (1 / 2 / 3)
2. Implicit: If Option 1 or 2, new commit implementing the change
   (new commit for new functionality - not amending 916bef7)

---

## Next Action After Approval

If Option 1 approved:
1. CHANGE_START event recorded
2. Modify authorization_pipeline.py: add READ_ONLY_TOOLS bypass at entry
3. Modify human_gate_authorization_integrity.py: read from args["_authz"]
4. Modify authorization_scope_binding.py: read scope from args["_authz"]
5. check_utf8 on modified files
6. CHANGE_DONE event recorded
7. Commit with message: "fix(GL8-GL9): Add READ bypass and _authz envelope (GAP-2 remediation)"
8. Push to development branch
9. Integration test Stage 1 + Happy Path executed (HGD-C1 completion)

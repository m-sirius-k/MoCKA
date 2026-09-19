# HG-M3-INTEGRATION-IMPLEMENTATION-IMPACT-ANALYSIS-001

## M3 Integration Architecture — Implementation Impact Analysis

**Date**: 2026-09-19  
**Phase**: Analysis Only (No Implementation)  
**Status**: ANALYSIS COMPLETE  

---

## STEP 1: EXISTING CONTRACT MAP

### 1A. MCP Request/Adapter/Router Contract

**File**: `mcp/mcp_gateway.py` (13 lines)

```python
class MCPGateway:
    def __init__(self):
        self.router = MCPRouterV2()
    
    def ingest(self, source: str, payload: dict) -> dict:
        return self.router.route(source, payload)
```

| Item | Current |
|------|---------|
| Function | `MCPGateway.ingest(source, payload)` |
| Input | `source: str` (http, github, filesystem, browser), `payload: dict` (source-specific) |
| Output | `dict` with parsed request data |
| Authority Context Present | **NO** |

**File**: `mcp/mcp_router.py` (37 lines)

```python
class MCPRouterV2:
    def route(self, source: str, payload: dict) -> dict:
        parsed = self.adapters[source].parse(payload)
        return {
            "type": SOURCE_TYPE_MAP[source],
            "source": source,
            **parsed,
        }
```

| Item | Current |
|------|---------|
| Method | `MCPRouterV2.route(source, payload)` |
| Input | `source`, `payload` |
| Output | `{"type": ..., "source": ..., **parsed}` |
| Authority Context Present | **NO** |
| Parsed Payload | No `authority_id`, `decision_type`, or `resource_class` |

**File**: `mcp/adapters/http.py` (11 lines)

```python
class HTTPAdapter(BaseAdapter):
    def parse(self, request: dict) -> dict:
        return {
            "endpoint": request.get("endpoint"),
            "method": request.get("method"),
            "body": request.get("body"),
        }
```

| Item | Current |
|------|---------|
| Contract | Each adapter extracts source-specific fields only |
| Authority Fields | **NOT EXTRACTED** |

**Change Required**: ALL adapters must extract `authority_context` or `authority_id` from source payload

---

### 1B. Decision Object / DecisionResult Contract

**File**: `decision/decision_model.py` (57 lines)

```python
@dataclass(frozen=True)
class DecisionResult:
    selected_action: str
    alternatives: tuple
    priority_score: float
    risk_score: float
    confidence: float
    rationale: str
    required_governance_check: bool = True
    risk_factors: tuple = field(default_factory=tuple)
```

| Item | Current |
|------|---------|
| Class | `DecisionResult` |
| Input | semantic_result, decision_profile (from decision_engine.py) |
| Output | `DecisionResult` dataclass |
| Authority Context Present | **NO** |
| Authority Binding | **MISSING** |

**Change Required**: Add `authority_context` and `authority_binding` fields to DecisionResult

---

### 1C. Decision → Executor Contract

**File**: `runtime/executor.py` (51 lines)

```python
def main():
    intent = load_json(INTENT_PATH)           # reads runtime/selected_intent.json
    history = load_history()                   # reads runtime/intent_history.json
    record = {
        "goal": intent["goal"],
        "score": intent.get("score", 0),
        "ts": datetime.now().isoformat(),
        "result": "pending"
    }
    history.append(record)
    save(history)
```

| Item | Current |
|------|---------|
| Input | JSON file `runtime/selected_intent.json` with `{"goal": ..., "score": ...}` |
| Processing | Load intent, record to history |
| Output | Updated `runtime/intent_history.json` |
| Authority Context Present | **NO** |
| Authority Validation | **NOT PRESENT** |

**Change Required**: Executor must receive `authority_id`, `decision_type`, `resource_class` and revalidate before execution

---

### 1D. Executor Input/History Contract

**Current Structure** (`runtime/intent_history.json`):

```json
[
  {
    "goal": "...",
    "score": 0,
    "ts": "2026-09-19T...",
    "result": "pending"
  }
]
```

| Item | Current |
|------|---------|
| Fields | goal, score, ts, result |
| Authority Fields | **NONE** |
| Execution Status | Simple string ("pending", "executed", etc) |
| Authority Validation Record | **NONE** |

**Change Required**: Add authority_id, revalidation_result, execution_authorization to history

---

### 1E. Decision Ledger Contract

**File**: `runtime/jarvis/record/ledger.py` (15 lines)

```python
class JarvisLedger:
    def __init__(self):
        self.records = []
    
    def append(self, decision_id, status):
        record = {
            "decision_id": decision_id,
            "status": status,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
        self.records.append(record)
        return record
```

| Item | Current |
|------|---------|
| Class | `JarvisLedger` |
| Storage | In-memory list (`self.records`) |
| Record Fields | `decision_id`, `status`, `timestamp` |
| Authority Fields | **NONE** |
| Persistence | **NO** (in-memory only) |
| Persistence Target | Not defined |

**Change Required**: 
- Add authority fields to record structure (conceptually defined, no schema change yet)
- Determine persistence mechanism (required but not authorized)

---

### 1F. Authority Runtime Modules (M3 Phase2)

**Existing M3 Authority Implementation**:
- `runtime/authority_model.py` (266 lines) — Authority Object model, Registry
- `runtime/delegation_validator.py` (265 lines) — Delegation validation and approval
- `runtime/revocation_engine.py` (239 lines) — Revocation and cascade logic
- `runtime/authority_enforcement.py` (271 lines) — MCP and Executor boundary validation
- `tests/test_authority_runtime.py` (625 lines) — 12/12 passing tests

**Status**: Sandbox-only, self-contained, ready for integration

---

## STEP 2: AUTHORITY CONTEXT PROPAGATION MAP

Current Authority Context presence at each boundary:

```
MCP Boundary
  Input: HTTP request payload
  Authority: ABSENT
  Extraction: NOT IMPLEMENTED
  
    ↓ (mcp/mcp_gateway.py:11-12 → mcp/mcp_router.py:27-36)
    
Decision Engine
  Input: DecisionResult (no authority context)
  Authority: ABSENT
  Binding: NOT IMPLEMENTED
  
    ↓ (decision/decision_engine.py → governance_pipeline.py)
    
Governance Layer
  Input: DecisionResult (no authority context)
  Authority: ABSENT (handled separately at tool level)
  
    ↓ (approved decision → executor)
    
Executor Boundary
  Input: intent JSON from runtime/selected_intent.json
  Authority: ABSENT
  Validation: NOT IMPLEMENTED
  
    ↓ (runtime/executor.py:main())
    
Decision Ledger
  Input: intent history
  Authority: ABSENT
  Recording: NOT IMPLEMENTED
  Persistence: IN-MEMORY ONLY
```

**Propagation Summary**:

| Boundary | Current | Desired | Status |
|----------|---------|---------|--------|
| MCP → Decision | ABSENT | PRESENT (extract from request) | ABSENT |
| Decision → Executor | ABSENT | PRESENT (pass through decision) | ABSENT |
| Executor → Ledger | ABSENT | PRESENT (record with execution) | ABSENT |
| Ledger Persistence | ABSENT | PRESENT (write/read authority records) | ABSENT |

**Classification**: ALL BOUNDARIES = ABSENT

---

## STEP 3: REQUIRED CONTRACT CHANGES

Based on Architecture Decision Record `1577fb8`, the following changes are CONCEPTUALLY REQUIRED but NOT YET IMPLEMENTED:

### Change 1: MCP Request Contract

**Current**:
```python
def ingest(self, source: str, payload: dict) -> dict
```

**Required**:
```python
def ingest(self, source: str, payload: dict, authority_context: AuthorityContext | None = None) -> dict
```

OR

Each adapter must extract authority_context from source payload (e.g., HTTP Authorization header)

| Aspect | Detail |
|--------|--------|
| Affected Files | mcp/mcp_gateway.py, mcp/mcp_router.py, mcp/adapters/*.py (4-5 files) |
| Affected Interfaces | MCPGateway.ingest(), MCPRouterV2.route(), All adapters.parse() |
| Backward Compatibility | Potentially breaking if authority_context becomes required |
| Migration Required | Existing callers of MCPGateway.ingest() must be updated |
| M2 Impact | M2 legacy requests without authority_context must be handled (grace period?) |
| Production Impact | HIGH (changes MCP entry point, affects all sources) |
| Authorization Class | **B** (Requires new Human Gate authorization for MCP contract change) |

---

### Change 2: Decision Engine Contract

**Current**:
```python
@dataclass(frozen=True)
class DecisionResult:
    selected_action: str
    alternatives: tuple
    priority_score: float
    risk_score: float
    confidence: float
    rationale: str
    required_governance_check: bool = True
    risk_factors: tuple = field(default_factory=tuple)
```

**Required**:
```python
@dataclass(frozen=True)
class DecisionResult:
    # ... existing fields ...
    authority_context: AuthorityContext | None      # NEW
    authority_binding: AuthorityBinding | None       # NEW (snapshot at T_decision)
```

| Aspect | Detail |
|--------|--------|
| Affected Files | decision/decision_model.py, decision/decision_engine.py |
| Affected Interfaces | DecisionResult dataclass, DecisionEngine.decide() output |
| Backward Compatibility | Breaking (new required fields, or optional with defaults) |
| Migration Required | All code consuming DecisionResult must handle new fields |
| M2 Impact | M2 decisions cannot populate authority fields (separate processing?) |
| Production Impact | MEDIUM (affects decision pipeline, mostly internal) |
| Authorization Class | **B** (Requires new Human Gate authorization for Decision model change) |

---

### Change 3: Executor Integration Contract

**Current**:
```python
# runtime/executor.py loads from file
intent = load_json("runtime/selected_intent.json")
record = {"goal": ..., "score": ..., "ts": ..., "result": "pending"}
```

**Required**:
```python
# New contract: Executor receives decision with authority_id
def execute(self, decision: DecisionResult, authority_context: AuthorityContext):
    # Revalidate authority before execution
    revalidation_result = validate_at_executor_boundary(
        authority_id=authority_context.authority_id,
        decision_id=decision.decision_id,
        decision_type=decision.decision_type,
        resource_class=decision.resource_class
    )
    if revalidation_result.valid:
        execute_action()
    else:
        record_failure(revalidation_result)
```

| Aspect | Detail |
|--------|--------|
| Affected Files | runtime/executor.py, decision flow (TBD) |
| Affected Interfaces | Executor.execute(), decision delivery mechanism |
| Backward Compatibility | Breaking (changes how decisions are passed to executor) |
| Migration Required | YE (how are pending decisions stored? JSON schema change? database?) |
| M2 Impact | M2 execution flow unchanged, M3 flow separate |
| Production Impact | HIGH (changes execution pipeline, authorization-critical) |
| Authorization Class | **B** (Requires new Human Gate authorization for Executor contract change) |

---

### Change 4: Decision Ledger Contract

**Current**:
```python
class JarvisLedger:
    def append(self, decision_id, status):
        record = {
            "decision_id": decision_id,
            "status": status,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
        }
```

**Required** (Conceptually from Architecture Decision):
```python
class JarvisLedger:
    def append_decision_with_authority(self, decision_record: dict):
        # decision_record includes:
        # - decision_id
        # - authority_context_id
        # - authority_lifecycle_state
        # - authority_verification_state (at T_decision)
        # - scope (decision_type, resource_class)
        # - temporal_validity
        # - execution_outcome
        # - revocation_state (if applicable)
        # etc (30+ fields defined in Architecture Decision)
```

| Aspect | Detail |
|--------|--------|
| Affected Files | runtime/jarvis/record/ledger.py (and persistence layer TBD) |
| Affected Interfaces | JarvisLedger.append() signature, record structure |
| Backward Compatibility | Breaking (new required fields) |
| Migration Required | **YES** (how to persist Authority records? database schema? file format?) |
| M2 Impact | M2 decision ledger entries unaffected (separate records?) |
| Production Impact | MEDIUM-HIGH (new data model, persistence required) |
| Authorization Class | **B** (Requires new Human Gate authorization for persistence schema) |

---

## STEP 4: AUTHORITY CONTEXT DATA MODEL

**Minimum fields required** for Authority Context to flow through pipeline:

```
Authority Context (conceptual data model):

  Identity & Reference
    - authority_context_id        : str (unique instance ID)
    - authority_id                : str (reference to Authority Object)
  
  Authority State (Lifecycle)
    - authority_lifecycle_state   : enum (NONE / GRANTED_HUMAN / DELEGATED_ACTIVE / DELEGATED_REVOKED / UNDEFINED)
  
  Authorization State (Runtime)
    - runtime_verification_state  : enum (VERIFIED / NOT_VERIFIED / INVALID / UNKNOWN)
    - verification_timestamp      : datetime
  
  Scope
    - decision_type               : str (what type of decision)
    - resource_class              : str (what resources apply to)
  
  Temporal Validity
    - valid_from                  : datetime
    - valid_until                 : datetime | null
    - is_indefinite               : bool (valid_until == null)
  
  Revocation State
    - is_revoked                  : bool
    - revoked_at                  : datetime | null
    - revoked_by                  : str | null
    - revocation_decision_id      : str | null
  
  Historical Snapshot (at decision time)
    - authority_state_at_decision : enum
    - verification_state_at_decision : enum
    - scope_at_decision           : object
    - temporal_at_decision        : object
  
  Provenance
    - granted_by                  : str (Human Gate or delegating authority)
    - granted_at                  : datetime
    - granting_decision_id        : str
    - provenance_evidence         : object (TBD - cryptographic binding or read-through reference)
  
  Decision/Execution Binding
    - decision_id                 : str (which decision uses this authority)
    - execution_id                : str | null (which execution used this authority)
```

**Total fields**: ~24 minimum fields

**NOT decided**: Cryptographic signature, token format, HMAC algorithm, key management

---

## STEP 5: TEMPORAL BINDING MAP

Authority validity at each critical timepoint:

```
T_authorized = 2026-09-01 10:00 (Authority Object granted)
              └─ Authority enters system, state = CREATED

T_decision = 2026-09-15 14:30 (Decision made)
           └─ Authority checked, state snapshot captured
           └─ Immutable snapshot recorded in ledger
           └─ DecisionResult includes authority_binding

T_execution = 2026-09-15 14:35 (Executor attempts execution)
            └─ Authority revalidated (current state, not snapshot)
            └─ If revoked between T_decision and T_execution → STOP
            └─ If expired → STOP
            └─ If still ACTIVE → proceed

T_revoked = 2026-09-16 09:00 (Authority revoked)
          └─ Authority state changes to REVOKED
          └─ Revocation recorded in separate ledger entry
          └─ Execution at T < T_revoked remains valid
          └─ Execution at T > T_revoked would be rejected

T_now = 2026-09-19 12:00 (Current query time)
      └─ Current authority state = REVOKED
      └─ Historical decision at T_decision still shows ACTIVE (immutable)
      └─ Historical execution at T_execution remains valid
      └─ Future authorizations at T > T_revoked are invalid
```

**Authority Validity at Each Point**:

| Timepoint | Check | Authority State | Validity | Recording |
|-----------|-------|-----------------|----------|-----------|
| T_authorized | N/A | CREATED → ACTIVE | N/A | Authority Object created |
| T_decision | Verify at MCP | ACTIVE (at T_decision) | **YES** | Immutable snapshot in ledger |
| T_execution | Revalidate | ACTIVE (current) | **YES** (if no revocation) | Execution allowed/denied recorded |
| T_revoked | N/A | REVOKED | N/A | Revocation event recorded |
| T_now | Query | REVOKED (current) | Historical at T_d=YES, Current=NO | Both recorded, separate |

**Historical Record Treatment**:

```
Decision Ledger Entry (T_decision):
  - decision_id: "DEC-20260915-001"
  - authority_id_at_decision: "AUTH-20260901-HG-001"
  - authority_state_at_decision: "ACTIVE"                    ← IMMUTABLE
  - authority_verification_at_decision: "VERIFIED"           ← IMMUTABLE
  - execution_timestamp: "2026-09-15T14:35:00"
  - execution_result: "SUCCESS"
  - revalidation_result: "VERIFIED_OK"
  - authority_state_at_recording: "REVOKED"                  ← CURRENT (updated)
  - authority_revoked_at: "2026-09-16T09:00:00"              ← SEPARATE RECORD
```

**Principle**: Historical state (at T_decision) never changes. Current state may change and is queryable separately.

---

## STEP 6: SECURITY / FAILURE BOUNDARY

Authority Context state → execution decision matrix:

```
Condition                         Decision      Action
─────────────────────────────────────────────────────────────────
authority_context ABSENT          UNKNOWN       → STOP (reject)
authority_context == null         UNKNOWN       → STOP (reject)
authority_id missing              UNKNOWN       → STOP (reject)
verification_state == UNKNOWN     UNKNOWN       → STOP (reject)
verification_state == NOT_VERIFIED UNKNOWN      → STOP (reject)

authority_lifecycle_state == REVOKED    INVALID → STOP (reject)
authority_lifecycle_state == EXPIRED    INVALID → STOP (reject)
authority_lifecycle_state == UNDEFINED  INVALID → STOP (reject)

temporal_validity.is_within_scope == false INVALID → STOP (reject)

decision_type != authority.decision_type INVALID → STOP (reject)
resource_class != authority.resource_class INVALID → STOP (reject)

verification_state == INVALID     INVALID       → STOP (reject)

verification_state == VERIFIED    
  AND lifecycle_state == ACTIVE
  AND scope matches
  AND temporal valid
  AND not revoked                 VALID        → ALLOW (proceed)
```

**Fail-Closed States**:
- ABSENT → STOP
- UNKNOWN → STOP
- INVALID → STOP
- EXPIRED → STOP
- REVOKED → STOP

**Allow States**:
- VERIFIED + ACTIVE + SCOPE_MATCH + TEMPORAL_VALID + NOT_REVOKED → ALLOW

**No exceptions to fail-closed behavior**. No degraded operation modes.

---

## STEP 7: IMPLEMENTATION DEPENDENCY GRAPH

If implementation were authorized, the logical dependency order would be:

```
1. Authority Context Data Model
   └─ Define minimum fields, data structures
   └─ Implement as dataclass/TypedDict in Python

2. MCP Boundary Integration
   ├─ Add authority_context extraction to adapters (http, github, filesystem, browser)
   ├─ Modify MCPGateway.ingest() to accept/pass authority_context
   ├─ Modify MCPRouterV2.route() to include authority_context in output
   └─ Add validate_at_mcp_boundary() call (from runtime/authority_enforcement.py)

3. Decision Engine Integration
   ├─ Add authority_context and authority_binding fields to DecisionResult
   ├─ Pass authority_context through DecisionEngine.decide()
   ├─ Capture authority_binding snapshot at decision time
   └─ Update decision_model.py dataclass

4. Governance Layer Integration
   ├─ Ensure authority_context flows through GL1-GL7
   ├─ GL7 (Execution Governance) includes authority validation
   └─ Approval includes authority binding record

5. Executor Boundary Integration
   ├─ Modify executor intake to receive DecisionResult with authority_context
   ├─ Implement revalidation before execution
   ├─ Call validate_at_executor_boundary() (from runtime/authority_enforcement.py)
   ├─ Handle STOP cases (revoked, expired, unknown)
   └─ Record revalidation_result in execution history

6. Decision Ledger Integration
   ├─ Extend JarvisLedger record structure (conceptual only, no schema yet)
   ├─ Add authority fields to append() method
   ├─ Implement immutable historical snapshot storage
   ├─ Handle revocation history separately
   └─ Design persistence mechanism (NOT implemented)

7. Integration Tests
   ├─ End-to-end MCP → Decision → Executor → Ledger flow
   ├─ Authority validation at boundaries
   ├─ Revocation between decision and execution
   ├─ Historical record immutability
   └─ M2 isolation verification

8. Runtime Evidence / Verification
   ├─ Verify Authority Context carries through entire pipeline
   ├─ Verify revalidation catches authority changes
   ├─ Verify fail-closed behavior on UNKNOWN/INVALID
   ├─ Verify immutable historical records
   └─ Verify M2 unchanged
```

**Critical Dependency**: Step 2 (MCP) must complete before Step 3 (Decision), because Decision needs authority_context from MCP.

---

## STEP 8: SCOPE CLASSIFICATION

Each required contract change classified by authorization scope:

| Change | Classification | Reason |
|--------|----------------|--------|
| **MCP Authority Extraction** | **B**: Requires new HG auth | MCP is shared production component; adapter contracts must be modified |
| **Decision Model Extension** | **B**: Requires new HG auth | DecisionResult is used across entire decision pipeline; contract changes affect all consumers |
| **Executor Revalidation** | **B**: Requires new HG auth | Changes how decisions are delivered to executor; affects execution contract |
| **Ledger Schema** | **B**: Requires new HG auth | Persistence mechanism TBD; requires governance decision on data model |
| **Authority Context Data Model** | **A**: Sandbox scope | Pure data structure, no external contracts; can be defined in runtime/ |
| **Boundary Validation Calls** | **A**: Sandbox scope | Uses existing M3 Phase2 runtime/authority_enforcement.py (already in sandbox) |
| **Test Suite** | **A**: Sandbox scope | New integration tests in tests/ directory |
| **M2 Handling** | **C**: Production impact | How do legacy requests without authority_context behave? Grace period? |
| **Cryptographic Binding** | **E**: Unresolved | Architecture Decision says "do not select algorithm yet"; deferred for implementation phase |

**Summary**:
- **A (Sandbox)**: 2 items (data model, calls to existing sandbox code)
- **B (New Auth Required)**: 4 items (MCP, Decision, Executor, Ledger contracts)
- **C (Production Impact)**: 1 item (M2 legacy handling)
- **E (Unresolved)**: 1 item (cryptographic binding mechanism)

---

## STEP 9: SINGLE IMPLEMENTATION READINESS MATRIX

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ M3 INTEGRATION ARCHITECTURE — IMPLEMENTATION READINESS MATRIX                │
├─────────────────────────────────────────────────────────────────────────────┤
│ AREA                                                                          │
│   Current State                                                              │
│   Required Change                                                            │
│   Files                                                                      │
│   Contract Change                                                            │
│   Migration Required                                                         │
│   M2 Impact                                                                  │
│   Production Impact                                                          │
│   Authorization Class                                                        │
│   Evidence Status                                                            │
└─────────────────────────────────────────────────────────────────────────────┘

1. AUTHORITY CONTEXT DATA MODEL
   Current State: None (separate files exist for Authority Object, DecisionResult)
   Required Change: Define unified AuthorityContext dataclass with ~24 fields
   Files: runtime/authority_model.py (ADD: AuthorityContext class)
   Contract Change: NO (new sandbox class, not changing existing contracts)
   Migration Required: NO
   M2 Impact: NONE (M3 parallel system)
   Production Impact: NONE (sandbox-only)
   Authorization Class: A (Sandbox scope)
   Evidence Status: READY (fields defined in Architecture Decision Record)

2. MCP REQUEST EXTRACTION
   Current State: MCP adapters extract {endpoint, method, body}; no authority
   Required Change: Add authority_context extraction from each source
                    - HTTP: Extract from Authorization header
                    - GitHub: Extract from webhook headers/payload
                    - Filesystem: Extract from metadata/context
                    - Browser: Extract from session/context
   Files: mcp/mcp_gateway.py, mcp/mcp_router.py, mcp/adapters/*.py (5 files)
   Contract Change: YES (major) — MCPGateway.ingest() signature changes
   Migration Required: YES — All MCP callers must provide authority_context
   M2 Impact: MAYBE — M2 requests without authority_context must be handled
   Production Impact: HIGH (MCP is critical path)
   Authorization Class: B (Requires new HG authorization)
   Evidence Status: BLOCKED (MCP contract change requires HG authorization)

3. DECISION ENGINE INTEGRATION
   Current State: DecisionResult carries no authority information
   Required Change: Add authority_context and authority_binding fields to DecisionResult
                    Capture authority snapshot at T_decision
   Files: decision/decision_model.py, decision/decision_engine.py (2 files)
   Contract Change: YES (major) — DecisionResult dataclass changes
   Migration Required: YES — All code consuming DecisionResult must handle new fields
   M2 Impact: MAYBE — M2 decision flow separate or extends this?
   Production Impact: MEDIUM (decision pipeline internal, but changes output)
   Authorization Class: B (Requires new HG authorization)
   Evidence Status: BLOCKED (Decision model change requires HG authorization)

4. GOVERNANCE LAYER FLOW-THROUGH
   Current State: GL1-GL7 govern tool execution, separate from authority
   Required Change: Ensure authority_context flows through governance pipeline
                    GL7 includes authority validation in execution governance
   Files: structural/governance_pipeline.py (TBD — may need changes)
   Contract Change: MAYBE (depends on current GL7 structure)
   Migration Required: MAYBE
   M2 Impact: UNKNOWN (need to check GL7 structure)
   Production Impact: MEDIUM (affects execution approval flow)
   Authorization Class: B or C (depends on scope of changes)
   Evidence Status: UNKNOWN (GL7 structure not fully examined)

5. EXECUTOR REVALIDATION
   Current State: Executor loads intent from JSON, no authority checks
   Required Change: Executor receives decision with authority_context
                    Calls validate_at_executor_boundary() before execution
                    Records revalidation_result
   Files: runtime/executor.py (MODIFY) + storage mechanism for pending decisions (NEW)
   Contract Change: YES (major) — How decisions reach executor changes
   Migration Required: YES — Pending decision storage mechanism must be defined
   M2 Impact: NONE (M2 execution flow unchanged)
   Production Impact: HIGH (changes how decisions are executed)
   Authorization Class: B (Requires new HG authorization)
   Evidence Status: BLOCKED (Executor contract requires HG authorization)

6. DECISION LEDGER INTEGRATION
   Current State: JarvisLedger stores {decision_id, status, timestamp} in-memory
   Required Change: Extend JarvisLedger to store authority fields (conceptually)
                    Define persistence mechanism (database? file format?)
                    Implement write/read for authority records
   Files: runtime/jarvis/record/ledger.py (MODIFY)
          + new persistence layer (TBD)
   Contract Change: YES (major) — Record structure changes
   Migration Required: YES (how to persist historical decision records with new schema?)
   M2 Impact: NONE (M2 decisions separate)
   Production Impact: MEDIUM-HIGH (new data model, persistence required)
   Authorization Class: B (Requires new HG authorization for persistence schema)
   Evidence Status: BLOCKED (Ledger persistence requires HG authorization)

7. CRYPTOGRAPHIC BINDING MECHANISM
   Current State: Not decided (Architecture Decision defers this)
   Required Change: Select and implement:
                    - HMAC signature with authority registry key
                    - JWT token with embedded authority claims
                    - Read-through verification (registry lookup)
                    - Other mechanism
   Files: TBD (new security layer)
   Contract Change: YES (new authentication/verification layer)
   Migration Required: UNKNOWN
   M2 Impact: NONE
   Production Impact: MEDIUM (new security infrastructure)
   Authorization Class: E (Unresolved — requires separate implementation design)
   Evidence Status: BLOCKED (Mechanism selection requires HG authorization)

8. M2 LEGACY COMPATIBILITY
   Current State: M2 requests don't carry authority_context
   Required Change: Decide on grace period / backward compatibility:
                    - Reject all M2 requests without authority_context immediately
                    - Grace period: Accept M2 without authority, log warnings
                    - Implicit M2 authority: Special handling for M2 flow
   Files: mcp/mcp_gateway.py (logic for handling missing authority)
   Contract Change: MAYBE (depends on compatibility strategy)
   Migration Required: MAYBE (if grace period, need transition plan)
   M2 Impact: YES (affects M2 request handling)
   Production Impact: MEDIUM (compatibility strategy affects deployed M2)
   Authorization Class: C (Production impact — requires HG authorization)
   Evidence Status: BLOCKED (Backward compatibility decision requires HG)

9. INTEGRATION TESTS
   Current State: M3 Phase2 has 12/12 sandbox unit tests
   Required Change: Add end-to-end tests:
                    - MCP + Decision + Executor + Ledger flow
                    - Authority validation at each boundary
                    - Revocation between decision and execution
                    - Historical immutability
                    - M2 unchanged
   Files: tests/ (NEW test suite)
   Contract Change: NO
   Migration Required: NO
   M2 Impact: NONE
   Production Impact: NONE (tests only)
   Authorization Class: A (Sandbox scope)
   Evidence Status: READY (test cases defined in Architecture Decision)

10. RUNTIME EVIDENCE VERIFICATION
    Current State: M3 Phase2 passes unit tests, architecture designed
    Required Change: Verify end-to-end evidence:
                     - Authority Context carries through entire pipeline
                     - Revalidation catches authority changes
                     - Fail-closed behavior on UNKNOWN/INVALID
                     - Historical records immutable
                     - M2 isolation maintained
    Files: Integration tests (above)
    Contract Change: NO
    Migration Required: NO
    M2 Impact: NONE
    Production Impact: NONE
    Authorization Class: A (Sandbox scope)
    Evidence Status: READY (verification criteria defined)
```

---

## SUMMARY: WHAT MUST CHANGE

**To implement M3 Integration Architecture, the following MUST change**:

### Must Change (Blocked — Requires HG Authorization):

1. **MCP Adapter Contracts** (5 files)
   - Extract authority_context from request
   - Pass through router
   - Signature change: ingest(source, payload, authority_context?)

2. **Decision Model** (2 files)
   - Add authority_context and authority_binding to DecisionResult
   - Capture authority snapshot at T_decision

3. **Executor Intake** (1+ files)
   - Accept decisions with authority_id
   - Implement revalidation before execution
   - Change how decisions are stored/retrieved

4. **Decision Ledger Schema** (1+ files)
   - Add authority fields to records
   - Define persistence mechanism
   - Handle immutable historical snapshots

5. **Legacy M2 Compatibility** (TBD)
   - Decide how to handle requests without authority_context
   - Grace period? Rejection? Special M2 path?

### Can Change (Within Sandbox Scope):

1. **Authority Context Data Model** (1 file)
   - Add AuthorityContext dataclass to runtime/authority_model.py
   - No contract changes, sandbox-only

2. **Integration Tests** (1+ files)
   - End-to-end test suite in tests/
   - Verifies authority flow through pipeline

### Cannot Change Yet (Deferred):

1. **Cryptographic Binding Mechanism**
   - Algorithm selection deferred
   - Key management deferred
   - Implementation design required first

---

## CONCLUSION: IMPLEMENTATION READINESS

**Status**: ANALYSIS COMPLETE, IMPLEMENTATION BLOCKED

**Blocking Factors**:
1. MCP contract changes require Human Gate authorization
2. Decision model changes require Human Gate authorization
3. Executor contract changes require Human Gate authorization
4. Ledger persistence schema requires Human Gate authorization
5. M2 backward compatibility strategy requires Human Gate authorization
6. Cryptographic binding mechanism requires separate design phase

**What's Ready**:
- Authority Context data model (defined)
- Sandbox unit tests (12/12 passing)
- Integration tests (design ready)
- Authority validation logic (implemented in Phase2)

**What's Blocked**:
- All production contract changes
- All shared component modifications
- Persistence mechanism
- Backward compatibility strategy
- Security implementation details

---

## STEP 10: STOP

**IMPLEMENTATION IMPACT ANALYSIS COMPLETE**

No code changes made. No contracts modified. Analysis only.

**Status**: `ANALYSIS COMPLETE — IMPLEMENTATION NOT AUTHORIZED`

**Proceeding to implementation requires**:

1. Human Gate authorization for 5 contract changes (MCP, Decision, Executor, Ledger, M2 compatibility)
2. Separate implementation design phase for cryptographic binding
3. Separate implementation authorization
4. Staged implementation with testing at each step
5. Evidence verification before production deployment

**No implementation can begin without additional Human Gate decisions on the 5 blocked items.**

---

**Analysis Date**: 2026-09-19  
**Analyzed By**: Architecture Analysis  
**Status**: FINAL (ANALYSIS ONLY)

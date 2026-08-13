# TARGET HUMAN GATE LEDGER ARCHITECTURE v1.0

**Report Date**: 2026-08-13
**Phase**: Human Gate Ledger Authority Boundary Consolidation — Phase 6
**Purpose**: Design implementable target architecture pending Human Gate decisions
**Constraint**: Design-only, no code changes, no implementation

---

## PREFACE

This document presents **one possible target architecture** based on best practices and evidence. No recommendation is made for which path Human Gate should choose. This is presented as a reference implementation IF Human Gate chooses to adopt authority boundaries.

**Explicitly NOT proposed**:
- Specific code changes
- Database modifications
- Migration procedures
- Implementation timeline
- Breaking changes

**Explicitly ONLY proposed**:
- Architectural structure
- Responsibility boundaries
- Data flow
- Integration points
- Design principles

---

## PROPOSED ARCHITECTURE: UNIFIED HUMAN GATE AUTHORITY BOUNDARY

### Core Principle

"All institutional decisions proceed through a single authority boundary that verifies Human Gate approval before becoming formal records."

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│ INSTITUTIONAL DECISION FLOW (Proposed Target Architecture)      │
└─────────────────────────────────────────────────────────────────┘

LAYER 1: HUMAN DECISION MAKING
┌──────────────────────────────────────────────┐
│         Human Gate (PHI-OS)                  │
│                                              │
│  ├─ Submission: Human requests approval     │
│  ├─ Deliberation: System captures context   │
│  └─ Approval: Individual approver decides   │
└──────────────────────────────────────────────┘
                    |
                    v
LAYER 2: AUTHORITY SOURCE (mocka_events.db)
┌──────────────────────────────────────────────┐
│      mocka_events.db [Event Authority]       │
│                                              │
│  ├─ event_id: HG20260813_001ABC             │
│  ├─ request_id: REQUEST_123                 │
│  ├─ approver: alice (individual)            │
│  ├─ timestamp: 2026-08-13T10:30:45Z         │
│  ├─ next_state: APPROVED                    │
│  └─ [immutable event records]               │
│                                              │
│ Authority: WHO approved? WHEN? Verifiable   │
│ Storage: Event-sourced, queryable           │
└──────────────────────────────────────────────┘
                    |
                    v
LAYER 3: AUTHORITY BOUNDARY (LedgerAdapter)
┌──────────────────────────────────────────────┐
│    LedgerAdapter [Authority Enforcement]     │
│                                              │
│  Step 1: Verify Approval                    │
│    └─ Query: HG event exists? APPROVED?     │
│    └─ Fail-Closed: No event = reject        │
│                                              │
│  Step 2: Extract Identity                   │
│    └─ Read: approver = "alice"              │
│    └─ Individual: not generic               │
│                                              │
│  Step 3: Check Duplicates                   │
│    └─ Query: decision_id already exists?    │
│    └─ Fail-Closed: duplicate = reject       │
│                                              │
│  Step 4: Create Record                      │
│    └─ Include: HG event reference           │
│    └─ Include: Individual approver          │
│    └─ Include: Timestamp from approval      │
│                                              │
│  Step 5: Append Record                      │
│    └─ Write: decision_ledger.jsonl          │
│    └─ Guarantee: Immutable append           │
│                                              │
│  Step 6: Return Receipt                     │
│    └─ Proof: File offset, hash, timestamp   │
│                                              │
│ Authority: VERIFY before writing             │
│ Boundary: ALL decisions pass through        │
│ Enforcement: Fail-closed on any check       │
└──────────────────────────────────────────────┘
                    |
                    v
LAYER 4: FORMAL RECORD (decision_ledger.jsonl)
┌──────────────────────────────────────────────┐
│ decision_ledger.jsonl [Canonical Decision]   │
│                                              │
│  ├─ decision_id: DC_20260813_001            │
│  ├─ request_id: REQUEST_123                 │
│  ├─ status: APPROVED                        │
│  ├─ approver: alice                         │
│  ├─ human_gate_event_id: HG20260813_001ABC │
│  ├─ timestamp: 2026-08-13T10:30:45Z         │
│  ├─ source: HUMAN_GATE                      │
│  ├─ content_hash: sha256:abc123...          │
│  └─ [immutable append-only]                 │
│                                              │
│ Authority: WHAT decision was recorded?      │
│ Record: Formal, canonical, immutable        │
│ Traceability: Links back to HG event        │
└──────────────────────────────────────────────┘
                    |
                    +─────────────────────────┐
                    |                         |
                    v                         v
LAYER 5: DOWNSTREAM SYSTEMS
┌──────────────────────┐        ┌──────────────────────┐
│  System Execution    │        │  Audit & Reporting   │
│                      │        │                      │
│ ├─ Read Decision     │        │ ├─ Query Ledger      │
│ ├─ Verify Authority  │        │ ├─ Trace to Event    │
│ ├─ Check Timestamp   │        │ ├─ Verify Approver   │
│ ├─ Execute Policy    │        │ ├─ Audit Trail       │
│ └─ Log Result        │        │ └─ Compliance Check  │
└──────────────────────┘        └──────────────────────┘
```

### Data Flow Example

**Real Scenario: Policy Approval**

```
Step 1: Human Gate Receives Request
  Request: "Update security policy"
  Submitted by: system
  Request ID: REQUEST_20260813_001

Step 2: Human Reviews and Approves
  Approver: alice
  Decision: APPROVE
  Action: Submit approval
  Timestamp: 2026-08-13T10:30:45.123456Z

Step 3: Event Stored in mocka_events.db
  Event written:
  {
    "event_id": "HG20260813_001ABC123DEF",
    "timestamp": "2026-08-13T10:30:45.123456Z",
    "request_id": "REQUEST_20260813_001",
    "action": "approve",
    "approver": "alice",
    "next_state": "APPROVED"
  }

Step 4: LedgerAdapter Boundary Triggered
  Condition: On HG approval, trigger decision recording
  
  Step 4a: Verify
    Query: events.db for REQUEST_20260813_001
    Result: Found, state = APPROVED, approver = alice ✓
  
  Step 4b: Check Duplicate
    Query: ledger for decision_id = DC_20260813_001
    Result: Not found ✓
  
  Step 4c: Create Record
    Record = {
      decision_id: "DC_20260813_001",
      request_id: "REQUEST_20260813_001",
      status: "APPROVED",
      approver: "alice",
      human_gate_event_id: "HG20260813_001ABC123DEF",
      timestamp: "2026-08-13T10:30:45.123456Z",
      source: "HUMAN_GATE",
      content_hash: "sha256:..."
    }
  
  Step 4d: Write to Ledger
    File append: decision_ledger.jsonl
    Mode: "a" (append-only)
    
    Result: Written at offset 48902, hash matches

Step 5: Decision Recorded
  Formal Record Stored:
  decision_ledger.jsonl contains:
  {"decision_id":"DC_20260813_001", "approver":"alice", ...}

Step 6: System Execution
  Application reads decision from ledger
  Validates: approver = alice, HG event exists
  Executes: Implements policy change
  Logs: "Policy updated per DC_20260813_001 (approved by alice)"

Step 7: Audit Trail
  Query ledger: DC_20260813_001
  Trace: decision_ledger → HG event ID → mocka_events.db
  Verify: alice approved REQUEST_20260813_001 on 2026-08-13
  Proof: Immutable records + verified authority
```

---

## ARCHITECTURE CHARACTERISTICS

### Design Principles

1. **AI Cannot Approve**
   - Authority is human-only
   - AI can read, cannot write decisions
   - AI can verify authority, cannot create it

2. **AI Cannot Bypass**
   - All decisions pass through boundary
   - No alternate paths to Decision Ledger
   - LedgerAdapter is mandatory gate

3. **Human Authority Cannot Disappear**
   - Individual approver identity preserved
   - Cannot be changed after recording
   - Traceable through both systems

4. **Decision History Cannot Mutate**
   - Decision Ledger: append-only immutable
   - Events: event-sourced (new events, not modifications)
   - No retroactive changes

5. **Unknown State Must Remain Preserved**
   - No automatic decisions
   - Manual Human Gate approval required
   - Missing approval = no decision recorded

---

## COMPONENT RESPONSIBILITIES

### mocka_events.db (Event Authority Store)

**Purpose**: Authoritative source for WHO approved and WHEN

**Responsibilities**:
- Record all Human Gate approvals
- Preserve individual approver identity
- Maintain state transitions
- Provide queryable history
- Support replay from start

**Schema** (unchanged):
```sql
CREATE TABLE human_gate_events (
  event_id TEXT PRIMARY KEY,
  timestamp TEXT NOT NULL,
  type TEXT NOT NULL,
  action TEXT NOT NULL,
  request_id TEXT NOT NULL,
  payload TEXT,
  previous_state TEXT,
  next_state TEXT,
  approver TEXT NOT NULL
);
```

**Guarantees**:
- ✅ Event uniqueness (event_id PK)
- ✅ Request uniqueness (cannot have two APPROVED states)
- ✅ State transition validity
- ✅ Timestamp ordering
- ❌ NOT cryptographically sealed (mutable)

**Queried by**:
- LedgerAdapter (for authority verification)
- Audit systems (for history)
- AI agents (for authority validation)

---

### LedgerAdapter (Authority Boundary)

**Purpose**: Enforce authority verification before Decision Ledger write

**Responsibilities**:
- Verify Human Gate approval exists
- Extract approver identity
- Check for duplicate decision_id
- Create formal Decision Record
- Write to Decision Ledger
- Return receipt with proof

**Input Interface**:
```python
class LedgerAdapter:
    def record(
        decision_id: str,
        request_id: str,
        status: str,
        approval_source: str = "HUMAN_GATE",
        additional_context: dict = None
    ) -> DecisionRecordReceipt:
        """
        Record a decision after verifying Human Gate approval.
        
        Arguments:
            decision_id: DC_YYYYMMDD_NNN format
            request_id: REQUEST_YYYYMMDD_NNN format
            status: APPROVED, REJECTED, PENDING, etc.
            approval_source: default "HUMAN_GATE"
            additional_context: optional metadata
        
        Returns:
            DecisionRecordReceipt with proof of recording
        
        Raises:
            AuthorizationError if approval not found
            AuthenticationError if approver invalid
            IntegrityError if duplicate detected
            PersistenceError if write fails
        """
```

**Output Receipt**:
```python
class DecisionRecordReceipt:
    decision_id: str
    request_id: str
    approver: str
    timestamp: str
    ledger_offset: int
    content_hash: str
    human_gate_event_id: str
```

**Failure Modes**:
- Approval not found → AuthorizationError (fail-closed)
- Approver invalid → AuthenticationError (fail-closed)
- Duplicate decision_id → IntegrityError (fail-closed)
- Write fails → PersistenceError (fail-closed)

---

### decision_ledger.jsonl (Decision Authority Record)

**Purpose**: Formal, immutable record of decisions with authority link

**Responsibilities**:
- Store formal decision records
- Maintain immutable append-only file
- Link to Human Gate authority
- Support audit queries
- Provide source of truth for "what was decided"

**Schema** (proposed):
```json
{
  "decision_id": "DC_20260813_001",
  "request_id": "REQUEST_20260813_001",
  "status": "APPROVED",
  "approver": "alice",
  "human_gate_event_id": "HG20260813_001ABC",
  "source": "HUMAN_GATE",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "content_hash": "sha256:abc123def456...",
  "title": "Security Policy Update",
  "context": {...},
  "canonical_source": "mocka_events.db"
}
```

**Guarantees**:
- ✅ Append-only (file mode "a")
- ✅ Immutable (cannot be modified)
- ✅ Chronological (by file append order)
- ✅ Authority-linked (event_id reference)
- ✅ Content-sealed (hash verification)

**Queried by**:
- System execution (read decisions)
- Audit systems (verify authority)
- AI agents (validate before acting)

---

## INTEGRATION POINTS

### Integration 1: PHI-OS Human Gate → LedgerAdapter

**Current State**: No integration (separate systems)

**Target State**: On approval, trigger boundary

```
phi_os/human_gate.py:approve(request_id, approver)
    |
    ├─ [existing] Write event to mocka_events.db
    |
    └─ [NEW] Trigger LedgerAdapter
        └─ LedgerAdapter.record(decision_id, request_id, "APPROVED")
            └─ Verify approval in events.db ✓
            └─ Write to decision_ledger.jsonl
            └─ Return receipt
```

**Coordination Needed**:
- decision_id generation (or mapping from request_id)
- LedgerAdapter availability
- Error handling if recording fails

---

### Integration 2: MCP Server → LedgerAdapter

**Current State**: MCP writes directly to Decision Ledger (bypasses HG)

**Target State**: MCP requests go through boundary

```
mocka_decision_write(decision_id, ..., approved_by=...)
    |
    └─ [CHANGED] Route through LedgerAdapter
        └─ LedgerAdapter.record(decision_id, request_id, status)
            ├─ Verify: HG event for request_id exists?
            ├─ Verify: Approval status is APPROVED?
            ├─ Extract: approver = alice
            └─ Write: decision_ledger.jsonl

Result: MCP cannot create unapproved decisions
```

**Impact**:
- MCP must provide request_id for approval lookup
- Or: MCP must provide pre-approval in mocka_events.db first
- Or: MCP calls cannot bypass Human Gate

---

### Integration 3: SealGov → LedgerAdapter

**Current State**: SealGov writes directly to Decision Ledger (with GL7 check)

**Target State**: SealGov executions trigger boundary

```
SealGovernanceGate.execute(seal_spec)
    |
    ├─ [existing] GL7 governance check
    |
    ├─ [existing] Execute seal script
    |
    └─ [CHANGED] Record via LedgerAdapter
        └─ LedgerAdapter.record(decision_id, ..., "EXECUTED")
            ├─ Verify: GL7 approval already performed ✓
            ├─ Check: Duplicate execution_id?
            └─ Write: decision_ledger.jsonl with execution_id

Result: SealGov still has GL7 authority, plus formal record
```

**Impact**:
- GL7 check is pre-execution authority (sufficient)
- LedgerAdapter records formal decision
- Both systems coordinated

---

## BYPASS PROTECTION

### MCP Direct Write Prevention

**Current Risk**: `mocka_decision_write()` can write any decision

**Target Protection**:
```
IF LedgerAdapter.record() is mandatory
  AND decision_ledger.jsonl is only write point
  AND _append_decision() calls LedgerAdapter (not direct)
THEN
  MCP cannot bypass authority check
```

**Enforcement**:
- Disable direct writes to decision_ledger.jsonl
- Route all writes through LedgerAdapter
- Fail if approval verification fails

### SealGov Re-execution Prevention

**Current Risk**: SealGov can re-execute and duplicate

**Target Protection**:
```
IF LedgerAdapter.record() detects duplicate decision_id
  AND idempotency check is in place
  AND execution_id is tracked
THEN
  Re-execution is detected and prevented
```

**Enforcement**:
- LedgerAdapter checks existing execution_id
- Silently returns existing record (idempotent)
- No duplicate entries created

### File I/O Prevention

**Current Risk**: Admin access can write directly to file

**Target Protection**:
```
IF file permissions restrict write access
  AND file is on separate filesystem
  AND audit logging captures access
THEN
  Direct file writes are detected
```

**Enforcement**:
- OS-level file permissions (read-only app)
- Separate storage (app cannot write, only append service)
- File access monitoring

---

## OPERATIONAL REQUIREMENTS

### 1. mocka_events.db Availability

**Requirement**: mocka_events.db must be available for approval verification

**Implementation**:
- Keep mocka_events.db on fast storage
- Index on request_id for quick lookup
- Replicate for high availability
- Cache recent approvals

---

### 2. Identity Service Integration

**Requirement**: Must verify approver identity

**Implementation**:
- Query user/identity database
- Validate approver is known entity
- Support role-based lookup (optional)
- Reject unknown approvers

---

### 3. Decision ID Coordination

**Requirement**: Must map request_id to decision_id

**Implementation Option A**: request_id is decision_id
- Simplest approach
- Requires coordination between systems

**Implementation Option B**: Mapping table
- request_id → decision_id mapping
- Supports different ID formats
- Requires additional storage

**Implementation Option C**: Embedded in context
- decision_id includes request_id
- Format: DC_req_{request_id}
- Self-documenting

---

### 4. LedgerAdapter Deployment

**Requirement**: LedgerAdapter must be deployed and accessible

**Implementation**:
- Deploy as shared library (Python import)
- Or: Deploy as service (HTTP endpoint)
- Or: Deploy inline (embedded in MCP server)
- Must be version-controlled and tested

---

## GOVERNANCE ENFORCEMENT

### Mandatory Integration Points

| System | Integration | Requirement | Enforcement |
|--------|---|---|---|
| PHI-OS | → LedgerAdapter | Record HG approvals | Automatic on approval |
| MCP Server | → LedgerAdapter | Verify before write | Redirect all calls |
| SealGov | → LedgerAdapter | Record execution | Automatic on execution |

### Approval Workflow

```
[MANDATORY SEQUENCE]

1. Human submits to Human Gate
2. Human reviews and approves
3. Event stored in mocka_events.db
4. LedgerAdapter triggered
5. Authority verified
6. Decision recorded in decision_ledger.jsonl
7. System can act on formal decision

[VIOLATIONS DETECTED]

If step 4-6 skipped → Warning/Error
If step 3 fails → Decision not recorded
If step 5 fails → Reject (authorization error)
```

---

## MIGRATION PATH (Informational Only)

**Note**: This section is for reference only. No migration implementation is proposed.

**Phase 1: Design & Testing**
- LedgerAdapter Model B implementation
- Test with Jarvis framework
- Validate all checks work

**Phase 2: Integration**
- Connect PHI-OS to LedgerAdapter
- Redirect MCP calls
- Update SealGov calls

**Phase 3: Validation**
- Run against historical data (offline)
- Verify no false positives
- Test failure modes

**Phase 4: Staged Rollout**
- Enable for new decisions first
- Keep old path available (fallback)
- Monitor for issues

**Phase 5: Transition**
- Migrate existing decisions (optional)
- Deprecate direct write path
- Remove fallback

**Phase 6: Enforcement**
- Block direct writes
- LedgerAdapter is only path
- Full authority boundary operational

---

## DESIGN CONSTRAINTS

### Architectural Constraints

1. **No modification to core decision logic** (only routing)
2. **No breaking changes to current APIs** (can add layers)
3. **No changes to mocka_events.db schema** (backward compatible)
4. **No forced migration of existing decisions** (optional)
5. **No changes to file storage** (append-only unchanged)

### Implementation Constraints

1. **Design-only** (no code changes in this phase)
2. **No database modifications** (schema unchanged)
3. **No production changes** (design only)
4. **Reversible** (can be undone if needed)
5. **Incremental** (can be phased in)

---

## SUCCESS CRITERIA

If this architecture were implemented, the following would be true:

1. ✅ Authority is verifiable
   - Every decision in Decision Ledger can be traced to HG approval
   - Approver identity is individual, not generic
   - Approval timestamp is recorded

2. ✅ No unauthorized decisions
   - MCP cannot create decisions without HG approval
   - SealGov decisions are linked to authority
   - All paths verified

3. ✅ No duplicates
   - Same decision_id cannot appear twice
   - LedgerAdapter detects and prevents

4. ✅ Audit is complete
   - Full chain from decision to approver
   - Timestamps at both levels
   - Queryable trail

5. ✅ Safe for AI agents
   - AI can verify authority before acting
   - Authority is machine-readable
   - Cannot be spoofed

6. ✅ Institutional governance
   - Authority model is clear
   - Responsibility is obvious
   - Compliance is verifiable

---

## EXPLICIT NON-GOALS

This design does NOT:
- ❌ Implement any code
- ❌ Modify any files
- ❌ Change database schemas
- ❌ Migrate existing decisions
- ❌ Break existing APIs
- ❌ Require users to change behavior
- ❌ Mandate new tools or services

This design ONLY:
- ✅ Shows possible architecture
- ✅ Defines responsibility boundaries
- ✅ Illustrates data flow
- ✅ Clarifies design principles
- ✅ Provides implementation reference

---

**PHASE 6 ARCHITECTURE PROPOSAL COMPLETE**

Target architecture designed pending Human Gate decisions.

Ready for Phase 7: Final Judgment Report.


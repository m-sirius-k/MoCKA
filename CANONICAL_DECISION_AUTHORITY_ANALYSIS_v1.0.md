# CANONICAL DECISION AUTHORITY ANALYSIS v1.0

**Report Date**: 2026-08-13
**Phase**: Human Gate Ledger Authority Boundary Consolidation — Phase 3
**Purpose**: Define single source of truth for institutional decision authority

---

## STRATEGIC QUESTION

**In MoCKA institutional governance, what single system should be the authoritative source of decision truth?**

Three candidates:

- **OPTION A**: mocka_events.db (Human Gate Event Store)
- **OPTION B**: decision_ledger.jsonl (MCP/SealGov Decision Ledger)
- **OPTION C**: Hybrid Model (Both systems with clear responsibility boundaries)

---

## EVALUATION FRAMEWORK

Six critical dimensions for institutional authority:

| Dimension | Definition | Score Scale |
|-----------|-----------|---|
| **Human Authority Proof** | Can the system prove a human made this decision? | ✅ YES / ⚠️ PARTIAL / ❌ NO |
| **Tamper Resistance** | How resistant to unauthorized modification? | 0-5 (0=mutable, 5=cryptographically sealed) |
| **Replay Capability** | Can decisions be reconstructed from first principles? | ✅ YES / ⚠️ PARTIAL / ❌ NO |
| **Audit Capability** | Can decisions be audited with full context? | ✅ COMPREHENSIVE / ⚠️ LIMITED / ❌ NONE |
| **Future AI Agent Compatibility** | Can AI agents safely operate on this authority? | ✅ POSSIBLE / ⚠️ RISKY / ❌ IMPOSSIBLE |
| **Institutional Clarity** | Is authority source clear to all stakeholders? | ✅ CLEAR / ⚠️ AMBIGUOUS / ❌ CONFLICTING |

---

## OPTION A: MOCKA_EVENTS.DB AS CANONICAL AUTHORITY

### Definition

All institutional decisions are recorded as Human Gate events in `mocka_events.db`. The event store becomes the formal authority source. All other systems reference or derive from this source.

### Architecture

```
Human Decision
    |
    v
[Human Gate]
    |
    ├─> Events Table
    |   ├─ event_id: HG20260813_001ABC
    |   ├─ type: human_gate_request
    |   ├─ action: approve
    |   ├─ request_id: REQUEST_123
    |   ├─ next_state: APPROVED
    |   ├─ approver: alice
    |   └─ timestamp: 2026-08-13T10:30:45Z
    |
    └─> Decision Ledger (derived)
        └─ "Only entries with Human Gate approval"
```

### Data Model

**Core Event Record** (mocka_events.db):
```json
{
  "event_id": "HG20260813_001ABC123DEF",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "type": "human_gate_request",
  "action": "submit|approve|reject|cancel",
  "request_id": "REQUEST_20260813_001",
  "payload": "{...}",
  "previous_state": "PENDING",
  "next_state": "APPROVED",
  "approver": "john_doe"
}
```

**Derived Decision Record** (decision_ledger.jsonl):
```json
{
  "decision_id": "DC_20260813_001",
  "request_id": "REQUEST_20260813_001",
  "status": "APPROVED",
  "actor": "john_doe",
  "human_gate_event_id": "HG20260813_001ABC123DEF",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "canonical_source": "mocka_events.db"
}
```

### Evaluation

#### 1. Human Authority Proof
**Score**: ✅ YES (EXCELLENT)

- Approver name explicitly stored
- Individual identity preserved
- Event-sourced: cannot be retroactively modified
- Direct proof: "john_doe approved REQUEST_123"

**Evidence**:
```sql
SELECT approver, next_state, timestamp 
FROM human_gate_events 
WHERE request_id = 'REQUEST_123' AND next_state = 'APPROVED'
```

#### 2. Tamper Resistance
**Score**: ⚠️ PARTIAL (MEDIUM)

**Strengths**:
- SQLite event table has primary key (event_id)
- Cannot modify event_id (primary key constraint)
- append-only semantics via newer events

**Weaknesses**:
- SQLite is mutable (UPDATE possible with direct access)
- No cryptographic sealing
- No transaction logs outside DB
- Admin access can modify records
- No content hash verification

**Verdict**: Protected from accidental corruption, vulnerable to deliberate modification

#### 3. Replay Capability
**Score**: ✅ YES (EXCELLENT)

- Event stream can be replayed from start
- State can be reconstructed at any timestamp
- All state transitions are recorded
- No gap in audit trail

**Example**:
```
2026-08-01: REQUEST_001 created (PENDING)
2026-08-05: REQUEST_001 approved by alice
2026-08-10: REQUEST_001 rejected by bob [later]
2026-08-13: REQUEST_001 CANCELED

Replay shows full lifecycle
```

#### 4. Audit Capability
**Score**: ✅ COMPREHENSIVE (EXCELLENT)

- Complete decision history available
- Timestamp of each action
- Approver identity recorded
- Previous state tracked
- All context preserved

**Queryable**:
- Who approved what
- When (exact timestamp)
- What was the previous state
- What context/payload was provided
- All changes to a single request

#### 5. Future AI Agent Compatibility
**Score**: ✅ POSSIBLE (but requires care)

**Safe Operations**:
- Read historical decisions (audit trail)
- Replay from point-in-time
- Aggregate statistics
- Query without modifying

**Unsafe Operations**:
- Direct event insertion (bypasses Human Gate)
- Event modification (violates immutability)
- State manipulation (authority abuse)

**Safeguard Required**: AI must be restricted to read-only access for audit queries

#### 6. Institutional Clarity
**Score**: ✅ CLEAR (EXCELLENT)

- "Human Gate events are the authority source"
- Clear responsibility: humans decide, events record
- No ambiguity: all decisions start here
- Easy to explain: "If it's not in events.db, it's not approved"

### Implementation Requirements

1. **Connection from MCP**
   - When mocka_decision_write called with decision_id
   - Must verify corresponding request_id in Human Gate events
   - Must extract approver from event
   - Must enforce: no decision without prior approval

2. **Connection from SealGov**
   - SealGov operations must reference Human Gate approval
   - Execution should be traceable to decision approval
   - Human authority must be evident

3. **Decision Ledger as Derived View**
   - decision_ledger.jsonl becomes cache/view of events
   - Not authoritative, just convenient reference
   - Can be regenerated from mocka_events.db
   - Includes human_gate_event_id link back to source

4. **Uniqueness Enforcement**
   - By request_id in events (already exists)
   - By decision_id in derived ledger

### Risks with Option A

1. **Request ID vs Decision ID Gap** (RISK_A1)
   - Human Gate works with request_id
   - MCP/SealGov work with decision_id
   - No automatic coordination
   - **Mitigation**: LedgerAdapter maps between them

2. **Distributed Authority** (RISK_A2)
   - Multiple systems reference events.db
   - If events.db unavailable, decisions cannot be verified
   - Single point of failure
   - **Mitigation**: Replicate events.db, cache decision_ledger locally

3. **Legacy Systems** (RISK_A3)
   - Existing MCP direct writes don't reference events.db
   - Existing decisions lack Human Gate connection
   - Backfill would be incomplete
   - **Mitigation**: Create mapping table for legacy decisions

4. **Performance** (RISK_A4)
   - Every decision write needs events.db query
   - Events table may grow large
   - Indexes required for query performance
   - **Mitigation**: Indexed queries, caching layer

### Strengths of Option A

✅ **Individual Human Authority**: Every approval traceable to person
✅ **Complete History**: Full lifecycle visible
✅ **Audit Trail**: Strong, queryable, timestamped
✅ **Institutional Intent**: Aligns with Human Gate concept
✅ **Replay-able**: Can reconstruct any state at any time
✅ **Clear Responsibility**: Humans decide, system records

---

## OPTION B: DECISION_LEDGER.JSONL AS CANONICAL AUTHORITY

### Definition

All institutional decisions are recorded in `decision_ledger.jsonl`. The append-only ledger becomes the formal authority source. This is the current de facto state.

### Architecture

```
Multiple Inputs
    |
    ├─> MCP Server
    ├─> SealGov
    ├─> Human Gate (potentially)
    |
    v
[Validation/Authority Check?]
    |
    v
decision_ledger.jsonl (append-only)
    |
    └─> mocka_events.db (reference only)
```

### Data Model

**Decision Record** (decision_ledger.jsonl):
```json
{
  "decision_id": "DC_20260813_001",
  "title": "Policy Amendment A",
  "context": "Urgency: High",
  "approved_by": "alice",
  "status": "APPROVED",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "actor": "system:mcp_server"
}
```

**No reference back** to Human Gate or request_id

### Evaluation

#### 1. Human Authority Proof
**Score**: ❌ NO (POOR)

- "approved_by" field is client-supplied (unverified)
- No proof that human actually approved
- No connection to Human Gate system
- Could be any string value
- **Evidence**: MCP server can write any name:

```python
mocka_decision_write(
    "DC_001",
    title="...",
    approved_by="fake_approver"  # No verification
)
```

#### 2. Tamper Resistance
**Score**: ✅ EXCELLENT (file-level immutability)

- Append-only file mode ("a")
- Once written, cannot be modified
- File system enforces immutability
- No UPDATE/DELETE possible at file level
- Cannot corrupt existing entries

**Weakness**: Does not prevent duplicate entries
**Weakness**: No per-record hash for integrity

**Verdict**: Perfectly immutable, but cannot prove authority of content

#### 3. Replay Capability
**Score**: ⚠️ PARTIAL (LIMITED)

- Can read all decisions in order
- Can see chronological sequence
- **But**: Cannot reconstruct why decisions were made
- **But**: No previous state information
- **But**: No context about deliberation

**Example**:
```
DC_001: APPROVED (no prior state, no context why)
DC_002: REJECTED (no prior state, no context why)
DC_003: APPROVED (no prior state, no context why)

Cannot answer: "What led to this approval?"
```

**Verdict**: Can replay sequence, not state transitions

#### 4. Audit Capability
**Score**: ⚠️ LIMITED (INCOMPLETE)

Can audit:
- ✅ What decision was made
- ✅ When it was made
- ✅ Who claimed to make it (but unverified)

Cannot audit:
- ❌ Why decision was made (no context preserved)
- ❌ Who actually made it (claimed only, not verified)
- ❌ What alternatives were considered
- ❌ Previous state/history
- ❌ Whether approval was real or forged

**Verdict**: Superficial auditability, no depth

#### 5. Future AI Agent Compatibility
**Score**: ⚠️ RISKY (DANGEROUS)

**Risks**:
- AI could read decisions with false authority
- AI might trust "approved_by" field (which is unverified)
- AI might create decisions based on precedent
- AI might execute decisions thinking they're approved
- AI might bypass Human Gate because decisions already in ledger

**Specific Danger**:
```python
# AI reads Decision Ledger
decision = decision_ledger.get("DC_001")
# Sees: approved_by = "alice"
# Trusts: This must be approved
# Acts: Executes decision
# Reality: No verification was done
```

**Verdict**: Unsafe for AI agent decision-making

#### 6. Institutional Clarity
**Score**: ❌ CONFLICTING (POOR)

- Current practice: MCP/SealGov write directly (no Human Gate)
- Design intent: Human Gate approvals recorded
- Actual state: Mixed, no clear authority
- Confusion: Who approves? MCP? Human Gate? SealGov?

**Verdict**: Ambiguous responsibility

### Implementation Requirements

For Option B to work as canonical authority:

1. **Approval Verification Must Exist**
   - Before mocka_decision_write, must verify Human Gate approval
   - But currently: no verification exists

2. **Duplicate Prevention Must Work**
   - Currently: No duplicate prevention in decision_ledger.jsonl
   - MCP can write same decision_id multiple times
   - Must implement per-record uniqueness

3. **Authority Field Must Be Real**
   - "approved_by" must come from verified source
   - Not client-supplied string
   - Must trace back to Human Gate

4. **Decision Ledger Must Own Authority**
   - Cannot reference mocka_events.db
   - Must contain all authority proof within itself
   - Currently: only partial information

### Risks with Option B

1. **No Human Verification** (RISK_B1)
   - Approver field is unverified
   - No proof human actually approved
   - System authority is compromised
   - **Impact**: Cannot trust authority

2. **Orphaned Decisions** (RISK_B2)
   - Decisions can exist without Human Gate context
   - No way to link back to approval request
   - No prior state information
   - **Impact**: Audit incomplete

3. **AI Safety Risk** (RISK_B3)
   - AI might trust unverified approval field
   - AI might execute false decisions
   - Authority could be spoofed
   - **Impact**: System compromise

4. **Duplicate Risk** (RISK_B4)
   - No duplicate prevention mechanism
   - Same decision_id can appear multiple times
   - Ledger integrity compromised
   - **Impact**: Audit cannot trust uniqueness

### Strengths of Option B

✅ **Immutable at File Level**: Existing records cannot be modified
✅ **Append-Only Semantics**: No deletion possible
✅ **Simple Storage**: Just a file, no database
✅ **Portable**: Can be archived/migrated easily
✅ **Chronological**: Shows decision timeline

⚠️ **But**: Authority is missing, unverified, incomplete

---

## OPTION C: HYBRID MODEL (Recommended Framework)

### Definition

Two separate systems with complementary responsibilities:

1. **mocka_events.db**: Authoritative source for Human Gate decisions
2. **decision_ledger.jsonl**: Formal record for canonical decision history

Each system is authoritative for its domain, with clear boundary.

### Architecture

```
Human Decision
    |
    v
[Human Gate Authority]
    |
    ├─> Events Table (mocka_events.db)
    |   └─ Authoritative: Who approved? When?
    |
    ├─> Approval Verified ✅
    |
    └─> LedgerAdapter [Authority Boundary]
        ├─ Verify: approval exists
        ├─ Verify: approver is valid
        ├─ Verify: no duplicate
        |
        └─> Decision Ledger (decision_ledger.jsonl)
            └─ Authoritative: What is formally recorded?
                ├─ approval_reference: HG20260813_001ABC
                ├─ approved_by: john_doe
                ├─ timestamp: 2026-08-13T10:30:45Z
                └─ [cannot modify, can only append]
```

### Responsibility Boundaries

#### mocka_events.db: Event Authority

**Authoritative For**:
- ✅ Who made the decision (person identity)
- ✅ When they made it (exact timestamp)
- ✅ What was the decision (approve/reject/cancel)
- ✅ What was the previous state
- ✅ Full decision lifecycle

**Schema**:
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

#### decision_ledger.jsonl: Decision Authority

**Authoritative For**:
- ✅ What decision was formally recorded
- ✅ When it was recorded
- ✅ Who approved it (linked to events)
- ✅ Immutable formal ledger
- ✅ Canonical decision history

**Schema**:
```json
{
  "decision_id": "DC_20260813_001",
  "request_id": "REQUEST_20260813_001",
  "status": "APPROVED",
  "actor": "john_doe",
  "human_gate_event_id": "HG20260813_001ABC",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "source": "HUMAN_GATE",
  "content_hash": "sha256:abc123..."
}
```

### LedgerAdapter as Boundary

LedgerAdapter enforces the transition from Event Authority to Decision Authority:

```
LedgerAdapter Responsibilities:
├─ Read: mocka_events.db (authority source)
├─ Verify: event exists and is APPROVED
├─ Extract: approver identity
├─ Validate: no duplicate decision_id
├─ Write: decision_ledger.jsonl
└─ Seal: cannot be bypassed
```

### Data Flow Example

**Real Scenario**:
```
Human Approves:
  1. Human Gate receives approval request
  2. Human reviews and approves
  3. Event written: HG20260813_001ABC → APPROVED
  4. Event stored: mocka_events.db

System Records:
  1. LedgerAdapter checks: Is HG20260813_001ABC approved? ✅ YES
  2. LedgerAdapter extracts: approver = "john_doe"
  3. LedgerAdapter verifies: No duplicate DC_001
  4. LedgerAdapter writes: Decision Ledger entry
  5. Entry stored: decision_ledger.jsonl (with link to HG event)

Query Authority:
  - Audit asks: "Who approved DC_001?"
  - Answer: Follow link to HG event → "john_doe"
  - Proof: Immutable event + immutable ledger entry
```

### Evaluation of Hybrid Model

#### 1. Human Authority Proof
**Score**: ✅ YES (EXCELLENT)

- Events table proves human made decision
- Ledger entry links back to event
- Double verification: both systems confirm
- **Proof chain**: Decision Ledger → HG Event → Person

#### 2. Tamper Resistance
**Score**: ✅ EXCELLENT

- Events table: event_id primary key
- Ledger file: append-only immutable
- Both levels protected
- No single point of failure

#### 3. Replay Capability
**Score**: ✅ YES (EXCELLENT)

- Events table: full state transition history
- Can reconstruct any point in time
- Decision Ledger: formal record
- Combined: complete picture

#### 4. Audit Capability
**Score**: ✅ COMPREHENSIVE

- Deep audit: mocka_events.db has all context
- Formal audit: decision_ledger.jsonl has record
- Two-level verification available
- Complete chain of custody

#### 5. Future AI Agent Compatibility
**Score**: ✅ POSSIBLE (with safeguards)

- AI can read formal decisions (Decision Ledger)
- AI can verify against authority (Events table)
- AI can execute with confidence
- **Safeguard**: Restrict AI to read-only, force manual decision

#### 6. Institutional Clarity
**Score**: ✅ CLEAR

- "Events are authority, ledger is formal record"
- Clear separation: humans in events, decisions in ledger
- No ambiguity: chain is obvious
- Easy to explain and verify

### Implementation Plan for Hybrid

**Phase 1: Design Consolidation** (Current)
- Document both systems' roles
- Establish boundary between them
- Design LedgerAdapter authority model

**Phase 2: Test Integration**
- Implement authority checks in LedgerAdapter
- Test full flow (events → ledger)
- Validate no bypasses possible

**Phase 3: Production Connection**
- Connect PHI-OS to LedgerAdapter
- Migrate to new flow for future decisions
- Keep legacy decisions as-is

**Phase 4: Closure**
- All new decisions flow through boundary
- Direct writes deprecated/blocked
- Authority model operational

### Risks with Hybrid Model

1. **Coordination Complexity** (RISK_C1)
   - Must maintain two systems
   - Queries span both
   - **Mitigation**: View/API layers abstract complexity

2. **Migration Burden** (RISK_C2)
   - Legacy decisions don't have events
   - Backfill incomplete
   - **Mitigation**: Accept incomplete history, enforce going forward

3. **Performance** (RISK_C3)
   - Every write queries two systems
   - **Mitigation**: Cache, indexes, async logging

### Strengths of Hybrid Model

✅ **Individual Authority**: Traceable to specific person
✅ **Immutable Record**: Formal decision ledger cannot change
✅ **Complete History**: Events give full context
✅ **Audit Trail**: Deep, verifiable, queryable
✅ **Safe for AI**: Authority can be machine-verified
✅ **Institutional Clarity**: Two roles are obvious
✅ **Replay-able**: Can reconstruct any state
✅ **Future-proof**: Designed to scale

---

## COMPARATIVE SCORECARD

| Dimension | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| **Human Authority Proof** | ✅ EXCELLENT | ❌ POOR | ✅ EXCELLENT |
| **Tamper Resistance** | ⚠️ MEDIUM | ✅ EXCELLENT | ✅ EXCELLENT |
| **Replay Capability** | ✅ EXCELLENT | ⚠️ LIMITED | ✅ EXCELLENT |
| **Audit Capability** | ✅ COMPREHENSIVE | ⚠️ LIMITED | ✅ COMPREHENSIVE |
| **AI Agent Compatibility** | ✅ POSSIBLE | ⚠️ RISKY | ✅ POSSIBLE |
| **Institutional Clarity** | ✅ CLEAR | ❌ CONFLICTING | ✅ CLEAR |
| **Implementation Cost** | 16 hours | 0 hours | 24 hours |
| **Risk Level** | MEDIUM | HIGH | LOW |
| **Institutional Value** | HIGH | LOW | VERY HIGH |

---

## RECOMMENDATION SUMMARY

**Option A** (Events-Only):
- ✅ Strong authority model
- ❌ Requires abandoning immutable ledger
- **Suitable if**: Institutional decision is to use event sourcing as primary authority

**Option B** (Ledger-Only):
- ✅ No changes needed (current state)
- ❌ Missing human authority verification
- ❌ Unsafe for formal governance
- **Suitable if**: Authority requirements are abandoned

**Option C** (Hybrid):
- ✅ Best of both systems
- ✅ Complete authority model
- ✅ Immutable formal record
- ✅ Full audit trail
- **Suitable if**: Institutional decision prioritizes authority and auditability

---

**PHASE 3 ANALYSIS COMPLETE**

Three options fully analyzed. No recommendation made (Human Gate authority).

Ready for Phase 4: Bypass Risk Final Classification.


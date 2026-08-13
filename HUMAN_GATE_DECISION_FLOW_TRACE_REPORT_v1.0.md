# HUMAN GATE DECISION FLOW TRACE REPORT v1.0

**Report Date**: 2026-08-13  
**Investigator**: KUROKO (Forensic Analysis)  
**Classification**: Phase 4 — Human Gate Review Support  
**Scope**: Complete lifecycle of Human Gate decisions from approval to persistence

---

## EXECUTIVE SUMMARY

Investigation identified **TWO DISTINCT HUMAN GATE IMPLEMENTATIONS**:

1. **PHI-OS Human Gate** (`phi_os/human_gate.py`) - Production state management
   - Event-sourced architecture (Flask blueprint)
   - Uses mocka_events.db for persistence
   - **NO connection to Decision Ledger**
   - **NO use of LedgerAdapter**

2. **Jarvis Human Gate** (`runtime/jarvis/gate/human_gate.py`) - Test/design pattern
   - Simple class-based implementation
   - Uses LedgerAdapter → LedgerStore
   - **NOT integrated into production**
   - **Test-only usage**

**Critical Finding**: The Human Gate implementation that uses LedgerAdapter (Jarvis) is NOT the production Human Gate. Production Human Gate (PHI-OS) does NOT connect to Decision Ledger or LedgerAdapter.

---

## IMPLEMENTATION 1: PHI-OS HUMAN GATE (PRODUCTION)

### Architecture

**File**: `phi_os/human_gate.py` (Flask Blueprint)

```
PHI-OS Application
    │
    ├─ Human Gate State Management
    │   ├─ /human_gate/submit (POST)
    │   ├─ /human_gate/approve (POST)
    │   ├─ /human_gate/reject (POST)
    │   └─ /human_gate/state (GET)
    │
    └─ Event Sourcing Backend
        └─ mocka_events.db
            └─ human_gate_events table
```

### Complete Decision Flow

**Stage 1: Request Submission**

```python
def submit(request_id: str, payload: dict) -> dict:
    """新しいHuman Gate requestを生成する。"""
    
    # Step 1: Validate request doesn't already exist
    conn = _get_conn()
    existing = _latest_event(conn, request_id)
    if existing and existing['next_state'] != 'CANCELED':
        raise HumanGateError(f"request_id already exists with state={existing['next_state']}")
    
    # Step 2: Generate event record
    event = {
        "event_id": _next_event_id(),        # HG20260813_NNNNNNNNN{hex}
        "timestamp": _now_iso(),             # ISO8601 UTC
        "type": "human_gate_request",
        "action": "submit",
        "request_id": request_id,
        "payload": json.dumps(payload),      # Serialized metadata
        "previous_state": None,              # New submission
        "next_state": "PENDING"
    }
    
    # Step 3: Persist event
    conn.execute(
        'INSERT INTO human_gate_events (...) VALUES (...)',
        (event_id, timestamp, type, action, request_id, payload, previous_state, next_state)
    )
    conn.commit()
    
    # Step 4: Return confirmation
    return {
        "request_id": request_id,
        "status": "PENDING",
        "event_id": event_id
    }
```

**Validation Performed**:
- ✅ Duplicate request_id check (prevents duplicate submissions)
- ✅ State transition validation (submit → PENDING only)
- ❌ Authority/permission check: NONE
- ❌ Decision content validation: NONE (payload is opaque JSON)

**Stage 2: Approval**

```python
def approve(request_id: str, approver: str) -> dict:
    """Human Gate request を承認する。"""
    
    # Step 1: Get current state
    conn = _get_conn()
    latest = _latest_event(conn, request_id)
    if not latest or latest['next_state'] != 'PENDING':
        raise HumanGateError(f"request_id not found or not in PENDING state")
    
    # Step 2: Generate approval event
    event = {
        "event_id": _next_event_id(),
        "timestamp": _now_iso(),
        "type": "human_gate_decision",
        "action": "approve",
        "request_id": request_id,
        "payload": json.dumps({"approver": approver}),  # Approver identity
        "previous_state": "PENDING",
        "next_state": "APPROVED"
    }
    
    # Step 3: Persist event
    conn.execute('INSERT INTO human_gate_events (...) VALUES (...)', (...))
    conn.commit()
    
    # Step 4: Return confirmation
    return {
        "request_id": request_id,
        "status": "APPROVED",
        "event_id": event_id
    }
```

**Validation Performed**:
- ✅ State validation (only PENDING → APPROVED)
- ✅ request_id validation (must exist and be PENDING)
- ❌ Approver authority check: NONE (approver is claimed by caller)
- ❌ Permission verification: NONE

**Stage 3: Rejection (Similar to Approval)**

```python
def reject(request_id: str, reason: str = "") -> dict:
    """Human Gate request を却下する。"""
    
    # Similar flow to approve(), but:
    # previous_state: "PENDING"
    # next_state: "REJECTED"
    # payload: json.dumps({"reason": reason})
```

### Data Persistence

**Storage**: `mocka_events.db` (SQLite)

**Table**: `human_gate_events`

```
┌─────────────────────────────────────────────────────────┐
│ human_gate_events                                       │
├─────────────────────────────────────────────────────────┤
│ event_id (TEXT, PRIMARY KEY)                            │
│ timestamp (TEXT, ISO8601)                               │
│ type (TEXT): "human_gate_request" | "human_gate_decision" │
│ action (TEXT): "submit" | "approve" | "reject"          │
│ request_id (TEXT)                                       │
│ payload (TEXT, JSON)                                    │
│ previous_state (TEXT): None | "PENDING" | ...           │
│ next_state (TEXT): "PENDING" | "APPROVED" | ...         │
└─────────────────────────────────────────────────────────┘
```

**Event Record Example**:
```json
{
  "event_id": "HG20260813_123456789abc",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "type": "human_gate_decision",
  "action": "approve",
  "request_id": "REQ_20260813_001",
  "payload": "{\"approver\": \"きむら博士\"}",
  "previous_state": "PENDING",
  "next_state": "APPROVED"
}
```

### State Reconstruction (Event Sourcing)

```python
def get_state(request_id: str) -> str | None:
    """request_idの現在状態をevent列から再構築する。"""
    
    # Query: Get latest event for this request_id
    latest_event = conn.execute(
        'SELECT * FROM human_gate_events WHERE request_id = ? ORDER BY timestamp DESC LIMIT 1',
        (request_id,)
    ).fetchone()
    
    # Return: next_state of latest event
    return latest_event['next_state'] if latest_event else None
```

**Implication**: Current state is NOT stored, only derived from event history.

### Authority/Metadata Handling

**Approver Information**:
- Stored in event payload: `{"approver": "きむら博士"}`
- **NOT verified** (caller-provided)
- Can be any string value

**Authority Chain**:
- Submit: No authority check
- Approve: approver name provided by caller, not verified
- Reject: reason provided by caller, no authority check

**Verdict**: ⚠️ WEAK
- Approver identity is **not cryptographically verified**
- Approval is **not authenticated** (any caller can claim to be anyone)
- No **role-based access control**

### Connection to Decision Ledger

**Status**: ❌ **NO CONNECTION**

**Evidence**:
- phi_os/human_gate.py does NOT import any LedgerAdapter
- phi_os/human_gate.py does NOT import any LedgerStore
- phi_os/human_gate.py does NOT write to data/decisions/decision_ledger.jsonl
- phi_os/human_gate.py uses mocka_events.db table only
- No call to LedgerAdapter.record()
- No call to LedgerStore.save()

**Conclusion**: PHI-OS Human Gate is COMPLETELY SEPARATE from Decision Ledger. They are independent systems with no integration path.

---

## IMPLEMENTATION 2: JARVIS HUMAN GATE (TEST/DESIGN)

### Architecture

**File**: `runtime/jarvis/gate/human_gate.py` (Simple class)

```
HumanGate Class
    │
    └─ LedgerAdapter (constructor)
        │
        └─ LedgerStore (constructor)
            │
            └─ File: data/jarvis_ledger.jsonl (default)
```

### Complete Decision Flow

**Stage 1: Create HumanGate Instance**

```python
class HumanGate:
    def __init__(self):
        self.status = "WAITING"
        self.ledger = LedgerAdapter()
```

**Initialization**:
- Creates LedgerAdapter instance
- LedgerAdapter creates LedgerStore with default path: `data/jarvis_ledger.jsonl`
- No parameters, no customization

**Stage 2: Request (Inquiry)**

```python
def request(self, decision_id):
    return {
        "decision_id": decision_id,
        "status": self.status,
        "authority": "human"
    }
```

**Behavior**:
- Returns decision metadata
- Does NOT persist
- Does NOT access ledger
- status = "WAITING" (initial state)

**Stage 3: Approval**

```python
def approve(self, decision_id):
    self.status = "APPROVED"
    return self.ledger.record(
        decision_id,
        self.status
    )
```

**Flow**:
1. Set internal status to "APPROVED"
2. Call LedgerAdapter.record(decision_id, "APPROVED")
3. LedgerAdapter creates DecisionRecord
4. LedgerStore.save() is called with duplicate prevention

**Persistence**:
- Written to: data/jarvis_ledger.jsonl
- NOT written to: data/decisions/decision_ledger.jsonl

**Stage 4: Rejection**

```python
def reject(self, decision_id):
    self.status = "REJECTED"
    return self.ledger.record(
        decision_id,
        self.status
    )
```

**Flow**: Same as approval, but status = "REJECTED"

### Data Persistence

**Storage**: `data/jarvis_ledger.jsonl` (JSONL file)

**Record Format**:
```json
{
  "decision_id": "DC_001",
  "status": "APPROVED",
  "timestamp": "2026-08-13T10:30:45.123456Z",
  "actor": "HUMAN_GATE"
}
```

**Persistence Path**:
```
HumanGate.approve()
    └─> LedgerAdapter.record()
        └─> DecisionRecord.to_dict()
            └─> LedgerStore.save()
                └─> File append to data/jarvis_ledger.jsonl
```

### Duplicate Prevention

**LedgerStore.save() Behavior**:

```python
def save(self, record):
    existing = self.load_all()
    
    if any(item.get("decision_id") == record.get("decision_id") for item in existing):
        return record  # Silently return without writing
    
    with self.path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    return record
```

**Duplicate Detection**:
- ✅ Reads all existing records
- ✅ Checks for duplicate decision_id
- ✅ Rejects duplicate (silent skip, doesn't write)
- ✅ But: No indication to caller (silent failure)

### Authority/Metadata Handling

**Authority Information**:
- actor field: hardcoded as "HUMAN_GATE"
- decision_id: caller-provided (no validation)
- timestamp: automatically generated (UTC)

**Authority Chain**:
- HumanGate.approve(): Sets status only
- LedgerAdapter.record(): No authority check
- LedgerStore.save(): No authority verification

**Verdict**: ⚠️ WEAK
- Actor identity is hardcoded, not individual
- decision_id is not verified
- No approval authentication

### Connection to Decision Ledger

**Status**: ❌ **NO CONNECTION**

**Evidence**:
- HumanGate writes to data/jarvis_ledger.jsonl
- Decision Ledger is at data/decisions/decision_ledger.jsonl
- Two completely separate files
- No coordination between them

**Production Integration**: ⚠️ **TEST-ONLY**
- JarvisEngine uses HumanGate
- But JarvisEngine is test-only
- No production code instantiates JarvisEngine or HumanGate

---

## COMPARISON: PHI-OS vs. JARVIS HUMAN GATE

| Aspect | PHI-OS | Jarvis |
|--------|--------|--------|
| **File Location** | phi_os/human_gate.py | runtime/jarvis/gate/human_gate.py |
| **Implementation Type** | Flask Blueprint | Simple Python Class |
| **Storage Backend** | SQLite (mocka_events.db) | JSONL file (jarvis_ledger.jsonl) |
| **State Management** | Event Sourcing | Simple status flag |
| **Persistence Architecture** | Event table | Append-only file |
| **Uses LedgerAdapter** | ❌ NO | ✅ YES |
| **Writes to Decision Ledger** | ❌ NO | ❌ NO |
| **Production Integrated** | ✅ YES | ❌ NO (test-only) |
| **Authority Verification** | ❌ NO | ❌ NO |
| **Approver Info Storage** | Event payload JSON | Hardcoded "HUMAN_GATE" |
| **Duplicate Prevention** | ✅ Built-in (request_id unique) | ✅ LedgerStore prevents |

---

## CRITICAL FINDING: NO PRODUCTION HUMAN GATE → DECISION LEDGER CONNECTION

### The Gap

```
PHI-OS Human Gate (Production)
    │
    ├─ mocka_events.db (human_gate_events table)
    │   └─ Decision Approval State
    │       (PENDING/APPROVED/REJECTED)
    │
    └─ NO CONNECTION TO:
        └─ data/decisions/decision_ledger.jsonl
```

**Implication**: When a Human Gate request is APPROVED in PHI-OS, it does NOT automatically create an entry in the Decision Ledger.

**Result**: 
- Human Gate decisions exist in mocka_events.db
- MCP decisions exist in decision_ledger.jsonl
- SealGov decisions exist in decision_ledger.jsonl
- **No unified decision authority model**

### Decision Recording Paths

**Path 1: Human Gate Decision**
```
Human submits → PHI-OS Human Gate → mocka_events.db
                                  └─ NOT in Decision Ledger
```

**Path 2: MCP Decision**
```
MCP Client → mocka_mcp_server.py → decision_ledger.jsonl
          └─ Bypasses Human Gate entirely
```

**Path 3: Seal Governance Decision**
```
Seal Request → SealGovernanceGate → decision_ledger.jsonl
            └─ GL7 authority check
```

**Missing Path**: Human Gate → Decision Ledger (designed but not implemented)

---

## JARVIS HUMANGATE LIFECYCLE (HYPOTHETICAL PRODUCTION USAGE)

If JarvisEngine/HumanGate were integrated into production:

```
User Decision
    │
    ├─ HumanGate.request(decision_id)
    │   └─ Returns: {"decision_id": "...", "status": "WAITING", "authority": "human"}
    │   └─ No persistence
    │
    ├─ HumanGate.approve(decision_id)
    │   ├─ Sets self.status = "APPROVED"
    │   ├─ Calls LedgerAdapter.record(decision_id, "APPROVED")
    │   ├─ LedgerStore checks for duplicates
    │   ├─ Writes to data/jarvis_ledger.jsonl
    │   └─ Returns: {"decision_id": "...", "status": "APPROVED", ...}
    │
    └─ Problem: This does NOT create entry in Decision Ledger
                (data/decisions/decision_ledger.jsonl)
```

**Gap**: Data/jarvis_ledger.jsonl ≠ data/decisions/decision_ledger.jsonl

---

## AUTHORITY INFORMATION FLOW

### PHI-OS Path (Production)

```
Approver Input (e.g., "きむら博士")
    │
    └─> approve(request_id, approver="きむら博士")
            │
            └─> Event payload: {"approver": "きむら博士"}
                    │
                    └─> Stored in mocka_events.db
                            │
                            └─ NOT verified
                            └─ NOT hashed
                            └─ NOT signed
```

**Authority Preservation**: ⚠️ WEAK
- approver name is stored but unverified
- Cannot distinguish authentic from spoofed approval
- Event record does not prove authorization

### Jarvis Path (Test)

```
HumanGate.approve(decision_id)
    │
    └─> DecisionRecord(decision_id, "APPROVED")
            │
            └─> Record: {"decision_id": "...", "status": "APPROVED", "actor": "HUMAN_GATE", ...}
                    │
                    └─> Stored in data/jarvis_ledger.jsonl
                            │
                            └─ actor hardcoded (no approver identity)
                            └─ Generic "HUMAN_GATE", not specific person
```

**Authority Preservation**: ❌ NONE (generic actor)

---

## FINDINGS

### Verified Facts

1. **Two separate HumanGate implementations exist**
   - PHI-OS (production Flask blueprint)
   - Jarvis (test/design simple class)

2. **PHI-OS HumanGate is production but NOT connected to Decision Ledger**
   - Uses mocka_events.db
   - No LedgerAdapter usage
   - No connection to decision_ledger.jsonl

3. **Jarvis HumanGate uses LedgerAdapter but is test-only**
   - Not integrated into production
   - Writes to different file (jarvis_ledger.jsonl)
   - Not used in any production code

4. **No production path from Human Gate to Decision Ledger**
   - Human decisions go to mocka_events.db
   - Decision Ledger receives MCP and SealGov decisions only
   - No unified authority model

5. **Authority information is weakly preserved**
   - PHI-OS: Approver name stored in JSON (unverified)
   - Jarvis: Actor hardcoded (no individual identity)
   - Neither path cryptographically verifies approval

6. **LedgerAdapter is isolated from production Human Gate**
   - Only used by test code (Jarvis HumanGate)
   - No production Human Gate calls LedgerAdapter
   - Designed boundary not integrated

### Boundary Implications

**Human Gate → LedgerAdapter → Decision Ledger Path**:
- ❌ NOT active in production
- ❌ NOT integrated with PHI-OS HumanGate
- ⚠️ Jarvis implementation exists but test-only
- ⚠️ LedgerAdapter sits between them but unused

---

**Report Status**: DECISION FLOW TRACE COMPLETE  
**Next Step**: TASK 2 - LedgerAdapter Authority Boundary Analysis

---

**Evidence Base**: Code inspection, integration tracing
**Verification Method**: Grep, read, architectural analysis
**Modifications**: NONE (read-only audit)

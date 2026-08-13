# HUMAN GATE BYPASS RISK REGISTER v1.0

**Report Date**: 2026-08-13
**Phase**: Human Gate Ledger Authority Boundary Consolidation — Phase 4
**Purpose**: Classify all bypass paths and their institutional risk levels

---

## BYPASS RISK CLASSIFICATION FRAMEWORK

Five risk severity levels:

| Level | Definition | Example |
|-------|-----------|---------|
| **CRITICAL** | Allows unauthorized decisions to become formal records | Unverified direct write to Decision Ledger |
| **HIGH** | Violates authority assumptions without detection | Duplicate decisions, approver spoofing |
| **MEDIUM** | Reduces assurance but not complete bypass | Direct writes with gating (SealGov GL7) |
| **LOW** | Test-only, isolated from production | Jarvis test paths |
| **INFORMATIONAL** | Design debt, migration necessary | LedgerAdapter unused, legacy paths |

---

## BYPASS ANALYSIS BY ROUTE

### BYPASS 1: MCP DIRECT WRITE

**Route**: mocka_mcp_server.py:mocka_decision_write() → _append_decision()

**Call Chain**:
```python
def mocka_decision_write(decision_id, title, context, approved_by, status, ...):
    # NO validation
    # NO authority check
    # NO Human Gate lookup
    # NO LedgerAdapter call
    # NO duplicate detection
    
    record = {
        "decision_id": decision_id,
        "title": title,
        "context": context,
        "approved_by": approved_by,  # Unverified, client-supplied
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "actor": "system:mcp_server"
    }
    
    _append_decision(record)  # Direct file write


def _append_decision(record):
    with open("data/decisions/decision_ledger.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
    # No failure handling, no receipt, no verification
```

**What It Bypasses**:
- ✅ Human Gate authority (no check)
- ✅ Human Gate approval workflow (no workflow)
- ✅ LedgerAdapter validation (no call)
- ✅ Duplicate prevention (no check, no uniqueness)
- ✅ Authority verification (no verification)
- ✅ Any form of approval gate

**What It Doesn't Bypass**:
- ❌ File-level append-only (immutability guaranteed)

**Who Can Exploit**:
- Any MCP client with network access
- Any system component using MCP server
- Internal tools calling mocka_decision_write

**Proof of Exploitation**:
```python
# Attacker (or buggy code) creates fake decision
mocka_decision_write(
    decision_id="DC_20260813_EXPLOIT",
    title="Unauthorized Policy",
    context="No approval was sought",
    approved_by="system:attacker",  # Not verified
    status="APPROVED"  # Unilaterally approved
)

# Result: Decision appears in decision_ledger.jsonl
# Looks like legitimate decision to untrained eye
# No indication it was unauthorized
# No Human Gate approval exists
```

**Impact Assessment**:

| Dimension | Impact |
|-----------|--------|
| **Authority Undermined** | YES (completely) |
| **Audit Trail Broken** | YES (no proof of approval) |
| **Duplicates Possible** | YES (no prevention) |
| **Institutional Governance** | YES (human oversight bypassed) |
| **Decision Ledger Integrity** | YES (false entries added) |

**Risk Classification**: **CRITICAL**

**Rationale**: 
- Allows any client to create decisions with false authority
- No verification, no approval, no safeguard
- Results in formal decision records without institutional authorization
- Undermines entire authority model
- **This is the primary attack vector**

**Mitigation**:
- Implement approval verification in mocka_decision_write
- Check Human Gate events before allowing write
- Use LedgerAdapter boundary
- Fail-closed: reject unapproved decisions

---

### BYPASS 2: SEALGOVERNANCE DIRECT WRITE

**Route**: governance/seal_governance_gate.py:execute() → _record_decision_unit()

**Call Chain**:
```python
def execute(seal_spec, seal_payload, ...):
    # GATING: GL7 governance check performed
    authority_check = perform_gl7_check(seal_spec)
    if not authority_check:
        raise GovernanceError("GL7 check failed")
    
    # Execute seal script
    seal_result = execute_seal_script(seal_payload)
    
    # Record decision
    _record_decision_unit(seal_result)  # Direct write to Decision Ledger


def _record_decision_unit(result):
    record = {
        "decision_id": result.decision_id,
        "execution_id": result.execution_id,
        "status": "EXECUTED",
        "actor": "system:seal_governance_gate",
        "timestamp": datetime.now().isoformat()
    }
    
    # Direct file append, no intermediate boundary
    with open("data/decisions/decision_ledger.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
```

**What It Bypasses**:
- ✅ Human Gate approval requirement (not checked at write time)
- ✅ LedgerAdapter validation (not called)
- ✅ Authority re-verification at write time (GL7 check was pre-execution only)
- ✅ Duplicate prevention (no check)

**What It Doesn't Bypass**:
- ❌ File-level append-only (immutability guaranteed)
- ❌ GL7 governance check (performed before execution)

**Who Can Exploit**:
- Seal operators with GL7 approval
- Authorized users in governance layer
- Seal scripts (if they can be controlled)

**Proof of Exploitation**:
```python
# Execute 1: GL7 check passes, seal executes, decision recorded
seal_governance_gate.execute(seal_spec)

# Execution 2 (Retry, hours later): 
# GL7 state may have changed, but is not re-checked at write time
seal_governance_gate.execute(seal_spec)  # GL7 check happens again first

# Result: Decision written twice (if no duplicate prevention elsewhere)
# Or: Execution state changed between GL7 check and write
```

**Impact Assessment**:

| Dimension | Impact |
|-----------|--------|
| **Authority Undermined** | PARTIAL (GL7 checked, but pre-execution) |
| **Audit Trail Broken** | PARTIAL (execution_id different, can trace) |
| **Duplicates Possible** | YES (no write-time prevention) |
| **Institutional Governance** | PARTIAL (GL7 enforces, not Human Gate) |
| **Decision Ledger Integrity** | PARTIAL (can have duplicate executions) |

**Risk Classification**: **MEDIUM**

**Rationale**:
- GL7 governance check is present (gates authority somewhat)
- But check is at pre-execution time, not at write time
- Re-execution/retry can write duplicate records
- No re-verification at write time
- Less severe than MCP (has some authority check), but still a gap
- **Institutional governance applies, but temporal gap exists**

**Specific Risk Scenario**:
```
Timeline:
10:00 - GL7 check: seal is approved (APPROVED)
10:00 - Seal executes
10:01 - First write to Decision Ledger succeeds

10:15 - Network error, retry initiated
10:15 - GL7 check again: seal is approved (still APPROVED)
10:15 - Seal executes again
10:16 - Second write to Decision Ledger succeeds
       (Same execution_id? If so, duplicate)

Result: Same decision recorded twice in ledger
Audit: Cannot tell which is "correct"
```

**Mitigation**:
- Implement idempotency check: has this execution already been recorded?
- Use LedgerAdapter with duplicate detection
- Re-verify at write time, not just pre-execution
- Fail-closed if execution already recorded

---

### BYPASS 3: DIRECT FILE I/O

**Route**: File system write directly to decision_ledger.jsonl

**Method**:
```python
# Attacker with file access bypasses all application logic
with open("data/decisions/decision_ledger.jsonl", "a") as f:
    # Write arbitrary JSON line
    f.write('{"decision_id":"DC_FAKE","status":"APPROVED"}\n')

# No validation, no authority check, no application logic
# Just direct file manipulation
```

**What It Bypasses**:
- ✅ MCP server validation (never called)
- ✅ SealGov governance (never called)
- ✅ LedgerAdapter checks (never called)
- ✅ All application-level safeguards
- ✅ All business logic

**What It Doesn't Bypass**:
- ❌ File system permissions (requires write access)
- ❌ Append-only enforcement (still append-only)

**Who Can Exploit**:
- System administrator
- Anyone with file system write access to data/ directory
- Container security breach
- Physical access to server

**Proof of Exploitation**:
```bash
# Admin account or compromised container
echo '{"decision_id":"DC_ADMIN_BACKDOOR","approved_by":"admin","status":"APPROVED"}' >> data/decisions/decision_ledger.jsonl

# Result: Fake decision in ledger
# No application validation was performed
# No audit trail of who wrote it (file system logs only)
```

**Impact Assessment**:

| Dimension | Impact |
|-----------|--------|
| **Authority Undermined** | YES (completely) |
| **Audit Trail Broken** | YES (no app-level logging) |
| **Duplicates Possible** | YES (no validation) |
| **Institutional Governance** | YES (governance bypassed) |
| **Decision Ledger Integrity** | YES (arbitrary content) |

**Risk Classification**: **MEDIUM** (high impact, low probability)

**Rationale**:
- Requires elevated file system access
- Probability is lower (not just network access)
- But impact is total (all safeguards bypassed)
- **Access control is the mitigation**
- **Not a design flaw, a deployment security issue**

**Mitigation**:
- Restrict file write access (OS-level permissions)
- Encrypt file with hardware key
- Monitor file access (audit logs)
- Separate file system from application (read-only for app)

---

### BYPASS 4: JARVIS TEST PATH

**Route**: runtime/jarvis/gate/human_gate.py → LedgerAdapter → LedgerStore

**Call Chain**:
```python
def approve(self, decision_id, status):
    # Uses LedgerAdapter (has duplicate prevention)
    record = LedgerAdapter().record(decision_id, status)
    
    # But writes to test file, not production Decision Ledger
    # jarvis_ledger.jsonl is NOT decision_ledger.jsonl
    
    return record


class LedgerAdapter:
    def record(self, decision_id, status):
        record = DecisionRecord(
            decision_id,
            status
        ).to_dict()
        
        return self.store.save(record)  # LedgerStore


class LedgerStore:
    def save(self, record):
        # Reads all existing records from jarvis_ledger.jsonl
        existing = self._read_all()
        
        # Check for duplicate
        if any(r['decision_id'] == record['decision_id'] for r in existing):
            return record  # Silent skip, return as if success
        
        # Write to jarvis_ledger.jsonl (test file)
        with open("data/jarvis_ledger.jsonl", "a") as f:
            f.write(json.dumps(record) + "\n")
        
        return record
```

**What It Bypasses**:
- ✅ Decision Ledger (writes to different file)
- ✅ Production authority model (test-only)
- ✅ MCP server path (doesn't use it)

**What It Doesn't Bypass**:
- ❌ LedgerAdapter (actually uses it)
- ❌ LedgerStore (actually uses it)
- ❌ Duplicate prevention (LedgerStore checks)
- ❌ Append-only (both files append-only)

**Scope**: Test-only, never runs in production

**Proof of Exploitation**:
```python
# This only affects test environment
# Jarvis is development/test framework
# Not used in production (PHI-OS is production)

adapter.record("TEST_001", "APPROVED")
adapter.record("TEST_001", "REJECTED")  # Duplicate, silently skipped

# Result: data/jarvis_ledger.jsonl has one entry
# Result: data/decisions/decision_ledger.jsonl untouched (production not affected)
```

**Impact Assessment**:

| Dimension | Impact |
|-----------|--------|
| **Production Authority** | NO (test-only) |
| **Production Audit** | NO (test-only) |
| **Test Integrity** | PARTIAL (duplicate detection works, but silent) |
| **Institutional Governance** | NO (not production) |

**Risk Classification**: **LOW** (isolated to test)

**Rationale**:
- Completely isolated from production
- Does not affect production Decision Ledger
- Does not affect production decisions
- Test-only code, test-only data
- **Not a production vulnerability**

**Mitigation** (for test environment):
- Add logging for silent skips
- Make duplicate detection loud (throw exception)
- Ensure test data is separate from production

---

### BYPASS 5: PHI-OS PRODUCTION HUMAN GATE

**Route**: phi_os/human_gate.py:approve() → mocka_events.db (not Decision Ledger)

**Call Chain**:
```python
def approve(self, request_id, approver):
    # PHI-OS Human Gate implementation
    
    # Step 1: Validation
    conn = _get_conn()
    existing = _latest_event(conn, request_id)
    if existing and existing['next_state'] != 'CANCELED':
        raise HumanGateError("Request already exists")
    
    # Step 2: Event creation
    event = {
        "event_id": _next_event_id(),
        "timestamp": _now_iso(),
        "type": "human_gate_request",
        "action": "approve",
        "request_id": request_id,
        "next_state": "APPROVED",
        "approver": approver  # Caller-supplied name
    }
    
    # Step 3: Persist to mocka_events.db
    conn.execute(
        'INSERT INTO human_gate_events (...) VALUES (...)',
        (event['event_id'], event['timestamp'], ...)
    )
    conn.commit()
    
    # Step 4: NOT written to Decision Ledger
    # NO LedgerAdapter call
    # NO decision_ledger.jsonl write
    # NO formal decision record created
```

**What It Bypasses**:
- ✅ Decision Ledger (not written to)
- ✅ LedgerAdapter (not called)
- ✅ Formal decision record creation
- ✅ Append-only enforcement (uses mutable DB)

**What It Doesn't Bypass**:
- ❌ Human Gate approval (IS the Human Gate)
- ❌ Authority (approver is recorded)
- ❌ Duplicate prevention (request_id checked)

**Gap**: No connection between approval and Decision Ledger entry

**Proof of the Gap**:
```
Scenario: Human approves request

Step 1: Human approval happens
  human_gate.approve("REQUEST_123", approver="alice")
  
Result:
  mocka_events.db: [APPROVED event recorded]
  decision_ledger.jsonl: [Nothing - no entry created]

Consequence:
  Formal record of approval: ABSENT
  Proof of authority: EXISTS (in events DB, not ledger)
  Audit trail: INCOMPLETE
```

**Impact Assessment**:

| Dimension | Impact |
|-----------|--------|
| **Authority Exists** | YES (in mocka_events.db) |
| **Authority in Decision Ledger** | NO (not propagated) |
| **Formal Decision Record** | NO (not created) |
| **Audit Trail** | INCOMPLETE (split across systems) |
| **Unified Authority Model** | NO (disconnected) |

**Risk Classification**: **INFORMATIONAL** (architectural gap, not security risk)

**Rationale**:
- Not a bypass in the attack sense
- Is the Human Gate (correct component)
- Authority is correctly recorded (in mocka_events.db)
- **Problem**: Authority not propagated to formal Decision Ledger
- **This is design debt, not exploitation**

**Design Issue**: 
- Designed: Human Gate → LedgerAdapter → Decision Ledger
- Actual: Human Gate → mocka_events.db (stop here, no propagation)
- Impact: Two-system audit required, authority not formalized

**Mitigation**:
- Integrate PHI-OS to LedgerAdapter
- Trigger Decision Ledger write on approval
- Use LedgerAdapter as boundary (Model B from Phase 2)

---

## CONSOLIDATED BYPASS RISK MATRIX

| Bypass Route | Risk Level | Who Can Use | Authority Check | Duplicate Prevention | Production Impact |
|---|---|---|---|---|---|
| **MCP Direct Write** | CRITICAL | Any MCP client | ❌ NO | ❌ NO | YES (direct entry) |
| **SealGov Direct Write** | MEDIUM | GL7-authorized users | ✅ GL7 only | ❌ NO | YES (with gating) |
| **File I/O Direct** | MEDIUM | File system access | ❌ NO | ❌ NO | YES (requires access) |
| **Jarvis Test** | LOW | Test harness | ⚠️ Silent | ✅ LedgerStore | NO (test-only) |
| **PHI-OS Native** | INFORMATIONAL | Authorized approvers | ✅ YES | ✅ YES | Design gap (not breach) |

---

## CRITICAL VULNERABILITIES

### VULN-001: Unverified MCP Authority

**Risk Level**: CRITICAL

**Description**: MCP server accepts any "approved_by" value without verification

**Exploitation**:
```python
mocka_decision_write(
    "DC_SPOOFED",
    approved_by="fake_authority",  # Any string accepted
    status="APPROVED"
)
# Result: Enters Decision Ledger as if approved by "fake_authority"
```

**Impact**: Decision authority is untrustworthy

**Remediation**: Mandatory Human Gate lookup before MCP write

---

### VULN-002: No Duplicate Decision ID Prevention

**Risk Level**: CRITICAL

**Description**: Multiple entries with same decision_id can exist in Decision Ledger

**Exploitation**:
```python
mocka_decision_write("DC_001", ...)
mocka_decision_write("DC_001", ...)  # Same ID, different content

# Result: Ledger has conflicting entries
# Audit: Cannot determine which is "correct"
```

**Impact**: Ledger integrity compromised

**Remediation**: Implement uniqueness constraint (LedgerAdapter with lookup)

---

### VULN-003: No Authority Verification at Write Time

**Risk Level**: CRITICAL

**Description**: No verification that decision was actually approved

**Exploitation**:
```python
# Unauthorized: approval doesn't actually exist
mocka_decision_write("DC_UNAUTHORIZED", approved_by="alice", status="APPROVED")

# Result: Ledger contains decision with unverified approval
# Audit: Cannot prove alice actually approved this
```

**Impact**: Authority model is compromised

**Remediation**: Mandatory authority verification (LedgerAdapter Model B)

---

## RISK SUMMARY BY SEVERITY

### CRITICAL (Immediate Action Required)

1. MCP Direct Write - Unverified authority
2. No Duplicate Prevention - Ledger can be corrupted
3. No Authority Verification - Approvals can be forged

**Mitigation Strategy**: Implement LedgerAdapter boundary (Model B)

### MEDIUM (Action Required)

1. SealGov Retry Risk - GL7 check doesn't prevent re-execution
2. File I/O Access - Admin access can write directly
3. Temporal Gap - Pre-exec check vs. write-time check

**Mitigation Strategy**: Add write-time verification, restrict access

### LOW (Monitor)

1. Jarvis Test Silent Failures - Test code assumes success incorrectly

**Mitigation Strategy**: Add logging, make failures loud

### INFORMATIONAL (Design Debt)

1. PHI-OS Disconnection - Authority not propagated to Decision Ledger

**Mitigation Strategy**: Connect PHI-OS to LedgerAdapter

---

## INSTITUTIONAL IMPLICATIONS

**Current State**: 
- Multiple bypass paths exist
- Authority is unverified
- Duplicates are possible
- Decision Ledger integrity is questionable

**If Boundaries Are Designed But Not Enforced**:
- Test code provides false confidence
- Production bypasses are operational
- Audit trail is incomplete
- Governance authority is undermined

**If Boundaries Are Enforced**:
- All bypasses are blocked
- Authority is verified
- Duplicates prevented
- Institutional governance operational

---

**PHASE 4 CLASSIFICATION COMPLETE**

All bypass paths classified and risk levels assigned.

Ready for Phase 5: Human Gate Decision Package Creation.


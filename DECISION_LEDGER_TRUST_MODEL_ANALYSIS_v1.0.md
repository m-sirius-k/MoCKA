# DECISION LEDGER TRUST MODEL ANALYSIS v1.0

**Report Date**: 2026-08-13  
**Investigator**: KUROKO (Forensic Analysis)  
**Classification**: Phase 4 — Human Gate Review Support  
**Scope**: Trust guarantees provided by current Decision Ledger implementation

---

## EXECUTIVE SUMMARY

Decision Ledger currently provides **PARTIAL trust guarantees**:

| Trust Dimension | Guarantee | Evidence | Risk |
|-----------------|-----------|----------|------|
| **Authenticity** | Weak | approved_by field unverified | HIGH |
| **Authority** | Partial | GL7 for SealGov only, not for MCP | HIGH |
| **Uniqueness** | None | No duplicate prevention in production | HIGH |
| **Immutability** | Strong | Append-only file enforcement | ✅ LOW |
| **Traceability** | Partial | Companion events not guaranteed | MEDIUM |

---

## 1. AUTHENTICITY

### Question: Can we prove who created this decision?

### Current Implementation

**MCP Server Path** (`mocka_mcp_server.py:970-1004`):

```python
def mocka_decision_write(...):
    approved_by = args.get("approved_by", "").strip()
    # ...
    record = {
        "approved_by": approved_by,  # ← UNVERIFIED
        # ...
    }
```

**Evidence**:
- Client provides `approved_by` as input
- No verification that client is authorized as that person
- No signature verification
- No session/authentication check
- Direct string acceptance

**Example Attack**:
```
Attacker:
1. Call: mocka_decision_write(approved_by="きむら博士", title="...", ...)
2. No authentication required
3. Decision Ledger entry: {"approved_by": "きむら博士", ...}

Result: Ledger claims きむら博士 approved this decision
Reality: Any MCP client can make this claim
```

**SealGovernance Path** (`governance/seal_governance_gate.py:135`):

```python
entry = {
    "approved_by": "system:seal_governance_gate",  # ← HARDCODED
    # ...
}
```

**Evidence**:
- approved_by is hardcoded as "system:seal_governance_gate"
- GL7 governance check verifies authority
- But: Actual human decision authority is opaque
- GL7 check is structural, not personal

**MCP Event Companion** (`mocka_mcp_server.py:1008-1027`):

```python
try:
    gate_payload = {
        "who_actor": args.get("approved_by", _DEFAULT_ACTOR),  # ← May fail
        # ...
    }
    r = requests.post(GATE_URL, json=gate_payload, timeout=5)
    # ...
except Exception as _companion_err:
    print(f"[MCP] mocka_decision_write companion event failed: {_companion_err}", 
          flush=True)  # ← Silently continues on failure
```

**Evidence**:
- Companion event (mocka_write_event) is attempted but not guaranteed
- If event service is unavailable, decision is still written
- No correlation between decision and event required
- audit trail may be incomplete

### Authenticity Verification Capability

**What can we prove from the ledger alone?**

✅ Can prove:
- A decision_id exists with a claimed approved_by value
- The record was written to the ledger file
- The timestamp when it was written

❌ Cannot prove:
- The claimed approver actually authorized this
- The approver's identity is authentic
- No impersonation occurred
- The approval was intentional (not injected)
- The approver understood the decision content

### Authenticity Risk Assessment

**Risk Level**: ⚠️ **HIGH**

**Risk Scenarios**:
1. **Direct Impersonation**: MCP client claims to be someone else
2. **Batch Injection**: Attacker submits multiple decisions with false approved_by values
3. **Event Gap**: Companion event fails, decision written without audit trail
4. **Missing Verification**: No cryptographic proof of approval

**Mitigation Capability**: ❌ NONE currently
- No signature verification
- No approval confirmation
- No timestamp validation against approver's history
- No cross-reference to authorization logs

---

## 2. AUTHORITY

### Question: Can we prove the creator had permission?

### Current Implementation

**MCP Path Authority**: ❌ **NO VERIFICATION**

```python
def mocka_decision_write(...):
    # No check on who is calling
    # No permission lookup
    # No authorization gate
    # Direct write if schema valid
```

**Authority Model**: 
- Caller: Any MCP client
- Permission: MCP tool access only
- Check: Tool name = mocka_decision_write exists
- Result: No per-decision authorization

**Example**:
```
MCP Client with access to mocka_decision_write tool
    └─ Can call with ANY decision_id
    └─ Can claim ANY approved_by value
    └─ Can set ANY status (Active/Superseded/Withdrawn)
    └─ No per-decision permission check
    └─ No Human Gate review
    └─ No approval workflow
```

**SealGovernance Path Authority**: ✅ **GL7 CHECK**

```python
def execute(self, message: str, ...):
    approval = self.governance.pre_execution_check(action)  # ← GL7 check
    
    if not approval.approved:
        result = GateResult(approved=False, ...)
        self._record_decision_unit(execution_id, change_start, result)
        return result
    # ... continue only if approved
```

**Authority Model**:
- Caller: Governance operation (audit/seal)
- Permission: GL7 structural governance engine
- Check: Scope, change limits, policy rules
- Result: Approval or rejection

**Gap**: GL7 check happens before decision_id is generated
- If decision_id changes or retry occurs, no re-verification
- Authority gate is not atomic with write

**LedgerAdapter Authority**: ❌ **NONE**

```python
def record(self, decision_id, status):
    record = DecisionRecord(decision_id, status).to_dict()
    return self.store.save(record)
```

**Authority Model**:
- Caller: Whoever instantiates HumanGate
- Permission: None (test-only)
- Check: None
- Result: Always passes (test scenario)

### Authority Verification Capability

**What can we prove from the ledger alone?**

✅ Can prove:
- SealGovernance: GL7 dry-run passed (if aborts field is empty)
- SealGovernance: Seal script executed (if seal_hash is present)

❌ Cannot prove:
- MCP: Client had authority to make the decision
- MCP: Human approved this decision
- MCP: Decision aligned with policy
- MCP: No privilege escalation occurred
- SealGov: Re-execution/retry authorization
- Any path: Who made the final approval

### Authority Risk Assessment

**Risk Level**: ⚠️ **HIGH** (MCP) **MEDIUM** (SealGov)

**MCP Risks**:
1. Unauthorized decision recording
2. Privilege escalation (low-permission client claims high-authority decision)
3. Bypass of Human Gate or approval workflow
4. Rogue decisions injected without governance

**SealGov Risks**:
1. GL7 check bypassed (would require governance structure change)
2. Retry without re-authorization
3. Authority transferred to "system:seal_governance_gate" (human accountability lost)

**Mitigation Capability**: ⚠️ **PARTIAL** (SealGov only)
- GL7 governance check (external authority verification)
- For MCP: No mitigation exists

---

## 3. UNIQUENESS

### Question: Can we prove this decision_id exists only once?

### Current Implementation

**MCP Path Uniqueness**: ❌ **NOT ENFORCED**

```python
def _append_decision(record):
    """decision_ledger.jsonlへ1行追記する（append-only、既存行は変更しない）。"""
    # No uniqueness check
    with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**Current State**:
- Duplicate decision_id values can be written
- Multiple records with same decision_id possible
- No detection
- No rejection
- No error

**SealGovernance Path Uniqueness**: ⚠️ **DETERMINISTIC BUT NOT UNIQUE**

```python
def execute(self, message: str, ...):
    execution_id = f"EXEC_{datetime.now(...).strftime(...)}_{uuid.uuid4().hex[:8]}"
    entry = {
        "decision_id": f"DC_{execution_id}",
        # ...
    }
```

**Current State**:
- execution_id uses timestamp + UUID (should be unique per execution)
- decision_id derived from execution_id (deterministic)
- But: Retry/re-execution can use same execution_id
- Timestamp has second-level precision (low granularity)
- UUID is 8 chars (128 bits per execution, but decision_id deterministic from exec_id)

**LedgerAdapter Uniqueness**: ✅ **ENFORCED** (but silent)

```python
def save(self, record):
    existing = self.load_all()
    
    if any(item.get("decision_id") == record.get("decision_id") for item in existing):
        return record  # Silently skip
    
    with self.path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**Current State**:
- Checks all existing records for duplicate
- Rejects duplicate without writing
- But: Silent rejection (no error indication)

### Uniqueness Verification Capability

**What can we prove from the ledger alone?**

✅ Can prove:
- A decision_id value exists
- Multiple records with same decision_id means either:
  a) Duplicate (error)
  b) Intended supersede (valid)
- Cannot distinguish from ledger alone

❌ Cannot prove:
- decision_id is truly unique (duplicates might exist)
- Duplicate detection occurred
- Duplicate was rejected
- Latest version is authoritative

### Uniqueness Risk Assessment

**Risk Level**: ⚠️ **HIGH** (MCP) **MEDIUM** (SealGov)

**Failure Scenario**:
```
Decision: "DC_20260815_001"
  Record 1: {decision_id: "DC_20260815_001", title: "A", status: "Active"}
  Record 2: {decision_id: "DC_20260815_001", title: "B", status: "Active"}
  Record 3: {decision_id: "DC_20260815_001", title: "C", supersedes: null, superseded_by: null}

Reader Question: Which is the current decision?
  └─ JSON file shows 3 records, all active, no clear supersede chain
  └─ Reader must assume last one is current
  └─ But: No explicit indication this is intentional or an error
  └─ Ambiguity: Is Record 2 a mistake or intentional update?
```

**Mitigation Capability**: ❌ **NONE** (MCP)
- LedgerStore could prevent duplicates if used
- But not integrated into production
- No alternative uniqueness mechanism

---

## 4. IMMUTABILITY

### Question: Can historical decisions be changed?

### Current Implementation

**Append-Only File Mode**: ✅ **STRONG ENFORCEMENT**

Both MCP and SealGovernance paths:
```python
with open(DECISION_LEDGER_PATH, "a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

**File System Level**:
- `"a"` mode: append-only, no truncate/seek
- File grows, never shrinks
- Once written, bytes cannot be modified
- OS-level protection (not application-dependent)

**JSONL Format**:
- One record per line
- Line cannot be modified without rewriting entire file
- Rewriting would require re-opening in write mode (`"w"`)
- No code path does this

**LedgerStore Enforcement**: ✅ **SAME** (append-only)

```python
with self.path.open("a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

### Immutability Verification Capability

**What can we prove from the ledger alone?**

✅ Can prove:
- Records exist in file with specific content
- No record was deleted (JSONL lines remain)
- No record was truncated (file only grows)
- Historical order is preserved (append-only order)

✅ Can verify:
- File hash (SHA256) to detect any modification
- Line count (number of records)
- First/last record timestamps

❌ Cannot prove:
- Original value of a field (if metadata lost)
- Whether a record is superseded (except via superseded_by field)
- Which record is "authoritative" (if duplicates exist)

### Immutability Risk Assessment

**Risk Level**: ✅ **LOW**

**Why Low Risk**:
- OS-level file mode enforcement
- No application code can modify records
- No delete operation possible
- File-based protection is strong

**Residual Risks**:
1. **File System Bypass** (MEDIUM): Direct disk access could modify file
2. **Backup/Restore Confusion** (MEDIUM): Restored from old backup without awareness
3. **Version Control Issues** (LOW): Git rebase could lose records (but indicates code change, not data change)

**Mitigation Capability**: ✅ **STRONG**
- Append-only file mode is enforced
- No application-level overwrite possible
- Cryptographic hashing can verify integrity
- Regular backups ensure recovery

---

## 5. TRACEABILITY

### Question: Can the full decision lifecycle be reconstructed?

### Current Implementation

**Companion Event System** (MCP Path):

```python
try:
    gate_payload = {
        "who_actor":       args.get("approved_by", _DEFAULT_ACTOR),
        "who_role":        "executor",
        "who_session":     SESSION_ID,
        "what_type":       "claude_mcp",
        "what_title":      f"[DECISION_MADE] {decision_id}: {title}",
        "where_path":      "mocka_mcp_server.py",
        "where_component": "mcp_caliber",
        "why_purpose":     rationale[:80] or title,
        "how_trigger":     "mcp_tool_call",
        "after_state":     decision[:200] or title,
        "description":     f"decision_id={decision_id}\n...",
        "tags":            f"decision_ledger,{decision_id},{status}",
    }
    r = requests.post(GATE_URL, json=gate_payload, timeout=5)
    if r.status_code == 201:
        event_id = r.json().get("event_id")
except Exception as _companion_err:
    print(f"[MCP] mocka_decision_write companion event failed: {_companion_err}", 
          flush=True)
```

**Current State**:
- Attempts to create event in mocka_write_event system
- Event_id is captured and returned
- But: Failure is silent (print only, no exception)
- Event creation is not guaranteed
- Ledger write succeeds even if event fails

**Traceability Fields in Decision Record** (MCP):

```python
"related_events":    args.get("related_events", []),
"related_documents": args.get("related_documents", []),
```

**Current State**:
- Optional array fields
- Caller-provided (unverified)
- No automatic event correlation
- No automatic schema reference

**Decision ID Format** (MCP):

```python
decision_id = args.get("decision_id", "").strip() or _next_decision_id()
# _next_decision_id() → DC_YYYYMMDD_NNN format
```

**Current State**:
- decision_id embeds date
- Can count decisions per day
- Sequential numbering helps identify scope
- But: No direct link to session or operator

**SealGovernance Traceability** (SealGov Path):

```python
entry = {
    "decision_id": f"DC_{execution_id}",
    "execution_id": execution_id,          # ← Traceable to seal operation
    "change_start": change_start,          # ← Timestamp
    "change_done": datetime.now(...),      # ← When recorded
    "artifact_hash": commit_hash,          # ← Commit SHA
    "seal_hash": summary_hash,             # ← Seal hash
    "aborts": result.aborts,               # ← GL7 aborts
}
```

**Current State**:
- execution_id provides direct link to seal operation
- Can trace back to GL7 decision
- artifact_hash links to git commit
- Better traceability than MCP path

### Traceability Verification Capability

**What can we reconstruct from the ledger alone?**

✅ Can trace:
- Decision creation timestamp (approved_at field)
- decision_id sequence (DC_YYYYMMDD_NNN)
- Status transitions (via supersedes chain)
- Seal operations (via execution_id)
- Git commits (via artifact_hash in SealGov)

❌ Cannot trace:
- MCP: Which session/user created this
- MCP: What events occurred before/after
- MCP: Approval workflow steps
- MCP: Rejections that occurred
- Any path: Full lifecycle if companion event fails
- Any path: Requester identity (only approved_by shown)

### Traceability Risk Assessment

**Risk Level**: ⚠️ **MEDIUM**

**Traceability Gaps**:
1. **Event Correlation**: Companion events may not be created
2. **Session Loss**: MCP client identity not captured
3. **Approval Workflow**: Steps before decision not recorded
4. **Rejection History**: Duplicates that were rejected not logged
5. **Related Events Gap**: No automatic correlation to triggering events

**Traceability Capabilities by Path**:
- **MCP Path**: LOW traceability (only decision record)
- **SealGov Path**: MEDIUM traceability (execution_id, artifact_hash)
- **LedgerAdapter Path**: LOW traceability (test-only)

**Mitigation Capability**: ⚠️ **PARTIAL**
- SealGov has strong traceability via execution_id
- MCP path needs event correlation or session capture
- Companion event system is optional (may fail)

---

## TRUST MODEL SUMMARY TABLE

| Dimension | Guarantee | Verification | Risk | Enforcement |
|-----------|-----------|--------------|------|------------|
| **Authenticity** | Weak | approved_by unverified | HIGH | None |
| **Authority** | Partial | GL7 (SealGov only) | HIGH | Governance gate |
| **Uniqueness** | None | No check (MCP) | HIGH | File append-only |
| **Immutability** | Strong | File mode enforcement | LOW | OS-level |
| **Traceability** | Partial | Event correlation optional | MEDIUM | SealGov better |

**Overall Trust Level**: ⚠️ **MODERATE**

---

## FAILURE SCENARIOS

### Scenario A: Impersonation Attack

```
Attacker (no authorization):
1. Call: mocka_decision_write(
     approved_by="きむら博士",
     title="Approve attacker's project",
     decision="Approved",
     ...
   )
2. No authentication check
3. No identity verification
4. Decision written to ledger

Result:
  └─ Ledger shows: {"approved_by": "きむら博士", "title": "Approve attacker's project", ...}
  └─ In reality: きむら博士 never saw this decision
  └─ Authenticity: BROKEN
  └─ Authority: BROKEN
```

**Detectability**: ❌ LOW
- From ledger alone, no indication of fraud
- Must cross-reference with きむら博士's logs
- No cryptographic proof available

### Scenario B: Duplicate Injection

```
Client A (authorized):
1. Call: mocka_decision_write(decision_id="DC_20260815_001", ...)
2. Writes to ledger

Attacker (different authorization level):
1. Call: mocka_decision_write(decision_id="DC_20260815_001", title="MODIFIED", ...)
2. Writes to ledger (duplicate allowed)

Result:
  └─ Ledger contains 2 records with same decision_id
  └─ No indication which is authoritative
  └─ Reader must guess (usually assumes last)
  └─ Uniqueness: BROKEN
  └─ Traceability: BROKEN
```

**Detectability**: ⚠️ MEDIUM
- Duplicate decision_id is visible if reader checks
- But: No explicit indication of error
- May be confused with intentional supersede

### Scenario C: Event Service Failure

```
MCP Client:
1. Call: mocka_decision_write(title="Policy Change", ...)
2. Decision written to decision_ledger.jsonl
3. Companion event creation attempted
4. Event service unavailable (network down)
5. Exception caught silently (print only)

Result:
  └─ Decision in ledger: ✅ YES
  └─ Event in mocka_write_event: ❌ NO
  └─ Audit trail: INCOMPLETE
  └─ Companion event fields in decision record: NOT POPULATED
  └─ Traceability: BROKEN
```

**Detectability**: ⚠️ LOW
- Decision record doesn't indicate event failure
- Related_events field is empty
- Only visible if comparing ledger to event service

### Scenario D: Authority Bypass (GL7 Bypass)

```
Governance Structure Bypass:
1. GL7 check would normally reject (aborts found)
2. But: GL7 check can be bypassed (structural vulnerability)
3. SealGovernanceGate.execute() called with forced approval
4. Seal script executes
5. Decision recorded as approved

Result:
  └─ Ledger shows: "approved": true, "aborts": []
  └─ Reality: GL7 check was bypassed
  └─ Authority: BROKEN
```

**Detectability**: ❌ NONE
- Ledger alone cannot detect GL7 bypass
- Must verify against GL7 state machine
- Requires external governance audit

---

## CONCLUSIONS

### Trust Dimensions Assessment

1. **Authenticity**: ⚠️ WEAK
   - approved_by field is unverified
   - No cryptographic proof
   - Impersonation possible
   - **Cannot rely on this field for security**

2. **Authority**: ⚠️ PARTIAL
   - GL7 provides governance check (SealGov only)
   - MCP path has no authorization
   - No per-decision permission check
   - **Cannot prove creator was authorized**

3. **Uniqueness**: ❌ BROKEN
   - No enforcement in production (MCP, SealGov)
   - Duplicates possible and undetected
   - LedgerStore unused (could prevent this)
   - **Cannot guarantee one decision_id = one decision**

4. **Immutability**: ✅ STRONG
   - Append-only file mode
   - OS-level protection
   - No application-level modifications
   - **Can trust historical records**

5. **Traceability**: ⚠️ PARTIAL
   - Companion events optional (may fail)
   - SealGov has better traceability
   - MCP path lacks session/user capture
   - **Cannot fully reconstruct lifecycle**

### Institutional Trust Gap

```
TRUST ASSUMPTION (Implicit):
  "Decision Ledger records represent genuine, authorized decisions"

TRUST REALITY (Evidence-based):
  "Decision Ledger records represent write operations,
   some authorized (SealGov) and some unverified (MCP).
   Duplicates are possible. Authenticity is unverified.
   Uniqueness is not enforced."
```

### Human Gate Decision Required

**Question**: What level of trust must Decision Ledger provide?

**Current Trust Level**: OPERATIONAL (accepts duplicates, unverified authority)

**Required Trust Levels**:
1. **Compliance**: Need proof of authorization (Authenticity + Authority)
2. **Audit**: Need complete lifecycle traceability (Traceability + Events)
3. **Governance**: Need uniqueness (Uniqueness enforcement)
4. **Security**: Need cryptographic proof (Signatures + Hashes)

---

**Report Status**: TRUST MODEL ANALYSIS COMPLETE  
**Next Step**: TASK 4 - Duplicate Scenario Simulation

---

**Evidence Base**: Code analysis, no execution
**Verification Method**: Pattern matching, control flow analysis
**Modifications**: NONE (read-only audit)
